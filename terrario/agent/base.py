"""Agent interface — the contract every agent in Terrario must implement."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import torch

from terrario.core.types import Action, Consequence, Observation


class AgentInterface(ABC):
    """Common interface for all agents.

    Every agent follows the perceive → decide → learn cycle.
    Trace events are collected for the observer subsystem.
    """

    @abstractmethod
    def perceive(self, observation: Observation) -> None:
        """Ingest a raw observation into the agent's internal state."""
        ...

    @abstractmethod
    def decide(self) -> Action:
        """Produce an action based on current internal state."""
        ...

    @abstractmethod
    def learn(self, consequence: Consequence) -> None:
        """Update internal parameters from the consequence of the last action."""
        ...

    @abstractmethod
    def get_internal_state(self) -> dict[str, Any]:
        """Return a snapshot of the agent's internal state for logging."""
        ...

    @abstractmethod
    def get_trace_events(self) -> list[dict[str, Any]]:
        """Return accumulated trace events and clear the buffer."""
        ...

    @abstractmethod
    def reset(self) -> None:
        """Reset the agent to its initial state (new episode)."""
        ...

    @abstractmethod
    def get_parameters(self) -> dict[str, torch.Tensor]:
        """Return all learnable parameters as a flat dict."""
        ...

    @abstractmethod
    def set_parameters(self, params: dict[str, torch.Tensor]) -> None:
        """Load learnable parameters from a flat dict."""
        ...

    @abstractmethod
    def parameter_count(self) -> int:
        """Total number of learnable parameters."""
        ...
