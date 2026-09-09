from terrario.experiment.adaptation import assess_run_validity
from terrario.experiment.campaign import ReasonCode


def _record(**updates):
    record = {
        "change_step": 10,
        "primary": {"num_steps": 220},
        "metrics": {"pre_change_status": "VALID", "post_change_status": "VALID", "pre_change_competence": 0.8},
        "numerical_health": {"finite_parameters": True, "finite_memory": True, "nonfinite_learning_events": 0, "aborted": False},
        "transfer_parameters_unchanged": True,
        "transfer_adaptive_state_unchanged": True,
        "classification": "RECOVERED",
        "opportunity_contract": {
            "record_count": 32, "all_spawn_positions_reachable": True, "concurrent_balance_pass": True,
        },
    }
    record.update(updates)
    return record


def test_validity_separates_world_signal_from_agent_interaction():
    record = _record(metrics={"pre_change_status": "INSUFFICIENT_EVIDENCE", "post_change_status": "VALID", "pre_change_competence": 0.0})

    validity = assess_run_validity(record)

    assert validity.world_signal_sufficient.passed is True
    assert validity.agent_interaction_sufficient.reason is ReasonCode.INSUFFICIENT_AGENT_INTERACTION
    assert validity.experimentally_interpretable.passed is False


def test_validity_marks_transfer_contamination_without_reclassifying_execution():
    validity = assess_run_validity(_record(transfer_parameters_unchanged=False))

    assert validity.technical_valid.passed is True
    assert validity.transfer_integrity_valid.reason is ReasonCode.TRANSFER_CONTAMINATED
