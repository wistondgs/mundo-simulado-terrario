import sqlite3
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import get_context

import pytest

from terrario.lab.api import LabAPI
from terrario.lab.persistence import (
    ArtifactBundleError,
    ArtifactNotFound,
    ArtifactRepository,
    DuplicateArtifact,
    ProvenanceConflict,
)
from terrario.lab.persistence.canonical import CanonicalizationError, content_hash
from terrario.lab.persistence.history import HistoricalArtifactIndexer


def repository(tmp_path):
    return ArtifactRepository(tmp_path / ".terrario")


def _process_write(data_root, output):
    try:
        record = ArtifactRepository(data_root).create_artifact(
            "ExperimentDraft", {"seed": 11}, "draft/v1", artifact_id="ED-PROCESS-RACE",
        )
        output.put(record.version_id)
    except (DuplicateArtifact, ProvenanceConflict):
        output.put("conflict")


def test_migration_pragmas_and_artifact_survive_reopen(tmp_path):
    store = repository(tmp_path)
    created = store.create_artifact(
        "ExperimentDraft",
        {"draft_id": "ED-PERSIST-1", "world_seeds": [1], "ui_preferences": {"tab": "matrix"}},
        "terrario.lab.experiment-draft/v1",
        scientific_payload={"world_seeds": [1]},
        artifact_id="ED-PERSIST-1",
        classification="SCIENTIFIC_DESIGN_DRAFT",
        initial_state="DRAFT",
    )
    reopened = repository(tmp_path)
    loaded = reopened.current("ED-PERSIST-1", "ExperimentDraft")
    assert loaded == created
    assert reopened.current_state(created.version_id) == "DRAFT"
    assert reopened.migration_status()[0]["version"] == 1
    assert reopened.integrity_check() == "ok"
    with sqlite3.connect(reopened.database_path) as connection:
        assert connection.execute("PRAGMA journal_mode").fetchone()[0].lower() == "wal"
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 0
    with reopened._connect() as configured:
        assert configured.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        assert configured.execute("PRAGMA synchronous").fetchone()[0] == 2


def test_versions_are_append_only_and_retain_parent_hash(tmp_path):
    store = repository(tmp_path)
    first = store.create_artifact("WorldDraft", {"size": [10, 10]}, "world/v1", artifact_id="WD-1")
    second = store.create_version(
        "WD-1", {"size": [12, 10]}, "world/v1", reason="wider world",
        delta={"size": {"from": [10, 10], "to": [12, 10]}}, state="DRAFT",
    )
    assert second.version_number == 2
    assert second.parent_version_id == first.version_id
    assert second.parent_hash == first.scientific_hash
    assert store.get_version(first.version_id).payload == {"size": [10, 10]}
    assert [version.version_number for version in store.versions("WD-1")] == [1, 2]
    with pytest.raises(sqlite3.IntegrityError, match="append-only"):
        with store.transaction() as connection:
            connection.execute(
                "UPDATE artifact_versions SET reason='overwrite' WHERE version_id=?", (first.version_id,)
            )


def test_duplicate_ids_and_hashes_cannot_overwrite(tmp_path):
    store = repository(tmp_path)
    first = store.create_artifact("WorldDraft", {"size": [8, 8]}, "world/v1", artifact_id="WD-1")
    with pytest.raises((DuplicateArtifact, ProvenanceConflict)):
        store.create_artifact("WorldDraft", {"size": [8, 8]}, "world/v1", artifact_id="WD-1")
    duplicate = store.create_artifact(
        "WorldDraft", {"size": [8, 8]}, "world/v1", artifact_id="WD-OTHER", deduplicate=True,
    )
    assert duplicate.version_id == first.version_id
    assert duplicate.artifact_id == "WD-1"
    assert duplicate.deduplicated is True
    assert store.count("WorldDraft") == 1


def test_concurrent_writers_create_only_one_identity(tmp_path):
    for round_id in range(5):
        data_root = tmp_path / f".terrario-{round_id}"

        def write():
            try:
                return ArtifactRepository(data_root).create_artifact(
                    "ExperimentDraft", {"seed": 7}, "draft/v1", artifact_id="ED-RACE",
                ).version_id
            except (DuplicateArtifact, ProvenanceConflict):
                return "conflict"

        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(lambda _: write(), range(2)))
        assert sum(result != "conflict" for result in results) == 1
        assert ArtifactRepository(data_root).count("ExperimentDraft") == 1


def test_two_processes_cannot_overwrite_same_artifact(tmp_path):
    data_root = str(tmp_path / ".terrario")
    context = get_context("spawn")
    output = context.Queue()
    processes = [context.Process(target=_process_write, args=(data_root, output)) for _ in range(2)]
    for process in processes:
        process.start()
    for process in processes:
        process.join(timeout=15)
        assert process.exitcode == 0
    results = [output.get(timeout=2) for _ in processes]
    assert sum(result != "conflict" for result in results) == 1
    assert ArtifactRepository(data_root).count("ExperimentDraft") == 1


def test_content_addressed_blobs_are_atomic_deduplicated_and_recoverable(tmp_path):
    store = repository(tmp_path)
    first = store.register_blob(b"scientific trace", "application/octet-stream")
    second = store.register_blob(b"scientific trace", "application/octet-stream")
    assert first.blob_hash == second.blob_hash
    assert second.deduplicated is True
    assert store.blobs.verify(first.blob_hash)
    assert store.blobs.read(first.blob_hash) == b"scientific trace"
    orphan = store.blobs.staging_root / "interrupted.staging"
    orphan.write_bytes(b"partial")
    reopened = repository(tmp_path)
    assert len(reopened.recovered_staging) == 1
    assert reopened.recovered_staging[0].read_bytes() == b"partial"
    assert not orphan.exists()


