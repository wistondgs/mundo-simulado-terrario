"""Walk the whole scientific chain, step by step, against a TUTORIAL data root.

This is a teaching script. It runs the real code path -- draft, matrix, design
review, preregistration, readiness, submission, review, lock, execution request,
authorization, plan, START, dispatch, terminal state, integrity verification --
and prints every identity it produces, so a reader can see what each gate is
and what it is not. It produces no scientific evidence: the data root is a
scratch directory and the design is throwaway.

Two gates are marked HUMAN. In real operation a person signs those with a
reason and a ceremony string; here the script signs them as the actor
"tutorial" so the chain can be watched end to end. That substitution is the
whole difference between a tutorial and science.
"""
from __future__ import annotations

import json
import secrets
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.api import LabAPI

HUMAN = "◆ COMPUERTA HUMANA"


def step(n: int, who: str, what: str) -> None:
    print(f"\n[{n:02d}] {who:<22} {what}")


def show(**fields: object) -> None:
    for key, value in fields.items():
        print(f"      {key:<22} {value}")


def ok(status: int, payload: dict, expected: int = 201) -> dict:
    if status != expected:
        raise SystemExit(f"esperaba {expected}, recibí {status}: {json.dumps(payload)[:400]}")
    return payload


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("uso: tutorial_scientific_chain.py <root de datos ABSOLUTO> -- nunca el .terrario vivo")
    data_root = Path(sys.argv[1])
    if not data_root.is_absolute():
        raise SystemExit("el root de datos debe ser absoluto; me niego a una ruta implícita")
    if data_root.resolve() == (Path(".").resolve() / ".terrario"):
        raise SystemExit("me niego a correr el tutorial contra el data root científico vivo")

    api = LabAPI(Path("."), data_root=data_root)
    tag = secrets.token_hex(4)
    offset = int(tag, 16) % 100000
    print(f"TUTORIAL {tag} · data root: {data_root}")

    step(1, "Compose", "ExperimentDraft durable (diseño desechable, un solo brazo, una semilla)")
    payload = {"draft_id": f"ED-TUTORIAL-{tag}", "scenario_id": "D2", "agent_ids": ["A4"], "controls": [],
               "world_seeds": [100000 + offset], "agent_seeds": [300000 + offset], "source_artifact": "HYPERCAND-01"}
    experiment = ok(*api.dispatch("POST", "/api/experiment-drafts", payload))
    show(version_id=experiment["version_id"], scientific_hash=experiment["scientific_hash"][:16] + "…",
         estado=experiment["draft"]["state"], ejecucion_cientifica=experiment["scientific_execution"])

    step(2, "Compose", "TrialMatrix durable (materializa celdas; execution_performed debe ser False)")
    matrix = ok(*api.dispatch("POST", "/api/trial-matrices/build", payload), expected=200)
    show(matrix_id=matrix["matrix_id"], version_id=matrix["version_id"],
         total_trials=matrix["matrix"]["total_trials"], execution_performed=matrix["matrix"]["execution_performed"])

    step(3, "Compose", "Solicitud de revisión humana del diseño (la que hoy tienes pendiente para CL-7)")
    request = ok(*api.dispatch("POST", "/api/v1/review-requests",
                               {"artifact_version_id": experiment["version_id"], "reason": "tutorial: revisar diseño exacto"}))
    show(review_id=request["data"]["review_id"], vinculada_a=experiment["version_id"])

    step(4, HUMAN, "Decisión sobre el diseño -- en producción la firma una persona con razón y ceremonia")
    decision = ok(*api.dispatch("POST", f"/api/v1/review-requests/{request['data']['review_id']}/decisions",
                                {"artifact_hash": experiment["scientific_hash"], "decision": "APPROVE_FOR_EXPERIMENT_DESIGN",
                                 "reason": "TUTORIAL: firmado por el script, no por una revisión humana"}))
    show(decision_id=decision["data"]["decision_id"], decision=decision["data"]["decision"], actor=decision["data"].get("actor_id"))

    step(5, "Preregistros", "Crear preregistro desde las versiones exactas (allow_dirty_tree=True: el árbol está sucio)")
    preregistration_id = f"PR-TUTORIAL-{tag}"
    created = ok(*api.dispatch("POST", "/api/v1/preregistrations", {
        "preregistration_id": preregistration_id, "experiment_draft_version_id": experiment["version_id"],
        "trial_matrix_version_id": matrix["version_id"], "study_intent": "EXPLORATORY",
        "environment_requirement": {"allow_dirty_tree": True}}))
    show(preregistration_id=preregistration_id, estado=created["data"]["state"], root_v0=created["data"]["scientific_hash"][:16] + "…")

    step(6, "Preregistros", "Readiness: sin la decisión del paso 4 aquí aparecería PR-REV-001 bloqueante")
    readiness = ok(*api.dispatch("GET", f"/api/v1/preregistrations/{preregistration_id}/readiness"), expected=200)
    findings = readiness["data"]["findings"]
    show(completo=readiness["data"]["complete"], bloqueantes=[f["rule_id"] for f in findings if f["blocking"]],
         avisos=[f["rule_id"] for f in findings if not f["blocking"]])

    step(7, "Preregistros", "Preparar revisión: sella los commitments en un bundle con root hash")
    candidate = ok(*api.dispatch("POST", f"/api/v1/preregistrations/{preregistration_id}/prepare-review",
                                 {"expected_hash": created["data"]["scientific_hash"], "reason": "tutorial: sellar commitments"}))
    root = candidate["data"]["bundle_root_hash"]
    show(bundle_root_hash=root)

    step(8, "Preregistros", "Someter el root a revisión")
    submitted = ok(*api.dispatch("POST", f"/api/v1/preregistrations/{preregistration_id}/submit", {"reason": "tutorial: revisar root"}))
    show(review_id=submitted["data"]["review_id"])

    step(9, HUMAN, "Decisión sobre el preregistro, aceptando explícitamente cada aviso no bloqueante")
    accepted = [{k: f[k] for k in ("finding_hash", "rule_id", "rule_version")}
                for f in candidate["data"]["review_package"]["readiness"]["findings"] if not f["blocking"]]
    prereg_decision = ok(*api.dispatch("POST", f"/api/v1/review-requests/{submitted['data']['review_id']}/decisions",
                                       {"artifact_hash": root, "decision": "APPROVE_PREREGISTRATION",
                                        "reason": "TUTORIAL: firmado por el script", "warning_acceptances": accepted}))
    show(decision_id=prereg_decision["data"]["decision_id"], avisos_aceptados=[a["rule_id"] for a in accepted])

    step(10, HUMAN, f"Ceremonia de LOCK -- en producción se teclea 'LOCK {root[:12]}' a mano")
    locked = ok(*api.dispatch("POST", f"/api/v1/preregistrations/{preregistration_id}/lock",
                              {"expected_hash": root, "decision_id": prereg_decision["data"]["decision_id"],
                               "reason": f"LOCK {root[:12]}", "idempotency_key": f"lock-{preregistration_id}"}))
    record = api.preregistrations.get(preregistration_id)
    locked_root = record["scientific_hash"]
    show(estado=record["state"], bloqueado=record.get("locked"), root_bloqueada=locked_root)
    print("      nota: un lock NO autoriza ejecutar. Es solo el protocolo congelado.")

    step(11, "Ejecución", "Solicitud de ejecución contra la root bloqueada exacta")
    execution = ok(*api.dispatch("POST", "/api/v1/scientific-executions", {"preregistration_root_hash": locked_root}))["data"]
    show(execution_id=execution["execution_id"], estado=execution["state"], revision=execution["revision"])

    step(12, HUMAN, "Autorización explícita: modo, máximo, razón y techo de recursos -- un registro de responsabilidad")
    ceiling = {"cpu_cores": 1, "gpu_devices": [], "memory_bytes": 1024**3, "disk_bytes": 1024**3, "max_processes": 1, "wall_clock_seconds": 3600}
    auth = ok(*api.dispatch("POST", "/api/v1/execution-authorizations",
                            {"preregistration_root_hash": locked_root, "scope_type": "ONE_EXECUTION", "max_execution_count": 1,
                             "resource_ceiling": ceiling, "reason": "TUTORIAL: autorización firmada por el script"}))["data"]
    show(authorization_id=auth["authorization_id"], scope=auth.get("scope_type"), max=auth.get("max_execution_count"))

    step(13, "Ejecución", "Vincular autorización y sellar el plan (plan_hash) → READY")
    bound = ok(*api.dispatch("POST", f"/api/v1/scientific-executions/{execution['execution_id']}/bind-authorization",
                             {"authorization_id": auth["authorization_id"], "expected_revision": execution["revision"]}), expected=200)["data"]
    planned = ok(*api.dispatch("POST", f"/api/v1/scientific-executions/{execution['execution_id']}/plan",
                               {"expected_revision": bound["revision"]}), expected=200)["data"]
    show(estado=planned["state"], revision=planned["revision"], plan_hash=str(planned["plan_hash"])[:16] + "…")

    step(14, "Ejecución", "START (consume la autorización) y despacho al worker local")
    started = ok(*api.dispatch("POST", f"/api/v1/scientific-executions/{execution['execution_id']}/commands",
                               {"command": "START", "command_id": f"tutorial-start-{tag}", "expected_revision": planned["revision"]}), expected=200)["data"]
    show(estado_tras_START=started["state"], autorizacion_consumida=started.get("authorization_consumed"))
    t0 = time.monotonic()
    dispatched = ok(*api.dispatch("POST", f"/api/v1/scientific-executions/{execution['execution_id']}/dispatch",
                                  {"worker_id": f"tutorial-worker-{tag}"}), expected=200)["data"]
    show(estado_tras_dispatch=dispatched["state"], segundos=round(time.monotonic() - t0, 1))

    step(15, "Ejecución", "Esperar estado terminal (COMPLETED no significa hipótesis confirmada)")
    deadline = time.monotonic() + 300
    view = dispatched
    while view["state"] not in {"COMPLETED", "FAILED", "CANCELLED", "ABORTED", "RECOVERY_REQUIRED"} and time.monotonic() < deadline:
        time.sleep(1.0)
        view = ok(*api.dispatch("GET", f"/api/v1/scientific-executions/{execution['execution_id']}"), expected=200)["data"]
    traces = [a for a in view.get("artifacts", []) if a.get("artifact_type") == "SCIENTIFIC_TRACE"]
    show(estado_terminal=view["state"], artefactos=len(view.get("artifacts", [])), trazas_cientificas=len(traces))
    if traces:
        show(trial_intent_id=traces[0].get("trial_intent_id"), attempt_id=traces[0].get("attempt_id"))

    step(16, "Ejecución", "Verificar integridad: cadena de eventos, CAS, preregistro, plan, desviaciones")
    report = ok(*api.dispatch("GET", f"/api/v1/scientific-executions/{execution['execution_id']}/verify"), expected=200)["data"]
    show(**{k: report[k] for k in sorted(report) if k in ("status", "verdict", "outcome", "deviations", "warnings", "report_hash") or isinstance(report[k], (str, int, bool))})

    print("\nFIN DEL TUTORIAL")
    print("  Lo que existe ahora en el root de tutorial: diseño, matriz, preregistro bloqueado, autorización,")
    print("  ejecución terminal con traza sellada y un informe de verificación. NADA de esto es evidencia:")
    print("  ningún EvidenceGraph fue escrito, y las tres compuertas humanas las firmó un script.")


if __name__ == "__main__":
    main()
