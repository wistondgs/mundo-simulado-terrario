"""Adapter from structured corpus artifacts to a navigable hypergraph."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable

import yaml

from terrario.lab.hypergraph.models import HyperedgeCandidateRecord, HypergraphEdge
from terrario.lab.models import EpistemicStatus, thaw


class HypergraphAdapter:
    def __init__(self, records: Iterable[object] = (), edges: Iterable[HypergraphEdge] = ()):
        self.records = tuple(records); self.edges = tuple(edges)

    @classmethod
    def ingest(cls, paths: Iterable[str | Path]) -> "HypergraphAdapter":
        """Read JSON/YAML derived artifacts only; PDFs are rejected."""
        records, edges = [], []
        for raw_path in paths:
            path = Path(raw_path)
            if path.suffix.lower() == ".pdf": raise ValueError("PDF ingestion is outside Terrario's scientific boundary")
            data = yaml.safe_load(path.read_text(encoding="utf-8")) if path.suffix.lower() in {".yaml", ".yml"} else json.loads(path.read_text(encoding="utf-8"))
            for item in data if isinstance(data, list) else data.get("records", []):
                status = EpistemicStatus(item.get("status", "RAW"))
                records.append({**item, "status": status, "provenance": item.get("provenance", str(path))})
            for item in data.get("edges", []) if isinstance(data, dict) else []:
                edges.append(HypergraphEdge(item["source"], item["target"], item.get("provenance", str(path)), EpistemicStatus(item.get("status", "UNRESOLVED"))))
        return cls(records, edges)

    def add_hyperedge_candidate(self, record: HyperedgeCandidateRecord) -> "HypergraphAdapter":
        if record.status != EpistemicStatus.TESTABLE_CONJUNCTION:
            raise ValueError("HYPERCAND must remain TESTABLE_CONJUNCTION")
        return HypergraphAdapter((*self.records, record), self.edges)

    def export(self) -> dict:
        def encode(x): return thaw(asdict(x)) if hasattr(x, "__dataclass_fields__") else thaw(x)
        return {"nodes": [encode(x) for x in self.records], "edges": [encode(x) for x in self.edges]}

    @staticmethod
    def operational_catalog():
        """Typed execution/observer relations, separate from theory candidates."""
        from terrario.lab.hypergraph.operational import operational_hypergraph
        return operational_hypergraph()
