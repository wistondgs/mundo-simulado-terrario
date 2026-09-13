"""Core tests for the scientific reference graph."""
import hashlib
import json
from pathlib import Path

import pytest

from terrario.lab.api import LabAPI
from terrario.lab.persistence import ArtifactRepository
from terrario.lab.referencegraph.domain import (
    DocumentStatus, DocumentVersionType, ProvenanceLevel,
)
from terrario.lab.referencegraph.import_corpus import CorpusImporter, parse_bibtex
from terrario.lab.referencegraph.repository import normalize_doi, normalize_text
from terrario.lab.referencegraph.service import ReferenceGraphService


def _pdf_bytes(seed: str) -> bytes:
    return b"%PDF-1.4\n%" + seed.encode() + b"\n" + (b"payload-" + seed.encode()) * 40


def make_corpus(root: Path, count: int = 3) -> Path:
    """Build a minimal synthetic corpus package for hermetic tests."""
    corpus = root / "corpus"
    for sub in ("manifest", "metadata", "bibliography", "provenance", "docs"):
        (corpus / sub).mkdir(parents=True, exist_ok=True)
    manifest, records, bibcsv = [], [], ["reference_id,bibtex_key,title,authors,year,venue,doi,url"]
    for index in range(count):
        ref_id = f"REF-{index:03d}"
        doc_id = f"{ref_id}-DOC-001"
        data = _pdf_bytes(f"doc{index}")
        sha = hashlib.sha256(data).hexdigest()
        rel = f"docs/{ref_id}.pdf"
        (corpus / rel).write_bytes(data)
        manifest.append({
            "document_id": doc_id, "reference_id": ref_id, "sha256": sha,
            "local_relative_path": rel, "mime_type": "application/pdf",
            "file_size_bytes": str(len(data)), "version_type": "PREPRINT",
            "doi": f"10.1234/ref.{index}", "title": f"Paper {index}",
            "authors": f"Author {index}", "year": str(2000 + index), "venue": "arXiv",
            "license": "arXiv", "access_status": "ACQUIRED", "terrario_levels": "D2",
            "d2_constructs": "OBJECT_PERSISTENCE", "experimental_paradigm": f"paradigm {index}",
            "discipline": "psychology", "provenance": "synthetic"})
        records.append({
            "reference_id": ref_id, "reference_type": "benchmark paper",
            "title": f"Paper {index}", "authors": f"Author {index}", "year": str(2000 + index),
            "constructs": ["OBJECT_PERSISTENCE"], "experimental_paradigms": [f"paradigm {index}"],
            "design_principles": [], "known_limitations": [f"limitation {index}"],
            "paper_document_ids": [doc_id], "terrario_levels": ["D2"], "d2_relevance": "",
            "discipline": "psychology", "code_url": "UNKNOWN", "verification_status": "ACQUIRED"})
        bibcsv.append(f"{ref_id},key{index},Paper {index},Author {index},{2000+index},arXiv,10.1234/ref.{index},http://x")
    (corpus / "manifest" / "CORPUS_MANIFEST.jsonl").write_text(
        "\n".join(json.dumps(row) for row in manifest), encoding="utf-8")
    (corpus / "metadata" / "REFERENCE_RECORDS.jsonl").write_text(
        "\n".join(json.dumps(row) for row in records), encoding="utf-8")
    (corpus / "bibliography" / "references.csv").write_text("\n".join(bibcsv), encoding="utf-8")
    (corpus / "metadata" / "D2_PROTOCOL_EXTRACTION.csv").write_text(
        "reference_id,extraction_status,subjects_or_agents\nREF-000,SOURCE_REPORTED,agents\n", encoding="utf-8")
    (corpus / "metadata" / "REFERENCE_LIMITATIONS.csv").write_text(
        "reference_id,limitation_id,limitation_type,limitation,source_basis,notes\n"
        "REF-000,REF-000-LIM-01,comparability,not a proof,documentary,note\n", encoding="utf-8")
    (corpus / "metadata" / "DESIGN_PRINCIPLES.csv").write_text(
        "reference_id,principle_id,source_basis,principle,terrario_possible_use,adaptation_type,limitations\n"
        "REF-000,DP-0001,bibliographic,principle one,use,TECHNICAL_REFERENCE,caution\n", encoding="utf-8")
    (corpus / "metadata" / "VERSION_RELATIONSHIPS.csv").write_text(
        "source_document_id,relation_type,target_document_id,notes\n", encoding="utf-8")
    return corpus


@pytest.fixture
def api(tmp_path):
    return LabAPI(Path("."), data_root=tmp_path / ".terrario")


@pytest.fixture
def service(tmp_path):
    return ReferenceGraphService(ArtifactRepository(tmp_path / ".terrario"))


def test_normalization_helpers():
    assert normalize_text("Héllo,  Wörld! 2021") == "hello world 2021"
    assert normalize_doi("https://doi.org/10.1234/ABC") == "10.1234/abc"
    assert normalize_doi("UNKNOWN") == "unknown"
    assert normalize_doi(None) is None


def test_bibtex_parser_minimal():
    entries = parse_bibtex("@article{key1,\n  title={A Title},\n  author={Doe, Jane},\n  year={2020},\n}\n")
    assert entries and entries[0]["bibtex_key"] == "key1"
    assert entries[0]["title"] == "A Title" and entries[0]["year"] == "2020"


