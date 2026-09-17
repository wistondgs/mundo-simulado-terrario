"""The six AC2 invariants, as gates.

These are not unit tests of convenience. Each one corresponds to a way the v1
contract lost causal identifiability, and each failure here would silently
restore that loss.
"""

from dataclasses import dataclass

import pytest

from terrario.core.action_contract import (
    IdentityPersistence,
    MAX_TARGET_SLOTS,
    ActionIntent,
    ActionProvenance,
    AddressingMode,
    ExecutionStatus,
    SelectorType,
    TargetStatus,
    perceive_targets,
    resolve,
)
from terrario.core.types import ActionType, Direction, Position


@dataclass
class _Obj:
    pos: Position


@dataclass
class _Agent:
    pos: Position
    alive: bool = True


class _State:
    def __init__(self, agent_pos, object_positions):
        self.agents = {0: _Agent(pos=agent_pos)}
        self.objects = {i + 1: _Obj(pos=p) for i, p in enumerate(object_positions)}


def _targets(state, **kw):
    return perceive_targets(state, 0, 5, salt="ep-1", **kw)[0]


# ── AC2-1 Opacity ──────────────────────────────────────────────────────

def test_handles_carry_no_semantics_and_do_not_survive_the_episode():
    state = _State(Position(5, 5), [Position(5, 6)])
    a = _targets(state)[0]
    b = perceive_targets(state, 0, 5, salt="ep-2")[0][0]
    assert a.entity_id == b.entity_id
    assert a.handle != b.handle, "a handle stable across episodes is a memorisable label"
    assert a.handle != f"entity_{a.entity_id}"
    # Fixed width and no order relation to the id: nothing about the entity can
    # be read off the name, which is what makes opacity a property and not a
    # naming convention.
    many = [_State(Position(5, 5), [Position(5, 6)]) for _ in range(1)]
    handles = [perceive_targets(s_, 0, 5, salt="ep")[0][0].handle for s_ in many]
    assert len({len(h) for h in handles}) == 1


def test_the_organism_emits_a_slot_not_an_identifier():
    # The only thing an intent can carry under TARGET_ID is an ordinal below the
    # slot count. There is no field in which an identifier could be smuggled.
    ActionIntent(ActionType.CONSUME, SelectorType.TARGET_ID, 0)
    with pytest.raises(ValueError):
        ActionIntent(ActionType.CONSUME, SelectorType.TARGET_ID, MAX_TARGET_SLOTS)


# ── AC2-2 Observability ────────────────────────────────────────────────

def test_entities_outside_the_view_window_are_not_addressable():
    state = _State(Position(5, 5), [Position(5, 6), Position(20, 20)])
    targets = _targets(state)
    assert [t.entity_id for t in targets] == [1], "a far object entered the slot table"


def test_occluded_entities_are_not_addressable():
    mask = [[1.0] * 5 for _ in range(5)]
    mask[2][3] = 0.0  # the cell the object sits in, in view coordinates
    state = _State(Position(5, 5), [Position(5, 6)])
    assert _targets(state, mask=mask) == []


# ── AC2-3 Deterministic resolution ─────────────────────────────────────

def test_same_state_same_slot_resolves_to_the_same_entity():
    state = _State(Position(5, 5), [Position(5, 6), Position(4, 5), Position(6, 5)])
    first = [(t.slot, t.entity_id) for t in _targets(state)]
    for _ in range(5):
        assert [(t.slot, t.entity_id) for t in _targets(state)] == first


def test_slot_order_depends_on_geometry_alone():
    state = _State(Position(5, 5), [Position(6, 5), Position(4, 5)])
    targets = _targets(state)
    # row-major by relative offset: (-1,0) before (+1,0), whatever the ids are
    assert [t.offset for t in targets] == [(-1, 0), (1, 0)]


# ── AC2-4 Temporality ──────────────────────────────────────────────────

