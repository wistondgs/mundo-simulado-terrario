"""G4 mechanical purity for the human-approved LEARN-A1 intervention.

These tests intentionally do not compare reward or conversion.  They pin the
first direct divergence to the optimizer commit and keep replay inputs fixed.
"""
from __future__ import annotations

import hashlib
from typing import Any

import numpy as np
import torch

from terrario.agent.agents import create_agent
from terrario.core.contracts import Transition
from terrario.core.rng import RNGManager
from terrario.core.types import Consequence, Observation
from terrario.experiment.controller import load_scenario
from terrario.lab.capability_intervention import (
    LEARN_A1_COMMIT_MANIFEST, InterventionManifest,
)
from terrario.lab.capability_operationalization import LEARN_A1_OPERATIONALIZATION
from terrario.lab.world_registry import WorldScenarioRegistry
from terrario.world.transition import build_episode_components, run_step


SEED = 47017
USE_KEYS = (
    "use_planner", "use_world_model", "use_episodic_memory", "use_longterm_memory",
    "use_uncertainty", "use_homeostasis", "use_temporal", "use_online_learning",
)


def _config(*, commit: bool) -> dict[str, Any]:
    return {
        "use_planner": False, "use_uncertainty": True, "use_episodic_memory": True,
        "use_longterm_memory": True, "use_temporal": True, "use_online_learning": True,
        "latent_dim": 16, "hidden_dim": 24, "memory_dim": 8, "memory_slots": 4,
        "memory_capacity": 16, "ensemble_size": 2, "learning_commit_enabled": commit,
    }


def _agent(*, commit: bool):
    # Module initialization uses Torch's global generator; reset it before
    # each twin exists.  The agent-local generator is separately seeded by the
    # factory and is checked below.
    RNGManager.set_global_determinism(SEED)
    return create_agent("A4_ADVANCED", _config(commit=commit), seed=SEED)


def _observation() -> Observation:
    return Observation(
        np.full((4, 5, 5), 0.2, dtype=np.float32), np.ones((5, 5), dtype=np.float32),
        0.5, 0.1,
    )


def _hash(value: Any) -> str:
    digest = hashlib.sha256()

    def visit(item: Any) -> None:
        if isinstance(item, torch.Tensor):
            digest.update(str((tuple(item.shape), str(item.dtype))).encode())
            digest.update(item.detach().cpu().contiguous().numpy().tobytes())
        elif isinstance(item, dict):
            for key in sorted(item, key=str):
                digest.update(str(key).encode()); visit(item[key])
        elif isinstance(item, (list, tuple)):
            for child in item:
                visit(child)
        else:
            digest.update(repr(item).encode())

    visit(value)
    return digest.hexdigest()


def _parameter_hash(agent: Any) -> str:
    return agent._parameters_hash(agent.get_parameters())


def _optimizer_hash(agent: Any) -> str:
    return _hash(agent.learner._optimizer.state_dict())


def _first_parameter_difference(full: Any, amputated: Any) -> str:
    full_parameters, ablated_parameters = full.get_parameters(), amputated.get_parameters()
    assert full_parameters.keys() == ablated_parameters.keys()
    return next(name for name in sorted(full_parameters)
                if not torch.equal(full_parameters[name], ablated_parameters[name]))


def _non_target_snapshot(agent: Any) -> dict[str, Any]:
    return {
        "episodic_memory": _hash(agent.episodic_memory._buffer),
        "episodic_write_index": agent.episodic_memory._write_idx,
        "hidden": _hash(agent._hidden),
        "homeostasis": _hash(agent.homeostasis.get_state()),
        "agent_rng": _hash(agent._generator.get_state()),
        "learning_signal": (agent._energy_baseline, agent._baseline_count, agent.learner.step_count),
        "configuration": tuple((key, agent.config[key]) for key in USE_KEYS),
        "architecture": (agent._state_dim, agent.config["latent_dim"], agent.config["hidden_dim"]),
    }


def _learn_once(full: Any, amputated: Any) -> tuple[list[dict], list[dict]]:
    observation = _observation()
    for agent in (full, amputated):
        agent.perceive(observation)
    assert _hash(full.get_scientific_state()) == _hash(amputated.get_scientific_state())
    full_action, ablated_action = full.decide(), amputated.decide()
    assert full_action == ablated_action
    transition = Transition(
        observation, None, full_action, Consequence(1.0, []), observation,
        False, False, 0, SEED,
    )
    full.learn(transition)
    amputated.learn(transition)
    return full.get_trace_events(), amputated.get_trace_events()


def _learning_event(events: list[dict]) -> dict:
    return next(event for event in events if event.get("op") == "learning_step")


def test_manifest_round_trip_and_binding_are_explicit():
    manifest = LEARN_A1_COMMIT_MANIFEST
    assert manifest.operationalization_id == LEARN_A1_OPERATIONALIZATION.operationalization_id
    assert manifest.capability_id == "LEARN-A1"
    assert InterventionManifest.from_payload(manifest.payload()) == manifest


