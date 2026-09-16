"""CL-7 ledger tests.

The positive fixture is an isolated contract fixture, not a scientific claim:
it explicitly replaces the registry entry with a construct-validated test
metric before preregistration.  Production's D2 energy proxy remains rejected.
"""
from dataclasses import replace
import json
from pathlib import Path

import pytest

from terrario.lab.api import LabAPI
from terrario.lab.evidence_publication import EmpiricalResultPublicationService, ResultIneligible, RESULT_SCHEMA
from terrario.lab.hypothesis_reconciliation import HypothesisReconciler, HypothesisReconciliationError
from terrario.lab.metrics_observer import ConstructValidationStatus
from terrario.lab.persistence.canonical import canonical_json
from tests.test_preregistration_core import locked_flow
from tests.test_scientific_execution_gate import _execution


def _test_api(tmp_path):
    api = LabAPI(Path("."), data_root=tmp_path / ".terrario")
    metric = api.metrics.get("D2-energy-trajectory")
    api.metrics._metrics[metric.metric_id] = replace(metric, construct_validation_status=ConstructValidationStatus.VALIDATED_FOR_CONSTRUCT)
    locked_flow(api)
    execution, _ = _execution(api)
    status, started = api.dispatch("POST", f"/api/v1/scientific-executions/{execution['execution_id']}/commands", {
        "command": "START", "command_id": "cl7-start", "expected_revision": execution["revision"]})
    assert status == 200 and started["data"]["state"] == "RUNNING"
    api.scientific_execution_dispatcher.run(execution["execution_id"], max_trials=1)
    attempt = api.scientific_observations.attempts(execution["execution_id"])[0]
    with api.artifacts._connect() as con:
        trace = con.execute("""SELECT * FROM scientific_execution_artifacts WHERE execution_id=? AND attempt_id=?
            AND artifact_type='SCIENTIFIC_TRACE'""", (execution["execution_id"], attempt["attempt_id"])).fetchone()
    draft = api.preregistrations.get("PR-CORE-1")["payload"]["draft"]
    metric = draft["metrics"][0]
    endpoint = draft["endpoints"][0]
    return api, execution, attempt, trace, draft, metric, endpoint


def _seal_metric(api, execution, attempt, trace, draft, metric, endpoint, **changes):
    value = {
        "schema_version": RESULT_SCHEMA,
        "execution_id": execution["execution_id"], "trial_intent_id": attempt["trial_intent_id"], "attempt_id": attempt["attempt_id"],
        "execution_plan_hash": execution["plan_hash"], "preregistration_root_hash": execution["preregistration_root_hash"],
        "hypothesis_id": draft["scientific_question"]["hypothesis_id"], "hypothesis_revision": draft["scientific_question"]["hypothesis_hash"],
        "metric_id": metric["metric_id"], "metric_version": metric["definition_version"],
        "value": 0.5, "numerator": 1, "denominator": 2, "excluded_count": 0, "missing_count": 0,
        "epistemic_classification": "EVIDENCE_FOR", "analysis_rule": endpoint["decision_rule"],
        "trace_blob_hash": trace["blob_hash"], "scope": "AUTHORIZED_SCIENTIFIC_RESULT",
    }
    value.update(changes)
    sealed = api.scientific_executions.record_raw_artifact(execution["execution_id"], "METRIC_RESULT",
        canonical_json(value).encode(), "test-metric-worker", attempt["trial_intent_id"], attempt["attempt_id"])
    with api.artifacts._connect() as con:
        row = con.execute("SELECT descriptor_hash FROM scientific_execution_artifacts WHERE execution_id=? AND attempt_id=? AND artifact_type='METRIC_RESULT' AND blob_hash=?", (execution["execution_id"], attempt["attempt_id"], sealed["blob_hash"])).fetchone()
    return {**sealed, "descriptor_hash": row["descriptor_hash"]}


def _completed_service(tmp_path):
    api, execution, attempt, trace, draft, metric, endpoint = _test_api(tmp_path)
    descriptor = _seal_metric(api, execution, attempt, trace, draft, metric, endpoint)
    api.scientific_executions.complete(execution["execution_id"], "test-metric-worker")
    assert api.scientific_executions.verify(execution["execution_id"])["classification"] == "PASS"
    return api, execution, attempt, descriptor


