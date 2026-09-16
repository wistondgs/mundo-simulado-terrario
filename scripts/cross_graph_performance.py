"""Performance characterization for the federated cross-graph.

Builds a synthetic cross-link dataset at stepped scales and measures
neighborhood, reverse neighborhood, typed path, 3-hop and 6-hop bounded
traversal, GraphSlice, snapshot creation, verify, and diff. Reports real
measurements only; no universal scalability claim. Run directly:

    PYTHONPATH=. .venv/bin/python scripts/cross_graph_performance.py
"""
from __future__ import annotations

import json
import statistics
import tempfile
import time
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.crossgraph.domain import (
    AssertionClass, CrossDomainEntityRef, Domain, LinkState,
)
from terrario.lab.crossgraph.queries import CrossGraphQueries
from terrario.lab.crossgraph.service import CrossGraphService
from terrario.lab.crossgraph.traversal import TraversalBudget, TraversalEngine
from terrario.lab.crossgraph.verify import CrossGraphVerifier
from terrario.lab.persistence import ArtifactRepository
from terrario.lab.persistence.canonical import content_hash, plain


def _ref(domain, entity_type, entity_id):
    return CrossDomainEntityRef(domain, entity_type, entity_id)


def build_links(service: CrossGraphService, count: int) -> None:
    """Insert `count` ACTIVE cross-links directly (synthetic, real SQL).

    Targets pin the real D2 world so endpoint resolution succeeds; this measures
    the engine's O(N) cost rather than the cost of reporting thousands of
    unresolvable synthetic endpoints.
    """
    now = service.artifacts.now()
    d2 = _ref(Domain.WORLD, "WorldDefinition", "D2")
    d2_hash = service.adapters[Domain.WORLD].get_content_hash(d2)
    target = CrossDomainEntityRef(Domain.WORLD, "WorldDefinition", "D2", content_hash=d2_hash)
    source = CrossDomainEntityRef(Domain.SCENARIO, "ScenarioDefinition", "D2")
    with service.artifacts.transaction() as connection:
        for index in range(count):
            link_id = service.artifacts._identifier("link")
            # link_id is unique per row, so each link hash is unique even though
            # both endpoints pin the real, resolvable D2 definitions.
            body = {"link_id": link_id, "source_ref": plain(source), "target_ref": plain(target),
                    "relation_type": "INSTANTIATES_WORLD",
                    "assertion_class": "USER_ASSERTED", "state": "ACTIVE",
                    "provenance": "synthetic perf", "created_at": now, "created_by": "perf",
                    "rule_id": None, "rule_version": None, "supersedes_link_id": None,
                    "effective_at": None}
            link_hash = content_hash(body)
            connection.execute(
                "INSERT INTO cross_links(link_id,source_ref_json,target_ref_json,source_key,"
                "target_key,relation_type,assertion_class,state,provenance,rule_id,rule_version,"
                "supersedes_link_id,link_hash,effective_at,created_at,created_by)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (link_id, json.dumps(plain(source)), json.dumps(plain(target)), source.key(),
                 target.key(), "INSTANTIATES_WORLD", "USER_ASSERTED", "ACTIVE", "synthetic perf",
                 None, None, None, link_hash, None, now, "perf"))


