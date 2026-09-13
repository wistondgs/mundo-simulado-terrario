"""Traversal engine for the federated cross-graph.

Supports BFS, DFS, shortest typed path, bounded path enumeration, reverse
traversal, and hyperedge-aware traversal. Every traversal is bounded by
max_depth / max_nodes / max_edges / allowed_domains / allowed_relations and a
snapshot manifest, so an accidental query cannot freeze the Lab. A topological
graph path is never presented automatically as valid scientific reasoning.
"""
from __future__ import annotations

import json
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Mapping

from terrario.lab.crossgraph.domain import (
    CrossDomainEntityRef, Domain, LinkState, PathKind, QueryMode,
)
from terrario.lab.crossgraph.service import CrossGraphService


@dataclass(frozen=True)
class TraversalBudget:
    max_depth: int = 4
    max_nodes: int = 500
    max_edges: int = 2000
    max_results: int = 100
    timeout_s: float = 5.0
    allowed_domains: tuple[str, ...] = ()
    allowed_relations: tuple[str, ...] = ()


@dataclass(frozen=True)
class TraversalStep:
    ref_key: str
    link_id: str
    relation_type: str
    direction: str


@dataclass(frozen=True)
class TraversalPath:
    kind: PathKind
    start_key: str
    end_key: str
    steps: tuple[TraversalStep, ...]
    warnings: tuple[str, ...]

    @property
    def depth(self) -> int:
        return len(self.steps)


