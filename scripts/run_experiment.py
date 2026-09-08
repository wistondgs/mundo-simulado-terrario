#!/usr/bin/env python
"""Run a Terrario experiment from a config file.

Usage:
    python scripts/run_experiment.py --config configs/default.yaml
    python scripts/run_experiment.py --config configs/default.yaml --output runs/my_experiment
"""

from __future__ import annotations

import argparse
import sys
import os

# Ensure project root is on the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from terrario.experiment.config import ExperimentConfig
from terrario.experiment.runner import ExperimentRunner


def main():
    parser = argparse.ArgumentParser(description="Run a Terrario experiment")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/default.yaml",
        help="Path to experiment config YAML",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Override output directory",
    )
    args = parser.parse_args()

    config = ExperimentConfig.from_yaml(args.config)
    if args.output:
        config.output_dir = args.output

    print(f"Running experiment: {config.experiment_id}")
    print(f"  Scenario: {config.scenario_path}")
    print(f"  Agents: {', '.join(config.agent_types)}")
    print(f"  Seeds: {config.seeds}")
    print(f"  Episodes per seed: {config.num_episodes}")
    print(f"  Max steps: {config.max_steps_per_episode}")
    print(f"  Config hash: {config.config_hash()[:16]}...")
    print()

    runner = ExperimentRunner()
    results = runner.run_comparison(config)

    report = runner.generate_report(results)
    print(report)

    # Save report
    os.makedirs(config.output_dir, exist_ok=True)
    report_path = os.path.join(config.output_dir, f"{config.experiment_id}_report.txt")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
