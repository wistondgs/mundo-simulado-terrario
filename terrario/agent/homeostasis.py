"""Homeostatic state — internal energy pressure that drives behavior.

NOT a reward signal. This is an internal pressure that modulates
exploration and urgency based on the agent's energy level.
"""

from __future__ import annotations

from typing import Any


class HomeostaticState:
    """Tracks internal energy level and computes drive / exploration bias.

    Energy is normalized to [0, 1]. Drive increases as energy drops
    below the threshold. Exploration bias increases when energy is low
    (the agent becomes more desperate).
    """

    def __init__(self, initial_energy: float = 1.0, threshold: float = 0.5):
        self._energy: float = max(0.0, min(1.0, initial_energy))
        self._threshold: float = threshold
        self._trace: list[dict[str, Any]] = []

    @property
    def energy(self) -> float:
        return self._energy

    @property
    def threshold(self) -> float:
        return self._threshold

    @property
    def drive(self) -> float:
        """Internal pressure: how far below threshold the energy is.

        Returns max(0, threshold - energy). Zero when energy is sufficient.
        """
        return max(0.0, self._threshold - self._energy)

    @property
    def exploration_bias(self) -> float:
        """Exploration pressure: higher when energy is low.

        Ranges from 0.0 (energy full, no pressure) to 1.0 (energy depleted).
        """
        return 1.0 - self._energy

    def update(self, energy_delta: float) -> dict[str, Any]:
        """Update internal energy level.

        Args:
            energy_delta: change in energy (positive = gain, negative = cost).

        Returns:
            trace_info dict.
        """
        old_energy = self._energy
        self._energy = max(0.0, min(1.0, self._energy + energy_delta))

        trace = {
            "op": "homeostatic_update",
            "old_energy": old_energy,
            "new_energy": self._energy,
            "energy_delta": energy_delta,
            "drive": self.drive,
            "exploration_bias": self.exploration_bias,
        }
        self._trace.append(trace)
        return trace

    def get_state(self) -> dict[str, Any]:
        """Return current state for logging."""
        return {
            "energy": self._energy,
            "threshold": self._threshold,
            "drive": self.drive,
            "exploration_bias": self.exploration_bias,
        }

    def get_trace(self) -> list[dict[str, Any]]:
        """Return and clear accumulated trace events."""
        events = list(self._trace)
        self._trace.clear()
        return events

    def reset(self, initial_energy: float = 1.0) -> None:
        self._energy = max(0.0, min(1.0, initial_energy))
        self._trace.clear()
