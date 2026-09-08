#!/usr/bin/env python
"""Terrario v0.1 — Cognitive Development Laboratory

Usage:
    python main.py run [--config CONFIG]          Run an experiment
    python main.py verify [--scenario SCENARIO]    Verify reproducibility
    python main.py ablate [--config CONFIG]        Run ablation study
    python main.py test                            Run test suite
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import os


def cmd_run(args):
    """Run an experiment."""
    from terrario.experiment.config import ExperimentConfig
    from terrario.experiment.runner import ExperimentRunner

    config = ExperimentConfig.from_yaml(args.config)
    if args.output:
        config.output_dir = args.output

    print(f"Running experiment: {config.experiment_id}")
    print(f"  Scenario: {config.scenario_path}")
    print(f"  Agents: {', '.join(config.agent_types)}")
    print(f"  Seeds: {config.seeds}")
    print(f"  Config hash: {config.config_hash()[:16]}...")
    print()

    runner = ExperimentRunner()
    results = runner.run_comparison(config)
    report = runner.generate_report(results)
    print(report)

    os.makedirs(config.output_dir, exist_ok=True)
    report_path = os.path.join(config.output_dir, f"{config.experiment_id}_report.txt")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")


def cmd_verify(args):
    """Verify reproducibility."""
    script = os.path.join(os.path.dirname(__file__), "scripts", "verify_reproducibility.py")
    cmd = [sys.executable, script]
    if args.scenario:
        cmd.extend(["--scenario", args.scenario])
    if args.steps:
        cmd.extend(["--steps", str(args.steps)])
    subprocess.run(cmd, check=True)


def cmd_ablate(args):
    """Run ablation study."""
    script = os.path.join(os.path.dirname(__file__), "scripts", "ablation_study.py")
    cmd = [sys.executable, script]
    if args.config:
        cmd.extend(["--config", args.config])
    if args.scenario:
        cmd.extend(["--scenario", args.scenario])
    if args.output:
        cmd.extend(["--output", args.output])
    subprocess.run(cmd, check=True)


def cmd_test(args):
    """Run test suite."""
    cmd = [sys.executable, "-m", "pytest", "tests/", "-v"]
    if args.filter:
        cmd.extend(["-k", args.filter])
    subprocess.run(cmd, check=True)


def main():
    parser = argparse.ArgumentParser(
        description="Terrario v0.1 — Cognitive Development Laboratory",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # run
    p_run = subparsers.add_parser("run", help="Run an experiment")
    p_run.add_argument("--config", default="configs/default.yaml", help="Config file")
    p_run.add_argument("--output", default=None, help="Output directory")

    # verify
    p_verify = subparsers.add_parser("verify", help="Verify reproducibility")
    p_verify.add_argument("--scenario", default="scenarios/d0_differences.yaml")
    p_verify.add_argument("--steps", type=int, default=50)

    # ablate
    p_ablate = subparsers.add_parser("ablate", help="Run ablation study")
    p_ablate.add_argument("--config", default="configs/default.yaml")
    p_ablate.add_argument("--scenario", default=None)
    p_ablate.add_argument("--output", default=None)

    # test
    p_test = subparsers.add_parser("test", help="Run test suite")
    p_test.add_argument("--filter", default=None, help="pytest -k filter")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    commands = {
        "run": cmd_run,
        "verify": cmd_verify,
        "ablate": cmd_ablate,
        "test": cmd_test,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
