"""The homeostatic path must be ablatable, and ablating it must change only that path.

Block 1 of the concept map -- viability -- was the one module with no flag, so
the question ADR-001 and ADR-002 ask (does viability have causal authority over
behaviour?) had no do(module = off) available.  These tests pin the two halves
that make the answer interpretable: the default arm is unchanged, and the
control arm still MEASURES viability while no longer being STEERED by it.
"""
import numpy as np

from terrario.agent.agents import create_agent
from terrario.agent.agents.a4_advanced import DEFAULT_CONFIG
from terrario.core.contracts import Transition
from terrario.core.types import Consequence, Observation


def _observation(energy=0.2):
    return Observation(np.full((4, 5, 5), 0.2, dtype=np.float32),
                       np.ones((5, 5), dtype=np.float32), energy, 0.1)


def _small(**overrides):
    config = {"use_planner": False, "use_uncertainty": False, "use_episodic_memory": False,
              "use_longterm_memory": False, "use_temporal": False, "use_online_learning": False,
              "latent_dim": 16, "hidden_dim": 24, "memory_dim": 8, "memory_slots": 4,
              "ensemble_size": 2}
    return config | overrides


def _drive_energy_down(agent, steps=6):
    """Push the organism below its homeostatic threshold, then read the decision."""
    observation = _observation()
    for step in range(steps):
        agent.perceive(observation)
        action = agent.decide()
        agent.learn(Transition(observation, None, action, Consequence(-0.2, []),
                               observation, False, False, step, 1))
    agent.perceive(observation)
    agent.decide()
    return next(item for item in agent.get_trace_events() if item.get("op") == "decide")


def test_default_keeps_homeostasis_on_and_threshold_unchanged():
    # The flag is additive: a default agent must be the agent that existed before it.
    assert DEFAULT_CONFIG["use_homeostasis"] is True
    assert DEFAULT_CONFIG["homeostasis_threshold"] == 0.5
    agent = create_agent("A4", _small(), seed=7)
    assert agent.homeostasis.threshold == 0.5


def test_ablation_removes_the_only_path_from_viability_to_behaviour():
    # temperature is the single site where viability pressure reaches the
    # action distribution.  With the flag off it must be the unmodulated 1.0.
    off = _drive_energy_down(create_agent("A4", _small(use_homeostasis=False), seed=7))
    assert off["temperature"] == 1.0

    on = _drive_energy_down(create_agent("A4", _small(use_homeostasis=True), seed=7))
    assert on["temperature"] > 1.0


def test_control_arm_still_measures_viability():
    # Ablating the bookkeeping too would confound "viability has no causal
    # authority" with "viability was never measured".
    event = _drive_energy_down(create_agent("A4", _small(use_homeostasis=False), seed=7))
    assert event["drive"] > 0.0
    assert event["exploration_bias"] > 0.0


def test_ablation_is_self_declaring_in_the_observer_trace():
    agent = create_agent("A4", _small(use_homeostasis=False), seed=7)
    agent.perceive(_observation())
    agent.decide()
    assert "use_homeostasis" in agent.get_scientific_state()["active_ablations"]
    on = create_agent("A4", _small(use_homeostasis=True), seed=7)
    on.perceive(_observation())
    on.decide()
    assert "use_homeostasis" not in on.get_scientific_state()["active_ablations"]


def test_threshold_is_declarable_and_is_not_the_observer_eta():
    # eta belongs in a preregistration, not in a constructor signature. A
    # different threshold is a different organism, not a different reading.
    agent = create_agent("A4", _small(homeostasis_threshold=0.23), seed=7)
    assert agent.homeostasis.threshold == 0.23
    agent.homeostasis.update(-0.7)  # energy 1.0 -> 0.3, above 0.23, below 0.5
    assert agent.homeostasis.drive == 0.0
    strict = create_agent("A4", _small(homeostasis_threshold=0.5), seed=7)
    strict.homeostasis.update(-0.7)
    assert strict.homeostasis.drive > 0.0
