#!/usr/bin/env python
"""Closed-loop T0 vs T1: the TOTAL effect of the selector, paired by seed.

What this is not
----------------
It is not a test of expressivity. That question is closed: on 3000 exogenous
states, representability is 1.0 under both contracts over 1894 physically
realisable intentions, so v1 could already express every intention the physics
admits. Nor is it a test of local isolation, which the one-step twin settled at
0 failures in 3000 pairs.

What it is
----------
A test of whether the REPRESENTATION of the action space changes what an
organism can learn to realise. T0 selects over spatial directions, some of which
denote no entity. T1 selects over observed entities. Neither is more expressive;
they differ in inductive bias and in the geometry of the choice. T1 reduces a
compound question -- "is anything there?" plus "which thing do I want?" -- to the
second alone, WITHOUT granting the third, "can I reach it?". That third is left
in deliberately: filtering T1 down to reachable entities would inject the world's
affordance knowledge into the agent and hand it part of the decision. The
OUT_OF_RANGE outcomes are evidence, not noise.

Design
------
Two arms. Everything else frozen: world model, planner, memory, learner,
homeostasis, entropy mechanism, step cost, MOVE, PUSH, INSPECT, NOOP, initial
weights, world seed, exogenous RNG. E is not an intervention here. C is frozen.

Statistical unit
----------------
The trial, not the step. Treating 1200 steps x N seeds as n would be
pseudoreplication: steps inside one run share an organism, a world instance and a
trajectory. Each metric is computed per run, and inference is on the paired
differences

    delta_i = Y(T1, seed_i) - Y(T0, seed_i)

by exact paired permutation over sign flips, with a paired bootstrap interval.
A seed where either arm reports NOT_EVALUABLE is dropped from the pairing and
counted, never coerced to zero.

Registered before running
-------------------------
PRIMARY
  P(valid reference | CONSUME)      the referential question alone
  P(executable target | CONSUME)    reference plus reach
  N_informative and P(informative | CONSUME)
  learning conversion               only where it has support

WASTE DECOMPOSITION
  W_reference  P(NONEXISTENT   | CONSUME)   aimed at nothing
  W_reach      P(OUT_OF_RANGE  | CONSUME)   aimed at something unreachable
  W_other      P(STALE/OCCLUDED| CONSUME)

SECONDARY (outcomes, not controls)
  effective meals, hit rate given a valid interaction, final energy, survival,
  operation distribution, policy entropy, modal concentration, path length,
  unique cells, experienced opportunity

Engineering sandbox. Not evidence.
"""

from __future__ import annotations

import argparse
import itertools
import json
import random
import sys
import time
from dataclasses import replace
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch

from terrario.lab.agent_composition import validate_selection
from terrario.lab.measurement_status import Reading, Status, ratio
from terrario.lab.models import thaw
from terrario.lab.run_measures import measure_run
from terrario.lab.sandbox_runtime import (
    ExecutionClassification, SandboxService, derive_sandbox, make_spec,
)
from terrario.lab.world_authoring import compile_registry_world
from terrario.lab.world_registry import WorldScenarioRegistry, configuration_for

SCHEMA = "terrario.lab.closed-loop-addressing/v1"
CLASSIFICATION = "ENGINEERING_SANDBOX_NOT_EVIDENCE"

ARMS = {"T0": {"addressing_mode": "T0_DIRECTIONAL"},
        "T1": {"addressing_mode": "T1_ENTITY"}}

PRIMARY = ("p_valid_reference_given_consume", "p_executable_given_consume",
           "p_executable_given_consume_and_contact", "p_beneficial_given_valid",
           "n_informative", "p_informative_given_consume", "learning_conversion")
WASTE = ("w_reference", "w_reach", "w_other")
SECONDARY = ("effective_meals", "hit_rate_given_valid", "final_energy", "steps_lived",
             "survived", "policy_entropy", "modal_action_share", "path_length",
             "unique_cells", "experienced_opportunity")