def test_authorized_result_is_durable_idempotent_and_roundtrips(tmp_path):
    api, execution, attempt, descriptor = _completed_service(tmp_path)
    service = EmpiricalResultPublicationService(api.artifacts, api.preregistrations)
    report = service.eligibility(execution["execution_id"], attempt["attempt_id"], descriptor["descriptor_hash"])
    assert report.eligible and report.envelope["denominator"] == 2
    first = service.ingest(execution["execution_id"], attempt["attempt_id"], descriptor["descriptor_hash"])
    second = service.ingest(execution["execution_id"], attempt["attempt_id"], descriptor["descriptor_hash"])
    assert not first["deduplicated"] and second["deduplicated"]
    reopened = EmpiricalResultPublicationService(LabAPI(Path("."), data_root=api.artifacts.data_root).artifacts, api.preregistrations)
    restored = reopened.get_result(first["result_id"])
    assert restored["result_hash"] == first["result_hash"]
    assert reopened.verify_integrity(first["result_id"])["valid"]
    aggregate = reopened.evidence_for_hypothesis(restored["envelope"]["hypothesis_id"], restored["envelope"]["hypothesis_revision"])
    assert aggregate["relations"] == ("EVIDENCE_FOR",) and not aggregate["automatic_truth_promotion"]
    forward = reopened.provenance_for_result(first["result_id"])["forward"]
    assert {edge["target_kind"] for edge in forward} >= {"ScientificResult", "TrialAttempt", "ScientificExecution", "Preregistration", "OperationalHypothesis", "Metric"}


@pytest.mark.parametrize(("changes", "expected"), [
    ({"scope": "INSTRUMENT_SELF_AUDIT_NOT_AGENT_EVIDENCE"}, "REJECT_NOT_SCIENTIFIC_RESULT"),
    ({"metric_id": "wrong-metric"}, "METRIC_NOT_PREREGISTERED_ENDPOINT"),
    ({"denominator": 0}, "METRIC_DENOMINATOR_INVALID"),
    ({"execution_id": "execution-from-another-lineage"}, "CROSS_LINEAGE_EXECUTION_ID"),
    ({"trace_blob_hash": "0" * 64}, "TRACE_IDENTITY_MISMATCH"),
])
def test_ineligible_or_cross_lineage_metric_results_fail_closed(tmp_path, changes, expected):
    api, execution, attempt, trace, draft, metric, endpoint = _test_api(tmp_path)
    descriptor = _seal_metric(api, execution, attempt, trace, draft, metric, endpoint, **changes)
    api.scientific_executions.complete(execution["execution_id"], "test-metric-worker")
    api.scientific_executions.verify(execution["execution_id"])
    report = EmpiricalResultPublicationService(api.artifacts, api.preregistrations).eligibility(execution["execution_id"], attempt["attempt_id"], descriptor["descriptor_hash"])
    assert not report.eligible and expected in report.blockers


def test_real_registry_energy_proxy_remains_ineligible(tmp_path):
    api = LabAPI(Path("."), data_root=tmp_path / ".terrario")
    locked_flow(api)
    execution, _ = _execution(api)
    status, started = api.dispatch("POST", f"/api/v1/scientific-executions/{execution['execution_id']}/commands", {
        "command": "START", "command_id": "energy-proxy-start", "expected_revision": execution["revision"]})
    assert status == 200
    api.scientific_execution_dispatcher.run(execution["execution_id"], max_trials=1)
    attempt = api.scientific_observations.attempts(execution["execution_id"])[0]
    with api.artifacts._connect() as con:
        trace = con.execute("SELECT * FROM scientific_execution_artifacts WHERE execution_id=? AND attempt_id=? AND artifact_type='SCIENTIFIC_TRACE'", (execution["execution_id"], attempt["attempt_id"])).fetchone()
    draft = api.preregistrations.get("PR-CORE-1")["payload"]["draft"]
    descriptor = _seal_metric(api, execution, attempt, trace, draft, draft["metrics"][0], draft["endpoints"][0])
    api.scientific_executions.complete(execution["execution_id"], "worker"); api.scientific_executions.verify(execution["execution_id"])
    report = EmpiricalResultPublicationService(api.artifacts, api.preregistrations).eligibility(execution["execution_id"], attempt["attempt_id"], descriptor["descriptor_hash"])
    assert "METRIC_NOT_VALIDATED_FOR_CONSTRUCT" in report.blockers


