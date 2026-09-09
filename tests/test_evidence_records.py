from terrario.experiment.adaptation import AdaptationProtocolRunner


def test_protocol_emits_an_evidence_record_per_paired_run(tmp_path, monkeypatch):
    runner = AdaptationProtocolRunner(
        "scenarios/d4_adaptation_scientific.yaml",
        "scenarios/d4_adaptation_transfer.yaml",
        str(tmp_path),
    )

    def fake_run_variant(variant_id, seed):
        return {
            "variant_id": variant_id, "seed": seed, "world_spec_hash": str(seed),
            "metrics": {"recovered_competence": 0.5, "pre_change_status": "VALID", "post_change_status": "VALID", "pre_change_competence": 0.8, "prediction_error_spike": 0.1},
            "numerical_health": {"finite_parameters": True, "finite_memory": True, "nonfinite_learning_events": 0, "aborted": False},
            "transfer_parameters_unchanged": True, "transfer_adaptive_state_unchanged": True,
        }

    monkeypatch.setattr(runner, "run_variant", fake_run_variant)
    result = runner.run([1, 2], variants=["A0_RANDOM", "A4_ADVANCED"])

    assert len(result["records"]) == 4
    assert len(result["evidence"]) == 4
    assert all(item["evidence_spec"]["hypothesis_id"] == "H-ADAPT-001" for item in result["evidence"])