STATUS_OK = "VALID"
STATUS_NO_REFERENT = "NONEXISTENT"
STATUS_UNREACHABLE = "OUT_OF_RANGE"


class Bench:
    def __init__(self, root: Path):
        self.registry = WorldScenarioRegistry(root)
        self.service = SandboxService(root / ".sandbox-closed-loop")
        self._compiled: dict[str, object] = {}

    def compiled(self, world: str):
        if world not in self._compiled:
            entry = self.registry.get(world)
            self._compiled[world] = (compile_registry_world(world, entry.source), entry)
        return self._compiled[world]

    def run(self, world, steps, seed, config):
        compiled, entry = self.compiled(world)
        base = replace(derive_sandbox(configuration_for(entry)), agent_reference="A4")
        spec = make_spec(base, compiled, 42, seed, steps + 1,
                         ExecutionClassification.ENGINEERING_SANDBOX,
                         validate_selection(config, "A4"))
        # The agent seed does not determine the agent: module weights come from
        # the GLOBAL torch RNG. Seeded here so both arms of a pair start from the
        # same initial weights, which is the whole point of pairing.
        torch.manual_seed(seed)
        run = self.service.create(spec, base, compiled)
        self.service.run_bounded(run.run_id, steps)
        return [thaw(step) for step in run.timeline]


def _reading(measures, key: str) -> Reading:
    for m in measures["measures"]:
        if m["key"] != key:
            continue
        if not m.get("evaluable", True) or m["value"] is None:
            return Reading.not_evaluable(m.get("reason") or "no support in this arm")
        return Reading.ok(float(m["value"]))
    return Reading.missing(f"{key} absent")


