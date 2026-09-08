"""Experiment runner — comparisons, ablations, and reports."""

from __future__ import annotations

import copy
from typing import Any

import numpy as np

from terrario.experiment.config import ExperimentConfig
from terrario.experiment.controller import ExperimentController


class ExperimentRunner:
    """Runs multiple experiments, compares agents, generates reports."""

    def run_comparison(self, config: ExperimentConfig) -> dict:
        """Run all agent types on the same scenario with same seeds.

        Returns a dict mapping agent_type → aggregated metrics.
        """
        controller = ExperimentController(config)
        results = controller.run()

        # Aggregate by agent type
        by_agent: dict[str, list[dict]] = {}
        for ep in results["episodes"]:
            at = ep["agent_type"]
            by_agent.setdefault(at, []).append(ep)

        comparison: dict[str, Any] = {
            "experiment_id": config.experiment_id,
            "config_hash": config.config_hash(),
            "agents": {},
        }

        for agent_type, episodes in by_agent.items():
            final_energies = [e["final_energy"] for e in episodes]
            acquisition_rates = [
                e["metrics"].get("acquisition_rate", 0.0) for e in episodes
            ]
            comparison["agents"][agent_type] = {
                "num_episodes": len(episodes),
                "mean_final_energy": float(np.mean(final_energies)),
                "std_final_energy": float(np.std(final_energies)),
                "mean_acquisition_rate": float(np.mean(acquisition_rates)),
                "std_acquisition_rate": float(np.std(acquisition_rates)),
                "episodes": episodes,
            }

            # Add adaptation metrics if available
            adaptation_latencies = [
                e["metrics"].get("adaptation_latency", -1)
                for e in episodes
                if e["metrics"].get("adaptation_latency", -1) >= 0
            ]
            if adaptation_latencies:
                comparison["agents"][agent_type]["mean_adaptation_latency"] = float(
                    np.mean(adaptation_latencies)
                )

        return comparison

    def run_ablation(
        self,
        config: ExperimentConfig,
        base_agent: str = "A4_ADVANCED",
    ) -> dict:
        """Run ablation study on A4.

        Runs the base agent, then re-runs with each module disabled.
        """
        ablation_modules = [
            "use_temporal",
            "use_episodic_memory",
            "use_longterm_memory",
            "use_world_model",
            "use_uncertainty",
            "use_online_learning",
        ]

        results: dict[str, Any] = {
            "experiment_id": f"{config.experiment_id}_ablation",
            "base_agent": base_agent,
            "conditions": {},
        }

        # Base condition (all modules enabled)
        base_config = copy.deepcopy(config)
        base_config.agent_types = [base_agent]
        controller = ExperimentController(base_config)
        base_results = controller.run()
        results["conditions"]["full"] = self._aggregate_episodes(base_results)

        # Ablation conditions
        for module in ablation_modules:
            ablated_config = copy.deepcopy(config)
            ablated_config.agent_types = [base_agent]
            ablated_config.agent_config = dict(config.agent_config)
            ablated_config.agent_config[module] = False

            controller = ExperimentController(ablated_config)
            ablated_results = controller.run()
            results["conditions"][f"no_{module}"] = self._aggregate_episodes(
                ablated_results
            )

        return results

    def generate_report(self, results: dict) -> str:
        """Generate a text report comparing agents.

        Parameters
        ----------
        results:
            Output from run_comparison() or run_ablation().

        Returns
        -------
        Formatted text report.
        """
        lines: list[str] = []
        lines.append("=" * 70)
        lines.append(f"TERRARIO EXPERIMENT REPORT")
        lines.append(f"Experiment: {results.get('experiment_id', 'unknown')}")
        lines.append(f"Config hash: {results.get('config_hash', 'N/A')}")
        lines.append("=" * 70)
        lines.append("")

        if "agents" in results:
            # Comparison report
            lines.append(f"{'Agent Type':<20} {'Mean Energy':>12} {'Std':>8} {'Acq Rate':>10} {'Adapt Lat':>10}")
            lines.append("-" * 70)

            for agent_type, data in sorted(
                results["agents"].items(),
                key=lambda x: x[1].get("mean_final_energy", 0),
                reverse=True,
            ):
                mean_e = data.get("mean_final_energy", 0)
                std_e = data.get("std_final_energy", 0)
                acq = data.get("mean_acquisition_rate", 0)
                lat = data.get("mean_adaptation_latency", -1)
                lat_str = f"{lat:.1f}" if lat >= 0 else "N/A"
                lines.append(
                    f"{agent_type:<20} {mean_e:>12.2f} {std_e:>8.2f} {acq:>10.4f} {lat_str:>10}"
                )

        elif "conditions" in results:
            # Ablation report
            lines.append(f"Base agent: {results.get('base_agent', 'unknown')}")
            lines.append("")
            lines.append(f"{'Condition':<30} {'Mean Energy':>12} {'Std':>8}")
            lines.append("-" * 70)

            for condition, data in results["conditions"].items():
                mean_e = data.get("mean_final_energy", 0)
                std_e = data.get("std_final_energy", 0)
                lines.append(f"{condition:<30} {mean_e:>12.2f} {std_e:>8.2f}")

        lines.append("")
        lines.append("=" * 70)
        return "\n".join(lines)

    def _aggregate_episodes(self, results: dict) -> dict:
        """Aggregate episode results into summary statistics."""
        episodes = results.get("episodes", [])
        if not episodes:
            return {"mean_final_energy": 0.0, "std_final_energy": 0.0, "num_episodes": 0}

        final_energies = [e["final_energy"] for e in episodes]
        return {
            "num_episodes": len(episodes),
            "mean_final_energy": float(np.mean(final_energies)),
            "std_final_energy": float(np.std(final_energies)),
        }
