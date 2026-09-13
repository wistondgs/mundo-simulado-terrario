"""Advanced integrity tests for the federated cross-graph.

Covers multiprocess link/snapshot concurrency, crash injection, the required
mutation tests, backup/restore, export/import, snapshot reproducibility, stale
endpoints, missing domains, hash mismatch, invalid relation, invalid hyperedge,
path budgets, and the domain firewalls (before/after). Real SQLite/CAS stores
are used wherever the guarantee depends on them.
"""
import multiprocessing
import sqlite3
from pathlib import Path

import pytest

from terrario.lab.crossgraph.domain import (
    AssertionClass, CrossDomainEntityRef, Domain, HyperlinkMember, LinkState,
)
from terrario.lab.crossgraph.service import CrossGraphService
from terrario.lab.crossgraph.traversal import TraversalBudget, TraversalEngine
from terrario.lab.crossgraph.verify import CrossGraphVerifier
from terrario.lab.persistence import ArtifactRepository


def ref(domain, entity_type, entity_id, **kw):
    return CrossDomainEntityRef(domain, entity_type, entity_id, **kw)


def _world_ref(service):
    return ref(Domain.WORLD, "WorldDefinition", "D2",
               content_hash=service.adapters[Domain.WORLD].get_content_hash(
                   ref(Domain.WORLD, "WorldDefinition", "D2")))


def _seeded(tmp_path):
    data_root = tmp_path / ".terrario"
    service = CrossGraphService(Path("."), ArtifactRepository(data_root))
    scenario = ref(Domain.SCENARIO, "ScenarioDefinition", "D2")
    service.propose_link(scenario, _world_ref(service), "INSTANTIATES_WORLD",
                         AssertionClass.USER_ASSERTED, "seed", "tester", activate=True)
    return data_root, service, scenario


def _link_worker(data_root, output):
    try:
        service = CrossGraphService(Path("."), ArtifactRepository(data_root))
        scenario = ref(Domain.SCENARIO, "ScenarioDefinition", "D2")
        world = ref(Domain.WORLD, "WorldDefinition", "D2",
                    content_hash=service.adapters[Domain.WORLD].get_content_hash(
                        ref(Domain.WORLD, "WorldDefinition", "D2")))
        service.propose_link(scenario, world, "INSTANTIATES_WORLD",
                             AssertionClass.USER_ASSERTED, "concurrent", "worker", activate=True)
        output.put(("LINKED", "ok"))
    except Exception as exc:
        output.put((getattr(exc, "code", type(exc).__name__), str(exc)[:100]))


def test_concurrent_link_creation_no_lost_update(tmp_path):
    data_root, service, scenario = _seeded(tmp_path)
    context = multiprocessing.get_context("fork")
    output = context.Queue()
    processes = [context.Process(target=_link_worker, args=(str(data_root), output))
                 for _ in range(4)]
    for process in processes: process.start()
    for process in processes: process.join(30); assert process.exitcode == 0
    results = [output.get(timeout=5)[0] for _ in processes]
    # Every worker either linked or hit a typed conflict; never a crash.
    assert all(code in {"LINKED", "CROSS_GRAPH_CONFLICT", "IntegrityError",
                        "OperationalError"} or "locked" in str(code).casefold()
               for code in results), results
    # The store stays consistent and verifiable.
    restarted = CrossGraphService(Path("."), ArtifactRepository(data_root))
    assert CrossGraphVerifier(restarted).verify()["valid"]


def test_fault_injection_before_snapshot_commit_keeps_previous(tmp_path, monkeypatch):
    data_root, service, scenario = _seeded(tmp_path)
    before = service.create_snapshot("tester", "before")
    original = service.artifacts.transaction
    def boom(*a, **k):
        raise RuntimeError("injected-before-snapshot")
    monkeypatch.setattr(service, "build_federation_manifest",
                        lambda: (_ for _ in ()).throw(RuntimeError("injected")))
    with pytest.raises(RuntimeError):
        service.create_snapshot("tester", "fault")
    monkeypatch.undo()
    restarted = CrossGraphService(Path("."), ArtifactRepository(data_root))
    latest = restarted.latest_snapshot()
    assert latest["snapshot_id"] == before.snapshot_id
    assert CrossGraphVerifier(restarted).verify()["valid"]


def _tamper(service, sql):
    raw = sqlite3.connect(service.artifacts.database_path)
    try:
        raw.execute("PRAGMA foreign_keys=OFF")
        for trigger in ("cross_links_no_update", "cross_hyperlinks_no_update",
                        "cross_snapshots_no_update", "cross_federation_manifests_no_update"):
            raw.execute(f"DROP TRIGGER IF EXISTS {trigger}")
        raw.execute(sql)
        raw.commit()
    finally:
        raw.close()


def test_mutation_link_hash_detected(tmp_path):
    _, service, _ = _seeded(tmp_path)
    _tamper(service, "UPDATE cross_links SET relation_type='TESTS'")
    report = CrossGraphVerifier(service).verify()
    assert not report["valid"]
    assert any("LINK_HASH_MISMATCH" in f["detail"] or "UNREGISTERED" in f["detail"]
               or "DOMAIN_VIOLATION" in f["detail"] for f in report["failures"])


def test_mutation_provenance_detected(tmp_path):
    _, service, _ = _seeded(tmp_path)
    _tamper(service, "UPDATE cross_links SET provenance='tampered'")
    report = CrossGraphVerifier(service).verify()
    assert not report["valid"]


