from terrario.experiment.statistics import paired_comparison


def test_paired_comparison_matches_world_seeds_only():
    result = paired_comparison({1: .8, 2: .6}, {1: .5, 3: .1})
    assert result["n"] == 1 and result["wins"] == 1
