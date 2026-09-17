"""A bank of world states that no policy produced, and the test it enables.

Every quantity measured during a rollout is endogenous. Opportunity is a
function of the world AND of everything the organism did before:

    O_t = f(W_0, A_{0:t-1})

An arm that consumes well destroys its own future opportunities; one that never
resolves stays surrounded and reports 1.0. Locomotion is no better -- distance
travelled, cells visited and movement events are all consequences of which action
the policy settled on. Restricting to an opening window shrinks the problem and
does not remove it: after the first divergent action the states differ.

So affordance and experience are separated for good:

    exogenous_affordance_rate     what the WORLD offers, measured on states no
                                  policy produced. A property of the scenario.
    experienced_opportunity_rate  what the organism's own trajectory produced or
                                  destroyed. An outcome, and a mediator -- never
                                  an initial condition.

The bank is built by placing the agent at sampled free cells of a freshly
instantiated world. No action is ever taken, so the states depend on the
scenario and on the bank's own seed and on nothing else. Both addressing
contracts then answer questions about the SAME states.
"""

from __future__ import annotations

import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from terrario.core.action_contract import (
    ActionIntent,
    AddressingMode,
    ArgumentRole,
    SelectorType,
    TargetStatus,
    allowed_selectors,
    perceive_targets,
    resolve,
)
from terrario.core.types import DIRECTION_DELTA, ActionType, Direction, Position
from terrario.experiment.controller import build_world_state, materialize_scenario
from terrario.lab.measurement_status import Reading, ratio


@dataclass
class Snapshot:
    state: Any
    agent_pos: Position
    label: str


def build_bank(scenario: Mapping[str, Any], *, seeds: Sequence[int],
               per_seed: int = 40, bank_seed: int = 20260917) -> list[Snapshot]:
    """States sampled from the world itself, never from a trajectory."""
    rng = random.Random(bank_seed)
    bank: list[Snapshot] = []
    for seed in seeds:
        # The layout is procedural: `objects` is empty in the template and the
        # world seed materialises it. Building from the template alone gave an
        # empty world and an affordance rate of exactly zero -- a bank of 180
        # states with nothing in them, which would have "proved" that neither
        # contract can express anything.
        spec = materialize_scenario(dict(scenario), seed)
        state = build_world_state(spec)
        occupied = {(o.pos.x, o.pos.y) for o in state.objects.values()}
        free = [(x, y) for x in range(state.grid_height) for y in range(state.grid_width)
                if (x, y) not in occupied]
        if not free:
            continue
        for index in range(per_seed):
            x, y = rng.choice(free)
            snapshot = build_world_state(spec)
            agent = snapshot.agents.get(0)
            if agent is None:
                continue
            agent.pos = Position(x, y)
            bank.append(Snapshot(snapshot, Position(x, y), f"seed{seed}#{index}"))
    return bank


def exogenous_affordance_rate(bank: Sequence[Snapshot]) -> Reading:
    """How much opportunity the WORLD offers, independent of any behaviour."""
    with_neighbour = sum(1 for s in bank if _adjacent(s.state, 0))
    return ratio(with_neighbour, len(bank), what="exogenous affordance")


def _adjacent(state, agent_id: int) -> list[int]:
    agent = state.agents.get(agent_id)
    if agent is None:
        return []
    return [eid for eid, obj in state.objects.items()
            if abs(obj.pos.x - agent.pos.x) + abs(obj.pos.y - agent.pos.y) == 1]


def intention_representability(bank: Sequence[Snapshot], mode: AddressingMode,
                               *, view_size: int = 5) -> dict[str, Any]:
    """Can the action space EXPRESS a known intention at all?

        R_T(I, s) = 1  iff  exists a in A_T such that Execute(s, a) realises I

    This is the test that was missing, and it separates two claims that have been
    running together. A measured addressing rate of 2-4% -- chance -- shows that
    the agent did not LEARN to use the channel. It does not show that the channel
    could not express the target. If exactly one object sits UP, then CONSUME(UP)
    already says "consume that object", and v1 was expressive after all.

    If Representability(T0) ~ 1 and Representability(T1) ~ 1, there was no
    expressive impossibility, and the defect lives in learning, credit assignment
    or policy stability -- a more interesting defect, and a different research
    programme. Only if Representability(T0) << 1 while Representability(T1) ~ 1
    may we say the v1 contract PREVENTED realising intentions that v2 makes
    realisable.

    The intentions enumerated are the ones the physics can realise at all:
    consuming an entity in contact. Realisation is checked through the same
    resolver the runtime uses, never through a second implementation of it.
    """
    roles = allowed_selectors(ActionType.CONSUME)
    entity_mode = (mode is AddressingMode.T1_ENTITY
                   and ArgumentRole.OBSERVED_ENTITY in roles)
    total = realisable = 0
    unrepresentable: list[dict[str, Any]] = []
    for snapshot in bank:
        state = snapshot.state
        for entity_id in _adjacent(state, 0):
            total += 1
            if entity_mode:
                targets, truncated = perceive_targets(
                    state, 0, view_size, salt=snapshot.label, step=0)
                slot = next((t.slot for t in targets if t.entity_id == entity_id), None)
                ok = slot is not None and resolve(
                    ActionIntent(ActionType.CONSUME, SelectorType.TARGET_ID, slot),
                    targets, state, 0).status is TargetStatus.VALID
                reason = "TRUNCATED_OUT_OF_SLOT_TABLE" if truncated and slot is None \
                    else "NOT_PERCEIVED"
            else:
                ok = False
                reason = "NO_DIRECTION_REACHES_IT"
                agent = state.agents[0]
                obj = state.objects[entity_id]
                for direction in Direction:
                    dx, dy = DIRECTION_DELTA[direction]
                    if (agent.pos.x + dx, agent.pos.y + dy) == (obj.pos.x, obj.pos.y):
                        ok = resolve(
                            ActionIntent(ActionType.CONSUME, SelectorType.DIRECTION,
                                         int(direction)),
                            [], state, 0).entity_id == entity_id
                        break
            if ok:
                realisable += 1
            elif len(unrepresentable) < 10:
                unrepresentable.append({"snapshot": snapshot.label,
                                        "entity": entity_id, "reason": reason})
    return {"mode": mode.value,
            "representability": ratio(realisable, total,
                                      what=f"representability under {mode.value}").as_record(),
            "intentions": total, "realisable": realisable,
            "unrepresentable_examples": unrepresentable}
