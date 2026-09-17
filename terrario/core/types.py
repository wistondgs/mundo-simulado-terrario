"""Fundamental types for Terrario. No semantic labels — only raw channels and primitives."""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any

import numpy as np


class ActionType(enum.IntEnum):
    MOVE = 0
    PUSH = 1
    CONSUME = 2
    INSPECT = 3
    NOOP = 4


class DataBoundary(enum.StrEnum):
    """Where a datum is allowed to travel in the experiment."""

    WORLD_PRIVATE = "WORLD_PRIVATE"
    OBSERVER_ONLY = "OBSERVER_ONLY"
    AGENT_PERCEPTIBLE = "AGENT_PERCEPTIBLE"
    AGENT_ACTION = "AGENT_ACTION"


NUM_ACTION_TYPES = len(ActionType)


class Direction(enum.IntEnum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    NONE = 4


NUM_DIRECTIONS = len(Direction)

DIRECTION_DELTA: dict[Direction, tuple[int, int]] = {
    Direction.UP: (-1, 0),
    Direction.DOWN: (1, 0),
    Direction.LEFT: (0, -1),
    Direction.RIGHT: (0, 1),
    Direction.NONE: (0, 0),
}


@dataclass(frozen=True)
class Position:
    x: int
    y: int

    def __add__(self, delta: tuple[int, int]) -> Position:
        return Position(self.x + delta[0], self.y + delta[1])

    def to_tuple(self) -> tuple[int, int]:
        return (self.x, self.y)


@dataclass
class ObjectSpec:
    object_id: int
    pos: Position
    channels: np.ndarray  # shape (C,) — raw perceptual channels, NO semantic names
    movable: bool = True
    energy_value: float = 0.0  # internal world property — agent never sees this directly
    properties: dict[str, Any] = field(default_factory=dict)

    def clone(self) -> ObjectSpec:
        return ObjectSpec(
            object_id=self.object_id,
            pos=Position(self.pos.x, self.pos.y),
            channels=self.channels.copy(),
            movable=self.movable,
            energy_value=self.energy_value,
            properties=dict(self.properties),
        )


@dataclass
class AgentState:
    agent_id: int
    pos: Position
    energy: float
    alive: bool = True


@dataclass
class WorldState:
    grid_width: int
    grid_height: int
    time: int
    objects: dict[int, ObjectSpec]
    agents: dict[int, AgentState]
    rules_version: int
    occupancy: np.ndarray  # shape (H, W), dtype=int32, count of objects per cell

    def clone(self) -> WorldState:
        return WorldState(
            grid_width=self.grid_width,
            grid_height=self.grid_height,
            time=self.time,
            objects={k: v.clone() for k, v in self.objects.items()},
            agents={k: AgentState(a.agent_id, Position(a.pos.x, a.pos.y), a.energy, a.alive)
                    for k, a in self.agents.items()},
            rules_version=self.rules_version,
            occupancy=self.occupancy.copy(),
        )

    def state_hash(self) -> str:
        """Deterministic hash of the full world state for reproducibility checks."""
        import hashlib
        h = hashlib.sha256()
        h.update(f"{self.grid_width},{self.grid_height},{self.time},{self.rules_version}".encode())
        for oid in sorted(self.objects.keys()):
            obj = self.objects[oid]
            h.update(f"obj:{oid}:{obj.pos.x},{obj.pos.y}:{obj.channels.tobytes()}:{obj.movable}:{obj.energy_value}".encode())
        for aid in sorted(self.agents.keys()):
            ag = self.agents[aid]
            h.update(f"agent:{aid}:{ag.pos.x},{ag.pos.y}:{ag.energy}:{ag.alive}".encode())
        h.update(self.occupancy.tobytes())
        return h.hexdigest()


@dataclass
class Action:
    """One action, under either addressing contract.

    Under v1 an action was `action_type * 5 + direction` and `target_id` was
    dead: `to_int`/`from_int` dropped it, so nothing an agent could emit reached
    it. The two fields below carry the v2 intention — see
    `terrario.core.action_contract` — and keep it separate from its resolution:

        selector_type / selector_value   what the ORGANISM meant (intended)
        target_id                        what the WORLD resolved it to

    `target_id` is therefore observer-side now, written by the runtime only
    after a resolution that passed the observability gate. An agent that sets it
    directly is reaching into world state it cannot perceive, which is the
    omniscience v1 allowed.

    Defaults keep every existing caller on the directional contract, and
    `to_int`/`from_int` are unchanged, so no identity or behavioural hash moves.
    """

    action_type: ActionType
    direction: Direction = Direction.NONE
    target_id: int = -1  # resolved world entity, or -1 for none
    selector_type: int = 0  # SelectorType.DIRECTION
    selector_value: int = -1  # direction ordinal under T0, perception slot under T1

    def to_int(self) -> int:
        """Flatten to a single integer for policy output."""
        return int(self.action_type) * NUM_DIRECTIONS + int(self.direction)

    @staticmethod
    def from_int(value: int) -> Action:
        at = ActionType(value // NUM_DIRECTIONS)
        d = Direction(value % NUM_DIRECTIONS)
        return Action(action_type=at, direction=d)

    @staticmethod
    def noop() -> Action:
        return Action(action_type=ActionType.NOOP, direction=Direction.NONE)


TOTAL_ACTIONS = NUM_ACTION_TYPES * NUM_DIRECTIONS


@dataclass
class Observation:
    """What the agent perceives — a local window of raw channels. No semantics."""
    channels: np.ndarray  # shape (C, H, W) — raw perceptual channels
    mask: np.ndarray      # shape (H, W) — 1.0 where visible, 0.0 where occluded
    agent_energy: float   # normalized 0-1
    time_fraction: float  # current time / max duration

    def obs_hash(self) -> str:
        import hashlib
        h = hashlib.sha256()
        h.update(self.channels.tobytes())
        h.update(self.mask.tobytes())
        h.update(f"{self.agent_energy},{self.time_fraction}".encode())
        return h.hexdigest()


@dataclass
class Consequence:
    energy_delta: float
    events: list[str]  # agent-perceptible outcome signals only
    observer_events: list[str] = field(default_factory=list)
    new_observation: Observation | None = None
    done: bool = False
