"""Experiment controller with an explicit agent-to-evidence circuit."""

from __future__ import annotations

import json
import os
import subprocess
from copy import deepcopy
from typing import Any, Callable, Mapping

import numpy as np
import yaml

from terrario.core.contracts import Transition
from terrario.core.rng import RNGManager
from terrario.core.types import Action, ActionType, AgentState, Consequence, ObjectSpec, Position, WorldState
from terrario.experiment.config import ExperimentConfig
from terrario.experiment.metrics import MetricsCalculator
from terrario.observer.logger import ScientificObserver
from terrario.observer.windows import ForensicWindowPolicy
from terrario.world.physics import Physics
from terrario.world.rules import RuleEngine
from terrario.world.scheduler import ChangeScheduler
from terrario.world.state import WorldStateManager
from terrario.world.transition import (
    EpisodeComponents, build_episode_components,
    build_world_state as _build_world_state, find_target, run_step)
from terrario.world.opportunities import OpportunityLifecycle
from terrario.agent.scientific import scientific_state as build_scientific_state, scientific_transport_projection


def load_scenario(path: str) -> dict[str, Any]:
    with open(path) as f:
        data = yaml.safe_load(f)
    return data.get("scenario", data)


def materialize_scenario(scenario: dict[str, Any], world_seed: int) -> dict[str, Any]:
    """Materialize procedural layout and hidden schedule deterministically."""
    resolved = deepcopy(scenario)
    layout = resolved.get("procedural_layout")
    if not layout:
        return resolved
    rng = np.random.default_rng(world_seed)
    grid_w, grid_h = resolved["grid_size"]
    start = tuple(resolved.get("agent_start", {}).get("pos", [grid_h // 2, grid_w // 2]))
    margin = int(layout.get("placement_margin", 1))
    candidates = [
        (x, y) for x in range(margin, grid_h - margin) for y in range(margin, grid_w - margin)
        if (x, y) != start
    ]
    templates = layout["class_templates"]
    class_names = [name for name, template in templates.items() for _ in range(template["count"])]
    if len(class_names) > len(candidates):
        raise ValueError("Procedural layout requests more objects than valid positions")
    positions = rng.choice(len(candidates), size=len(class_names), replace=False)
    rng.shuffle(class_names)
    resolved["objects"] = [
        {
            "pos": list(candidates[position_index]),
            "channels": templates[class_name]["channels"],
            "movable": False,
            "energy_value": 0.0,
            "properties": {"causal_class": class_name},
        }
        for class_name, position_index in zip(class_names, positions)
    ]
    jitter = int(resolved.get("change_jitter", 0))
    for change in resolved.get("changes", []):
        change["at_step"] = int(change["at_step"]) + int(rng.integers(-jitter, jitter + 1))
    resolved["world_seed"] = world_seed
    return resolved


def _observer_decision_trace(agent_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Project decision facts required by the observer-only metric contract."""
    return [
        {key: event[key] for key in ("op", "step", "action_int") if key in event}
        for event in agent_events if event.get("op") == "decide"
    ]


def _observer_planner_proposal_trace(agent_events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Project the declared plan proposal contract without exposing agent state.

    The retained fields are all produced by the planner at decision time.  In
    particular, this projection never adds a target, oracle action, world
    truth, or post-hoc evaluator label.
    """
    fields = ("op", "horizon", "num_candidates", "best_action", "best_score", "rollouts")
    return [
        {key: event[key] for key in fields if key in event}
        for event in agent_events if event.get("op") == "plan"
    ]


#: Re-exported from `world/transition.py`, where the implementation now lives.
#: Thirty callers import it from here; the name stays so none of them change.
build_world_state = _build_world_state


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
        world_seed = seed
        agent_seed = seed + 1_000_003
        scenario = materialize_scenario(self.scenario, world_seed)
        RNGManager.set_global_determinism(agent_seed)
        components = build_episode_components(
            scenario, duration_fallback=self.config.max_steps_per_episode)
        world_mgr, rule_engine, scheduler = (
            components.world, components.rules, components.scheduler)
        agent = self._create_agent(agent_type, agent_seed, scenario)
        run_dir = os.path.join(
            self.config.output_dir, "observations", self.config.experiment_id,
            agent_type, f"seed_{seed:08d}", f"episode_{episode_idx:04d}",
        )
        observer = ScientificObserver(run_dir, self.config.observer_mode, {
            "experiment_id": self.config.experiment_id,
            "hypothesis_id": self.config.hypothesis.hypothesis_id if self.config.hypothesis else None,
            "seed": seed, "world_seed": world_seed, "agent_seed": agent_seed,
            "config_hash": self.config.config_hash(), "code_hash": self._code_hash(),
            "device": self.config.device, "agent_identity": agent.agent_identity,
        })
        observer.set_episode(episode_idx)
        try:
            episode_data = self.run_episode(agent, world_mgr, Physics(), rule_engine, scheduler, observer, agent_seed, scenario=scenario)
        finally:
            observer.close()
        change_step = next(iter(scenario.get("changes", [])), {}).get("at_step")
        return {
            "agent_type": agent_type, "seed": seed, "world_seed": world_seed, "agent_seed": agent_seed, "episode_idx": episode_idx,
            "metrics": MetricsCalculator.compute_all(episode_data, change_step=change_step),
            "num_steps": episode_data["num_steps"], "final_energy": episode_data["final_energy"],
            "agent_identity": agent.agent_identity, "observer_run_dir": run_dir,
        }

    def run_episode(
        self, agent: Any, world_state_mgr: WorldStateManager, physics: Physics,
        rule_engine: RuleEngine, scheduler: ChangeScheduler,
        observer: ScientificObserver, seed: int, scenario: dict[str, Any] | None = None,
        learning_enabled: bool = True, phase: str = "training",
        frame_sink: Callable[[Mapping[str, Any]], None] | None = None,
    ) -> dict[str, Any]:
        active_scenario = scenario or self.scenario
        max_steps = min(self.config.max_steps_per_episode, active_scenario.get("duration", 500))
        view_radius = active_scenario.get("view_radius", 2)
        num_channels = active_scenario.get("num_channels", 4)
        energy_history: list[float] = []
        action_history: list[int] = []
        step_traces: list[dict[str, Any]] = []
        observation_faults: list[dict[str, Any]] = []
        change_step = next(iter(active_scenario.get("changes", [])), {}).get("at_step")
        forensic_policy = ForensicWindowPolicy(change_step) if change_step is not None else None
        lifecycle = OpportunityLifecycle(active_scenario.get("opportunity_lifecycle", {}), active_scenario.get("world_seed", seed))
        lifecycle.register_initial(world_state_mgr)
        # `run_episode` recibe mundo, reglas, calendario y física inyectados --
        # tres tests los construyen ellos mismos -- así que los componentes del
        # paso se arman a partir de lo recibido en vez de reconstruirse.
        step_components = EpisodeComponents(
            world=world_state_mgr, rules=rule_engine, scheduler=scheduler,
            physics=physics, scenario=active_scenario, lifecycle=lifecycle)

        for step in range(max_steps):
            agent_state = world_state_mgr._mutable_state().agents.get(0)
            if agent_state is None or not agent_state.alive:
                break
            # La secuencia la ejecuta `run_step`, la misma que ejecuta el banco.
            # Lo que queda aquí es la instrumentación científica -- anotaciones
            # causales, geometría, ventana forense, sumidero de frames,
            # checkpoints -- que es lo que sí puede diferir entre superficies.
            before_parameters = agent.get_parameters() if observer.mode == "forensic_full" else None
            outcome = run_step(
                step_components, agent, step,
                world_seed=active_scenario.get("world_seed", seed), agent_seed=seed,
                max_steps=max_steps, learning_enabled=learning_enabled)
            observation_t, action_t = outcome.observation_t, outcome.action
            change_events, respawn_events = outcome.change_events, outcome.respawn_events
            target, target_before = outcome.target, outcome.target_before
            energy_delta, lifecycle_event = outcome.energy_delta, outcome.lifecycle_event
            consequence, observation_t1 = outcome.consequence, outcome.observation_t1
            terminated, truncated = outcome.terminated, outcome.truncated
            transition = outcome.transition
            scientific_snapshot = build_scientific_state(agent)
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
                "prediction_error": getattr(agent, "last_prediction_error", 0.0),
                "state_hash": truth.state_hash(),
                "rule_changes": [{"step": e.step, "old_version": e.old_version, "new_version": e.new_version} for e in change_events],
            }
            observer_annotations = self._causal_annotations(target, action_t, energy_delta, truth.rules_version)
            observer_annotations["geometry"] = lifecycle.geometry(world_state_mgr, view_radius=view_radius)
            observer_annotations["interaction_target_distance"] = (
                abs(target_before.pos.x - agent_state.pos.x) + abs(target_before.pos.y - agent_state.pos.y)
                if target_before is not None else None
            )
            observer_annotations["opportunity_event"] = lifecycle_event.__dict__ if lifecycle_event else None
            observer_annotations["respawn_events"] = [event.__dict__ for event in respawn_events]
            observer_annotations["phase"] = phase
            if forensic_policy is not None:
                observer_annotations["forensic_window"] = forensic_policy.label(step)
            trace["causal_interaction"] = observer_annotations
            prediction_error = scientific_snapshot["prediction_error"]
            trace["prediction_error"] = prediction_error if isinstance(prediction_error, (int, float)) else None
            trace["predictor_available"] = trace["prediction_error"] is not None
            step_traces.append(trace)
            observer.log_step(step, truth.clone(), agent, observation_t, action_t, consequence, {})
            agent_events = agent.get_trace_events()
            trace["numerical_events"] = [
                event for event in agent_events if event.get("op") == "learning_skipped_nonfinite"
            ]
            observer.log_transition(
                transition, world_state_mgr.observer_snapshot(step), agent.agent_identity,
                agent.get_internal_state(), agent_events, parameter_deltas, observer_annotations, scientific_snapshot,
            )
            # The optional sink is observer-only.  It receives state captured in
            # this exact transition, never re-reads mutable agent internals.
            if frame_sink is not None:
                try:
                    captured_frame = {
                        "tick": step + 1,
                        "simulation_time": float(world_state_mgr.serialize()["time"]),
                        "world_revision": int(truth.rules_version),
                        "world_truth": world_state_mgr.serialize(),
                        "agent_observation": {
                            "channels": observation_t1.channels.tolist(), "mask": observation_t1.mask.tolist(),
                            "agent_energy": observation_t1.agent_energy, "time_fraction": observation_t1.time_fraction,
                        },
                        # Captured after the agent acts and never routed back
                        # into its observation.  This is a narrow scientific
                        # projection, not a copy of mutable internal state.
                        "observer_view": {
                            "events": list(consequence.observer_events), "causal_interaction": observer_annotations,
                            "decision_trace": _observer_decision_trace(agent_events),
                            "planner_proposal_trace": _observer_planner_proposal_trace(agent_events),
                        },
                        "scientific_state": scientific_transport_projection(scientific_snapshot),
                        "trace_cursor": step,
                        "runtime_state": "COMPLETED" if consequence.done else "RUNNING",
                    }
                    frame_sink(captured_frame)
                except Exception as exc:
                    observation_faults.append({"kind": "FRAME_SINK_FAILURE", "tick": step + 1,
                                               "error_type": type(exc).__name__, "message": str(exc)})
            if observer.mode == "forensic_full" and (forensic_policy is None or forensic_policy.should_capture(step)):
                observer.capture_forensic(agent, step, parameter_deltas or {})
            if self.config.checkpoint_every > 0 and (step + 1) % self.config.checkpoint_every == 0:
                observer.checkpoint(agent, step + 1, {"world_snapshot": world_state_mgr.serialize()})
            if terminated:
                break

        return {
            "energy_history": energy_history, "actions": action_history, "traces": step_traces,
            "final_energy": world_state_mgr._mutable_state().agents[0].energy,
            "num_steps": len(energy_history), "compute_cost": getattr(agent, "compute_cost", 1.0),
            "opportunity_events": [event.__dict__ for event in lifecycle.events],
            "opportunity_records": [record.__dict__ for record in lifecycle.records.values()],
            "observation_faults": observation_faults,
        }

    def _find_target(self, world_mgr: WorldStateManager, agent_id: int, action: Action) -> ObjectSpec | None:
        """Delegates to the shared semantics.

        Kept as a method because `CausalRuntime.step` calls it across packages
        to avoid writing a fourth copy of the same resolution.
        """
        return find_target(world_mgr, agent_id, action)

    def _create_agent(self, agent_type: str, seed: int, scenario: dict[str, Any] | None = None) -> Any:
        from terrario.agent.agents import create_agent
        active_scenario = scenario or self.scenario
        return create_agent(agent_type, {
            **self.config.agent_config, "num_channels": active_scenario.get("num_channels", 4),
            "view_size": 2 * active_scenario.get("view_radius", 2) + 1,
        }, seed=seed, device=self.config.device)

    @staticmethod
    def _causal_annotations(target: ObjectSpec | None, action: Action, energy_delta: float, rules_version: int) -> dict[str, Any]:
        """Observer-only causal labels; this dict is never passed to the agent."""
        informative = target is not None and action.action_type == ActionType.CONSUME
        return {
            "informative": informative,
            "perceptual_class": target.properties.get("causal_class") if target else None,
            "hidden_causal_class": target.properties.get("causal_class") if target else None,
            "action": action.to_int(),
            "actual_consequence": energy_delta,
            "causally_appropriate": informative and energy_delta > 0.0,
            "rule_version": rules_version,
        }

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
