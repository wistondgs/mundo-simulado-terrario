"""Orchestration for the scientific reference graph.

Builds immutable graph snapshots, runs the structured integrity verifier, and
coordinates document/reference/claim recording. This service never writes the
TheoryGraph, never writes the EvidenceGraph, never creates a hypothesis or an
ExperimentDraft, never preregisters, and never executes a trial.
"""
from __future__ import annotations

import json
from typing import Any, Mapping

from terrario.lab.persistence import ArtifactRepository
from terrario.lab.persistence.canonical import content_hash, plain
from terrario.lab.referencegraph.domain import (
    BibliographicRecord, DocumentRecord, DocumentStatus, DocumentVersionType,
    EdgeType, GraphEdge, GraphNode, NodeType, ProvenanceLevel,
    ReferenceGraphSnapshot, SCHEMA_VERSION, SNAPSHOT_SCHEMA_VERSION,
    ScientificReferenceRecord, SourceClaimRecord, VerificationStatus,
)
from terrario.lab.referencegraph.repository import ReferenceGraphRepository


class ReferenceGraphService:
    def __init__(self, artifacts: ArtifactRepository):
        self.artifacts = artifacts
        self.repository = ReferenceGraphRepository(artifacts)

    # ------------------------------------------------------------------ ids
    def _node(self, connection, node_type: NodeType, reference_id: str | None,
              payload: Mapping[str, Any]) -> GraphNode:
        body = {"node_type": node_type.value, "reference_id": reference_id,
                "payload": plain(payload)}
        node_hash = content_hash(body)
        existing = self.repository.node_by_hash(connection, node_hash)
        if existing:
            return GraphNode(str(existing["node_id"]), node_type, reference_id,
                             payload, node_hash, str(existing["recorded_at"]))
        node = GraphNode(self.artifacts._identifier(f"node-{node_type.value.casefold()}"),
                         node_type, reference_id, payload, node_hash, self.artifacts.now())
        self.repository.insert_node(connection, node)
        return node

    def _edge(self, connection, edge_type: EdgeType, source: GraphNode, target: GraphNode,
              provenance: ProvenanceLevel, detail: str) -> GraphEdge:
        body = {"edge_type": edge_type.value, "source_node_hash": source.node_hash,
                "target_node_hash": target.node_hash, "provenance_level": provenance.value,
                "provenance_detail": detail}
        edge_hash = content_hash(body)
        edge = GraphEdge(self.artifacts._identifier(f"edge-{edge_type.value.casefold()}"),
                         edge_type, source.node_id, target.node_id, provenance, detail,
                         edge_hash, self.artifacts.now())
        self.repository.insert_edge(connection, edge)
        return edge

    # ------------------------------------------------------------- snapshots
    def _compute_root(self, connection) -> tuple[str, str, str, int, int]:
        nodes = self.repository.all_nodes(connection)
        edges = self.repository.all_edges(connection)
        node_set_hash = content_hash([row["node_hash"] for row in nodes])
        edge_set_hash = content_hash([row["edge_hash"] for row in edges])
        return node_set_hash, edge_set_hash, "", len(nodes), len(edges)

    def create_snapshot(self, provenance: str, connection=None) -> ReferenceGraphSnapshot:
        own = connection is None
        if own:
            connection = self.artifacts._connect()
            connection.execute("BEGIN IMMEDIATE")
        try:
            node_set_hash, edge_set_hash, _, node_count, edge_count = self._compute_root(connection)
            parent = self.repository.latest_snapshot(connection)
            parent_id = str(parent["snapshot_id"]) if parent else None
            root = content_hash({
                "schema_version": SNAPSHOT_SCHEMA_VERSION, "node_set_hash": node_set_hash,
                "edge_set_hash": edge_set_hash, "parent_snapshot_id": parent_id,
                "parent_root_hash": parent["root_hash"] if parent else None})
            existing = connection.execute(
                "SELECT * FROM ref_snapshots WHERE root_hash=?", (root,)).fetchone()
            if existing:
                if own:
                    connection.commit()
                return ReferenceGraphSnapshot(
                    str(existing["snapshot_id"]), existing["parent_snapshot_id"],
                    str(existing["schema_version"]), str(existing["node_set_hash"]),
                    str(existing["edge_set_hash"]), str(existing["root_hash"]),
                    int(existing["node_count"]), int(existing["edge_count"]),
                    str(existing["provenance"]), str(existing["created_at"]))
            snapshot = ReferenceGraphSnapshot(
                self.artifacts._identifier("snapshot"), parent_id, SNAPSHOT_SCHEMA_VERSION,
                node_set_hash, edge_set_hash, root, node_count, edge_count, provenance,
                self.artifacts.now())
            self.repository.insert_snapshot(connection, snapshot)
            if own:
                connection.commit()
            return snapshot
        except Exception:
            if own:
                connection.rollback()
            raise
        finally:
            if own:
                connection.close()

    def verify_snapshot(self, snapshot_id: str) -> Mapping[str, Any]:
        snapshot = self.repository.get_snapshot(snapshot_id)
        if snapshot is None:
            return {"snapshot_id": snapshot_id, "valid": False, "failures": ["SNAPSHOT_NOT_FOUND"]}
        with self.artifacts._connect() as connection:
            node_set_hash, edge_set_hash, _, node_count, edge_count = self._compute_root(connection)
        failures = []
        if node_set_hash != snapshot["node_set_hash"]:
            failures.append("NODE_SET_HASH_MISMATCH")
        if edge_set_hash != snapshot["edge_set_hash"]:
            failures.append("EDGE_SET_HASH_MISMATCH")
        parent = self.repository.get_snapshot(snapshot["parent_snapshot_id"]) if snapshot["parent_snapshot_id"] else None
        expected_root = content_hash({
            "schema_version": snapshot["schema_version"], "node_set_hash": node_set_hash,
            "edge_set_hash": edge_set_hash, "parent_snapshot_id": snapshot["parent_snapshot_id"],
            "parent_root_hash": parent["root_hash"] if parent else None})
        if expected_root != snapshot["root_hash"]:
            failures.append("ROOT_HASH_MISMATCH")
        return {"snapshot_id": snapshot_id, "valid": not failures, "failures": failures,
                "node_count": snapshot["node_count"], "edge_count": snapshot["edge_count"],
                "root_hash": snapshot["root_hash"]}

    # -------------------------------------------------------------- verifier
    def verify(self) -> Mapping[str, Any]:
        failures: list[str] = []
        warnings: list[str] = []
        with self.artifacts._connect() as connection:
            nodes = self.repository.all_nodes(connection)
            edges = self.repository.all_edges(connection)
            node_ids = {row["node_id"] for row in nodes}
            # edge endpoints exist + provenance present
            for edge in edges:
                if edge["source_node_id"] not in node_ids:
                    failures.append(f"EDGE_SOURCE_MISSING:{edge['edge_id']}")
                if edge["target_node_id"] not in node_ids:
                    failures.append(f"EDGE_TARGET_MISSING:{edge['edge_id']}")
                if not edge["provenance_level"]:
                    failures.append(f"EDGE_PROVENANCE_MISSING:{edge['edge_id']}")
                expected = content_hash({
                    "edge_type": edge["edge_type"],
                    "source_node_hash": self._hash_of(connection, edge["source_node_id"]),
                    "target_node_hash": self._hash_of(connection, edge["target_node_id"]),
                    "provenance_level": edge["provenance_level"],
                    "provenance_detail": edge["provenance_detail"]})
                if expected != edge["edge_hash"]:
                    failures.append(f"EDGE_HASH_MISMATCH:{edge['edge_id']}")
            # node hashes
            for node in nodes:
                expected = content_hash({
                    "node_type": node["node_type"], "reference_id": node["reference_id"],
                    "payload": json.loads(node["payload_json"])})
                if expected != node["node_hash"]:
                    failures.append(f"NODE_HASH_MISMATCH:{node['node_id']}")
            # documents: CAS integrity + hash matches bytes
            documents = [dict(r) for r in connection.execute("SELECT * FROM ref_documents")]
            for doc in documents:
                if doc["document_id"] != doc["cas_blob_hash"]:
                    failures.append(f"DOCUMENT_ID_NOT_CONTENT_HASH:{doc['document_id']}")
                if not self.artifacts.blobs.verify(doc["cas_blob_hash"]):
                    failures.append(f"DOCUMENT_CAS_INVALID:{doc['document_id']}")
            # claims: source binding + analyst-inference not SOURCE_EXPLICIT
            claims = [dict(r) for r in connection.execute("SELECT * FROM ref_claims")]
            reference_ids = {r["reference_id"] for r in connection.execute("SELECT reference_id FROM ref_references")}
            for claim in claims:
                if claim["reference_id"] not in reference_ids:
                    failures.append(f"CLAIM_SOURCE_MISSING:{claim['claim_id']}")
                if (claim["claim_type"] == "ANALYST_INTERPRETATION"
                        and claim["epistemic_source"] == "SOURCE_EXPLICIT"):
                    failures.append(f"ANALYST_INFERENCE_MARKED_SOURCE_EXPLICIT:{claim['claim_id']}")
            # retracted references not deleted (status preserved)
            for row in connection.execute("SELECT reference_id,status FROM ref_references"):
                if row["status"] == "RETRACTED":
                    warnings.append(f"RETRACTED_REFERENCE_RETAINED:{row['reference_id']}")
            # snapshot ancestry
            latest = self.repository.latest_snapshot(connection)
            snapshot_valid = None
            if latest:
                seen, cursor, ancestry_ok = set(), latest, True
                while cursor:
                    if cursor["snapshot_id"] in seen:
                        ancestry_ok = False
                        failures.append("SNAPSHOT_ANCESTRY_CYCLE")
                        break
                    seen.add(cursor["snapshot_id"])
                    parent_id = cursor["parent_snapshot_id"]
                    if parent_id is None:
                        break
                    parent = self.repository.get_snapshot(parent_id)
                    if parent is None:
                        ancestry_ok = False
                        failures.append(f"SNAPSHOT_PARENT_MISSING:{parent_id}")
                        break
                    cursor = parent
                snapshot_valid = ancestry_ok
            else:
                warnings.append("NO_SNAPSHOT")
        report = {
            "schema_version": SCHEMA_VERSION, "valid": not failures, "failures": failures,
            "warnings": warnings, "node_count": len(nodes), "edge_count": len(edges),
            "document_count": len(documents), "claim_count": len(claims),
            "snapshot_present": latest is not None, "snapshot_ancestry_valid": snapshot_valid,
            "scientific_execution": False, "evidence_publication": False,
            "theory_graph_modified": False, "evidence_graph_modified": False}
        with self.artifacts.transaction() as connection:
            self.repository.insert_verification(connection, "reference-graph", report)
        return report

    @staticmethod
    def _hash_of(connection, node_id: str) -> str | None:
        row = connection.execute("SELECT node_hash FROM ref_nodes WHERE node_id=?", (node_id,)).fetchone()
        return str(row["node_hash"]) if row else None

    # ---------------------------------------------------------------- views
    def get_reference(self, reference_id: str) -> Mapping[str, Any]:
        reference = self.repository.get_reference(reference_id)
        if reference is None:
            from terrario.lab.referencegraph.domain import ReferenceNotFound
            raise ReferenceNotFound(reference_id)
        return reference

    def list_references(self) -> tuple[Mapping[str, Any], ...]:
        return self.repository.list_references()

    def counts(self) -> Mapping[str, int]:
        with self.artifacts._connect() as connection:
            def count(table: str) -> int:
                return int(connection.execute(f"SELECT count(*) FROM {table}").fetchone()[0])
            return {"references": count("ref_references"), "documents": count("ref_documents"),
                    "claims": count("ref_claims"), "nodes": count("ref_nodes"),
                    "edges": count("ref_edges"), "snapshots": count("ref_snapshots"),
                    "quarantine": count("ref_quarantine"),
                    "bibliographic": count("ref_bibliographic")}
