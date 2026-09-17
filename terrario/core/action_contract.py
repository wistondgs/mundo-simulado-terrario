"""Action Contract v2 — the action as a factored structure, not a flat integer.

Under v1 an action was one integer in [0, 25): `action_type * 5 + direction`.
`Action` carried a `target_id` field, but `to_int`/`from_int` dropped it, so
nothing the agent could emit ever reached it. The organism could say CONSUME-UP;
it could not say "consume *that*". Measured addressing rate was 2-4% — chance.

v2 factors the action into three parts:

    a_t = (o_t, s_t, v_t)      operation, selector type, selector value

`o_t` keeps its v1 meaning: CONSUME still means consume. What changes is how the
operation finds its object. `s_t` is the axis the experiment varies:

    T0  DIRECTION   selector value is a Direction     (v1 behaviour, exactly)
    T1  TARGET_ID   selector value is a perception slot
    T2  RELATION    selector value names a relation   (reserved, not implemented)

T2 is not built. It is declared here so that the contract does not foreclose it:
"the object blocking the route", "the most uncertain object", "the newest member
of a class" are selections that are neither a direction nor a fixed identity, and
Genesis will need to express them. A two-valued selector enum would have had to
be widened later; a three-valued one with a reserved arm does not.

Six invariants, each enforced somewhere in this module:

AC2-1 OPACITY        The organism emits a slot index, never an identifier. It
                     cannot read `food_good_17` off its own action because no
                     identifier is ever handed to it — only an ordinal position
                     in what it perceived. Opacity is structural, not a naming
                     convention. Handles exist for provenance and are salted per
                     episode so they cannot be memorised across episodes.
AC2-2 OBSERVABILITY  Slots are built only from entities inside the agent's view
                     window and unoccluded by its own mask. `target ∈ Observable`,
                     never `target ∈ WorldEntities`. v1's `target_id` path read
                     `world.objects[id]` directly — omniscience — and is replaced.
AC2-3 DETERMINISM    Same state + same agent + same slot resolves to the same
                     entity. Slot order is row-major over the view window, which
                     depends on geometry the agent already perceives and on
                     nothing else. Required for replay, twins and causal claims.
AC2-4 TEMPORALITY    A slot valid at t need not be valid at t+1. Resolution
                     returns VALID / STALE / OUT_OF_RANGE / OCCLUDED /
                     NONEXISTENT. A world that moved is not a cognitive error,
                     and the status says which of the two happened.
AC2-5 NO FALLBACK    An unresolvable CONSUME(slot) does NOT become CONSUME(UP) or
                     "consume the nearest". It fails, loudly, as
                     FAILED_TARGET_RESOLUTION, and intended/resolved/executed are
                     recorded separately. Silent repair is what destroys
                     identifiability.
AC2-6 PROVENANCE     `ActionProvenance` carries the whole chain for one step, so
                     the path from perception to learning signal can be
                     reconstructed after the fact rather than inferred.
"""

from __future__ import annotations

import enum
import hashlib
from dataclasses import dataclass, field
from typing import Any

from terrario.core.types import (
    NUM_ACTION_TYPES,
    NUM_DIRECTIONS,
    ActionType,
    Direction,
    Position,
)


class SelectorType(enum.IntEnum):
    """How an operation finds the thing it operates on."""

    DIRECTION = 0
    TARGET_ID = 1
    RELATION = 2  # RESERVED — see module docstring. Never emitted by any agent.


NUM_SELECTOR_TYPES = len(SelectorType)


class AddressingMode(enum.StrEnum):
    """Experimental factor T. One level per selector type."""

    T0_DIRECTIONAL = "T0_DIRECTIONAL"
    T1_ENTITY = "T1_ENTITY"
    T2_RELATIONAL = "T2_RELATIONAL"


SELECTOR_OF_MODE: dict[AddressingMode, SelectorType] = {
    AddressingMode.T0_DIRECTIONAL: SelectorType.DIRECTION,
    AddressingMode.T1_ENTITY: SelectorType.TARGET_ID,
    AddressingMode.T2_RELATIONAL: SelectorType.RELATION,
}

IMPLEMENTED_MODES = (AddressingMode.T0_DIRECTIONAL, AddressingMode.T1_ENTITY)


