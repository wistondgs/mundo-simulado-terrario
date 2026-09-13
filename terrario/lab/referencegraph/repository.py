"""Durable, append-only repository for the scientific reference graph."""
from __future__ import annotations

import json
import re
import unicodedata
from dataclasses import dataclass
from typing import Any, Mapping

from terrario.lab.persistence import ArtifactRepository
from terrario.lab.persistence.canonical import content_hash, plain
from terrario.lab.referencegraph.domain import (
    BibliographicRecord, DocumentRecord, DocumentStatus, DocumentVersionType,
    DuplicateStatus, EdgeType, GraphEdge, GraphNode, NodeType, ProvenanceLevel,
    ReferenceGraphSnapshot, ScientificReferenceRecord, SourceClaimRecord,
    VerificationStatus,
)


def normalize_text(value: str) -> str:
    """Lowercase, strip accents/punctuation, collapse whitespace."""
    decomposed = unicodedata.normalize("NFKD", value or "")
    stripped = "".join(char for char in decomposed if not unicodedata.combining(char))
    collapsed = re.sub(r"[^a-z0-9 ]+", " ", stripped.casefold())
    return re.sub(r"\s+", " ", collapsed).strip()


def normalize_doi(value: str | None) -> str | None:
    if not value:
        return None
    cleaned = value.strip().casefold()
    for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):]
    return cleaned or None


@dataclass(frozen=True)
class DuplicateCandidate:
    left_reference_id: str
    right_reference_id: str
    detection_method: str


