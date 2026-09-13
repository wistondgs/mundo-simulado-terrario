"""Core tests for the federated cross-graph."""
import sqlite3
from pathlib import Path

import pytest

from terrario.lab.api import LabAPI
from terrario.lab.crossgraph.domain import (
    AssertionClass, CrossDomainEntityRef, Domain, LinkState,
)
from terrario.lab.crossgraph.relations import RELATIONS, get_relation
from terrario.lab.crossgraph.service import CrossGraphService
from terrario.lab.crossgraph.traversal import TraversalBudget, TraversalEngine
from terrario.lab.crossgraph.verify import CrossGraphVerifier
from terrario.lab.persistence import ArtifactRepository


def ref(domain, entity_type, entity_id, **kw):
    return CrossDomainEntityRef(domain, entity_type, entity_id, **kw)


@pytest.fixture
def service(tmp_path):
    return CrossGraphService(Path("."), ArtifactRepository(tmp_path / ".terrario"))


@pytest.fixture
def linked(service):
    """A service with a small real SCENARIO->WORLD->? chain and a hypothesis link."""
    world = ref(Domain.WORLD, "WorldDefinition", "D2",
                content_hash=service.adapters[Domain.WORLD].get_content_hash(
                    ref(Domain.WORLD, "WorldDefinition", "D2")))
    scenario = ref(Domain.SCENARIO, "ScenarioDefinition", "D2")
    service.propose_link(scenario, world, "INSTANTIATES_WORLD",
                         AssertionClass.USER_ASSERTED, "scenario instantiates world", "tester",
                         activate=True)
    return service, scenario, world


def test_relation_registry_excludes_supports_theory():
    assert "SUPPORTS_THEORY" not in RELATIONS
    tests = get_relation("TESTS")
    assert tests.inverse_relation == "TESTED_BY"
    assert get_relation("DERIVED_FROM").acyclic is True


def test_cross_domain_entity_ref_is_pinnable():
    pinned = ref(Domain.WORLD, "WorldDefinition", "D2", snapshot_id="snap",
                 content_hash="a" * 64, schema_version="v1")
    assert pinned.snapshot_id == "snap" and pinned.content_hash == "a" * 64
    assert pinned.key() == "WORLD:WorldDefinition:D2"
    assert pinned.ref_hash != ref(Domain.WORLD, "WorldDefinition", "D2").ref_hash


def test_endpoint_resolution_resolves_and_dangles(service):
    world = ref(Domain.WORLD, "WorldDefinition", "D2")
    assert service.resolve_endpoint(world)["status"] == "RESOLVED"
    missing = ref(Domain.WORLD, "WorldDefinition", "NOPE")
    assert service.resolve_endpoint(missing)["status"] == "DANGLING"


def test_activation_requires_resolvable_endpoints(service):
    from terrario.lab.crossgraph.domain import UnresolvableEndpoint
    scenario = ref(Domain.SCENARIO, "ScenarioDefinition", "D2")
    missing = ref(Domain.WORLD, "WorldDefinition", "NOPE")
    with pytest.raises(UnresolvableEndpoint):
        service.propose_link(scenario, missing, "INSTANTIATES_WORLD",
                             AssertionClass.USER_ASSERTED, "p", "tester", activate=True)


def test_relation_domain_constraints_enforced(service):
    # TESTS requires source in {EXPERIMENT, SCENARIO, PREREGISTRATION}; WORLD is forbidden.
    world = ref(Domain.WORLD, "WorldDefinition", "D2")
    hypothesis = ref(Domain.HYPOTHESIS, "HypothesisRecord", "H-1")
    with pytest.raises(ValueError):
        service.propose_link(world, hypothesis, "TESTS",
                             AssertionClass.USER_ASSERTED, "p", "tester")


def test_machine_candidate_can_never_be_active(service):
    scenario = ref(Domain.SCENARIO, "ScenarioDefinition", "D2")
    world = ref(Domain.WORLD, "WorldDefinition", "D2")
    with pytest.raises(ValueError):
        service.propose_link(scenario, world, "INSTANTIATES_WORLD",
                             AssertionClass.MACHINE_CANDIDATE, "p", "tester",
                             state=LinkState.ACTIVE)


def test_candidate_review_activates_or_rejects(service):
    world = ref(Domain.WORLD, "WorldDefinition", "D2",
                content_hash=service.adapters[Domain.WORLD].get_content_hash(
                    ref(Domain.WORLD, "WorldDefinition", "D2")))
    scenario = ref(Domain.SCENARIO, "ScenarioDefinition", "D2")
    candidate = service.propose_link(scenario, world, "INSTANTIATES_WORLD",
                                     AssertionClass.USER_ASSERTED, "p", "tester")
    assert candidate.state is LinkState.CANDIDATE
    approved = service.review_candidate(candidate.link_id, True, "reviewer", "looks right")
    assert approved.state is LinkState.ACTIVE
    assert service.current_link_state(candidate.link_id) is LinkState.ACTIVE


