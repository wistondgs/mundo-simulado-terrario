#!/usr/bin/env python
"""Run the preregistered H-ADAPT-001 adaptation protocol."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from terrario.experiment.adaptation import AdaptationProtocolRunner, VARIANTS, lock_protocol


PILOT_SEEDS = [11, 23, 37, 53]
CONFIRMATORY_SEEDS = list(range(101, 125))


def parse_seed_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("pilot", "lock", "confirmatory"), default="pilot")
    parser.add_argument("--output", default="runs/h_adapt_001")
    parser.add_argument("--seeds", default=None, help="Comma-separated paired seeds")
    parser.add_argument("--variants", default=",".join(VARIANTS), help="Comma-separated variant IDs")
    parser.add_argument("--forensic", action="store_true", help="Capture bounded forensic windows")
    args = parser.parse_args()

    output = Path(args.output)
    lock_path = output / "H_ADAPT_001_PROTOCOL_LOCK.json"
    runner = AdaptationProtocolRunner(
        "scenarios/d4_adaptation_scientific.yaml",
        "scenarios/d4_adaptation_transfer.yaml",
        str(output),
        observer_mode="forensic_full" if args.forensic else "scientific_standard",
    )

    if args.stage == "lock":
        pilot_path = output / "h_adapt_001_pilot_results.json"
        if not pilot_path.exists():
            parser.error(f"protocol lock requires a completed clean pilot at {pilot_path}")
        pilot = json.loads(pilot_path.read_text())
        if pilot.get("pilot_diagnostic", {}).get("status") != "PASS":
            parser.error("protocol lock prohibited: pilot diagnostic did not pass every validity gate")
        lock_protocol(str(lock_path), runner)
        print(f"Protocol locked: {lock_path}")
        return

    if args.stage == "confirmatory" and not lock_path.exists():
        parser.error(f"confirmatory runs require the protocol lock at {lock_path}")

    default_seeds = PILOT_SEEDS if args.stage == "pilot" else CONFIRMATORY_SEEDS
    seeds = parse_seed_list(args.seeds) if args.seeds else default_seeds
    variants = [item.strip() for item in args.variants.split(",") if item.strip()]
    unknown = sorted(set(variants) - set(VARIANTS))
    if unknown:
        parser.error(f"unknown variants: {', '.join(unknown)}")

    result = runner.run(seeds=seeds, variants=variants)
    result["stage"] = args.stage
    result["seeds"] = seeds
    result["protocol_hash"] = runner.protocol_hash()
    result["code_hash"] = runner.code_hash()
    output.mkdir(parents=True, exist_ok=True)
    result_path = output / f"h_adapt_001_{args.stage}_results.json"
    result_path.write_text(json.dumps(result, indent=2, default=str))
    print(f"Results: {result_path}")
    print(json.dumps(result["summary"], indent=2, default=str))


if __name__ == "__main__":
    main()
