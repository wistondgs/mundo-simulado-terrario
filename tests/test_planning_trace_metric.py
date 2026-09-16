from terrario.lab.metrics_observer import ConstructValidationStatus, MetricImplementationStatus, MetricRegistry, ObserverRegistry
from terrario.lab.planning_trace_metric import (
    METRIC_ID, METRIC_VERSION, PlanningTraceMetricError, evaluate, evaluate_scientific_trace,
    freeze_construct_validation, specification, validate_construct,
)
from terrario.lab.persistence import ArtifactRepository
from terrario.lab.execution.runtime import ScientificTrialIdentity, run_materialized_trial


def _decision(step): return {"op": "decide", "step": step, "action_int": step % 4}
def _plan(action): return {"op": "plan", "horizon": 2, "num_candidates": 2, "best_action": action, "rollouts": [{"candidate": 0, "actions": [action, 0]}]}


def test_exact_cl4_metric_is_transport_verified_not_planning_quality():
    definition = MetricRegistry().get(METRIC_ID)
    assert definition.implementation_status is MetricImplementationStatus.IMPLEMENTED
    assert definition.construct_validation_status is ConstructValidationStatus.VALIDATED_FOR_CONSTRUCT
    assert "quality" not in definition.construct and "energy" not in definition.mathematical_definition
    assert "planner_proposal_trace" in ObserverRegistry().profile("STANDARD").channels


def test_planner_trace_metric_has_explicit_counts_and_no_proxy_substitution():
    result = evaluate((_decision(0), _plan(0), _decision(1), _plan(1)))
    assert (result.metric_id, result.metric_version, result.numerator, result.denominator, result.value) == (METRIC_ID, METRIC_VERSION, 2, 2, 1.0)
    absent = evaluate((_decision(0), _decision(1)))
    assert (absent.numerator, absent.denominator, absent.value) == (0, 2, 0.0)


def test_trace_metric_fails_closed_for_leakage_malformed_and_ablated_pathway():
    import pytest
    with pytest.raises(PlanningTraceMetricError, match="LEAKAGE"):
        evaluate((_decision(0), _plan(0)), agent_observation={"optimal_action": 0})
    with pytest.raises(PlanningTraceMetricError, match="MALFORMED"):
        evaluate((_decision(0), {"op": "plan", "horizon": 1}))
    # A treatment label is not an evaluator input: trace semantics alone drive
    # the result.  Terminal integrity separately checks the ablated mechanism.
    assert evaluate((_decision(0), _plan(0))).value == 1.0


def test_metric_reads_only_sealed_observer_trace_and_rejects_missing_transport():
    trace = {"frames": [
        {"tick": 0, "observer_view": {}},
        {"tick": 1, "world_truth": {"oracle_score": 100}, "agent_observation": {"optimal_action": 2},
         "observer_view": {"decision_trace": [_decision(0)], "planner_proposal_trace": [_plan(0)]}},
        {"tick": 2, "observer_view": {"decision_trace": [_decision(1)], "planner_proposal_trace": [_plan(1)]}},
    ]}
    result = evaluate_scientific_trace(trace)
    assert (result.numerator, result.denominator, result.value) == (2, 2, 1.0)
    import pytest
    with pytest.raises(PlanningTraceMetricError, match="PLANNER_PROJECTION_REQUIRED"):
        evaluate_scientific_trace({"frames": [{"tick": 1, "observer_view": {}}]})


def test_real_a4_runtime_seals_exact_planner_ablation_trace(tmp_path):
    """Transport calibration: it is explicitly not an authorized experiment."""
    from pathlib import Path
    from terrario.lab.execution.runtime import scientific_frame_payload
    from terrario.lab.persistence.canonical import canonical_json
    def calibrate(name, config, expected):
        identity = ScientificTrialIdentity(
            f"CALIBRATION-{name}", "INTENT-CALIBRATION", f"ATTEMPT-{name}", "p" * 64, "r" * 64,
            "LOCAL-CALIBRATION", "d2-calibration", "A4_ADVANCED", 17, 23, config,
        )
        frames = []
        outcome = run_materialized_trial(
            tmp_path / name, identity, scenario_path=Path("scenarios/d2_properties.yaml"),
            observer_profile="scientific_standard", step_limit=2,
            frame_sink=lambda frame: frames.append(scientific_frame_payload(frame)),
        )
        assert outcome["observation_faults"] == []
        # The exact A4 planner projection is representable by the same
        # canonical serializer used when the dispatcher seals SCIENTIFIC_TRACE.
        canonical_json({"identity": outcome["identity"], "frames": frames})
        return evaluate_scientific_trace({"frames": frames})

    preserved = calibrate("preserved", {"use_planner": True, "use_world_model": True}, True)
    ablated = calibrate("ablated", {"use_planner": False, "use_world_model": True}, False)
    assert (preserved.numerator, preserved.denominator, preserved.value) == (2, 2, 1.0)
    assert (ablated.numerator, ablated.denominator, ablated.value) == (0, 2, 0.0)


def test_construct_validation_is_deterministic_and_not_agent_evidence():
    report = validate_construct()
    assert report["evaluator_calibrated"] and report["construct_validated"] and report["transport_verified"] and all(report["checks"].values())
    assert report["agent_executed"] is False and report["scientific_result"] is False and report["evidence_graph_writes"] == 0
    assert report["metric"]["metric_spec_hash"] == specification()["metric_spec_hash"]
    assert "lookahead-choice oracle" in report["not_applicable"]


def test_construct_validation_freeze_is_durable_and_idempotent(tmp_path):
    artifacts = ArtifactRepository(tmp_path / ".terrario")
    first = freeze_construct_validation(artifacts)
    second = freeze_construct_validation(artifacts)
    assert first.sealed and second.version_id == first.version_id
    assert artifacts.current_state(first.version_id) == "CONSTRUCT_VALIDATED"