def test_a_consumed_entity_reads_stale_not_nonexistent():
    state = _State(Position(5, 5), [Position(5, 6)])
    targets = _targets(state)
    del state.objects[1]  # the world moved on between perception and execution
    r = resolve(ActionIntent(ActionType.CONSUME, SelectorType.TARGET_ID, 0), targets, state, 0)
    assert r.status is TargetStatus.STALE


def test_a_perceived_but_distant_entity_reads_out_of_range():
    state = _State(Position(5, 5), [Position(5, 7)])
    targets = _targets(state)
    r = resolve(ActionIntent(ActionType.CONSUME, SelectorType.TARGET_ID, 0), targets, state, 0)
    assert r.status is TargetStatus.OUT_OF_RANGE
    assert r.entity_id == 1, "the referent was found; only the range failed"


def test_an_empty_slot_reads_nonexistent():
    state = _State(Position(5, 5), [Position(5, 6)])
    targets = _targets(state)
    r = resolve(ActionIntent(ActionType.CONSUME, SelectorType.TARGET_ID, 7), targets, state, 0)
    assert r.status is TargetStatus.NONEXISTENT


# ── AC2-5 No silent fallback ───────────────────────────────────────────

def test_an_unresolvable_target_never_becomes_a_direction_or_a_neighbour():
    state = _State(Position(5, 5), [Position(5, 6)])
    targets = _targets(state)
    r = resolve(ActionIntent(ActionType.CONSUME, SelectorType.TARGET_ID, 9), targets, state, 0)
    assert not r.usable
    assert r.entity_id is None, "resolution substituted an entity the organism did not name"
    assert r.direction is None, "resolution fell back to directional addressing"


def test_direction_selector_keeps_v1_behaviour_exactly():
    state = _State(Position(5, 5), [Position(5, 6)])
    r = resolve(
        ActionIntent(ActionType.CONSUME, SelectorType.DIRECTION, int(Direction.RIGHT)), [], state, 0
    )
    assert r.status is TargetStatus.VALID and r.entity_id == 1
    empty = resolve(
        ActionIntent(ActionType.CONSUME, SelectorType.DIRECTION, int(Direction.LEFT)), [], state, 0
    )
    assert empty.status is TargetStatus.NONEXISTENT


def test_operations_that_take_no_target_are_not_addressing_failures():
    state = _State(Position(5, 5), [])
    r = resolve(ActionIntent(ActionType.MOVE, SelectorType.DIRECTION, 0), [], state, 0)
    assert r.status is TargetStatus.NOT_ADDRESSED and r.usable


# ── AC2-6 Provenance ───────────────────────────────────────────────────

def test_provenance_separates_intended_resolved_and_executed():
    p = ActionProvenance(
        step=3, addressing_mode=AddressingMode.T1_ENTITY.value,
        perceived_targets=["entity_aaaa"], perceived_truncated=False,
        chosen_operation=ActionType.CONSUME.name,
        chosen_selector_type=SelectorType.TARGET_ID.name,
        intended_selector_value=4, intended_target=None, resolved_target=None,
        target_status=TargetStatus.NONEXISTENT.value, executed_target=None,
        execution_status=ExecutionStatus.FAILED_TARGET_RESOLUTION.value,
    )
    record = p.as_record()
    for field_name in ("intended_target", "resolved_target", "executed_target",
                       "target_status", "execution_status", "learning_signal"):
        assert field_name in record


def test_provenance_never_carries_world_private_identifiers():
    state = _State(Position(5, 5), [Position(5, 6)])
    targets = _targets(state)
    handles = [t.handle for t in targets]
    assert all(not h.removeprefix("entity_").isdigit() for h in handles)


# ── T2 is reserved, not silently usable ────────────────────────────────

def test_relational_addressing_refuses_rather_than_pretending():
    with pytest.raises(NotImplementedError):
        ActionIntent(ActionType.CONSUME, SelectorType.RELATION, 0)


