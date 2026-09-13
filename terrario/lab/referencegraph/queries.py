"""First-level query service and read-only projections for the reference graph.

Projections are derived read-only views; they never create a new scientific
snapshot and never mutate the graph.
"""
from __future__ import annotations

import json
from collections import deque
from typing import Any, Mapping

from terrario.lab.persistence import ArtifactRepository
from terrario.lab.referencegraph.domain import ReferenceNotFound
from terrario.lab.referencegraph.repository import normalize_doi, normalize_text
from terrario.lab.referencegraph.service import ReferenceGraphService


class ReferenceGraphQueries:
    def __init__(self, artifacts: ArtifactRepository):
        self.artifacts = artifacts
        self.service = ReferenceGraphService(artifacts)
        self.repository = self.service.repository

    # ------------------------------------------------------------- lookups
    def get_reference(self, reference_id: str) -> Mapping[str, Any]:
        return self.service.get_reference(reference_id)

    def find_references(self, title: str | None = None, doi: str | None = None,
                        year: str | None = None, author: str | None = None) -> tuple[Mapping[str, Any], ...]:
        clauses, params = [], []
        if doi:
            clauses.append("b.doi=?"); params.append(normalize_doi(doi))
        if year:
            clauses.append("b.year=?"); params.append(str(year))
        if title:
            clauses.append("b.normalized_title LIKE ?"); params.append(f"%{normalize_text(title)}%")
        if author:
            clauses.append("LOWER(b.authors_json) LIKE ?"); params.append(f"%{author.casefold()}%")
        where = ("WHERE " + " AND ".join(clauses)) if clauses else ""
        with self.artifacts._connect() as connection:
            rows = connection.execute(
                f"SELECT r.* FROM ref_references r JOIN ref_bibliographic b ON b.biblio_id=r.biblio_id "
                f"{where} ORDER BY r.reference_id", params).fetchall()
            return tuple(self.repository._reference_view(dict(row)) for row in rows)

    def get_document_versions(self, reference_id: str) -> tuple[Mapping[str, Any], ...]:
        reference = self.service.get_reference(reference_id)
        return self.repository.document_versions(str(reference["biblio_id"]))

    def get_claims(self, reference_id: str) -> tuple[Mapping[str, Any], ...]:
        return self.repository.claims_for_reference(reference_id)

    def get_protocol(self, reference_id: str) -> Mapping[str, Any] | None:
        with self.artifacts._connect() as connection:
            row = connection.execute(
                "SELECT payload_json FROM ref_nodes WHERE reference_id=? AND node_type='PROTOCOL'",
                (reference_id,)).fetchone()
            return json.loads(row["payload_json"]) if row else None

    def get_provenance(self, reference_id: str) -> Mapping[str, Any]:
        reference = self.service.get_reference(reference_id)
        with self.artifacts._connect() as connection:
            edges = connection.execute(
                "SELECT e.* FROM ref_edges e JOIN ref_nodes n ON n.node_id=e.source_node_id "
                "WHERE n.reference_id=?", (reference_id,)).fetchall()
            claims = connection.execute(
                "SELECT claim_id,epistemic_source,extraction_method,verification_status "
                "FROM ref_claims WHERE reference_id=?", (reference_id,)).fetchall()
        return {"reference_id": reference_id,
                "d_level_tags": reference["d_level_tags"],
                "edges": [{"edge_id": e["edge_id"], "edge_type": e["edge_type"],
                           "provenance_level": e["provenance_level"],
                           "provenance_detail": e["provenance_detail"]} for e in edges],
                "claims": [dict(c) for c in claims]}

    # ------------------------------------------------------------- traversal
    def get_neighborhood(self, node_id: str, depth: int = 1) -> Mapping[str, Any]:
        depth = max(1, min(int(depth), 4))
        with self.artifacts._connect() as connection:
            start = connection.execute("SELECT * FROM ref_nodes WHERE node_id=?", (node_id,)).fetchone()
            if start is None:
                raise ReferenceNotFound(node_id)
            seen_nodes, seen_edges, frontier = {node_id}, set(), {node_id}
            for _ in range(depth):
                if not frontier:
                    break
                marks = ",".join("?" for _ in frontier)
                rows = connection.execute(
                    f"SELECT edge_id,source_node_id,target_node_id FROM ref_edges "
                    f"WHERE source_node_id IN ({marks}) OR target_node_id IN ({marks})",
                    tuple(frontier) + tuple(frontier)).fetchall()
                next_frontier = set()
                for edge in rows:
                    seen_edges.add(edge["edge_id"])
                    for endpoint in (edge["source_node_id"], edge["target_node_id"]):
                        if endpoint not in seen_nodes:
                            seen_nodes.add(endpoint)
                            next_frontier.add(endpoint)
                frontier = next_frontier
            nodes = [dict(connection.execute("SELECT * FROM ref_nodes WHERE node_id=?", (nid,)).fetchone())
                     for nid in seen_nodes]
            edges = [dict(connection.execute("SELECT * FROM ref_edges WHERE edge_id=?", (eid,)).fetchone())
                     for eid in seen_edges]
        return {"center": node_id, "depth": depth, "nodes": nodes, "edges": edges}

    # --------------------------------------------------------------- finders
    def _references_by_node_payload(self, node_type: str, key: str, value: str) -> tuple[Mapping[str, Any], ...]:
        with self.artifacts._connect() as connection:
            rows = connection.execute(
                "SELECT DISTINCT n.reference_id FROM ref_nodes n WHERE n.node_type=? "
                "AND LOWER(n.payload_json) LIKE ?",
                (node_type, f"%{value.casefold()}%")).fetchall()
            return tuple(self.service.get_reference(str(row["reference_id"])) for row in rows
                         if row["reference_id"])

    def find_by_construct(self, construct: str) -> tuple[Mapping[str, Any], ...]:
        with self.artifacts._connect() as connection:
            rows = connection.execute(
                "SELECT r.* FROM ref_constructs c JOIN ref_references r"
                " ON r.reference_id=c.reference_id WHERE c.construct=? ORDER BY r.reference_id",
                (construct,)).fetchall()
            return tuple(self.repository._reference_view(dict(row)) for row in rows)

    def find_by_paradigm(self, paradigm: str) -> tuple[Mapping[str, Any], ...]:
        with self.artifacts._connect() as connection:
            rows = connection.execute(
                "SELECT r.* FROM ref_paradigms p JOIN ref_references r"
                " ON r.reference_id=p.reference_id WHERE p.paradigm LIKE ? ORDER BY r.reference_id",
                (f"%{paradigm}%",)).fetchall()
            return tuple(self.repository._reference_view(dict(row)) for row in rows)

    def _references_by_edge_type(self, edge_type: str) -> tuple[Mapping[str, Any], ...]:
        with self.artifacts._connect() as connection:
            rows = connection.execute(
                "SELECT DISTINCT n.reference_id FROM ref_edges e "
                "JOIN ref_nodes n ON n.node_id=e.source_node_id WHERE e.edge_type=?",
                (edge_type,)).fetchall()
            return tuple(self.service.get_reference(str(row["reference_id"])) for row in rows
                         if row["reference_id"])

    def find_replications(self) -> tuple[Mapping[str, Any], ...]:
        return self._references_by_edge_type("REPLICATES")

    def find_critiques(self) -> tuple[Mapping[str, Any], ...]:
        return self._references_by_edge_type("CRITIQUES")

    def find_limitations(self) -> tuple[Mapping[str, Any], ...]:
        return self._references_by_edge_type("REPORTS_LIMITATION")

    def search_claims(self, text: str) -> tuple[Mapping[str, Any], ...]:
        with self.artifacts._connect() as connection:
            rows = connection.execute(
                "SELECT c.* FROM ref_claims c JOIN ref_claims_fts f ON c.claim_id=f.claim_id "
                "WHERE ref_claims_fts MATCH ? ORDER BY rank", (text,)).fetchall()
            return tuple({**dict(row), "locator": json.loads(row["locator_json"])} for row in rows)

    # ------------------------------------------------------------- snapshots
    def verify_snapshot(self, snapshot_id: str) -> Mapping[str, Any]:
        return self.service.verify_snapshot(snapshot_id)

    def snapshot_diff(self, left_id: str, right_id: str) -> Mapping[str, Any]:
        left = self.repository.get_snapshot(left_id)
        right = self.repository.get_snapshot(right_id)
        if left is None or right is None:
            raise ReferenceNotFound(f"snapshot not found: {left_id if left is None else right_id}")
        return {"left_snapshot_id": left_id, "right_snapshot_id": right_id,
                "same_node_set": left["node_set_hash"] == right["node_set_hash"],
                "same_edge_set": left["edge_set_hash"] == right["edge_set_hash"],
                "same_root": left["root_hash"] == right["root_hash"],
                "node_count_delta": right["node_count"] - left["node_count"],
                "edge_count_delta": right["edge_count"] - left["edge_count"],
                "left_root_hash": left["root_hash"], "right_root_hash": right["root_hash"]}

    # ------------------------------------------------------------ projections
    def projection(self, construct: str | None = None, paradigm: str | None = None,
                   author: str | None = None, year: str | None = None,
                   discipline: str | None = None, d_level: str | None = None,
                   status: str | None = None, verification_state: str | None = None
                   ) -> Mapping[str, Any]:
        """Derived read-only view; never a new snapshot, never a mutation."""
        references = self.repository.list_references()
        def keep(reference: Mapping[str, Any]) -> bool:
            if construct and construct not in reference["constructs"]:
                return False
            if paradigm and not any(paradigm.casefold() in p.casefold()
                                    for p in reference["experimental_paradigms"]):
                return False
            if discipline and discipline.casefold() not in reference["discipline"].casefold():
                return False
            if d_level and not any(tag.get("level") == d_level
                                   for tag in reference["d_level_tags"]):
                return False
            if status and reference["status"] != status:
                return False
            if verification_state and reference["verification_status"] != verification_state:
                return False
            if author or year:
                biblio = self._biblio(str(reference["biblio_id"]))
                if author and author.casefold() not in biblio["authors_json"].casefold():
                    return False
                if year and biblio["year"] != str(year):
                    return False
            return True
        selected = tuple(r for r in references if keep(r))
        return {"projection": True, "read_only": True, "is_snapshot": False,
                "filters": {"construct": construct, "paradigm": paradigm, "author": author,
                            "year": year, "discipline": discipline, "d_level": d_level,
                            "status": status, "verification_state": verification_state},
                "count": len(selected), "references": selected}

    def _biblio(self, biblio_id: str) -> Mapping[str, Any]:
        with self.artifacts._connect() as connection:
            row = connection.execute(
                "SELECT * FROM ref_bibliographic WHERE biblio_id=?", (biblio_id,)).fetchone()
            return dict(row) if row else {}
