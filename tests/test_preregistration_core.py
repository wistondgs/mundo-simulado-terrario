from pathlib import Path

import pytest

from terrario.lab.api import LabAPI
from terrario.lab.persistence.canonical import content_hash
from tests.test_lab_02c_api import experiment_payload


@pytest.fixture
def api(tmp_path):
    return LabAPI(Path("."), data_root=tmp_path / ".terrario")


def sources(api):
    status, experiment = api.dispatch("POST", "/api/experiment-drafts", experiment_payload())
    assert status == 201
    status, matrix = api.dispatch("POST", "/api/trial-matrices/build", experiment_payload())
    assert status == 200
    return experiment, matrix


def create_request(experiment, matrix, **changes):
    value = {
        "preregistration_id": "PR-CORE-1",
        "experiment_draft_version_id": experiment["version_id"],
        "trial_matrix_version_id": matrix["version_id"],
        "study_intent": "EXPLORATORY",
        "environment_requirement": {"allow_dirty_tree": True},
    }
    value.update(changes)
    return value


def approve_upstream(api, experiment):
    status, request = api.dispatch("POST", "/api/v1/review-requests", {
        "artifact_version_id": experiment["version_id"], "reason": "review exact design"})
    assert status == 201
    status, decision = api.dispatch("POST", f"/api/v1/review-requests/{request['data']['review_id']}/decisions", {
        "artifact_hash": experiment["scientific_hash"],
        "decision": "APPROVE_FOR_EXPERIMENT_DESIGN", "reason": "human approval"})
    assert status == 201
    return decision["data"]


def locked_flow(api):
    experiment, matrix = sources(api)
    status, created = api.dispatch("POST", "/api/v1/preregistrations", create_request(experiment, matrix))
    assert status == 201
    approve_upstream(api, experiment)
    root0 = created["data"]["scientific_hash"]
    status, candidate = api.dispatch("POST", "/api/v1/preregistrations/PR-CORE-1/prepare-review", {
        "expected_hash": root0, "reason": "seal exact commitments"})
    assert status == 201
    root = candidate["data"]["bundle_root_hash"]
    status, submitted = api.dispatch("POST", "/api/v1/preregistrations/PR-CORE-1/submit", {"reason": "review root"})
    assert status == 201
    findings = candidate["data"]["review_package"]["readiness"]["findings"]
    accepted = [{k: item[k] for k in ("finding_hash", "rule_id", "rule_version")}
                for item in findings if not item["blocking"]]
    status, decision = api.dispatch("POST", f"/api/v1/review-requests/{submitted['data']['review_id']}/decisions", {
        "artifact_hash": root, "decision": "APPROVE_PREREGISTRATION",
        "reason": "human scientific review", "warning_acceptances": accepted})
    assert status == 201
    lock_payload = {"expected_hash": root, "decision_id": decision["data"]["decision_id"],
                    "reason": f"LOCK {root[:12]}", "idempotency_key": "lock-core-1"}
    status, locked = api.dispatch("POST", "/api/v1/preregistrations/PR-CORE-1/lock", lock_payload)
    assert status == 201
    return experiment, matrix, candidate["data"], decision["data"], lock_payload, locked["data"]


def test_migration_two_is_applied_and_append_only(api):
    applied = [(x["version"], x["name"]) for x in api.artifacts.migration_status()]
    assert (2, "scientific_preregistration_core") in applied
    with api.artifacts._connect() as connection:
        names = {x[0] for x in connection.execute("select name from sqlite_master where type='table'")}
    assert {"preregistration_locks", "exposure_records", "preregistration_audit_chain"} <= names


def test_unapproved_upstream_is_a_blocker(api):
    experiment, matrix = sources(api)
    status, created = api.dispatch("POST", "/api/v1/preregistrations", create_request(experiment, matrix))
    assert status == 201
    status, readiness = api.dispatch("GET", "/api/v1/preregistrations/PR-CORE-1/readiness")
    assert status == 200 and not readiness["data"]["complete"]
    assert "PR-REV-001" in {x["rule_id"] for x in readiness["data"]["findings"]}


def test_client_cannot_spoof_authority(api):
    experiment, matrix = sources(api)
    status, error = api.dispatch("POST", "/api/v1/preregistrations", create_request(experiment, matrix, state="PREREGISTERED_LOCKED"))
    assert status == 400 and "state" in error["error"]["message"]


def test_complete_human_review_lock_and_verification(api):
    _, _, candidate, _, _, attestation = locked_flow(api)
    assert attestation["bundle_root_hash"] == candidate["bundle_root_hash"]
    assert attestation["signature_status"] == "UNSIGNED_LOCAL_ATTESTATION"
    status, verified = api.dispatch("GET", "/api/v1/preregistrations/PR-CORE-1/verify")
    assert status == 200 and verified["data"]["valid"] and verified["data"]["locked"]
    assert verified["data"]["scientific_execution"] is False


