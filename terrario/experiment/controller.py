"""Experiment controller — runs episodes and collects data."""

from __future__ import annotations

import json
import os
import time
from typing import Any

import numpy as np
import yaml

from terrario.core.rng import RNGManager
from terrario.core.types import (
    Action,
    ActionType,
    AgentState,
    Consequence,
    Direction,
    ObjectSpec,
    Position,
    WorldState,
)
from terrario.experiment.config import ExperimentConfig
from terrario.experiment.metrics import MetricsCalculator
from terrario.world.physics import Physics
from terrario.world.rules import RuleEngine
from terrario.world.scheduler import ChangeScheduler
from terrario.world.state import WorldStateManager


def load_scenario(path: str) -> dict[str, Any]:
    """Load a scenario YAML file and return the scenario dict."""
    with open(path) as f:
        data = yaml.safe_load(f)
    return data.get("scenario", data)


def build_world_state(scenario: dict[str, Any]) -> WorldState:
    """Construct a WorldState from a scenario specification."""
    grid_w, grid_h = scenario["grid_size"]
    occupancy = np.zeros((grid_h, grid_w), dtype=np.int32)

    objects: dict[int, ObjectSpec] = {}
    for i, obj_data in enumerate(scenario.get("objects", [])):
        pos = Position(obj_data["pos"][0], obj_data["pos"][1])
        channels = np.array(obj_data["channels"], dtype=np.float32)
        obj = ObjectSpec(
            object_id=i,
            pos=pos,
            channels=channels,
            movable=obj_data.get("movable", True),
            energy_value=obj_data.get("energy_value", 0.0),
        )
        objects[i] = obj
        occupancy[pos.x, pos.y] += 1

    agent_start = scenario.get("agent_start", {"pos": [5, 5], "energy": 100.0})
    agent_pos = Position(agent_start["pos"][0], agent_start["pos"][1])
    agents: dict[int, AgentState] = {
        0: AgentState(
            agent_id=0,
            pos=agent_pos,
            energy=agent_start.get("energy", 100.0),
        )
    }
    occupancy[agent_pos.x, agent_pos.y] += 1

    return WorldState(
        grid_width=grid_w,
        grid_height=grid_h,
        time=0,
        objects=objects,
        agents=agents,
        rules_version=0,
        occupancy=occupancy,
    )