def metrics_of(trace) -> dict[str, Reading]:
    measures = measure_run(trace)
    statuses: dict[str, int] = {}
    operations: dict[str, int] = {}
    positions, entropies = [], []
    informative = 0
    for step in trace:
        action = step.get("agent_action") or {}
        contract = action.get("action_contract")
        if contract:
            statuses[contract["target_status"]] = statuses.get(contract["target_status"], 0) + 1
        op = action.get("action_type")
        if op:
            operations[op] = operations.get(op, 0) + 1
        world = step.get("observer_world") or {}
        agents = world.get("agents") or {}
        entries = list(agents.values()) if isinstance(agents, dict) else list(agents)
        if entries and "pos" in entries[0]:
            pos = entries[0]["pos"]
            positions.append(tuple(pos.values()) if isinstance(pos, dict) else tuple(pos))
        state = step.get("scientific_state") or {}
        if isinstance(state.get("policy_entropy"), (int, float)):
            entropies.append(float(state["policy_entropy"]))

    # ── The full decomposition of a consume attempt ──────────────────
    #
    #   N_consume = N_nonexistent + N_out_of_range + N_valid + N_other
    #   N_valid   = N_beneficial  + N_harmful      + N_neutral
    #
    # Three questions that used to live inside one failure rate, and a fourth
    # that only becomes askable once they are apart:
    #
    #   REFERENCE       did it point at something that exists?
    #   AFFORDANCE      could it act on that thing?
    #   DISCRIMINATION  was choosing that thing correct?
    #   LEARNING        did the discrimination improve with experience?
    #
    # N_other should be zero or exactly explained; it is reported either way
    # rather than folded into one of the others.
    declared = (trace[0].get("observer_world") or {}).get("step_energy_cost") if trace else None
    baseline = -float(declared) if isinstance(declared, (int, float)) \
        and not isinstance(declared, bool) and declared > 0 else None
    energies = []
    for step in trace:
        world = step.get("observer_world") or {}
        agents = world.get("agents") or {}
        entries = list(agents.values()) if isinstance(agents, dict) else list(agents)
        energies.append(float(entries[0]["energy"]) if entries
                        and isinstance(entries[0].get("energy"), (int, float)) else None)
    beneficial = harmful = neutral = 0
    unclassified = 0
    for index in range(1, len(trace)):
        contract = (trace[index].get("agent_action") or {}).get("action_contract")
        if not contract or contract["target_status"] != STATUS_OK:
            continue
        before, after = energies[index - 1], energies[index]
        if before is None or after is None or baseline is None:
            unclassified += 1
            continue
        effect = (after - before) - baseline
        if effect > 0.5:
            beneficial += 1
        elif effect < -0.5:
            harmful += 1
        else:
            neutral += 1

    consumes = operations.get("CONSUME", 0)
    # THE DENOMINATOR, and the one place this instrument nearly went wrong.
    #
    # Under T0 provenance is emitted only for target-bearing operations; under
    # T1 it is emitted for every step, with NOT_ADDRESSED on the ones that take
    # no referent. Summing all statuses therefore gave T0 a denominator of
    # "consume attempts" and T1 one of "all steps" -- the two rates would have
    # answered different questions while sharing a column heading, and the
    # smoke run duly reported 81% "other waste" for T1, which was simply MOVE
    # and NOOP. Attempts that carried a referent, in both arms, is the shared
    # quantity.
    addressed = sum(count for status, count in statuses.items()
                    if status != "NOT_ADDRESSED")
    valid = statuses.get(STATUS_OK, 0)
    absent = statuses.get(STATUS_NO_REFERENT, 0)
    unreachable = statuses.get(STATUS_UNREACHABLE, 0)
    other = addressed - valid - absent - unreachable
    informative = _reading(measures, "tasa_informativa")
    n_informative = next((m["value"] for m in measures["measures"]
                          if m["key"] == "comidas_efectivas"), None)

    moves = sum(1 for a, b in zip(positions, positions[1:]) if a != b)
    modal = max(operations.values()) / max(len(trace), 1) if operations else None

    out = {
        "p_valid_reference_given_consume": ratio(addressed - absent, addressed,
                                                 what="valid reference"),
        "p_executable_given_consume": ratio(valid, addressed, what="executable target"),
        # Conditioned on an entity actually being in contact. This is the rate
        # the exogenous bank reported (T0 0.272, T1 0.327); the unconditioned one
        # above is not comparable to it, because a consume issued with nothing
        # adjacent cannot succeed under either contract and both arms issue many.
        "p_executable_given_consume_and_contact": _reading(measures, "tasa_direccionamiento"),
        "n_informative": (Reading.ok(float(n_informative)) if n_informative is not None
                          else Reading.not_evaluable("no informative count")),
        "p_informative_given_consume": ratio(n_informative, consumes,
                                             what="informative given consume")
        if n_informative is not None and consumes else Reading.not_evaluable(
            "no consume attempts, so the rate has no support"),
        "learning_conversion": _reading(measures, "conversion_aprendizaje"),
        "w_reference": ratio(absent, addressed, what="referential waste"),
        "w_reach": ratio(unreachable, addressed, what="reach waste"),
        "w_other": ratio(other, addressed, what="other waste"),
        "effective_meals": Reading.ok(float(n_informative)) if n_informative is not None
        else Reading.not_evaluable("absent"),
        "hit_rate_given_valid": _reading(measures, "conversion_aprendizaje"),
        "final_energy": _reading(measures, "energia_final"),
        "steps_lived": Reading.ok(float(len(trace))),
        "survived": _reading(measures, "sigue_vivo"),
        "policy_entropy": Reading.ok(sum(entropies) / len(entropies)) if entropies
        else Reading.not_evaluable("no policy telemetry"),
        "modal_action_share": Reading.ok(modal) if modal is not None
        else Reading.not_evaluable("no operations"),
        "path_length": Reading.ok(float(moves)),
        "unique_cells": Reading.ok(float(len(set(positions)))),
        "experienced_opportunity": _reading(measures, "tasa_oportunidad"),
    }
    out["_status_counts"] = statuses
    out["_decomposition"] = {
        "N_consume": consumes, "N_addressed": addressed,
        "N_nonexistent": absent, "N_out_of_range": unreachable,
        "N_valid": valid, "N_other": other,
        "identity_holds": addressed == absent + unreachable + valid + other,
        "N_beneficial": beneficial, "N_harmful": harmful, "N_neutral": neutral,
        "N_valid_unclassified": unclassified,
        "valid_identity_holds": valid == beneficial + harmful + neutral + unclassified,
        "baseline_source": "DECLARED_STEP_COST" if baseline is not None
        else "UNAVAILABLE_SO_VALID_OUTCOMES_ARE_UNCLASSIFIED",
    }
    out["p_beneficial_given_valid"] = ratio(beneficial, valid - unclassified,
                                            what="discrimination given a valid target")
    out["_denominator_addressed_attempts"] = addressed
    out["_denominator_definition"] = ("steps whose operation carried a referent; "
                                      "NOT_ADDRESSED excluded so both arms share it")
    out["_operation_counts"] = operations
    out["_consume_attempts"] = consumes
    out["_addressed_attempts"] = addressed
    return out


