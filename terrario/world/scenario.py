"""ScenarioSpec loader — parses YAML scenario files and constructs world components."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import yaml

from terrario.core.types import AgentState, ObjectSpec, Position, WorldState
from terrario.world.rules import RuleEngine
from terrario.world.scheduler import ChangeScheduler


@dataclass
class ObjectConfig:
    """Configuration for a single object in the scenario."""
    pos: tuple[int, int]
    channels: list[float]
    movable: bool = True
    energy_value: float = 0.0


@dataclass
class AgentStartConfig:
    """Initial agent placement and energy."""
    pos: tuple[int, int]
    energy: float = 100.0


@dataclass
class ScenarioSpec:
    """Parsed scenario specification.

    All fields come from the YAML scenario file. No semantic names —
    only raw channel indices and numeric values.
    """
    name: str
    grid_size: tuple[int, int]  # (height, width)
    duration: int
    seed: int
    objects: list[ObjectConfig]
    agent_start: AgentStartConfig
    rules: dict[str, Any]  # inline rules dict
    changes: list[dict[str, Any]] = field(default_factory=list)
    view_radius: int = 3
    num_channels: int = 4

    def create_world_state(self) -> WorldState:
        """Construct the initial WorldState from this scenario."""
        h, w = self.grid_size
        occupancy = np.zeros((h, w), dtype=np.int32)

        objects: dict[int, ObjectSpec] = {}
        for i, oc in enumerate(self.objects):
            obj = ObjectSpec(
                object_id=i,
                pos=Position(oc.pos[0], oc.pos[1]),
                channels=np.array(oc.channels, dtype=np.float32),
                movable=oc.movable,
                energy_value=oc.energy_value,
            )
            objects[i] = obj
            occupancy[obj.pos.x, obj.pos.y] += 1

        agent = AgentState(
            agent_id=0,
            pos=Position(self.agent_start.pos[0], self.agent_start.pos[1]),
            energy=self.agent_start.energy,
        )
        agents = {0: agent}
        occupancy[agent.pos.x, agent.pos.y] += 1

        return WorldState(
            grid_width=w,
            grid_height=h,
            time=0,
            objects=objects,
            agents=agents,
            rules_version=0,
            occupancy=occupancy,
        )

    def create_rule_engine(self) -> RuleEngine:
        """Construct a RuleEngine loaded with this scenario's initial rules."""
        engine = RuleEngine()
        engine.load_rules(self.rules)
        return engine

    def create_scheduler(self, rule_engine: RuleEngine) -> ChangeScheduler:
        """Construct a ChangeScheduler for this scenario's rule changes."""
        return ChangeScheduler(self.changes, rule_engine)


def load_scenario(path: str | Path) -> ScenarioSpec:
    """Load a scenario YAML file and return a ScenarioSpec.

    The ``rules`` field can be an inline dict or a string path to a separate
    YAML file containing the rules dict.
    """
    path = Path(path)
    with open(path, "r") as f:
        data = yaml.safe_load(f)

    # Parse grid size — accept [H, W] list or separate keys
    grid_raw = data.get("grid_size", [data.get("grid_height", 10), data.get("grid_width", 10)])
    grid_size = (int(grid_raw[0]), int(grid_raw[1]))

    # Parse objects
    objects = [
        ObjectConfig(
            pos=(o["pos"][0], o["pos"][1]),
            channels=o.get("channels", []),
            movable=o.get("movable", True),
            energy_value=o.get("energy_value", 0.0),
        )
        for o in data.get("objects", [])
    ]

    # Parse agent start
    agent_raw = data.get("agent_start", {})
    agent_start = AgentStartConfig(
        pos=(agent_raw.get("pos", [0, 0])[0], agent_raw.get("pos", [0, 0])[1]),
        energy=agent_raw.get("energy", 100.0),
    )

    # Parse rules — inline dict or path to external file
    rules_raw = data.get("rules", {})
    if isinstance(rules_raw, str):
        rules_path = path.parent / rules_raw
        with open(rules_path, "r") as f:
            rules_raw = yaml.safe_load(f)

    # Parse scheduled changes
    changes = data.get("changes", [])

    return ScenarioSpec(
        name=data.get("name", path.stem),
        grid_size=grid_size,
        duration=data.get("duration", 1000),
        seed=data.get("seed", 42),
        objects=objects,
        agent_start=agent_start,
        rules=rules_raw,
        changes=changes,
        view_radius=data.get("view_radius", 3),
        num_channels=data.get("num_channels", 4),
    )
