#!/usr/bin/env python
"""Run the preregistered H-ADAPT-001 adaptation protocol."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from terrario.experiment.adaptation import AdaptationProtocolRunner, VARIANTS, analyze_records, lock_protocol


PILOT_SEEDS = [11, 23, 37, 53]
CONFIRMATORY_SEEDS = list(range(101, 125))


def parse_seed_list(value: str) -> list[int]:
    return [int(item.strip()) for item in value.split(",") if item.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("preflight", "pilot", "analysis", "lock", "confirmatory"), default="pilot")
    parser.add_argument("--output", default="runs/h_adapt_001")
    parser.add_argument("--seeds", default=None, help="Comma-separated paired seeds")
    parser.add_argument("--variants", default=",".join(VARIANTS), help="Comma-separated variant IDs")
    parser.add_argument("--forensic", action="store_true", help="Capture bounded forensic windows")
    parser.add_argument("--resume", action="store_true", help="Reuse only runs with a valid completion certificate")
    parser.add_argument("--retry-invalid", action="store_true", help="With --resume, re-run completed but experimentally invalid runs")
    args = parser.parse_args()

    output = Path(args.output)
    lock_path = output / "H_ADAPT_001_PROTOCOL_LOCK.json"
    runner = AdaptationProtocolRunner(
        "scenarios/d4_adaptation_scientific.yaml",
        "scenarios/d4_adaptation_transfer.yaml",
        str(output),
        observer_mode="forensic_full" if args.forensic else "scientific_standard",
    )

    if args.retry_invalid and not args.resume:
        parser.error("--retry-invalid requires --resume")

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

    if args.stage == "analysis":
        pilot_path = output / "h_adapt_001_pilot_results.json"
        if not pilot_path.exists():
            parser.error(f"analysis requires pilot results at {pilot_path}")
        pilot = json.loads(pilot_path.read_text())
        analysis_path = output / "h_adapt_001_analysis_results.json"
        analysis = analyze_records(pilot.get("records", []))
        analysis.update({"stage": "analysis", "source": str(pilot_path), "pilot_diagnostic": pilot.get("pilot_diagnostic", {})})
        analysis_path.write_text(json.dumps(analysis, indent=2, default=str))
        print(f"Analysis: {analysis_path}")
        print(json.dumps(analysis["analysis_population"], indent=2, default=str))
        return

    default_seeds = PILOT_SEEDS if args.stage in {"pilot", "preflight"} else CONFIRMATORY_SEEDS
    seeds = parse_seed_list(args.seeds) if args.seeds else default_seeds
    variants = [item.strip() for item in args.variants.split(",") if item.strip()]
    unknown = sorted(set(variants) - set(VARIANTS))
    if unknown:
        parser.error(f"unknown variants: {', '.join(unknown)}")

    output.mkdir(parents=True, exist_ok=True)
    result_path = output / f"h_adapt_001_{args.stage}_results.json"
    if args.stage == "preflight":
        result = runner.preflight(seeds, variants)
        result.update({"stage": args.stage, "seeds": seeds, "variants": variants})
        result_path.write_text(json.dumps(result, indent=2, default=str))
        print(f"Preflight: {result_path}")
        print(json.dumps(result, indent=2, default=str))
        return

    existing_records = []
    if args.resume:
        if not result_path.exists():
            parser.error(f"--resume requires a prior result file at {result_path}")
        previous = json.loads(result_path.read_text())
        existing_records = previous.get("records", [])

    result = runner.run(
        seeds=seeds, variants=variants, existing_records=existing_records, resume=args.resume,
        retry_invalid=args.retry_invalid, progress_path=result_path,
    )
    result["stage"] = args.stage
    result["seeds"] = seeds
    result["protocol_hash"] = runner.protocol_hash()
    result["code_hash"] = runner.code_hash()
    result_path.write_text(json.dumps(result, indent=2, default=str))
    print(f"Results: {result_path}")
    print(json.dumps(result["summary"], indent=2, default=str))


if __name__ == "__main__":
    main()
