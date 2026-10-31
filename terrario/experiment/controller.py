"""Experiment controller with an explicit agent-to-evidence circuit."""

from __future__ import annotations

import json
import os
import subprocess
from typing import Any

import numpy as np
import yaml

from terrario.core.contracts import Transition
from terrario.core.rng import RNGManager
from terrario.core.types import Action, ActionType, AgentState, Consequence, ObjectSpec, Position, WorldState
from terrario.experiment.config import ExperimentConfig
from terrario.experiment.metrics import MetricsCalculator
from terrario.observer.logger import ScientificObserver
from terrario.world.physics import Physics
from terrario.world.rules import RuleEngine
from terrario.world.scheduler import ChangeScheduler
from terrario.world.state import WorldStateManager


def load_scenario(path: str) -> dict[str, Any]:
    with open(path) as f:
        data = yaml.safe_load(f)
    return data.get("scenario", data)


def build_world_state(scenario: dict[str, Any]) -> WorldState:
    grid_w, grid_h = scenario["grid_size"]
    occupancy = np.zeros((grid_h, grid_w), dtype=np.int32)
    objects: dict[int, ObjectSpec] = {}
    for i, obj_data in enumerate(scenario.get("objects", [])):
        pos = Position(*obj_data["pos"])
        objects[i] = ObjectSpec(
            object_id=i, pos=pos, channels=np.array(obj_data["channels"], dtype=np.float32),
            movable=obj_data.get("movable", True), energy_value=obj_data.get("energy_value", 0.0),
        )
        occupancy[pos.x, pos.y] += 1
    start = scenario.get("agent_start", {"pos": [5, 5], "energy": 100.0})
    agent_pos = Position(*start["pos"])
    occupancy[agent_pos.x, agent_pos.y] += 1
    return WorldState(
        grid_width=grid_w, grid_height=grid_h, time=0, objects=objects,
        agents={0: AgentState(0, agent_pos, start.get("energy", 100.0))},
        rules_version=0, occupancy=occupancy,
    )


