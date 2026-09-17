"""Observer-visible lifecycle for finite causal opportunities in D4."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import hashlib

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


@dataclass
class OpportunityRecord:
    opportunity_id: int
    causal_class: str
    spawn_step: int
    spawn_position: tuple[int, int]
    despawn_step: int | None = None
    interaction_step: int | None = None
    interaction_agent_id: int | None = None
    reachable_at_spawn: bool = True
    visible_at_spawn: bool = False
    ever_visible: bool = False
    min_distance_during_lifetime: int | None = None
    interacted: bool = False
    respawn_parent: int | None = None


def _stream(seed: int, kind: str, key: int) -> "np.random.Generator":
    """A generator keyed on identity, never on how many calls came before.

    The cooldown and the placement draw used to be seeded from
    `len(self.events)` -- the number of opportunities consumed so far. That made
    the world's exogenous schedule a function of the ORGANISM's behaviour: two
    runs from the same world seed, differing only in how often the agent ate,
    drew their respawn delays from different streams. The world registry
    declares "world seed materializes layout; agent seed is independently
    offset", and with a call-order key that was simply untrue.

    It also breaks the paired design outright. Comparing two addressing
    contracts on the same seed is only a comparison of T if the exogenous shocks
    are held; otherwise T reaches the outcome twice, once as itself and once
    through `T -> RNG order -> W_{t+1}`.

    Keyed on (seed, kind, identity) the variate for opportunity 7 is the same
    variate whether it was the first thing eaten or the fortieth. Trajectories
    may diverge; the shocks attached to a given opportunity do not.
    """
    mixed = hashlib.blake2b(f"{seed}:{kind}:{key}".encode(), digest_size=8).digest()
    return np.random.default_rng(int.from_bytes(mixed, "big"))


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
        self.records: dict[int, OpportunityRecord] = {}

    def register_initial(self, world: WorldStateManager, step: int = 0) -> None:
        if not self.enabled:
            return
        agent = world._mutable_state().agents[0]
        for obj in world._mutable_state().objects.values():
            causal_class = obj.properties.get("causal_class")
            if causal_class not in {"A", "B"}:
                continue
            opportunity_id = self._next_opportunity_id
            self._next_opportunity_id += 1
            obj.properties["opportunity_id"] = opportunity_id
            distance = abs(obj.pos.x - agent.pos.x) + abs(obj.pos.y - agent.pos.y)
            self.records[opportunity_id] = OpportunityRecord(opportunity_id, causal_class, step, obj.pos.to_tuple(), reachable_at_spawn=True, visible_at_spawn=distance <= 2, min_distance_during_lifetime=distance)

    def consume(self, world: WorldStateManager, obj: ObjectSpec, step: int) -> OpportunityEvent | None:
        if not self.enabled or "causal_class" not in obj.properties:
            return None
        causal_class = str(obj.properties["causal_class"])
        opportunity_id = int(obj.properties.get("opportunity_id", self._next_opportunity_id))
        self._next_opportunity_id = max(self._next_opportunity_id, opportunity_id + 1)
        event_index = len(self.events)
        rng = _stream(self._seed, "cooldown", opportunity_id)
        low, high = self._config.get("cooldown_steps", [3, 8])
        due_step = step + int(rng.integers(int(low), int(high) + 1))
        self._pending.append({
            "due_step": due_step, "causal_class": causal_class, "channels": obj.channels.copy(),
            "opportunity_id": self._next_opportunity_id, "event_index": event_index,
            "spawn_key": self._next_opportunity_id,
        })
        self._next_opportunity_id += 1
        event = OpportunityEvent("despawn", opportunity_id, causal_class, step, obj.pos.to_tuple())
        record = self.records.setdefault(opportunity_id, OpportunityRecord(opportunity_id, causal_class, step, obj.pos.to_tuple()))
        record.despawn_step = step; record.interaction_step = step; record.interaction_agent_id = 0; record.interacted = True
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
            position = self._spawn_position(world, agent_pos, pending["spawn_key"])
            obj = ObjectSpec(
                object_id=self._next_object_id, pos=Position(*position), channels=pending["channels"], movable=False,
                properties={"causal_class": pending["causal_class"], "opportunity_id": pending["opportunity_id"]},
            )
            self._next_object_id += 1
            distance = abs(position[0] - agent_pos.x) + abs(position[1] - agent_pos.y)
            self.records[pending["opportunity_id"]] = OpportunityRecord(
                pending["opportunity_id"], pending["causal_class"], step, position,
                reachable_at_spawn=True, visible_at_spawn=distance <= 2, min_distance_during_lifetime=distance,
            )
            world.add_object(obj)
            event = OpportunityEvent("respawn", pending["opportunity_id"], pending["causal_class"], step, position)
            self.events.append(event)
            emitted.append(event)
        return emitted

    def _spawn_position(self, world: WorldStateManager, agent_pos: Position,
                        spawn_key: int) -> tuple[int, int]:
        """Where a respawn lands.

        The DRAW is keyed on the opportunity's identity, so the same variate
        comes up for the same opportunity in either arm. The candidate SET is
        another matter: it excludes occupied cells, cells too close to the agent
        and recently-consumed positions, so it depends on where the organism is
        and on what it has eaten. That is a declared rule of this scenario --
        the world places new opportunities relative to the organism -- and not a
        bookkeeping leak. It means a paired comparison holds the shock SCHEDULE
        fixed while placement still follows each arm's own trajectory, by design.
        """
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
        rng = _stream(self._seed, "placement", spawn_key)
        return candidates[int(rng.integers(len(candidates)))]

    def geometry(self, world: WorldStateManager, agent_id: int = 0, view_radius: int = 2) -> dict[str, Any]:
        state = world._mutable_state(); agent = state.agents[agent_id]
        classes = {"A": [], "B": []}; visible = []
        for obj in state.objects.values():
            distance = abs(obj.pos.x - agent.pos.x) + abs(obj.pos.y - agent.pos.y)
            causal_class = obj.properties.get("causal_class")
            opportunity_id = obj.properties.get("opportunity_id")
            if opportunity_id in self.records:
                record = self.records[opportunity_id]
                record.min_distance_during_lifetime = min(
                    record.min_distance_during_lifetime if record.min_distance_during_lifetime is not None else distance,
                    distance,
                )
                record.ever_visible = record.ever_visible or distance <= view_radius
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
            "concurrent_balance_ratio": len(classes["A"]) / len(classes["B"]) if classes["B"] else None,
        }


def summarize_opportunity_contract(episode_data: dict[str, Any], max_concurrent_imbalance: int = 4) -> dict[str, Any]:
    """Summarize observer-only D4 opportunity availability for validity gates."""
    geometries = [
        trace.get("causal_interaction", {}).get("geometry", {})
        for trace in episode_data.get("traces", [])
    ]
    samples = [
        (int(geometry["opportunities_class_A"]), int(geometry["opportunities_class_B"]))
        for geometry in geometries
        if "opportunities_class_A" in geometry and "opportunities_class_B" in geometry
    ]
    records = list(episode_data.get("opportunity_records", []))
    events = list(episode_data.get("opportunity_events", []))
    imbalances = [abs(class_a - class_b) for class_a, class_b in samples]
    class_counts = {"A": 0, "B": 0}
    for record in records:
        causal_class = record.get("causal_class")
        if causal_class in class_counts:
            class_counts[causal_class] += 1
    return {
        "record_count": len(records),
        "records": records,
        "despawns": sum(event.get("kind") == "despawn" for event in events),
        "respawns": sum(event.get("kind") == "respawn" for event in events),
        "interacted_records": sum(bool(record.get("interacted")) for record in records),
        "class_record_counts": class_counts,
        "all_spawn_positions_reachable": bool(records) and all(bool(record.get("reachable_at_spawn")) for record in records),
        "visible_records": sum(bool(record.get("ever_visible") or record.get("visible_at_spawn")) for record in records),
        "concurrent_samples": len(samples),
        "max_concurrent_imbalance": max(imbalances, default=None),
        "concurrent_balance_tolerance": max_concurrent_imbalance,
        "concurrent_balance_pass": bool(samples) and all(value <= max_concurrent_imbalance for value in imbalances),
    }
