"""Dependency-free local HTTP API for the Terrario laboratory."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
import mimetypes
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from terrario.lab.hypergraph.adapter import HypergraphAdapter
from terrario.lab.models import thaw
from terrario.lab.read_model import LabReadModel
from terrario.lab.theory.store import TheoryGraphStore
from terrario.lab.theory.compiler import HypothesisCompiler
from terrario.lab.theory.ingestion import TheoryIngestor
from terrario.lab.theory.factory import build_portfolio
from terrario.lab.theory.scientific_review import review_portfolio
from terrario.lab.analyzer import DeterministicScientificAnalyzer, ExternalAnalyzerInput
from terrario.lab.world_registry import WorldScenarioRegistry, configuration_for, configuration_from_payload, d2_views, generalization_check, patched_configuration
from terrario.lab.world_contracts import config_diff, validate_configuration
from terrario.lab.world_authoring import SeedBrowser,compile_draft,compile_registry_world,draft_from_legacy,generate_instance,preview,validate_draft
from terrario.lab.sandbox_runtime import ExecutionClassification,SandboxService,derive_sandbox,make_spec,serialize_run


class LabAPI:
    def __init__(self, root: str | Path):
        self.model = LabReadModel(root)
        self.root = Path(root).resolve()
        graphs = sorted((self.root / "theory_snapshots").glob("*/theory_graph.json"))
        self.theory_graph = TheoryGraphStore.load(graphs[-1]) if graphs else None
        summary = graphs[-1].parent / "ingestion_summary.json" if graphs else None
        self.theory_summary = json.loads(summary.read_text()) if summary and summary.exists() else {}
        self.theory_import = TheoryIngestor(graphs[-1].parent).ingest() if graphs else None
        snapshot_id = self.theory_summary.get("snapshot_id", graphs[-1].parent.name if graphs else "NOT_AVAILABLE")
        self.experiment_portfolio = build_portfolio(self.theory_import.hyperedges, snapshot_id) if self.theory_import else None
        self.scientific_review = review_portfolio(self.experiment_portfolio) if self.experiment_portfolio else None
        self.world_registry = WorldScenarioRegistry(self.root)
        d2_entry = self.world_registry.get("D2")
        self.d2_configuration = configuration_for(d2_entry) if d2_entry.scenario else None
        self.compiled_worlds = {e.world_id:compile_registry_world(e.world_id,e.source) for e in self.world_registry.entries() if e.scenario}
        self.sandbox = SandboxService(self.root/".sandbox")
        self.world_drafts = {}

    def dispatch(self, method: str, url: str, payload: dict | None = None):
        parsed = urlparse(url); parts = [unquote(x) for x in parsed.path.strip("/").split("/") if x]
        query = parse_qs(parsed.query)
        try:
            if method == "GET" and parts == ["api","worlds"]: return 200, thaw(self.world_registry.entries())
            if method == "GET" and len(parts)==3 and parts[:2]==["api","worlds"]:
                entry=self.world_registry.get(parts[2].upper()); return 200, thaw(entry)
            if method == "GET" and parts == ["api","studio","d2"]:
                if self.d2_configuration is None: return 404,{"error":"D2 is not implemented in this project root"}
                return 200, {"configuration":thaw(self.d2_configuration),"views":thaw(d2_views(self.world_registry.get("D2"))),"generalization":generalization_check(self.world_registry)}
            if method == "GET" and len(parts)==4 and parts[:2]==["api","worlds"] and parts[3]=="preview":
                wid=parts[2].upper(); seed=int(query.get("seed",[42])[0]); return 200,thaw(preview(self.compiled_worlds[wid],seed))
            if method == "GET" and len(parts)==4 and parts[:2]==["api","worlds"] and parts[3]=="seeds":
                wid=parts[2].upper(); values=query.get("values",["42"])[0]; seeds=[int(x) for x in values.split(",") if x]; return 200,thaw(SeedBrowser(self.compiled_worlds[wid]).analyze(seeds))
            if method == "GET" and len(parts)>=3 and parts[:2]==["api","sandbox"]:
                run=self.sandbox.get(parts[2]); return 200,(thaw(run.timeline) if len(parts)==4 and parts[3]=="trace" else serialize_run(run))
            if method == "GET" and len(parts)==4 and parts[:3]==["api","worlds","drafts"]:
                return 200,thaw(self.world_drafts[parts[3]])
            if method == "POST" and parts == ["api","worlds","validate"]:
                draft=self._draft_input(payload or {})
                findings=validate_draft(draft); return 200,{"valid":not any(x.blocking for x in findings),"findings":thaw(findings),"draft":thaw(draft)}
            if method == "POST" and parts == ["api","worlds","drafts"]:
                draft=self._draft_input(payload or {}); findings=validate_draft(draft)
                if any(x.blocking for x in findings): return 400,{"error":"invalid world draft","findings":thaw(findings),"category":"WORLD_ERROR"}
                if draft.draft_id in self.world_drafts: return 409,{"error":"silent draft overwrite prohibited","category":"PROVENANCE_ERROR"}
                self.world_drafts[draft.draft_id]=draft; return 201,{"draft":thaw(draft),"findings":thaw(findings)}
            if method == "POST" and parts == ["api","worlds","preview"]:
                draft=self._draft_input(payload or {}); compiled=compile_draft(draft); return 200,thaw(preview(compiled,int((payload or {}).get("seed",42))))
            if method == "POST" and parts == ["api","worlds","compile"]:
                wid=str((payload or {}).get("world_id","D2")).upper(); compiled=self.compiled_worlds[wid]; return 200,{"definition":thaw(compiled.definition),"definition_hash":compiled.definition.content_hash,"warnings":thaw(compiled.warnings)}
            if method == "POST" and parts == ["api","sandbox","validate"]:
                spec,config,compiled=self._sandbox_inputs(payload or {}); instance=generate_instance(compiled,spec.world_seed); return 200,self.sandbox.validate_spec(spec,config,compiled,instance)
            if method == "POST" and parts == ["api","sandbox"]:
                spec,config,compiled=self._sandbox_inputs(payload or {}); return 201,serialize_run(self.sandbox.create(spec,config,compiled))
            if method == "POST" and len(parts)==4 and parts[:2]==["api","sandbox"]:
                rid,action=parts[2],parts[3]
                if action=="step": self.sandbox.step(rid)
                elif action=="run": self.sandbox.run_bounded(rid,int((payload or {}).get("steps",1)))
                elif action=="pause": self.sandbox.pause(rid)
                elif action=="resume": self.sandbox.resume(rid)
                elif action=="stop": self.sandbox.stop(rid)
                elif action=="restart": return 201,serialize_run(self.sandbox.restart(rid))
                else: return 404,{"error":"unknown sandbox action"}
                return 200,serialize_run(self.sandbox.get(rid))
            if method == "POST" and parts == ["api","config","validate"]:
                if self.d2_configuration is None: return 404,{"error":"D2 configuration is unavailable"}
                candidate=patched_configuration(self.d2_configuration,payload or {})
                return 200,{"configuration":thaw(candidate),"findings":thaw(validate_configuration(candidate)),"scientific_hash":candidate.content_hash}
            if method == "POST" and parts == ["api","config","diff"]:
                if self.d2_configuration is None: return 404,{"error":"D2 configuration is unavailable"}
                candidate=patched_configuration(self.d2_configuration,payload or {})
                return 200,thaw(config_diff(self.d2_configuration,candidate))
            if method == "POST" and parts == ["api","config","roundtrip"]:
                if self.d2_configuration is None: return 404,{"error":"D2 configuration is unavailable"}
                decoded=configuration_from_payload(payload or {},self.d2_configuration)
                return 200,{"configuration":thaw(decoded),"scientific_hash":decoded.content_hash}
            if method != "GET": return 405, {"error":"mutation endpoint not available; configuration validation creates no persisted state"}
            if parts == ["api", "status"]:
                return 200, {"mode": "READ_ONLY", "experiments": len(self.model.experiments()), "runs": len(self.model.runs()), "theory": self.theory_summary, "h_adapt": "BLOCKED_CUDA"}
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
            if parts == ["api", "theory", "summary"]: return 200, self.theory_summary
            if parts == ["api", "theory", "graph"]: return (200, self.theory_graph.export()) if self.theory_graph else (404, {"error": "no theory snapshot"})
            if parts == ["api", "theory", "drafts"]:
                drafts = tuple(HypothesisCompiler().compile(edge) for edge in (self.theory_import.hyperedges if self.theory_import else ()))
                return 200, thaw(drafts)
            if parts == ["api", "theory", "portfolio"]:
                return (200, thaw(self.experiment_portfolio)) if self.experiment_portfolio else (404, {"error": "no theory portfolio"})
            if parts == ["api", "theory", "scientific-review"]:
                return (200, thaw(self.scientific_review)) if self.scientific_review else (404, {"error": "no scientific review"})
            if parts == ["api", "theory", "rival-groups"]: return 200, []
            if parts == ["api", "theory", "paths"]:
                if not self.theory_graph: return 404, {"error": "no theory snapshot"}
                paths = self.theory_graph.paths(query.get("from", [""])[0], query.get("to", [""])[0])
                return 200, thaw(paths)
            if parts == ["api", "evidence"]: return 200, thaw(self.model.evidence_manifests())
            if len(parts) == 3 and parts[:2] == ["api", "evidence"]: return self._one(self.model.evidence(parts[2]))
            if len(parts) == 3 and parts[:2] == ["api", "forensic"]: return self._one(self.model.forensic_case(parts[2]))
            if parts == ["api", "checkpoints"]: return 200, thaw(self.model.checkpoints())
            if parts == ["api", "analyzer", "deterministic"]:
                invalid = tuple(run.id for run in self.model.runs() if run.experimental_valid is False)
                request = ExternalAnalyzerInput({}, "catalog-audit", "1", {"code_hash": "catalog", "config_hash": "catalog", "protocol": "catalog-audit"}, {"invalid_runs": invalid}, (), (), {"source": "LabReadModel"})
                return 200, thaw(DeterministicScientificAnalyzer().analyze(request))
            return 404, {"error": "not found"}
        except (KeyError, IndexError, ValueError) as exc:
            return (404 if method=="GET" else 400), {"error": str(exc),"category":getattr(exc,"code","CONFIG_ERROR")}

    @staticmethod
    def _one(value): return (200, thaw(value)) if value is not None else (404, {"error": "not found"})

    def _sandbox_inputs(self,payload):
        wid=str(payload.get("world_id","D2")).upper(); entry=self.world_registry.get(wid); compiled=self.compiled_worlds[wid]
        base=configuration_for(entry); config=derive_sandbox(base)
        if payload.get("agent_reference"): config=replace(config,agent_reference=str(payload["agent_reference"]))
        classification=ExecutionClassification(payload.get("classification","ENGINEERING_SANDBOX"))
        spec=make_spec(config,compiled,int(payload.get("world_seed",42)),int(payload.get("agent_seed",1000045)),int(payload.get("step_limit",100)),classification)
        return spec,config,compiled

    def _draft_input(self,payload):
        allowed={"world_id","draft_id","purpose","dimensions","action_availability","seed"}; unknown=set(payload)-allowed
        if unknown: raise ValueError(f"unknown/import-unsafe world fields: {sorted(unknown)}")
        wid=str(payload.get("world_id","D2")).upper(); draft=draft_from_legacy(wid,self.world_registry.get(wid).source)
        changes={}
        for name in ("purpose","dimensions","action_availability"):
            if name in payload: changes[name]=tuple(payload[name]) if name in {"dimensions","action_availability"} else str(payload[name])
        if "draft_id" in payload: changes["draft_id"]=str(payload["draft_id"])
        return replace(draft,**changes)

    def _hypergraph(self):
        if self.theory_graph:
            graph = self.theory_graph.export(); theory = graph["theory_graph"]; evidence = graph["evidence_graph"]
            return {"snapshot_id": graph["snapshot_id"], "nodes": [*theory["nodes"], *evidence["nodes"]], "edges": [*theory["edges"], *evidence["edges"]]}
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
        def do_POST(self):
            length=int(self.headers.get("Content-Length","0")); raw=self.rfile.read(length)
            try: payload=json.loads(raw or b"{}")
            except json.JSONDecodeError as exc: self.send_error(400,str(exc)); return
            status,result=api.dispatch("POST",self.path,payload); body=json.dumps(result).encode()
            self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
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
