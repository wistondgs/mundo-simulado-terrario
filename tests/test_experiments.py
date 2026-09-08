"""Tests for the experiment subsystem: scenario loading, config, metrics, mini episodes."""

from __future__ import annotations

import os
import tempfile

import numpy as np
import pytest
import yaml

from terrario.experiment.config import ExperimentConfig
from terrario.experiment.controller import ExperimentController, build_world_state, load_scenario
from terrario.experiment.hypothesis import HypothesisSpec
from terrario.experiment.metrics import MetricsCalculator


class TestScenarioLoading:
    """Test that all scenario YAML files load correctly."""

    @pytest.mark.parametrize("scenario_file", [
        "scenarios/d0_differences.yaml",
        "scenarios/d1_objects.yaml",
        "scenarios/d2_properties.yaml",
        "scenarios/d3_causality.yaml",
        "scenarios/d4_change.yaml",
    ])
    def test_scenario_loads(self, scenario_file):
        scenario = load_scenario(scenario_file)
        assert "grid_size" in scenario
        assert "objects" in scenario
        assert "agent_start" in scenario
        assert "rules" in scenario
        assert len(scenario["objects"]) > 0

    @pytest.mark.parametrize("scenario_file", [
        "scenarios/d0_differences.yaml",
        "scenarios/d1_objects.yaml",
        "scenarios/d2_properties.yaml",
        "scenarios/d3_causality.yaml",
        "scenarios/d4_change.yaml",
    ])
    def test_scenario_builds_world(self, scenario_file):
        scenario = load_scenario(scenario_file)
        state = build_world_state(scenario)
        assert state.grid_width > 0
        assert len(state.objects) > 0
        assert len(state.agents) == 1

    def test_d4_has_changes(self):
        scenario = load_scenario("scenarios/d4_change.yaml")
        changes = scenario.get("changes", [])
        assert len(changes) > 0
        assert changes[0]["at_step"] == 750

    def test_d0_has_no_changes(self):
        scenario = load_scenario("scenarios/d0_differences.yaml")
        changes = scenario.get("changes", [])
        assert len(changes) == 0

    def test_scenario_channels_use_indices(self):
        """Verify scenarios use channel indices, not semantic names."""
        for fname in ["d0_differences", "d1_objects", "d2_properties", "d3_causality", "d4_change"]:
            path = f"scenarios/{fname}.yaml"
            with open(path) as f:
                raw = f.read()
            # Should not contain semantic channel names
            for semantic in ["color", "smell", "taste", "shape", "texture", "sound"]:
                assert semantic not in raw.lower(), f"Semantic name '{semantic}' found in {path}"


