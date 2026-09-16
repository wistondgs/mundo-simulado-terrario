"""Run the CL-7 paired design with NEW seeds against a SCRATCH data root and extract results.

Purpose: see how the preserved / ablated arms behave without touching the live
scientific root and without peeking at the preregistered seed cells (11,12 x
21,22). The design comes from a stored ExperimentDraft payload (the real CL-7
draft) and is DERIVED: only world_seeds and agent_seeds change; the hypothesis
mapping, arms, metric and manipulation check travel unchanged, and provenance
records the parent and the changed fields.

Every human gate is signed by this script as `local-user`. That is what makes
this a scratch run and not science. Nothing here is evidence.
"""
from __future__ import annotations

import argparse
import json
import secrets
import sys
import time
from dataclasses import replace
from pathlib import Path

from terrario.lab.api import LabAPI
from terrario.lab.persistence import DuplicateArtifact, ProvenanceConflict
from terrario.lab.experiment_composer import build_trial_matrix, state_for, validate_draft
from terrario.lab.models import thaw
from terrario.lab.persistence.canonical import content_hash as durable_content_hash
from terrario.lab.persistence.codecs import experiment_draft_from_payload
from terrario.lab.planning_trace_metric import PlanningTraceMetricError, evaluate_scientific_trace

HUMAN = "◆ COMPUERTA HUMANA"


def step(n, who, what): print(f"\n[{n:02d}] {who:<22} {what}")
def show(**f):
    for k, v in f.items(): print(f"      {k:<22} {v}")
def ok(status, payload, expected=201):
    if status != expected: raise SystemExit(f"esperaba {expected}, recibí {status}: {json.dumps(payload)[:500]}")
    return payload


def num(value):
    return float(value) if isinstance(value, (int, float)) and value == value else None