class IdentityPersistence(enum.StrEnum):
    """How long an ObservationHandle means the same thing. A cognitive choice.

    A handle belongs to the PERCEPTUAL space, not to the world:

        WorldEntityID  ->  ObservationHandle_t

    The organism sees `entity_6f21`; Terrario privately knows it names world
    entity 219. That indirection is what keeps the world's own identifiers out of
    the action channel, and it is also where object permanence gets decided.

    EPHEMERAL is the default, and deliberately the harsher one. The handle is
    re-minted every frame, so an organism cannot tell that the thing it sees now
    is the thing it saw before — it must establish that itself, from perception.
    A handle stable across frames would hand it object identity over time for
    free, and recognising "same object" is precisely a capability we mean to
    measure rather than to grant. Genesis will need that distinction to stay a
    finding rather than an artefact of the interface.

    TRACKED_IDENTITY exists for the case where a perceptual capability is meant
    to supply persistence. It must be requested, never inherited.
    """

    EPHEMERAL = "EPHEMERAL"
    TRACKED_IDENTITY = "TRACKED_IDENTITY"


class TargetStatus(enum.StrEnum):
    """Why a selector did or did not resolve. AC2-4."""

    VALID = "VALID"
    STALE = "STALE"              # the handle was real, the entity has since moved
    OUT_OF_RANGE = "OUT_OF_RANGE"  # resolved, but the operation needs adjacency
    OCCLUDED = "OCCLUDED"        # inside the window, hidden under the mask
    NONEXISTENT = "NONEXISTENT"  # no entity ever occupied that slot
    NOT_ADDRESSED = "NOT_ADDRESSED"  # operation takes no target (MOVE, NOOP)


class ExecutionStatus(enum.StrEnum):
    EXECUTED = "EXECUTED"
    FAILED_TARGET_RESOLUTION = "FAILED_TARGET_RESOLUTION"
    NOT_APPLICABLE = "NOT_APPLICABLE"


# Slots are a fixed-width channel: the selector head must have a constant output
# dimension. A 5x5 window holds up to 24 entities, more than fits. Perceiving
# more than MAX_TARGET_SLOTS entities truncates — and says so, rather than
# dropping the tail in silence.
MAX_TARGET_SLOTS = 16

class ArgumentRole(enum.StrEnum):
    """What KIND of argument an operation takes. Typed, per operation."""

    SPATIAL_DIRECTION = "SPATIAL_DIRECTION"
    OBSERVED_ENTITY = "OBSERVED_ENTITY"


#: Typed action schema:  Action = Operation + TypedArguments(Operation).
#:
#: A selector applied globally is too generic, and PUSH proved it. The domain of
#: a valid selector depends on the SEMANTICS of each operation, and those
#: semantics are read off the physics, not off intuition:
#:
#:   MOVE     `_handle_move` uses DIRECTION_DELTA and nothing else.
#:   PUSH     `_handle_push` pushes toward a direction and follows. Spatial.
#:   CONSUME  `_handle_consume` accepts EITHER an explicit target or the object
#:            in the faced direction. The only operation with two argument roles,
#:            and therefore the only place T can vary anything.
#:   INSPECT  `_handle_inspect` returns a constant event and reads NEITHER
#:            direction nor target. It has no argument semantics at all today,
#:            so giving it one would be inventing physics in the agent.
#:   NOOP     no arguments.
#:
#: The consequence is that T stops being "the whole agent addresses directions"
#: versus "the whole agent addresses entities", and becomes the narrow question
#: it should always have been: for the operation that is semantically aimed at an
#: entity, which representation realises the target? MOVE and PUSH are then
#: byte-identical across conditions, which is what the first two versions of this
#: contract destroyed.
ALLOWED_SELECTORS: dict[ActionType, frozenset[ArgumentRole]] = {
    ActionType.MOVE: frozenset({ArgumentRole.SPATIAL_DIRECTION}),
    ActionType.PUSH: frozenset({ArgumentRole.SPATIAL_DIRECTION}),
    ActionType.CONSUME: frozenset({ArgumentRole.SPATIAL_DIRECTION,
                                   ArgumentRole.OBSERVED_ENTITY}),
    ActionType.INSPECT: frozenset(),
    ActionType.NOOP: frozenset(),
}


def allowed_selectors(operation: ActionType) -> frozenset[ArgumentRole]:
    return ALLOWED_SELECTORS[operation]


def selector_for(operation: ActionType, mode: AddressingMode) -> SelectorType | None:
    """Which selector this operation uses under this addressing mode.

    Returns None for an operation that takes no argument, so a caller cannot
    accidentally hand one a direction the physics will ignore.
    """
    roles = ALLOWED_SELECTORS[operation]
    if not roles:
        return None
    if (mode is AddressingMode.T1_ENTITY
            and ArgumentRole.OBSERVED_ENTITY in roles):
        return SelectorType.TARGET_ID
    return SelectorType.DIRECTION


