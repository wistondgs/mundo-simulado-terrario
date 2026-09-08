"""Physics engine — resolves agent actions against the world state."""

from __future__ import annotations

from typing import Any

from terrario.core.rng import RNGManager
from terrario.core.types import (
    Action,
    ActionType,
    Consequence,
    DIRECTION_DELTA,
    Direction,
    Position,
    WorldState,
)
from terrario.world.state import WorldStateManager


class Physics:
    """Resolves physical interactions: movement, pushing, consuming, inspecting.

    Physics handles only the mechanical effects. Energy changes from rules
    are the RuleEngine's responsibility.
    """

    def step(
        self,
        world: WorldStateManager,
        actions: dict[int, Action],
        rng: RNGManager,
    ) -> dict[int, Consequence]:
        """Execute one physics step for all agents.

        Parameters
        ----------
        world:
            The WorldStateManager wrapping the canonical state.
        actions:
            Mapping from agent_id to the Action they chose.
        rng:
            RNGManager for any stochastic resolution (currently unused but
            available for future stochastic physics).

        Returns
        -------
        dict[int, Consequence]
            Consequence per agent, including events for the observer.
        """
        consequences: dict[int, Consequence] = {}

        # Resolve in deterministic agent order
        for agent_id in sorted(actions.keys()):
            action = actions[agent_id]
            agent = world.state.agents.get(agent_id)
            if agent is None or not agent.alive:
                consequences[agent_id] = Consequence(
                    energy_delta=0.0,
                    events=["agent_not_active"],
                )
                continue

            events: list[str] = []

            if action.action_type == ActionType.MOVE:
                events.extend(self._handle_move(world, agent_id, action.direction))
            elif action.action_type == ActionType.PUSH:
                events.extend(self._handle_push(world, agent_id, action.direction))
            elif action.action_type == ActionType.CONSUME:
                events.extend(self._handle_consume(world, agent_id, action))
            elif action.action_type == ActionType.INSPECT:
                events.extend(self._handle_inspect(world, agent_id, action))
            elif action.action_type == ActionType.NOOP:
                events.append("noop")

            consequences[agent_id] = Consequence(
                energy_delta=0.0,  # RuleEngine fills this in
                events=events,
            )

        world.advance_time()
        return consequences

    # ── Action handlers ───────────────────────────────────────────────

    def _handle_move(
        self, world: WorldStateManager, agent_id: int, direction: Direction
    ) -> list[str]:
        """Handle MOVE: attempt to move agent in the given direction."""
        agent = world.state.agents[agent_id]
        delta = DIRECTION_DELTA[direction]
        new_pos = agent.pos + delta

        if not self._in_bounds(world.state, new_pos):
            return ["move_blocked_wall"]

        # Check for collision with objects (any object blocks movement)
        if world.state.occupancy[new_pos.x, new_pos.y] > 0:
            return ["move_blocked_object"]

        world.move_agent(agent_id, new_pos)
        return ["move_success"]

    def _handle_push(
        self, world: WorldStateManager, agent_id: int, direction: Direction
    ) -> list[str]:
        """Handle PUSH: push a movable object and follow it."""
        agent = world.state.agents[agent_id]
        delta = DIRECTION_DELTA[direction]
        target_pos = agent.pos + delta

        if not self._in_bounds(world.state, target_pos):
            return ["push_blocked_wall"]

        # Find object at target cell
        target_obj = self._object_at(world.state, target_pos)
        if target_obj is None:
            return ["push_no_target"]

        if not target_obj.movable:
            return ["push_immovable"]

        # Where the object would land
        obj_dest = target_pos + delta
        if not self._in_bounds(world.state, obj_dest):
            return ["push_blocked_wall"]

        if world.state.occupancy[obj_dest.x, obj_dest.y] > 0:
            return ["push_blocked_object"]

        # Move object, then move agent into the vacated cell
        world.move_object(target_obj.object_id, obj_dest)
        world.move_agent(agent_id, target_pos)
        return [f"push_success_obj_{target_obj.object_id}"]

    def _handle_consume(
        self, world: WorldStateManager, agent_id: int, action: Action
    ) -> list[str]:
        """Handle CONSUME: mark target object for RuleEngine evaluation.

        Physics does NOT apply energy changes — that is RuleEngine's job.
        This handler only validates the target exists and is adjacent.
        """
        agent = world.state.agents[agent_id]

        # Determine target: explicit target_id or object in facing direction
        target_obj = None
        if action.target_id >= 0:
            target_obj = world.state.objects.get(action.target_id)
            if target_obj is not None and not self._is_adjacent(agent.pos, target_obj.pos):
                return ["consume_target_not_adjacent"]
        else:
            delta = DIRECTION_DELTA[action.direction]
            target_pos = agent.pos + delta
            target_obj = self._object_at(world.state, target_pos)

        if target_obj is None:
            return ["consume_no_target"]

        # Mark for rule engine — the actual effect is applied by RuleEngine
        return [f"consume_pending_obj_{target_obj.object_id}"]

    def _handle_inspect(
        self, world: WorldStateManager, agent_id: int, action: Action
    ) -> list[str]:
        """Handle INSPECT: no physical effect.

        The observation system handles the increased detail separately.
        """
        return ["inspect"]

    # ── Helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _in_bounds(state: WorldState, pos: Position) -> bool:
        return 0 <= pos.x < state.grid_height and 0 <= pos.y < state.grid_width

    @staticmethod
    def _object_at(state: WorldState, pos: Position):
        """Return the first object at a position, or None."""
        for obj in state.objects.values():
            if obj.pos.x == pos.x and obj.pos.y == pos.y:
                return obj
        return None

    @staticmethod
    def _is_adjacent(a: Position, b: Position) -> bool:
        return abs(a.x - b.x) + abs(a.y - b.y) == 1
