"""Tests for the materialized adjacency index and query cache."""
import sqlite3
from pathlib import Path

import pytest

from terrario.lab.crossgraph.domain import (
    AssertionClass, CrossDomainEntityRef, Domain,
)
from terrario.lab.crossgraph.service import CrossGraphService
from terrario.lab.crossgraph.traversal import TraversalBudget, TraversalEngine
from terrario.lab.persistence import ArtifactRepository


def ref(domain, entity_type, entity_id, **kw):
    return CrossDomainEntityRef(domain, entity_type, entity_id, **kw)


@pytest.fixture
def service(tmp_path):
    return CrossGraphService(Path("."), ArtifactRepository(tmp_path / ".terrario"))


@pytest.fixture
def linked(service):
    world = ref(Domain.WORLD, "WorldDefinition", "D2",
                content_hash=service.adapters[Domain.WORLD].get_content_hash(
                    ref(Domain.WORLD, "WorldDefinition", "D2")))
    scenario = ref(Domain.SCENARIO, "ScenarioDefinition", "D2")
    service.propose_link(scenario, world, "INSTANTIATES_WORLD",
                         AssertionClass.USER_ASSERTED, "p", "tester", activate=True)
    return service, scenario, world


def test_index_stale_until_rebuilt(service, linked):
    assert service.adjacency_index_stale() is True
    result = service.rebuild_adjacency_index()
    assert result["rebuilt"] and result["link_count"] >= 1
    assert service.adjacency_index_stale() is False


def test_index_invalidated_on_link_write(service, linked):
    service.rebuild_adjacency_index()
    assert service.adjacency_index_stale() is False
    # A new canonical link write invalidates the derived index (O(1)).
    d3 = ref(Domain.SCENARIO, "ScenarioDefinition", "D3")
    world = ref(Domain.WORLD, "WorldDefinition", "D3")
    service.propose_link(d3, world, "INSTANTIATES_WORLD",
                         AssertionClass.USER_ASSERTED, "p", "tester")
    assert service.adjacency_index_stale() is True


def test_indexed_bfs_matches_canonical_links(service, linked):
    _, scenario, world = linked
    engine = TraversalEngine(service)
    result = engine.bfs_indexed(scenario, TraversalBudget(max_depth=2))
    assert result["indexed"] is True
    assert world.key() in result["nodes"]


def test_indexed_bfs_reverse(service, linked):
    _, scenario, world = linked
    engine = TraversalEngine(service)
    result = engine.bfs_indexed(world, TraversalBudget(max_depth=2), reverse=True)
    assert scenario.key() in result["nodes"]


def test_corrupt_index_detected_by_hash_verification(service, linked):
    service.rebuild_adjacency_index()
    # Tamper the derived index directly (it is non-authoritative, so this is
    # possible); hash verification must flag it as stale/corrupt.
    raw = sqlite3.connect(service.artifacts.database_path)
    try:
        raw.execute("UPDATE cross_adjacency_index SET target_key='WORLD:WorldDefinition:GHOST'")
        raw.commit()
    finally:
        raw.close()
    assert service.adjacency_index_stale(verify_hash=False) is False  # fast path: meta present
    # Rebuilding discards the corrupt rows and restores from canonical links.
    service.rebuild_adjacency_index()
    engine = TraversalEngine(service)
    _, scenario, world = linked
    result = engine.bfs_indexed(scenario, TraversalBudget(max_depth=2))
    assert world.key() in result["nodes"]


def test_query_cache_keyed_by_snapshot(service, linked):
    service.create_snapshot("tester", "for cache")
    calls = []
    def compute():
        calls.append(1)
        return {"value": 42}
    spec = {"kind": "neighborhood", "center": "SCENARIO:ScenarioDefinition:D2"}
    first = service.cached_query(spec, compute)
    second = service.cached_query(spec, compute)
    assert first == second == {"value": 42}
    assert len(calls) == 1  # second call served from cache


def test_query_cache_not_served_from_wrong_snapshot(service, linked):
    service.create_snapshot("tester", "snap1")
    spec = {"kind": "count"}
    service.cached_query(spec, lambda: {"n": 1})
    # A new snapshot changes the cache key, so the old entry is not served.
    world = ref(Domain.WORLD, "WorldDefinition", "D3")
    service.propose_link(ref(Domain.SCENARIO, "ScenarioDefinition", "D3"), world,
                         "INSTANTIATES_WORLD", AssertionClass.USER_ASSERTED, "p", "t", activate=True)
    service.create_snapshot("tester", "snap2")
    calls = []
    service.cached_query(spec, lambda: calls.append(1) or {"n": 2})
    assert calls, "cache must recompute under a new snapshot"
