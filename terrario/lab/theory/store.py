"""Lightweight versioned graph store with separate theory/evidence layers."""

from __future__ import annotations

import json
import re
from collections import deque
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Any, Iterable

from terrario.lab.models import thaw


@dataclass(frozen=True)
class GraphPath:
    node_ids: tuple[str, ...]
    edges: tuple[dict, ...]


class TheoryGraphStore:
    def __init__(self, snapshot_id: str):
        self.snapshot_id = snapshot_id
        self.theory_nodes: dict[str, dict] = {}
        self.theory_edges: list[dict] = []
        self.evidence_nodes: dict[str, dict] = {}
        self.evidence_edges: list[dict] = []

    @staticmethod
    def _record(record: Any) -> dict:
        return {field.name: thaw(getattr(record, field.name)) for field in fields(record)}

    def add_theory(self, record: Any):
        data = self._record(record); node_type = type(record).__name__
        graph_id = f"{node_type}:{data['id']}"
        data.update({"record_id": data["id"], "id": graph_id, "node_type": node_type, "graph_layer": "THEORY"})
        self.theory_nodes[graph_id] = data
        return graph_id

    def add_evidence(self, node_id: str, data: dict):
        self.evidence_nodes[node_id] = {**thaw(data), "id": node_id, "graph_layer": "EXPERIMENTAL_EVIDENCE"}

    def link_theory(self, source: str, target: str, relation: str, provenance: str, epistemic_status: str):
        self.theory_edges.append({"source": source, "target": target, "relation": relation, "provenance": provenance, "epistemic_status": epistemic_status})

    def link_evidence(self, source: str, target: str, relation: str, provenance: str, epistemic_status: str):
        self.evidence_edges.append({"source": source, "target": target, "relation": relation, "provenance": provenance, "epistemic_status": epistemic_status})

    def paths(self, start: str, end: str, max_depth: int = 8) -> tuple[GraphPath, ...]:
        edges = (*self.theory_edges, *self.evidence_edges); queue = deque([(start, (), ())]); found = []
        while queue:
            node, visited, route = queue.popleft()
            if len(route) >= max_depth: continue
            for edge in edges:
                if edge["source"] != node or edge["target"] in visited: continue
                nodes = (*visited, node)
                next_route = (*route, dict(edge))
                if edge["target"] == end: found.append(GraphPath((*nodes, end), next_route))
                else: queue.append((edge["target"], nodes, next_route))
        return tuple(found)

    def lineage(self, node_id: str, max_depth: int = 8) -> tuple[GraphPath, ...]:
        """Return every upstream route without declaring one route authoritative."""
        edges = (*self.theory_edges, *self.evidence_edges); queue = deque([(node_id, (), ())]); found = []
        while queue:
            node, visited, route = queue.popleft()
            if len(route) >= max_depth: continue
            incoming = [edge for edge in edges if edge["target"] == node and edge["source"] not in visited]
            if not incoming and route: found.append(GraphPath(tuple(reversed((*visited, node))), tuple(reversed(route))))
            for edge in incoming: queue.append((edge["source"], (*visited, node), (*route, dict(edge))))
        return tuple(found)

    def source_for(self, node_id: str) -> str | None:
        node = self.theory_nodes.get(node_id) or self.evidence_nodes.get(node_id)
        return node.get("provenance") if node else None

    def ids_for_record(self, record_id: str) -> tuple[str, ...]:
        return tuple(node_id for node_id, node in self.theory_nodes.items() if node.get("record_id") == record_id)

    def export(self) -> dict:
        return {"schema_version": 1, "snapshot_id": self.snapshot_id,
                "theory_graph": {"nodes": list(self.theory_nodes.values()), "edges": self.theory_edges},
                "evidence_graph": {"nodes": list(self.evidence_nodes.values()), "edges": self.evidence_edges}}

    def save(self, path: str | Path):
        target = Path(path); target.write_text(json.dumps(self.export(), indent=2, ensure_ascii=False), encoding="utf-8"); return target

    @classmethod
    def load(cls, path: str | Path):
        data = json.loads(Path(path).read_text(encoding="utf-8")); store = cls(data["snapshot_id"])
        for node in data["theory_graph"]["nodes"]: store.theory_nodes[node["id"]] = node
        store.theory_edges = data["theory_graph"]["edges"]
        for node in data["evidence_graph"]["nodes"]: store.evidence_nodes[node["id"]] = node
        store.evidence_edges = data["evidence_graph"]["edges"]
        return store

    def compare(self, other: "TheoryGraphStore") -> dict:
        mine, theirs = self.theory_nodes, other.theory_nodes
        added = sorted(set(theirs) - set(mine)); removed = sorted(set(mine) - set(theirs))
        changed = sorted(k for k in set(mine) & set(theirs) if mine[k] != theirs[k])
        return {"from": self.snapshot_id, "to": other.snapshot_id, "nodes_added": added, "nodes_removed": removed, "nodes_changed": changed}


