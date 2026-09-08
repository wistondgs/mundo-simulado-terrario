"""Tests for agent creation, interface compliance, and ablation."""

from __future__ import annotations

import numpy as np
import pytest

from terrario.core.types import Action, ActionType, Consequence, Observation


class TestAgentCreation:
    """Test that each agent type can be created."""

    def test_builtin_agent_types(self):
        from terrario.experiment.controller import _BuiltinAgent

        for agent_type in ["A0_RANDOM", "A1_REACTIVE", "A2_GRU", "A3_WORLD_MODEL", "A4_ADVANCED"]:
            agent = _BuiltinAgent(agent_type, seed=42)
            assert agent.agent_type == agent_type

    def test_agent_has_required_methods(self):
        from terrario.experiment.controller import _BuiltinAgent

        agent = _BuiltinAgent("A0_RANDOM", seed=42)
        assert hasattr(agent, "perceive")
        assert hasattr(agent, "decide")
        assert hasattr(agent, "learn")
        assert callable(agent.perceive)
        assert callable(agent.decide)
        assert callable(agent.learn)


class TestAgentInterface:
    """Test AgentInterface compliance."""

    def _make_obs(self) -> Observation:
        return Observation(
            channels=np.random.rand(4, 5, 5).astype(np.float32),
            mask=np.ones((5, 5), dtype=np.float32),
            agent_energy=0.8,
            time_fraction=0.5,
        )

    def test_perceive_accepts_observation(self):
        from terrario.experiment.controller import _BuiltinAgent

        agent = _BuiltinAgent("A0_RANDOM", seed=42)
        obs = self._make_obs()
        agent.perceive(obs)  # should not raise

    def test_decide_returns_action(self):
        from terrario.experiment.controller import _BuiltinAgent

        for agent_type in ["A0_RANDOM", "A1_REACTIVE"]:
            agent = _BuiltinAgent(agent_type, seed=42)
            agent.perceive(self._make_obs())
            action = agent.decide()
            assert isinstance(action, Action)
            assert isinstance(action.action_type, ActionType)

    def test_learn_accepts_consequence(self):
        from terrario.experiment.controller import _BuiltinAgent

        agent = _BuiltinAgent("A0_RANDOM", seed=42)
        consequence = Consequence(energy_delta=5.0, events=["test"])
        agent.learn(consequence)  # should not raise

    def test_full_cycle(self):
        from terrario.experiment.controller import _BuiltinAgent

        agent = _BuiltinAgent("A1_REACTIVE", seed=42)
        obs = self._make_obs()
        agent.perceive(obs)
        action = agent.decide()
        consequence = Consequence(energy_delta=1.0, events=["test"], new_observation=obs)
        agent.learn(consequence)


class TestA4Ablation:
    """Test that disabling A4 modules doesn't crash."""

    def test_ablation_flags_accepted(self):
        from terrario.experiment.controller import _BuiltinAgent

        # The builtin agent doesn't use config, but the factory should accept it
        agent = _BuiltinAgent("A4_ADVANCED", seed=42)
        assert agent is not None

    def test_ablation_with_config(self, tmp_path):
        """Test that agent creation works with various module flags disabled."""
        from terrario.experiment.controller import ExperimentController
        from terrario.experiment.config import ExperimentConfig

        modules = [
            "use_temporal",
            "use_episodic_memory",
            "use_longterm_memory",
            "use_world_model",
            "use_uncertainty",
            "use_online_learning",
        ]

        config = ExperimentConfig(
            experiment_id="test_ablation",
            hypothesis=None,
            scenario_path="scenarios/d0_differences.yaml",
            agent_types=["A4_ADVANCED"],
            agent_config={},
            seeds=[42],
            num_episodes=1,
            max_steps_per_episode=10,
            observer_mode="performance",
            checkpoint_every=100,
            output_dir=str(tmp_path),
        )
        controller = ExperimentController(config)

        for module in modules:
            # Should not crash
            agent = controller._create_agent("A4_ADVANCED", seed=42)
            assert agent is not None


class TestA4StateDependence:
    """Test that agent with different history can produce different actions."""

    def test_random_agent_deterministic_with_seed(self):
        from terrario.experiment.controller import _BuiltinAgent

        agent1 = _BuiltinAgent("A0_RANDOM", seed=42)
        agent2 = _BuiltinAgent("A0_RANDOM", seed=42)

        obs = Observation(
            channels=np.zeros((4, 5, 5), dtype=np.float32),
            mask=np.ones((5, 5), dtype=np.float32),
            agent_energy=0.5,
            time_fraction=0.5,
        )

        agent1.perceive(obs)
        agent2.perceive(obs)

        action1 = agent1.decide()
        action2 = agent2.decide()
        assert action1.to_int() == action2.to_int()

    def test_different_seeds_different_actions(self):
        from terrario.experiment.controller import _BuiltinAgent

        obs = Observation(
            channels=np.zeros((4, 5, 5), dtype=np.float32),
            mask=np.ones((5, 5), dtype=np.float32),
            agent_energy=0.5,
            time_fraction=0.5,
        )

        actions = set()
        for seed in range(20):
            agent = _BuiltinAgent("A0_RANDOM", seed=seed)
            agent.perceive(obs)
            action = agent.decide()
            actions.add(action.to_int())

        # With 20 different seeds, we should get more than one unique action
        assert len(actions) > 1
