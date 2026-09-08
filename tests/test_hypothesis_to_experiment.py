from terrario.experiment.specs import EvidenceRecord, EvidenceSpec, experiments_from_hypothesis, synthetic_h_adapt_001


def test_hypothesis_generates_traceable_conditions_and_evidence():
    hypothesis = synthetic_h_adapt_001()
    experiments = experiments_from_hypothesis(hypothesis, "scenarios/d4_change.yaml", [1, 2])
    assert {item.condition_id for item in experiments} == {"full", "no-memory", "no-prediction", "no-online-learning", "reactive", "random"}
    evidence = EvidenceRecord(EvidenceSpec("memory", hypothesis.hypothesis_id, "memory->adaptation"), experiments[0].experiment_id, "run-1", experiments[0].config_hash(), "code-hash")
    record = evidence.to_dict()
    assert record["evidence_spec"]["hypothesis_id"] == "H-ADAPT-001"
    assert record["config_hash"] == experiments[0].config_hash()
