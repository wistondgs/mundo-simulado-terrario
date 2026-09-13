"""HTTP-neutral dispatcher for WorldStream v1."""
from __future__ import annotations

from uuid import uuid4

from terrario.lab.models import thaw

from .contracts import ResyncRequest, SessionCommand
from .service import LiveSandboxService, SessionConflict
from .trace import TraceIntegrityError


class WorldStreamAPI:
    def __init__(self, service: LiveSandboxService, create_inputs):
        self.service = service
        self.create_inputs = create_inputs

    def dispatch(self, method: str, parts: list[str], query: dict, payload: dict | None):
        body = payload or {}
        try:
            if method == "POST" and parts == ["sessions"]:
                spec, config, compiled = self.create_inputs(body)
                run = self.service.create(spec, config, compiled)
                return 201, thaw(self.service.describe(run.run_id))
            if len(parts) >= 2 and parts[0] == "sessions":
                session_id = parts[1]
                if method == "GET" and len(parts) == 2:
                    return 200, thaw(self.service.describe(session_id))
                if method == "GET" and len(parts) == 3 and parts[2] == "stream":
                    after = int(query.get("after_sequence", ["-1"])[0])
                    return 200, {"stream": self.service.envelopes_after(session_id, after), "transport": "SSE"}
                if method == "POST" and len(parts) == 3 and parts[2] == "commands":
                    command = SessionCommand(session_id, str(body.get("command_id") or uuid4()),
                        str(body["command"]).upper(), int(body["expected_session_revision"]), body.get("parameters", {}))
                    return 200, self.service.command(command)
                if method == "POST" and len(parts) == 3 and parts[2] == "resync":
                    request = ResyncRequest(session_id, int(body.get("after_sequence", -1)),
                        int(body.get("last_frame_sequence", -1)), str(body.get("reason", "CLIENT_REQUEST")))
                    return 200, self.service.resync(session_id, request.reason)
            if len(parts) >= 2 and parts[0] == "traces":
                trace_id = parts[1]
                archive = self.service.archive(trace_id)
                if archive is None: return 404, {"error": "trace not found", "category": "NOT_FOUND"}
                if method == "GET" and len(parts) == 2:
                    return 200, {"trace_id": trace_id, "integrity": archive.verify(), "schema_version": "terrario.sandbox.trace/v2"}
                if method == "GET" and len(parts) == 3 and parts[2] == "events":
                    return 200, archive.read(after_sequence=int(query.get("after_sequence", ["-1"])[0]),
                        limit=int(query.get("limit", ["10000"])[0]), event_type=query.get("event_type", [None])[0],
                        entity_id=query.get("entity_id", [None])[0])
                if method == "GET" and len(parts) == 3 and parts[2] == "seek":
                    return 200, {"cursor": archive.seek(int(query.get("tick", ["0"])[0]))}
                if method == "GET" and len(parts) == 3 and parts[2] == "compare":
                    left, right = int(query.get("left", ["0"])[0]), int(query.get("right", ["0"])[0])
                    return 200, {"left": archive.seek(left), "right": archive.seek(right),
                        "explanation": "DERIVED STATE DIFF · NOT CAUSAL"}
            return 404, {"error": "world-stream endpoint not found", "category": "NOT_FOUND"}
        except SessionConflict as exc:
            return 409, {"error": str(exc), "category": exc.code}
        except TraceIntegrityError as exc:
            return 409, {"error": str(exc), "category": exc.code}
        except (KeyError, ValueError) as exc:
            return 400, {"error": str(exc), "category": getattr(exc, "code", "CONFIG_ERROR")}