class ReferenceGraphRepository:
    def __init__(self, artifacts: ArtifactRepository):
        self.artifacts = artifacts

    # -- documents ---------------------------------------------------------
    def insert_document(self, connection, record: DocumentRecord) -> None:
        connection.execute(
            "INSERT INTO ref_documents(document_id,cas_blob_hash,media_type,size_bytes,"
            "version_type,status,effective_at,recorded_at) VALUES(?,?,?,?,?,?,?,?)",
            (record.document_id, record.cas_blob_hash, record.media_type, record.size_bytes,
             record.version_type.value, record.status.value, record.effective_at, record.recorded_at))

    def get_document(self, document_id: str) -> Mapping[str, Any] | None:
        with self.artifacts._connect() as connection:
            row = connection.execute(
                "SELECT * FROM ref_documents WHERE document_id=?", (document_id,)).fetchone()
            return dict(row) if row else None

    # -- bibliographic -----------------------------------------------------
    def upsert_author(self, connection, display_name: str) -> str:
        normalized = normalize_text(display_name)
        row = connection.execute(
            "SELECT author_id FROM ref_authors WHERE normalized_name=?", (normalized,)).fetchone()
        if row:
            return str(row["author_id"])
        author_id = self.artifacts._identifier("author")
        connection.execute(
            "INSERT INTO ref_authors(author_id,display_name,normalized_name,recorded_at) VALUES(?,?,?,?)",
            (author_id, display_name, normalized, self.artifacts.now()))
        return author_id

    def upsert_venue(self, connection, name: str, venue_type: str = "UNKNOWN") -> str:
        normalized = normalize_text(name)
        row = connection.execute(
            "SELECT venue_id FROM ref_venues WHERE normalized_name=?", (normalized,)).fetchone()
        if row:
            return str(row["venue_id"])
        venue_id = self.artifacts._identifier("venue")
        connection.execute(
            "INSERT INTO ref_venues(venue_id,name,normalized_name,venue_type,recorded_at) VALUES(?,?,?,?,?)",
            (venue_id, name, normalized, venue_type, self.artifacts.now()))
        return venue_id

    def find_bibliographic(self, connection, identity_hash: str) -> Mapping[str, Any] | None:
        row = connection.execute(
            "SELECT * FROM ref_bibliographic WHERE identity_hash=?", (identity_hash,)).fetchone()
        return dict(row) if row else None

    def find_bibliographic_by_doi(self, connection, doi: str) -> Mapping[str, Any] | None:
        row = connection.execute(
            "SELECT * FROM ref_bibliographic WHERE doi=?", (normalize_doi(doi),)).fetchone()
        return dict(row) if row else None

    def insert_bibliographic(self, connection, record: BibliographicRecord) -> None:
        connection.execute(
            "INSERT INTO ref_bibliographic(biblio_id,title,normalized_title,authors_json,year,"
            "venue_id,edition,doi,identity_hash,recorded_at) VALUES(?,?,?,?,?,?,?,?,?,?)",
            (record.biblio_id, record.title, record.normalized_title, json.dumps(list(record.authors)),
             record.year, record.venue_id, record.edition, normalize_doi(record.doi),
             record.identity_hash, record.recorded_at))

    # -- references --------------------------------------------------------
    def insert_reference(self, connection, record: ScientificReferenceRecord) -> None:
        connection.execute(
            "INSERT INTO ref_references(reference_id,biblio_id,primary_document_id,reference_type,"
            "status,d_level_tags_json,constructs_json,experimental_paradigms_json,discipline,"
            "code_url,verification_status,recorded_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (record.reference_id, record.biblio_id, record.primary_document_id, record.reference_type,
             record.status.value, json.dumps([dict(x) for x in record.d_level_tags]),
             json.dumps(list(record.constructs)), json.dumps(list(record.experimental_paradigms)),
             record.discipline, record.code_url, record.verification_status.value, record.recorded_at))

    def get_reference(self, reference_id: str) -> Mapping[str, Any] | None:
        with self.artifacts._connect() as connection:
            row = connection.execute(
                "SELECT * FROM ref_references WHERE reference_id=?", (reference_id,)).fetchone()
            return self._reference_view(dict(row)) if row else None

    def list_references(self) -> tuple[Mapping[str, Any], ...]:
        with self.artifacts._connect() as connection:
            rows = connection.execute("SELECT * FROM ref_references ORDER BY reference_id").fetchall()
            return tuple(self._reference_view(dict(row)) for row in rows)

    @staticmethod
    def _reference_view(row: Mapping[str, Any]) -> Mapping[str, Any]:
        return {**row, "d_level_tags": json.loads(row["d_level_tags_json"]),
                "constructs": json.loads(row["constructs_json"]),
                "experimental_paradigms": json.loads(row["experimental_paradigms_json"])}

    # -- document versions ---------------------------------------------------
    def insert_document_version(self, connection, version_id: str, document_id: str, biblio_id: str,
                                version_type: DocumentVersionType, relation: EdgeType | None,
                                target_document_id: str | None) -> None:
        connection.execute(
            "INSERT INTO ref_document_versions(version_id,document_id,biblio_id,version_type,"
            "relation,relation_target_document_id,recorded_at) VALUES(?,?,?,?,?,?,?)",
            (version_id, document_id, biblio_id, version_type.value,
             relation.value if relation else None, target_document_id, self.artifacts.now()))

    def document_versions(self, biblio_id: str) -> tuple[Mapping[str, Any], ...]:
        with self.artifacts._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM ref_document_versions WHERE biblio_id=? ORDER BY recorded_at",
                (biblio_id,)).fetchall()
            return tuple(dict(row) for row in rows)

    # -- claims --------------------------------------------------------------
    def insert_claim(self, connection, record: SourceClaimRecord) -> None:
        connection.execute(
            "INSERT INTO ref_claims(claim_id,reference_id,document_id,claim_text,normalized_summary,"
            "claim_type,epistemic_source,extraction_method,verification_status,locator_json,context,"
            "recorded_at) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
            (record.claim_id, record.reference_id, record.document_id, record.claim_text,
             record.normalized_summary, record.claim_type.value, record.epistemic_source.value,
             record.extraction_method, record.verification_status.value,
             json.dumps(plain(record.locator)), record.context, record.recorded_at))
        connection.execute(
            "INSERT INTO ref_claims_fts(claim_id,claim_text,normalized_summary) VALUES(?,?,?)",
            (record.claim_id, record.claim_text, record.normalized_summary))

    def claims_for_reference(self, reference_id: str) -> tuple[Mapping[str, Any], ...]:
        with self.artifacts._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM ref_claims WHERE reference_id=? ORDER BY recorded_at",
                (reference_id,)).fetchall()
            return tuple({**dict(row), "locator": json.loads(row["locator_json"])} for row in rows)

    # -- nodes / edges -------------------------------------------------------
    def insert_node(self, connection, node: GraphNode) -> None:
        connection.execute(
            "INSERT INTO ref_nodes(node_id,node_type,reference_id,payload_json,node_hash,recorded_at)"
            " VALUES(?,?,?,?,?,?)",
            (node.node_id, node.node_type.value, node.reference_id, json.dumps(plain(node.payload)),
             node.node_hash, node.recorded_at))

    def insert_edge(self, connection, edge: GraphEdge) -> None:
        connection.execute(
            "INSERT INTO ref_edges(edge_id,edge_type,source_node_id,target_node_id,provenance_level,"
            "provenance_detail,edge_hash,recorded_at) VALUES(?,?,?,?,?,?,?,?)",
            (edge.edge_id, edge.edge_type.value, edge.source_node_id, edge.target_node_id,
             edge.provenance_level.value, edge.provenance_detail, edge.edge_hash, edge.recorded_at))

    def all_nodes(self, connection=None) -> tuple[Mapping[str, Any], ...]:
        if connection is not None:
            rows = connection.execute("SELECT * FROM ref_nodes ORDER BY node_id").fetchall()
            return tuple(dict(row) for row in rows)
        with self.artifacts._connect() as connection:
            rows = connection.execute("SELECT * FROM ref_nodes ORDER BY node_id").fetchall()
            return tuple(dict(row) for row in rows)

    def all_edges(self, connection=None) -> tuple[Mapping[str, Any], ...]:
        if connection is not None:
            rows = connection.execute("SELECT * FROM ref_edges ORDER BY edge_id").fetchall()
            return tuple(dict(row) for row in rows)
        with self.artifacts._connect() as connection:
            rows = connection.execute("SELECT * FROM ref_edges ORDER BY edge_id").fetchall()
            return tuple(dict(row) for row in rows)

    def node_by_hash(self, connection, node_hash: str) -> Mapping[str, Any] | None:
        row = connection.execute("SELECT * FROM ref_nodes WHERE node_hash=?", (node_hash,)).fetchone()
        return dict(row) if row else None

    # -- snapshots -----------------------------------------------------------
    def insert_snapshot(self, connection, snapshot: ReferenceGraphSnapshot) -> None:
        connection.execute(
            "INSERT INTO ref_snapshots(snapshot_id,parent_snapshot_id,schema_version,node_set_hash,"
            "edge_set_hash,root_hash,node_count,edge_count,provenance,created_at)"
            " VALUES(?,?,?,?,?,?,?,?,?,?)",
            (snapshot.snapshot_id, snapshot.parent_snapshot_id, snapshot.schema_version,
             snapshot.node_set_hash, snapshot.edge_set_hash, snapshot.root_hash, snapshot.node_count,
             snapshot.edge_count, snapshot.provenance, snapshot.created_at))

    def latest_snapshot(self, connection=None) -> Mapping[str, Any] | None:
        query = ("SELECT s.* FROM ref_snapshots s LEFT JOIN ref_snapshots child"
                 " ON child.parent_snapshot_id = s.snapshot_id WHERE child.snapshot_id IS NULL"
                 " ORDER BY s.created_at DESC LIMIT 1")
        if connection is not None:
            row = connection.execute(query).fetchone()
            return dict(row) if row else None
        with self.artifacts._connect() as connection:
            row = connection.execute(query).fetchone()
            return dict(row) if row else None

    def get_snapshot(self, snapshot_id: str) -> Mapping[str, Any] | None:
        with self.artifacts._connect() as connection:
            row = connection.execute(
                "SELECT * FROM ref_snapshots WHERE snapshot_id=?", (snapshot_id,)).fetchone()
            return dict(row) if row else None

    def snapshot_chain(self, snapshot_id: str) -> tuple[Mapping[str, Any], ...]:
        chain: list[Mapping[str, Any]] = []
        with self.artifacts._connect() as connection:
            cursor = connection.execute(
                "SELECT * FROM ref_snapshots WHERE snapshot_id=?", (snapshot_id,)).fetchone()
            seen = set()
            while cursor:
                if cursor["snapshot_id"] in seen:
                    break
                seen.add(cursor["snapshot_id"])
                chain.append(dict(cursor))
                parent = cursor["parent_snapshot_id"]
                cursor = connection.execute(
                    "SELECT * FROM ref_snapshots WHERE snapshot_id=?", (parent,)).fetchone() if parent else None
        return tuple(chain)

    # -- duplicates ----------------------------------------------------------
    def insert_duplicate(self, connection, candidate: DuplicateCandidate,
                         status: DuplicateStatus) -> None:
        connection.execute(
            "INSERT INTO ref_duplicates(duplicate_id,left_reference_id,right_reference_id,"
            "detection_method,status,recorded_at) VALUES(?,?,?,?,?,?)",
            (self.artifacts._identifier("duplicate"), candidate.left_reference_id,
             candidate.right_reference_id, candidate.detection_method, status.value,
             self.artifacts.now()))

    # -- quarantine ----------------------------------------------------------
    def insert_quarantine(self, connection, reason: str, source: str, batch_id: str | None,
                          payload: Mapping[str, Any], resolution_state: str = "PENDING") -> str:
        quarantine_id = self.artifacts._identifier("quarantine")
        connection.execute(
            "INSERT INTO ref_quarantine(quarantine_id,reason,source,batch_id,payload_json,"
            "resolution_state,recorded_at) VALUES(?,?,?,?,?,?,?)",
            (quarantine_id, reason, source, batch_id, json.dumps(plain(payload)),
             resolution_state, self.artifacts.now()))
        return quarantine_id

    def list_quarantine(self) -> tuple[Mapping[str, Any], ...]:
        with self.artifacts._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM ref_quarantine ORDER BY recorded_at").fetchall()
            return tuple({**dict(row), "payload": json.loads(row["payload_json"])} for row in rows)

    # -- verification --------------------------------------------------------
    def insert_verification(self, connection, subject_id: str, report: Mapping[str, Any]) -> str:
        verification_id = self.artifacts._identifier("verification")
        connection.execute(
            "INSERT INTO ref_verifications(verification_id,subject_id,report_json,recorded_at)"
            " VALUES(?,?,?,?)",
            (verification_id, subject_id, json.dumps(plain(report)), self.artifacts.now()))
        return verification_id
