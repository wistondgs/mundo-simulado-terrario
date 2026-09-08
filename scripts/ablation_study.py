#!/usr/bin/env python
"""Run ablation study on A4.

Usage:
    python scripts/ablation_study.py
    python scripts/ablation_study.py --config configs/default.yaml --scenario scenarios/d4_change.yaml
"""

from __future__ import annotations

import argparse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from terrario.experiment.config import ExperimentConfig
from terrario.experiment.runner import ExperimentRunner


def main():
    parser = argparse.ArgumentParser(description="Run A4 ablation study")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/default.yaml",
        help="Base experiment config",
    )
    parser.add_argument(
        "--scenario",
        type=str,
        default=None,
        help="Override scenario path",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help="Override max steps per episode",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Override output directory",
    )
    args = parser.parse_args()

    config = ExperimentConfig.from_yaml(args.config)
    if args.scenario:
        config.scenario_path = args.scenario
    if args.steps:
        config.max_steps_per_episode = args.steps
    if args.output:
        config.output_dir = args.output

    # Load A4 agent config if available
    a4_config_path = "configs/agent_a4.yaml"
    if os.path.exists(a4_config_path):
        import yaml
        with open(a4_config_path) as f:
            a4_data = yaml.safe_load(f)
        config.agent_config = a4_data.get("agent", {})

    print(f"A4 Ablation Study")
    print(f"  Scenario: {config.scenario_path}")
    print(f"  Seeds: {config.seeds}")
    print(f"  Episodes per condition: {config.num_episodes}")
    print(f"  Max steps: {config.max_steps_per_episode}")
    print()

    runner = ExperimentRunner()
    results = runner.run_ablation(config, base_agent="A4_ADVANCED")

    report = runner.generate_report(results)
    print(report)

    # Save report
    os.makedirs(config.output_dir, exist_ok=True)
    report_path = os.path.join(config.output_dir, f"{config.experiment_id}_ablation_report.txt")
    with open(report_path, "w") as f:
        f.write(report)
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
