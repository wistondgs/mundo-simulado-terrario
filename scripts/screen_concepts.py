#!/usr/bin/env python
"""Screening: what does each concept contribute, measured several ways.

Mixing three concepts and watching something happen does not say which of the
three did it.  Measuring each one alone first does: the contribution of a
concept is the difference between the organism that has it and the same
organism without it, everything else held fixed.

    full organism                     the reference
    full organism minus one concept   one condition per concept
    difference, per mesh              that concept's contribution HERE

"Here" carries weight.  A concept's contribution is not a property of the
concept: it depends on the world and on what else is present.  The planner is
worth one thing in D0 and another in D4T.  That is the finding, not the noise.

Nothing here is evidence.  Every run is ENGINEERING_SANDBOX, the firewall
refuses to publish it, and the report says so in its own body.  What it is for
is deciding which of the 2^8 mixes deserve a preregistered experiment.

RESUMABLE BY DESIGN.  A campaign runs for hours and the power does go out, so
every finished run is appended to a JSONL as it completes and a restart skips
what is already there.  Interrupting this costs the run in flight and nothing
else.

    scripts/screen_concepts.py --world D4T --steps 120 --seeds 3
    scripts/screen_concepts.py --world D4T --steps 120 --seeds 3   # continues
"""
from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.agent_composition import CONCEPTS
from terrario.lab.api import LabAPI
from terrario.lab.run_measures import measure_run

SCHEMA = "terrario.lab.concept-screening/v1"
CLASSIFICATION = "ENGINEERING_SANDBOX_NOT_EVIDENCE"


def conditions(keys):
    """The reference plus one ablation each: k+1 conditions, not 2^k."""
    yield "completo", {}
    for key in keys:
        yield f"sin:{key}", {key: False}


def already_done(path):
    if not path.exists():
        return {}
    done = {}
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue  # a line torn in half by the cut; the run is simply redone
        done[(row["condition"], row["seed"])] = row
    return done


def run_one(api, world, steps, seed, mix):
    status, run = api.dispatch("POST", "/api/sandbox", {
        "world_id": world, "agent_reference": "A4", "step_limit": steps + 1,
        "agent_seed": seed, "world_seed": 42, "agent_configuration": mix})
    if status != 201:
        raise RuntimeError(f"sandbox refused the mix: {run}")
    run_id = run["sandbox_run_id"]
    try:
        api.dispatch("POST", f"/api/sandbox/{run_id}/run", {"steps": steps})
        _, timeline = api.dispatch("GET", f"/api/sandbox/{run_id}/trace")
        return measure_run(timeline)
    finally:
        api.dispatch("POST", f"/api/sandbox/{run_id}/stop")


def effects(rows, keys):
    """Contribution per concept per mesh: reference minus the ablated arm."""
    def sample(condition, mesh):
        return [r["measures"][mesh] for r in rows
                if r["condition"] == condition and isinstance(r["measures"].get(mesh), (int, float))]

    meshes = sorted({m for r in rows for m in r["measures"]})
    out = []
    for key in keys:
        for mesh in meshes:
            con, sin = sample("completo", mesh), sample(f"sin:{key}", mesh)
            if not con or not sin:
                out.append({"concept": key, "mesh": mesh, "evaluable": False,
                            "reason": "NOT_EVALUABLE_IN_ONE_ARM"})
                continue
            mean_con, mean_sin = sum(con) / len(con), sum(sin) / len(sin)
            spread = max(max(con) - min(con), max(sin) - min(sin))
            out.append({
                "concept": key, "mesh": mesh, "evaluable": True,
                "with": round(mean_con, 4), "without": round(mean_sin, 4),
                "effect": round(mean_con - mean_sin, 4),
                "within_arm_spread": round(spread, 4),
                # The honest guard against reading noise as a finding: an effect
                # smaller than the spread among seeds of a single arm is not a
                # result, it is the seed.
                "larger_than_seed_spread": abs(mean_con - mean_sin) > spread,
            })
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--world", default="D4T")
    parser.add_argument("--steps", type=int, default=120)
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument("--out", default="runs/screening")
    args = parser.parse_args()

    keys = [c.key for c in CONCEPTS]
    seeds = [1000045 + i for i in range(args.seeds)]
    out_dir = PROJECT_ROOT / args.out
    out_dir.mkdir(parents=True, exist_ok=True)
    tag = f"{args.world}-{args.steps}steps-{args.seeds}seeds"
    ledger = out_dir / f"{tag}.jsonl"

    done = already_done(ledger)
    plan = [(name, mix, seed) for name, mix in conditions(keys) for seed in seeds]
    pending = [item for item in plan if (item[0], item[2]) not in done]
    print(f"{SCHEMA}  {CLASSIFICATION}")
    print(f"mundo {args.world} · {args.steps} pasos · {len(plan)} corridas · "
          f"{len(done)} ya hechas · {len(pending)} por hacer", flush=True)

    with tempfile.TemporaryDirectory() as tmp:
        api = LabAPI(PROJECT_ROOT, data_root=Path(tmp) / ".terrario")
        for index, (name, mix, seed) in enumerate(pending, 1):
            started = time.time()
            measured = run_one(api, args.world, args.steps, seed, mix)
            row = {"condition": name, "seed": seed, "world": args.world, "steps": args.steps,
                   "seconds": round(time.time() - started, 1),
                   "measures": {m["key"]: (m["value"] if m["evaluable"] else None)
                                for m in measured["measures"]}}
            # Appended and flushed per run: a cut costs this one, never the rest.
            with ledger.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(row, ensure_ascii=False) + "\n")
                handle.flush()
            print(f"  [{index}/{len(pending)}] {name:28} semilla {seed} "
                  f"{row['seconds']:>6.1f}s", flush=True)

    rows = list(already_done(ledger).values())
    report = {"schema_version": SCHEMA, "classification": CLASSIFICATION,
              "world": args.world, "steps": args.steps, "seeds": seeds,
              "runs": len(rows), "effects": effects(rows, keys),
              "reading_rule": ("Un efecto menor que la dispersión entre semillas de un mismo "
                               "brazo no es un hallazgo: es la semilla. Mirá "
                               "larger_than_seed_spread antes que effect.")}
    report_path = out_dir / f"{tag}.report.json"
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\ninforme: {report_path}")
    for row in report["effects"]:
        if row.get("larger_than_seed_spread"):
            print(f"  {row['concept']:22} {row['mesh']:24} efecto {row['effect']:+.3f}")


if __name__ == "__main__":
    main()
