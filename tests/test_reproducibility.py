"""Tests for reproducibility: same seed → identical results, different seed → different results."""

from __future__ import annotations

import numpy as np
import pytest

from terrario.core.rng import RNGManager
from terrario.core.types import Action, ActionType, Direction
from terrario.experiment.controller import build_world_state, load_scenario
from terrario.world.physics import Physics
from terrario.world.rules import RuleEngine
from terrario.world.scheduler import ChangeScheduler
from terrario.world.state import WorldStateManager


def _run_episode_and_collect_hashes(scenario: dict, seed: int, num_steps: int = 50) -> list[str]:
    """Run a mini episode and return state hashes at each step."""
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

        # Deterministic random action
        at = ActionType(agent_rng.integers(0, len(ActionType)))
        d = Direction(agent_rng.integers(0, len(Direction)))
        action = Action(action_type=at, direction=d)

        consequences = physics.step(world_mgr, {0: action}, rng)

        # Find target for rules
        target = None
        if action.action_type == ActionType.CONSUME:
            from terrario.core.types import DIRECTION_DELTA
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


@pytest.fixture
def scenario():
    return {
        "grid_size": [10, 10],
        "duration": 100,
        "seed": 42,
        "view_radius": 2,
        "num_channels": 4,
        "objects": [
            {"pos": [3, 4], "channels": [0.9, 0.1, 0.2, 0.0], "movable": True, "energy_value": 5.0},
            {"pos": [6, 7], "channels": [0.1, 0.9, 0.3, 0.1], "movable": True, "energy_value": -2.0},
        ],
        "agent_start": {"pos": [5, 5], "energy": 100.0},
        "rules": {
            "rules": [
                {
                    "id": "r1",
                    "condition": {"object_channel": {"index": 0, "min": 0.7}, "action": "CONSUME"},
                    "effect": {"energy_delta": 5.0, "destroy_object": True},
                },
            ]
        },
        "changes": [],
    }


class TestReproducibility:
    def test_same_seed_identical_hashes(self, scenario):
        hashes1 = _run_episode_and_collect_hashes(scenario, seed=42)
        hashes2 = _run_episode_and_collect_hashes(scenario, seed=42)
        assert len(hashes1) > 0
        assert hashes1 == hashes2

    def test_different_seed_different_hashes(self, scenario):
        hashes1 = _run_episode_and_collect_hashes(scenario, seed=42)
        hashes2 = _run_episode_and_collect_hashes(scenario, seed=999)
        assert len(hashes1) > 0
        assert len(hashes2) > 0
        # At least some hashes should differ
        assert hashes1 != hashes2

    def test_rng_state_save_restore(self):
        rng = RNGManager(42)
        # Generate some numbers
        v1 = rng.python.random()
        n1 = rng.numpy.random()

        # Save state
        state = rng.get_state()

        # Generate more numbers (changes state)
        rng.python.random()
        rng.numpy.random()

        # Restore state
        rng.set_state(state)

        # Should generate the same sequence as after the save point
        v2 = rng.python.random()
        n2 = rng.numpy.random()

        # Now do the same from scratch
        rng2 = RNGManager(42)
        rng2.python.random()  # v1
        rng2.numpy.random()   # n1
        v3 = rng2.python.random()
        n3 = rng2.numpy.random()

        assert v2 == v3
        assert n2 == pytest.approx(n3)

    def test_global_determinism(self):
        RNGManager.set_global_determinism(42)
        import random
        v1 = random.random()
        n1 = np.random.random()

        RNGManager.set_global_determinism(42)
        v2 = random.random()
        n2 = np.random.random()

        assert v1 == v2
        assert n1 == n2