class ExperimentController:
    """Runs episodes while preserving the complete scientific transition."""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.scenario = load_scenario(config.scenario_path)
        self.results: dict[str, Any] = {
            "experiment_id": config.experiment_id,
            "config_hash": config.config_hash(), "code_hash": self._code_hash(), "episodes": [],
        }

    def run(self) -> dict:
        for seed in self.config.seeds:
            for episode_idx in range(self.config.num_episodes):
                for agent_type in self.config.agent_types:
                    self.results["episodes"].append(self._run_single_episode(agent_type, seed, episode_idx))
        self._save_results()
        return self.results

    def _run_single_episode(self, agent_type: str, seed: int, episode_idx: int) -> dict:
        RNGManager.set_global_determinism(seed)
        world_mgr = WorldStateManager(
            build_world_state(self.scenario),
            self.scenario.get("duration", self.config.max_steps_per_episode), 100.0,
        )
        rule_engine = RuleEngine()
        rule_engine.load_rules(self.scenario.get("rules", {}))
        world_mgr.set_rules_version(rule_engine.version)
        scheduler = ChangeScheduler(self.scenario.get("changes", []), rule_engine)
        agent = self._create_agent(agent_type, seed)
        run_dir = os.path.join(
            self.config.output_dir, "observations", self.config.experiment_id,
            agent_type, f"seed_{seed:08d}", f"episode_{episode_idx:04d}",
        )
        observer = ScientificObserver(run_dir, self.config.observer_mode, {
            "experiment_id": self.config.experiment_id,
            "hypothesis_id": self.config.hypothesis.hypothesis_id if self.config.hypothesis else None,
            "seed": seed, "config_hash": self.config.config_hash(), "code_hash": self._code_hash(),
            "device": self.config.device, "agent_identity": agent.agent_identity,
        })
        observer.set_episode(episode_idx)
        try:
            episode_data = self.run_episode(agent, world_mgr, Physics(), rule_engine, scheduler, observer, seed)
        finally:
            observer.close()
        change_step = next(iter(self.scenario.get("changes", [])), {}).get("at_step")
        return {
            "agent_type": agent_type, "seed": seed, "episode_idx": episode_idx,
            "metrics": MetricsCalculator.compute_all(episode_data, change_step=change_step),
            "num_steps": episode_data["num_steps"], "final_energy": episode_data["final_energy"],
            "agent_identity": agent.agent_identity, "observer_run_dir": run_dir,
        }

    def run_episode(
        self, agent: Any, world_state_mgr: WorldStateManager, physics: Physics,
        rule_engine: RuleEngine, scheduler: ChangeScheduler,
        observer: ScientificObserver, seed: int,
    ) -> dict[str, Any]:
        max_steps = min(self.config.max_steps_per_episode, self.scenario.get("duration", 500))
        view_radius = self.scenario.get("view_radius", 2)
        num_channels = self.scenario.get("num_channels", 4)
        energy_history: list[float] = []
        action_history: list[int] = []
        step_traces: list[dict[str, Any]] = []

        for step in range(max_steps):
            agent_state = world_state_mgr._mutable_state().agents.get(0)
            if agent_state is None or not agent_state.alive:
                break
            observation_t = world_state_mgr.get_observation(0, view_radius, num_channels)
            agent.perceive(observation_t)
            action_t = agent.decide()
            change_events = scheduler.check(world_state_mgr, step=step)  # PRE_STEP convention
            consequences = physics.step(world_state_mgr, {0: action_t}, RNGManager(seed + step))
            consequence = consequences.get(0, Consequence(energy_delta=0.0, events=[]))
            target = self._find_target(world_state_mgr, 0, action_t)
            # The rule engine may only see the target that Physics accepted.
            # In particular, an explicit remote target must not receive hidden
            # rule effects after Physics rejected the consume request.
            accepted_target = (
                target is not None
                and f"consume_pending_obj_{target.object_id}" in consequence.observer_events
            )
            effects = rule_engine.evaluate(world_state_mgr, 0, action_t, target if accepted_target else None)
            energy_delta = rule_engine.apply_effects(world_state_mgr, 0, target.object_id, effects) if accepted_target else 0.0
            consequence.energy_delta = energy_delta
            observation_t1 = world_state_mgr.get_observation(0, view_radius, num_channels)
            terminated = not world_state_mgr._mutable_state().agents[0].alive
            truncated = step + 1 >= max_steps
            consequence.new_observation = observation_t1
            consequence.done = terminated or truncated
            transition = Transition(
                observation_t, str(agent.get_internal_state()), action_t, consequence,
                observation_t1, terminated, truncated, step, seed,
            )
            before_parameters = agent.get_parameters() if observer.mode == "forensic_full" else None
            agent.learn(transition)
            parameter_deltas = None
            if before_parameters is not None:
                after_parameters = agent.get_parameters()
                parameter_deltas = {
                    name: float((after_parameters[name] - value).norm().item())
                    for name, value in before_parameters.items() if name in after_parameters
                }

            truth = world_state_mgr._mutable_state()
            energy_history.append(truth.agents[0].energy)
            action_history.append(action_t.to_int())
            trace = {
                "step": step, "action": action_t.to_int(), "energy": truth.agents[0].energy,
                "events": consequence.events, "observer_events": consequence.observer_events,
                "prediction_error": getattr(agent, "last_prediction_error", None),
                "prediction_measurement_status": getattr(agent, "prediction_measurement_status", "NOT_MEASURED"),
                "state_hash": truth.state_hash(),
                "rule_changes": [{"step": e.step, "old_version": e.old_version, "new_version": e.new_version} for e in change_events],
            }
            step_traces.append(trace)
            observer.log_step(step, truth.clone(), agent, observation_t, action_t, consequence, {})
            observer.log_transition(
                transition, world_state_mgr.observer_snapshot(step), agent.agent_identity,
                agent.get_internal_state(), agent.get_trace_events(), parameter_deltas,
            )
            if observer.mode == "forensic_full":
                observer.capture_forensic(agent, step, parameter_deltas or {})
            if self.config.checkpoint_every > 0 and (step + 1) % self.config.checkpoint_every == 0:
                observer.checkpoint(agent, step + 1, {"world_snapshot": world_state_mgr.serialize()})
            if terminated:
                break

        return {
            "energy_history": energy_history, "actions": action_history, "traces": step_traces,
            "final_energy": world_state_mgr._mutable_state().agents[0].energy,
            "num_steps": len(energy_history), "compute_cost": getattr(agent, "compute_cost", 1.0),
        }

    def _find_target(self, world_mgr: WorldStateManager, agent_id: int, action: Action) -> ObjectSpec | None:
        if action.action_type != ActionType.CONSUME:
            return None
        truth = world_mgr._mutable_state()
        agent = truth.agents[agent_id]
        if action.target_id >= 0:
            return truth.objects.get(action.target_id)
        from terrario.core.types import DIRECTION_DELTA
        position = agent.pos + DIRECTION_DELTA[action.direction]
        return next((obj for obj in truth.objects.values() if obj.pos == position), None)

    def _create_agent(self, agent_type: str, seed: int) -> Any:
        from terrario.agent.agents import create_agent
        return create_agent(agent_type, {
            **self.config.agent_config, "num_channels": self.scenario.get("num_channels", 4),
            "view_size": 2 * self.scenario.get("view_radius", 2) + 1,
        }, seed=seed, device=self.config.device)

    def _save_results(self) -> None:
        os.makedirs(self.config.output_dir, exist_ok=True)
        path = os.path.join(self.config.output_dir, f"{self.config.experiment_id}_results.json")
        with open(path, "w") as f:
            json.dump(self.results, f, indent=2, default=lambda x: float(x) if isinstance(x, (np.floating, np.integer)) else str(x))

    @staticmethod
    def _code_hash() -> str:
        try:
            return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
        except (OSError, subprocess.CalledProcessError):
            return "unavailable"
