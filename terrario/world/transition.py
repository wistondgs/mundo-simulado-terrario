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

from terrario.core.action_contract import (
    ActionIntent, ActionProvenance, AddressingMode, ExecutionStatus, SelectorType,
    TARGET_BEARING_OPERATIONS, TargetStatus, perceive_targets, resolve,
)
from terrario.core.contracts import Transition
from terrario.core.rng import RNGManager
from terrario.core.types import (
    DIRECTION_DELTA, Action, ActionType, AgentState, Consequence, ObjectSpec, Position,
    WorldState,
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


# ── Contrato de Acción v2 ────────────────────────────────────────────────
#
# Estas tres funciones vivían en `lab/sandbox_runtime.py`, así que la ruta
# científica no las tenía: bajo T1 el organismo emitía `direction=NONE` y
# `target_id=-1`, y `find_target` buscaba en su propia celda. Todo CONSUME
# dirigido a una entidad fallaba en silencio. El brazo experimental T no podía
# correrse por la ruta autoritativa, y nadie lo sabía porque no fallaba: daba
# ceros plausibles.

def perceive_slot_table(world,obs,agent,step,world_seed):
    """The slot table, or None when this agent does not address entities."""
    mode=getattr(agent,"_addressing_mode",None)
    if mode is None or mode is AddressingMode.T0_DIRECTIONAL: return None
    return perceive_targets(world._mutable_state(),0,obs.channels.shape[-1],
                            salt=f"{world_seed}",step=step,mask=obs.mask)


def directional_provenance(world,action,step):
    """Provenance for a directional consume, so the two arms are comparable.

    Without this the waste decomposition exists only for T1 and the comparison
    is between a measured arm and an unmeasured one. Resolution is READ here and
    nothing is written back: T0 keeps the v1 physics path exactly, the faced-cell
    lookup, so the control arm stays byte-identical to every run that came before
    Action Contract v2.
    """
    if action.action_type not in TARGET_BEARING_OPERATIONS: return {}
    truth=world._mutable_state()
    res=resolve(ActionIntent(action.action_type,SelectorType.DIRECTION,int(action.direction)),
                [],truth,0)
    valid=res.status is TargetStatus.VALID
    return {"action_contract":ActionProvenance(step=step,
        addressing_mode=AddressingMode.T0_DIRECTIONAL.value,perceived_targets=[],
        perceived_truncated=False,chosen_operation=action.action_type.name,
        chosen_selector_type=SelectorType.DIRECTION.name,
        intended_selector_value=int(action.direction),
        intended_target=action.direction.name,resolved_target=str(res.entity_id) if valid else None,
        target_status=res.status.value,executed_target=str(res.entity_id) if valid else None,
        execution_status=(ExecutionStatus.EXECUTED.value if valid
            else ExecutionStatus.FAILED_TARGET_RESOLUTION.value)).as_record()}


def apply_action_contract(world,obs,action,agent,step,perceived):
    """Resolve the organism's intention against what it could actually perceive.

    Under T0 this is a no-op by construction: the directional contract needs no
    resolution layer, and the returned action is the one the agent emitted, so a
    T0 run is byte-identical to a run before Action Contract v2 existed. That
    matters -- T0 is the control arm, and a control that quietly changed would
    make the comparison meaningless.

    Under T1 the slot the organism named is resolved here, and ONLY a VALID
    resolution writes `target_id`. Everything else leaves it at -1 with the
    direction already pinned to NONE by the agent, so an unresolvable target
    consumes nothing rather than silently becoming a neighbour (AC2-5). The
    physics is untouched: it still reads `target_id`, it simply can no longer be
    handed an entity the organism never perceived (AC2-2), because the only
    writer is a resolution that came out of the agent's own view window.
    """
    if perceived is None: return action,directional_provenance(world,action,step)
    mode=getattr(agent,"_addressing_mode",AddressingMode.T1_ENTITY)
    truth=world._mutable_state()
    targets,truncated=perceived
    # An operation that addresses space rather than an entity -- MOVE, NOOP --
    # arrives in v1 shape even under T1, with the direction in `direction` and no
    # selector value. Normalising here keeps `Domain(s, O_t)` a property of the
    # operation instead of forcing every caller to remember it.
    selector=SelectorType(action.selector_type)
    value=action.selector_value if action.selector_value>=0 else int(action.direction)
    intent=ActionIntent(action.action_type,selector,value)
    res=resolve(intent,targets,truth,0)
    resolved=res.status is TargetStatus.VALID
    action.target_id=res.entity_id if resolved else -1
    prov=ActionProvenance(step=step,addressing_mode=mode.value,
        perceived_targets=[t.handle for t in targets],perceived_truncated=truncated,
        chosen_operation=action.action_type.name,chosen_selector_type=SelectorType(action.selector_type).name,
        intended_selector_value=action.selector_value,
        intended_target=next((t.handle for t in targets if t.slot==action.selector_value),None),
        resolved_target=res.handle if resolved else None,target_status=res.status.value,
        executed_target=res.handle if resolved else None,
        execution_status=(ExecutionStatus.EXECUTED.value if resolved else
            ExecutionStatus.NOT_APPLICABLE.value if res.status is TargetStatus.NOT_ADDRESSED
            else ExecutionStatus.FAILED_TARGET_RESOLUTION.value))
    return action,{"action_contract":prov.as_record()}


@dataclass
class StepOutcome:
    """Lo que ocurrió en un paso, para que cada superficie lo instrumente a su modo.

    Lleva más de lo que cualquiera de las dos necesita por separado, a propósito:
    lo que una superficie decida no registrar es asunto suyo, pero lo que ocurrió
    tiene que ser lo mismo para ambas o no hay una respuesta a «qué pasó».
    """

    step: int
    observation_t: Any
    action: Action
    provenance: Mapping[str, Any]
    change_events: list
    respawn_events: list
    target: ObjectSpec | None
    target_before: ObjectSpec | None
    effects: list
    energy_delta: float
    lifecycle_event: Any
    consequence: Consequence
    observation_t1: Any
    terminated: bool
    truncated: bool
    transition: Transition


def run_step(
    components: EpisodeComponents,
    agent: Any,
    step: int,
    *,
    world_seed: int,
    agent_seed: int,
    max_steps: int,
    learning_enabled: bool = True,
) -> StepOutcome:
    """Un paso, con la única semántica que ambas superficies ejecutan.

    El orden es el del controller —física antes de resolver el objetivo—, con el
    contrato de acción del banco y el ciclo de oportunidades que sólo el
    controller tenía. Cada pieza viene de la ruta que ya la hacía bien; ninguna
    se inventó aquí.

    La semilla de la física es `world_seed + step`, que es lo que el registro de
    mundos declara: *world seed materializes layout; agent seed is independently
    offset*. El controller usaba `agent_seed + step`, lo que ataría los shocks
    exógenos futuros a qué agente corre. Hoy es inerte porque `Physics.step` no
    consume su RNG, y por eso canonizarlo ahora es gratis y después no lo sería.

    El llamante comprueba que el organismo siga vivo antes de llamar. No se
    decide aquí porque lo que sigue a la muerte es orquestación: el controller
    rompe el bucle y el banco transiciona a COMPLETED, y ninguna de las dos es
    más correcta que la otra.
    """
    world, rules, scheduler = components.world, components.rules, components.scheduler
    lifecycle = components.lifecycle
    view_radius, channels = components.view_radius, components.num_channels

    observation_t = world.get_observation(0, view_radius, channels)
    agent.perceive(observation_t)

    targets = perceive_slot_table(world, observation_t, agent, step, world_seed)
    if targets is not None and hasattr(agent, "offer_targets"):
        agent.offer_targets(targets[0])
    action = agent.decide()
    action, provenance = apply_action_contract(
        world, observation_t, action, agent, step, targets)

    change_events = scheduler.check(world, step=step)
    respawn_events = lifecycle.advance(world, step) if lifecycle is not None else []

    physical = components.physics.step(world, {0: action}, RNGManager(world_seed + step))
    target = find_target(world, 0, action)
    target_before = target.clone() if target is not None else None

    effects = rules.evaluate(world, 0, action, target)
    application = (rules.apply_effects_detailed(world, 0, target.object_id, effects)
                   if target else None)
    energy_delta = application.realized if application is not None else 0.0
    requested_delta = application.requested if application is not None else 0.0
    energy_before = (application.energy_before if application is not None
                     else world._mutable_state().agents[0].energy)

    lifecycle_event = None
    if (lifecycle is not None and target_before is not None
            and target_before.object_id not in world._mutable_state().objects):
        lifecycle_event = lifecycle.consume(world, target_before, step)

    # El coste de paso es igual pedido que realizado: sólo baja, y el suelo no
    # se recorta. Lo único que el techo puede morder es el efecto de las reglas.
    step_cost = world.apply_step_energy_cost(0)
    energy_delta += step_cost

    consequence = physical.get(0, Consequence(energy_delta=energy_delta, events=[]))
    consequence.energy_delta = energy_delta
    consequence.requested_energy_delta = requested_delta + step_cost
    consequence.energy_before = energy_before
    consequence.energy_after = world._mutable_state().agents[0].energy
    observation_t1 = world.get_observation(0, view_radius, channels)
    terminated = not world._mutable_state().agents[0].alive
    truncated = step + 1 >= max_steps
    consequence.new_observation = observation_t1
    consequence.done = terminated or truncated

    transition = Transition(
        observation_t, str(agent.get_internal_state()), action, consequence,
        observation_t1, terminated, truncated, step, agent_seed)
    if learning_enabled:
        agent.learn(transition)

    return StepOutcome(
        step=step, observation_t=observation_t, action=action, provenance=provenance,
        change_events=list(change_events), respawn_events=list(respawn_events),
        target=target, target_before=target_before, effects=list(effects),
        energy_delta=energy_delta, lifecycle_event=lifecycle_event,
        consequence=consequence, observation_t1=observation_t1,
        terminated=terminated, truncated=truncated, transition=transition,
    )