def test_lock_is_idempotent_but_conflicting_key_is_rejected(api):
    _, _, _, _, payload, first = locked_flow(api)
    status, repeated = api.dispatch("POST", "/api/v1/preregistrations/PR-CORE-1/lock", payload)
    assert status == 201 and repeated["data"]["attestation_id"] == first["attestation_id"]
    changed = {**payload, "reason": "different", "idempotency_key": "lock-core-1"}
    assert api.dispatch("POST", "/api/v1/preregistrations/PR-CORE-1/lock", changed)[0] == 409


def test_locked_preregistration_cannot_be_derived(api):
    _, _, candidate, _, _, _ = locked_flow(api)
    status, error = api.dispatch("POST", "/api/v1/preregistrations/PR-CORE-1/derive", {
        "expected_hash": candidate["bundle_root_hash"], "changes": {"study_intent": "STRESS_TEST"}, "reason": "forbidden edit"})
    assert status == 423 and error["error"]["code"] == "LOCKED_ARTIFACT"


def test_postlock_deviation_is_separate_and_root_stays_fixed(api):
    _, _, candidate, _, _, _ = locked_flow(api)
    status, record = api.dispatch("POST", "/api/v1/preregistrations/PR-CORE-1/deviations", {
        "reason": "observed environment differs", "deviation_type": "ENVIRONMENT_DEVIATION",
        "affected_component": "environment_requirement", "planned_behavior": "CPU",
        "actual_behavior": "CPU constrained", "scientific_impact_assessment": "review required",
        "disposition": "QUARANTINE_PENDING_REVIEW"})
    assert status == 201 and record["data"]["classification"] == "POST_LOCK_GOVERNANCE_RECORD"
    assert api.dispatch("GET", "/api/v1/preregistrations/PR-CORE-1")[1]["data"]["scientific_hash"] == candidate["bundle_root_hash"]


def test_exposure_is_written_before_legacy_preview(api):
    status, _ = api.dispatch("GET", "/api/worlds/D2/preview?seed=731")
    assert status == 200
    status, rows = api.dispatch("GET", "/api/v1/exposure-records?scenario_id=D2&world_seed=731")
    assert status == 200 and rows["data"]["items"][0]["exposure_kind"] == "PREVIEWED"


def test_csrf_and_local_origin_are_enforced_by_http_contract(api):
    experiment, matrix = sources(api)
    request = create_request(experiment, matrix)
    assert api.dispatch("POST", "/api/v1/preregistrations", request, {"Host": "localhost:8765"})[0] == 403
    session = api.dispatch("GET", "/api/v1/session")[1]["data"]
    headers = {"Host": "localhost:8765", "Origin": "http://localhost:8765", "X-CSRF-Token": session["csrf_token"]}
    assert api.dispatch("POST", "/api/v1/preregistrations", request, headers)[0] == 201
    bad = {**headers, "Origin": "https://attacker.invalid"}
    assert api.dispatch("POST", "/api/v1/exposure-records", {}, bad)[0] == 403


def test_no_execution_or_evidence_endpoint_exists(api):
    assert api.dispatch("POST", "/api/v1/preregistrations/x/execute", {})[0] == 404
    assert api.dispatch("POST", "/api/v1/evidence-candidates", {})[0] == 404


def test_portable_bundle_roundtrip_and_tamper_detection(api, tmp_path):
    locked_flow(api)
    status, exported = api.dispatch("GET", "/api/v1/preregistrations/PR-CORE-1/export")
    assert status == 200
    bundle = exported["data"]
    status, report = api.dispatch("POST", "/api/v1/bundles/validate", bundle)
    assert status == 200 and report["data"]["valid"]
    digest = next(iter(bundle["component_payloads"]))
    bundle["component_payloads"][digest]["tampered"] = True
    status, report = api.dispatch("POST", "/api/v1/bundles/validate", bundle)
    assert status == 200 and not report["data"]["valid"]
    assert any("TAMPERED" in x or "PORTABLE_HASH" in x for x in report["data"]["failures"])


def test_sql_layer_rejects_lock_update_and_delete(api):
    locked_flow(api)
    import sqlite3
    with pytest.raises(sqlite3.IntegrityError), api.artifacts.transaction() as connection:
        connection.execute("UPDATE preregistration_locks SET reason='rewrite' WHERE preregistration_id='PR-CORE-1'")
    with pytest.raises(sqlite3.IntegrityError), api.artifacts.transaction() as connection:
        connection.execute("DELETE FROM preregistration_locks WHERE preregistration_id='PR-CORE-1'")


def test_openapi_exposes_governance_but_no_execution(api):
    status, document = api.dispatch("GET", "/api/v1/openapi.json")
    assert status == 200 and document["data"]["openapi"] == "3.1.0"
    paths = document["data"]["paths"]
    assert "/api/v1/preregistrations/{id}/lock" in paths
    assert not any("execute" in path or "evidence" in path for path in paths)
