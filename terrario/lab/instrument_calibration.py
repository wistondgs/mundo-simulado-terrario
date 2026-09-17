"""Instrument falsification controls — calibration, not software testing.

Three measuring instruments were wrong in one night, and all three were caught
only because they collided with something already known:

  * the opportunity probe walked into a wall and oscillated between two cells,
    and would have reported that not even a perfect eater survives — the exact
    opposite of the truth;
  * the addressing rate demanded a field the trace does not carry, so it read
    zero everywhere;
  * the addressing rate, repaired, then paired each action with the world left
    *after* it, so every successful consume scored as a miss and the rate came
    out 0.000 for an agent that was demonstrably eating.

Each was found by luck — by a contradiction loud enough to notice. An instrument
that is wrong by a factor of two, or wrong only under an ablation, produces no
contradiction at all and is simply believed. Unit tests do not catch this: the
code did exactly what it said, and what it said was not the quantity we needed.

So a metric here must first answer correctly on cases whose answer is fixed by
construction, before it is allowed to answer on cases whose answer we want to
learn. A control is not "does the function run" but "on a world where the true
value is 1.0, does it say 1.0". Where a chance baseline exists, it must also
reproduce the analytic value — that is the control that would have caught the
third failure on the spot, because 0.000 is not 0.04.

This is an acceptance requirement, not a courtesy: `CALIBRATION_REQUIRED` lists
the metrics that may not be reported without passing controls, and
`tests/test_instrument_calibration.py` fails if a listed metric has none.
"""

from __future__ import annotations

import random
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import Any, Callable

from terrario.core.action_contract import AddressingMode
from terrario.core.types import Position
from terrario.lab.run_measures import _cadena, _eating, _energy_ledger, _realizacion
from terrario.lab.snapshot_bank import Snapshot, intention_representability

ADJACENT = ((-1, 0), (1, 0), (0, -1), (0, 1))
DIRECTION_NAMES = ("UP", "DOWN", "LEFT", "RIGHT", "NONE")
ACTION_NAMES = ("MOVE", "PUSH", "CONSUME", "INSPECT", "NOOP")


# ── Synthetic traces with a known answer ───────────────────────────────

def trace(pairs: Sequence[tuple[Sequence[tuple[int, int]], Mapping[str, Any]]],
          *, agent_at: tuple[int, int] = (5, 5),
          energies: Sequence[float] | None = None) -> list[dict[str, Any]]:
    """Build a trace where step k sees `objects_k` and then takes `action_k`.

    The offset by one is the whole point. A trace row records the world as it
    stood *after* that row's action, so an action must be judged against the
    previous row's world. Getting this backwards is precisely the bug that made
    the addressing rate read zero for an eating agent, so the builder encodes
    the correct pairing once and every control inherits it.
    """
    rows: list[dict[str, Any]] = []
    for index in range(len(pairs) + 1):
        objects = pairs[index][0] if index < len(pairs) else ()
        energy = energies[index] if energies and index < len(energies) else 100.0
        row: dict[str, Any] = {
            "observer_world": {
                "agents": [{"pos": {"x": agent_at[0], "y": agent_at[1]},
                            "energy": energy, "alive": True}],
                "objects": [{"pos": {"x": agent_at[0] + dx, "y": agent_at[1] + dy}}
                            for dx, dy in objects],
            }
        }
        if index > 0:
            row["agent_action"] = dict(pairs[index - 1][1])
        rows.append(row)
    return rows


def _act(action_type: str, direction: str = "NONE") -> dict[str, str]:
    return {"action_type": action_type, "direction": direction}


def _act_t1(action_type: str, status: str, *, intended: str = "entity_aaaa",
            executed: str | None = "entity_aaaa") -> dict[str, Any]:
    """A step under entity addressing: the direction says nothing, the resolver does."""
    return {"action_type": action_type, "direction": "NONE",
            "action_contract": {"addressing_mode": "T1_ENTITY", "target_status": status,
                                "intended_target": intended,
                                "resolved_target": intended if status == "VALID" else None,
                                "executed_target": executed if status == "VALID" else None,
                                "execution_status": "EXECUTED" if status == "VALID"
                                else "FAILED_TARGET_RESOLUTION"}}


