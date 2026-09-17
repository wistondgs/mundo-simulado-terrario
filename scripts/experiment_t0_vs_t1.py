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
        mix = validate_selection(config) if agent_id == "A4" else dict(config)
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
            for step in trace:
                contract = (step.get("agent_action") or {}).get("action_contract")
                if contract:
                    key = contract["target_status"]
                    statuses[key] = statuses.get(key, 0) + 1
            row = {
                "arm": arm, "agent": agent_id, "seed": seed,
                "addressing_mode": config["addressing_mode"],
                "rates": {r: reading_of(measures, r).as_record() for r in RATES},
                "meals": next((m["value"] for m in measures["measures"]
                               if m["key"] == "comidas_efectivas"), None),
                "steps_lived": next((m["value"] for m in measures["measures"]
                                     if m["key"] == "pasos_vividos"), None),
                "target_status_counts": statuses,
                "seconds": round(time.time() - t0, 1),
            }
            rows.append(row)
            addressing = row["rates"]["tasa_direccionamiento"]
            print(f"  {arm:<7} seed {seed}  addressing="
                  f"{addressing['value'] if addressing['value'] is not None else addressing['status']}"
                  f"  steps={row['steps_lived']}  {row['seconds']}s", flush=True)

    summary = {
        arm: {rate: aggregate([Reading(Status(r["rates"][rate]["status"]),
                                       r["rates"][rate]["value"])
                               for r in rows if r["arm"] == arm])
              for rate in RATES}
        for arm in ARMS
    }

    out = {
        "schema_version": SCHEMA, "classification": CLASSIFICATION,
        "world": args.world, "steps": args.steps, "seeds": seeds,
        "predictions": {
            "P1": "Addressing(A0,T1) < Addressing(A0,T0) -- T1 buys expressiveness, not accuracy",
            "P2": "Addressing(A4,T1) >> Addressing(A4,T0) and >> Addressing(A0,T1)",
            "P3": "Conversion(A4,T1) > Conversion(A4,T0) -- the decisive one",
        },
        "arms": {a: {"agent": ARMS[a][0], "config": ARMS[a][1]} for a in ARMS},
        "summary": summary, "runs": rows,
        "elapsed_seconds": round(time.time() - started, 1),
    }
    path = PROJECT_ROOT / args.out
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(f"\nwrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
