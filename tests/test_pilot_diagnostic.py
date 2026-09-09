from terrario.experiment.adaptation import diagnose_pilot


def test_pilot_diagnostic_rejects_nonfinite_learning_and_unpaired_worlds():
    record = {
        "variant_id": "A0_RANDOM", "seed": 1, "world_spec_hash": "world-a",
        "metrics": {"pre_change_status": "VALID", "post_change_status": "VALID", "pre_change_competence": 0.5, "prediction_error_spike": "NOT_APPLICABLE"},
        "numerical_health": {"finite_parameters": True, "finite_memory": True, "nonfinite_learning_events": 1, "aborted": False},
        "transfer_parameters_unchanged": True, "transfer_adaptive_state_unchanged": True,
    }
    diagnosis = diagnose_pilot([record], [1], ["A0_RANDOM"])
    assert diagnosis["status"] == "FAIL"
    assert diagnosis["gates"]["P1_numerical_integrity"] is False
