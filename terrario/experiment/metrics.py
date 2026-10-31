"""Metrics for evaluating cognitive development in Terrario."""

from __future__ import annotations

import numpy as np


class MetricsCalculator:
    """Computes developmental metrics from episode data."""

    @staticmethod
    def acquisition_rate(energy_history: list[float]) -> float:
        """Capacity acquired per unit of experience.

        Measures the slope of energy improvement over time.
        Positive = learning, zero = flat, negative = degrading.
        """
        if len(energy_history) < 2:
            return 0.0
        x = np.arange(len(energy_history), dtype=np.float64)
        y = np.array(energy_history, dtype=np.float64)
        # Simple linear regression slope
        x_mean = x.mean()
        y_mean = y.mean()
        ss_xy = ((x - x_mean) * (y - y_mean)).sum()
        ss_xx = ((x - x_mean) ** 2).sum()
        if ss_xx == 0:
            return 0.0
        return float(ss_xy / ss_xx)

    @staticmethod
    def adaptation_latency(
        energy_history: list[float],
        change_step: int,
        window: int = 50,
    ) -> float:
        """Steps to recover competence after a rule change.

        Finds the number of steps after `change_step` until the energy
        returns to within one standard deviation of the pre-change baseline.
        Returns -1 if recovery never happens within the episode.
        """
        if change_step >= len(energy_history) or change_step < 1:
            return -1.0

        pre_change = energy_history[max(0, change_step - window):change_step]
        if not pre_change:
            return -1.0

        baseline = np.mean(pre_change)
        threshold = baseline - np.std(pre_change) if len(pre_change) > 1 else baseline

        post_change = energy_history[change_step:]
        for i, val in enumerate(post_change):
            if val >= threshold:
                return float(i)

        return -1.0  # never recovered

    @staticmethod
    def perseveration_cost(
        actions: list[int],
        change_step: int,
        old_optimal: int,
        window: int = 50,
    ) -> int:
        """Number of times the agent applies the obsolete rule after change.

        Counts how many times the old optimal action is taken in the
        window after the rule change.
        """
        if change_step >= len(actions):
            return 0
        end = min(change_step + window, len(actions))
        count = 0
        for i in range(change_step, end):
            if actions[i] == old_optimal:
                count += 1
        return count

    @staticmethod
    def prediction_error_history(traces: list[dict]) -> list[float]:
        """Extract only actually measured pre-outcome prediction errors."""
        errors = []
        for trace in traces:
            pe = trace.get("prediction_error")
            if pe is not None:
                errors.append(float(pe))
        return errors

    @staticmethod
    def generalization_score(
        train_performance: float,
        test_performance: float,
    ) -> float:
        """Ratio of test to train performance.

        1.0 = perfect generalization, <1.0 = degradation on novel inputs,
        >1.0 = better on test (unusual).
        """
        if train_performance == 0.0:
            return 0.0 if test_performance == 0.0 else float("inf")
        return test_performance / train_performance

    @staticmethod
    def efficiency(
        performance: float,
        compute_cost: float,
        experience: int,
    ) -> float:
        """Performance per unit of compute and experience.

        Higher = more efficient learning.
        """
        denominator = compute_cost * max(experience, 1)
        if denominator == 0:
            return 0.0
        return performance / denominator

    @staticmethod
    def compute_all(
        episode_data: dict,
        change_step: int | None = None,
    ) -> dict:
        """Compute all metrics for an episode.

        Parameters
        ----------
        episode_data:
            Dict with keys: energy_history, actions, traces, final_energy,
            compute_cost, num_steps.
        change_step:
            Step at which rules changed (if applicable).

        Returns
        -------
        dict of metric_name → value
        """
        energy_history = episode_data.get("energy_history", [])
        actions = episode_data.get("actions", [])
        traces = episode_data.get("traces", [])
        final_energy = episode_data.get("final_energy", 0.0)
        compute_cost = episode_data.get("compute_cost", 1.0)
        num_steps = episode_data.get("num_steps", len(energy_history))

        energy_slope = MetricsCalculator.acquisition_rate(energy_history)
        prediction_errors = MetricsCalculator.prediction_error_history(traces)
        metrics = {
            "final_energy": final_energy,
            "mean_energy": float(np.mean(energy_history)) if energy_history else 0.0,
            # Energy trend is an outcome of this episode, not evidence that a
            # learned mechanism acquired a capability. It remains for legacy
            # consumers under the old name, explicitly marked below.
            "acquisition_rate": energy_slope,
            "energy_slope": energy_slope,
            "learning_acquisition_rate": {"status": "NOT_MEASURED", "reason": "requires a preregistered learning contrast"},
            "prediction_errors": prediction_errors if prediction_errors else None,
            "prediction_measurement": (
                "MEASURED_PRE_OUTCOME" if prediction_errors else "NOT_MEASURED"
            ),
            "num_steps": num_steps,
        }

        if change_step is not None:
            metrics["adaptation_latency"] = MetricsCalculator.adaptation_latency(
                energy_history, change_step
            )
            # old_optimal defaults to 0; caller should provide if relevant
            old_optimal = episode_data.get("old_optimal_action", 0)
            metrics["perseveration_cost"] = MetricsCalculator.perseveration_cost(
                actions, change_step, old_optimal
            )

        if compute_cost > 0:
            metrics["efficiency"] = MetricsCalculator.efficiency(
                final_energy, compute_cost, num_steps
            )

        return metrics
