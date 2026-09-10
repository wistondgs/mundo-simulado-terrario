from terrario.lab.theory.factory import ExperimentCostEstimator
def test_cost_is_deterministic_and_labels_basis():
    e=ExperimentCostEstimator(); a=e.estimate(3,4); b=e.estimate(3,4)
    assert a == b and a.runs == 12 and a.basis == "ASSUMPTION_BASED"
    assert e.estimate(1,2,observed_seconds_per_run=4,bytes_per_run=8).basis == "OBSERVED_BASED"
