"""Atomic corpus import for the scientific reference graph.

Consumes a versioned corpus package (manifest JSONL/CSV, reference records
JSONL, bibliography CSV/BibTeX, provenance JSONL, D2 protocol extraction,
limitations, design principles, version relationships) and commits it as an
immutable graph snapshot. The pipeline is:

    parse -> schema validate -> file verify -> SHA-256 verify -> identity
    resolution -> duplicate analysis -> conflict analysis -> ImportPlan
    -> (human review on conflict) -> stage CAS -> transaction -> graph snapshot
    -> commit.

A failed import leaves the previous snapshot valid. Nothing here auto-repairs
significant metadata, auto-merges duplicates, or promotes machine extraction to
a verified claim.
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

from terrario.lab.persistence import ArtifactRepository
from terrario.lab.persistence.canonical import content_hash, plain
from terrario.lab.referencegraph.domain import (
    BibliographicRecord, DocumentRecord, DocumentStatus, DocumentVersionType,
    DuplicateStatus, EdgeType, ImportAction, NodeType, ProvenanceLevel,
    QuarantineReason, ScientificReferenceRecord, SourceClaimRecord, ClaimLocator,
    ClaimType, VerificationStatus,
)
from terrario.lab.referencegraph.repository import (
    DuplicateCandidate, ReferenceGraphRepository, normalize_doi, normalize_text,
)
from terrario.lab.referencegraph.service import ReferenceGraphService

CORPUS_SCHEMA = "terrario.scientific-reference-corpus/v1"


@dataclass(frozen=True)
class PlannedRecord:
    external_id: str
    action: ImportAction
    detail: str


@dataclass(frozen=True)
class ImportPlan:
    plan_hash: str
    creates: tuple[PlannedRecord, ...]
    new_versions: tuple[PlannedRecord, ...]
    exact_duplicates: tuple[PlannedRecord, ...]
    conflicts: tuple[PlannedRecord, ...]
    quarantines: tuple[PlannedRecord, ...]

    @property
    def has_conflicts(self) -> bool:
        return bool(self.conflicts or self.quarantines)


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    records = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            records.append(json.loads(line))
    return records


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def parse_bibtex(text: str) -> list[dict[str, str]]:
    """Minimal BibTeX entry parser for the fields this phase consumes."""
    entries = []
    for match in re.finditer(r"@(\w+)\s*\{([^,]+),(.*?)\n\}", text, re.DOTALL):
        entry_type, key, body = match.group(1), match.group(2).strip(), match.group(3)
        fields: dict[str, str] = {"entry_type": entry_type.casefold(), "bibtex_key": key}
        for field_match in re.finditer(r"(\w+)\s*=\s*[\{\"](.+?)[\}\"]\s*,?\n", body + "\n"):
            fields[field_match.group(1).casefold()] = field_match.group(2).strip()
        entries.append(fields)
    return entries


class CorpusImporter:
    def __init__(self, artifacts: ArtifactRepository):
        self.artifacts = artifacts
        self.service = ReferenceGraphService(artifacts)
        self.repository = self.service.repository

    # ------------------------------------------------------------- planning
    def build_plan(self, corpus_root: str | Path) -> ImportPlan:
        root = Path(corpus_root)
        manifest = _read_jsonl(root / "manifest" / "CORPUS_MANIFEST.jsonl") or _read_csv(
            root / "manifest" / "CORPUS_MANIFEST.csv")
        creates: list[PlannedRecord] = []
        new_versions: list[PlannedRecord] = []
        exact: list[PlannedRecord] = []
        conflicts: list[PlannedRecord] = []
        quarantines: list[PlannedRecord] = []
        with self.artifacts._connect() as connection:
            for row in manifest:
                document_id = str(row.get("document_id", "")).strip()
                sha256 = str(row.get("sha256", "")).strip()
                rel = str(row.get("local_relative_path", "")).strip()
                if not document_id or not sha256:
                    quarantines.append(PlannedRecord(
                        document_id or rel or "unknown", ImportAction.QUARANTINE,
                        QuarantineReason.MALFORMED_METADATA.value))
                    continue
                existing = self.repository.get_document(sha256)
                if existing:
                    exact.append(PlannedRecord(document_id, ImportAction.EXACT_DUPLICATE, sha256))
                    continue
                doi = str(row.get("doi", "")).strip()
                if doi and doi != "UNKNOWN":
                    by_doi = self.repository.find_bibliographic_by_doi(connection, doi)
                    if by_doi and by_doi["doi"] != normalize_doi(doi):
                        conflicts.append(PlannedRecord(
                            document_id, ImportAction.CONFLICT,
                            QuarantineReason.CONFLICTING_DOI_IDENTITY.value))
                        continue
                creates.append(PlannedRecord(document_id, ImportAction.CREATE, sha256))
        plan_body = {"schema_version": CORPUS_SCHEMA,
                     "creates": [plain(x) for x in creates],
                     "new_versions": [plain(x) for x in new_versions],
                     "exact_duplicates": [plain(x) for x in exact],
                     "conflicts": [plain(x) for x in conflicts],
                     "quarantines": [plain(x) for x in quarantines]}
        return ImportPlan(content_hash(plan_body), tuple(creates), tuple(new_versions),
                          tuple(exact), tuple(conflicts), tuple(quarantines))

    # --------------------------------------------------------------- import
    def import_corpus(self, corpus_root: str | Path, actor_id: str = "corpus-import",
                      allow_with_quarantine: bool = True) -> Mapping[str, Any]:
        root = Path(corpus_root)
        plan = self.build_plan(root)
        if plan.conflicts and not allow_with_quarantine:
            return {"imported": False, "reason": "conflicts require human review",
                    "plan_hash": plan.plan_hash,
                    "conflicts": [plain(x) for x in plan.conflicts]}
        manifest = {str(r.get("document_id", "")).strip(): r
                    for r in (_read_jsonl(root / "manifest" / "CORPUS_MANIFEST.jsonl")
                              or _read_csv(root / "manifest" / "CORPUS_MANIFEST.csv"))}
        records = {str(r.get("reference_id", "")).strip(): r
                   for r in _read_jsonl(root / "metadata" / "REFERENCE_RECORDS.jsonl")}
        bibliography = {str(r.get("reference_id", "")).strip(): r
                        for r in _read_csv(root / "bibliography" / "references.csv")}
        protocols = {str(r.get("reference_id", "")).strip(): r
                     for r in _read_csv(root / "metadata" / "D2_PROTOCOL_EXTRACTION.csv")}
        limitations: dict[str, list[dict[str, str]]] = {}
        for row in _read_csv(root / "metadata" / "REFERENCE_LIMITATIONS.csv"):
            limitations.setdefault(str(row.get("reference_id", "")).strip(), []).append(row)
        principles: dict[str, list[dict[str, str]]] = {}
        for row in _read_csv(root / "metadata" / "DESIGN_PRINCIPLES.csv"):
            principles.setdefault(str(row.get("reference_id", "")).strip(), []).append(row)

        batch_id = self.artifacts._identifier("import-batch")
        stats = {"documents": 0, "references": 0, "claims": 0, "nodes": 0, "edges": 0,
                 "quarantine": 0, "skipped_exact": len(plan.exact_duplicates)}
        with self.artifacts.transaction() as connection:
            self._record_batch(connection, batch_id, root, plan, actor_id)
            for planned in plan.creates:
                row = manifest.get(planned.external_id)
                if row is None:
                    continue
                outcome = self._import_document(connection, root, row, batch_id)
                stats["quarantine"] += outcome.get("quarantined", 0)
                stats["documents"] += outcome.get("documents", 0)
            for reference_id, record in records.items():
                outcome = self._import_reference(
                    connection, reference_id, record, bibliography.get(reference_id),
                    protocols.get(reference_id), limitations.get(reference_id, []),
                    principles.get(reference_id, []), manifest, batch_id)
                for key in ("references", "claims", "nodes", "edges", "quarantine"):
                    stats[key] += outcome.get(key, 0)
            snapshot = self.service.create_snapshot(f"corpus import {batch_id}", connection)
            connection.execute(
                "UPDATE ref_import_batches SET snapshot_id=?, state=? WHERE batch_id=?",
                (snapshot.snapshot_id, "COMMITTED", batch_id))
        return {"imported": True, "batch_id": batch_id, "plan_hash": plan.plan_hash,
                "snapshot_id": snapshot.snapshot_id, "root_hash": snapshot.root_hash,
                "node_count": snapshot.node_count, "edge_count": snapshot.edge_count,
                "stats": stats}

    def _record_batch(self, connection, batch_id: str, root: Path,
                      plan: ImportPlan, actor_id: str) -> None:
        plan_json = json.dumps({"schema_version": CORPUS_SCHEMA,
                                "creates": [plain(x) for x in plan.creates],
                                "conflicts": [plain(x) for x in plan.conflicts],
                                "quarantines": [plain(x) for x in plan.quarantines]},
                               sort_keys=True)
        connection.execute(
            "INSERT INTO ref_import_batches(batch_id,source,plan_json,plan_hash,snapshot_id,"
            "state,recorded_at) VALUES(?,?,?,?,?,?,?)",
            (batch_id, str(root), plan_json, plan.plan_hash, None, "VALIDATED", self.artifacts.now()))

    # ------------------------------------------------------------- documents
    def _import_document(self, connection, root: Path, row: Mapping[str, Any],
                         batch_id: str) -> Mapping[str, int]:
        rel = str(row.get("local_relative_path", "")).strip()
        expected_sha = str(row.get("sha256", "")).strip()
        source = root / rel
        quarantined = 0
        if not source.is_file():
            self.repository.insert_quarantine(
                connection, QuarantineReason.MISSING_FILE.value, rel, batch_id, dict(row))
            return {"quarantined": 1, "documents": 0}
        data = source.read_bytes()
        if not data:
            self.repository.insert_quarantine(
                connection, QuarantineReason.ZERO_BYTE_DOCUMENT.value, rel, batch_id, dict(row))
            return {"quarantined": 1, "documents": 0}
        if data.lstrip()[:15].lower().startswith((b"<!doctype html", b"<html")):
            self.repository.insert_quarantine(
                connection, QuarantineReason.HTML_DISGUISED_AS_PDF.value, rel, batch_id, dict(row))
            return {"quarantined": 1, "documents": 0}
        actual_sha = hashlib.sha256(data).hexdigest()
        if actual_sha != expected_sha:
            self.repository.insert_quarantine(
                connection, QuarantineReason.HASH_MISMATCH.value, rel, batch_id,
                {**dict(row), "actual_sha256": actual_sha})
            return {"quarantined": 1, "documents": 0}
        # Re-verify dedup inside the serialized transaction: a concurrent import
        # may have committed this exact document between planning and commit.
        if connection.execute("SELECT 1 FROM ref_documents WHERE document_id=?",
                              (actual_sha,)).fetchone():
            return {"quarantined": 0, "documents": 0, "deduplicated": 1}
        blob = self.artifacts.blobs.put_bytes(data, str(row.get("mime_type", "application/pdf")))
        connection.execute(
            "INSERT OR IGNORE INTO blob_manifests(blob_hash,relative_path,size_bytes,"
            "media_type,created_at) VALUES(?,?,?,?,?)",
            (blob.blob_hash, blob.relative_path, blob.size_bytes, blob.media_type,
             self.artifacts.now()))
        version_type = self._version_type(str(row.get("version_type", "UNKNOWN_VERSION")))
        document = DocumentRecord(
            blob.blob_hash, blob.blob_hash, blob.media_type, blob.size_bytes, version_type,
            DocumentStatus.ACTIVE, self.artifacts.now(),
            str(row.get("access_date")) or None)
        self.repository.insert_document(connection, document)
        return {"quarantined": quarantined, "documents": 1}

    @staticmethod
    def _version_type(value: str) -> DocumentVersionType:
        try:
            return DocumentVersionType(value)
        except ValueError:
            return DocumentVersionType.UNKNOWN_VERSION

    # ------------------------------------------------------------ references
    def _import_reference(self, connection, reference_id: str, record: Mapping[str, Any],
                          biblio_row: Mapping[str, str] | None,
                          protocol_row: Mapping[str, str] | None,
                          limitation_rows: list[Mapping[str, str]],
                          principle_rows: list[Mapping[str, str]],
                          manifest: Mapping[str, Mapping[str, Any]],
                          batch_id: str) -> Mapping[str, int]:
        stats = {"references": 0, "claims": 0, "nodes": 0, "edges": 0, "quarantine": 0}
        existing = connection.execute(
            "SELECT reference_id FROM ref_references WHERE reference_id=?", (reference_id,)).fetchone()
        if existing:
            # Idempotent re-import: an existing reference record is never
            # destructively overwritten or merged; it is left untouched.
            return stats
        title = str(record.get("title", "")).strip()
        authors_raw = str(record.get("authors", "")).strip()
        authors = tuple(a.strip() for a in re.split(r"\s*(?:;| and )\s*", authors_raw) if a.strip())
        year = str(record.get("year", "")).strip()
        doi = (biblio_row or {}).get("doi") or "UNKNOWN"
        venue_name = (biblio_row or {}).get("venue") or "UNKNOWN"
        venue_id = self.repository.upsert_venue(connection, venue_name)
        for author in authors:
            self.repository.upsert_author(connection, author)
        normalized_title = normalize_text(title)
        identity_hash = BibliographicRecord.compute_identity(doi, normalized_title, authors, year)
        biblio = self.repository.find_bibliographic(connection, identity_hash)
        if biblio is None:
            biblio_id = self.artifacts._identifier("biblio")
            self.repository.insert_bibliographic(connection, BibliographicRecord(
                biblio_id, title, normalized_title, authors, year, venue_id, None,
                normalize_doi(doi), identity_hash, self.artifacts.now()))
        else:
            biblio_id = str(biblio["biblio_id"])
        primary_doc = None
        for doc_ref in record.get("paper_document_ids", ()) or ():
            candidate = self._document_id_for(connection, manifest, str(doc_ref))
            if candidate:
                primary_doc = candidate
                break
        d_level_tags = tuple({"level": level, "relevance": "PRIMARY_RELEVANCE",
                              "provenance": ProvenanceLevel.IMPORTED_METADATA.value}
                             for level in record.get("terrario_levels", ()) or ())
        reference = ScientificReferenceRecord(
            reference_id, biblio_id, primary_doc, str(record.get("reference_type", "UNKNOWN")),
            DocumentStatus.ACTIVE, d_level_tags, tuple(record.get("constructs", ()) or ()),
            tuple(record.get("experimental_paradigms", ()) or ()),
            str(record.get("discipline", "UNKNOWN")), str(record.get("code_url")) or None,
            self._verification(record.get("verification_status")), self.artifacts.now())
        self.repository.insert_reference(connection, reference)
        for construct in reference.constructs:
            connection.execute(
                "INSERT OR IGNORE INTO ref_constructs(reference_id,construct) VALUES(?,?)",
                (reference_id, construct))
        for paradigm in reference.experimental_paradigms:
            connection.execute(
                "INSERT OR IGNORE INTO ref_paradigms(reference_id,paradigm) VALUES(?,?)",
                (reference_id, paradigm))
        stats["references"] += 1

        ref_node = self.service._node(connection, NodeType.REFERENCE, reference_id,
                                      {"reference_id": reference_id, "title": title,
                                       "reference_type": reference.reference_type})
        stats["nodes"] += 1
        for construct in reference.constructs:
            construct_node = self.service._node(connection, NodeType.CONSTRUCT, reference_id,
                                                {"name": construct})
            self.service._edge(connection, EdgeType.STUDIES_CONSTRUCT, ref_node, construct_node,
                               ProvenanceLevel.IMPORTED_METADATA, "corpus reference record")
            stats["nodes"] += 1
            stats["edges"] += 1
        for paradigm in reference.experimental_paradigms:
            paradigm_node = self.service._node(connection, NodeType.PARADIGM, reference_id,
                                               {"name": paradigm})
            self.service._edge(connection, EdgeType.USES_PARADIGM, ref_node, paradigm_node,
                               ProvenanceLevel.IMPORTED_METADATA, "corpus reference record")
            stats["nodes"] += 1
            stats["edges"] += 1
        if protocol_row:
            protocol_node = self.service._node(connection, NodeType.PROTOCOL, reference_id,
                                               dict(protocol_row))
            self.service._edge(connection, EdgeType.IMPLEMENTS_PROTOCOL, ref_node, protocol_node,
                               self._protocol_provenance(protocol_row),
                               str(protocol_row.get("extraction_basis", "UNKNOWN")))
            stats["nodes"] += 1
            stats["edges"] += 1
        for row in limitation_rows:
            limitation_node = self.service._node(connection, NodeType.LIMITATION, reference_id,
                                                 dict(row))
            self.service._edge(connection, EdgeType.REPORTS_LIMITATION, ref_node, limitation_node,
                               ProvenanceLevel.SOURCE_DERIVED,
                               str(row.get("source_basis", "documentary extraction")))
            stats["nodes"] += 1
            stats["edges"] += 1
        for row in principle_rows:
            adaptation = self._adaptation_edge(str(row.get("adaptation_type", "TECHNICAL_REFERENCE")))
            principle_node = self.service._node(connection, NodeType.DESIGN_PRINCIPLE, reference_id,
                                                dict(row))
            self.service._edge(connection, adaptation, ref_node, principle_node,
                               ProvenanceLevel.SOURCE_DERIVED,
                               str(row.get("source_basis", "bibliographic/documentary extraction")))
            stats["nodes"] += 1
            stats["edges"] += 1
        for claim_text in record.get("known_limitations", ()) or ():
            claim = SourceClaimRecord(
                self.artifacts._identifier("claim"), reference_id, primary_doc, str(claim_text),
                normalize_text(str(claim_text)), ClaimType.SOURCE_REPORTED_CLAIM,
                ProvenanceLevel.SOURCE_DERIVED, "corpus reference record",
                self._verification(record.get("verification_status")), ClaimLocator(),
                "known_limitations", self.artifacts.now())
            self.repository.insert_claim(connection, claim)
            claim_node = self.service._node(connection, NodeType.SOURCE_CLAIM, reference_id,
                                            {"claim_id": claim.claim_id, "text": claim.claim_text})
            self.service._edge(connection, EdgeType.REPORTS_CLAIM, ref_node, claim_node,
                               ProvenanceLevel.SOURCE_DERIVED, "corpus reference record")
            stats["claims"] += 1
            stats["nodes"] += 1
            stats["edges"] += 1
        return stats

    def _document_id_for(self, connection, manifest: Mapping[str, Mapping[str, Any]],
                         doc_ref: str) -> str | None:
        row = manifest.get(doc_ref)
        if row is None:
            return None
        sha = str(row.get("sha256", "")).strip()
        if not sha:
            return None
        # Only bind a document that was actually imported (quarantined/missing
        # documents must not become a dangling foreign key).
        exists = connection.execute(
            "SELECT 1 FROM ref_documents WHERE document_id=?", (sha,)).fetchone()
        return sha if exists else None

    @staticmethod
    def _verification(value: Any) -> VerificationStatus:
        try:
            return VerificationStatus(str(value))
        except ValueError:
            return VerificationStatus.UNKNOWN

    @staticmethod
    def _protocol_provenance(row: Mapping[str, str]) -> ProvenanceLevel:
        basis = str(row.get("extraction_basis", "")).casefold()
        if "source_reported" in basis:
            return ProvenanceLevel.SOURCE_EXPLICIT
        return ProvenanceLevel.SOURCE_DERIVED

    @staticmethod
    def _adaptation_edge(value: str) -> EdgeType:
        try:
            return EdgeType(value)
        except ValueError:
            return EdgeType.TECHNICAL_REFERENCE
