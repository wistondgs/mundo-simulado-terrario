#!/usr/bin/env python
"""Environmental micro-simulation for D4-SIGNAL-01; it does not train an agent."""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from terrario.core.rng import RNGManager
from terrario.core.types import Action, ActionType, Direction
from terrario.experiment.controller import build_world_state, load_scenario, materialize_scenario
from terrario.world.opportunities import OpportunityLifecycle
from terrario.world.physics import Physics
from terrario.world.rules import RuleEngine
from terrario.world.scheduler import ChangeScheduler
from terrario.world.state import WorldStateManager


def run(seed: int) -> dict:
    scenario = materialize_scenario(load_scenario("scenarios/d4_adaptation_scientific.yaml"), seed)
    world = WorldStateManager(build_world_state(scenario), scenario["duration"], scenario["max_energy"], scenario["step_energy_cost"], False)
    rules = RuleEngine(); rules.load_rules(scenario["rules"]); world.set_rules_version(rules.version)
    scheduler = ChangeScheduler(scenario["changes"], rules)
    lifecycle = OpportunityLifecycle(scenario["opportunity_lifecycle"], seed)
    physics = Physics(); change = scenario["changes"][0]["at_step"]
    phase = {"pre": {"A": 0, "B": 0}, "post": {"A": 0, "B": 0}}
    for step in range(scenario["duration"]):
        scheduler.check(world, step); lifecycle.advance(world, step)
        agent = world._mutable_state().agents[0]
        objects = list(world._mutable_state().objects.values())
        target = min(objects, key=lambda obj: abs(obj.pos.x-agent.pos.x)+abs(obj.pos.y-agent.pos.y))
        dx, dy = target.pos.x-agent.pos.x, target.pos.y-agent.pos.y
        if abs(dx)+abs(dy) == 1:
            direction = Direction.DOWN if dx == 1 else Direction.UP if dx == -1 else Direction.RIGHT if dy == 1 else Direction.LEFT
            action = Action(ActionType.CONSUME, direction)
        else:
            direction = Direction.DOWN if dx > 0 else Direction.UP if dx < 0 else Direction.RIGHT if dy > 0 else Direction.LEFT
            action = Action(ActionType.MOVE, direction)
        physics.step(world, {0: action}, RNGManager(seed + step))
        current = next((obj for obj in world._mutable_state().objects.values() if obj.object_id == target.object_id), None)
        if current is not None and action.action_type == ActionType.CONSUME:
            effects = rules.evaluate(world, 0, action, current)
            rules.apply_effects(world, 0, current.object_id, effects)
            if current.object_id not in world._mutable_state().objects:
                lifecycle.consume(world, current, step)
                phase["pre" if step < change else "post"][current.properties["causal_class"]] += 1
    return {"seed": seed, "change_step": change, "interactions": phase, "events": [event.__dict__ for event in lifecycle.events]}


if __name__ == "__main__":
    results = [run(seed) for seed in (11, 23, 37, 53)]
    summary = []
    for result in results:
        events = result["events"]
        summary.append({
            "seed": result["seed"], "change_step": result["change_step"], "interactions": result["interactions"],
            "despawns": sum(event["kind"] == "despawn" for event in events),
            "respawns": sum(event["kind"] == "respawn" for event in events),
        })
    print(json.dumps(summary, indent=2))
