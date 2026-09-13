"""HTTP contract for raw-only scientific execution."""
from __future__ import annotations

import secrets
from typing import Any, Mapping

from terrario.lab.execution.domain import ExecutionConflict, ExecutionError, ExecutionNotReady, ExecutionUnauthorized
from terrario.lab.persistence import ArtifactNotFound, ProvenanceConflict


class ScientificExecutionAPI:
    def __init__(self, service, governance_api, dispatcher=None):
        self.service, self.governance_api, self.dispatcher = service, governance_api, dispatcher

    def dispatch(self, method: str, parts: list[str], query: Mapping[str, list[str]], payload: Mapping[str, Any] | None, headers: Mapping[str, str] | None = None):
        request_id, p, headers = f"req-{secrets.token_hex(8)}", dict(payload or {}), dict(headers or {})
        try:
            # Direct in-process callers have no HTTP header envelope; real HTTP
            # mutations always carry headers and are CSRF-checked by the same
            # session authority as preregistration.
            if method != "GET" and headers: self.governance_api._authorize(headers)
            status, data = self._route(method, parts, p)
            return status, {"data": data, "meta": {"request_id": request_id, "schema_version": "terrario.api/v1", "scientific_execution": True}}
        except Exception as exc:
            code = getattr(exc, "code", "INVALID_REQUEST")
            status = 404 if isinstance(exc, ArtifactNotFound) else 409 if isinstance(exc, (ExecutionConflict, ProvenanceConflict)) else 422 if isinstance(exc, ExecutionNotReady) else 403 if isinstance(exc, ExecutionUnauthorized) else 400 if isinstance(exc, (ValueError, KeyError)) else 500
            return status, {"error": {"code": code, "message": str(exc), "details": {}, "request_id": request_id}}

    def _route(self, method: str, parts: list[str], p: Mapping[str, Any]):
        if method == "POST" and parts == ["scientific-executions"]:
            return 201, self.service.request(str(p["preregistration_root_hash"]), "local-user")
        if method == "GET" and parts == ["scientific-executions"]:
            return 200, {"items": self.service.list(), "next_cursor": None}
        if method == "POST" and parts == ["execution-authorizations"]:
            return 201, self.service.authorize(p, "local-user")
        if method == "GET" and len(parts) == 2 and parts[0] == "execution-authorizations":
            return 200, self.service.authorization(parts[1])
        if method == "POST" and len(parts) == 3 and parts[0] == "execution-authorizations" and parts[2] == "revoke":
            return 200, self.service.revoke(parts[1], str(p["reason"]), "local-user")
        if len(parts) >= 2 and parts[0] == "scientific-executions":
            execution_id = parts[1]
            if method == "GET" and len(parts) == 2: return 200, self.service.get(execution_id)
            if method == "POST" and parts[2:] == ["bind-authorization"]:
                return 200, self.service.bind_authorization(execution_id, str(p["authorization_id"]), int(p["expected_revision"]), "local-user")
            if method == "POST" and parts[2:] == ["plan"]:
                return 200, self.service.plan(execution_id, int(p["expected_revision"]), "local-user")
            if method == "GET" and parts[2:] == ["readiness"]:
                return 200, self.service._readiness(self.service.get(execution_id)["preregistration_root_hash"])
            if method == "POST" and parts[2:] == ["commands"]:
                return 200, self.service.command(execution_id, str(p["command_id"]), int(p["expected_revision"]), str(p["command"]), "local-user")
            if method == "POST" and parts[2:] == ["dispatch"]:
                if not self.dispatcher: raise ValueError("scientific dispatcher unavailable")
                return 200, self.dispatcher.run(execution_id, str(p.get("worker_id", "scientific-dispatcher")))
            if method == "POST" and parts[2:] == ["safe-boundary"]:
                return 200, self.service.certify_safe_boundary(execution_id, "local-worker")
            if method == "POST" and parts[2:] == ["complete"]:
                return 200, self.service.complete(execution_id, "local-worker")
            if method == "POST" and parts[2:] == ["deviations"]:
                return 201, self.service.deviation(execution_id, str(p["deviation_type"]), dict(p["payload"]), "local-user")
            if method == "GET" and parts[2:] == ["verify"]:
                return 200, self.service.verify(execution_id)
            if method == "GET" and parts[2:] == ["artifacts"]:
                return 200, {"items": self.service.get(execution_id)["artifacts"], "next_cursor": None}
            if method == "GET" and len(parts) == 5 and parts[2] == "trials" and parts[4] == "frames":
                return 200, {"items": self.dispatcher.frames_after(execution_id, parts[3], int(p.get("after_sequence", -1))) if self.dispatcher else (), "next_cursor": None}
            if method == "GET" and parts[2:] == ["export"]:
                return 200, self.service.export_bundle(execution_id)
            if method == "POST" and parts[2:] == ["recover"]:
                return 200, {"items": self.service.recover_expired_leases("local-recovery")}
        if method == "POST" and parts == ["scientific-execution-bundles", "validate"]:
            return 200, self.service.validate_bundle(str(p["archive_path"]))
        raise ArtifactNotFound("/api/v1/" + "/".join(parts))
