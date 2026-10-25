from __future__ import annotations

import json

from terrario.level19.experiment import HELD_OUT_SEEDS, campaign, life


def test_l19_life_has_causal_prediction_decision_and_checkpoint(tmp_path):
    row = life(HELD_OUT_SEEDS[0], train_episodes=192, evaluation_episodes=96,
               checkpoint=tmp_path / "checkpoint.json")
    assert row["predictive_gain"] > 0.0
    assert row["decision_gain"] > 0.35
    assert row["observation_action_gain"] > 0.35
    assert row["perturbed_decision_gain"] > 0.20
    assert row["splits"] > 0
    assert row["checkpoint_hash"]
    assert row["train_seed"] != row["seed"]


def test_l19_campaign_keeps_training_and_heldout_data_separate(tmp_path):
    result = campaign(seeds=HELD_OUT_SEEDS[:4], train_episodes=192,
                      evaluation_episodes=96, checkpoint_dir=tmp_path)
    assert result["verdict"] == "CAPACIDAD_DEMOSTRADA"
    assert result["lcb95_predictive_gain"] > 0.0
    assert result["lcb95_decision_gain"] > 0.0
    assert len(list(tmp_path.glob("*.json"))) == 4
    assert {row["train_seed"] for row in result["lives"]}.isdisjoint(
        {row["seed"] for row in result["lives"]})
