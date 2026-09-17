#!/usr/bin/env python
"""Read a finished closed-loop artifact and say what it does and does not license.

Kept apart from the experiment on purpose. The batch it reads must not be
touched while running, and the claims built on a number are a separate job from
producing it -- the failure mode this whole line of work has been correcting is
a measurement that was fine and an interpretation that was not.

Two things it enforces.

SUPPORT CATEGORIES. A conditioned ratio needs a denominator, and a seed without
one is dropped from THAT ratio and from nothing else: it remains evaluable for
consume count, successes, survival and every unconditioned outcome. So the
support is declared in four buckets -- both arms, T0 only, T1 only, neither --
because a comparison restricted to pairs with support in both answers a question
about that subset, and the treatment itself can decide whether support appears.
That changes the population under study even when the arithmetic is right.

THE INTERPRETATION LADDER. Four observations, four different claims, and the
fourth does not follow from the first three.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

#: What each observation licenses, and where the licence stops.
LADDER = [
    ("p_executable_given_consume",
     "more valid resolutions",
     "better realised execution under that selector"),
    ("n_informative",
     "more beneficial consumes",
     "better total behavioural outcome in these runs"),
    ("p_beneficial_given_valid",
     "a higher beneficial share among valid consumes",
     "better COMPOSITION of the consumes actually made -- not learned "
     "discrimination. T also changes WHICH entities get consumed, so a "
     "difference can reflect better selection, different exposure, or both. "
     "Conditioning on a post-treatment variable does not compare discriminative "
     "capacity over the same objects and opportunities."),
    ("__not_measured__",
     "improvement attributable to the agent's own updating, over comparable "
     "opportunities",
     "specific evidence of LEARNING. Not deducible from the three above, and "
     "not measured by this batch."),
]

CONDITIONED = ("p_executable_given_consume", "p_executable_given_consume_and_contact",
               "p_beneficial_given_valid", "p_valid_reference_given_consume",
               "p_informative_given_consume", "learning_conversion")


def support_categories(artifact: dict, metric: str) -> dict:
    """How many pairs had a denominator, and in which arm."""
    seeds = [str(s) for s in artifact["seeds"]]
    runs = artifact["runs"]
    buckets = {"both": [], "t0_only": [], "t1_only": [], "neither": []}
    for seed in seeds:
        a = runs["T0"][seed].get(metric, {})
        b = runs["T1"][seed].get(metric, {})
        ok_a, ok_b = a.get("status") == "OK", b.get("status") == "OK"
        key = ("both" if ok_a and ok_b else
               "t0_only" if ok_a else "t1_only" if ok_b else "neither")
        buckets[key].append(int(seed))
    return buckets


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--artifact", default="artifacts/closed_loop_addressing.json")
    ap.add_argument("--rng-mechanism", default="lineage+generation",
                    help="stamped so batches run under different coupling stay apart")
    args = ap.parse_args()

    path = PROJECT_ROOT / args.artifact
    if not path.exists():
        print(f"not finished yet: {path}")
        return 1
    artifact = json.loads(path.read_text(encoding="utf-8"))
    artifact["rng_mechanism"] = args.rng_mechanism
    artifact["batch_note"] = (
        "Runs made under the previous coupling are a DIAGNOSTIC of that defect. "
        "They must not complete pairs or feed intervals here. The demonstrated "
        "problem was a failure of coupling BETWEEN ARMS, which is not the same "
        "property as reproducibility of each run on its own.")

    print(f"RNG mechanism: {args.rng_mechanism}")
    print(f"seeds: {len(artifact['seeds'])}   steps: {artifact['steps']}\n")

    print("SUPPORT FOR CONDITIONED RATIOS")
    support = {}
    for metric in CONDITIONED:
        if metric not in artifact["results"]:
            continue
        buckets = support_categories(artifact, metric)
        support[metric] = {k: len(v) for k, v in buckets.items()}
        print(f"  {metric:<40} both={len(buckets['both']):>2}  "
              f"T0only={len(buckets['t0_only']):>2}  T1only={len(buckets['t1_only']):>2}  "
              f"neither={len(buckets['neither']):>2}")
        if buckets["t0_only"] or buckets["t1_only"]:
            print(f"      RESTRICTED POPULATION: the paired comparison covers "
                  f"{len(buckets['both'])} of {len(artifact['seeds'])} seeds. The "
                  f"treatment can decide whether support appears, so this is a "
                  f"statement about that subset, not about all seeds.")
    artifact["support_categories"] = support

    print("\nPAIRED RESULTS  (unit = seed pair; steps are not replicates)")
    for family in ("PRIMARY", "WASTE", "SECONDARY"):
        print(f"\n  {family}")
        for metric, result in artifact["results"].items():
            if result["family"] != family:
                continue
            paired = result["paired"]
            signs = paired.get("signs") or {}
            print(f"    {metric:<40} n={result.get('support_n', '-'):>2}  "
                  f"T0med={result.get('T0_median')}  T1med={result.get('T1_median')}  "
                  f"medΔ={paired.get('median_delta')}  "
                  f"meanΔ={paired.get('mean_delta')}  "
                  f"ci95={paired.get('ci95')}  "
                  f"+{signs.get('positive', '-')}/-{signs.get('negative', '-')}  "
                  f"p={paired.get('p_value')}")

    print("\nWHAT THIS LICENSES")
    for metric, observation, claim in LADDER:
        marker = "  " if metric != "__not_measured__" else "x "
        print(f"{marker}{observation}")
        print(f"      -> {claim}\n")

    print("The question this batch answers is whether T1 improves the organism's "
          "whole functioning.\nShowing that any improvement comes from LEARNING is a "
          "further attribution, and eating\nmore is not that attribution.")

    out = path.with_name(path.stem + ".analysed.json")
    out.write_text(json.dumps(artifact, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
