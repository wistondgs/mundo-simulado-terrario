from terrario.experiment.adaptation import AdaptationThresholds, adaptation_criterion


def _metrics(**overrides):
    baseline = {
        "pre_change_status": "VALID", "pre_change_competence": 0.8,
        "post_change_drop": 0.3, "recovery_latency": 100.0,
        "recovered_competence": 0.8, "transfer_score": 0.7,
    }
    return {**baseline, **overrides}


def test_criterion_separates_no_disruption_from_failure():
    assert adaptation_criterion(_metrics(post_change_drop=0.1)) == "NO_DISRUPTION_OBSERVED"
    assert adaptation_criterion(_metrics(recovery_latency="INSUFFICIENT_EVIDENCE")) == "FAILED_TO_RECOVER"


def test_criterion_requires_pre_change_competence_and_can_confirm_transfer():
    assert adaptation_criterion(_metrics(pre_change_competence=0.5)) == "NOT_LEARNED_PRE_CHANGE"
    assert adaptation_criterion(_metrics(transfer_score=0.8), AdaptationThresholds()) == "RECOVERED_AND_TRANSFERRED"
