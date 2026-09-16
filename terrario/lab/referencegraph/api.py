"""Versioned HTTP contract for the scientific reference graph.

Read/query routes and mutating governance routes are kept separate. This API
exposes no route that writes the TheoryGraph, writes the EvidenceGraph, creates
a hypothesis, creates an ExperimentDraft, preregisters, or executes a trial.
"""
from __future__ import annotations

import secrets
from typing import Any, Mapping

from terrario.lab.persistence import ArtifactNotFound, ProvenanceConflict
from terrario.lab.referencegraph.domain import ReferenceNotFound
from terrario.lab.referencegraph.import_corpus import CorpusImporter
from terrario.lab.referencegraph.queries import ReferenceGraphQueries
from terrario.lab.referencegraph.service import ReferenceGraphService


def _header(headers: Mapping[str, str], name: str) -> str | None:
    """Read HTTP fields case-insensitively, as required by HTTP."""
    wanted = name.casefold()
    return next((str(value) for key, value in headers.items()
                 if str(key).casefold() == wanted), None)


class ReferenceGraphAPI:
    def __init__(self, service: ReferenceGraphService):
        self.service = service
        self.queries = ReferenceGraphQueries(service.artifacts)
        self.importer = CorpusImporter(service.artifacts)
        self.session_id = f"session-{secrets.token_hex(16)}"
        self.csrf_token = secrets.token_urlsafe(32)

    def dispatch(self, method: str, parts: list[str], query: Mapping[str, list[str]],
                 payload: Mapping[str, Any] | None, headers: Mapping[str, str] | None = None):
        request_id = f"req-{secrets.token_hex(8)}"
        p, headers = dict(payload or {}), dict(headers or {})
        try:
            if method != "GET" and headers and self._is_mutating(parts):
                self._authorize(headers)
            status, data = self._route(method, parts, query, p, headers)
            meta = {"request_id": request_id, "schema_version": "terrario.api/v1"}
            return status, {"data": data, "meta": meta}
        except Exception as exc:
            code = getattr(exc, "code", "INVALID_REQUEST")
            if isinstance(exc, (ArtifactNotFound, ReferenceNotFound)): status = 404
            elif isinstance(exc, ProvenanceConflict): status = 409
            elif isinstance(exc, PermissionError): status = 403
            elif isinstance(exc, (ValueError, KeyError)): status = 400
            else: status = 500
            return status, {"error": {"code": code, "message": str(exc), "details": {}, "request_id": request_id}}

    def _route(self, method, parts, query, p, headers):
        # parts begins after "reference-graph"
        if method == "GET" and parts == []:
            return 200, {"counts": self.service.counts(), "scientific_execution": False,
                         "evidence_publication": False, "theory_graph_modified": False,
                         "evidence_graph_modified": False}
        if method == "GET" and parts == ["references"]:
            return 200, {"items": self.service.list_references(), "next_cursor": None}
        if method == "POST" and parts == ["references", "find"]:
            return 200, {"items": self.queries.find_references(
                p.get("title"), p.get("doi"), p.get("year"), p.get("author"))}
        if len(parts) >= 2 and parts[0] == "references":
            reference_id = parts[1]
            if method == "GET" and len(parts) == 2:
                return 200, self.queries.get_reference(reference_id)
            if method == "GET" and parts[2:] == ["claims"]:
                return 200, {"items": self.queries.get_claims(reference_id)}
            if method == "GET" and parts[2:] == ["protocol"]:
                return 200, self.queries.get_protocol(reference_id) or {}
            if method == "GET" and parts[2:] == ["provenance"]:
                return 200, self.queries.get_provenance(reference_id)
            if method == "GET" and parts[2:] == ["document-versions"]:
                return 200, {"items": self.queries.get_document_versions(reference_id)}
        if method == "POST" and parts == ["claims", "search"]:
            return 200, {"items": self.queries.search_claims(str(p["text"]))}
        if method == "POST" and parts == ["find", "by-construct"]:
            return 200, {"items": self.queries.find_by_construct(str(p["construct"]))}
        if method == "POST" and parts == ["find", "by-paradigm"]:
            return 200, {"items": self.queries.find_by_paradigm(str(p["paradigm"]))}
        if method == "GET" and parts == ["find", "replications"]:
            return 200, {"items": self.queries.find_replications()}
        if method == "GET" and parts == ["find", "critiques"]:
            return 200, {"items": self.queries.find_critiques()}
        if method == "GET" and parts == ["find", "limitations"]:
            return 200, {"items": self.queries.find_limitations()}
        if method == "POST" and parts == ["projection"]:
            return 200, self.queries.projection(
                p.get("construct"), p.get("paradigm"), p.get("author"), p.get("year"),
                p.get("discipline"), p.get("d_level"), p.get("status"), p.get("verification_state"))
        if method == "POST" and parts == ["neighborhood"]:
            return 200, self.queries.get_neighborhood(str(p["node_id"]), int(p.get("depth", 1)))
        if method == "GET" and parts == ["snapshots"]:
            latest = self.service.repository.latest_snapshot()
            return 200, {"latest": latest}
        if method == "POST" and parts == ["snapshots", "diff"]:
            return 200, self.queries.snapshot_diff(str(p["left_snapshot_id"]), str(p["right_snapshot_id"]))
        if len(parts) == 3 and parts[0] == "snapshots" and parts[2] == "verify":
            return 200, self.queries.verify_snapshot(parts[1])
        if method == "GET" and parts == ["verify"]:
            return 200, self.service.verify()
        if method == "GET" and parts == ["quarantine"]:
            return 200, {"items": self.service.repository.list_quarantine()}
        # mutating governance routes (CSRF/local enforced above)
        if method == "POST" and parts == ["imports", "plan"]:
            plan = self.importer.build_plan(str(p["corpus_root"]))
            return 200, {"plan_hash": plan.plan_hash,
                         "creates": len(plan.creates), "new_versions": len(plan.new_versions),
                         "exact_duplicates": len(plan.exact_duplicates),
                         "conflicts": len(plan.conflicts), "quarantines": len(plan.quarantines),
                         "has_conflicts": plan.has_conflicts}
        if method == "POST" and parts == ["imports"]:
            return 201, self.importer.import_corpus(
                str(p["corpus_root"]), "local-user", bool(p.get("allow_with_quarantine", True)))
        if method == "POST" and parts == ["snapshots"]:
            snapshot = self.service.create_snapshot(str(p.get("provenance", "manual snapshot")))
            return 201, {"snapshot_id": snapshot.snapshot_id, "root_hash": snapshot.root_hash,
                         "node_count": snapshot.node_count, "edge_count": snapshot.edge_count}
        raise ArtifactNotFound("/api/v1/reference-graph/" + "/".join(parts))

    def _is_mutating(self, parts: list[str]) -> bool:
        # Only corpus imports and manual snapshot creation mutate governance
        # state; reference/claim/protocol/provenance/find/projection queries are
        # read-only even when sent as POST.
        return bool(parts) and parts[0] in {"imports", "snapshots"}

    def _authorize(self, headers: Mapping[str, str]) -> None:
        host = _header(headers, "Host") or ""
        origin = _header(headers, "Origin") or ""
        if host and not (host.startswith("127.0.0.1") or host.startswith("localhost")):
            raise PermissionError("non-local Host rejected")
        if origin and not (origin.startswith("http://127.0.0.1") or origin.startswith("http://localhost")):
            raise PermissionError("non-local Origin rejected")
        if _header(headers, "X-CSRF-Token") != self.csrf_token:
            raise PermissionError("invalid CSRF token")