def _median(values: list[float]) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    middle = len(ordered) // 2
    return (ordered[middle] if len(ordered) % 2
            else (ordered[middle - 1] + ordered[middle]) / 2)


def paired_test(deltas: list[float], *, bootstrap: int = 20000,
                seed: int = 20260917) -> dict:
    """Exact sign-flip permutation on the paired differences, plus a bootstrap CI.

    The weight belongs on the MAGNITUDE and the CONSISTENCY of the effect, not on
    clearing a threshold. With sixteen pairs, a p-value is a weak summary of a
    small sample, while the sign counts say directly how many worlds moved the
    same way -- which is the question a mechanism has to answer. Both are
    reported; neither is the verdict on its own.
    """
    n = len(deltas)
    if n < 2:
        return {"status": Status.NOT_EVALUABLE.value, "n_pairs": n,
                "reason": "fewer than two usable pairs"}
    observed = sum(deltas) / n
    if n <= 20:
        means = [sum(s * d for s, d in zip(signs, deltas)) / n
                 for signs in itertools.product((1, -1), repeat=n)]
        p = sum(1 for m in means if abs(m) >= abs(observed) - 1e-12) / len(means)
        method = f"exact sign-flip over 2^{n} assignments"
    else:
        rng = random.Random(seed)
        hits = sum(1 for _ in range(bootstrap)
                   if abs(sum(rng.choice((1, -1)) * d for d in deltas) / n)
                   >= abs(observed) - 1e-12)
        p = (hits + 1) / (bootstrap + 1)
        method = f"{bootstrap} random sign flips"
    rng = random.Random(seed)
    resamples = sorted(sum(rng.choice(deltas) for _ in range(n)) / n
                       for _ in range(bootstrap))
    positive = sum(1 for d in deltas if d > 0)
    negative = sum(1 for d in deltas if d < 0)
    return {
        "status": Status.OK.value, "n_pairs": n,
        "mean_delta": round(observed, 6),
        "median_delta": round(_median(deltas), 6),
        "signs": {"positive": positive, "negative": negative,
                  "zero": n - positive - negative},
        "consistency": round(max(positive, negative) / n, 4),
        "deltas": [round(d, 6) for d in deltas],
        "ci95": [round(resamples[int(0.025 * bootstrap)], 6),
                 round(resamples[int(0.975 * bootstrap)], 6)],
        "p_value": round(p, 6), "method": method,
        "verdict": "DIFFERENT" if p < 0.05 else "NOT_DISTINGUISHABLE",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--world", default="D4T")
    ap.add_argument("--steps", type=int, default=1200)
    ap.add_argument("--seeds", type=int, default=12)
    ap.add_argument("--out", default="artifacts/closed_loop_addressing.json")
    args = ap.parse_args()

    bench = Bench(PROJECT_ROOT)
    seeds = [1000041 + i for i in range(args.seeds)]
    started = time.time()
    per_run: dict[str, dict[int, dict]] = {"T0": {}, "T1": {}}

    for seed in seeds:
        for arm, config in ARMS.items():
            t0 = time.time()
            trace = bench.run(args.world, args.steps, seed, config)
            per_run[arm][seed] = metrics_of(trace)
            m = per_run[arm][seed]
            print(f"  {arm} seed {seed}  "
                  f"ref={m['p_valid_reference_given_consume']}  "
                  f"exec={m['p_executable_given_consume']}  "
                  f"meals={m['effective_meals']}  "
                  f"steps={int(float(m['steps_lived']))}  "
                  f"{round(time.time() - t0, 1)}s", flush=True)

    results = {}
    for metric in PRIMARY + WASTE + SECONDARY:
        deltas, dropped = [], []
        for seed in seeds:
            a, b = per_run["T0"][seed][metric], per_run["T1"][seed][metric]
            if a.evaluable and b.evaluable:
                deltas.append(float(b) - float(a))
            else:
                dropped.append({"seed": seed, "T0": a.status.value, "T1": b.status.value})
        results[metric] = {
            "T0_mean": _mean(per_run["T0"], seeds, metric),
            "T0_median": _median_of(per_run["T0"], seeds, metric),
            "T1_mean": _mean(per_run["T1"], seeds, metric),
            "T1_median": _median_of(per_run["T1"], seeds, metric),
            "support_n": len(deltas),
            "paired": paired_test(deltas),
            "dropped_pairs": dropped,
            "family": ("PRIMARY" if metric in PRIMARY else
                       "WASTE" if metric in WASTE else "SECONDARY"),
        }

    out = {
        "schema_version": SCHEMA, "classification": CLASSIFICATION,
        "status_block": {
            "EXPRESSIVITY_CLAIM": "REFUTED",
            "SELECTOR_ISOLATION": "PASS",
            "INITIAL_BEHAVIORAL_PARITY": "PASS",
            "LOCAL_RESOLUTION_EFFECT": "DETECTED",
            "MECHANISM": "ACTION-SPACE FACTORIZATION / REFERENTIAL INDUCTIVE BIAS",
            "CLOSED_LOOP_TOTAL_EFFECT": "MEASURED_HERE",
            "E_INTERVENTION": "FROZEN", "C_INTERVENTION": "FROZEN",
        },
        "world": args.world, "steps": args.steps, "seeds": seeds,
        "statistical_unit": "trial (seed pair); steps are NOT independent replicates",
        "results": results,
        "runs": {arm: {str(s): {**{k: v.as_record() for k, v in m.items()
                                   if isinstance(v, Reading)},
                                "decomposition": m["_decomposition"],
                                "status_counts": m["_status_counts"],
                                "operation_counts": m["_operation_counts"],
                                "denominator": m["_denominator_definition"]}
                       for s, m in runs.items()} for arm, runs in per_run.items()},
        "elapsed_seconds": round(time.time() - started, 1),
    }
    path = PROJECT_ROOT / args.out
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    for family in ("PRIMARY", "WASTE", "SECONDARY"):
        print(f"\n{family}")
        for metric, result in results.items():
            if result["family"] != family:
                continue
            paired = result["paired"]
            verdict = paired.get("verdict", paired.get("status"))
            signs = paired.get("signs") or {}
            print(f"  {metric:<38} n={result['support_n']:>2}  "
                  f"T0={result['T0_median']}  T1={result['T1_median']}  "
                  f"medΔ={paired.get('median_delta')}  "
                  f"signos=+{signs.get('positive','-')}/-{signs.get('negative','-')}  "
                  f"p={paired.get('p_value')}  {verdict}")
    print(f"\nwrote {path}")
    return 0


def _mean(runs, seeds, metric):
    values = [float(runs[s][metric]) for s in seeds if runs[s][metric].evaluable]
    return round(sum(values) / len(values), 4) if values else "NOT_EVALUABLE"


def _median_of(runs, seeds, metric):
    values = [float(runs[s][metric]) for s in seeds if runs[s][metric].evaluable]
    median = _median(values)
    return round(median, 4) if median is not None else "NOT_EVALUABLE"


if __name__ == "__main__":
    raise SystemExit(main())