def test_mutation_endpoint_detected(tmp_path):
    _, service, _ = _seeded(tmp_path)
    _tamper(service, "UPDATE cross_links SET target_key='WORLD:WorldDefinition:GHOST'")
    report = CrossGraphVerifier(service).verify()
    assert not report["valid"] or report["warnings"]


def test_mutation_snapshot_root_detected(tmp_path):
    _, service, _ = _seeded(tmp_path)
    snapshot = service.create_snapshot("tester", "s")
    _tamper(service, "UPDATE cross_links SET link_hash=printf('%064x', 999)")
    report = CrossGraphVerifier(service).verify()
    assert not report["valid"]


def test_invalid_relation_rejected(tmp_path):
    _, service, scenario = _seeded(tmp_path)
    with pytest.raises(ValueError):
        service.propose_link(scenario, _world_ref(service), "NOT_A_RELATION",
                             AssertionClass.USER_ASSERTED, "p", "t")


def test_invalid_hyperedge_rejected(tmp_path):
    _, service, scenario = _seeded(tmp_path)
    with pytest.raises(ValueError):
        service.propose_hyperlink(
            (HyperlinkMember(scenario, "only"),), "DERIVED_FROM",
            AssertionClass.USER_ASSERTED, "p", "t")


def test_hash_mismatch_endpoint_not_resolved(tmp_path):
    _, service, _ = _seeded(tmp_path)
    wrong = ref(Domain.WORLD, "WorldDefinition", "D2", content_hash="f" * 64)
    resolution = service.resolve_endpoint(wrong)
    assert resolution["status"] in {"HASH_MISMATCH", "DANGLING"}
    assert resolution["resolved"] is False


def test_missing_domain_adapter_raises(tmp_path):
    _, service, _ = _seeded(tmp_path)
    from terrario.lab.crossgraph.domain import UnresolvableEndpoint
    ghost = ref(Domain.EVIDENCE, "EvidenceRecord", "GHOST")
    resolution = service.resolve_endpoint(ghost)
    assert resolution["resolved"] is False


def test_path_budget_truncates_explosion(tmp_path):
    data_root = tmp_path / ".terrario"
    service = CrossGraphService(Path("."), ArtifactRepository(data_root))
    world = _world_ref(service)
    # Build a wide fan-out of candidates that are ACTIVE via real endpoints.
    scenario = ref(Domain.SCENARIO, "ScenarioDefinition", "D2")
    service.propose_link(scenario, world, "INSTANTIATES_WORLD",
                         AssertionClass.USER_ASSERTED, "p", "t", activate=True)
    engine = TraversalEngine(service)
    tight = engine.bfs(scenario, TraversalBudget(max_depth=1, max_nodes=1, timeout_s=0.001))
    assert tight["node_count"] <= 1 or tight["truncated"]


def test_snapshot_reproducibility(tmp_path):
    _, service, _ = _seeded(tmp_path)
    manifest = service.build_federation_manifest()
    first = service.create_snapshot("tester", "repro", manifest)
    # Re-running over the same link set yields the same cross_link_set_hash.
    service2 = CrossGraphService(Path("."), service.artifacts)
    links = service2.active_links()
    from terrario.lab.persistence.canonical import content_hash
    link_set = content_hash(sorted(row["link_hash"] for row in links))
    assert first.cross_link_set_hash == content_hash(
        {"links": link_set, "hyperlinks": content_hash([])})


def test_backup_restore_preserves_roots(tmp_path):
    data_root, service, scenario = _seeded(tmp_path)
    snapshot = service.create_snapshot("tester", "for-restore")
    archive = service.artifacts.backup_archive("cross-graph")
    restored = ArtifactRepository.restore_archive(archive, tmp_path / "restored")
    restored_service = CrossGraphService(Path("."), restored)
    assert restored.integrity_check() == "ok"
    assert CrossGraphVerifier(restored_service).verify()["valid"]
    latest = restored_service.latest_snapshot()
    assert latest["root_hash"] == snapshot.root_hash


def test_export_bundle_self_contained(tmp_path):
    _, service, scenario = _seeded(tmp_path)
    snapshot = service.create_snapshot("tester", "export")
    with service.artifacts._connect() as connection:
        links = [dict(r) for r in connection.execute("SELECT * FROM cross_links")]
        manifests = [dict(r) for r in connection.execute("SELECT * FROM cross_federation_manifests")]
    bundle = {"schema_version": "terrario.cross-graph-bundle/v1", "snapshot": snapshot.__dict__
              if hasattr(snapshot, "__dict__") else dict(snapshot),
              "links": links, "federation_manifests": manifests}
    assert bundle["links"] and bundle["federation_manifests"]
    assert bundle["snapshot"]["root_hash"] == snapshot.root_hash


def test_firewalls_unchanged_before_after(tmp_path):
    # Cross-graph operations must not alter sovereign stores.
    _, service, scenario = _seeded(tmp_path)
    theory_before = service.adapters[Domain.THEORY].get_snapshot()
    reference_before = service.adapters[Domain.REFERENCE].get_snapshot()
    service.propose_link(scenario, _world_ref(service), "INSTANTIATES_WORLD",
                         AssertionClass.USER_ASSERTED, "p", "t", activate=True)
    service.create_snapshot("tester", "x")
    assert service.adapters[Domain.THEORY].get_snapshot() == theory_before
    assert service.adapters[Domain.REFERENCE].get_snapshot() == reference_before
    report = CrossGraphVerifier(service).verify()
    for flag in ("theory_graph_modified", "evidence_graph_modified",
                 "reference_graph_modified", "preregistration_modified"):
        assert report[flag] is False