def extract(api, execution_id: str, out: str) -> None:
    """Per cell: CL-7 metric from the sealed trace + per-tick series. Read-only."""
    step(8, "Resultados", "Por celda: métrica CL-7 desde la traza sellada + series por tick")
    view = ok(*api.dispatch("GET", f"/api/v1/scientific-executions/{execution_id}"), expected=200)["data"]
    status, payload = api.dispatch("GET", f"/api/v1/scientific-executions/{execution_id}/verify")
    if status == 200:
        report = payload["data"]
    else:
        with api.artifacts.transaction() as con:
            row = con.execute("SELECT report_json FROM scientific_execution_verifications WHERE execution_id=? ORDER BY rowid DESC LIMIT 1", (execution_id,)).fetchone()
        report = json.loads(row["report_json"]) if row else {"classification": "UNVERIFIED"}
        print(f"      (verify devolvió {status}; se usa el informe sellado en la corrida: {report.get('classification')})")
    # plan.trial_identities is keyed by the matrix trial_id; trace artifacts by
    # trial_intent_id. Both carry the seeds and agent_config, which is the join.
    prereg = api.artifacts.current(view["preregistration_id"], "Preregistration").payload["draft"]
    matrix = api.artifacts.get_version(prereg["protocol"]["trial_matrix_version_id"]).payload
    def arm_of(cfg): return "PLANNER_PRESERVED" if (cfg or {}).get("use_planner") else "PLANNER_ABLATED"
    cell_by_key = {(int(c["world_seed"]), int(c["agent_seed"]), c["arm_id"]): c for c in matrix["cells"]}
    plan_by_key = {(int(t["world_seed"]), int(t["agent_seed"]), arm_of(t.get("agent_config"))): t for t in view["plan"]["trial_identities"]}
    traces = [x for x in view["artifacts"] if x["artifact_type"] == "SCIENTIFIC_TRACE"]
    cells = []
    for art in traces:
        page = ok(*api.dispatch("GET", f"/api/v1/scientific-executions/{execution_id}/trials/{art['trial_intent_id']}/frames?attempt_id={art['attempt_id']}&after_sequence=-1"), expected=200)["data"]
        frames = page["frames"]; ident = frames[0].get("identity", {}) if frames else {}
        cfg = dict(ident.get("agent_config") or {})
        if not cfg:  # fall back to the sealed observer manifest of the attempt
            import yaml
            manifest = Path(api.artifacts.data_root) / "runtime" / execution_id / art["attempt_id"] / "observer" / "manifest.yaml"
            if manifest.exists(): cfg = dict((yaml.safe_load(manifest.read_text())["config"]["scientific_trial_identity"].get("agent_config") or {}))
        key = (int(ident["world_seed"]), int(ident["agent_seed"]), arm_of(cfg))
        cell = cell_by_key.get(key, {}); plan = plan_by_key.get(key, {})
        try:
            m = evaluate_scientific_trace({"frames": frames}); metric = {"value": m.value, "numerator": m.numerator, "denominator": m.denominator}
        except PlanningTraceMetricError as exc:
            metric = {"error": str(exc)}
        series = {"tick": [], "energy": [], "uncertainty": [], "prediction_error": [], "policy_entropy": [], "selected_action_probability": []}
        for fr in frames:
            cs = fr.get("cognitive_state", {}) or {}
            series["tick"].append(int(fr["tick"])); series["energy"].append(num((fr.get("agent_observation") or {}).get("agent_energy")))
            for k in ("uncertainty", "prediction_error", "policy_entropy", "selected_action_probability"): series[k].append(num(cs.get(k)))
        energies = [e for e in series["energy"] if e is not None]
        cells.append({"trial_intent_id": art["trial_intent_id"], "attempt_id": art["attempt_id"], "trial_id": plan.get("trial_id"),
                      "arm": key[2], "seed_pair_id": cell.get("seed_pair_id"), "condition_id": plan.get("condition_id"),
                      "world_seed": key[0], "agent_seed": key[1], "agent_config": cfg, "frames": len(frames), "metric": metric,
                      "final_energy": energies[-1] if energies else None, "mean_energy": (sum(energies) / len(energies)) if energies else None, "series": series})
    cells.sort(key=lambda c: (c["seed_pair_id"] or "", c["arm"]))
    for c in cells:
        print(f"      {c['seed_pair_id'] or '?':<3} {c['arm']:<18} w{c['world_seed']} a{c['agent_seed']}  frames={c['frames']:<4} métrica={c['metric']}  E_final={c['final_energy']}")
    Path(out).write_text(json.dumps({"run": execution_id, "execution_id": execution_id, "verification": report,
                                     "world_seeds": prereg["protocol"].get("world_seeds") or sorted({c["world_seed"] for c in cells}),
                                     "agent_seeds": prereg["protocol"].get("agent_seeds") or sorted({c["agent_seed"] for c in cells}), "cells": cells}, indent=1))
    print(f"\nresultados escritos en {out}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("data_root"); ap.add_argument("--template", required=True)
    ap.add_argument("--world-seeds", default="41,42"); ap.add_argument("--agent-seeds", default="61,62")
    ap.add_argument("--out", required=True)
    ap.add_argument("--extract-only", metavar="EXECUTION_ID", help="skip the chain; extract results from a completed execution in this root")
    a = ap.parse_args()
    data_root = Path(a.data_root)
    if not data_root.is_absolute(): raise SystemExit("el root de datos debe ser absoluto")
    if data_root.resolve() == (Path(".").resolve() / ".terrario"): raise SystemExit("me niego a correr contra el data root científico vivo")
    world_seeds = tuple(int(x) for x in a.world_seeds.split(",")); agent_seeds = tuple(int(x) for x in a.agent_seeds.split(","))
    if set(world_seeds) & {11, 12} or set(agent_seeds) & {21, 22}:
        raise SystemExit("esas semillas son las preregistradas de CL-7; este guion existe para NO mirarlas")

    api = LabAPI(Path("."), data_root=data_root); tag = secrets.token_hex(4)
    if a.extract_only:
        print(f"EXTRACCIÓN sobre {a.extract_only} · root: {data_root}"); extract(api, a.extract_only, a.out); return
    print(f"CORRIDA {tag} · root: {data_root}")

    step(1, "Compose", "Cargar el diseño real de CL-7 y DERIVARLO: solo cambian las semillas")
    parent = experiment_draft_from_payload(json.loads(Path(a.template).read_text()))
    child = parent.derive("scratch: semillas nuevas, diseño CL-7 intacto", world_seeds=world_seeds, agent_seeds=agent_seeds)
    scenario = api.world_registry.get(child.scenario_id).scenario
    findings = validate_draft(child, scenario, api.metrics, api.observers); child = replace(child, state=state_for(findings))
    blockers = tuple(sorted({x.code for x in findings if x.blocking}))
    try:
        stored = api.artifacts.create_artifact("ExperimentDraft", thaw(child), child.schema_version, scientific_payload=child.scientific_payload(),
                                               artifact_id=child.draft_id, classification="SCIENTIFIC_DESIGN_DRAFT",
                                               reason="scratch derivation of the CL-7 design with new seeds", initial_state=child.state.value)
    except (DuplicateArtifact, ProvenanceConflict):
        # Same derivation on a reused scratch root: the durable version already exists.
        stored = api.artifacts.current(child.draft_id, "ExperimentDraft")
        print("      (draft derivado ya existía en este root; se reutiliza su versión exacta)")
    show(padre=parent.draft_id, hijo=child.draft_id, cambios=child.provenance.changed_fields, version_id=stored.version_id,
         hash=stored.scientific_hash[:16] + "…", estado=child.state.value, bloqueantes=blockers or "ninguno",
         brazos=[(c.condition_id, dict(c.agent_config)) for c in child.hypothesis_mapping.conditions])

    step(2, "Compose", "TrialMatrix desde la versión derivada (8 celdas = 4 pares × 2 brazos)")
    conditions = tuple(c.condition_id for c in child.hypothesis_mapping.conditions)
    matrix = build_trial_matrix(child, {k: blockers for k in conditions} if blockers else {}, 500)
    mp = thaw(matrix); ms = {k: v for k, v in mp.items() if k not in {"warnings", "execution_performed"}}
    stored_matrix = api.artifacts.create_artifact("TrialMatrix", mp, "terrario.lab.trial-matrix/v1", scientific_payload=ms,
                                                  artifact_id=f"TM-{durable_content_hash(ms)[:20]}", classification="NON_EXECUTING_TRIAL_MATRIX",
                                                  reason="scratch matrix", initial_state="MATERIALIZED", deduplicate=True)
    cell_by_seeds = {(c["world_seed"], c["agent_seed"], c["arm_id"]): c for c in mp["cells"]}
    show(matrix_id=stored_matrix.artifact_id, version_id=stored_matrix.version_id, celdas=mp["total_trials"], execution_performed=mp["execution_performed"])

    step(3, HUMAN, "Decisión sobre el diseño (firmada por el script)")
    req = ok(*api.dispatch("POST", "/api/v1/review-requests", {"artifact_version_id": stored.version_id, "reason": "scratch: diseño derivado"}))
    ok(*api.dispatch("POST", f"/api/v1/review-requests/{req['data']['review_id']}/decisions",
                     {"artifact_hash": stored.scientific_hash, "decision": "APPROVE_FOR_EXPERIMENT_DESIGN", "reason": "SCRATCH: firmado por script"}))

    step(4, "Preregistros", "Preregistro (allow_dirty_tree=True) → readiness → sellar → someter")
    pid = f"PR-CL7-SCRATCH-{tag}"
    created = ok(*api.dispatch("POST", "/api/v1/preregistrations", {"preregistration_id": pid, "experiment_draft_version_id": stored.version_id,
                 "trial_matrix_version_id": stored_matrix.version_id, "study_intent": "EXPLORATORY", "environment_requirement": {"allow_dirty_tree": True}}))
    ready = ok(*api.dispatch("GET", f"/api/v1/preregistrations/{pid}/readiness"), expected=200)["data"]
    show(readiness_completo=ready["complete"], bloqueantes=[f["rule_id"] for f in ready["findings"] if f["blocking"]])
    if not ready["complete"]: raise SystemExit("readiness bloqueado; no se fuerza")
    cand = ok(*api.dispatch("POST", f"/api/v1/preregistrations/{pid}/prepare-review", {"expected_hash": created["data"]["scientific_hash"], "reason": "scratch"}))
    root = cand["data"]["bundle_root_hash"]
    sub = ok(*api.dispatch("POST", f"/api/v1/preregistrations/{pid}/submit", {"reason": "scratch"}))

    step(5, HUMAN, "Decisión sobre el preregistro + LOCK (firmados por el script)")
    accepted = [{k: f[k] for k in ("finding_hash", "rule_id", "rule_version")} for f in cand["data"]["review_package"]["readiness"]["findings"] if not f["blocking"]]
    dec = ok(*api.dispatch("POST", f"/api/v1/review-requests/{sub['data']['review_id']}/decisions",
                           {"artifact_hash": root, "decision": "APPROVE_PREREGISTRATION", "reason": "SCRATCH", "warning_acceptances": accepted}))
    ok(*api.dispatch("POST", f"/api/v1/preregistrations/{pid}/lock", {"expected_hash": root, "decision_id": dec["data"]["decision_id"],
                     "reason": f"LOCK {root[:12]}", "idempotency_key": f"lock-{pid}"}))
    locked_root = api.preregistrations.get(pid)["scientific_hash"]; show(root_bloqueada=locked_root[:16] + "…")

    step(6, "Ejecución", "Solicitud → autorización (◆) → bind → plan → READY")
    ex = ok(*api.dispatch("POST", "/api/v1/scientific-executions", {"preregistration_root_hash": locked_root}))["data"]
    ceiling = {"cpu_cores": 1, "gpu_devices": [], "memory_bytes": 1024**3, "disk_bytes": 1024**3, "max_processes": 1, "wall_clock_seconds": 3600}
    auth = ok(*api.dispatch("POST", "/api/v1/execution-authorizations", {"preregistration_root_hash": locked_root, "scope_type": "ONE_EXECUTION",
              "max_execution_count": 1, "resource_ceiling": ceiling, "reason": "SCRATCH: autorización firmada por script"}))["data"]
    bound = ok(*api.dispatch("POST", f"/api/v1/scientific-executions/{ex['execution_id']}/bind-authorization",
                             {"authorization_id": auth["authorization_id"], "expected_revision": ex["revision"]}), expected=200)["data"]
    planned = ok(*api.dispatch("POST", f"/api/v1/scientific-executions/{ex['execution_id']}/plan", {"expected_revision": bound["revision"]}), expected=200)["data"]
    show(execution_id=ex["execution_id"], estado=planned["state"], trial_count=planned["plan"]["trial_count"], plan_hash=str(planned["plan_hash"])[:16] + "…")

    step(7, "Ejecución", "START + dispatch de las 8 celdas")
    started = ok(*api.dispatch("POST", f"/api/v1/scientific-executions/{ex['execution_id']}/commands",
                               {"command": "START", "command_id": f"scratch-start-{tag}", "expected_revision": planned["revision"]}), expected=200)["data"]
    t0 = time.monotonic(); view = started; rounds = 0
    while view["state"] not in {"COMPLETED", "FAILED", "CANCELLED", "ABORTED", "RECOVERY_REQUIRED"} and rounds < 12:
        view = ok(*api.dispatch("POST", f"/api/v1/scientific-executions/{ex['execution_id']}/dispatch", {"worker_id": f"scratch-worker-{tag}"}), expected=200)["data"]
        rounds += 1
    show(estado_terminal=view["state"], rondas_dispatch=rounds, segundos=round(time.monotonic() - t0, 1))
    report = ok(*api.dispatch("GET", f"/api/v1/scientific-executions/{ex['execution_id']}/verify"), expected=200)["data"]
    show(verificacion=report.get("classification"), avisos=report.get("warnings"))

    extract(api, view["execution_id"], a.out)


if __name__ == "__main__":
    main()
