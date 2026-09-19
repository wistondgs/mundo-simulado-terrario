"""Tests for the world subsystem: WorldState, Physics, RuleEngine, ChangeScheduler, Observation."""

from __future__ import annotations

import numpy as np
import pytest

from terrario.core.rng import RNGManager
from terrario.core.types import (
    Action,
    ActionType,
    AgentState,
    Direction,
    ObjectSpec,
    Position,
    WorldState,
)
from terrario.experiment.controller import build_world_state, load_scenario
from terrario.world.physics import Physics
from terrario.world.rules import RuleEngine
from terrario.world.scheduler import ChangeScheduler
from terrario.world.state import WorldStateManager


@pytest.fixture
def simple_scenario():
    return {
        "grid_size": [10, 10],
        "duration": 100,
        "seed": 42,
        "view_radius": 2,
        "num_channels": 4,
        "objects": [
            {"pos": [3, 4], "channels": [0.9, 0.1, 0.2, 0.0], "movable": True, "energy_value": 5.0},
            {"pos": [6, 7], "channels": [0.1, 0.9, 0.3, 0.1], "movable": False, "energy_value": -2.0},
        ],
        "agent_start": {"pos": [5, 5], "energy": 100.0},
        "rules": {
            "rules": [
                {
                    "id": "rule_001",
                    "condition": {"object_channel": {"index": 0, "min": 0.7}, "action": "CONSUME"},
                    "effect": {"energy_delta": 5.0, "destroy_object": True},
                },
            ]
        },
        "changes": [],
    }


@pytest.fixture
def world_mgr(simple_scenario):
    state = build_world_state(simple_scenario)
    return WorldStateManager(state, max_duration=100, max_energy=100.0)


class TestWorldState:
    def test_creation_from_scenario(self, simple_scenario):
        state = build_world_state(simple_scenario)
        assert state.grid_width == 10
        assert state.grid_height == 10
        assert len(state.objects) == 2
        assert len(state.agents) == 1
        assert state.time == 0

    def test_object_positions(self, simple_scenario):
        state = build_world_state(simple_scenario)
        obj0 = state.objects[0]
        assert obj0.pos.x == 3
        assert obj0.pos.y == 4
        assert obj0.channels[0] == pytest.approx(0.9)

    def test_agent_start(self, simple_scenario):
        state = build_world_state(simple_scenario)
        agent = state.agents[0]
        assert agent.pos.x == 5
        assert agent.pos.y == 5
        assert agent.energy == 100.0
        assert agent.alive

    def test_occupancy_grid(self, simple_scenario):
        state = build_world_state(simple_scenario)
        assert state.occupancy[3, 4] == 1  # object 0
        assert state.occupancy[6, 7] == 1  # object 1
        assert state.occupancy[5, 5] == 1  # agent

    def test_state_hash_deterministic(self, simple_scenario):
        s1 = build_world_state(simple_scenario)
        s2 = build_world_state(simple_scenario)
        assert s1.state_hash() == s2.state_hash()

    def test_clone(self, simple_scenario):
        state = build_world_state(simple_scenario)
        cloned = state.clone()
        assert cloned.state_hash() == state.state_hash()
        # Mutating clone doesn't affect original
        cloned.time = 99
        assert state.time == 0


