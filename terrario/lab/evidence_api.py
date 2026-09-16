"""Local HTTP contract for explicit CL-7 empirical-result publication."""
from __future__ import annotations

import secrets
from typing import Any, Mapping

from terrario.lab.evidence_publication import ResultIneligible, ResultPublicationError


class EmpiricalEvidenceAPI:
    def __init__(self, service, governance_api):
        self.service, self.governance_api = service, governance_api

    def dispatch(self, method: str, parts: list[str], query: Mapping[str, list[str]],
                 payload: Mapping[str, Any] | None, headers: Mapping[str, str] | None = None):
        request_id, p, headers = f"req-{secrets.token_hex(8)}", dict(payload or {}), dict(headers or {})
        try:
            if method != "GET" and headers:
                self.governance_api._authorize(headers)
            if method == "GET" and parts == ["empirical-results", "status"]:
                data = self.service.status()
            elif method == "POST" and parts == ["empirical-results"]:
                required = {"execution_id", "attempt_id", "metric_artifact_descriptor_hash"}
                if set(p) != required:
                    raise ValueError("empirical result publication requires exactly execution_id, attempt_id, metric_artifact_descriptor_hash")
                data = self.service.ingest(str(p["execution_id"]), str(p["attempt_id"]), str(p["metric_artifact_descriptor_hash"]))
            elif method == "GET" and len(parts) == 2 and parts[0] == "empirical-results":
                data = self.service.get_result(parts[1])
            elif method == "GET" and len(parts) == 3 and parts[0] == "empirical-results" and parts[2] == "provenance":
                data = self.service.provenance_for_result(parts[1])
            elif method == "GET" and len(parts) == 3 and parts[:2] == ["empirical-results", "hypotheses"]:
                data = self.service.evidence_for_hypothesis(parts[2], query.get("revision", [None])[0])
            else:
                raise ResultPublicationError("EMPIRICAL_RESULT_ROUTE_NOT_FOUND")
            return 201 if method == "POST" else 200, {"data": data, "meta": {"request_id": request_id,
                "schema_version": "terrario.api/v1", "evidence_publication": True, "automatic_execution": False}}
        except Exception as exc:
            code = getattr(exc, "code", "INVALID_REQUEST")
            status = 422 if isinstance(exc, ResultIneligible) else 404 if code in {"RESULT_NOT_FOUND", "EMPIRICAL_RESULT_ROUTE_NOT_FOUND"} else 403 if isinstance(exc, PermissionError) else 400 if isinstance(exc, ValueError) else 500
            return status, {"error": {"code": code, "message": str(exc), "details": {}, "request_id": request_id}}
