"""One step, one snapshot, two contracts — and a gate that refuses the rest.

A closed-loop comparison of T0 against T1 runs into a loop with no exit:

    T changes -> the trajectory changes -> opportunities change -> objects
    disappear -> locomotion changes -> nobody can say what caused what

Three versions of this contract were confounded before anybody noticed, and each
produced a plausible number rather than an error. So the effect of the selector
is measured where the loop cannot close: ONE step, on a state neither arm
produced, with everything before the selector held identical.

                        SAME STATE s_t
                             |
                       SAME COGNITION
                             |
                        SAME PLANNER
                             |
                       SAME OPERATION
                             |
                   +---------+---------+
                   |                   |
                  T0                  T1
              direction           typed target
                   |                   |
                   +---------+---------+
                             |
                       compare resolver

`first_divergence` is the structural gate. For a paired snapshot it walks the
chain in order and reports where the two arms first differ. Anything earlier
than the selector representation means the intervention was not isolated, and
the verdict is INTERVENTION_ISOLATION = FAIL. It would have stopped, without a
single rollout, every version that omitted the planner, that transformed PUSH,
that discarded the planner's direction, or that initialised a head with a
different behavioural distribution.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any

from terrario.core.action_contract import (
    ActionIntent,
    AddressingMode,
    SelectorType,
    TargetStatus,
    perceive_targets,
    resolve,
)
from terrario.core.types import DIRECTION_DELTA, ActionType, Direction
from terrario.lab.measurement_status import Reading, ratio

#: The chain, in the order the gate walks it. The first permitted difference is
#: the last entry; a difference at any earlier link fails isolation.
CHAIN = ("observation_hash", "world_model_state", "memory_state", "planner_state",
         "operation", "pre_selector_intention", "selector_representation")

FIRST_PERMITTED = "selector_representation"


@dataclass
class PairedStep:
    snapshot_label: str
    t0: dict[str, Any]
    t1: dict[str, Any]


def first_divergence(pair: PairedStep) -> dict[str, Any]:
    """Where the two arms first differ, and whether that is allowed."""
    for link in CHAIN:
        if pair.t0.get(link) != pair.t1.get(link):
            return {
                "snapshot": pair.snapshot_label, "first_divergence": link,
                "verdict": "PASS" if link == FIRST_PERMITTED else "FAIL",
                "t0": pair.t0.get(link), "t1": pair.t1.get(link),
            }
    return {"snapshot": pair.snapshot_label, "first_divergence": None,
            "verdict": "PASS",
            "note": "the arms did not differ at all, which happens when the operation "
                    "takes no entity argument -- MOVE, PUSH, NOOP, INSPECT are "
                    "byte-identical across T by the typed schema"}


def isolation_verdict(pairs: Sequence[PairedStep]) -> dict[str, Any]:
    results = [first_divergence(p) for p in pairs]
    failures = [r for r in results if r["verdict"] == "FAIL"]
    return {
        "INTERVENTION_ISOLATION": "PASS" if not failures else "FAIL",
        "pairs": len(results), "failures": len(failures),
        "first_failures": failures[:5],
        "rule": f"the first permitted difference is {FIRST_PERMITTED}; a difference at "
                f"any earlier link means T changed something other than addressing, and "
                f"no rollout length repairs that",
    }


def selector_outcome(state: Any, agent_id: int, operation: ActionType,
                     mode: AddressingMode, choice: int, *, view_size: int,
                     salt: str, step: int) -> dict[str, Any]:
    """Resolve one operation under one contract, without advancing the world."""
    if mode is AddressingMode.T0_DIRECTIONAL:
        intent = ActionIntent(operation, SelectorType.DIRECTION, choice)
        res = resolve(intent, [], state, agent_id)
        representation = ("DIRECTION", Direction(choice).name)
    else:
        targets, _ = perceive_targets(state, agent_id, view_size, salt=salt, step=step)
        intent = ActionIntent(operation, SelectorType.TARGET_ID, choice)
        res = resolve(intent, targets, state, agent_id)
        representation = ("TARGET_ID", choice)
    return {"selector_representation": representation, "target_status": res.status.value,
            "resolved_entity": res.entity_id, "resolvable": res.status is TargetStatus.VALID}


def direction_to(state: Any, agent_id: int, entity_id: int) -> int | None:
    """The direction that reaches an entity, or None. Used for parity."""
    agent = state.agents.get(agent_id)
    obj = state.objects.get(entity_id)
    if agent is None or obj is None:
        return None
    for direction in Direction:
        dx, dy = DIRECTION_DELTA[direction]
        if (agent.pos.x + dx, agent.pos.y + dy) == (obj.pos.x, obj.pos.y):
            return int(direction)
    return None


def resolvability(states: Sequence[Any], mode: AddressingMode, choices,
                  *, view_size: int = 5) -> Reading:
    """Fraction of one-step decisions that resolved, on identical states."""
    ok = total = 0
    for index, state in enumerate(states):
        choice = choices(state, index)
        if choice is None:
            continue
        total += 1
        outcome = selector_outcome(state, 0, ActionType.CONSUME, mode, choice,
                                   view_size=view_size, salt=f"pair{index}", step=0)
        ok += outcome["resolvable"]
    return ratio(ok, total, what=f"resolvability under {mode.value}")
