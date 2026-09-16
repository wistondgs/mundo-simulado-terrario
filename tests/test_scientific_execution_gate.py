"""Regression tests for SCIENTIFIC-EXECUTION-GATE-01."""
import json
from pathlib import Path

import pytest

from terrario.lab.api import LabAPI
from terrario.lab.execution.domain import ExecutionState, InvalidExecutionTransition, assert_transition
from tests.test_preregistration_core import locked_flow


@pytest.fixture
def api(tmp_path):
    value = LabAPI(Path("."), data_root=tmp_path / ".terrario")
    locked_flow(value)
    return value


def _execution(api):
    root = api.preregistrations.get("PR-CORE-1")["scientific_hash"]
    status, response = api.dispatch("POST", "/api/v1/scientific-executions", {"preregistration_root_hash": root})
    assert status == 201
    execution = response["data"]
    ceiling = {"cpu_cores": 1, "gpu_devices": [], "memory_bytes": 1024**3,
               "disk_bytes": 1024**3, "max_processes": 1, "wall_clock_seconds": 3600}
    status, response = api.dispatch("POST", "/api/v1/execution-authorizations", {
        "preregistration_root_hash": root, "scope_type": "ONE_EXECUTION", "max_execution_count": 1,
        "resource_ceiling": ceiling, "reason": "explicit human authorization"})
    assert status == 201
    auth = response["data"]
    status, response = api.dispatch("POST", f"/api/v1/scientific-executions/{execution['execution_id']}/bind-authorization", {
        "authorization_id": auth["authorization_id"], "expected_revision": execution["revision"]})
    assert status == 200
    status, response = api.dispatch("POST", f"/api/v1/scientific-executions/{execution['execution_id']}/plan", {"expected_revision": response["data"]["revision"]})
    assert status == 200
    return response["data"], auth


def test_exact_root_authorization_plan_and_raw_artifact_firewall(api):
    execution, auth = _execution(api)
    assert execution["state"] == "READY" and execution["plan_hash"] and execution["execution_root_hash"]
    assert execution["evidence_publication"] is False
    status, started = api.dispatch("POST", f"/api/v1/scientific-executions/{execution['execution_id']}/commands", {
        "command": "START", "command_id": "start-once", "expected_revision": execution["revision"]})
    assert status == 200 and started["data"]["state"] == "RUNNING"
    # A duplicate command id has precisely one effect and no second quota use.
    status, duplicate = api.dispatch("POST", f"/api/v1/scientific-executions/{execution['execution_id']}/commands", {
        "command": "START", "command_id": "start-once", "expected_revision": execution["revision"]})
    assert status == 200 and duplicate["data"]["revision"] == started["data"]["revision"]
    api.scientific_executions.record_raw_artifact(execution["execution_id"], "SCIENTIFIC_TRACE", b'{"raw":true}\n', "worker")
    complete = api.scientific_executions.complete(execution["execution_id"], "worker")
    report = api.scientific_executions.verify(execution["execution_id"])
    assert complete["state"] == "COMPLETED"
    assert report["classification"] == "PASS"
    assert api.scientific_executions.authorization(auth["authorization_id"])["consumed_execution_count"] == 1
    bundle = api.scientific_executions.export_bundle(execution["execution_id"])
    assert api.scientific_executions.validate_bundle(bundle["archive_path"])["valid"]


def test_execution_rejects_nonexact_root_and_illegal_transition(api):
    status, result = api.dispatch("POST", "/api/v1/scientific-executions", {"preregistration_root_hash": "0" * 64})
    assert status == 422 and result["error"]["code"] == "EXECUTION_NOT_READY"
    with pytest.raises(InvalidExecutionTransition):
        assert_transition(ExecutionState.REQUESTED.value, ExecutionState.RUNNING)


def test_mutating_api_csrf_headers_are_case_insensitive(api):
    """HTTP field casing must not turn a valid local request into a 403."""
    root = api.preregistrations.get("PR-CORE-1")["scientific_hash"]
    status, response = api.dispatch(
        "POST", "/api/v1/scientific-executions", {"preregistration_root_hash": root},
        headers={"x-csrf-token": api.api_v1.csrf_token})
    assert status == 201 and response["data"]["state"] == "REQUESTED"
    status, _ = api.dispatch("POST", "/api/v1/cross-graph/snapshots", {},
                             headers={"x-csrf-token": api.cross_graph_api.csrf_token})
    assert status == 201
    status, _ = api.dispatch("POST", "/api/v1/reference-graph/snapshots", {},
                             headers={"x-csrf-token": api.reference_graph_api.csrf_token})
    assert status == 201


def test_dispatcher_materializes_one_real_trial_and_seals_its_trace(api):
    execution, _ = _execution(api)
    status, started = api.dispatch("POST", f"/api/v1/scientific-executions/{execution['execution_id']}/commands", {
        "command": "START", "command_id": "dispatch-start", "expected_revision": execution["revision"]})
    assert status == 200 and started["data"]["state"] == "RUNNING"
    api.scientific_execution_dispatcher.run(execution["execution_id"], max_trials=1)
    with api.artifacts._connect() as con:
        trial = con.execute("SELECT trial_intent_id FROM run_attempts WHERE projected_state='COMPLETED' LIMIT 1").fetchone()[0]
    frames = api.scientific_execution_dispatcher.frames_after(execution["execution_id"], trial)
    assert len(frames) > 1 and frames[0]["tick"] == 0
    assert all(frame["identity"]["execution_id"] == execution["execution_id"] for frame in frames)
    artifacts = api.scientific_executions.get(execution["execution_id"])["artifacts"]
    assert {item["artifact_type"] for item in artifacts} >= {"SCIENTIFIC_TRACE", "TRIAL_RESULT"}
    trace_ref = next(item for item in artifacts if item["artifact_type"] == "SCIENTIFIC_TRACE")
    trace = json.loads(api.artifacts.blobs.read(trace_ref["blob_hash"]))
    transitions = [frame for frame in trace["frames"] if frame["tick"] > 0]
    assert transitions
    # The runtime seals the narrow observer projections on every transition;
    # whether a plan exists is a condition-level fact, never inferred here.
    assert all(isinstance(frame["observer_view"]["decision_trace"], list) for frame in transitions)
    assert all(isinstance(frame["observer_view"]["planner_proposal_trace"], list) for frame in transitions)


def test_terminal_scientific_playback_survives_dispatcher_memory_loss(api):
    execution, _ = _execution(api)
    api.dispatch("POST", f"/api/v1/scientific-executions/{execution['execution_id']}/commands", {"command": "START", "command_id": "playback-start", "expected_revision": execution["revision"]})
    api.scientific_execution_dispatcher.run(execution["execution_id"], max_trials=1)
    attempt = api.scientific_observations.attempts(execution["execution_id"])[0]
    api.scientific_execution_dispatcher.frames.clear()
    page = api.scientific_observations.playback(execution["execution_id"], attempt["trial_intent_id"], attempt["attempt_id"])
    assert page["mode"] == "PLAYBACK" and page["frames"][0]["tick"] == 0
    assert page["frames"][0]["identity"]["plan_hash"] == execution["plan_hash"]


def test_execution_package_has_no_evidence_or_sandbox_imports():
    root = Path("terrario/lab/execution")
    source = "\n".join(path.read_text() for path in root.glob("*.py"))
    for forbidden in ("theory.store", "EvidenceRecord", "add_evidence(", "sandbox_runtime", "run_experiment_specs"):
        assert forbidden not in source