#: Operations whose selector is an entity rather than a place.
#:
#: CONSUME and INSPECT are about a THING: "eat that", "look at that". PUSH is
#: about a DIRECTION -- you push toward somewhere and whatever is there moves --
#: and MOVE and NOOP plainly address space. Putting PUSH on the entity side cost
#: the organism its main means of travel: under T0 it moved by pushing (158 of
#: 300 steps, 12 cells visited), and under entity-addressed PUSH those pushes
#: stopped resolving and it visited 2 cells with something adjacent at every
#: single step. T is supposed to vary how an intention is addressed and nothing
#: else; an arm that cannot walk is measuring a different organism.
TARGET_BEARING_OPERATIONS = frozenset(
    op for op, roles in ALLOWED_SELECTORS.items()
    if ArgumentRole.OBSERVED_ENTITY in roles)


@dataclass(frozen=True)
class PerceivedTarget:
    """One addressable entity, as the organism could have perceived it.

    `handle` is what provenance records. `entity_id` is the world's own id and is
    WORLD_PRIVATE: it lives here so resolution can do its job, and it must never
    be handed to the agent or written into an agent-perceptible field.
    """

    slot: int
    handle: str
    entity_id: int
    offset: tuple[int, int]  # relative to the agent, in view coordinates
    adjacent: bool


def _handle(salt: str, entity_id: int, step: int,
            persistence: IdentityPersistence) -> str:
    """Mint an ObservationHandle for one entity. AC2-1.

    Under EPHEMERAL the step enters the digest, so the same world entity wears a
    different handle on every frame and no amount of handle-watching yields
    object permanence. Under TRACKED_IDENTITY it does not, and the handle is
    stable for the episode.
    """
    scope = salt if persistence is IdentityPersistence.TRACKED_IDENTITY else f"{salt}:{step}"
    digest = hashlib.sha256(f"{scope}:{entity_id}".encode()).hexdigest()
    return f"entity_{digest[:8]}"


def perceive_targets(
    state: Any,
    agent_id: int,
    view_size: int,
    *,
    salt: str,
    step: int = 0,
    persistence: IdentityPersistence = IdentityPersistence.EPHEMERAL,
    mask: Any = None,
) -> tuple[list[PerceivedTarget], bool]:
    """Build the slot table from what this agent can actually see. AC2-2, AC2-3.

    Returns the targets and whether the list was truncated by MAX_TARGET_SLOTS.

    Order is row-major over the view window: deterministic, and derived from
    geometry the agent already receives through its channels. It encodes no
    property of the entity — an object's slot says where it is, never what it is.
    """
    agent = state.agents.get(agent_id)
    if agent is None or not agent.alive:
        return [], False

    half = view_size // 2
    found: list[tuple[tuple[int, int], int]] = []
    for entity_id, obj in state.objects.items():
        dx = obj.pos.x - agent.pos.x
        dy = obj.pos.y - agent.pos.y
        if abs(dx) > half or abs(dy) > half:
            continue
        if mask is not None and not _visible(mask, dx + half, dy + half):
            continue
        found.append(((dx, dy), entity_id))

    # Ordered by distance first, then row-major to break ties. AC2-3.
    #
    # Both orderings are pure geometry -- neither says anything about WHAT an
    # entity is, only where it sits, which the organism already receives through
    # its channels. The reason to prefer distance is that row-major over
    # OCCUPIED cells is non-stationary: the same physical neighbour wears a
    # different slot depending on what else happens to be in view, so there is no
    # stable thing for a selector head to learn in the seven informative steps a
    # lifetime affords. Under distance ordering the thing in contact is slot 0
    # nearly always.
    #
    # This is a design choice that favours T1, and it is recorded as one. It does
    # not hand the organism the answer: slot 0 is the nearest entity whether that
    # entity is food or poison, and choosing to act on it is still a decision
    # about what, not merely where.
    found.sort(key=lambda item: (abs(item[0][0]) + abs(item[0][1]), item[0]))
    truncated = len(found) > MAX_TARGET_SLOTS
    targets = [
        PerceivedTarget(
            slot=slot,
            handle=_handle(salt, entity_id, step, persistence),
            entity_id=entity_id,
            offset=offset,
            adjacent=abs(offset[0]) + abs(offset[1]) == 1,
        )
        for slot, (offset, entity_id) in enumerate(found[:MAX_TARGET_SLOTS])
    ]
    return targets, truncated


def _visible(mask: Any, row: int, col: int) -> bool:
    try:
        return bool(mask[row][col])
    except (IndexError, TypeError):
        return True


@dataclass(frozen=True)
class ActionIntent:
    """What the organism meant. Pre-resolution, pre-execution."""

    operation: ActionType
    selector_type: SelectorType
    selector_value: int

    def __post_init__(self) -> None:
        if self.selector_type is SelectorType.RELATION:
            raise NotImplementedError(
                "SelectorType.RELATION is reserved for T2 and has no resolver yet. "
                "It exists so the contract does not have to be widened later."
            )
        limit = NUM_DIRECTIONS if self.selector_type is SelectorType.DIRECTION else MAX_TARGET_SLOTS
        if not 0 <= self.selector_value < limit:
            raise ValueError(
                f"selector_value {self.selector_value} outside [0, {limit}) "
                f"for {self.selector_type.name}"
            )


