"""Execution-plane adapter: exact TrialIntent -> real Terrario episode.

This module does not use sandbox services or evidence-producing code paths.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any, Callable, Mapping

from terrario.core.rng import RNGManager
from terrario.experiment.config import ExperimentConfig
from terrario.experiment.controller import ExperimentController, build_world_state, materialize_scenario
from terrario.world.physics import Physics
from terrario.world.rules import RuleEngine
from terrario.world.scheduler import ChangeScheduler
from terrario.world.state import WorldStateManager
from terrario.world.transition import build_episode_components
from terrario.observer.logger import ScientificObserver
from terrario.agent.scientific import scientific_state, scientific_transport_projection
from terrario.lab.persistence.canonical import content_hash

SCIENTIFIC_FRAME_SCHEMA = "terrario.scientific-frame/v1"


@dataclass(frozen=True)
class ScientificTrialIdentity:
    execution_id: str; trial_intent_id: str; attempt_id: str; plan_hash: str; preregistration_root_hash: str
    software_identity: str; scenario_identity: str; agent_identity: str; world_seed: int; agent_seed: int
    agent_config: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = "terrario.scientific-trial-identity/v1"
    def __post_init__(self):
        if any(not isinstance(key, str) or not key.startswith("use_") or not isinstance(value, bool)
               for key, value in self.agent_config.items()):
            raise ValueError("scientific trial identity requires explicit boolean use_* agent config")
        object.__setattr__(self, "agent_config", MappingProxyType(dict(self.agent_config)))
    @property
    def identity_hash(self) -> str: return content_hash(self)


@dataclass(frozen=True)
class ScientificFrame:
    identity: ScientificTrialIdentity; tick: int; simulation_time: float; world_revision: int; frame_sequence: int
    world_truth: Mapping[str, Any]; agent_observation: Mapping[str, Any]; observer_view: Mapping[str, Any]
    runtime_state: str; trace_cursor: int; schema_version: str = SCIENTIFIC_FRAME_SCHEMA
    # Additive: historical v1 frames legitimately omit this field.
    cognitive_state: Mapping[str, Any] | None = None
    def __post_init__(self):
        if self.tick < 0 or self.frame_sequence < 0: raise ValueError("scientific frame tick/sequence must be non-negative")
        if not all(isinstance(x, Mapping) for x in (self.world_truth, self.agent_observation, self.observer_view)): raise ValueError("scientific frame requires all atomic views")
        if self.cognitive_state is not None and not isinstance(self.cognitive_state, Mapping): raise ValueError("scientific frame cognitive state must be a mapping or absent")


def scientific_trial_identity_payload(identity: ScientificTrialIdentity) -> dict[str, Any]:
    """Canonicalizable identity projection; never leak a mutable config handle."""
    return {
        "execution_id": identity.execution_id, "trial_intent_id": identity.trial_intent_id,
        "attempt_id": identity.attempt_id, "plan_hash": identity.plan_hash,
        "preregistration_root_hash": identity.preregistration_root_hash,
        "software_identity": identity.software_identity, "scenario_identity": identity.scenario_identity,
        "agent_identity": identity.agent_identity, "world_seed": identity.world_seed,
        "agent_seed": identity.agent_seed, "agent_config": dict(identity.agent_config),
        "schema_version": identity.schema_version,
    }


def scientific_frame_payload(frame: ScientificFrame) -> dict[str, Any]:
    """Explicit durable frame projection compatible with immutable contracts."""
    return {
        "identity": scientific_trial_identity_payload(frame.identity), "tick": frame.tick,
        "simulation_time": frame.simulation_time, "world_revision": frame.world_revision,
        "frame_sequence": frame.frame_sequence, "world_truth": dict(frame.world_truth),
        "agent_observation": dict(frame.agent_observation), "observer_view": dict(frame.observer_view),
        "runtime_state": frame.runtime_state, "trace_cursor": frame.trace_cursor,
        "schema_version": frame.schema_version,
        "cognitive_state": None if frame.cognitive_state is None else dict(frame.cognitive_state),
    }


def run_materialized_trial(root: Path, identity: ScientificTrialIdentity, *, scenario_path: Path,
                           observer_profile: str, step_limit: int,
                           frame_sink: Callable[[ScientificFrame], None] | None = None) -> Mapping[str, Any]:
    """Run one sealed intent through the real controller and public engine loop."""
    if not scenario_path.is_file(): raise ValueError("TRIAL_MATERIALIZATION_FAILED: scenario path missing")
    config = ExperimentConfig(identity.execution_id, None, str(scenario_path), [identity.agent_identity], dict(identity.agent_config), [identity.world_seed], 1,
        int(step_limit), observer_profile if observer_profile in ScientificObserver.VALID_MODES else "scientific_standard", max(1, min(int(step_limit), 100)), str(root), "cpu")
    controller = ExperimentController(config); scenario = materialize_scenario(controller.scenario, identity.world_seed); scenario["world_seed"] = identity.world_seed
    RNGManager.set_global_determinism(identity.agent_seed)
    components = build_episode_components(scenario, duration_fallback=config.max_steps_per_episode)
    world, rules, scheduler = components.world, components.rules, components.scheduler
    agent = controller._create_agent(identity.agent_identity, identity.agent_seed, scenario)
    observer = ScientificObserver(str(root / "observer"), config.observer_mode, {"scientific_trial_identity": scientific_trial_identity_payload(identity), "plan_hash": identity.plan_hash, "preregistration_root_hash": identity.preregistration_root_hash})
    observation_faults: list[dict[str, Any]] = []
    try:
        if frame_sink:
            try:
                frame_sink(_frame(identity, world, scenario, agent, 0, 0, "RUNNING", 0))
            except Exception as exc:
                observation_faults.append({"kind": "FRAME_SINK_FAILURE", "tick": 0,
                                           "error_type": type(exc).__name__, "message": str(exc)})
        def capture(step_frame):
            if frame_sink:
                frame_sink(_captured_frame(identity, step_frame, int(step_frame["tick"]), step_frame["runtime_state"]))
        episode = controller.run_episode(agent, world, Physics(), rules, scheduler, observer, identity.agent_seed,
            scenario=scenario, phase="scientific_execution", frame_sink=capture if frame_sink else None)
    finally: observer.close()
    observation_faults.extend(episode["observation_faults"])
    return {"identity": scientific_trial_identity_payload(identity), "episode": episode, "config_hash": config.config_hash(),
            "observer_dir": str(root / "observer"), "observation_faults": observation_faults}


def _frame(identity, world, scenario, agent, tick, sequence, state, cursor):
    observation = world.get_observation(0, scenario.get("view_radius", 2), scenario.get("num_channels", 4)); truth = world.serialize()
    agent_view = {"channels": observation.channels.tolist(), "mask": observation.mask.tolist(), "agent_energy": observation.agent_energy, "time_fraction": observation.time_fraction}
    return ScientificFrame(identity, tick, float(truth["time"]), int(truth.get("rules_version", 0)), sequence, truth, agent_view, {"profile": "SCIENTIFIC", "agent_identity": dict(agent.agent_identity)}, state, cursor, cognitive_state=scientific_transport_projection(scientific_state(agent)))


def _captured_frame(identity, captured, sequence, state):
    """Build a frame from the transition-captured snapshot, never from replay."""
    return ScientificFrame(identity, int(captured["tick"]), float(captured["simulation_time"]), int(captured["world_revision"]),
        sequence, captured["world_truth"], captured["agent_observation"], captured["observer_view"], state,
        int(captured["trace_cursor"]), cognitive_state=captured["scientific_state"])