def test_complete_blob_without_database_commit_is_detected_as_unregistered(tmp_path):
    store = repository(tmp_path)
    orphan = store.blobs.put_bytes(b"complete but transactionless")
    assert store.blobs.verify(orphan.blob_hash)
    with pytest.raises(ArtifactNotFound):
        store.blob_manifest(orphan.blob_hash)
    assert store.unregistered_blobs() == (store.blobs.destination(orphan.blob_hash),)


def test_hash_signed_bundle_roundtrip_and_tamper_detection(tmp_path):
    source = repository(tmp_path / "source")
    created = source.create_artifact(
        "ExperimentDraft", {"seed": 7, "ui_preferences": {"zoom": 2}}, "draft/v1",
        scientific_payload={"seed": 7}, artifact_id="ED-BUNDLE",
    )
    bundle = source.export_bundle(created.version_id)
    destination = repository(tmp_path / "destination")
    imported = destination.import_bundle(bundle)
    assert imported.artifact_id == "ED-BUNDLE"
    assert imported.scientific_hash == created.scientific_hash
    altered = {**bundle, "artifact": {**bundle["artifact"], "kind": "EvidenceRecord"}}
    with pytest.raises(ArtifactBundleError, match="bundle hash mismatch"):
        destination.import_bundle(altered)


def test_nonfinite_scientific_values_are_rejected():
    with pytest.raises(CanonicalizationError):
        content_hash({"metric": float("nan")})
    with pytest.raises(CanonicalizationError):
        content_hash({"metric": float("inf")})


def experiment_payload():
    return {
        "draft_id": "ED-RESTART",
        "scenario_id": "D2",
        "agent_ids": ["A4"],
        "world_seeds": [1, 2],
        "agent_seeds": [3],
        "source_artifact": "HYPERCAND-01",
    }


def test_lab_api_recovers_world_experiment_and_matrix_after_restart(tmp_path):
    data_root = tmp_path / ".terrario"
    first = LabAPI(".", data_root=data_root)
    world_payload = {
        "world_id": "D2", "draft_id": "WD-RESTART", "purpose": "durable draft",
        "dimensions": [10, 10], "action_availability": ["MOVE", "NOOP"],
    }
    status, world = first.dispatch("POST", "/api/worlds/drafts", world_payload)
    assert status == 201 and world["durable"] is True
    status, experiment = first.dispatch("POST", "/api/experiment-drafts", experiment_payload())
    assert status == 201 and experiment["durable"] is True
    status, matrix = first.dispatch("POST", "/api/trial-matrices/build", experiment_payload())
    assert status == 200 and matrix["durable"] is True and matrix["execution_performed"] is False

    restarted = LabAPI(".", data_root=data_root)
    assert restarted.dispatch("GET", "/api/worlds/drafts/WD-RESTART")[1]["purpose"] == "durable draft"
    assert restarted.dispatch("GET", "/api/experiment-drafts/ED-RESTART")[1]["world_seeds"] == [1, 2]
    recovered_matrix = restarted.dispatch("GET", f"/api/trial-matrices/{matrix['matrix_id']}")
    assert recovered_matrix[0] == 200
    assert recovered_matrix[1]["execution_performed"] is False
    assert restarted.artifacts.count() == 3


def test_backup_is_valid_sqlite_database(tmp_path):
    store = repository(tmp_path)
    store.create_artifact("WorldDraft", {"seed": 1}, "world/v1", artifact_id="WD-BACKUP")
    backup = store.backup()
    with sqlite3.connect(backup) as connection:
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert connection.execute("SELECT COUNT(*) FROM artifacts").fetchone()[0] == 1


def test_historical_index_is_read_only_idempotent_and_not_evidence(tmp_path):
    project = tmp_path / "project"
    theory = project / "theory_snapshots" / "snapshot-1"
    review = project / "scientific_reviews" / "review-1"
    runs = project / "runs" / "pilot"
    theory.mkdir(parents=True); review.mkdir(parents=True); runs.mkdir(parents=True)
    (theory / "snapshot_manifest.json").write_text('{"snapshot":"one"}', encoding="utf-8")
    (review / "review_manifest.json").write_text('{"review":"one"}', encoding="utf-8")
    (runs / "pilot_results.json").write_text('{"stage":"pilot"}', encoding="utf-8")
    before = {path: path.read_bytes() for path in (theory / "snapshot_manifest.json", review / "review_manifest.json", runs / "pilot_results.json")}
    store = ArtifactRepository(tmp_path / "data")
    first = HistoricalArtifactIndexer(project, store).index()
    second = HistoricalArtifactIndexer(project, store).index()
    assert len(first.theory_snapshots) == len(first.scientific_reviews) == len(first.historical_runs) == 1
    assert all(record.deduplicated for record in (*second.theory_snapshots, *second.scientific_reviews, *second.historical_runs))
    assert all(record.payload["scientific_evidence_published"] is False for record in (*first.theory_snapshots, *first.scientific_reviews, *first.historical_runs))
    assert before == {path: path.read_bytes() for path in before}
    assert store.count() == 3