# ── The controls ───────────────────────────────────────────────────────

@dataclass(frozen=True)
class Control:
    case: str
    expected: float | None
    tolerance: float
    why: str


@dataclass(frozen=True)
class Outcome:
    metric: str
    case: str
    expected: float | None
    observed: float | None
    passed: bool
    why: str

    @property
    def verdict(self) -> str:
        return "PASS" if self.passed else "FAIL"


def _rate(rows, numerator: str, denominator: str) -> float | None:
    counts = _cadena(rows)
    den = counts[denominator]
    return counts[numerator] / den if den else None


# Addressing: of the opportunities, how many the action actually pointed at.
def _addressing(rows) -> float | None:
    return _rate(rows, "direccionable", "oportunidad")


def _opportunity(rows) -> float | None:
    return _rate(rows, "oportunidad", "pasos")


def _interaction(rows) -> float | None:
    return _rate(rows, "intentos", "pasos")


def _conversion(rows) -> float | None:
    return _eating(rows)["best_segment"]


def _realization(rows) -> float | None:
    counts = _realizacion(rows)
    return counts["realizadas"] / counts["validas"] if counts["validas"] else None


class _Obj:
    def __init__(self, pos): self.pos = pos


class _Agent:
    def __init__(self, pos): self.pos, self.alive = pos, True


class _State:
    def __init__(self, agent_pos, object_positions):
        self.agents = {0: _Agent(agent_pos)}
        self.objects = {i + 1: _Obj(p) for i, p in enumerate(object_positions)}


def _bank(object_offsets) -> list[Snapshot]:
    here = Position(5, 5)
    return [Snapshot(_State(here, [Position(5 + dx, 5 + dy) for dx, dy in object_offsets]),
                     here, f"synthetic#{i}") for i in range(20)]


def _representability(rows) -> float | None:
    """`rows` is (bank, mode, view_size) here: this metric reads states, not traces."""
    bank, mode, view = rows
    return intention_representability(bank, mode, view_size=view)["representability"]["value"]


def _accounting(rows) -> float | None:
    ledger = _energy_ledger(rows)
    return ledger["reconciled"] / ledger["checked"] if ledger["checked"] else None


# A uniform agent draws one of 25 actions. Addressing needs CONSUME (1 of 5
# operations) AND a direction landing on the single neighbour (1 of 5, since
# NONE points at no cell). So P(address | opportunity) = 1/25 = 0.04 — which is
# the value the real runs reported as "chance", and the reason we can call the
# action channel a bottleneck rather than a policy failure.
UNIFORM_ADDRESSING = 1.0 / (len(ACTION_NAMES) * len(DIRECTION_NAMES))


def _uniform_trace(steps: int = 40000, seed: int = 20260917) -> list[dict[str, Any]]:
    rng = random.Random(seed)
    pairs = [(((0, 1),), _act(rng.choice(ACTION_NAMES), rng.choice(DIRECTION_NAMES)))
             for _ in range(steps)]
    return trace(pairs)


def _perfect_trace(steps: int = 200) -> list[dict[str, Any]]:
    return trace([(((0, 1),), _act("CONSUME", "RIGHT")) for _ in range(steps)])


def _never_trace(steps: int = 200) -> list[dict[str, Any]]:
    return trace([(((0, 1),), _act("MOVE", "UP")) for _ in range(steps)])


