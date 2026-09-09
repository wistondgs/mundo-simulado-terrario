from terrario.experiment.specs import EvidenceRecord, EvidenceSpec, ExperimentSpec, experiments_from_hypothesis, run_experiment_specs, synthetic_h_adapt_001


def test_hypothesis_generates_traceable_conditions_and_evidence():
    hypothesis = synthetic_h_adapt_001()
    experiments = experiments_from_hypothesis(hypothesis, "scenarios/d4_change.yaml", [1, 2])
    assert {item.condition_id for item in experiments} == {"full", "no-memory", "no-prediction", "no-online-learning", "reactive", "random"}
    evidence = EvidenceRecord(EvidenceSpec("memory", hypothesis.hypothesis_id, "memory->adaptation"), experiments[0].experiment_id, "run-1", experiments[0].config_hash(), "code-hash")
    record = evidence.to_dict()
    assert record["evidence_spec"]["hypothesis_id"] == "H-ADAPT-001"
    assert record["config_hash"] == experiments[0].config_hash()


def test_experiment_spec_executes_into_evidence(tmp_path):
    spec = ExperimentSpec("H-ADAPT-001:random", "H-ADAPT-001", "random", "A0_RANDOM", {}, "scenarios/d0_differences.yaml", [3])
    runs, evidence = run_experiment_specs([spec], str(tmp_path), "test-code", max_steps=1, observer_mode="performance")
    assert len(runs) == 1
    assert evidence and all(record.config_hash == spec.config_hash() for record in evidence)
    assert all(record.code_hash == "test-code" for record in evidence)
