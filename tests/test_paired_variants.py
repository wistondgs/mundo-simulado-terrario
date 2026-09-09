import math

from terrario.experiment.adaptation import VARIANTS, summarize_records


def test_h_adapt_variant_set_contains_controls_full_and_three_ablations():
    assert list(VARIANTS) == [
        "A0_RANDOM", "A1_REACTIVE", "A2_GRU", "A3_WORLD_MODEL", "A4_ADVANCED",
        "A4_NO_MEMORY", "A4_NO_PREDICTION", "A4_NO_ONLINE_LEARNING",
    ]


def test_ablation_summary_uses_seed_matched_difference():
    records = [
        {"variant_id": "A4_ADVANCED", "seed": 7, "metrics": {"recovered_competence": 0.8}},
        {"variant_id": "A4_NO_MEMORY", "seed": 7, "metrics": {"recovered_competence": 0.5}},
    ]
    summary = summarize_records(records)
    paired = summary["paired_ablations"]["A4_NO_MEMORY"]
    assert paired["n"] == 1
    assert math.isclose(paired["mean_difference"], 0.3)