def test_migration_three_applied(service):
    versions = {m["version"] for m in service.artifacts.migration_status()}
    assert {1, 2, 3} <= versions
    with service.artifacts._connect() as connection:
        tables = {row[0] for row in connection.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'ref_%'")}
        assert {"ref_documents", "ref_references", "ref_claims", "ref_nodes", "ref_edges",
                "ref_snapshots", "ref_quarantine"} <= tables


def test_import_plan_then_commit_produces_verified_snapshot(service, tmp_path):
    corpus = make_corpus(tmp_path, count=3)
    importer = CorpusImporter(service.artifacts)
    plan = importer.build_plan(corpus)
    assert len(plan.creates) == 3 and not plan.has_conflicts
    result = importer.import_corpus(corpus)
    assert result["imported"] and result["stats"]["references"] == 3
    assert result["stats"]["documents"] == 3
    report = service.verify()
    assert report["valid"] and not report["failures"]
    assert report["node_count"] > 0 and report["edge_count"] > 0


def test_three_identity_model_is_not_collapsed(service, tmp_path):
    corpus = make_corpus(tmp_path, count=1)
    CorpusImporter(service.artifacts).import_corpus(corpus)
    reference = service.get_reference("REF-000")
    with service.artifacts._connect() as connection:
        biblio = connection.execute("SELECT * FROM ref_bibliographic WHERE biblio_id=?",
                                    (reference["biblio_id"],)).fetchone()
        document = connection.execute("SELECT * FROM ref_documents WHERE document_id=?",
                                      (reference["primary_document_id"],)).fetchone()
    # DocumentIdentity == SHA-256(bytes) == CAS hash; BibliographicIdentity separate; ReferenceRecordIdentity separate.
    assert document["document_id"] == document["cas_blob_hash"]
    assert len(document["document_id"]) == 64
    assert biblio["identity_hash"] != document["document_id"]
    assert reference["reference_id"] == "REF-000" != biblio["biblio_id"]


def test_append_only_triggers_block_update_and_delete(service, tmp_path):
    import sqlite3
    corpus = make_corpus(tmp_path, count=1)
    # Corrupt one hash so a quarantine row exists to target.
    manifest_path = corpus / "manifest" / "CORPUS_MANIFEST.jsonl"
    row = json.loads(manifest_path.read_text().strip())
    row["sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(row), encoding="utf-8")
    CorpusImporter(service.artifacts).import_corpus(corpus)
    assert service.repository.list_quarantine(), "expected a quarantine row to target"
    for statement in (
        "UPDATE ref_references SET discipline='x'",
        "DELETE FROM ref_references",
        "DELETE FROM ref_nodes",
        "DELETE FROM ref_edges",
        "DELETE FROM ref_snapshots",
        "DELETE FROM ref_claims",
        "DELETE FROM ref_quarantine",
    ):
        with pytest.raises(sqlite3.IntegrityError), service.artifacts.transaction() as connection:
            connection.execute(statement)


def test_quarantine_on_hash_mismatch(service, tmp_path):
    corpus = make_corpus(tmp_path, count=1)
    # Corrupt the manifest hash so the file no longer matches.
    manifest_path = corpus / "manifest" / "CORPUS_MANIFEST.jsonl"
    row = json.loads(manifest_path.read_text().strip())
    row["sha256"] = "0" * 64
    manifest_path.write_text(json.dumps(row), encoding="utf-8")
    result = CorpusImporter(service.artifacts).import_corpus(corpus)
    assert result["stats"]["quarantine"] == 1 and result["stats"]["documents"] == 0
    quarantine = service.repository.list_quarantine()
    assert quarantine and quarantine[0]["reason"] == "HASH_MISMATCH"


def test_no_true_proven_score_fields_in_domain():
    import terrario.lab.referencegraph.domain as domain
    source = Path(domain.__file__).read_text()
    for forbidden in ("TRUE", "PROVEN", "CORRECT_THEORY", "INTELLIGENCE_SCORE"):
        assert forbidden not in source


def test_reference_graph_firewall_no_evidence_or_theory_write(api):
    # The reference-graph service/queries/importer expose no call that writes the
    # EvidenceGraph/TheoryGraph, creates a hypothesis/ExperimentDraft, preregisters,
    # or executes. Verify structurally: no such creation call exists in the package.
    import terrario.lab.referencegraph as package
    package_dir = Path(package.__file__).parent
    forbidden_calls = ("create_artifact(\"ScientificRun", "EvidenceRecord(",
                       "add_evidence(", "link_evidence(", "ScientificConclusion(",
                       "ExperimentDraft(", "create_hypothesis(", "execute_trial(",
                       "preregistrations.lock", "ScientificRun(")
    for module in package_dir.glob("*.py"):
        text = module.read_text()
        for call in forbidden_calls:
            assert call not in text, f"{call} found in {module.name}"
    status, report = api.dispatch("GET", "/api/v1/reference-graph")
    assert status == 200
    assert report["data"]["scientific_execution"] is False
    assert report["data"]["evidence_publication"] is False
    assert report["data"]["theory_graph_modified"] is False
    assert report["data"]["evidence_graph_modified"] is False


def test_projection_is_read_only_not_snapshot(service, tmp_path):
    from terrario.lab.referencegraph.queries import ReferenceGraphQueries
    corpus = make_corpus(tmp_path, count=3)
    CorpusImporter(service.artifacts).import_corpus(corpus)
    before = service.counts()["snapshots"]
    projection = ReferenceGraphQueries(service.artifacts).projection(d_level="D2")
    assert projection["read_only"] and projection["is_snapshot"] is False
    assert service.counts()["snapshots"] == before


def test_snapshot_immutable_and_chained(service, tmp_path):
    corpus = make_corpus(tmp_path, count=2)
    CorpusImporter(service.artifacts).import_corpus(corpus)
    first = service.repository.latest_snapshot()
    second = service.create_snapshot("second")
    assert second.parent_snapshot_id == first["snapshot_id"]
    assert second.root_hash != first["root_hash"] or second.node_count == first["node_count"]
    verification = service.verify_snapshot(second.snapshot_id)
    assert verification["valid"]
