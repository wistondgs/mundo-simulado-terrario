"""One semantics for a timestep, so a result means one thing.

Terrario grew three complete implementations of the same step -- the scientific
one in `ExperimentController.run_episode`, the engineering one in
`SandboxService._step_runtime`, and a third in `CausalRuntime.step` -- plus a
fourth inside the reproducibility test and its script. They diverged in physics,
not only in bookkeeping: the sandbox never instantiated `OpportunityLifecycle`,
so a scenario that declares a respawn cooldown of 3 to 8 steps ran there as a
strictly depleting world. Measured on D4T over 250 steps: 32 objects at the
start, 29 at the end, not one respawn.

The consequence is that "D4T" had no single meaning, and every recent result --
the screening, the paired T0/T1 rollout, the one-step twins, the capability
run -- was produced on the surface that is not the authoritative one.

This module holds the parts that decide what happened. Storage, streaming,
observers, run state, provenance and trace schemas stay with whichever surface
owns them: those can differ without the world differing.

Nothing here is new behaviour. Each function is lifted from the path that was
already correct, and the behaviour fixture -- nine cases over D2, D3 and D4,
compared field for field including its semantic digest -- is what proves the
lift changed nothing.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

import numpy as np

from terrario.core.types import (
    DIRECTION_DELTA, Action, ActionType, AgentState, ObjectSpec, Position, WorldState,
)
from terrario.world.opportunities import OpportunityLifecycle
from terrario.world.physics import Physics
from terrario.world.rules import RuleEngine
from terrario.world.scheduler import ChangeScheduler
from terrario.world.state import WorldStateManager

#: The semantics a piece of evidence was produced under. It travels with the
#: result rather than being inferred later from a commit date, because the
#: question "which physics ran this?" had to be answered by reading code.
SEMANTICS_VERSION = "terrario.world.transition/v1"


class WorldPhysicsNotDeclared(ValueError):
    """A world whose economy the scenario never stated."""


def find_target(world: WorldStateManager, agent_id: int, action: Action) -> ObjectSpec | None:
    """The object a CONSUME acts on, by entity or by the faced cell.

    Lifted verbatim from two implementations that were character-for-character
    equivalent and written differently -- `ExperimentController._find_target`
    and the module-level `_find_target` in the sandbox. Keeping two was a drift
    waiting to happen: the third caller reached across packages for the
    controller's private method to avoid writing a third.

    Adjacency is Manhattan distance exactly 1, which excludes the agent's own
    cell and the diagonals. The `target_id` branch looks the entity up in world
    truth; that is safe only because the sole writer of `target_id` is a
    resolution that already checked the organism could perceive it.
    """
    if action.action_type != ActionType.CONSUME:
        return None
    truth = world._mutable_state()
    agent = truth.agents[agent_id]
    if action.target_id >= 0:
        target = truth.objects.get(action.target_id)
        if target is None:
            return None
        if abs(target.pos.x - agent.pos.x) + abs(target.pos.y - agent.pos.y) != 1:
            return None
        return target
    position = agent.pos + DIRECTION_DELTA[action.direction]
    return next((obj for obj in truth.objects.values() if obj.pos == position), None)


def build_world_state(scenario: Mapping[str, Any]) -> WorldState:
    """A WorldState from a materialised scenario.

    Lifted verbatim from `experiment/controller.py`, where it had been living
    since before the layers existed. It builds a world and nothing else, so it
    belongs to `world/`; leaving it in `experiment/` meant the shared semantics
    could not assemble a world without importing the surface it serves, which is
    a cycle. The controller keeps the name as a re-export, so the thirty callers
    that import it from there are untouched.
    """
    grid_w, grid_h = scenario["grid_size"]
    occupancy = np.zeros((grid_h, grid_w), dtype=np.int32)
    objects: dict[int, ObjectSpec] = {}
    for i, obj_data in enumerate(scenario.get("objects", [])):
        pos = Position(*obj_data["pos"])
        objects[i] = ObjectSpec(
            object_id=i, pos=pos, channels=np.array(obj_data["channels"], dtype=np.float32),
            movable=obj_data.get("movable", True), energy_value=obj_data.get("energy_value", 0.0),
            properties=dict(obj_data.get("properties", {})),
        )
        occupancy[pos.x, pos.y] += 1
    start = scenario.get("agent_start", {"pos": [5, 5], "energy": 100.0})
    agent_pos = Position(*start["pos"])
    occupancy[agent_pos.x, agent_pos.y] += 1
    return WorldState(
        grid_width=grid_w, grid_height=grid_h, time=0, objects=objects,
        agents={0: AgentState(0, agent_pos, start.get("energy", 100.0))},
        rules_version=0, occupancy=occupancy,
    )


@dataclass
class EpisodeComponents:
    """Everything a timestep needs, built once instead of in four places.

    The construction of a world was copied into `ExperimentController`,
    `lab/execution/runtime`, `experiment/adaptation` and `SandboxService`, with
    fallbacks that had already drifted: one defaults `duration` to the campaign
    limit and another to the literal 500. Four copies of five lines is how two
    surfaces end up running different physics without anyone deciding to.
    """

    world: WorldStateManager
    rules: RuleEngine
    scheduler: ChangeScheduler
    physics: Physics
    scenario: Mapping[str, Any]
    lifecycle: OpportunityLifecycle | None = None

    @property
    def view_radius(self) -> int:
        return int(self.scenario.get("view_radius", 2))

    @property
    def num_channels(self) -> int:
        return int(self.scenario.get("num_channels", 4))


def build_episode_components(
    scenario: Mapping[str, Any],
    *,
    duration_fallback: int,
    strict_physics: bool = False,
    with_lifecycle: bool = False,
    world_seed: int | None = None,
) -> EpisodeComponents:
    """Assemble the world, its rules, its schedule and its physics.

    `strict_physics` is the sandbox's rule and it is the better one: a world
    whose physics is not declared is a world nobody designed, and substituting
    zero is how an organism ran 1200 steps with no energy cost and no reward.
    The controller keeps the permissive path because its defaults are baked into
    the behaviour fixture, and changing them here would be a physics decision
    smuggled in as a refactor.

    `duration_fallback` is a parameter rather than a constant because the two
    callers genuinely differ -- one bounds the episode by the campaign limit and
    the other by a scenario default. That is orchestration, and orchestration is
    allowed to differ; what may not differ is what happens inside a step.

    `with_lifecycle` is declared by the caller rather than inferred, so that a
    surface which does not run opportunity respawn has to say so rather than
    omit it silently, which is exactly how the sandbox came to execute a world
    the scenario never described.
    """
    if strict_physics:
        missing = [key for key in ("duration", "max_energy", "step_energy_cost",
                                   "expose_time_fraction") if key not in scenario]
        if missing:
            raise WorldPhysicsNotDeclared(f"WORLD_PHYSICS_NOT_DECLARED: {sorted(missing)}")

    world = WorldStateManager(
        build_world_state(dict(scenario)),
        scenario.get("duration", duration_fallback),
        scenario.get("max_energy", 100.0),
        scenario.get("step_energy_cost", 0.0),
        scenario.get("expose_time_fraction", True),
    )
    rules = RuleEngine()
    rules.load_rules(scenario.get("rules", {}))
    world.set_rules_version(rules.version)

    lifecycle: OpportunityLifecycle | None = None
    if with_lifecycle:
        seed = world_seed if world_seed is not None else int(scenario.get("world_seed", 0))
        lifecycle = OpportunityLifecycle(scenario.get("opportunity_lifecycle", {}), seed)
        lifecycle.register_initial(world)

    return EpisodeComponents(
        world=world, rules=rules,
        scheduler=ChangeScheduler(scenario.get("changes", []), rules),
        physics=Physics(), scenario=scenario, lifecycle=lifecycle,
    )
