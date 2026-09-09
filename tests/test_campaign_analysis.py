from terrario.experiment.adaptation import analyze_records


def _record(variant_id, seed, recovered, valid=True):
    return {
        "variant_id": variant_id, "seed": seed, "run_id": f"{variant_id}-{seed}", "change_step": 10,
        "primary": {"num_steps": 220}, "classification": "RECOVERED",
        "metrics": {
            "pre_change_status": "VALID", "post_change_status": "VALID", "pre_change_competence": 0.8,
            "post_change_drop": 0.3, "recovered_competence": recovered, "recovery_latency": 100.0, "transfer_score": 0.7,
        },
        "numerical_health": {"finite_parameters": True, "finite_memory": True, "nonfinite_learning_events": 0, "aborted": False},
        "transfer_parameters_unchanged": True, "transfer_adaptive_state_unchanged": True,
        "opportunity_contract": {"record_count": 32, "all_spawn_positions_reachable": True, "concurrent_balance_pass": valid},
    }


def test_campaign_analysis_excludes_noninterpretable_runs_and_keeps_paired_effects():
    records = [
        _record("A4_ADVANCED", 1, 0.9), _record("A4_ADVANCED", 2, 0.8),
        _record("A4_NO_MEMORY", 1, 0.5), _record("A4_NO_MEMORY", 2, 0.4),
        _record("A4_NO_PREDICTION", 3, 0.6, valid=False),
    ]

    analysis = analyze_records(records)

    assert analysis["analysis_population"]["n_experimentally_interpretable"] == 4
    paired = analysis["paired_ablations"]["A4_NO_MEMORY"]
    assert paired["n"] == 2
    assert paired["wins"] == 2