def test_replay_intervention_purity_has_its_first_difference_at_commit():
    full, amputated = _agent(commit=True), _agent(commit=False)
    assert _parameter_hash(full) == _parameter_hash(amputated)
    initial_optimizer_hash = _optimizer_hash(full)
    assert initial_optimizer_hash == _optimizer_hash(amputated)
    assert _non_target_snapshot(full) == _non_target_snapshot(amputated)

    full_events, ablated_events = _learn_once(full, amputated)
    full_learning, ablated_learning = _learning_event(full_events), _learning_event(ablated_events)

    # M2: same proposal up to the causal boundary.
    assert full_learning["loss_total"] == ablated_learning["loss_total"]
    assert full_learning["loss_components"] == ablated_learning["loss_components"]
    assert full_learning["grad_norms"] == ablated_learning["grad_norms"]
    assert full_learning["gradient_hash"] == ablated_learning["gradient_hash"]

    # M3/M4: only the manifest's commit surface diverges directly.
    assert _parameter_hash(full) != _parameter_hash(amputated)
    assert _optimizer_hash(full) != _optimizer_hash(amputated)
    assert _optimizer_hash(amputated) == initial_optimizer_hash
    first_field = _first_parameter_difference(full, amputated)
    assert first_field.split(".", 1)[0] in full.learner._modules
    assert _non_target_snapshot(full) == _non_target_snapshot(amputated)
    assert full_learning["commit_applied"] is True
    assert ablated_learning["commit_applied"] is False
    assert all(parameter.grad is None for module in full.learner._modules.values()
               for parameter in module.parameters())
    assert all(parameter.grad is None for module in amputated.learner._modules.values()
               for parameter in module.parameters())


def test_replay_first_divergence_is_reproducible():
    def signature() -> tuple[str, str, str]:
        full, amputated = _agent(commit=True), _agent(commit=False)
        full_events, ablated_events = _learn_once(full, amputated)
        return (
            _first_parameter_difference(full, amputated),
            _learning_event(full_events)["gradient_hash"],
            _learning_event(ablated_events)["gradient_hash"],
        )

    assert signature() == signature()


def test_suppressed_commit_cannot_leak_stale_gradients_into_the_next_update():
    agent = _agent(commit=False)
    _learn_once(_agent(commit=True), agent)
    assert all(parameter.grad is None for module in agent.learner._modules.values()
               for parameter in module.parameters())
    before = _parameter_hash(agent)
    agent._learning_commit_enabled = True
    observation = _observation()
    agent.perceive(observation)
    action = agent.decide()
    agent.learn(Transition(observation, None, action, Consequence(1.0, []), observation,
                           False, False, 1, SEED))
    assert _parameter_hash(agent) != before
    assert agent.learner.step_count == 2
    assert all(parameter.grad is None for module in agent.learner._modules.values()
               for parameter in module.parameters())


def test_live_causal_twin_has_equal_world_observation_action_before_commit():
    source = WorldScenarioRegistry(".").get("D2").source
    scenario = load_scenario(source)
    first = build_episode_components(scenario, duration_fallback=scenario["duration"], world_seed=SEED)
    second = build_episode_components(scenario, duration_fallback=scenario["duration"], world_seed=SEED)
    full, amputated = _agent(commit=True), _agent(commit=False)
    assert first.world.state.state_hash() == second.world.state.state_hash()
    assert _parameter_hash(full) == _parameter_hash(amputated)
    outcome_full = run_step(first, full, 0, world_seed=SEED, agent_seed=SEED,
                            max_steps=scenario["duration"])
    outcome_ablated = run_step(second, amputated, 0, world_seed=SEED, agent_seed=SEED,
                               max_steps=scenario["duration"])
    assert _hash(outcome_full.observation_t.channels) == _hash(outcome_ablated.observation_t.channels)
    assert outcome_full.action == outcome_ablated.action
    assert outcome_full.consequence.energy_delta == outcome_ablated.consequence.energy_delta
    assert first.world.state.state_hash() == second.world.state.state_hash()
    assert _parameter_hash(full) != _parameter_hash(amputated)


def test_historical_flag_ablation_is_control_flow_confounded():
    full, historical = _agent(commit=True), _agent(commit=True)
    historical._use_online_learning = False
    historical.config["use_online_learning"] = False
    observation = _observation()
    for agent in (full, historical):
        agent.perceive(observation)
    full_action, historical_action = full.decide(), historical.decide()
    assert full_action == historical_action
    full.learn(Transition(observation, None, full_action, Consequence(1.0, []), observation,
                          False, False, 0, SEED))
    historical.learn(Transition(observation, None, historical_action, Consequence(1.0, []), observation,
                                False, False, 0, SEED))
    full_events, historical_events = full.get_trace_events(), historical.get_trace_events()
    assert _learning_event(full_events)["commit_applied"] is True
    assert not any(event.get("op") == "learning_step" for event in historical_events)
    assert full.learner.step_count == 1 and historical.learner.step_count == 0
    assert full._baseline_count == 1 and historical._baseline_count == 0
    assert full.config["use_online_learning"] is not historical.config["use_online_learning"]


def test_non_target_capability_configuration_regression():
    full, amputated = _agent(commit=True), _agent(commit=False)
    assert {key: full.config[key] for key in USE_KEYS} == {key: amputated.config[key] for key in USE_KEYS}
    assert full._state_dim == amputated._state_dim
    assert full._generator.get_state().equal(amputated._generator.get_state())


def test_parameter_surface_includes_every_t1_module_the_learner_can_update():
    def entity_agent(commit: bool):
        RNGManager.set_global_determinism(SEED)
        return create_agent("A4_ADVANCED", {
            **_config(commit=commit), "addressing_mode": "T1_ENTITY",
        }, seed=SEED)

    full, amputated = entity_agent(True), entity_agent(False)
    names = set(full.get_parameters())
    assert {"direction_head.weight", "direction_head.bias", "selector_residual.weight", "selector_residual.bias"} <= names
    assert _parameter_hash(full) == _parameter_hash(amputated)