@dataclass
class Resolution:
    """What the intent turned out to refer to. AC2-4, AC2-5."""

    status: TargetStatus
    entity_id: int | None = None
    handle: str | None = None
    direction: Direction | None = None

    @property
    def usable(self) -> bool:
        return self.status in (TargetStatus.VALID, TargetStatus.NOT_ADDRESSED)


def resolve(
    intent: ActionIntent,
    targets: list[PerceivedTarget],
    state: Any,
    agent_id: int,
) -> Resolution:
    """Turn an intent into a concrete referent — or refuse, with a reason.

    This function never substitutes. If the slot the organism named is empty, the
    answer is NONEXISTENT; it is not "the nearest object", and it is not UP.
    AC2-5 is the whole point: a repaired action makes the addressing rate
    unmeasurable, because every miss would score as a hit.
    """
    if intent.selector_type is SelectorType.DIRECTION:
        direction = Direction(intent.selector_value)
        if intent.operation not in TARGET_BEARING_OPERATIONS:
            return Resolution(TargetStatus.NOT_ADDRESSED, direction=direction)
        agent = state.agents.get(agent_id)
        if agent is None:
            return Resolution(TargetStatus.NONEXISTENT, direction=direction)
        from terrario.core.types import DIRECTION_DELTA

        target_pos = agent.pos + DIRECTION_DELTA[direction]
        for entity_id, obj in state.objects.items():
            if obj.pos.x == target_pos.x and obj.pos.y == target_pos.y:
                return Resolution(TargetStatus.VALID, entity_id=entity_id, direction=direction)
        return Resolution(TargetStatus.NONEXISTENT, direction=direction)

    # TARGET_ID
    if intent.operation not in TARGET_BEARING_OPERATIONS:
        return Resolution(TargetStatus.NOT_ADDRESSED)

    slot = intent.selector_value
    chosen = next((t for t in targets if t.slot == slot), None)
    if chosen is None:
        return Resolution(TargetStatus.NONEXISTENT)

    obj = state.objects.get(chosen.entity_id)
    if obj is None:
        return Resolution(TargetStatus.STALE, entity_id=chosen.entity_id, handle=chosen.handle)

    agent = state.agents.get(agent_id)
    if agent is None:
        return Resolution(TargetStatus.STALE, entity_id=chosen.entity_id, handle=chosen.handle)

    live_adjacent = abs(obj.pos.x - agent.pos.x) + abs(obj.pos.y - agent.pos.y) == 1
    if not live_adjacent:
        # The entity is real and perceived; the operation simply needs contact.
        # That is a range fact about the world, not a failure of the organism to
        # refer — which is why it is OUT_OF_RANGE and not NONEXISTENT.
        return Resolution(
            TargetStatus.OUT_OF_RANGE, entity_id=chosen.entity_id, handle=chosen.handle
        )
    return Resolution(TargetStatus.VALID, entity_id=chosen.entity_id, handle=chosen.handle)


@dataclass
class ActionProvenance:
    """The whole chain for one step. AC2-6.

    Written per step so that afterwards nobody has to infer where the organism
    lost the thread. Every field is separately recorded on purpose: collapsing
    intended and executed into one 'action' column is exactly how v1 made the
    bottleneck invisible.
    """

    step: int
    addressing_mode: str
    perceived_targets: list[str]           # handles, never entity ids
    perceived_truncated: bool
    chosen_operation: str
    chosen_selector_type: str
    intended_selector_value: int
    intended_target: str | None
    resolved_target: str | None
    target_status: str
    executed_target: str | None
    execution_status: str
    outcome_events: list[str] = field(default_factory=list)
    learning_signal: float | None = None

    def as_record(self) -> dict[str, Any]:
        return {
            "step": self.step,
            "addressing_mode": self.addressing_mode,
            "perceived_targets": list(self.perceived_targets),
            "perceived_truncated": self.perceived_truncated,
            "chosen_operation": self.chosen_operation,
            "chosen_selector_type": self.chosen_selector_type,
            "intended_selector_value": self.intended_selector_value,
            "intended_target": self.intended_target,
            "resolved_target": self.resolved_target,
            "target_status": self.target_status,
            "executed_target": self.executed_target,
            "execution_status": self.execution_status,
            "outcome_events": list(self.outcome_events),
            "learning_signal": self.learning_signal,
        }