CONTROLS: dict[str, tuple[Callable[[Any], float | None], tuple[Control, ...]]] = {
    "tasa_direccionamiento": (_addressing, (
        Control("perfect_targeting_agent", 1.0, 0.0,
                "Consumes the adjacent object every step. Anything below 1.0 means the "
                "instrument cannot see a hit it was handed."),
        Control("never_target_agent", 0.0, 0.0,
                "Never issues CONSUME. Anything above 0.0 is the instrument crediting "
                "an addressing that did not happen."),
        Control("t1_perfect_targeting_agent", 1.0, 0.0,
                "Entity addressing, every slot resolving VALID. Under T1 the direction "
                "is pinned to NONE by the contract, so an instrument that reads "
                "`direction` scores every T1 run at 0.000 -- the measurement would "
                "report the absence of exactly the capability the experiment adds."),
        Control("t1_never_resolving_agent", 0.0, 0.0,
                "Entity addressing where every slot named is empty. Must read zero "
                "through the resolver, not through a geometric fallback."),
        Control("uniform_random_agent", UNIFORM_ADDRESSING, 0.006,
                "Analytic chance: CONSUME is 1 of 5 operations and the neighbour is 1 of "
                "5 directions, so 1/25. Reading 0.000 here is the failure that actually "
                "happened and went unnoticed for a full experimental round."),
    )),
    "tasa_oportunidad": (_opportunity, (
        Control("empty_world", 0.0, 0.0,
                "No objects anywhere. An opportunity counted here is an opportunity "
                "invented by the instrument."),
        Control("adjacent_every_step", 1.0, 0.0,
                "An object in contact at every step. Below 1.0 means opportunities are "
                "being missed, which would understate the world and overstate the organism."),
    )),
    "tasa_interaccion": (_interaction, (
        Control("never_target_agent", 0.0, 0.0,
                "Never issues CONSUME, so intent must read zero."),
        Control("perfect_targeting_agent", 1.0, 0.0,
                "Issues CONSUME every step, so intent must read one — independently of "
                "whether those consumes landed."),
    )),
    "tasa_realizacion": (_realization, (
        Control("realization_faithful", 1.0, 0.0,
                "Every resolved intention executed against the entity named. The ceiling "
                "must read 1.0 or every real value below it is uninterpretable."),
        Control("realization_substituted", 0.0, 0.0,
                "Every resolved intention executed against a DIFFERENT entity. This is "
                "the silent-substitution failure AC2-5 forbids, and the instrument has "
                "to be able to see it -- an instrument that cannot distinguish "
                "substitution from fidelity cannot police the invariant."),
        Control("realization_no_contract", None, 0.0,
                "A v1 trace carries no intention to compare against. The answer is "
                "NOT_EVALUABLE; reading it as 1.0 would report perfect execution for "
                "every run made before the contract existed."),
    )),
    "representabilidad_intencion": (_representability, (
        Control("representability_t0_reachable", 1.0, 0.0,
                "An entity in contact under directional addressing. CONSUME(direction) "
                "already names it, so the ceiling must read 1.0."),
        Control("representability_t1_reachable", 1.0, 0.0,
                "The same entity under entity addressing."),
        Control("representability_t1_blind", 0.0, 0.0,
                "The entity is in contact but the view window cannot perceive it, so no "
                "slot names it and no expressible action realises the intention. This is "
                "the control that matters: without it the instrument could return 1.0 "
                "unconditionally and nobody would know."),
        Control("representability_no_intentions", None, 0.0,
                "Nothing in contact anywhere. There are no realisable intentions to "
                "score, and the answer is NOT_EVALUABLE -- not 1.0, which would claim "
                "perfect expressivity on no evidence."),
    )),
    "contabilidad_energetica": (_accounting, (
        Control("ledger_balanced", 1.0, 0.0,
                "Energy falls by exactly the declared cost on every non-consuming step."),
        Control("ledger_undeclared_flow", 0.0, 0.0,
                "A second drain the scenario never declared. The instrument must fail it; "
                "otherwise a reconstructed baseline absorbs the unknown flow and every "
                "downstream reading shifts with nothing raising an objection."),
    )),
    "conversion_aprendizaje": (_conversion, (
        Control("non_learning_agent", None, 0.0,
                "Energy moves only by the fixed step cost: no consume ever lands. There "
                "is no stable-rule segment to score, and the honest answer is "
                "'not evaluable' — NOT zero. Coercing it to 0.0 would report a learner "
                "that failed where there was no evidence either way."),
        Control("oracle_learner", 1.0, 0.0,
                "Every consume gains energy against the idle baseline. A learner that "
                "always picks right must score 1.0, or the ceiling of the scale is wrong "
                "and every real reading below it is uninterpretable."),
    )),
}

# Metrics that may not be reported until their controls pass.
CALIBRATION_REQUIRED = frozenset(CONTROLS)


