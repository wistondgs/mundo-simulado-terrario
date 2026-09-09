from terrario.experiment.statistics import bootstrap_ci


def test_bootstrap_is_seed_reproducible():
    assert bootstrap_ci([1.0, 2.0, 3.0], seed=9) == bootstrap_ci([1.0, 2.0, 3.0], seed=9)
