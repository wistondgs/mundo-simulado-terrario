"""Dependency-free local HTTP API for the Terrario laboratory."""

from __future__ import annotations

import argparse
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from terrario.lab.hypergraph.adapter import HypergraphAdapter
from terrario.lab.models import thaw
from terrario.lab.read_model import LabReadModel


class LabAPI:
    def __init__(self, root: str | Path):
        self.model = LabReadModel(root)

    def dispatch(self, method: str, url: str):
        if method != "GET": return 405, {"error": "read-only API"}
        parsed = urlparse(url); parts = [unquote(x) for x in parsed.path.strip("/").split("/") if x]
        query = parse_qs(parsed.query)
        try:
            if parts == ["api", "status"]:
                return 200, {"mode": "READ_ONLY", "experiments": len(self.model.experiments()), "runs": len(self.model.runs())}
            if parts == ["api", "experiments"]: return 200, thaw(self.model.experiments())
            if len(parts) == 3 and parts[:2] == ["api", "experiments"]: return self._one(self.model.experiment(parts[2]))
            if parts == ["api", "runs"]: return 200, thaw(self.model.runs(query.get("experiment", [None])[0]))
            if len(parts) >= 3 and parts[:2] == ["api", "runs"]:
                rid = parts[2]
                if len(parts) == 3: return self._one(self.model.run(rid))
                step = int(query.get("step", [0])[0])
                action = parts[3]
                if action == "timeline": return 200, thaw(self.model.timeline(rid))
                if action in {"world", "observer-view"}: return 200, thaw(self.model.observer_view(rid, step))
                if action == "agent-view": return 200, thaw(self.model.agent_view(rid, step))
            if parts == ["api", "hypotheses"]: return 200, thaw(self.model.hypotheses())
            if parts == ["api", "hypergraph"]: return 200, self._hypergraph()
            if parts == ["api", "evidence"]: return 200, thaw(self.model.evidence_manifests())
            if len(parts) == 3 and parts[:2] == ["api", "evidence"]: return self._one(self.model.evidence(parts[2]))
            if len(parts) == 3 and parts[:2] == ["api", "forensic"]: return self._one(self.model.forensic_case(parts[2]))
            if parts == ["api", "checkpoints"]: return 200, thaw(self.model.checkpoints())
            return 404, {"error": "not found"}
        except (KeyError, IndexError, ValueError) as exc:
            return 404, {"error": str(exc)}

    @staticmethod
    def _one(value): return (200, thaw(value)) if value is not None else (404, {"error": "not found"})

    def _hypergraph(self):
        nodes, edges = [], []
        for h in self.model.hypotheses():
            nodes.append({"id": h.id, "label": h.id, "type": "Hypothesis", "status": "UNTESTED_HYPOTHESIS", "provenance": h.source})
        for e in self.model.experiments():
            nodes.append({"id": e.id, "label": e.protocol, "type": "Experiment", "status": "UNRESOLVED", "provenance": e.source})
            for h in self.model.hypotheses():
                if h.id in e.protocol or h.id.replace("-", "_").lower() in e.source.lower():
                    edges.append({"source": h.id, "target": e.id, "status": "UNTESTED_HYPOTHESIS", "provenance": e.source})
        for evidence in self.model.evidence_manifests():
            nodes.append({"id": evidence.id, "label": evidence.id, "type": "Evidence", "status": "UNRESOLVED", "provenance": evidence.source})
            edges.append({"source": evidence.experiment_id, "target": evidence.id, "status": "UNRESOLVED", "provenance": evidence.source})
        return {"nodes": nodes, "edges": edges}


def handler_factory(api: LabAPI, static_dir: Path):
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path.startswith("/api/"):
                status, payload = api.dispatch("GET", self.path)
                body = json.dumps(payload).encode()
                self.send_response(status); self.send_header("Content-Type", "application/json")
            else:
                rel = urlparse(self.path).path.lstrip("/") or "index.html"
                target = (static_dir / rel).resolve()
                if static_dir not in target.parents and target != static_dir or not target.is_file():
                    self.send_error(404); return
                body = target.read_bytes(); self.send_response(200)
                self.send_header("Content-Type", mimetypes.guess_type(target.name)[0] or "application/octet-stream")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
        def log_message(self, fmt, *args): pass
    return Handler


def serve(root: str | Path, host: str = "127.0.0.1", port: int = 8765):
    api = LabAPI(root); static_dir = Path(__file__).parent / "static"
    server = ThreadingHTTPServer((host, port), handler_factory(api, static_dir))
    print(f"Terrario Lab: http://{host}:{port}", flush=True)
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--root", default="."); parser.add_argument("--host", default="127.0.0.1"); parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args(); serve(args.root, args.host, args.port)


if __name__ == "__main__": main()
