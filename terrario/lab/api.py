"""Dependency-free local HTTP API for the Terrario laboratory."""

from __future__ import annotations

import argparse
from dataclasses import replace
import json
import mimetypes
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

from terrario.lab.hypergraph.adapter import HypergraphAdapter
from terrario.lab.models import thaw
from terrario.lab.read_model import LabReadModel
from terrario.lab.theory.store import TheoryGraphStore
from terrario.lab.theory.compiler import HypothesisCompiler, OperationalExperimentCompiler, OperationalHypothesisCompiler
from terrario.lab.theory.ingestion import TheoryIngestor
from terrario.lab.theory.factory import build_portfolio
from terrario.lab.theory.scientific_review import review_portfolio
from terrario.lab.analyzer import DeterministicScientificAnalyzer, ExternalAnalyzerInput
from terrario.lab.world_registry import WorldScenarioRegistry, configuration_for, configuration_from_payload, d2_views, generalization_check, patched_configuration
from terrario.lab.world_contracts import config_diff, validate_configuration
from terrario.lab.world_authoring import SeedBrowser,compile_draft,compile_registry_world,draft_from_legacy,generate_instance,preview,validate_draft
from terrario.lab.sandbox_runtime import ExecutionClassification,derive_sandbox,make_spec,serialize_run
from terrario.lab.worldstream.service import MAX_ACTIVE_SESSIONS
from terrario.lab.run_measures import measure_run
from terrario.lab.agent_composition import catalogue as agent_catalogue,validate_selection
from terrario.lab.worldstream.service import LiveSandboxService
from terrario.lab.worldstream.api import WorldStreamAPI
from terrario.lab.capabilities import CapabilityRegistry,assess_compatibility,audited_agent_assessments,scenario_requirements
from terrario.lab.agent_inspector import AgentInspector
from terrario.lab.metrics_observer import MetricRegistry,ObserverRegistry
from terrario.lab.experiment_composer import (SCHEMA_VERSION as EXPERIMENT_DRAFT_SCHEMA,ControlCondition,DraftProvenance,DraftState,ExperimentDraft,build_trial_matrix,draft_diff,state_for,validate_draft as validate_experiment_draft)
from terrario.lab.persistence import ArtifactNotFound,ArtifactRepository,DuplicateArtifact,ProvenanceConflict
from terrario.lab.persistence.codecs import experiment_draft_from_payload
from terrario.lab.persistence.canonical import content_hash as durable_content_hash
from terrario.lab.preregistration.service import PreregistrationService
from terrario.lab.preregistration.api import PreregistrationAPI
from terrario.lab.execution.service import ScientificExecutionService
from terrario.lab.execution.api import ScientificExecutionAPI
from terrario.lab.execution.dispatcher import ScientificExecutionDispatcher
from terrario.lab.execution.observation import ScientificObservationService
from terrario.lab.evidence_publication import EmpiricalResultPublicationService
from terrario.lab.evidence_api import EmpiricalEvidenceAPI
from terrario.lab.referencegraph.service import ReferenceGraphService
from terrario.lab.referencegraph.api import ReferenceGraphAPI
from terrario.lab.crossgraph.service import CrossGraphService
from terrario.lab.crossgraph.api import CrossGraphAPI
from terrario.lab.hypergraph.theory_operational import (
    BindingRequirement, CompositionRule, RoleCompatibility, compose, load_bindings, materialize,
)
from terrario.lab.d2_operational import D2BindingProtocol
from terrario.lab.d2_visual_fixture import build_d2_visual_validation_fixture, validate_visual_fixture_payload


