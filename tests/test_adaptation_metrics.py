import math

from terrario.experiment.adaptation import (
    INSUFFICIENT_EVIDENCE,
    NOT_APPLICABLE,
    AdaptationThresholds,
    adaptation_metrics,
    causal_competence,
    prediction_metrics,
)


def _traces(change_step=20):
    traces = []
    for step in range(60):
        appropriate = step < change_step or step >= 40
        traces.append({
            "step": step,
            "prediction_error": 0.1 if step < change_step else 0.9 - (step - change_step) * 0.02,
            "causal_interaction": {
                "informative": True,
                "causally_appropriate": appropriate,
                "hidden_causal_class": "A" if step % 2 else "B",
            },
        })
    return traces


def test_causal_competence_refuses_sparse_windows():
    result = causal_competence(_traces()[:3], 0, 3, minimum_interactions=12)
    assert result["status"] == INSUFFICIENT_EVIDENCE
    assert math.isnan(result["competence"])


def test_prediction_is_explicitly_not_applicable_without_predictor():
    assert prediction_metrics(_traces(), 20, predictor_available=False) == {
        "prediction_error_spike": NOT_APPLICABLE,
        "prediction_error_decay": NOT_APPLICABLE,
    }


def test_adaptation_metrics_compute_recovery_and_prediction_windows():
    thresholds = AdaptationThresholds(minimum_informative_interactions=5, window_steps=10)
    metrics = adaptation_metrics({"traces": _traces(), "num_steps": 60}, 20, True, thresholds=thresholds)
    assert metrics["pre_change_competence"] == 1.0
    assert metrics["post_change_drop"] == 1.0
    assert metrics["recovery_latency"] == 20.0
    assert metrics["prediction_error_spike"] > 0