def build_graph(snapshot_id: str, imported, experiments: Iterable[Any] = (), runs: Iterable[Any] = ()) -> TheoryGraphStore:
    graph = TheoryGraphStore(snapshot_id)
    for collection in (imported.sources, imported.claims, imported.raw_concepts, imported.canonical_candidates,
                       imported.relations, imported.ambiguities, imported.conflicts, imported.hyperedges,
                       imported.coverage, imported.integrity):
        for record in collection: graph.add_theory(record)
    for mapping in imported.canonical_candidates:
        graph.link_theory(f"RawConceptRecord:{mapping.raw_concept_id}", f"CanonicalConceptCandidate:{mapping.id}", "MAPS_TO_CANDIDATE", mapping.provenance, mapping.epistemic_status.value)
    source_titles = {}
    for source in imported.sources:
        for key in ("titulo", "Obra"):
            title = source.fields.get(key)
            if title: source_titles[str(title).strip().casefold()] = f"SourceRecord:{source.id}"
    for claim in imported.claims:
        source_id = source_titles.get(claim.source_id.strip().casefold())
        if not source_id and f"SourceRecord:{claim.source_id}" in graph.theory_nodes:
            source_id = f"SourceRecord:{claim.source_id}"
        embedded_id = re.search(r"\[((?:TI|DEV|X)\w*-?\d+)\]", claim.source_id)
        if not source_id and embedded_id and f"SourceRecord:{embedded_id.group(1)}" in graph.theory_nodes:
            source_id = f"SourceRecord:{embedded_id.group(1)}"
        if source_id:
            graph.link_theory(source_id, f"ClaimRecord:{claim.id}", "SUPPORTS_AUTHORED_CLAIM", claim.provenance, claim.epistemic_status.value)
        if f"RelationRecord:{claim.id}" in graph.theory_nodes:
            graph.link_theory(f"ClaimRecord:{claim.id}", f"RelationRecord:{claim.id}", "AUDITED_AS_RELATION", claim.provenance, claim.epistemic_status.value)
    concept_labels = {}
    for concept in imported.raw_concepts:
        for key in ("nombre_original", "nombre_normalizado_provisional"):
            label = concept.fields.get(key)
            if label: concept_labels.setdefault(str(label).strip().casefold(), f"RawConceptRecord:{concept.id}")
    for relation in imported.relations:
        source = concept_labels.get(relation.source_concept.strip().casefold())
        target = concept_labels.get(relation.target_concept.strip().casefold())
        if source: graph.link_theory(f"RelationRecord:{relation.id}", source, "HAS_SOURCE_CONCEPT", relation.provenance, relation.epistemic_status.value)
        if target: graph.link_theory(f"RelationRecord:{relation.id}", target, "HAS_TARGET_CONCEPT", relation.provenance, relation.epistemic_status.value)
    for hyperedge in imported.hyperedges:
        for component in hyperedge.components:
            source = concept_labels.get(component.strip().casefold())
            if source: graph.link_theory(source, f"HyperedgeCandidateRecord:{hyperedge.id}", "COMPONENT_OF_TESTABLE_CONJUNCTION", hyperedge.provenance, "TESTABLE_CONJUNCTION")
    for experiment in experiments:
        graph.add_evidence(experiment.id, {"node_type": "ExperimentRecord", "provenance": experiment.source, "status": experiment.status})
    for run in runs:
        graph.add_evidence(run.id, {"node_type": "RunRecord", "provenance": run.source, "status": run.status, "seed": run.seed})
        graph.link_evidence(run.experiment_id, run.id, "HAS_RUN", run.source, "UNRESOLVED")
        evidence_id = f"EvidenceRecord:{run.id}"
        metric_id = f"Metric:{run.id}:status"
        graph.add_evidence(evidence_id, {"node_type": "EvidenceRecord", "provenance": run.evidence_path, "status": "INCONCLUSIVE", "raw_reference": run.evidence_path})
        graph.add_evidence(metric_id, {"node_type": "Metric", "provenance": run.source, "name": "run_status", "value": run.status, "origin": "RECORDED"})
        graph.link_evidence(run.id, evidence_id, "HAS_EVIDENCE_RECORD", run.evidence_path, "UNRESOLVED")
        graph.link_evidence(evidence_id, metric_id, "REPORTS_METRIC", run.source, "UNRESOLVED")
    return graph
