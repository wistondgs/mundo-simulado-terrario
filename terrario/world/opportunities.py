"""Observer-visible lifecycle for finite causal opportunities in D4."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from terrario.core.types import ObjectSpec, Position
from terrario.world.state import WorldStateManager


@dataclass(frozen=True)
class OpportunityEvent:
    kind: str
    opportunity_id: int
    causal_class: str
    step: int
    position: tuple[int, int]


class OpportunityLifecycle:
    """Despawns a consumed instance and respawns its class after a fixed-delay draw."""

    def __init__(self, config: dict[str, Any], world_seed: int):
        self.enabled = bool(config)
        self._config = config
        self._seed = world_seed
        self._next_object_id = 10_000
        self._next_opportunity_id = 1
        self._pending: list[dict[str, Any]] = []
        self._recent_positions: list[tuple[int, int]] = []
        self.events: list[OpportunityEvent] = []

    def consume(self, world: WorldStateManager, obj: ObjectSpec, step: int) -> OpportunityEvent | None:
        if not self.enabled or "causal_class" not in obj.properties:
            return None
        causal_class = str(obj.properties["causal_class"])
        opportunity_id = int(obj.properties.get("opportunity_id", self._next_opportunity_id))
        self._next_opportunity_id = max(self._next_opportunity_id, opportunity_id + 1)
        event_index = len(self.events)
        rng = np.random.default_rng(self._seed + 104_729 * (event_index + 1))
        low, high = self._config.get("cooldown_steps", [3, 8])
        due_step = step + int(rng.integers(int(low), int(high) + 1))
        self._pending.append({
            "due_step": due_step, "causal_class": causal_class, "channels": obj.channels.copy(),
            "opportunity_id": self._next_opportunity_id, "event_index": event_index,
        })
        self._next_opportunity_id += 1
        event = OpportunityEvent("despawn", opportunity_id, causal_class, step, obj.pos.to_tuple())
        self.events.append(event)
        self._recent_positions.append(obj.pos.to_tuple())
        self._recent_positions = self._recent_positions[-int(self._config.get("recent_position_exclusion", 2)):]
        return event

    def advance(self, world: WorldStateManager, step: int, agent_id: int = 0) -> list[OpportunityEvent]:
        if not self.enabled:
            return []
        due, self._pending = [p for p in self._pending if p["due_step"] <= step], [p for p in self._pending if p["due_step"] > step]
        emitted: list[OpportunityEvent] = []
        agent_pos = world._mutable_state().agents[agent_id].pos
        for pending in due:
            position = self._spawn_position(world, agent_pos, pending["event_index"])
            obj = ObjectSpec(
                object_id=self._next_object_id, pos=Position(*position), channels=pending["channels"], movable=False,
                properties={"causal_class": pending["causal_class"], "opportunity_id": pending["opportunity_id"]},
            )
            self._next_object_id += 1
            world.add_object(obj)
            event = OpportunityEvent("respawn", pending["opportunity_id"], pending["causal_class"], step, position)
            self.events.append(event)
            emitted.append(event)
        return emitted

    def _spawn_position(self, world: WorldStateManager, agent_pos: Position, event_index: int) -> tuple[int, int]:
        state = world._mutable_state()
        margin = int(self._config.get("placement_margin", 1))
        minimum_distance = int(self._config.get("minimum_agent_distance", 2))
        candidates = [
            (x, y) for x in range(margin, state.grid_height - margin) for y in range(margin, state.grid_width - margin)
            if state.occupancy[x, y] == 0 and abs(x - agent_pos.x) + abs(y - agent_pos.y) >= minimum_distance
            and (x, y) not in self._recent_positions
        ]
        if not candidates:
            candidates = [(x, y) for x in range(margin, state.grid_height - margin) for y in range(margin, state.grid_width - margin) if state.occupancy[x, y] == 0]
        rng = np.random.default_rng(self._seed + 1_000_003 + event_index)
        return candidates[int(rng.integers(len(candidates)))]

    def geometry(self, world: WorldStateManager, agent_id: int = 0, view_radius: int = 2) -> dict[str, Any]:
        state = world._mutable_state(); agent = state.agents[agent_id]
        classes = {"A": [], "B": []}; visible = []
        for obj in state.objects.values():
            distance = abs(obj.pos.x - agent.pos.x) + abs(obj.pos.y - agent.pos.y)
            causal_class = obj.properties.get("causal_class")
            if causal_class in classes:
                classes[causal_class].append(distance)
            if distance <= view_radius:
                visible.append(distance)
        return {
            "agent_position": agent.pos.to_tuple(), "nearest_A_distance": min(classes["A"], default=None),
            "nearest_B_distance": min(classes["B"], default=None), "objects_visible": len(visible),
            "nearest_visible_object_distance": min(visible, default=None),
            "opportunities_class_A": len(classes["A"]), "opportunities_class_B": len(classes["B"]),
            "pending_respawns": len(self._pending),
        }
