"""Regression tests for real Terrario agents, not controller fallbacks."""

from __future__ import annotations

import numpy as np
import pytest

from terrario.agent.agents import create_agent
from terrario.core.contracts import Transition
from terrario.core.types import Action, ActionType, Consequence, Observation


def make_obs() -> Observation:
    return Observation(
        channels=np.random.default_rng(1).random((4, 5, 5), dtype=np.float32),
        mask=np.ones((5, 5), dtype=np.float32), agent_energy=0.8, time_fraction=0.5,
    )


def make_transition(obs: Observation) -> Transition:
    return Transition(obs, None, Action.noop(), Consequence(1.0, ["contact"]), obs, False, False, 0, 42)


class TestAgentCreation:
    @pytest.mark.parametrize("requested, architecture", [
        ("A0_RANDOM", "A0_RANDOM"), ("A1_REACTIVE", "A1_REACTIVE"),
        ("A2_GRU", "A2_GRU"), ("A3_WORLD_MODEL", "A3_WORLD_MODEL"),
        ("A4_ADVANCED", "A4_ADVANCED"),
    ])
    def test_requested_agent_is_instantiated(self, requested, architecture):
        agent = create_agent(requested, {"use_planner": False}, seed=42)
        assert agent.agent_identity["requested_agent_id"] == requested
        assert agent.agent_identity["architecture_id"] == architecture
        assert agent.agent_identity["instantiated_agent_class"] == type(agent).__name__

    def test_invalid_agent_fails_loudly(self):
        with pytest.raises(ValueError, match="Unsupported agent"):
            create_agent("BROKEN_AGENT", seed=42)


class TestAgentInterface:
    @pytest.mark.parametrize("agent_type", ["A0_RANDOM", "A1_REACTIVE", "A2_GRU", "A3_WORLD_MODEL", "A4_ADVANCED"])
    def test_real_agent_full_cycle(self, agent_type):
        agent = create_agent(agent_type, {"use_planner": False}, seed=42)
        obs = make_obs()
        agent.perceive(obs)
        action = agent.decide()
        assert isinstance(action, Action)
        assert isinstance(action.action_type, ActionType)
        agent.learn(make_transition(obs))
        assert isinstance(agent.get_internal_state(), dict)


class TestAblationAndRandomness:
    def test_a4_ablation_flags_are_real(self):
        agent = create_agent("A4_ADVANCED", {
            "use_temporal": False, "use_episodic_memory": False,
            "use_longterm_memory": False, "use_world_model": False,
            "use_uncertainty": False, "use_online_learning": False,
        }, seed=42)
        assert agent.config["use_online_learning"] is False

    def test_random_agent_is_seed_deterministic(self):
        obs = make_obs()
        first = create_agent("A0_RANDOM", seed=42)
        second = create_agent("A0_RANDOM", seed=42)
        first.perceive(obs)
        second.perceive(obs)
        assert first.decide().to_int() == second.decide().to_int()
