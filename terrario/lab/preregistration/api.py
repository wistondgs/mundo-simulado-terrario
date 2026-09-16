"""Versioned HTTP contract for preregistration governance."""
from __future__ import annotations

import secrets
from typing import Any, Mapping

from terrario.lab.persistence import ArtifactNotFound, DuplicateArtifact, ProvenanceConflict
from terrario.lab.preregistration.domain import PreregistrationError


def _header(headers: Mapping[str, str], name: str) -> str | None:
    """Return an HTTP field without depending on its transport spelling."""
    wanted = name.casefold()
    return next((str(value) for key, value in headers.items()
                 if str(key).casefold() == wanted), None)


class PreregistrationAPI:
    def __init__(self, service):
        self.service = service
        self.session_id = f"session-{secrets.token_hex(16)}"
        self.csrf_token = secrets.token_urlsafe(32)

    def dispatch(self, method: str, parts: list[str], query: Mapping[str, list[str]],
                 payload: Mapping[str, Any] | None, headers: Mapping[str, str] | None = None):
        request_id = f"req-{secrets.token_hex(8)}"
        p, headers = dict(payload or {}), dict(headers or {})
        try:
            if method != "GET" and headers:
                self._authorize(headers)
            status, data, etag = self._route(method, parts, query, p, headers)
            meta = {"request_id": request_id, "schema_version": "terrario.api/v1"}
            if etag: meta["etag"] = etag
            return status, {"data": data, "meta": meta}
        except Exception as exc:
            code = getattr(exc, "code", "INVALID_REQUEST")
            if isinstance(exc, ArtifactNotFound): status = 404
            elif code == "STALE_ARTIFACT_HASH": status = 412
            elif code == "LOCKED_ARTIFACT": status = 423
            elif isinstance(exc, (DuplicateArtifact, ProvenanceConflict)): status = 409
            elif code == "PREREGISTRATION_NOT_READY": status = 422
            elif isinstance(exc, PermissionError): status = 403
            elif isinstance(exc, (ValueError, KeyError)): status = 400
            else: status = 500
            return status, {"error": {"code": code, "message": str(exc), "details": {}, "request_id": request_id}}

    def _route(self, method, parts, query, p, headers):
        if method == "GET" and parts == ["session"]:
            return 200, {"session_id": self.session_id, "csrf_token": self.csrf_token,
                "actor": "local-user", "same_site": "Strict"}, None
        if method == "GET" and parts == ["health"]:
            return 200, {"status": "ok", "database": self.service.artifacts.integrity_check(),
                "migrations": self.service.artifacts.migration_status(), "scientific_execution": False}, None
        if method == "GET" and parts == ["status"]:
            return 200, {"preregistrations": len(self.service.list()), "execution": "NOT_AVAILABLE",
                "evidence_publication": "NOT_AVAILABLE"}, None
        if method == "GET" and parts == ["openapi.json"]:
            return 200, self._openapi(), None
        if method == "POST" and parts == ["preregistrations", "validate"]:
            return 200, self.service.validate_request(p), None
        if method == "POST" and parts == ["preregistrations"]:
            data = self.service.create(p, "local-user"); return 201, data, data["etag"]
        if method == "GET" and parts == ["preregistrations"]:
            return 200, {"items": self.service.list(), "next_cursor": None}, None
        if len(parts) >= 2 and parts[0] == "preregistrations":
            pid = parts[1]
            if method == "GET" and len(parts) == 2:
                data = self.service.get(pid); return 200, data, data["etag"]
            if method == "GET" and parts[2:] == ["versions"]:
                return 200, {"items": self.service.versions(pid), "next_cursor": None}, None
            if method == "POST" and parts[2:] == ["derive"]:
                data = self.service.derive(pid, self._if_match(headers, p), p.get("changes", {}),
                    str(p.get("reason", "derived preregistration")), "local-user")
                return 201, data, data["etag"]
            if method == "GET" and parts[2:] == ["readiness"]:
                return 200, self.service.readiness(pid), None
            if method == "POST" and parts[2:] == ["prepare-review"]:
                data = self.service.prepare_review(pid, self._if_match(headers, p), "local-user",
                    str(p.get("reason", "prepare exact review package")))
                return 201, data, data["etag"]
            if method == "POST" and parts[2:] == ["submit"]:
                return 201, self.service.submit(pid, "local-user", str(p.get("reason", "human review requested"))), None
            if method == "GET" and parts[2:] == ["review-package"]:
                return 200, self.service.review_package(pid), None
            if method == "POST" and parts[2:] == ["lock"]:
                return 201, self.service.lock(pid, self._if_match(headers, p), str(p["decision_id"]),
                    str(p.get("reason", "human lock ceremony")), "local-user", headers.get("Idempotency-Key") or p.get("idempotency_key")), None
            if method == "GET" and parts[2:] == ["verify"]:
                return 200, self.service.verify(pid), None
            if method == "GET" and parts[2:] == ["trial-matrix"]:
                return 200, self.service.trial_matrix(pid), None
            if method == "GET" and parts[2:] == ["audit-chain"]:
                return 200, self.service.audit_chain(pid), None
            if method == "GET" and parts[2:] == ["export"]:
                return 200, self.service.export(pid), None
            if method == "POST" and parts[2:] == ["withdraw"]:
                return 200, self.service.withdraw(pid, str(p["reason"]), "local-user"), None
            if method == "POST" and parts[2:] == ["supersede"]:
                return 200, self.service.supersede(pid, str(p["child_preregistration_id"]), str(p["reason"]), "local-user"), None
            if len(parts) == 3 and parts[2] in {"amendments", "deviations"}:
                if method == "POST":
                    kind = "PreregistrationAmendment" if parts[2] == "amendments" else "ProtocolDeviation"
                    return 201, self.service.add_postlock_record(pid, kind, p, "local-user"), None
                kind = "PreregistrationAmendment" if parts[2] == "amendments" else "ProtocolDeviation"
                items = [x for x in self.service.artifacts.list_artifacts(kind) if x.payload.get("preregistration_id") == pid]
                return 200, {"items": [self.service._view(x) for x in items], "next_cursor": None}, None
        if method == "POST" and parts == ["review-requests"]:
            return 201, self.service.request_experiment_review(str(p["artifact_version_id"]), "local-user", str(p["reason"])), None
        if method == "GET" and parts == ["review-requests"]:
            return 200, {"items": self.service.review_requests(), "next_cursor": None}, None
        if method == "POST" and len(parts) == 3 and parts[0] == "review-requests" and parts[2] == "decisions":
            return 201, self.service.decide(parts[1], str(p["artifact_hash"]), str(p["decision"]),
                str(p["reason"]), tuple(p.get("warning_acceptances", ())), "local-user"), None
        if method == "GET" and parts == ["exposure-records"]:
            seed = query.get("world_seed", [None])[0]
            return 200, {"items": self.service.exposure_records(query.get("scenario_id", [None])[0], int(seed) if seed else None), "next_cursor": None}, None
        if method == "POST" and parts == ["exposure-records"]:
            return 201, self.service.record_exposure(str(p["scenario_id"]), str(p["scenario_hash"]), int(p["world_seed"]),
                str(p["exposure_kind"]), "local-user", str(p["context_type"]), str(p["context_id"]), p.get("preregistration_root_hash")), None
        if method == "POST" and parts == ["bundles", "validate"]:
            return 200, self.service.validate_portable(p), None
        if method == "POST" and parts == ["bundles", "import"]:
            return 201, self.service.import_portable(p, "local-user"), None
        raise ArtifactNotFound("/api/v1/" + "/".join(parts))

    def _authorize(self, headers: Mapping[str, str]) -> None:
        host = _header(headers, "Host") or ""
        origin = _header(headers, "Origin") or ""
        if host and not (host.startswith("127.0.0.1") or host.startswith("localhost")):
            raise PermissionError("non-local Host rejected")
        if origin and not (origin.startswith("http://127.0.0.1") or origin.startswith("http://localhost")):
            raise PermissionError("non-local Origin rejected")
        if _header(headers, "X-CSRF-Token") != self.csrf_token:
            raise PermissionError("invalid CSRF token")

    @staticmethod
    def _if_match(headers: Mapping[str, str], payload: Mapping[str, Any]) -> str:
        value = _header(headers, "If-Match") or payload.get("expected_hash")
        if not value: raise ValueError("If-Match is required")
        return str(value).strip('"')

    @staticmethod
    def _openapi():
        paths = {}
        for method, path in (
            ("get", "/api/v1/session"), ("get", "/api/v1/health"), ("get", "/api/v1/status"),
            ("get", "/api/v1/preregistrations"), ("post", "/api/v1/preregistrations"),
            ("post", "/api/v1/preregistrations/validate"),
            ("get", "/api/v1/preregistrations/{id}"), ("post", "/api/v1/preregistrations/{id}/derive"),
            ("get", "/api/v1/preregistrations/{id}/readiness"), ("post", "/api/v1/preregistrations/{id}/prepare-review"),
            ("post", "/api/v1/preregistrations/{id}/submit"), ("post", "/api/v1/preregistrations/{id}/lock"),
            ("get", "/api/v1/preregistrations/{id}/verify"), ("get", "/api/v1/preregistrations/{id}/trial-matrix"),
            ("get", "/api/v1/preregistrations/{id}/audit-chain"), ("get", "/api/v1/preregistrations/{id}/export"),
            ("post", "/api/v1/review-requests"), ("get", "/api/v1/review-requests"),
            ("post", "/api/v1/review-requests/{id}/decisions"),
            ("get", "/api/v1/exposure-records"), ("post", "/api/v1/exposure-records"),
            ("post", "/api/v1/bundles/validate"), ("post", "/api/v1/bundles/import")):
            paths.setdefault(path, {})[method] = {"responses": {"200": {"description": "Terrario API envelope"}},
                "x-scientific-execution": False, "x-automatic-approval": False}
        return {"openapi": "3.1.0", "info": {"title": "Terrario Preregistration API", "version": "1.0.0"},
                "servers": [{"url": "http://127.0.0.1:8765"}], "paths": paths}
