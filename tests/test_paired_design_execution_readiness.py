"""A locked CL-7 paired preregistration must be executable.

Its matrix cells carry the intervention in `agent_config` and run on the base
scenario; `TreatmentArm.variant` ("preserved" / "ablated") is descriptive
metadata by the domain's own docstring, never a world variant awaiting binding.
The execution readiness rule must not read it as one.

Reproduces the gap found on 2026-09-16: after design approval, preregistration,
human review and lock, `_readiness` answered UNRESOLVED_VARIANT_BINDING and the
authorization could not be bound. No agent is executed here.
"""
from __future__ import annotations

from dataclasses import replace
from pathlib import Path

from terrario.lab.api import LabAPI
from terrario.lab.experiment_composer import build_trial_matrix, state_for, validate_draft
from terrario.lab.models import thaw
from terrario.lab.persistence.canonical import content_hash
from tests.test_cl7_paired_preregistration import _draft


def _ok(status, payload, expected=201):
    assert status == expected, (status, payload)
    return payload


def _locked_paired_preregistration(api: LabAPI) -> str:
    draft = _draft()
    scenario = api.world_registry.get(draft.scenario_id).scenario
    findings = validate_draft(draft, scenario, api.metrics, api.observers)
    draft = replace(draft, state=state_for(findings))
    stored = api.artifacts.create_artifact("ExperimentDraft", thaw(draft), draft.schema_version, scientific_payload=draft.scientific_payload(),
                                           artifact_id=draft.draft_id, classification="SCIENTIFIC_DESIGN_DRAFT", reason="test", initial_state=draft.state.value)
    matrix = build_trial_matrix(draft)
    payload = thaw(matrix); scientific = {k: v for k, v in payload.items() if k not in {"warnings", "execution_performed"}}
    stored_matrix = api.artifacts.create_artifact("TrialMatrix", payload, "terrario.lab.trial-matrix/v1", scientific_payload=scientific,
                                                  artifact_id=f"TM-{content_hash(scientific)[:20]}", classification="NON_EXECUTING_TRIAL_MATRIX",
                                                  reason="test", initial_state="MATERIALIZED", deduplicate=True)
    assert {c["arm_id"] for c in payload["cells"]} == {"PLANNER_PRESERVED", "PLANNER_ABLATED"}
    request = _ok(*api.dispatch("POST", "/api/v1/review-requests", {"artifact_version_id": stored.version_id, "reason": "test"}))
    _ok(*api.dispatch("POST", f"/api/v1/review-requests/{request['data']['review_id']}/decisions",
                      {"artifact_hash": stored.scientific_hash, "decision": "APPROVE_FOR_EXPERIMENT_DESIGN", "reason": "test"}))
    pid = "PR-PAIRED-READINESS"
    created = _ok(*api.dispatch("POST", "/api/v1/preregistrations", {"preregistration_id": pid, "experiment_draft_version_id": stored.version_id,
                  "trial_matrix_version_id": stored_matrix.version_id, "study_intent": "EXPLORATORY", "environment_requirement": {"allow_dirty_tree": True}}))
    readiness = _ok(*api.dispatch("GET", f"/api/v1/preregistrations/{pid}/readiness"), expected=200)["data"]
    assert readiness["complete"], readiness["findings"]
    candidate = _ok(*api.dispatch("POST", f"/api/v1/preregistrations/{pid}/prepare-review", {"expected_hash": created["data"]["scientific_hash"], "reason": "test"}))
    root = candidate["data"]["bundle_root_hash"]
    submitted = _ok(*api.dispatch("POST", f"/api/v1/preregistrations/{pid}/submit", {"reason": "test"}))
    accepted = [{k: f[k] for k in ("finding_hash", "rule_id", "rule_version")} for f in candidate["data"]["review_package"]["readiness"]["findings"] if not f["blocking"]]
    decision = _ok(*api.dispatch("POST", f"/api/v1/review-requests/{submitted['data']['review_id']}/decisions",
                                 {"artifact_hash": root, "decision": "APPROVE_PREREGISTRATION", "reason": "test", "warning_acceptances": accepted}))
    _ok(*api.dispatch("POST", f"/api/v1/preregistrations/{pid}/lock", {"expected_hash": root, "decision_id": decision["data"]["decision_id"],
                      "reason": f"LOCK {root[:12]}", "idempotency_key": f"lock-{pid}"}))
    return api.preregistrations.get(pid)["scientific_hash"]


def test_locked_paired_preregistration_is_execution_ready(tmp_path):
    api = LabAPI(Path("."), data_root=tmp_path / ".terrario")
    root = _locked_paired_preregistration(api)
    report = api.scientific_executions._readiness(root)
    assert report["ready"], report["blockers"]


def test_bind_authorization_accepts_a_locked_paired_root(tmp_path):
    api = LabAPI(Path("."), data_root=tmp_path / ".terrario")
    root = _locked_paired_preregistration(api)
    execution = _ok(*api.dispatch("POST", "/api/v1/scientific-executions", {"preregistration_root_hash": root}))["data"]
    ceiling = {"cpu_cores": 1, "gpu_devices": [], "memory_bytes": 1024**3, "disk_bytes": 1024**3, "max_processes": 1, "wall_clock_seconds": 3600}
    auth = _ok(*api.dispatch("POST", "/api/v1/execution-authorizations", {"preregistration_root_hash": root, "scope_type": "ONE_EXECUTION",
               "max_execution_count": 1, "resource_ceiling": ceiling, "reason": "test"}))["data"]
    status, bound = api.dispatch("POST", f"/api/v1/scientific-executions/{execution['execution_id']}/bind-authorization",
                                 {"authorization_id": auth["authorization_id"], "expected_revision": execution["revision"]})
    assert status == 200, bound