class TestExperimentConfig:
    def test_config_from_yaml(self):
        config = ExperimentConfig.from_yaml("configs/default.yaml")
        assert config.experiment_id == "default"
        assert config.scenario_path == "scenarios/d0_differences.yaml"
        assert len(config.agent_types) == 5
        assert len(config.seeds) == 3
        assert config.num_episodes == 3

    def test_config_hash_deterministic(self):
        c1 = ExperimentConfig.from_yaml("configs/default.yaml")
        c2 = ExperimentConfig.from_yaml("configs/default.yaml")
        assert c1.config_hash() == c2.config_hash()

    def test_config_hash_changes_with_params(self):
        c1 = ExperimentConfig.from_yaml("configs/default.yaml")
        c2 = ExperimentConfig.from_yaml("configs/default.yaml")
        c2.num_episodes = 99
        assert c1.config_hash() != c2.config_hash()

    def test_config_with_hypothesis(self):
        hyp_data = {
            "hypothesis": {
                "hypothesis_id": "H1",
                "claim": "Memory enables adaptation",
                "participants": ["memory"],
                "predicted_effect": "faster_adaptation",
                "world_pressure": "causal_rule_reversal",
                "controls": ["A0_RANDOM"],
                "ablations": ["use_episodic_memory"],
                "evidence_required": ["multiple_seeds"],
            }
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(hyp_data, f)
            path = f.name

        try:
            hyp = HypothesisSpec.from_yaml(path)
            assert hyp.hypothesis_id == "H1"
            assert "memory" in hyp.participants
        finally:
            os.unlink(path)

    def test_hypothesis_roundtrip(self):
        hyp = HypothesisSpec(
            hypothesis_id="H2",
            claim="Test claim",
            participants=["prediction"],
            predicted_effect="better_generalization",
            world_pressure="novel_objects",
            controls=["A0_RANDOM", "A1_REACTIVE"],
            ablations=["use_world_model"],
            evidence_required=["generalization"],
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            path = f.name

        try:
            hyp.to_yaml(path)
            loaded = HypothesisSpec.from_yaml(path)
            assert loaded.hypothesis_id == hyp.hypothesis_id
            assert loaded.claim == hyp.claim
            assert loaded.participants == hyp.participants
        finally:
            os.unlink(path)


class TestMetrics:
    def test_acquisition_rate_positive(self):
        energy = [100.0, 101.0, 102.0, 103.0, 104.0]
        rate = MetricsCalculator.acquisition_rate(energy)
        assert rate > 0

    def test_acquisition_rate_flat(self):
        energy = [100.0] * 10
        rate = MetricsCalculator.acquisition_rate(energy)
        assert rate == pytest.approx(0.0)

    def test_acquisition_rate_negative(self):
        energy = [100.0, 99.0, 98.0, 97.0]
        rate = MetricsCalculator.acquisition_rate(energy)
        assert rate < 0

    def test_adaptation_latency_recovers(self):
        # Energy drops at step 50, recovers at step 60
        energy = [100.0] * 50 + [80.0] * 5 + [95.0, 98.0, 100.0, 100.0, 100.0] + [100.0] * 40
        latency = MetricsCalculator.adaptation_latency(energy, change_step=50, window=10)
        assert latency >= 0

    def test_adaptation_latency_never_recovers(self):
        energy = [100.0] * 50 + [50.0] * 50
        latency = MetricsCalculator.adaptation_latency(energy, change_step=50, window=10)
        assert latency == -1.0

    def test_perseveration_cost(self):
        # Old optimal action = 2, agent keeps doing it after change
        actions = [0, 1, 2, 2, 2, 2, 2, 2, 2, 2]
        cost = MetricsCalculator.perseveration_cost(actions, change_step=5, old_optimal=2, window=5)
        assert cost == 5

    def test_perseveration_cost_zero(self):
        actions = [0, 1, 2, 3, 4, 0, 1, 3, 4, 0]
        cost = MetricsCalculator.perseveration_cost(actions, change_step=5, old_optimal=2, window=5)
        assert cost == 0

    def test_prediction_error_history(self):
        traces = [
            {"prediction_error": 0.5},
            {"prediction_error": 0.3},
            {"prediction_error": 0.1},
        ]
        errors = MetricsCalculator.prediction_error_history(traces)
        assert errors == [0.5, 0.3, 0.1]

    def test_generalization_score(self):
        assert MetricsCalculator.generalization_score(100.0, 90.0) == pytest.approx(0.9)
        assert MetricsCalculator.generalization_score(100.0, 100.0) == pytest.approx(1.0)
        assert MetricsCalculator.generalization_score(0.0, 0.0) == 0.0

    def test_efficiency(self):
        eff = MetricsCalculator.efficiency(performance=100.0, compute_cost=2.0, experience=50)
        assert eff == pytest.approx(1.0)

    def test_compute_all(self):
        episode_data = {
            "energy_history": [100.0, 101.0, 102.0],
            "actions": [0, 1, 2],
            "traces": [{"prediction_error": 0.1}],
            "final_energy": 102.0,
            "compute_cost": 1.0,
            "num_steps": 3,
        }
        metrics = MetricsCalculator.compute_all(episode_data)
        assert "final_energy" in metrics
        assert "acquisition_rate" in metrics
        assert "mean_energy" in metrics

    def test_compute_all_with_change(self):
        episode_data = {
            "energy_history": [100.0] * 50 + [80.0] * 10 + [100.0] * 40,
            "actions": [0] * 100,
            "traces": [],
            "final_energy": 100.0,
            "compute_cost": 1.0,
            "num_steps": 100,
        }
        metrics = MetricsCalculator.compute_all(episode_data, change_step=50)
        assert "adaptation_latency" in metrics
        assert "perseveration_cost" in metrics


class TestMiniEpisode:
    """Test that a mini episode runs without errors."""

    def test_mini_episode_d0(self, tmp_path):
        config = ExperimentConfig(
            experiment_id="test_mini",
            hypothesis=None,
            scenario_path="scenarios/d0_differences.yaml",
            agent_types=["A0_RANDOM"],
            agent_config={},
            seeds=[42],
            num_episodes=1,
            max_steps_per_episode=20,
            observer_mode="performance",
            checkpoint_every=100,
            output_dir=str(tmp_path),
        )
        controller = ExperimentController(config)
        results = controller.run()
        assert len(results["episodes"]) == 1
        ep = results["episodes"][0]
        assert ep["agent_type"] == "A0_RANDOM"
        assert ep["seed"] == 42
        assert ep["num_steps"] > 0

    def test_mini_episode_multiple_agents(self, tmp_path):
        config = ExperimentConfig(
            experiment_id="test_multi",
            hypothesis=None,
            scenario_path="scenarios/d0_differences.yaml",
            agent_types=["A0_RANDOM", "A1_REACTIVE"],
            agent_config={},
            seeds=[42],
            num_episodes=1,
            max_steps_per_episode=10,
            observer_mode="performance",
            checkpoint_every=100,
            output_dir=str(tmp_path),
        )
        controller = ExperimentController(config)
        results = controller.run()
        assert len(results["episodes"]) == 2

    def test_mini_episode_with_rule_change(self, tmp_path):
        config = ExperimentConfig(
            experiment_id="test_change",
            hypothesis=None,
            scenario_path="scenarios/d4_change.yaml",
            agent_types=["A0_RANDOM"],
            agent_config={},
            seeds=[42],
            num_episodes=1,
            max_steps_per_episode=20,
            observer_mode="performance",
            checkpoint_every=100,
            output_dir=str(tmp_path),
        )
        controller = ExperimentController(config)
        results = controller.run()
        assert len(results["episodes"]) == 1
        # Episode should complete without errors even with scheduled changes
        assert results["episodes"][0]["num_steps"] > 0