class TestPhysics:
    def test_move_success(self, world_mgr):
        physics = Physics()
        rng = RNGManager(42)
        action = Action(action_type=ActionType.MOVE, direction=Direction.UP)
        consequences = physics.step(world_mgr, {0: action}, rng)
        assert "move_success" in consequences[0].events
        assert world_mgr.state.agents[0].pos.x == 4
        assert world_mgr.state.agents[0].pos.y == 5

    def test_move_blocked_wall(self, world_mgr):
        physics = Physics()
        rng = RNGManager(42)
        # Move agent to edge first
        world_mgr.move_agent(0, Position(0, 0))
        action = Action(action_type=ActionType.MOVE, direction=Direction.UP)
        consequences = physics.step(world_mgr, {0: action}, rng)
        assert "move_blocked_wall" in consequences[0].events

    def test_move_blocked_object(self, world_mgr):
        physics = Physics()
        rng = RNGManager(42)
        # Agent at (5,5), object at (3,4) — move agent next to object
        world_mgr.move_agent(0, Position(3, 3))
        action = Action(action_type=ActionType.MOVE, direction=Direction.RIGHT)
        consequences = physics.step(world_mgr, {0: action}, rng)
        assert "move_blocked_object" in consequences[0].events

    def test_push_movable(self, world_mgr):
        physics = Physics()
        rng = RNGManager(42)
        # Agent at (3,3), object 0 at (3,4) — push right
        world_mgr.move_agent(0, Position(3, 3))
        action = Action(action_type=ActionType.PUSH, direction=Direction.RIGHT)
        consequences = physics.step(world_mgr, {0: action}, rng)
        assert any("push_success" in e for e in consequences[0].observer_events)
        assert all("obj_" not in e for e in consequences[0].events)
        assert world_mgr.state.objects[0].pos.y == 5
        assert world_mgr.state.agents[0].pos.y == 4

    def test_push_immovable(self, world_mgr):
        physics = Physics()
        rng = RNGManager(42)
        # Object 1 at (6,7) is immovable
        world_mgr.move_agent(0, Position(6, 6))
        action = Action(action_type=ActionType.PUSH, direction=Direction.RIGHT)
        consequences = physics.step(world_mgr, {0: action}, rng)
        assert "push_immovable" in consequences[0].events

    def test_consume_pending(self, world_mgr):
        physics = Physics()
        rng = RNGManager(42)
        # Agent next to object 0 at (3,4)
        world_mgr.move_agent(0, Position(3, 3))
        action = Action(action_type=ActionType.CONSUME, direction=Direction.RIGHT)
        consequences = physics.step(world_mgr, {0: action}, rng)
        assert any("consume_pending" in e for e in consequences[0].observer_events)
        assert all("consume_pending" not in e for e in consequences[0].events)

    def test_consume_no_target(self, world_mgr):
        physics = Physics()
        rng = RNGManager(42)
        action = Action(action_type=ActionType.CONSUME, direction=Direction.UP)
        consequences = physics.step(world_mgr, {0: action}, rng)
        assert "consume_no_target" in consequences[0].events

    def test_noop(self, world_mgr):
        physics = Physics()
        rng = RNGManager(42)
        consequences = physics.step(world_mgr, {0: Action.noop()}, rng)
        assert "noop" in consequences[0].events

    def test_time_advances(self, world_mgr):
        physics = Physics()
        rng = RNGManager(42)
        assert world_mgr.state.time == 0
        physics.step(world_mgr, {0: Action.noop()}, rng)
        assert world_mgr.state.time == 1


class TestRuleEngine:
    def test_rule_evaluation_match(self, world_mgr):
        engine = RuleEngine()
        engine.load_rules({
            "rules": [
                {
                    "id": "r1",
                    "condition": {"object_channel": {"index": 0, "min": 0.7}, "action": "CONSUME"},
                    "effect": {"energy_delta": 5.0, "destroy_object": True},
                },
            ]
        })
        obj = world_mgr.state.objects[0]  # ch0 = 0.9
        action = Action(action_type=ActionType.CONSUME, direction=Direction.RIGHT)
        effects = engine.evaluate(world_mgr, 0, action, obj)
        assert len(effects) == 1
        assert effects[0].energy_delta == 5.0

    def test_rule_evaluation_no_match(self, world_mgr):
        engine = RuleEngine()
        engine.load_rules({
            "rules": [
                {
                    "id": "r1",
                    "condition": {"object_channel": {"index": 0, "min": 0.7}, "action": "CONSUME"},
                    "effect": {"energy_delta": 5.0},
                },
            ]
        })
        obj = world_mgr.state.objects[1]  # ch0 = 0.1
        action = Action(action_type=ActionType.CONSUME, direction=Direction.RIGHT)
        effects = engine.evaluate(world_mgr, 0, action, obj)
        assert len(effects) == 0

    def test_apply_effects_energy(self, world_mgr):
        engine = RuleEngine()
        engine.load_rules({
            "rules": [
                {
                    "id": "r1",
                    "condition": {"object_channel": {"index": 0, "min": 0.7}, "action": "CONSUME"},
                    "effect": {"energy_delta": 5.0, "destroy_object": True},
                },
            ]
        })
        # El agente del fixture nace EN el techo (100.0 de 100.0). Desde que
        # `max_energy` es un techo de verdad, ahí no cabe ninguna ganancia, así
        # que la premisa del test necesita margen para poder medir lo que mide:
        # que el efecto energético de una regla se aplica.
        world_mgr.set_agent_energy(0, 50.0)
        obj = world_mgr.state.objects[0]
        action = Action(action_type=ActionType.CONSUME, direction=Direction.RIGHT)
        effects = engine.evaluate(world_mgr, 0, action, obj)
        delta = engine.apply_effects(world_mgr, 0, obj.object_id, effects)
        assert delta == 5.0
        assert world_mgr.state.agents[0].energy == 55.0

    def test_apply_effects_destroy(self, world_mgr):
        engine = RuleEngine()
        engine.load_rules({
            "rules": [
                {
                    "id": "r1",
                    "condition": {"object_channel": {"index": 0, "min": 0.7}, "action": "CONSUME"},
                    "effect": {"energy_delta": 5.0, "destroy_object": True},
                },
            ]
        })
        obj = world_mgr.state.objects[0]
        action = Action(action_type=ActionType.CONSUME, direction=Direction.RIGHT)
        effects = engine.evaluate(world_mgr, 0, action, obj)
        engine.apply_effects(world_mgr, 0, obj.object_id, effects)
        assert 0 not in world_mgr.state.objects

    def test_version_increments(self):
        engine = RuleEngine()
        assert engine.version == 0
        engine.load_rules({"rules": []})
        assert engine.version == 1
        engine.load_rules({"rules": []})
        assert engine.version == 2


