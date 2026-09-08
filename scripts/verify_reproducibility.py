#!/usr/bin/env python
"""Verify that Terrario produces identical results with identical seeds.

Usage:
    python scripts/verify_reproducibility.py
    python scripts/verify_reproducibility.py --scenario scenarios/d0_differences.yaml --steps 50
"""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np

from terrario.core.rng import RNGManager
from terrario.core.types import Action, ActionType, DIRECTION_DELTA, Direction
from terrario.experiment.controller import build_world_state, load_scenario
from terrario.world.physics import Physics
from terrario.world.rules import RuleEngine
from terrario.world.scheduler import ChangeScheduler
from terrario.world.state import WorldStateManager


def run_episode_hashes(scenario: dict, seed: int, num_steps: int) -> list[str]:
    """Run an episode and return state hashes at each step."""
    RNGManager.set_global_determinism(seed)
    rng = RNGManager(seed)

    world_state = build_world_state(scenario)
    world_mgr = WorldStateManager(world_state, max_duration=num_steps, max_energy=100.0)

    rule_engine = RuleEngine()
    rule_engine.load_rules(scenario.get("rules", {}))
    world_mgr.set_rules_version(rule_engine.version)

    scheduler = ChangeScheduler(scenario.get("changes", []), rule_engine)
    physics = Physics()
    agent_rng = np.random.default_rng(seed)

    hashes = []

    for step in range(num_steps):
        agent = world_mgr.state.agents.get(0)
        if agent is None or not agent.alive:
            break

        at = ActionType(agent_rng.integers(0, len(ActionType)))
        d = Direction(agent_rng.integers(0, len(Direction)))
        action = Action(action_type=at, direction=d)

        consequences = physics.step(world_mgr, {0: action}, rng)

        # Find target for rules
        target = None
        if action.action_type == ActionType.CONSUME:
            delta = DIRECTION_DELTA[action.direction]
            tpos = agent.pos + delta
            for obj in world_mgr.state.objects.values():
                if obj.pos.x == tpos.x and obj.pos.y == tpos.y:
                    target = obj
                    break

        if target is not None:
            effects = rule_engine.evaluate(world_mgr, 0, action, target)
            rule_engine.apply_effects(world_mgr, 0, target.object_id, effects)

        scheduler.check(world_mgr)
        hashes.append(world_mgr.state.state_hash())

    return hashes


def main():
    parser = argparse.ArgumentParser(description="Verify Terrario reproducibility")
    parser.add_argument(
        "--scenario",
        type=str,
        default="scenarios/d0_differences.yaml",
        help="Scenario to test",
    )
    parser.add_argument("--steps", type=int, default=50, help="Number of steps")
    parser.add_argument("--seed", type=int, default=42, help="Seed to test")
    args = parser.parse_args()

    scenario = load_scenario(args.scenario)

    print(f"Reproducibility verification")
    print(f"  Scenario: {args.scenario}")
    print(f"  Steps: {args.steps}")
    print(f"  Seed: {args.seed}")
    print()

    # Run 1
    print("Run 1...", end=" ", flush=True)
    hashes1 = run_episode_hashes(scenario, args.seed, args.steps)
    print(f"{len(hashes1)} steps")

    # Run 2 (same seed)
    print("Run 2 (same seed)...", end=" ", flush=True)
    hashes2 = run_episode_hashes(scenario, args.seed, args.steps)
    print(f"{len(hashes2)} steps")

    # Run 3 (different seed)
    print("Run 3 (different seed)...", end=" ", flush=True)
    hashes3 = run_episode_hashes(scenario, args.seed + 1, args.steps)
    print(f"{len(hashes3)} steps")

    print()

    # Check same-seed reproducibility
    if hashes1 == hashes2:
        print("PASS: Same seed produces identical state hashes at every step.")
    else:
        mismatches = sum(1 for a, b in zip(hashes1, hashes2) if a != b)
        print(f"FAIL: {mismatches}/{len(hashes1)} state hashes differ between identical runs!")
        for i, (a, b) in enumerate(zip(hashes1, hashes2)):
            if a != b:
                print(f"  First mismatch at step {i}: {a[:16]}... vs {b[:16]}...")
                break
        sys.exit(1)

    # Check different-seed divergence
    if hashes1 != hashes3:
        print("PASS: Different seeds produce different state hashes.")
    else:
        print("WARNING: Different seeds produced identical hashes (possible for short runs).")

    print("\nReproducibility verification complete.")


if __name__ == "__main__":
    main()
