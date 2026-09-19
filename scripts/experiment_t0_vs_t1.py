#!/usr/bin/env python
"""T0 vs T1: does the action channel explain the organism's behavioural floor?

The screening result that motivates this: removing the world model or the
planner takes A4 from ~6.7 meals to ~0, so those modules are materially shaping
the trajectory. Yet addressing -- the fraction of genuine opportunities the
emitted action actually referred to -- sat at 2-4% for EVERY agent including the
uniformly random one, whose analytic chance value is 1/25 = 0.04. An organism
that represents and plans, and then cannot say which thing it means, produces
almost no informative experience: 7 steps in 1000.

So this is not a test of whether T1 makes A4 intelligent. It is a test of whether
the actuator is what has been hiding the answer.

DESIGN
Everything is held identical across arms except the selector type: same worlds,
seeds, initial parameters, metabolism, object distribution, horizon and
cognitive components. Five arms:

    A0-T0   chance under directional addressing
    A0-T1   chance under entity addressing
    A4-T0   the organism as it has been measured all along
    A4-T0F  the organism with factored heads, still addressing directions
    A4-T1   the organism addressing entities

A4-T0F is the arm that keeps the experiment honest. T1 changes two things at
once -- the action is factored into (operation, selector) AND the selector
becomes an entity -- so without it, any gain under T1 could be credited to "two
heads are better than one" rather than to addressing. T0F holds the factoring
and varies only the selector type.

PREDICTIONS, registered before the run
P1  Addressing(A0,T1) < Addressing(A0,T0). Uniform choice over 16 slots, of
    which few are ever occupied, is worse than uniform choice over 5 directions.
    T1 buys expressiveness, not accuracy. If A0 improves under T1, the channel
    is handing out hits and the comparison is worthless.
P2  Addressing(A4,T1) >> Addressing(A4,T0), and >> Addressing(A0,T1). This is
    validation of the new actuator, not yet evidence of cognition.
P3  The decisive one: Conversion(A4,T1) > Conversion(A4,T0). If T1 raises
    addressing and conversion stays flat, the actuator is eliminated as the
    explanation and the learner becomes reachable for the first time. That is
    progress even if A4 still dies.

P3 failing is an informative outcome, not a failed experiment.

Engineering sandbox. Not evidence. No preregistration is signed here.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from dataclasses import replace
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch

from terrario.lab.agent_composition import validate_selection
from terrario.lab.measurement_status import Reading, Status
from terrario.lab.models import thaw
from terrario.lab.run_measures import measure_run
from terrario.lab.sandbox_runtime import (
    ExecutionClassification, SandboxService, derive_sandbox, make_spec,
)
from terrario.lab.world_authoring import compile_registry_world
from terrario.lab.world_registry import WorldScenarioRegistry, configuration_for

SCHEMA = "terrario.lab.addressing-contract/v1"
CLASSIFICATION = "ENGINEERING_SANDBOX_NOT_EVIDENCE"

#: The chain, in the order a failure travels it. Read the first drop.
RATES = ("tasa_oportunidad", "tasa_interaccion", "tasa_direccionamiento",
         "tasa_informativa", "conversion_aprendizaje")

ARMS = {
    "A0-T0":  ("A0", {"addressing_mode": "T0_DIRECTIONAL"}),
    "A0-T1":  ("A0", {"addressing_mode": "T1_ENTITY"}),
    "A4-T0":  ("A4", {"addressing_mode": "T0_DIRECTIONAL"}),
    "A4-T0F": ("A4", {"addressing_mode": "T0_DIRECTIONAL", "use_factored_action": True}),
    "A4-T1":  ("A4", {"addressing_mode": "T1_ENTITY"}),
    # E arms. The paired T contrast is run, but its own purity gate refuses it:
    # A4's policy collapses onto ONE action within a few hundred steps, a
    # different one in each arm, and which action it lands on decides how often
    # the organism meets anything -- which sits upstream of addressing. So the
    # T contrast alone is not attributable to the selector type, and adding
    # seeds would not change that.
    #
    # E is the factor that speaks to the collapse. Under T0 entropy
    # regularisation measured an effect of -0.67 meals, inside seed spread:
    # nothing. The design directive predicts that is not because exploration is
    # useless but because it had nothing to express -- Effect(E | T0) = 0 while
    # Effect(E | T1) > 0. Running E here rather than after makes that prediction
    # testable in the same campaign, and makes the T contrast interpretable if
    # it holds.
    "A4-T0-E": ("A4", {"addressing_mode": "T0_DIRECTIONAL",
                       "use_entropy_regularization": True}),
    "A4-T1-E": ("A4", {"addressing_mode": "T1_ENTITY",
                       "use_entropy_regularization": True}),
}


class Bench:
    """The runtime one layer below the streaming surface, as in the screening."""

    def __init__(self, root: Path):
        self.registry = WorldScenarioRegistry(root)
        self.service = SandboxService(root / ".sandbox-addressing")
        self._compiled: dict[str, object] = {}

    def compiled(self, world: str):
        if world not in self._compiled:
            entry = self.registry.get(world)
            self._compiled[world] = (compile_registry_world(world, entry.source), entry)
        return self._compiled[world]

    def run(self, world, steps, seed, agent_id, config):
        compiled, entry = self.compiled(world)
        base = replace(derive_sandbox(configuration_for(entry)), agent_reference=agent_id)
        # Antes esto era `if agent_id == "A4"`, porque el validador sólo sabía de
        # A4 y los brazos A0 tenían que rodearlo. Ahora valida contra el agente
        # del brazo, así que el brazo A0 pasa por la misma puerta que los demás.
        mix = validate_selection(config, agent_id)
        spec = make_spec(base, compiled, 42, seed, steps + 1,
                         ExecutionClassification.ENGINEERING_SANDBOX, mix)
        # Same reason as the screening: the agent seed does not determine the
        # agent, because module weights come from the GLOBAL torch RNG. Without
        # this, an arm's result depends on its position in the loop.
        torch.manual_seed(seed)
        run = self.service.create(spec, base, compiled)
        self.service.run_bounded(run.run_id, steps)
        rows = [thaw(step) for step in run.timeline]
        return measure_run(rows), rows


#: Steps of the opening window used for the purity check, chosen to be long
#: enough to characterise movement and short enough that differential eating has
#: not yet reshaped the two arms' surroundings.
EARLY_WINDOW = 100


def _position(step) -> tuple | None:
    agents = (step.get("observer_world") or {}).get("agents") or {}
    entries = list(agents.values()) if isinstance(agents, dict) else list(agents)
    if not entries or "pos" not in entries[0]:
        return None
    pos = entries[0]["pos"]
    return tuple(pos.values()) if isinstance(pos, dict) else tuple(pos)


def reading_of(measures, key: str) -> Reading:
    """Pull one rate out WITHOUT flattening not-evaluable into zero."""
    for m in measures["measures"]:
        if m["key"] != key:
            continue
        if not m.get("evaluable", True) or m["value"] is None:
            return Reading.not_evaluable(m.get("reason") or "arm reported no support")
        return Reading.ok(float(m["value"]))
    return Reading.missing(f"{key} absent from the measure set")


def aggregate(readings: list[Reading]) -> dict:
    """Mean over the seeds that HAD support, and a count of the ones that did not.

    Averaging a not-evaluable as zero is the error this whole layer exists to
    prevent, so the absent seeds are reported next to the mean rather than
    folded into it.
    """
    usable = [r for r in readings if r.evaluable]
    absent = len(readings) - len(usable)
    if not usable:
        return {"status": Status.NOT_EVALUABLE.value, "mean": None,
                "seeds_with_support": 0, "seeds_without_support": absent}
    values = [float(r) for r in usable]
    return {"status": Status.OK.value,
            "mean": round(sum(values) / len(values), 4),
            "min": round(min(values), 4), "max": round(max(values), 4),
            "seeds_with_support": len(usable), "seeds_without_support": absent}


#: How far two arms' opportunity rates may differ before the addressing contrast
#: between them stops being about addressing.
PURITY_TOLERANCE = 0.25


def intervention_purity(summary: dict) -> dict:
    """T must vary addressing and NOTHING upstream of it.

    This gate exists because two versions of this contract failed it silently.
    The first pinned every operation's direction to NONE under T1, including
    MOVE, and paralysed the organism: one opportunity in three hundred steps
    against dozens for the same agent under T0, and a random policy scoring 1.0
    addressing off a denominator of 1. The second left PUSH addressing entities,
    and PUSH is how this organism travels -- its pushes stopped resolving and it
    visited two cells with something adjacent at every step.

    Neither showed up as an error. Both produced a plausible-looking addressing
    number. What gave them away was the opportunity rate, which sits UPSTREAM of
    addressing and therefore has no business moving when only the selector type
    changed. So it is checked, per agent, across that agent's T arms, and a
    contrast that fails is reported CONFOUNDED rather than as a result.

    An instrument gate asks whether the ruler is honest. This asks whether the
    intervention was the one we named.
    """
    verdicts = {}
    # Purity is judged WITHIN an exploration condition: E is a second
    # intervention, and comparing a T0 arm without it against a T1 arm with it
    # would fail for a reason that has nothing to do with addressing.
    groups = {"A0": ("A0-T0", "A0-T1"),
              "A4 (E off)": ("A4-T0", "A4-T0F", "A4-T1"),
              "A4 (E on)": ("A4-T0-E", "A4-T1-E")}
    for agent, arms in groups.items():
        rates = {a: summary[a]["early_opportunity"].get("mean") for a in arms}
        present = {a: v for a, v in rates.items() if v is not None}
        if len(present) < 2:
            verdicts[agent] = {"verdict": "NOT_EVALUABLE", "opportunity_rates": rates,
                               "reason": "fewer than two arms reported an opportunity rate"}
            continue
        low, high = min(present.values()), max(present.values())
        spread = (high - low) / high if high else 0.0
        verdicts[agent] = {
            "verdict": "PURE" if spread <= PURITY_TOLERANCE else "CONFOUNDED_UPSTREAM",
            "opportunity_rates": {a: round(v, 4) for a, v in present.items()},
            "relative_spread": round(spread, 4), "tolerance": PURITY_TOLERANCE,
            "reason": ("the arms meet the world equally often, so a difference in "
                       "addressing is a difference in addressing")
            if spread <= PURITY_TOLERANCE else
            ("the arms do not meet the world equally often, so T changed something "
             "upstream of addressing and the addressing contrast is not attributable "
             "to the selector type"),
        }
    return verdicts


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", default="D4T")
    ap.add_argument("--steps", type=int, default=1200)
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--out", default="artifacts/addressing_contract.json")
    args = ap.parse_args()

    bench = Bench(PROJECT_ROOT)
    seeds = [1000041 + i for i in range(args.seeds)]
    started = time.time()
    rows: list[dict] = []

    for arm, (agent_id, config) in ARMS.items():
        for seed in seeds:
            t0 = time.time()
            measures, trace = bench.run(args.world, args.steps, seed, agent_id, config)
            statuses: dict[str, int] = {}
            operations: dict[str, int] = {}
            cells = set()
            for step in trace:
                contract = (step.get("agent_action") or {}).get("action_contract")
                if contract:
                    key = contract["target_status"]
                    statuses[key] = statuses.get(key, 0) + 1
                op = (step.get("agent_action") or {}).get("action_type")
                if op:
                    operations[op] = operations.get(op, 0) + 1
                agents = (step.get("observer_world") or {}).get("agents") or {}
                entries = list(agents.values()) if isinstance(agents, dict) else list(agents)
                if entries and "pos" in entries[0]:
                    pos = entries[0]["pos"]
                    cells.add(tuple(pos.values()) if isinstance(pos, dict) else tuple(pos))
            # Policy collapse, measured rather than inferred. Every arm so far
            # settles onto ONE action within a few hundred steps, and WHICH one
            # differs by arm -- PUSH under T0, INSPECT under T0 factored, NOOP
            # under T1. Only PUSH moves this organism, so the collapse target
            # decides how often it meets anything at all, which sits upstream of
            # addressing. Recorded per arm so the confound is a number in the
            # record instead of a guess about the trajectory.
            modal = max(operations.items(), key=lambda kv: kv[1]) if operations else (None, 0)
            # Opportunity over the WHOLE run is not a purity check, because
            # eating removes the object eaten: an arm that addresses well clears
            # its surroundings and reports FEWER opportunities, while one that
            # never resolves stays permanently surrounded and reports 1.0. That
            # is the outcome feeding back into the exposure, so the number
            # conflates "the intervention was clean" with "the intervention
            # worked" -- and it read exactly 1.0 for every T1 arm at every
            # length, which is what gave it away.
            #
            # Two measures that are not outcome-coupled in that way: the
            # opportunity rate over the opening window, before the arms' eating
            # has had time to diverge, and the fraction of steps on which the
            # organism actually changed cell. No consume ever moves the agent,
            # so locomotion is not downstream of addressing.
            early = measure_run(trace[:EARLY_WINDOW + 1])
            positions = [_position(step) for step in trace]
            moves = sum(1 for a, b in zip(positions, positions[1:])
                        if a is not None and b is not None and a != b)
            row = {
                "arm": arm, "agent": agent_id, "seed": seed,
                "addressing_mode": config["addressing_mode"],
                "rates": {r: reading_of(measures, r).as_record() for r in RATES},
                "meals": next((m["value"] for m in measures["measures"]
                               if m["key"] == "comidas_efectivas"), None),
                "steps_lived": next((m["value"] for m in measures["measures"]
                                     if m["key"] == "pasos_vividos"), None),
                "target_status_counts": statuses,
                "operation_counts": operations,
                "modal_action": modal[0],
                "modal_action_share": round(modal[1] / max(len(trace), 1), 4),
                "cells_visited": len(cells),
                "early_opportunity": reading_of(early, "tasa_oportunidad").as_record(),
                "locomotion_rate": round(moves / max(len(positions) - 1, 1), 4),
                "seconds": round(time.time() - t0, 1),
            }
            rows.append(row)
            addressing = row["rates"]["tasa_direccionamiento"]
            print(f"  {arm:<7} seed {seed}  addressing="
                  f"{addressing['value'] if addressing['value'] is not None else addressing['status']}"
                  f"  steps={row['steps_lived']}  modal={row['modal_action']}"
                  f"@{row['modal_action_share']}  cells={row['cells_visited']}"
                  f"  {row['seconds']}s", flush=True)

    summary = {
        arm: {rate: aggregate([Reading(Status(r["rates"][rate]["status"]),
                                       r["rates"][rate]["value"])
                               for r in rows if r["arm"] == arm])
              for rate in RATES}
        for arm in ARMS
    }
    for arm in ARMS:
        summary[arm]["early_opportunity"] = aggregate(
            [Reading(Status(r["early_opportunity"]["status"]), r["early_opportunity"]["value"])
             for r in rows if r["arm"] == arm])
        shares = [r["locomotion_rate"] for r in rows if r["arm"] == arm]
        collapse = [r["modal_action_share"] for r in rows if r["arm"] == arm]
        summary[arm]["locomotion_rate"] = round(sum(shares) / len(shares), 4) if shares else None
        summary[arm]["modal_action_share"] = (round(sum(collapse) / len(collapse), 4)
                                              if collapse else None)

    out = {
        "schema_version": SCHEMA, "classification": CLASSIFICATION,
        "world": args.world, "steps": args.steps, "seeds": seeds,
        "predictions": {
            "P1": "Addressing(A0,T1) < Addressing(A0,T0) -- T1 buys expressiveness, not accuracy",
            "P2": "Addressing(A4,T1) >> Addressing(A4,T0) and >> Addressing(A0,T1)",
            "P3": "Conversion(A4,T1) > Conversion(A4,T0) -- the decisive one",
            "P4": "Effect(E | T0) ~ 0 but Effect(E | T1) > 0 -- epistemic exploration "
                  "needed actuator expressiveness before it could show any effect. "
                  "A T x E interaction would be a functional relation BETWEEN "
                  "capabilities, not two independently useful modules.",
            "P5": "E raises modal_action_share away from collapse. If it does not, "
                  "the collapse is not an exploration failure and E is the wrong "
                  "instrument for it.",
        },
        "arms": {a: {"agent": ARMS[a][0], "config": ARMS[a][1]} for a in ARMS},
        "summary": summary, "intervention_purity": intervention_purity(summary),
        "runs": rows,
        "elapsed_seconds": round(time.time() - started, 1),
    }
    path = PROJECT_ROOT / args.out
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print("\nINTERVENTION PURITY")
    for agent, verdict in out["intervention_purity"].items():
        print(f"  {agent}: {verdict['verdict']}  {verdict.get('opportunity_rates')}")
    print("\nCOLLAPSE AND LOCOMOTION")
    for arm in ARMS:
        print(f"  {arm:<8} modal_share={summary[arm]['modal_action_share']}"
              f"  locomotion={summary[arm]['locomotion_rate']}"
              f"  early_opportunity={summary[arm]['early_opportunity'].get('mean')}")
    print("\nFIVE RATES")
    for arm in ARMS:
        line = "  ".join(
            f"{r.split('_')[-1][:6]}={summary[arm][r]['mean'] if summary[arm][r]['mean'] is not None else 'n/e'}"
            for r in RATES)
        print(f"  {arm:<7} {line}")
    print(f"\nwrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