class TestChangeScheduler:
    def test_rule_change_at_correct_step(self, world_mgr):
        engine = RuleEngine()
        engine.load_rules({"rules": [{"id": "old", "condition": {}, "effect": {"energy_delta": 1.0}}]})
        old_version = engine.version

        changes = [
            {
                "at_step": 5,
                "rules": {"rules": [{"id": "new", "condition": {}, "effect": {"energy_delta": -1.0}}]},
            }
        ]
        scheduler = ChangeScheduler(changes, engine)

        # Not yet at step 5
        for _ in range(4):
            world_mgr.advance_time()
            events = scheduler.check(world_mgr)
            assert len(events) == 0

        # At step 5
        world_mgr.advance_time()
        assert world_mgr.state.time == 5
        events = scheduler.check(world_mgr)
        assert len(events) == 1
        assert events[0].old_version == old_version
        assert engine.version == old_version + 1
        assert engine.rules[0].rule_id == "new"

    def test_no_change_when_empty(self, world_mgr):
        engine = RuleEngine()
        scheduler = ChangeScheduler([], engine)
        events = scheduler.check(world_mgr)
        assert len(events) == 0

    def test_change_fires_only_once(self, world_mgr):
        engine = RuleEngine()
        engine.load_rules({"rules": []})
        changes = [{"at_step": 0, "rules": {"rules": []}}]
        scheduler = ChangeScheduler(changes, engine)
        events1 = scheduler.check(world_mgr)
        events2 = scheduler.check(world_mgr)
        assert len(events1) == 1
        assert len(events2) == 0


class TestObservation:
    def test_observation_shape(self, world_mgr):
        obs = world_mgr.get_observation(0, view_radius=2, num_channels=4)
        assert obs.channels.shape == (4, 5, 5)
        assert obs.mask.shape == (5, 5)

    def test_observation_no_semantic_leakage(self, world_mgr):
        """Observation channels should only contain raw float values, no labels."""
        obs = world_mgr.get_observation(0, view_radius=2, num_channels=4)
        assert obs.channels.dtype == np.float32
        # All values should be between 0 and 1 (normalized channels)
        assert np.all(obs.channels >= 0.0)
        assert np.all(obs.channels <= 1.0)

    def test_observation_energy_normalized(self, world_mgr):
        obs = world_mgr.get_observation(0, view_radius=2, num_channels=4)
        assert 0.0 <= obs.agent_energy <= 1.0
        assert obs.agent_energy == pytest.approx(1.0)  # 100/100

    def test_observation_time_fraction(self, world_mgr):
        obs = world_mgr.get_observation(0, view_radius=2, num_channels=4)
        assert obs.time_fraction == pytest.approx(0.0)  # time=0, duration=100

    def test_observation_mask_at_edges(self, world_mgr):
        world_mgr.move_agent(0, Position(0, 0))
        obs = world_mgr.get_observation(0, view_radius=2, num_channels=4)
        # Top-left corner: some cells should be occluded
        assert obs.mask[0, 0] == 0.0  # out of bounds
        assert obs.mask[2, 2] == 1.0  # agent position

    def test_observation_deterministic(self, world_mgr):
        obs1 = world_mgr.get_observation(0, view_radius=2, num_channels=4)
        obs2 = world_mgr.get_observation(0, view_radius=2, num_channels=4)
        assert obs1.obs_hash() == obs2.obs_hash()