def test_critical_deviation_preserves_result_but_qualifies_epistemic_effect(tmp_path):
    api, execution, attempt, trace, draft, metric, endpoint = _test_api(tmp_path)
    descriptor = _seal_metric(api, execution, attempt, trace, draft, metric, endpoint)
    api.scientific_executions.deviation(execution["execution_id"], "ENVIRONMENT_DEVIATION", {"critical": True}, "reviewer")
    api.scientific_executions.complete(execution["execution_id"], "worker")
    # A critical deviation preserves the observation but blocks an unqualified
    # epistemic contribution; it is not silently discarded.
    assert api.scientific_executions.verify(execution["execution_id"])["classification"] == "DEVIATED"
    service = EmpiricalResultPublicationService(api.artifacts, api.preregistrations)
    report = service.eligibility(execution["execution_id"], attempt["attempt_id"], descriptor["descriptor_hash"])
    assert report.eligible and report.envelope["epistemic_classification"] == "UNRESOLVED"
    assert service.ingest(execution["execution_id"], attempt["attempt_id"], descriptor["descriptor_hash"])["qualification"] == "CRITICAL_DEVIATION_NO_UNQUALIFIED_UPDATE"


def test_crash_between_result_and_evidence_rolls_back_atomically(tmp_path):
    api, execution, attempt, descriptor = _completed_service(tmp_path)
    class CrashingPublisher(EmpiricalResultPublicationService):
        def _after_result_insert(self, _connection, _envelope):
            raise RuntimeError("simulated interruption")
    service = CrashingPublisher(api.artifacts, api.preregistrations)
    with pytest.raises(RuntimeError, match="simulated interruption"):
        service.ingest(execution["execution_id"], attempt["attempt_id"], descriptor["descriptor_hash"])
    with api.artifacts._connect() as con:
        assert con.execute("SELECT COUNT(*) FROM scientific_results").fetchone()[0] == 0
        assert con.execute("SELECT COUNT(*) FROM empirical_evidence").fetchone()[0] == 0


def test_pre_normalization_hypothesis_is_superseded_without_deletion(tmp_path):
    api = LabAPI(Path("."), data_root=tmp_path / ".terrario")
    common = {"derivation_rule": "ROLE_REFINEMENT_ABLATION_PREDICTION@v1", "prediction": "declared prediction",
              "epistemic_status": "REVIEW_REQUIRED", "premises": [{"claim_id": "C1", "participant": "actor", "role": "proposer"}]}
    old = api.artifacts.create_artifact("OperationalHypothesisDraft", {**common, "legacy_locator": "/absolute/old"}, "test/v1",
        artifact_id="H-OLD", initial_state="REVIEW_REQUIRED", sealed=True)
    canonical = api.artifacts.create_artifact("OperationalHypothesisDraft", {**common, "locator": "corpus-relative"}, "test/v1",
        artifact_id="H-CANONICAL", initial_state="REVIEW_REQUIRED", sealed=True)
    result = HypothesisReconciler(api.artifacts).reconcile(old.artifact_id, canonical.artifact_id, "migration", "canonical identifiers replace path-dependent predecessor")
    assert not result["deduplicated"] and api.artifacts.current_state(old.version_id) == "SUPERSEDED"
    assert HypothesisReconciler(api.artifacts).reconcile(old.artifact_id, canonical.artifact_id, "migration", "same")["deduplicated"]
    with api.artifacts._connect() as con:
        assert con.execute("SELECT COUNT(*) FROM artifact_links WHERE relation='SUPERSEDED_BY'").fetchone()[0] == 1


def test_empirical_result_api_is_readable_but_never_an_execution_or_metric_surface(tmp_path):
    api = LabAPI(Path("."), data_root=tmp_path / ".terrario")
    status, response = api.dispatch("GET", "/api/v1/empirical-results/status")
    assert status == 200 and response["data"]["scientific_results"] == 0
    assert response["meta"]["automatic_execution"] is False
    status, response = api.dispatch("POST", "/api/v1/empirical-results", {"execution_id": "x"})
    assert status == 400 and response["error"]["code"] == "INVALID_REQUEST"
