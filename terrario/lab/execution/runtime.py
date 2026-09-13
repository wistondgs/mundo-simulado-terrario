"""Execution-plane adapter: exact TrialIntent -> real Terrario episode.

This module does not use sandbox services or evidence-producing code paths.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping

from terrario.core.rng import RNGManager
from terrario.experiment.config import ExperimentConfig
from terrario.experiment.controller import ExperimentController, build_world_state, materialize_scenario
from terrario.world.physics import Physics
from terrario.world.rules import RuleEngine
from terrario.world.scheduler import ChangeScheduler
from terrario.world.state import WorldStateManager
from terrario.observer.logger import ScientificObserver
from terrario.lab.persistence.canonical import content_hash

SCIENTIFIC_FRAME_SCHEMA = "terrario.scientific-frame/v1"


@dataclass(frozen=True)
class ScientificTrialIdentity:
    execution_id: str; trial_intent_id: str; attempt_id: str; plan_hash: str; preregistration_root_hash: str
    software_identity: str; scenario_identity: str; agent_identity: str; world_seed: int; agent_seed: int
    schema_version: str = "terrario.scientific-trial-identity/v1"
    @property
    def identity_hash(self) -> str: return content_hash(self)


@dataclass(frozen=True)
class ScientificFrame:
    identity: ScientificTrialIdentity; tick: int; simulation_time: float; world_revision: int; frame_sequence: int
    world_truth: Mapping[str, Any]; agent_observation: Mapping[str, Any]; observer_view: Mapping[str, Any]
    runtime_state: str; trace_cursor: int; schema_version: str = SCIENTIFIC_FRAME_SCHEMA
    def __post_init__(self):
        if self.tick < 0 or self.frame_sequence < 0: raise ValueError("scientific frame tick/sequence must be non-negative")
        if not all(isinstance(x, Mapping) for x in (self.world_truth, self.agent_observation, self.observer_view)): raise ValueError("scientific frame requires all atomic views")


def run_materialized_trial(root: Path, identity: ScientificTrialIdentity, *, scenario_path: Path,
                           observer_profile: str, step_limit: int,
                           frame_sink: Callable[[ScientificFrame], None] | None = None) -> Mapping[str, Any]:
    """Run one sealed intent through the real controller and public engine loop."""
    if not scenario_path.is_file(): raise ValueError("TRIAL_MATERIALIZATION_FAILED: scenario path missing")
    config = ExperimentConfig(identity.execution_id, None, str(scenario_path), [identity.agent_identity], {}, [identity.world_seed], 1,
        int(step_limit), observer_profile if observer_profile in ScientificObserver.VALID_MODES else "scientific_standard", max(1, min(int(step_limit), 100)), str(root), "cpu")
    controller = ExperimentController(config); scenario = materialize_scenario(controller.scenario, identity.world_seed); scenario["world_seed"] = identity.world_seed
    RNGManager.set_global_determinism(identity.agent_seed)
    world = WorldStateManager(build_world_state(scenario), scenario.get("duration", config.max_steps_per_episode), scenario.get("max_energy", 100.0), scenario.get("step_energy_cost", 0.0), scenario.get("expose_time_fraction", True))
    rules = RuleEngine(); rules.load_rules(scenario.get("rules", {})); world.set_rules_version(rules.version)
    scheduler = ChangeScheduler(scenario.get("changes", []), rules); agent = controller._create_agent(identity.agent_identity, identity.agent_seed, scenario)
    observer = ScientificObserver(str(root / "observer"), config.observer_mode, {"scientific_trial_identity": identity.__dict__, "plan_hash": identity.plan_hash, "preregistration_root_hash": identity.preregistration_root_hash})
    try:
        if frame_sink: frame_sink(_frame(identity, world, scenario, agent, 0, 0, "RUNNING", 0))
        episode = controller.run_episode(agent, world, Physics(), rules, scheduler, observer, identity.agent_seed, scenario=scenario, phase="scientific_execution")
        if frame_sink:
            for sequence, trace in enumerate(episode["traces"], 1): frame_sink(_trace_frame(identity, trace, sequence, "COMPLETED"))
    finally: observer.close()
    return {"identity": identity.__dict__, "episode": episode, "config_hash": config.config_hash(), "observer_dir": str(root / "observer")}


def _frame(identity, world, scenario, agent, tick, sequence, state, cursor):
    observation = world.get_observation(0, scenario.get("view_radius", 2), scenario.get("num_channels", 4)); truth = world.serialize()
    agent_view = {"channels": observation.channels.tolist(), "mask": observation.mask.tolist(), "agent_energy": observation.agent_energy, "time_fraction": observation.time_fraction}
    return ScientificFrame(identity, tick, float(truth["time"]), int(truth.get("rules_version", 0)), sequence, truth, agent_view, {"profile": "SCIENTIFIC", "agent_identity": dict(agent.agent_identity)}, state, cursor)


def _trace_frame(identity, trace, sequence, state):
    return ScientificFrame(identity, int(trace["step"]) + 1, float(int(trace["step"]) + 1), 0, sequence, {"state_hash": trace["state_hash"], "energy": trace["energy"]}, {"status": "NOT_RETAINED_IN_RAW_STEP_TRACE"}, {"events": trace["observer_events"], "causal_interaction": trace["causal_interaction"]}, state, sequence)