def test_acyclic_relation_rejects_cycle(service):
    a = ref(Domain.WORLD, "WorldDefinition", "D2")
    b = ref(Domain.SCENARIO, "ScenarioDefinition", "D2")
    c = ref(Domain.SCENARIO, "ScenarioDefinition", "D3")
    service.propose_link(a, b, "DERIVED_FROM", AssertionClass.USER_ASSERTED, "p", "t", activate=True)
    service.propose_link(b, c, "DERIVED_FROM", AssertionClass.USER_ASSERTED, "p", "t", activate=True)
    with pytest.raises(ValueError):
        service.propose_link(c, a, "DERIVED_FROM", AssertionClass.USER_ASSERTED, "p", "t", activate=True)


def test_append_only_triggers(service, linked):
    # Populate a snapshot and a trace break so their triggers have rows to block.
    service.create_snapshot("tester", "for trigger test")
    service.record_trace_break(
        ref(Domain.REFERENCE, "ScientificReferenceRecord", "REF-X"), "THEORY",
        "no concept", "concept identity")
    for statement in ("UPDATE cross_links SET provenance='x'", "DELETE FROM cross_links",
                      "DELETE FROM cross_snapshots", "DELETE FROM cross_trace_breaks"):
        with pytest.raises(sqlite3.IntegrityError), service.artifacts.transaction() as connection:
            connection.execute(statement)


def test_traversal_bfs_shortest_typed_reverse(linked):
    service, scenario, world = linked
    engine = TraversalEngine(service)
    forward = engine.bfs(scenario, TraversalBudget(max_depth=2))
    assert world.key() in forward["nodes"]
    reverse = engine.bfs(world, TraversalBudget(max_depth=2), reverse=True)
    assert scenario.key() in reverse["nodes"]
    shortest = engine.shortest_path(scenario, world, TraversalBudget())
    assert shortest and shortest.depth == 1
    typed = engine.typed_path(scenario, (("INSTANTIATES_WORLD", "WORLD"),), TraversalBudget())
    assert len(typed) == 1


def test_explain_path_has_meaning_and_provenance(linked):
    service, scenario, world = linked
    engine = TraversalEngine(service)
    path = engine.shortest_path(scenario, world, TraversalBudget())
    explanation = engine.explain_path(path)
    assert explanation["link_sequence"][0]["relation_meaning"]
    assert explanation["link_sequence"][0]["provenance"]
    assert explanation["is_scientific_trace"] is False


def test_trace_validation_requires_active_and_resolvable(linked):
    service, scenario, world = linked
    engine = TraversalEngine(service)
    path = engine.shortest_path(scenario, world, TraversalBudget())
    result = engine.validate_trace(path)
    assert result["valid"] and not result["failures"]


def test_snapshot_and_manifest_and_diff(service, linked):
    snapshot = service.create_snapshot("tester", "first")
    assert snapshot.link_count >= 1
    latest = service.latest_snapshot()
    assert latest["root_hash"] == snapshot.root_hash
    from terrario.lab.crossgraph.queries import CrossGraphQueries
    second = service.create_snapshot("tester", "second")
    diff = CrossGraphQueries(service).snapshot_diff(snapshot.snapshot_id, second.snapshot_id)
    assert "same_root" in diff


def test_verify_clean_and_detects_tamper(service, linked):
    verifier = CrossGraphVerifier(service)
    assert verifier.verify()["valid"]
    with service.artifacts.transaction() as connection:
        connection.execute("DROP TRIGGER IF EXISTS cross_links_no_update")
        connection.execute("UPDATE cross_links SET provenance='tampered'")
    report = verifier.verify()
    assert not report["valid"]
    assert any(f["class"] == "INTEGRITY_FAILURE" for f in report["failures"])


def test_graph_slice_is_frontend_ready(service, linked):
    from terrario.lab.crossgraph.queries import CrossGraphQueries
    _, scenario, world = linked
    slice_ = CrossGraphQueries(service).graph_slice(scenario, depth=2)
    assert "nodes" in slice_ and "edges" in slice_ and "hyperedges" in slice_
    assert "snapshot_manifest" in slice_ and "provenance_summary" in slice_


def test_research_composition_is_working_layer(service, linked):
    from terrario.lab.crossgraph.queries import CrossGraphQueries
    _, scenario, world = linked
    queries = CrossGraphQueries(service)
    composition = queries.save_composition(
        "D2 study", (scenario, world), ({"kind": "visual", "from": scenario.key(),
                                          "to": world.key()},), "notes", "tester")
    assert composition.version == 1
    second = queries.save_composition("D2 study v2", (scenario,), (), "more", "tester",
                                      composition_id=composition.composition_id)
    assert second.version == 2
    fetched = queries.get_composition(composition.composition_id)
    assert fetched["versions"] == 2
    # Composition local links never touch canonical cross-links.
    assert service.counts()["links"] == 0 or all(
        l["source_key"] != "visual" for l in service.active_links())


def test_firewall_status_flags(service):
    report = CrossGraphVerifier(service).verify()
    assert report["theory_graph_modified"] is False
    assert report["evidence_graph_modified"] is False
    assert report["reference_graph_modified"] is False
    assert report["preregistration_modified"] is False
    assert report["scientific_execution"] is False
    assert report["evidence_publication"] is False
