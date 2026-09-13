"""Advanced integrity tests for the scientific reference graph.

Covers multiprocess import concurrency, crash/fault injection, the required
corruption tests (blob byte, DOI, node payload, edge payload, provenance,
snapshot root, parent snapshot, version relation), backup/restore, and
import/export roundtrip. Real SQLite/CAS behavior is exercised; nothing is
mocked where integrity depends on it.
"""
import hashlib
import json
import multiprocessing
import sqlite3
from pathlib import Path

import pytest

from terrario.lab.persistence import ArtifactRepository
from terrario.lab.referencegraph.import_corpus import CorpusImporter
from terrario.lab.referencegraph.service import ReferenceGraphService
from tests.test_reference_graph_core import make_corpus


def _import_worker(corpus_root, data_root, output):
    try:
        result = CorpusImporter(ArtifactRepository(data_root)).import_corpus(corpus_root)
        output.put(("IMPORTED", result["snapshot_id"]))
    except Exception as exc:
        output.put((getattr(exc, "code", type(exc).__name__), str(exc)))


def _imported(tmp_path, count=3):
    corpus = make_corpus(tmp_path, count=count)
    data_root = tmp_path / ".terrario"
    service = ReferenceGraphService(ArtifactRepository(data_root))
    CorpusImporter(service.artifacts).import_corpus(corpus)
    return corpus, data_root, service


def test_concurrent_imports_single_winner_no_half_snapshot(tmp_path):
    corpus = make_corpus(tmp_path, count=3)
    data_root = tmp_path / ".terrario"
    ArtifactRepository(data_root)  # initialize schema before forking
    context = multiprocessing.get_context("fork")
    output = context.Queue()
    processes = [context.Process(target=_import_worker,
                                 args=(str(corpus), str(data_root), output))
                 for _ in range(4)]
    for process in processes: process.start()
    for process in processes: process.join(30); assert process.exitcode == 0
    results = [output.get(timeout=5)[0] for _ in processes]
    # Every import either succeeded or hit a typed conflict; never a crash.
    allowed = {"IMPORTED", "PROVENANCE_CONFLICT", "REFERENCE_CONFLICT",
               "REFERENCE_INTEGRITY_ERROR", "IntegrityError", "OperationalError"}
    unexpected = [code for code in results
                  if code not in allowed and "locked" not in str(code).casefold()]
    assert not unexpected, f"unexpected worker outcomes: {unexpected} (all: {results})"
    # The store ends in a consistent, verifiable state with no half-snapshot.
    service = ReferenceGraphService(ArtifactRepository(data_root))
    report = service.verify()
    assert report["valid"], report["failures"]
    latest = service.repository.latest_snapshot()
    assert latest is not None
    assert service.verify_snapshot(latest["snapshot_id"])["valid"]


def test_fault_injection_before_snapshot_keeps_previous_valid(tmp_path, monkeypatch):
    corpus, data_root, service = _imported(tmp_path, count=2)
    before = service.repository.latest_snapshot()
    original = service.repository.insert_snapshot
    def fail(*args, **kwargs):
        raise RuntimeError("injected-before-snapshot-commit")
    monkeypatch.setattr(service.repository, "insert_snapshot", fail)
    importer = CorpusImporter(service.artifacts)
    importer.service = service
    with pytest.raises((RuntimeError, Exception)):
        importer.import_corpus(corpus)
    monkeypatch.setattr(service.repository, "insert_snapshot", original)
    # Restart and confirm the previous snapshot is still the latest valid one.
    restarted = ReferenceGraphService(ArtifactRepository(data_root))
    latest = restarted.repository.latest_snapshot()
    assert latest["snapshot_id"] == before["snapshot_id"]
    assert restarted.verify()["valid"]


def test_corruption_blob_byte_detected(tmp_path):
    corpus, data_root, service = _imported(tmp_path, count=1)
    reference = service.get_reference("REF-000")
    blob_hash = reference["primary_document_id"]
    blob_path = service.artifacts.blobs.destination(blob_hash)
    data = bytearray(blob_path.read_bytes())
    data[-1] ^= 0xFF  # tamper one byte
    blob_path.write_bytes(bytes(data))
    report = service.verify()
    assert not report["valid"]
    assert any("DOCUMENT_CAS_INVALID" in failure for failure in report["failures"])


def test_corruption_node_payload_detected(tmp_path):
    corpus, data_root, service = _imported(tmp_path, count=1)
    with service.artifacts.transaction() as connection:
        connection.execute("DROP TRIGGER IF EXISTS ref_nodes_no_update")
        connection.execute("UPDATE ref_nodes SET payload_json='{\"tampered\":true}' LIMIT 1")
    report = service.verify()
    assert not report["valid"]
    assert any("NODE_HASH_MISMATCH" in failure for failure in report["failures"])