class TraversalEngine:
    def __init__(self, service: CrossGraphService):
        self.service = service

    # ------------------------------------------------------------ adjacency
    def _active_links(self) -> tuple[Mapping[str, Any], ...]:
        return self.service.active_links()

    def _adjacency(self, links, budget: TraversalBudget):
        """Build outbound/inbound indexes once per traversal (O(E), not per node)."""
        out_index: dict[str, list[tuple[str, Mapping[str, Any]]]] = {}
        in_index: dict[str, list[tuple[str, Mapping[str, Any]]]] = {}
        for link in links:
            if budget.allowed_relations and link["relation_type"] not in budget.allowed_relations:
                continue
            out_index.setdefault(link["source_key"], []).append((link["target_key"], link))
            in_index.setdefault(link["target_key"], []).append((link["source_key"], link))
        return out_index, in_index

    def _domain_allowed(self, key: str, budget: TraversalBudget) -> bool:
        if not budget.allowed_domains:
            return True
        return key.split(":", 1)[0] in budget.allowed_domains

    # ---------------------------------------------------------------- BFS
    def bfs(self, start: CrossDomainEntityRef, budget: TraversalBudget,
            reverse: bool = False) -> Mapping[str, Any]:
        start_key = start.key()
        links = self._active_links()
        visited, order, edges_used = {start_key}, [start_key], []
        queue, depth_of = deque([start_key]), {start_key: 0}
        deadline = time.monotonic() + budget.timeout_s
        truncated = False
        out_index, in_index = self._adjacency(links, budget)
        index = in_index if reverse else out_index
        while queue:
            if time.monotonic() > deadline or len(visited) >= budget.max_nodes:
                truncated = True
                break
            current = queue.popleft()
            if depth_of[current] >= budget.max_depth:
                continue
            for neighbor, link in index.get(current, []):
                if not self._domain_allowed(neighbor, budget):
                    continue
                edges_used.append(link)
                if len(edges_used) >= budget.max_edges:
                    truncated = True
                    break
                if neighbor not in visited:
                    visited.add(neighbor)
                    depth_of[neighbor] = depth_of[current] + 1
                    order.append(neighbor)
                    queue.append(neighbor)
        return {"start": start_key, "mode": "reverse" if reverse else "forward",
                "nodes": order, "node_count": len(order), "edge_count": len(edges_used),
                "truncated": truncated, "depth_reached": max(depth_of.values(), default=0)}

    # ------------------------------------------------------- shortest path
    def shortest_path(self, start: CrossDomainEntityRef, end: CrossDomainEntityRef,
                      budget: TraversalBudget, reverse: bool = False) -> TraversalPath | None:
        start_key, end_key = start.key(), end.key()
        links = self._active_links()
        out_index, in_index = self._adjacency(links, budget)
        index = in_index if reverse else out_index
        queue = deque([(start_key, ())])
        seen = {start_key}
        deadline = time.monotonic() + budget.timeout_s
        while queue:
            if time.monotonic() > deadline:
                return None
            current, path = queue.popleft()
            if len(path) >= budget.max_depth:
                continue
            if current == end_key:
                return TraversalPath(PathKind.GRAPH_PATH, start_key, end_key, tuple(path), ())
            for neighbor, link in index.get(current, []):
                if neighbor in seen or not self._domain_allowed(neighbor, budget):
                    continue
                seen.add(neighbor)
                direction = "reverse" if reverse else "forward"
                queue.append((neighbor, (*path, TraversalStep(
                    neighbor, link["link_id"], link["relation_type"], direction))))
        return None

    # ------------------------------------------------- bounded enumeration
    def enumerate_paths(self, start: CrossDomainEntityRef, end: CrossDomainEntityRef,
                        budget: TraversalBudget) -> tuple[TraversalPath, ...]:
        start_key, end_key = start.key(), end.key()
        links = self._active_links()
        out_index, _ = self._adjacency(links, budget)
        results: list[TraversalPath] = []
        deadline = time.monotonic() + budget.timeout_s

        def dfs(current: str, path: tuple[TraversalStep, ...], seen: frozenset[str]) -> None:
            if len(results) >= budget.max_results or time.monotonic() > deadline:
                return
            if len(path) > budget.max_depth:
                return
            if current == end_key and path:
                results.append(TraversalPath(PathKind.GRAPH_PATH, start_key, end_key, path, ()))
                return
            for neighbor, link in out_index.get(current, []):
                if neighbor in seen or not self._domain_allowed(neighbor, budget):
                    continue
                dfs(neighbor, (*path, TraversalStep(
                    neighbor, link["link_id"], link["relation_type"], "forward")),
                    seen | {neighbor})

        dfs(start_key, (), frozenset({start_key}))
        return tuple(results)

    # -------------------------------------------------------- typed path
    def typed_path(self, start: CrossDomainEntityRef,
                   pattern: tuple[tuple[str, str], ...],
                   budget: TraversalBudget) -> tuple[TraversalPath, ...]:
        """Follow a declarative pattern of (relation, target_domain) steps.

        Example: (("REPORTS_CLAIM", "CLAIM"), ("REFERS_TO_CONCEPT", "ONTOLOGY")).
        """
        links = self._active_links()
        out_index, _ = self._adjacency(links, budget)
        results: list[TraversalPath] = []
        deadline = time.monotonic() + budget.timeout_s

        def walk(current: str, index: int, path: tuple[TraversalStep, ...]) -> None:
            if len(results) >= budget.max_results or time.monotonic() > deadline:
                return
            if index == len(pattern):
                results.append(TraversalPath(PathKind.GRAPH_PATH, start.key(), current, path, ()))
                return
            relation, target_domain = pattern[index]
            for neighbor, link in out_index.get(current, []):
                if link["relation_type"] != relation:
                    continue
                if neighbor.split(":", 1)[0] != target_domain:
                    continue
                walk(neighbor, index + 1, (*path, TraversalStep(
                    neighbor, link["link_id"], relation, "forward")))

        walk(start.key(), 0, ())
        return tuple(results)

    # ------------------------------------------------------- path explanation
    def explain_path(self, path: TraversalPath) -> Mapping[str, Any]:
        from terrario.lab.crossgraph.relations import get_relation
        node_sequence = [path.start_key] + [step.ref_key for step in path.steps]
        link_rows = {row["link_id"]: row for row in self.service.active_links()}
        explanations = []
        for step in path.steps:
            link = link_rows.get(step.link_id)
            semantics = get_relation(step.relation_type)
            explanations.append({
                "link_id": step.link_id, "relation_type": step.relation_type,
                "relation_meaning": semantics.scientific_meaning if semantics else "UNREGISTERED",
                "provenance": link["provenance"] if link else "UNAVAILABLE",
                "assertion_class": link["assertion_class"] if link else "UNAVAILABLE",
                "direction": step.direction})
        return {"kind": path.kind.value, "node_sequence": node_sequence,
                "link_sequence": explanations, "depth": path.depth,
                "warnings": list(path.warnings),
                "is_scientific_trace": path.kind is PathKind.SCIENTIFIC_TRACE,
                "note": "a topological graph path is not automatically valid scientific reasoning"}

    # --------------------------------------------------- trace validation
    def validate_trace(self, path: TraversalPath) -> Mapping[str, Any]:
        """A SCIENTIFIC_TRACE requires active links, resolvable endpoints,
        provenance, exact versions, compatible semantics, and no unreviewed
        machine candidates."""
        failures: list[str] = []
        link_rows = {row["link_id"]: row for row in self.service.active_links()}
        from terrario.lab.crossgraph.relations import get_relation
        for step in path.steps:
            link = link_rows.get(step.link_id)
            if link is None:
                failures.append(f"LINK_NOT_ACTIVE:{step.link_id}")
                continue
            if not link["provenance"]:
                failures.append(f"PROVENANCE_MISSING:{step.link_id}")
            if link["assertion_class"] == "MACHINE_CANDIDATE":
                failures.append(f"UNREVIEWED_CANDIDATE:{step.link_id}")
            if get_relation(step.relation_type) is None:
                failures.append(f"UNREGISTERED_RELATION:{step.relation_type}")
        for key in [path.start_key] + [s.ref_key for s in path.steps]:
            ref = self._ref_from_key(key)
            resolution = self.service.resolve_endpoint(ref)
            if not resolution["resolved"]:
                failures.append(f"ENDPOINT_{resolution['status']}:{key}")
        return {"valid": not failures, "failures": failures, "kind": PathKind.SCIENTIFIC_TRACE.value}

    @staticmethod
    def _ref_from_key(key: str) -> CrossDomainEntityRef:
        domain, entity_type, entity_id = key.split(":", 2)
        return CrossDomainEntityRef(Domain(domain), entity_type, entity_id)