def _case_trace(case: str) -> list[dict[str, Any]]:
    if case == "perfect_targeting_agent":
        return _perfect_trace()
    if case == "never_target_agent":
        return _never_trace()
    if case == "uniform_random_agent":
        return _uniform_trace()
    if case == "t1_perfect_targeting_agent":
        return trace([(((0, 1),), _act_t1("CONSUME", "VALID")) for _ in range(200)])
    if case == "t1_never_resolving_agent":
        return trace([(((0, 1),), _act_t1("CONSUME", "NONEXISTENT")) for _ in range(200)])
    if case == "representability_t0_reachable":
        return (_bank([(0, 1)]), AddressingMode.T0_DIRECTIONAL, 5)
    if case == "representability_t1_reachable":
        return (_bank([(0, 1)]), AddressingMode.T1_ENTITY, 5)
    if case == "representability_t1_blind":
        return (_bank([(0, 1)]), AddressingMode.T1_ENTITY, 1)
    if case == "representability_no_intentions":
        return (_bank([(0, 4)]), AddressingMode.T1_ENTITY, 5)
    if case == "realization_faithful":
        return trace([(((0, 1),), _act_t1("CONSUME", "VALID")) for _ in range(100)])
    if case == "realization_substituted":
        return trace([(((0, 1),), _act_t1("CONSUME", "VALID", executed="entity_bbbb"))
                      for _ in range(100)])
    if case == "realization_no_contract":
        return _perfect_trace()
    if case in ("ledger_balanced", "ledger_undeclared_flow"):
        drain = 1.0 if case == "ledger_balanced" else 1.7
        steps = 100
        rows = trace([((), _act("MOVE", "UP")) for _ in range(steps)],
                     energies=[100.0 - i * drain for i in range(steps + 1)])
        for row in rows:
            row["observer_world"]["step_energy_cost"] = 1.0
            row["agent_events"] = ("move_success",)
        return rows
    if case == "empty_world":
        return trace([((), _act("CONSUME", "RIGHT")) for _ in range(200)])
    if case == "adjacent_every_step":
        return _perfect_trace()
    if case == "non_learning_agent":
        # Consume every step against nothing: energy falls by the step cost only,
        # so no consume is ever distinguishable from idling.
        steps = 200
        return trace([((), _act("CONSUME", "RIGHT")) for _ in range(steps)],
                     energies=[100.0 - i for i in range(steps + 1)])
    if case == "oracle_learner":
        # Idle costs 1; every consume nets +9 against that baseline.
        levels, energy = [100.0], 100.0
        pairs = []
        for i in range(200):
            eats = i % 2 == 0
            energy += 9.0 if eats else -1.0
            levels.append(energy)
            pairs.append((((0, 1),) if eats else (), _act("CONSUME" if eats else "MOVE", "RIGHT")))
        return trace(pairs, energies=levels)
    raise KeyError(case)


def calibrate(metric: str) -> list[Outcome]:
    """Run one metric against every case whose answer is known by construction."""
    compute, controls = CONTROLS[metric]
    outcomes = []
    for control in controls:
        observed = compute(_case_trace(control.case))
        if control.expected is None:
            passed = observed is None
        elif observed is None:
            passed = False
        else:
            passed = abs(observed - control.expected) <= control.tolerance
        outcomes.append(Outcome(metric, control.case, control.expected, observed,
                                passed, control.why))
    return outcomes


def calibrate_all() -> list[Outcome]:
    return [o for metric in sorted(CONTROLS) for o in calibrate(metric)]


def report() -> str:
    lines = ["INSTRUMENT FALSIFICATION CONTROLS", ""]
    for o in calibrate_all():
        expected = "not evaluable" if o.expected is None else f"{o.expected:.4f}"
        observed = "not evaluable" if o.observed is None else f"{o.observed:.4f}"
        lines.append(f"  [{o.verdict}] {o.metric:<24} {o.case:<26} "
                     f"expected {expected:>13}  observed {observed:>13}")
    failed = [o for o in calibrate_all() if not o.passed]
    lines += ["", f"{len(failed)} failing control(s)." if failed else "All controls pass."]
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
