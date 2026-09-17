"""Sealing a measurement is the step that was missing between trace and evidence.

The ledger holds sealed traces and no sealed measurements, so the chain stops
one step before evidence.  These tests pin that the step closes the chain, and
that it refuses rather than inventing anything the preregistration did not say.
"""
import pytest

from terrario.lab.evidence_publication import EmpiricalResultPublicationService
from terrario.lab.metric_result_sealing import MetricResultSealingError, seal_metric_result
from tests.test_empirical_result_publication import _test_api


def _evaluator(value=0.5, numerator=1, denominator=2):
    """Stands in for a construct-validated instrument; reads the trace it is given."""
    def run(trace):
        assert isinstance(trace, dict)          # it really receives the sealed trace
        return {"value": value, "numerator": numerator, "denominator": denominator}
    return run


def _seal(api, execution, attempt, metric, **kw):
    return seal_metric_result(
        api, execution_id=execution["execution_id"], attempt_id=attempt["attempt_id"],
        metric_id=kw.pop("metric_id", metric["metric_id"]), evaluator=kw.pop("evaluator", _evaluator()),
        classification=kw.pop("classification", "EVIDENCE_FOR"), actor_id="metric-worker", **kw)


def test_sealing_closes_the_chain_from_a_sealed_trace_to_a_published_result(tmp_path):
    api, execution, attempt, trace, draft, metric, endpoint = _test_api(tmp_path)
    service = EmpiricalResultPublicationService(api.artifacts, api.preregistrations)

    # Before: the measurement is among the things standing between this run and
    # the ledger, and it is the one no existing code path could supply.
    assert "METRIC_RESULT_ARTIFACT_NOT_SEALED" in service.eligibility(
        execution["execution_id"], attempt["attempt_id"], "no-such-descriptor").blockers

    sealed = _seal(api, execution, attempt, metric)
    api.scientific_executions.complete(execution["execution_id"], "metric-worker")
    assert api.scientific_executions.verify(execution["execution_id"])["classification"] == "PASS"

    report = service.eligibility(execution["execution_id"], attempt["attempt_id"], sealed["descriptor_hash"])
    assert report.blockers == () and report.eligible is True

    assert service.status()["scientific_results"] == 0
    service.ingest(execution["execution_id"], attempt["attempt_id"], sealed["descriptor_hash"])
    status = service.status()
    assert status["scientific_results"] == 1 and status["empirical_evidence"] == 1
    # The counter the moratorium in PROCESO_DE_TRABAJO_01 §4 waits on.


def test_the_trace_the_evaluator_reads_is_the_one_named_in_the_result(tmp_path):
    api, execution, attempt, trace, draft, metric, endpoint = _test_api(tmp_path)
    sealed = _seal(api, execution, attempt, metric)
    # Identity, not a filesystem path: evidence_publication rejects a result
    # whose trace_blob_hash does not name the sealed trace of that attempt.
    assert sealed["measured"]["trace_blob_hash"] == trace["blob_hash"]


def test_every_scientific_field_is_copied_from_the_preregistration(tmp_path):
    api, execution, attempt, trace, draft, metric, endpoint = _test_api(tmp_path)
    sealed = _seal(api, execution, attempt, metric)
    measured = sealed["measured"]
    # None of these is an argument of the function. If any were, the tool could
    # preregister after the fact by supplying its own answer.
    assert measured["metric_version"] == metric["definition_version"]
    assert measured["analysis_rule"] == endpoint["decision_rule"]
    assert measured["hypothesis_id"] == draft["scientific_question"]["hypothesis_id"]
    assert measured["hypothesis_revision"] == draft["scientific_question"]["hypothesis_hash"]
    assert measured["execution_plan_hash"] == execution["plan_hash"]
    assert measured["preregistration_root_hash"] == execution["preregistration_root_hash"]


def test_it_refuses_a_metric_the_preregistration_never_declared(tmp_path):
    api, execution, attempt, trace, draft, metric, endpoint = _test_api(tmp_path)
    with pytest.raises(MetricResultSealingError) as exc:
        _seal(api, execution, attempt, metric, metric_id="viability-recovery-profile")
    assert exc.value.reason == "METRIC_NOT_A_PREREGISTERED_ENDPOINT"


def test_it_refuses_a_classification_outside_the_declared_relations(tmp_path):
    api, execution, attempt, trace, draft, metric, endpoint = _test_api(tmp_path)
    with pytest.raises(MetricResultSealingError) as exc:
        _seal(api, execution, attempt, metric, classification="LOOKS_GOOD")
    assert "CLASSIFICATION_NOT_ONE_OF" in exc.value.reason


def test_it_refuses_an_instrument_that_reports_no_denominator(tmp_path):
    api, execution, attempt, trace, draft, metric, endpoint = _test_api(tmp_path)
    with pytest.raises(MetricResultSealingError) as exc:
        _seal(api, execution, attempt, metric, evaluator=lambda t: {"value": 1.0, "numerator": 1})
    assert exc.value.reason == "EVALUATOR_DID_NOT_REPORT_DENOMINATOR"


def test_a_refusal_seals_nothing(tmp_path):
    # An append-only ledger cannot take back a bad artifact, so a refusal must
    # happen before the write, not be cleaned up after it.
    api, execution, attempt, trace, draft, metric, endpoint = _test_api(tmp_path)
    with pytest.raises(MetricResultSealingError):
        _seal(api, execution, attempt, metric, classification="LOOKS_GOOD")
    with api.artifacts._connect() as con:
        count = con.execute("""SELECT count(*) FROM scientific_execution_artifacts
            WHERE execution_id=? AND artifact_type='METRIC_RESULT'""",
            (execution["execution_id"],)).fetchone()[0]
    assert count == 0


def test_the_scope_is_never_the_self_audit_scope(tmp_path):
    # A calibration report must not be publishable as a finding; the publication
    # service rejects that scope, and this function never writes it.
    api, execution, attempt, trace, draft, metric, endpoint = _test_api(tmp_path)
    sealed = _seal(api, execution, attempt, metric)
    assert sealed["measured"]["scope"] == "AUTHORIZED_SCIENTIFIC_RESULT"
