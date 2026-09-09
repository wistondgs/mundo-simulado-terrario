"""WorldState manager — owns the canonical world state and provides controlled access."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from terrario.core.types import (
    AgentState,
    ObjectSpec,
    Observation,
    Position,
    WorldState,
)
from terrario.core.contracts import ImmutableObserverSnapshot


class WorldStateManager:
    """Manages the canonical WorldState.

    Only Physics and RuleEngine should call the mutation methods.
    All other subsystems use read-only accessors.
    """

    def __init__(
        self, state: WorldState, max_duration: int = 1000, max_energy: float = 100.0,
        step_energy_cost: float = 0.0, expose_time_fraction: bool = True,
    ):
        self._state = state
        self._max_duration = max_duration
        self._max_energy = max_energy
        self._step_energy_cost = max(0.0, step_energy_cost)
        self._expose_time_fraction = expose_time_fraction

    # ── Read-only access ──────────────────────────────────────────────

    @property
    def state(self) -> WorldState:
        """Detached compatibility view; mutating it cannot alter WorldTruth."""
        return self._state.clone()

    def _mutable_state(self) -> WorldState:
        """Internal world-only access to canonical mutable truth."""
        return self._state

    def observer_snapshot(self, step: int) -> ImmutableObserverSnapshot:
        """Return a detached full-truth record for the scientific observer."""
        return ImmutableObserverSnapshot(
            step=step,
            world_state_hash=self._state.state_hash(),
            world=self.serialize(),
        )

    @property
    def max_duration(self) -> int:
        return self._max_duration

    @property
    def max_energy(self) -> float:
        return self._max_energy

    def get_observation(
        self,
        agent_id: int,
        view_radius: int,
        num_channels: int,
    ) -> Observation:
        """Extract a local observation window around the agent.

        Channel 0 is occupancy (1.0 if any object present).
        Channels 1..N are the object perceptual channels averaged per cell.
        """
        agent = self._state.agents.get(agent_id)
        if agent is None:
            raise KeyError(f"Agent {agent_id} not found in world state")

        size = 2 * view_radius + 1
        channels = np.zeros((num_channels, size, size), dtype=np.float32)
        mask = np.ones((size, size), dtype=np.float32)

        ax, ay = agent.pos.x, agent.pos.y

        for dx in range(-view_radius, view_radius + 1):
            for dy in range(-view_radius, view_radius + 1):
                wx, wy = ax + dx, ay + dy
                ox, oy = dx + view_radius, dy + view_radius

                # Out-of-bounds cells are occluded
                if not (0 <= wx < self._state.grid_height and 0 <= wy < self._state.grid_width):
                    mask[ox, oy] = 0.0
                    continue

                # Channel 0: occupancy
                if self._state.occupancy[wx, wy] > 0:
                    channels[0, ox, oy] = 1.0

                # Channels 1..N: average object perceptual channels in this cell
                cell_objects = [
                    obj for obj in self._state.objects.values()
                    if obj.pos.x == wx and obj.pos.y == wy
                ]
                if cell_objects and num_channels > 1:
                    stacked = np.stack([o.channels for o in cell_objects])
                    avg = stacked.mean(axis=0)
                    n_obj_ch = min(avg.shape[0], num_channels - 1)
                    channels[1 : 1 + n_obj_ch, ox, oy] = avg[:n_obj_ch]

        energy_norm = min(agent.energy / self._max_energy, 1.0) if self._max_energy > 0 else 0.0
        time_frac = (
            self._state.time / self._max_duration
            if self._expose_time_fraction and self._max_duration > 0 else 0.0
        )

        channels.setflags(write=False)
        mask.setflags(write=False)
        return Observation(
            channels=channels,
            mask=mask,
            agent_energy=energy_norm,
            time_fraction=time_frac,
        )

    # ── Mutation pass-throughs (Physics / RuleEngine only) ────────────

    def set_time(self, t: int) -> None:
        self._state.time = t

    def advance_time(self) -> None:
        self._state.time += 1

    def set_rules_version(self, version: int) -> None:
        self._state.rules_version = version

    def move_agent(self, agent_id: int, new_pos: Position) -> None:
        agent = self._state.agents[agent_id]
        old = agent.pos
        self._state.occupancy[old.x, old.y] -= 1
        agent.pos = new_pos
        self._state.occupancy[new_pos.x, new_pos.y] += 1

    def move_object(self, object_id: int, new_pos: Position) -> None:
        obj = self._state.objects[object_id]
        old = obj.pos
        self._state.occupancy[old.x, old.y] -= 1
        obj.pos = new_pos
        self._state.occupancy[new_pos.x, new_pos.y] += 1

    def remove_object(self, object_id: int) -> None:
        obj = self._state.objects.pop(object_id)
        self._state.occupancy[obj.pos.x, obj.pos.y] -= 1

    def add_object(self, obj: ObjectSpec) -> None:
        self._state.objects[obj.object_id] = obj
        self._state.occupancy[obj.pos.x, obj.pos.y] += 1

    def set_agent_energy(self, agent_id: int, energy: float) -> None:
        self._state.agents[agent_id].energy = energy

    def set_agent_alive(self, agent_id: int, alive: bool) -> None:
        self._state.agents[agent_id].alive = alive

    def apply_step_energy_cost(self, agent_id: int) -> float:
        """Apply observer-configured environmental pressure after an action."""
        if self._step_energy_cost == 0.0:
            return 0.0
        agent = self._state.agents[agent_id]
        agent.energy -= self._step_energy_cost
        if agent.energy <= 0.0:
            agent.alive = False
        return -self._step_energy_cost

    def set_object_channels(self, object_id: int, channels: np.ndarray) -> None:
        self._state.objects[object_id].channels = channels

    # ── Serialization ─────────────────────────────────────────────────

    def serialize(self) -> dict[str, Any]:
        """Serialize the full world state to a plain dict for logging."""
        return {
            "grid_width": self._state.grid_width,
            "grid_height": self._state.grid_height,
            "time": self._state.time,
            "rules_version": self._state.rules_version,
            "max_duration": self._max_duration,
            "max_energy": self._max_energy,
            "step_energy_cost": self._step_energy_cost,
            "expose_time_fraction": self._expose_time_fraction,
            "objects": {
                str(oid): {
                    "object_id": obj.object_id,
                    "pos": [obj.pos.x, obj.pos.y],
                    "channels": obj.channels.tolist(),
                    "movable": obj.movable,
                    "energy_value": obj.energy_value,
                    "properties": obj.properties,
                }
                for oid, obj in self._state.objects.items()
            },
            "agents": {
                str(aid): {
                    "agent_id": ag.agent_id,
                    "pos": [ag.pos.x, ag.pos.y],
                    "energy": ag.energy,
                    "alive": ag.alive,
                }
                for aid, ag in self._state.agents.items()
            },
            "occupancy": self._state.occupancy.tolist(),
        }

    def restore(self, data: dict[str, Any]) -> None:
        """Restore world state from a serialized dict."""
        grid_width = data["grid_width"]
        grid_height = data["grid_height"]

        objects = {}
        for oid_str, odata in data["objects"].items():
            oid = int(oid_str)
            objects[oid] = ObjectSpec(
                object_id=odata["object_id"],
                pos=Position(odata["pos"][0], odata["pos"][1]),
                channels=np.array(odata["channels"], dtype=np.float32),
                movable=odata["movable"],
                energy_value=odata["energy_value"],
                properties=odata.get("properties", {}),
            )

        agents = {}
        for aid_str, adata in data["agents"].items():
            aid = int(aid_str)
            agents[aid] = AgentState(
                agent_id=adata["agent_id"],
                pos=Position(adata["pos"][0], adata["pos"][1]),
                energy=adata["energy"],
                alive=adata["alive"],
            )

        self._max_duration = data.get("max_duration", self._max_duration)
        self._max_energy = data.get("max_energy", self._max_energy)
        self._step_energy_cost = data.get("step_energy_cost", self._step_energy_cost)
        self._expose_time_fraction = data.get("expose_time_fraction", self._expose_time_fraction)

        self._state = WorldState(
            grid_width=grid_width,
            grid_height=grid_height,
            time=data["time"],
            objects=objects,
            agents=agents,
            rules_version=data["rules_version"],
            occupancy=np.array(data["occupancy"], dtype=np.int32),
        )