class ExperimentController:
    """Runs a single experiment: episodes × seeds × agent types."""

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.scenario = load_scenario(config.scenario_path)
        self.results: dict[str, Any] = {
            "experiment_id": config.experiment_id,
            "config_hash": config.config_hash(),
            "episodes": [],
        }

    def run(self) -> dict:
        """Run the full experiment. Returns results summary."""
        for seed in self.config.seeds:
            for ep_idx in range(self.config.num_episodes):
                for agent_type in self.config.agent_types:
                    episode_result = self._run_single_episode(
                        agent_type=agent_type,
                        seed=seed,
                        episode_idx=ep_idx,
                    )
                    self.results["episodes"].append(episode_result)

        self._save_results()
        return self.results

    def _run_single_episode(
        self,
        agent_type: str,
        seed: int,
        episode_idx: int,
    ) -> dict:
        """Set up and run one episode, returning metrics."""
        rng = RNGManager(seed)
        RNGManager.set_global_determinism(seed)

        # Build world
        world_state = build_world_state(self.scenario)
        max_duration = self.scenario.get("duration", self.config.max_steps_per_episode)
        max_energy = 100.0
        world_mgr = WorldStateManager(world_state, max_duration, max_energy)

        # Build rule engine
        rule_engine = RuleEngine()
        rules_data = self.scenario.get("rules", {})
        rule_engine.load_rules(rules_data)
        world_mgr.set_rules_version(rule_engine.version)

        # Build change scheduler
        changes = self.scenario.get("changes", [])
        scheduler = ChangeScheduler(changes, rule_engine)

        # Build physics
        physics = Physics()

        # Build agent (simple built-in agents for now)
        agent = self._create_agent(agent_type, seed)

        # Observer placeholder — log steps into a list
        step_logs: list[dict] = []

        # Run episode loop
        episode_data = self.run_episode(
            agent=agent,
            world_state_mgr=world_mgr,
            physics=physics,
            rule_engine=rule_engine,
            scheduler=scheduler,
            observer=step_logs,
            seed=seed,
        )

        # Compute metrics
        change_step = None
        if changes:
            change_step = changes[0].get("at_step")

        metrics = MetricsCalculator.compute_all(episode_data, change_step=change_step)

        return {
            "agent_type": agent_type,
            "seed": seed,
            "episode_idx": episode_idx,
            "metrics": metrics,
            "num_steps": episode_data["num_steps"],
            "final_energy": episode_data["final_energy"],
        }

    def run_episode(
        self,
        agent: Any,
        world_state_mgr: WorldStateManager,
        physics: Physics,
        rule_engine: RuleEngine,
        scheduler: ChangeScheduler,
        observer: list[dict],
        seed: int,
    ) -> dict:
        """Run a single episode. Returns episode data dict."""
        max_steps = min(
            self.config.max_steps_per_episode,
            self.scenario.get("duration", 500),
        )
        view_radius = self.scenario.get("view_radius", 2)
        num_channels = self.scenario.get("num_channels", 4)
        agent_id = 0

        energy_history: list[float] = []
        action_history: list[int] = []
        step_traces: list[dict] = []

        for step in range(max_steps):
            agent_state = world_state_mgr.state.agents.get(agent_id)
            if agent_state is None or not agent_state.alive:
                break

            # Get observation
            obs = world_state_mgr.get_observation(agent_id, view_radius, num_channels)

            # Agent perceives and decides
            agent.perceive(obs)
            action = agent.decide()

            # Physics step
            consequences = physics.step(
                world_state_mgr, {agent_id: action}, RNGManager(seed + step)
            )

            # Determine target object for rule evaluation
            target_obj = self._find_target(world_state_mgr, agent_id, action)

            # Rule evaluation and effects
            rule_effects = rule_engine.evaluate(
                world_state_mgr, agent_id, action, target_obj
            )
            if target_obj is not None:
                energy_from_rules = rule_engine.apply_effects(
                    world_state_mgr, agent_id, target_obj.object_id, rule_effects
                )
            else:
                energy_from_rules = 0.0

            # Check for scheduled rule changes
            change_events = scheduler.check(world_state_mgr)

            # Get consequence for agent
            consequence = consequences.get(agent_id, Consequence(
                energy_delta=energy_from_rules,
                events=[],
            ))
            consequence.energy_delta = energy_from_rules

            # Agent learns
            agent.learn(consequence)

            # Record
            current_energy = world_state_mgr.state.agents[agent_id].energy
            energy_history.append(current_energy)
            action_history.append(action.to_int())

            trace = {
                "step": step,
                "action": action.to_int(),
                "energy": current_energy,
                "events": consequence.events,
                "prediction_error": getattr(agent, "last_prediction_error", 0.0),
                "state_hash": world_state_mgr.state.state_hash(),
            }
            if change_events:
                trace["rule_changes"] = [
                    {"old_version": e.old_version, "new_version": e.new_version}
                    for e in change_events
                ]
            step_traces.append(trace)
            observer.append(trace)

        final_energy = world_state_mgr.state.agents[agent_id].energy

        return {
            "energy_history": energy_history,
            "actions": action_history,
            "traces": step_traces,
            "final_energy": final_energy,
            "num_steps": len(energy_history),
            "compute_cost": getattr(agent, "compute_cost", 1.0),
        }

    def _find_target(
        self,
        world_mgr: WorldStateManager,
        agent_id: int,
        action: Action,
    ) -> ObjectSpec | None:
        """Find the target object for an action (for rule evaluation)."""
        if action.action_type != ActionType.CONSUME:
            return None

        agent = world_mgr.state.agents[agent_id]

        if action.target_id >= 0:
            return world_mgr.state.objects.get(action.target_id)

        # Look in facing direction
        from terrario.core.types import DIRECTION_DELTA
        delta = DIRECTION_DELTA[action.direction]
        target_pos = agent.pos + delta
        for obj in world_mgr.state.objects.values():
            if obj.pos.x == target_pos.x and obj.pos.y == target_pos.y:
                return obj
        return None

    def _create_agent(self, agent_type: str, seed: int) -> Any:
        """Create an agent instance by type name.

        Uses simple built-in implementations. When the full agent module
        is available, this will delegate to the agent factory.
        """
        try:
            from terrario.agent.agents import create_agent
            return create_agent(agent_type, self.config.agent_config, seed)
        except (ImportError, AttributeError):
            return _BuiltinAgent(agent_type, seed)

    def _save_results(self) -> None:
        """Save results to output directory."""
        os.makedirs(self.config.output_dir, exist_ok=True)
        out_path = os.path.join(
            self.config.output_dir,
            f"{self.config.experiment_id}_results.json",
        )
        # Convert numpy types for JSON serialization
        serializable = json.loads(
            json.dumps(self.results, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))
        )
        with open(out_path, "w") as f:
            json.dump(serializable, f, indent=2)


class _BuiltinAgent:
    """Minimal agent for testing when the full agent module isn't available."""

    def __init__(self, agent_type: str, seed: int):
        self.agent_type = agent_type
        self.rng = np.random.default_rng(seed)
        self.last_prediction_error = 0.0
        self.compute_cost = 1.0
        self._obs = None
        self._energy_history: list[float] = []

    def perceive(self, obs: Any) -> None:
        self._obs = obs

    def decide(self) -> Action:
        if self.agent_type == "A0_RANDOM":
            at = ActionType(self.rng.integers(0, len(ActionType)))
            d = Direction(self.rng.integers(0, len(Direction)))
            return Action(action_type=at, direction=d)

        # Simple reactive: move toward highest channel-0 cell
        if self._obs is not None and self._obs.channels.shape[0] > 1:
            ch = self._obs.channels[1]  # first object channel
            mask = self._obs.mask
            visible = ch * mask
            center = visible.shape[0] // 2
            best_val = -1.0
            best_dir = Direction.NONE
            for d, (dx, dy) in [(Direction.UP, (-1, 0)), (Direction.DOWN, (1, 0)),
                                 (Direction.LEFT, (0, -1)), (Direction.RIGHT, (0, 1))]:
                nx, ny = center + dx, center + dy
                if 0 <= nx < visible.shape[0] and 0 <= ny < visible.shape[1]:
                    if visible[nx, ny] > best_val:
                        best_val = visible[nx, ny]
                        best_dir = d
            if best_val > 0.3:
                return Action(action_type=ActionType.CONSUME, direction=best_dir)
            elif best_dir != Direction.NONE:
                return Action(action_type=ActionType.MOVE, direction=best_dir)

        return Action.noop()

    def learn(self, consequence: Consequence) -> None:
        pass
