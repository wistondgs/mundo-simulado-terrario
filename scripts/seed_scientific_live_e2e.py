"""Seed a real scientific execution for E2E live-observability tests.

Runs the genuine preregistration -> authorization -> plan chain against the
repository data_root shared with the Playwright webServer, using a unique
preregistration id per run so repeated E2E executions never collide, then
prints the execution identity as JSON for the browser test. The trial is left
READY (plan sealed, not started) so the browser test starts and dispatches it
in the server process and observes live frames there.
"""
from __future__ import annotations

import json
import secrets
import sys
from pathlib import Path

from terrario.lab.api import LabAPI
from tests.test_lab_02c_api import experiment_payload


def _locked_preregistration(api, preregistration_id: str) -> str:
    suffix = preregistration_id.removeprefix("PR-LIVE-")
    # Vary the seeds so the draft's scientific hash is unique per E2E run; the
    # content-addressed store rejects silent duplicate scientific payloads.
    offset = int(suffix[:6], 16) % 100000
    payload = experiment_payload(draft_id=f"ED-LIVE-{suffix}", world_seeds=[100000 + offset, 200000 + offset],
                                 agent_seeds=[300000 + offset])
    status, experiment = api.dispatch("POST", "/api/experiment-drafts", payload)
    assert status == 201, experiment
    status, matrix = api.dispatch("POST", "/api/trial-matrices/build", payload)
    assert status == 200, matrix
    status, created = api.dispatch("POST", "/api/v1/preregistrations", {
        "preregistration_id": preregistration_id,
        "experiment_draft_version_id": experiment["version_id"],
        "trial_matrix_version_id": matrix["version_id"],
        "study_intent": "EXPLORATORY",
        "environment_requirement": {"allow_dirty_tree": True}})
    assert status == 201, created
    status, request = api.dispatch("POST", "/api/v1/review-requests", {
        "artifact_version_id": experiment["version_id"], "reason": "review exact design"})
    assert status == 201, request
    status, decision = api.dispatch("POST", f"/api/v1/review-requests/{request['data']['review_id']}/decisions", {
        "artifact_hash": experiment["scientific_hash"],
        "decision": "APPROVE_FOR_EXPERIMENT_DESIGN", "reason": "human approval"})
    assert status == 201, decision
    root0 = created["data"]["scientific_hash"]
    status, candidate = api.dispatch("POST", f"/api/v1/preregistrations/{preregistration_id}/prepare-review", {
        "expected_hash": root0, "reason": "seal exact commitments"})
    assert status == 201, candidate
    root = candidate["data"]["bundle_root_hash"]
    status, submitted = api.dispatch("POST", f"/api/v1/preregistrations/{preregistration_id}/submit", {"reason": "review root"})
    assert status == 201, submitted
    findings = candidate["data"]["review_package"]["readiness"]["findings"]
    accepted = [{k: item[k] for k in ("finding_hash", "rule_id", "rule_version")}
                for item in findings if not item["blocking"]]
    status, decision = api.dispatch("POST", f"/api/v1/review-requests/{submitted['data']['review_id']}/decisions", {
        "artifact_hash": root, "decision": "APPROVE_PREREGISTRATION",
        "reason": "human scientific review", "warning_acceptances": accepted})
    assert status == 201, decision
    status, locked = api.dispatch("POST", f"/api/v1/preregistrations/{preregistration_id}/lock", {
        "expected_hash": root, "decision_id": decision["data"]["decision_id"],
        "reason": f"LOCK {root[:12]}", "idempotency_key": f"lock-{preregistration_id}"})
    assert status == 201, locked
    return api.preregistrations.get(preregistration_id)["scientific_hash"]


def main() -> None:
    data_root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".terrario")
    api = LabAPI(Path("."), data_root=data_root)
    preregistration_id = f"PR-LIVE-{secrets.token_hex(6)}"
    root = _locked_preregistration(api, preregistration_id)
    status, response = api.dispatch("POST", "/api/v1/scientific-executions", {"preregistration_root_hash": root})
    assert status == 201, response
    execution = response["data"]
    ceiling = {"cpu_cores": 1, "gpu_devices": [], "memory_bytes": 1024**3,
               "disk_bytes": 1024**3, "max_processes": 1, "wall_clock_seconds": 3600}
    status, response = api.dispatch("POST", "/api/v1/execution-authorizations", {
        "preregistration_root_hash": root, "scope_type": "ONE_EXECUTION", "max_execution_count": 1,
        "resource_ceiling": ceiling, "reason": "e2e live observability"})
    assert status == 201, response
    auth = response["data"]
    status, response = api.dispatch("POST", f"/api/v1/scientific-executions/{execution['execution_id']}/bind-authorization",
                                    {"authorization_id": auth["authorization_id"], "expected_revision": execution["revision"]})
    assert status == 200, response
    status, response = api.dispatch("POST", f"/api/v1/scientific-executions/{execution['execution_id']}/plan",
                                    {"expected_revision": response["data"]["revision"]})
    assert status == 200, response
    execution = response["data"]
    print(json.dumps({"execution_id": execution["execution_id"], "plan_hash": execution["plan_hash"],
                      "revision": execution["revision"]}))


if __name__ == "__main__":
    main()