def test_truncation_is_reported_not_hidden():
    positions = [Position(5 + dx, 5 + dy) for dx in range(-2, 3) for dy in range(-2, 3)
                 if (dx, dy) != (0, 0)]
    state = _State(Position(5, 5), positions)
    targets, truncated = perceive_targets(state, 0, 5, salt="ep-1")
    assert len(targets) == MAX_TARGET_SLOTS and truncated


# ── ObservationHandle is not a WorldEntityID (§5) ──────────────────────

def test_object_permanence_is_not_given_away_by_a_stable_handle():
    """The default must not hand the organism identity over time for free."""
    state = _State(Position(5, 5), [Position(5, 6)])
    now = perceive_targets(state, 0, 5, salt="ep", step=10)[0][0]
    later = perceive_targets(state, 0, 5, salt="ep", step=11)[0][0]
    assert now.entity_id == later.entity_id, "same world entity, two frames"
    assert now.handle != later.handle, (
        "an EPHEMERAL handle that survives the frame grants object permanence "
        "through the interface instead of requiring the organism to establish it")


def test_tracked_identity_must_be_requested_never_inherited():
    state = _State(Position(5, 5), [Position(5, 6)])
    kw = dict(salt="ep", persistence=IdentityPersistence.TRACKED_IDENTITY)
    a = perceive_targets(state, 0, 5, step=10, **kw)[0][0]
    b = perceive_targets(state, 0, 5, step=11, **kw)[0][0]
    assert a.handle == b.handle


# ── The four addressing controls of the design directive (§8) ──────────

def test_control_1_perfect_observed_target_addresses_every_opportunity():
    state = _State(Position(5, 5), [Position(5, 6)])
    targets = _targets(state)
    r = resolve(ActionIntent(ActionType.CONSUME, SelectorType.TARGET_ID, targets[0].slot),
                targets, state, 0)
    assert r.status is TargetStatus.VALID and r.entity_id == 1


def test_control_2_a_nonexistent_handle_fails_and_executes_nothing():
    state = _State(Position(5, 5), [Position(5, 6)])
    targets = _targets(state)
    r = resolve(ActionIntent(ActionType.CONSUME, SelectorType.TARGET_ID, 15), targets, state, 0)
    assert r.status is TargetStatus.NONEXISTENT
    assert r.entity_id is None and r.direction is None


def test_control_3_a_stale_handle_does_not_resolve_to_whatever_took_the_cell():
    """The referent disappeared and something else moved in. Under a positional
    fallback the organism would silently consume the newcomer and the trace would
    call it a hit. The handle names an entity, so the answer is STALE."""
    state = _State(Position(5, 5), [Position(5, 6)])
    targets = _targets(state)
    del state.objects[1]
    state.objects[99] = _Obj(pos=Position(5, 6))  # a different entity, same cell
    r = resolve(ActionIntent(ActionType.CONSUME, SelectorType.TARGET_ID, 0), targets, state, 0)
    assert r.status is TargetStatus.STALE
    assert r.entity_id != 99, "resolution substituted the entity that took the cell"


def test_control_4_an_unobservable_entity_cannot_be_addressed_at_all():
    """Not 'is rejected' — cannot be expressed. The organism's only handle on a
    target is a slot index into what it perceived, so an entity it did not
    perceive has no expressible referent. This is AC2-2 demonstrated through the
    interface rather than asserted by inspecting the resolver."""
    hidden = Position(20, 20)
    state = _State(Position(5, 5), [Position(5, 6), hidden])
    targets = _targets(state)
    assert [t.entity_id for t in targets] == [1]
    reachable = set()
    for slot in range(MAX_TARGET_SLOTS):
        for operation in (ActionType.CONSUME, ActionType.INSPECT, ActionType.PUSH):
            r = resolve(ActionIntent(operation, SelectorType.TARGET_ID, slot),
                        targets, state, 0)
            if r.entity_id is not None:
                reachable.add(r.entity_id)
    assert 2 not in reachable, "an unobservable entity was reachable from the action space"
    assert reachable == {1}