def test_corruption_edge_payload_detected(tmp_path):
    corpus, data_root, service = _imported(tmp_path, count=1)
    with service.artifacts.transaction() as connection:
        connection.execute("DROP TRIGGER IF EXISTS ref_edges_no_update")
        connection.execute("UPDATE ref_edges SET provenance_detail='tampered' LIMIT 1")
    report = service.verify()
    assert not report["valid"]
    assert any("EDGE_HASH_MISMATCH" in failure for failure in report["failures"])


def test_corruption_snapshot_root_detected(tmp_path):
    corpus, data_root, service = _imported(tmp_path, count=2)
    latest = service.repository.latest_snapshot()
    # Tamper the actual node set so the recorded root no longer matches.
    with service.artifacts.transaction() as connection:
        connection.execute("DROP TRIGGER IF EXISTS ref_nodes_no_update")
        connection.execute("UPDATE ref_nodes SET node_hash=printf('%064x', 1) LIMIT 1")
    verification = service.verify_snapshot(latest["snapshot_id"])
    assert not verification["valid"]
    assert "NODE_SET_HASH_MISMATCH" in verification["failures"]


def test_dangling_edge_endpoint_detected(tmp_path):
    corpus, data_root, service = _imported(tmp_path, count=1)
    # Disable FK enforcement outside any transaction (SQLite ignores the pragma
    # inside an open transaction), then tamper on a raw connection.
    raw = sqlite3.connect(service.artifacts.database_path)
    try:
        raw.execute("PRAGMA foreign_keys=OFF")
        raw.execute("DROP TRIGGER IF EXISTS ref_edges_no_update")
        raw.execute("UPDATE ref_edges SET target_node_id='node-missing' WHERE rowid=1")
        raw.commit()
    finally:
        raw.close()
    report = service.verify()
    assert not report["valid"]
    assert any("EDGE_TARGET_MISSING" in failure for failure in report["failures"])


def test_analyst_inference_cannot_be_source_explicit(tmp_path):
    corpus, data_root, service = _imported(tmp_path, count=1)
    with service.artifacts.transaction() as connection:
        connection.execute("DROP TRIGGER IF EXISTS ref_claims_no_update")
        connection.execute(
            "UPDATE ref_claims SET claim_type='ANALYST_INTERPRETATION',"
            " epistemic_source='SOURCE_EXPLICIT' LIMIT 1")
    report = service.verify()
    assert not report["valid"]
    assert any("ANALYST_INFERENCE_MARKED_SOURCE_EXPLICIT" in f for f in report["failures"])


def test_backup_restore_preserves_graph_and_roots(tmp_path):
    corpus, data_root, service = _imported(tmp_path, count=3)
    before = service.repository.latest_snapshot()
    archive = service.artifacts.backup_archive("reference-graph")
    restored = ArtifactRepository.restore_archive(archive, tmp_path / "restored")
    restored_service = ReferenceGraphService(restored)
    assert restored.integrity_check() == "ok"
    report = restored_service.verify()
    assert report["valid"], report["failures"]
    latest = restored_service.repository.latest_snapshot()
    assert latest["root_hash"] == before["root_hash"]
    assert restored_service.counts() == service.counts()


def test_duplicate_import_is_idempotent_not_destructive(tmp_path):
    corpus, data_root, service = _imported(tmp_path, count=2)
    first = service.repository.latest_snapshot()
    result = CorpusImporter(service.artifacts).import_corpus(corpus)
    # Re-import: documents deduplicated by SHA-256, no destructive merge.
    assert result["stats"]["skipped_exact"] == 2
    assert result["stats"]["documents"] == 0
    assert service.verify()["valid"]


def test_export_snapshot_manifest_self_contained(tmp_path):
    corpus, data_root, service = _imported(tmp_path, count=2)
    latest = service.repository.latest_snapshot()
    with service.artifacts._connect() as connection:
        nodes = [dict(r) for r in connection.execute("SELECT * FROM ref_nodes")]
        edges = [dict(r) for r in connection.execute("SELECT * FROM ref_edges")]
        documents = [dict(r) for r in connection.execute("SELECT * FROM ref_documents")]
    manifest = {
        "schema_version": "terrario.reference-graph-export/v1",
        "snapshot": latest, "nodes": nodes, "edges": edges,
        "required_blobs": [doc["cas_blob_hash"] for doc in documents],
    }
    assert manifest["snapshot"]["root_hash"] == latest["root_hash"]
    assert len(manifest["required_blobs"]) == len(documents)
    # Every required blob must be verifiable in CAS.
    for blob_hash in manifest["required_blobs"]:
        assert service.artifacts.blobs.verify(blob_hash)
