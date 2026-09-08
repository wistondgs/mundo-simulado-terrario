"""Probe interface for analyzing agent representations.

Probes are scientific instruments that decode information from the agent's
internal representations (latent vectors, hidden states, etc.) to test
hypotheses about what the agent has learned.

This module provides the abstract base class and a stub linear probe.
Full implementations will be added in future versions.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ProbeInterface(ABC):
    """Base class for scientific probes that analyze agent representations.

    A probe is trained on recorded traces (not live agent state) to decode
    whether specific information is present in the representations.
    Probes are strictly read-only analysis tools.
    """

    @abstractmethod
    def fit(self, traces: list[dict], labels: list) -> None:
        """Train the probe on recorded traces and corresponding labels.

        Args:
            traces: List of trace dicts (e.g., from PerceptionTrace.to_dict()).
            labels: Target labels for each trace.
        """
        ...

    @abstractmethod
    def predict(self, traces: list[dict]) -> list:
        """Predict labels for new traces.

        Args:
            traces: List of trace dicts.

        Returns:
            Predicted labels.
        """
        ...

    @abstractmethod
    def score(self, traces: list[dict], labels: list) -> float:
        """Evaluate probe performance.

        Args:
            traces: List of trace dicts.
            labels: Ground-truth labels.

        Returns:
            Accuracy or R² score depending on probe type.
        """
        ...


class LinearProbe(ProbeInterface):
    """Simple linear probe for decoding information from representations.

    Fits a linear model from representation features to target labels.
    This is a stub — full implementation will be added in future versions.
    """

    def __init__(self, feature_key: str = "latent_vector"):
        """Initialize the probe.

        Args:
            feature_key: Key in trace dicts that contains the feature vector.
        """
        self.feature_key = feature_key
        self._weights = None
        self._fitted = False

    def fit(self, traces: list[dict], labels: list) -> None:
        """Train the linear probe. Stub implementation."""
        raise NotImplementedError(
            "LinearProbe.fit() is not yet implemented. "
            "This is a stub for future versions."
        )

    def predict(self, traces: list[dict]) -> list:
        """Predict using the linear probe. Stub implementation."""
        raise NotImplementedError(
            "LinearProbe.predict() is not yet implemented. "
            "This is a stub for future versions."
        )

    def score(self, traces: list[dict], labels: list) -> float:
        """Score the linear probe. Stub implementation."""
        raise NotImplementedError(
            "LinearProbe.score() is not yet implemented. "
            "This is a stub for future versions."
        )