class LabAPI:
    def __init__(self, root: str | Path, data_root: str | Path | None = None):
        self.model = LabReadModel(root)
        self.root = Path(root).resolve()
        graphs = sorted((self.root / "theory_snapshots").glob("*/theory_graph.json"))
        self.theory_graph = TheoryGraphStore.load(graphs[-1]) if graphs else None
        summary = graphs[-1].parent / "ingestion_summary.json" if graphs else None
        self.theory_summary = json.loads(summary.read_text()) if summary and summary.exists() else {}
        self.theory_import = TheoryIngestor(graphs[-1].parent).ingest() if graphs else None
        configured_source_root = os.environ.get("TERRARIO_PRIMARY_SOURCE_ROOT")
        self.primary_source_root = Path(configured_source_root).resolve() if configured_source_root else None
        snapshot_id = self.theory_summary.get("snapshot_id", graphs[-1].parent.name if graphs else "NOT_AVAILABLE")
        self.experiment_portfolio = build_portfolio(self.theory_import.hyperedges, snapshot_id) if self.theory_import else None
        self.scientific_review = review_portfolio(self.experiment_portfolio) if self.experiment_portfolio else None
        self.world_registry = WorldScenarioRegistry(self.root)
        d2_entry = self.world_registry.get("D2")
        self.d2_configuration = configuration_for(d2_entry) if d2_entry.scenario else None
        self.compiled_worlds = {e.world_id:compile_registry_world(e.world_id,e.source) for e in self.world_registry.entries() if e.scenario}
        self.sandbox = LiveSandboxService(self.root/".sandbox")
        self.artifacts = ArtifactRepository(data_root or self.root/".terrario")
        self.capabilities = CapabilityRegistry()
        self.agent_inspector = AgentInspector()
        self.metrics = MetricRegistry()
        self.observers = ObserverRegistry()
        self.preregistrations = PreregistrationService(self.root, self.artifacts, self.metrics, self.observers)
        self.api_v1 = PreregistrationAPI(self.preregistrations)
        self.scientific_executions = ScientificExecutionService(self.root, self.artifacts, self.preregistrations)
        self.scientific_execution_dispatcher = ScientificExecutionDispatcher(self.scientific_executions)
        self.scientific_observations = ScientificObservationService(self.scientific_executions, self.scientific_execution_dispatcher)
        self.scientific_execution_api = ScientificExecutionAPI(self.scientific_executions, self.api_v1, self.scientific_execution_dispatcher, self.scientific_observations)
        self.empirical_results = EmpiricalResultPublicationService(self.artifacts, self.preregistrations)
        self.empirical_evidence_api = EmpiricalEvidenceAPI(self.empirical_results, self.api_v1)
        self.world_stream_api = WorldStreamAPI(self.sandbox, self._sandbox_inputs)
        self.reference_graph = ReferenceGraphService(self.artifacts)
        self.reference_graph_api = ReferenceGraphAPI(self.reference_graph)
        self.cross_graph = CrossGraphService(self.root, self.artifacts)
        self.cross_graph_api = CrossGraphAPI(self.cross_graph)

    def dispatch(self, method: str, url: str, payload: dict | None = None, headers: dict | None = None):
        parsed = urlparse(url); parts = [unquote(x) for x in parsed.path.strip("/").split("/") if x]
        query = parse_qs(parsed.query)
        if parts[:2] == ["api", "v1"]:
            if len(parts) >= 3 and parts[2] in {"scientific-executions", "execution-authorizations"}:
                return self.scientific_execution_api.dispatch(method, parts[2:], query, payload, headers)
            if len(parts) >= 3 and parts[2] == "empirical-results":
                return self.empirical_evidence_api.dispatch(method, parts[2:], query, payload, headers)
            if len(parts) >= 3 and parts[2] == "world-stream":
                if method != "GET" and headers:
                    self.api_v1._authorize(headers)
                return self.world_stream_api.dispatch(method, parts[3:], query, payload)
            if len(parts) >= 3 and parts[2] == "reference-graph":
                return self.reference_graph_api.dispatch(method, parts[3:], query, payload, headers)
            if len(parts) >= 3 and parts[2] == "cross-graph":
                return self.cross_graph_api.dispatch(method, parts[3:], query, payload, headers)
            return self.api_v1.dispatch(method, parts[2:], query, payload, headers)
        try:
            if method == "GET" and parts == ["api","capabilities"]:
                return 200,{"schema_version":"terrario.lab.capability/v1","definitions":thaw(self.capabilities.definitions()),"matrix":{x:thaw(audited_agent_assessments(x)) for x in self.agent_inspector.IDS}}
            if method == "GET" and parts == ["api","agents"]: return 200,thaw(self.agent_inspector.all())
            if method == "GET" and len(parts)==3 and parts[:2]==["api","agents"]: return 200,thaw(self.agent_inspector.describe(parts[2]))
            if method == "GET" and len(parts)==4 and parts[:2]==["api","agents"] and parts[3]=="runtime":
                return 200,thaw(self.agent_inspector.runtime(self.sandbox,query.get("run_id",[None])[0]))
            if method == "GET" and parts == ["api","metrics"]: return 200,thaw(self.metrics.definitions())
            if method == "GET" and parts == ["api","agent-concepts"]: return 200,thaw(agent_catalogue(query.get("agent",["A4"])[0]))
            if method == "GET" and parts == ["api","observer","profiles"]: return 200,{"profiles":thaw(self.observers.profiles()),"channels":thaw(self.observers.channels())}
            if method == "GET" and len(parts)==3 and parts[:2]==["api","experiment-drafts"]:
                return 200,self.artifacts.current(parts[2],"ExperimentDraft").payload
            if method == "POST" and parts == ["api","compatibility"]:
                p=payload or {}; scenario=self.world_registry.get(str(p.get("scenario_id","D2")).upper()).scenario
                report=assess_compatibility(scenario,str(p.get("agent_id","A0")),bool(p.get("observation_interface",True)),bool(p.get("action_interface",True)),str(p.get("device","cpu"))=="cpu",bool(p.get("reset_interface",True)))
                return 200,{"requirements":thaw(scenario_requirements(scenario)),"report":thaw(report)}
            if method == "POST" and parts == ["api","metrics","applicability"]:
                p=payload or {}; scenario=self.world_registry.get(str(p.get("scenario_id","D2")).upper()).scenario
                return 200,thaw(self.metrics.applicability(str(p["metric_id"]),scenario,tuple(p.get("observer_signals",()))))
            if method == "POST" and parts == ["api","observer","estimate"]:
                p=payload or {}; return 200,thaw(self.observers.estimate(str(p.get("profile_id","STANDARD")),p.get("steps"),p.get("trials"),int(p.get("checkpoints",0)),int(p.get("forensic_window_steps",0))))
            if method == "POST" and parts == ["api","experiment-drafts","validate"]:
                draft,scenario=self._experiment_draft_input(payload or {}); findings=validate_experiment_draft(draft,scenario,self.metrics,self.observers)
                return 200,{"artifact_type":"ExperimentDraft","scientific_execution":False,"draft":thaw(replace(draft,state=state_for(findings))),"scientific_hash":draft.content_hash,"findings":thaw(findings)}
            if method == "POST" and parts == ["api","experiment-drafts"]:
                draft,scenario=self._experiment_draft_input(payload or {}); findings=validate_experiment_draft(draft,scenario,self.metrics,self.observers); draft=replace(draft,state=state_for(findings))
                try:
                    stored=self.artifacts.create_artifact("ExperimentDraft",thaw(draft),draft.schema_version,
                        scientific_payload=draft.scientific_payload(),artifact_id=draft.draft_id,
                        classification="SCIENTIFIC_DESIGN_DRAFT",reason="experiment draft creation",initial_state=draft.state.value)
                except (DuplicateArtifact,ProvenanceConflict):
                    return 409,{"error":"silent experiment draft overwrite prohibited","category":"PROVENANCE_ERROR"}
                return 201,{"artifact_type":"ExperimentDraft","scientific_execution":False,"draft":stored.payload,"scientific_hash":stored.scientific_hash,"version_id":stored.version_id,"durable":True,"findings":thaw(findings)}
            if method == "POST" and parts == ["api","experiment-drafts","diff"]:
                p=payload or {}; parent=experiment_draft_from_payload(self.artifacts.current(str(p["parent_id"]),"ExperimentDraft").payload); child=parent.derive(str(p.get("reason","derived draft")),**self._experiment_changes(p.get("changes",{})))
                return 200,{"parent":parent.draft_id,"child":thaw(child),"diff":thaw(draft_diff(parent,child)),"persisted":False}
            if method == "POST" and parts == ["api","trial-matrices","build"]:
                draft,scenario=self._experiment_draft_input(payload or {}); findings=validate_experiment_draft(draft,scenario,self.metrics,self.observers)
                blockers=tuple(sorted({x.code for x in findings if x.blocking}))
                condition_ids = (tuple(item.condition_id for item in draft.hypothesis_mapping.conditions)
                                 if draft.hypothesis_mapping is not None
                                 else (*draft.agent_ids, *(c.control_id for c in draft.controls)))
                by_condition={key:blockers for key in condition_ids} if blockers else {}
                matrix=build_trial_matrix(draft,by_condition,int((payload or {}).get("warning_threshold",500)))
                matrix_payload=thaw(matrix); matrix_scientific={key:value for key,value in matrix_payload.items() if key not in {"warnings","execution_performed"}}
                matrix_id=f"TM-{durable_content_hash(matrix_scientific)[:20]}"
                stored=self.artifacts.create_artifact("TrialMatrix",matrix_payload,"terrario.lab.trial-matrix/v1",
                    scientific_payload=matrix_scientific,artifact_id=matrix_id,classification="NON_EXECUTING_TRIAL_MATRIX",
                    reason="trial matrix materialization",initial_state="MATERIALIZED",deduplicate=True)
                return 200,{"artifact_type":"TrialMatrix","execution_performed":False,"matrix":stored.payload,"matrix_id":stored.artifact_id,"version_id":stored.version_id,"durable":True,"deduplicated":stored.deduplicated,"findings":thaw(findings)}
            if method == "GET" and parts == ["api","worlds"]: return 200, thaw(self.world_registry.entries())
            if method == "GET" and len(parts)==3 and parts[:2]==["api","worlds"]:
                entry=self.world_registry.get(parts[2].upper()); return 200, thaw(entry)
            if method == "GET" and parts == ["api","studio","d2"]:
                if self.d2_configuration is None: return 404,{"error":"D2 is not implemented in this project root"}
                return 200, {"configuration":thaw(self.d2_configuration),"views":thaw(d2_views(self.world_registry.get("D2"))),"generalization":generalization_check(self.world_registry)}
            if method == "GET" and parts == ["api", "studio", "d2", "protocol-audit"]:
                scenario_path = self.root / "scenarios" / "d2_properties.yaml"
                if not scenario_path.exists(): return 404, {"error": "D2 protocol scenario is unavailable"}
                return 200, thaw(D2BindingProtocol(scenario_path).self_audit())
            if method == "GET" and parts == ["api", "studio", "d2", "visual-fixture"]:
                scenario_path = self.root / "scenarios" / "d2_properties.yaml"
                if not scenario_path.exists(): return 404, {"error": "D2 protocol scenario is unavailable"}
                fixture = build_d2_visual_validation_fixture(scenario_path).payload()
                validate_visual_fixture_payload(fixture)
                return 200, fixture
            if method == "GET" and len(parts)==4 and parts[:2]==["api","worlds"] and parts[3]=="preview":
                wid=parts[2].upper(); seed=int(query.get("seed",[42])[0]); compiled=self.compiled_worlds[wid]
                self.preregistrations.record_exposure(wid,compiled.definition.content_hash,seed,"PREVIEWED","local-user","LEGACY_WORLD_PREVIEW",f"{wid}:{seed}")
                return 200,thaw(preview(compiled,seed))
            if method == "GET" and len(parts)==4 and parts[:2]==["api","worlds"] and parts[3]=="seeds":
                wid=parts[2].upper(); values=query.get("values",["42"])[0]; seeds=[int(x) for x in values.split(",") if x]; compiled=self.compiled_worlds[wid]
                for seed in seeds: self.preregistrations.record_exposure(wid,compiled.definition.content_hash,seed,"INSPECTED","local-user","LEGACY_SEED_BROWSER",f"{wid}:{seed}")
                return 200,thaw(SeedBrowser(compiled).analyze(seeds))
            if method == "GET" and parts == ["api","sandbox"]:
                return 200,{"schema_version":"terrario.lab.sandbox-sessions/v1","limit":MAX_ACTIVE_SESSIONS,"active":list(self.sandbox.active())}
            if method == "GET" and len(parts)==4 and parts[:2]==["api","sandbox"] and parts[3]=="measures":
                # Computed here, not in the page: the screening harness must read
                # the same meshes the screen shows, or they would drift apart.
                return 200,thaw(measure_run(thaw(self.sandbox.get(parts[2]).timeline)))
            if method == "GET" and len(parts)>=3 and parts[:2]==["api","sandbox"]:
                run=self.sandbox.get(parts[2]); return 200,(thaw(run.timeline) if len(parts)==4 and parts[3]=="trace" else serialize_run(run))
            if method == "GET" and len(parts)==4 and parts[:3]==["api","worlds","drafts"]:
                return 200,self.artifacts.current(parts[3],"WorldDraft").payload
            if method == "GET" and len(parts)==3 and parts[:2]==["api","trial-matrices"]:
                return 200,self.artifacts.current(parts[2],"TrialMatrix").payload
            if method == "POST" and parts == ["api","worlds","validate"]:
                draft=self._draft_input(payload or {})
                findings=validate_draft(draft); return 200,{"valid":not any(x.blocking for x in findings),"findings":thaw(findings),"draft":thaw(draft)}
            if method == "POST" and parts == ["api","worlds","drafts"]:
                draft=self._draft_input(payload or {}); findings=validate_draft(draft)
                if any(x.blocking for x in findings): return 400,{"error":"invalid world draft","findings":thaw(findings),"category":"WORLD_ERROR"}
                draft_payload=thaw(draft); scientific={key:value for key,value in draft_payload.items() if key not in {"draft_id","provenance"}}
                try:
                    stored=self.artifacts.create_artifact("WorldDraft",draft_payload,draft.schema_version,
                        scientific_payload=scientific,artifact_id=draft.draft_id,classification="WORLD_DESIGN_DRAFT",
                        reason="world draft creation",initial_state="DRAFT")
                except (DuplicateArtifact,ProvenanceConflict):
                    return 409,{"error":"silent draft overwrite prohibited","category":"PROVENANCE_ERROR"}
                return 201,{"draft":stored.payload,"version_id":stored.version_id,"scientific_hash":stored.scientific_hash,"durable":True,"findings":thaw(findings)}
            if method == "POST" and parts == ["api","worlds","preview"]:
                draft=self._draft_input(payload or {}); compiled=compile_draft(draft); seed=int((payload or {}).get("seed",42))
                self.preregistrations.record_exposure(compiled.definition.world_id,compiled.definition.content_hash,seed,"PREVIEWED","local-user","WORLD_DRAFT_PREVIEW",draft.draft_id)
                return 200,thaw(preview(compiled,seed))
            if method == "POST" and parts == ["api","worlds","compile"]:
                wid=str((payload or {}).get("world_id","D2")).upper(); compiled=self.compiled_worlds[wid]; return 200,{"definition":thaw(compiled.definition),"definition_hash":compiled.definition.content_hash,"warnings":thaw(compiled.warnings)}
            if method == "POST" and parts == ["api","sandbox","validate"]:
                spec,config,compiled=self._sandbox_inputs(payload or {}); instance=generate_instance(compiled,spec.world_seed); return 200,self.sandbox.validate_spec(spec,config,compiled,instance)
            if method == "POST" and parts == ["api","sandbox"]:
                spec,config,compiled=self._sandbox_inputs(payload or {})
                self.preregistrations.record_exposure(compiled.definition.world_id,compiled.definition.content_hash,spec.world_seed,"SANDBOXED","local-user","ENGINEERING_SANDBOX",durable_content_hash(thaw(spec))[:24])
                return 201,serialize_run(self.sandbox.create(spec,config,compiled))
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
            if method == "POST" and parts == ["api", "operational-hypotheses"]:
                draft, experiment = self._derive_operational_hypothesis()
                stored = self.artifacts.create_artifact(
                    "OperationalHypothesisDraft", draft.payload(), "terrario.theory.hypothesis-draft/v2",
                    scientific_payload=draft.payload(), artifact_id=draft.semantic_id,
                    classification="REVIEW_REQUIRED_HYPOTHESIS", reason="source-backed operational hypothesis derivation",
                    initial_state=draft.epistemic_status, deduplicate=True,
                )
                experiment_payload = thaw(experiment)
                experiment_scientific = experiment.scientific_payload()
                try:
                    prior_experiment = self.artifacts.current(experiment.draft_id, "ExperimentDraft")
                except ArtifactNotFound:
                    experiment_stored = self.artifacts.create_artifact(
                        "ExperimentDraft", experiment_payload, experiment.schema_version,
                        scientific_payload=experiment_scientific, artifact_id=experiment.draft_id,
                        classification="REVIEW_BLOCKED_DERIVED_EXPERIMENT_DRAFT",
                        reason="CL-4 deterministic mapping from review-required operational hypothesis",
                        initial_state=experiment.state.value, deduplicate=True,
                    )
                else:
                    if prior_experiment.scientific_hash == durable_content_hash(experiment_scientific):
                        experiment_stored = prior_experiment
                    else:
                        experiment_stored = self.artifacts.create_version(
                            experiment.draft_id, experiment_payload, experiment.schema_version,
                            scientific_payload=experiment_scientific,
                            classification="REVIEW_BLOCKED_DERIVED_EXPERIMENT_DRAFT",
                            reason="CL7 observer-only metric channel materialization before review",
                            delta={"reason": "planner_proposal_trace channel added to exact declared metric"},
                            state=experiment.state.value, deduplicate=True,
                        )
                lineage = self._reconcile_operational_draft_binding(experiment_stored, draft.semantic_id)
                return 201, {"artifact_type": "OperationalHypothesisDraft", "durable": True,
                             "artifact_id": stored.artifact_id, "deduplicated": stored.deduplicated, "hypothesis": stored.payload,
                             "scientific_hash": stored.scientific_hash, "experiment_draft_preview": experiment_payload,
                             "experiment_draft": {"artifact_id": experiment_stored.artifact_id,
                                 "version_id": experiment_stored.version_id, "scientific_hash": experiment_stored.scientific_hash,
                                 "state": self.artifacts.current_state(experiment_stored.version_id),
                                 "deduplicated": experiment_stored.deduplicated, "payload": experiment_stored.payload},
                             "experiment_draft_lineage": lineage,
                             "scientific_execution": False}
            if method != "GET": return 405, {"error":"mutation endpoint not available; configuration validation creates no persisted state"}
            if parts == ["api", "status"]:
                return 200, {"mode": "READ_ONLY", "experiments": len(self.model.experiments()), "runs": len(self.model.runs()), "theory": self.theory_summary, "h_adapt": "BLOCKED_CUDA", "durable_artifacts": self.artifacts.count(), "database_integrity": self.artifacts.integrity_check()}
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
            if parts == ["api", "operational-hypergraph"]:
                return 200, {"schema_version": "terrario.operational-hypergraph/v1",
                             "classification": "OPERATIONAL_DERIVED_NOT_EVIDENCE",
                             "hyperedges": thaw(HypergraphAdapter.operational_catalog())}
            if parts == ["api", "operational-hypotheses", "status"]:
                return 200, {"available": self._operational_source_available(),
                             "source_root_configured": self.primary_source_root is not None,
                             "required_environment": "TERRARIO_PRIMARY_SOURCE_ROOT",
                             "classification": "REVIEW_REQUIRED_HYPOTHESIS_ONLY"}
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
        except (KeyError, IndexError, ValueError, ArtifactNotFound) as exc:
            return (404 if method=="GET" else 400), {"error": str(exc),"category":getattr(exc,"code","CONFIG_ERROR")}

    @staticmethod
    def _one(value): return (200, thaw(value)) if value is not None else (404, {"error": "not found"})

    def _operational_source_available(self) -> bool:
        if self.primary_source_root is None:
            return False
        expected = self.primary_source_root / "09_Inteligencia_Formal_AGI" / "TI-0077_Yann_LeCun_A_Path_Towards_Autonomous_Machine_Intelligence.pdf"
        return expected.is_file()

    def _derive_operational_hypothesis(self):
        """The one reviewed operational path; no candidate/role inference is accepted."""
        if not self._operational_source_available() or self.theory_import is None:
            raise ValueError("source-backed derivation unavailable; configure TERRARIO_PRIMARY_SOURCE_ROOT with the verified corpus")
        snapshot = Path(self.theory_summary.get("snapshot_id", ""))
        snapshot_dir = self.root / "theory_snapshots" / snapshot
        imported = TheoryIngestor(snapshot_dir, include_operational_evidence=True).ingest()
        evidence_dir = snapshot_dir.parent.parent / "theory_operational_artifacts" / snapshot_dir.name

        def edge(candidate_id: str):
            candidate = next(item for item in imported.hyperedges if item.id == candidate_id)
            bindings = load_bindings(evidence_dir / "HYPEREDGE_ROLE_BINDINGS_v0.2.csv", candidate_id)
            return materialize(candidate, bindings, imported, primary_source_root=self.primary_source_root)

        edge02, edge08 = edge("HYPERCAND-02"), edge("HYPERCAND-08")
        derived = compose(edge02, edge08, compatibility=(RoleCompatibility(
            BindingRequirement("agent", "agent"), BindingRequirement("actor", "action_sequence_proposer"),
            "both source-backed roles explicitly produce actions",
        ),), rule=CompositionRule("ACTION_PRODUCING_AGENT_REFINEMENT", "v1", "architectural actor refines formal agent action role"),
            provenance="role-compatible structural refinement; TI-0071 + TI-0077")
        hypothesis = OperationalHypothesisCompiler().compile(derived, {
            edge02.semantic_id: edge02, edge08.semantic_id: edge08, derived.semantic_id: derived,
        })
        entry = self.world_registry.get("D2")
        experiment = OperationalExperimentCompiler().compile(
            hypothesis, scenario=entry.scenario, difficulty_fingerprint=configuration_for(entry).difficulty.fingerprint,
        )
        return hypothesis, experiment

    def _reconcile_operational_draft_binding(self, current, hypothesis_id: str):
        """Link a review-blocked pre-binding draft to its executable binding repair.

        Only a draft that is still review-blocked and has the same scientific
        question may be superseded.  This prevents a new config contract from
        silently replacing a preregistered or executed protocol.
        """
        def mapping_key(payload):
            mapping = payload.get("hypothesis_mapping") or {}
            return (
                mapping.get("hypothesis_semantic_id"), mapping.get("prediction"),
                mapping.get("metric_id"), tuple(mapping.get("source_claim_ids") or ()),
            )
        target_key = mapping_key(current.payload)
        if target_key[0] != hypothesis_id:
            raise ValueError("operational experiment lineage hypothesis mismatch")
        candidates = [item for item in self.artifacts.list_artifacts("ExperimentDraft")
                      if item.artifact_id != current.artifact_id and mapping_key(item.payload) == target_key]
        linked = []
        for old in candidates:
            old_state = self.artifacts.current_state(old.version_id)
            if old_state not in {"REVIEW_BLOCKED", "SUPERSEDED"}:
                raise ValueError("operational draft binding repair refuses non-review-blocked history")
            with self.artifacts.transaction() as con:
                existing = con.execute("SELECT link_id FROM artifact_links WHERE source_version_id=? AND target_version_id=? AND relation='SUPERSEDED_BY'", (old.version_id, current.version_id)).fetchone()
                if existing:
                    linked.append({"old_version_id": old.version_id, "link_id": existing["link_id"], "deduplicated": True})
                    continue
                now = self.artifacts.now()
                if old_state != "SUPERSEDED":
                    sequence = con.execute("SELECT COALESCE(MAX(sequence),0)+1 FROM artifact_state_events WHERE version_id=?", (old.version_id,)).fetchone()[0]
                    self.artifacts._insert_state_event(con, old.version_id, int(sequence), old_state, "SUPERSEDED", "CL7-CONDITION-BINDING-REPAIR", "replaced by explicit immutable condition binding", now)
                link_id = "experiment-draft-supersession-" + durable_content_hash((old.version_id, current.version_id))[:24]
                provenance = {"schema_version": "terrario.experiment-draft-binding-reconciliation/v1",
                              "reason": "explicit condition config replaces non-executable prose-only mapping",
                              "old_scientific_hash": old.scientific_hash, "current_scientific_hash": current.scientific_hash,
                              "hypothesis_id": hypothesis_id}
                con.execute("INSERT INTO artifact_links(link_id,source_version_id,target_version_id,relation,epistemic_status,provenance_json,created_at) VALUES(?,?,?,?,?,?,?)", (link_id, old.version_id, current.version_id, "SUPERSEDED_BY", "REVIEW_REQUIRED", json.dumps(provenance, sort_keys=True, separators=(",", ":")), now))
                self.artifacts._insert_audit(con, self.artifacts._identifier("correlation"), "CL7-CONDITION-BINDING-REPAIR", "EXPERIMENT_DRAFT_BINDING_RECONCILED", "ExperimentDraft", old.artifact_id, {"replacement_artifact_id": current.artifact_id, "link_id": link_id}, now)
                linked.append({"old_version_id": old.version_id, "link_id": link_id, "deduplicated": False})
        return tuple(linked)

    def _sandbox_inputs(self,payload):
        wid=str(payload.get("world_id","D2")).upper(); entry=self.world_registry.get(wid); compiled=self.compiled_worlds[wid]
        base=configuration_for(entry); config=derive_sandbox(base)
        if payload.get("agent_reference"): config=replace(config,agent_reference=str(payload["agent_reference"]))
        classification=ExecutionClassification(payload.get("classification","ENGINEERING_SANDBOX"))
        # The chosen mix of concepts. Absent means A4's defaults, so every existing
        # caller keeps the organism it was already running.
        spec=make_spec(config,compiled,int(payload.get("world_seed",42)),int(payload.get("agent_seed",1000045)),int(payload.get("step_limit",100)),classification,validate_selection(payload.get("agent_configuration"),str(payload.get("agent_reference","A4"))))
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

    def _experiment_draft_input(self,payload):
        allowed={"draft_id","scenario_id","variant_ids","agent_ids","controls","metric_ids","observer_profile","world_seeds","agent_seeds","repetitions","step_limit","device_requirement","available_ground_truth","available_signals","manipulation_check","transfer_phase","source_artifact","ui_preferences","warning_threshold"}
        unknown=set(payload)-allowed
        if unknown: raise ValueError(f"unknown experiment draft fields: {sorted(unknown)}")
        scenario_id=str(payload.get("scenario_id","D2")).upper(); entry=self.world_registry.get(scenario_id); scenario=entry.scenario
        if scenario is None: raise ValueError("scenario is not implemented")
        config=configuration_for(entry); profile_id=str(payload.get("observer_profile","STANDARD")).upper(); profile=self.observers.profile(profile_id)
        controls=tuple(ControlCondition(str(x["control_id"]),str(x.get("control_type","BASELINE_AGENT")),str(x["agent_id"]),str(x.get("contrast","")),str(x.get("availability","AVAILABLE"))) for x in payload.get("controls",({"control_id":"A0-baseline","control_type":"BASELINE_AGENT","agent_id":"A0","contrast":"target agent versus random baseline"},)))
        source=str(payload.get("source_artifact","UNSELECTED_DESIGN"))
        provenance=DraftProvenance("lab-user","experiment composition",source,"READY_FOR_HUMAN_REVIEW")
        draft=ExperimentDraft(str(payload.get("draft_id","experiment-draft-1")),EXPERIMENT_DRAFT_SCHEMA,DraftState.DRAFT,
            scenario.scenario_id,scenario.content_hash,tuple(str(x) for x in payload.get("variant_ids",(f"{scenario_id}-base",))),config.difficulty.fingerprint,
            tuple(str(x) for x in payload.get("agent_ids",("A4",))),controls,
            tuple(str(x) for x in payload.get("metric_ids",(f"{scenario_id}-energy-trajectory",))),profile_id,profile.channels,
            tuple(int(x) for x in payload.get("world_seeds",(11,12))),tuple(int(x) for x in payload.get("agent_seeds",(21,22))),
            int(payload.get("repetitions",1)),int(payload.get("step_limit",100)),str(payload.get("device_requirement","cpu")),
            scenario.required_ground_truth,tuple(str(x) for x in payload.get("available_ground_truth",scenario.required_ground_truth)),
            tuple(str(x) for x in payload.get("available_signals",("agent_energy",))),payload.get("manipulation_check","observer verifies structured rules_version event" if scenario.interventions else None),
            payload.get("transfer_phase"),provenance,dict(payload.get("ui_preferences",{})))
        return draft,scenario

    @staticmethod
    def _experiment_changes(changes):
        allowed={"variant_ids","agent_ids","metric_ids","observer_profile","observer_channels","world_seeds","agent_seeds","repetitions","step_limit","device_requirement","available_ground_truth","available_signals","manipulation_check","transfer_phase","ui_preferences"}
        unknown=set(changes)-allowed
        if unknown: raise ValueError(f"unsupported derived fields: {sorted(unknown)}")
        tuple_fields={"variant_ids","agent_ids","metric_ids","observer_channels","world_seeds","agent_seeds","available_ground_truth","available_signals"}
        return {k:(tuple(v) if k in tuple_fields else v) for k,v in changes.items()}

    def _hypergraph(self):
        if self.theory_graph:
            graph = self.theory_graph.export(); theory = graph["theory_graph"]; evidence = graph["evidence_graph"]
            portfolio_sources = ({entry.family.source_hyperedge_id for entry in self.experiment_portfolio.entries}
                                 if self.experiment_portfolio else set())
            nodes = []
            for raw in [*theory["nodes"], *evidence["nodes"]]:
                node = dict(raw)
                if node.get("node_type") == "HyperedgeCandidateRecord":
                    # Graph node keys are namespaced for graph identity while
                    # the portfolio is keyed by the source record identity.
                    # Publish the bridge explicitly so the browser never has
                    # to guess or strip a namespace to find a design.
                    source_id = str(node.get("original_id") or node.get("record_id") or "")
                    if source_id in portfolio_sources:
                        node["experiment_design_source_id"] = source_id
                nodes.append(node)
            return {"snapshot_id": graph["snapshot_id"], "nodes": nodes,
                    "edges": [*theory["edges"], *evidence["edges"]]}
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
            parsed = urlparse(self.path)
            stream_parts = [unquote(x) for x in parsed.path.strip("/").split("/") if x]
            if len(stream_parts) == 6 and stream_parts[:3] == ["api", "v1", "world-stream"] and stream_parts[3] == "sessions" and stream_parts[5] == "stream":
                acquired = False
                try:
                    api.api_v1._authorize(dict(self.headers))
                    session_id = stream_parts[4]
                    api.sandbox.acquire_subscriber(session_id)
                    acquired = True
                    after = int(parse_qs(parsed.query).get("after_sequence", ["-1"])[0])
                    self.send_response(200); self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Cache-Control", "no-cache, no-transform"); self.send_header("Connection", "keep-alive")
                    self.send_header("X-Accel-Buffering", "no"); self.end_headers()
                    last_heartbeat = 0.0
                    while True:
                        rows = api.sandbox.envelopes_after(session_id, after)
                        if rows:
                            for envelope in rows:
                                self.wfile.write(f"id: {envelope['sequence']}\nevent: {envelope['message_type']}\ndata: {json.dumps(envelope, separators=(',', ':'))}\n\n".encode())
                                after = max(after, int(envelope["sequence"]))
                            self.wfile.flush()
                        now = __import__("time").monotonic()
                        if now - last_heartbeat >= 5:
                            heartbeat = api.sandbox.heartbeat(session_id)
                            self.wfile.write(f"id: {heartbeat['sequence']}\nevent: HEARTBEAT\ndata: {json.dumps(heartbeat, separators=(',', ':'))}\n\n".encode()); self.wfile.flush()
                            after, last_heartbeat = heartbeat["sequence"], now
                        ctx = api.sandbox._live[session_id]
                        with ctx.changed: ctx.changed.wait(timeout=1.0)
                except (BrokenPipeError, ConnectionResetError):
                    return
                except PermissionError as exc:
                    self.send_error(403, str(exc)); return
                except ValueError as exc:
                    self.send_error(429, str(exc)); return
                finally:
                    if acquired: api.sandbox.release_subscriber(session_id)
            if len(stream_parts) == 8 and stream_parts[:2] == ["api", "v1"] and stream_parts[2] == "scientific-executions" and stream_parts[4] == "trials" and stream_parts[6] == "live" and stream_parts[7] == "stream":
                acquired = False
                try:
                    api.api_v1._authorize(dict(self.headers))
                    execution_id, trial_intent_id = stream_parts[3], stream_parts[5]
                    attempt_id = parse_qs(parsed.query).get("attempt_id", [None])[0]
                    if not attempt_id: self.send_error(400, "attempt_id is required"); return
                    # A cursor bound to a different attempt/execution/trial fails closed.
                    query = parse_qs(parsed.query)
                    for key, expected in (("cursor_execution_id", execution_id), ("cursor_trial_intent_id", trial_intent_id), ("cursor_attempt_id", attempt_id)):
                        supplied = query.get(key, [None])[0]
                        if supplied is not None and supplied != expected:
                            self.send_error(400, f"CURSOR_WRONG_ATTEMPT: {key}"); return
                    live = api.scientific_execution_dispatcher.live
                    live.acquire_subscriber(execution_id, trial_intent_id, attempt_id)
                    acquired = True
                    after = int(query.get("after_sequence", ["-1"])[0])
                    cursor = {"schema_version": "terrario.scientific-live/v1", "execution_id": execution_id,
                              "trial_intent_id": trial_intent_id, "attempt_id": attempt_id, "frame_sequence": after}
                    self.send_response(200); self.send_header("Content-Type", "text/event-stream")
                    self.send_header("Cache-Control", "no-cache, no-transform"); self.send_header("Connection", "keep-alive")
                    self.send_header("X-Accel-Buffering", "no"); self.end_headers()
                    last_heartbeat = 0.0
                    while True:
                        try:
                            page = live.frames_after(execution_id, trial_intent_id, attempt_id, cursor)
                        except Exception as exc:
                            payload = {"code": getattr(exc, "code", "SCIENTIFIC_LIVE_ERROR"), "message": str(exc),
                                       "attempt_id": attempt_id, "earliest_hint": after + 1}
                            self.wfile.write(f"id: {max(after, 0)}\nevent: RESYNC_REQUIRED\ndata: {json.dumps(payload, separators=(',', ':'))}\n\n".encode())
                            self.wfile.flush(); return
                        for frame in page["frames"]:
                            self.wfile.write(f"id: {frame['frame_sequence']}\nevent: FRAME\ndata: {json.dumps(frame, separators=(',', ':'))}\n\n".encode())
                            after = int(frame["frame_sequence"])
                        cursor = page["cursor"]
                        if page["frames"]: self.wfile.flush()
                        if page["terminal"]:
                            payload = {"schema_version": "terrario.scientific-live/v1", **page["terminal_state"],
                                       "execution_id": execution_id, "trial_intent_id": trial_intent_id, "attempt_id": attempt_id}
                            self.wfile.write(f"id: {max(after, 0)}\nevent: TERMINAL\ndata: {json.dumps(payload, separators=(',', ':'))}\n\n".encode())
                            self.wfile.flush(); return
                        now = __import__("time").monotonic()
                        if now - last_heartbeat >= 5:
                            payload = {"schema_version": "terrario.scientific-live/v1", "execution_id": execution_id,
                                       "trial_intent_id": trial_intent_id, "attempt_id": attempt_id, "frame_sequence": after}
                            self.wfile.write(f"id: {max(after, 0)}\nevent: HEARTBEAT\ndata: {json.dumps(payload, separators=(',', ':'))}\n\n".encode()); self.wfile.flush()
                            last_heartbeat = now
                        live.wait_for_frames(execution_id, trial_intent_id, attempt_id, after, timeout=1.0)
                except (BrokenPipeError, ConnectionResetError):
                    return
                except PermissionError as exc:
                    self.send_error(403, str(exc)); return
                except ValueError as exc:
                    self.send_error(429, str(exc)); return
                finally:
                    if acquired: api.scientific_execution_dispatcher.live.release_subscriber(execution_id, trial_intent_id, attempt_id)
            if self.path.startswith("/api/"):
                status, payload = api.dispatch("GET", self.path, headers=dict(self.headers))
                body = json.dumps(payload).encode()
                self.send_response(status); self.send_header("Content-Type", "application/json")
            else:
                rel = urlparse(self.path).path.lstrip("/") or "index.html"
                target = (static_dir / rel).resolve()
                if static_dir not in target.parents and target != static_dir or not target.is_file():
                    self.send_error(404); return
                body = target.read_bytes(); self.send_response(200)
                self.send_header("Content-Type", mimetypes.guess_type(target.name)[0] or "application/octet-stream")
            try:
                self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                return
        def do_POST(self):
            length=int(self.headers.get("Content-Length","0")); raw=self.rfile.read(length)
            if length > 1_048_576: self.send_error(413,"JSON payload exceeds 1 MiB"); return
            try: payload=json.loads(raw or b"{}")
            except json.JSONDecodeError as exc: self.send_error(400,str(exc)); return
            status,result=api.dispatch("POST",self.path,payload,dict(self.headers)); body=json.dumps(result).encode()
            try:
                self.send_response(status); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
            except (BrokenPipeError, ConnectionResetError):
                return
        def log_message(self, fmt, *args): pass
    return Handler