def build_sparse_links(service: CrossGraphService, count: int, fanout: int = 4) -> None:
    """Insert `count` ACTIVE cross-links as a sparse graph (low per-node fan-out).

    This is the realistic interactive-navigation case: many nodes, each with a
    small neighborhood, rather than one node with a 100k fan-out. Endpoints are
    synthetic (traversal does not require them to resolve).
    """
    now = service.artifacts.now()
    domains = [Domain.SCENARIO, Domain.WORLD, Domain.THEORY, Domain.REFERENCE,
               Domain.HYPOTHESIS, Domain.EXPERIMENT]
    relations = ["INSTANTIATES_WORLD", "MAPS_TO", "DERIVED_FROM", "TESTS",
                 "USES_SCENARIO", "MOTIVATES"]
    with service.artifacts.transaction() as connection:
        for index in range(count):
            source = _ref(domains[index % len(domains)], "Entity", f"N{index}")
            target = _ref(domains[(index + 1) % len(domains)], "Entity",
                          f"N{(index + 1 + (index % fanout)) % max(count, 2)}")
            relation = relations[index % len(relations)]
            link_id = service.artifacts._identifier("link")
            body = {"link_id": link_id, "source_ref": plain(source), "target_ref": plain(target),
                    "relation_type": relation, "assertion_class": "USER_ASSERTED",
                    "state": "ACTIVE", "provenance": "synthetic sparse perf", "created_at": now,
                    "created_by": "perf", "rule_id": None, "rule_version": None,
                    "supersedes_link_id": None, "effective_at": None}
            link_hash = content_hash(body)
            connection.execute(
                "INSERT INTO cross_links(link_id,source_ref_json,target_ref_json,source_key,"
                "target_key,relation_type,assertion_class,state,provenance,rule_id,rule_version,"
                "supersedes_link_id,link_hash,effective_at,created_at,created_by)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
                (link_id, json.dumps(plain(source)), json.dumps(plain(target)), source.key(),
                 target.key(), relation, "USER_ASSERTED", "ACTIVE", "synthetic sparse perf",
                 None, None, None, link_hash, None, now, "perf"))


def _time(fn, repeat=1):
    samples, result = [], None
    for _ in range(repeat):
        start = time.perf_counter()
        result = fn()
        samples.append(time.perf_counter() - start)
    return result, statistics.median(samples)


def characterize(scale: int) -> dict:
    root = Path(tempfile.mkdtemp())
    service = CrossGraphService(Path("."), ArtifactRepository(root / ".terrario"))
    queries = CrossGraphQueries(service)
    engine = TraversalEngine(service)
    verifier = CrossGraphVerifier(service)

    _, build_s = _time(lambda: build_links(service, scale))
    center = _ref(Domain.SCENARIO, "ScenarioDefinition", "S1")
    world = _ref(Domain.WORLD, "WorldDefinition", "W2")

    _, neighborhood_s = _time(lambda: engine.bfs(center, TraversalBudget(max_depth=2)), repeat=10)
    _, reverse_s = _time(lambda: engine.bfs(world, TraversalBudget(max_depth=2), reverse=True), repeat=10)
    _, typed_s = _time(lambda: engine.typed_path(
        center, (("INSTANTIATES_WORLD", "WORLD"),), TraversalBudget(max_depth=2)), repeat=10)
    _, hop3_s = _time(lambda: engine.bfs(center, TraversalBudget(max_depth=3)), repeat=10)
    _, hop6_s = _time(lambda: engine.bfs(center, TraversalBudget(max_depth=6, max_nodes=2000)), repeat=5)
    _, slice_s = _time(lambda: queries.graph_slice(center, depth=2), repeat=10)
    _, snapshot_s = _time(lambda: service.create_snapshot("perf", "perf"))
    _, verify_s = _time(lambda: verifier.verify())
    latest = service.latest_snapshot()
    second = service.create_snapshot("perf", "perf2")
    _, diff_s = _time(lambda: queries.snapshot_diff(latest["snapshot_id"], second.snapshot_id), repeat=10)

    return {"scale": scale, "counts": service.counts(),
            "build_links_s": round(build_s, 3),
            "neighborhood_ms": round(neighborhood_s * 1000, 3),
            "reverse_neighborhood_ms": round(reverse_s * 1000, 3),
            "typed_path_ms": round(typed_s * 1000, 3),
            "hop3_ms": round(hop3_s * 1000, 3),
            "hop6_ms": round(hop6_s * 1000, 3),
            "graph_slice_ms": round(slice_s * 1000, 3),
            "snapshot_create_s": round(snapshot_s, 3),
            "verify_s": round(verify_s, 3),
            "snapshot_diff_ms": round(diff_s * 1000, 3)}


if __name__ == "__main__":
    results = [characterize(scale) for scale in (100_000,)]
    print(json.dumps(results, indent=2))