class LabHTTPServer(ThreadingHTTPServer):
    """Local lab server sized for a browser, not for a single client.

    The `socketserver` default accept queue is 5. A browser opens several
    parallel connections per origin and this API also holds long-lived SSE
    streams, so five pending connections is easy to exceed during a long
    session or an end-to-end suite; the overflow surfaces to the browser as a
    refused connection rather than as a slow one. `block_on_close` is disabled
    so an open SSE stream cannot keep the process alive on shutdown.
    """

    request_queue_size = 128
    daemon_threads = True
    block_on_close = False

    #: Disconnects that are normal for a browser, not faults of this server.
    _CLIENT_DISCONNECT = (BrokenPipeError, ConnectionResetError, ConnectionAbortedError)

    def handle_error(self, request, client_address):
        """Keep a closed page from looking like a server fault.

        `BaseHTTPRequestHandler.handle_one_request` flushes the response with
        only `TimeoutError` guarded, so a viewer closing a page mid-response
        reaches `handle_error` and prints a traceback. The request is already
        over and both SSE handlers release their subscriber in a `finally`, so
        there is nothing to recover: only the noise is suppressed. Every other
        exception still reports normally.
        """
        if isinstance(sys.exc_info()[1], self._CLIENT_DISCONNECT):
            return
        super().handle_error(request, client_address)


def serve(
    root: str | Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    data_root: str | Path | None = None,
):
    if data_root is not None and not Path(data_root).is_absolute():
        raise ValueError("--data-root must be absolute; refusing an implicit root escape")
    api = LabAPI(root, data_root=data_root); static_dir = Path(__file__).parent / "static"
    server = LabHTTPServer((host, port), handler_factory(api, static_dir))
    print(f"Terrario Lab: http://{host}:{port}", flush=True)
    server.serve_forever()


def main():
    parser = argparse.ArgumentParser(); parser.add_argument("--root", default="."); parser.add_argument("--host", default="127.0.0.1"); parser.add_argument("--port", type=int, default=8765); parser.add_argument("--data-root")
    args = parser.parse_args(); serve(args.root, args.host, args.port, args.data_root)


if __name__ == "__main__": main()
