"""Temporal cores — recurrent state tracking for agents.

Two implementations:
    GRUCore: standard GRU cell.
    SSMCore: simplified linear state-space model.
"""

from __future__ import annotations

from abc import abstractmethod

import torch
import torch.nn as nn


class TemporalCore(nn.Module):
    """Abstract temporal core interface."""

    @abstractmethod
    def forward(self, x: torch.Tensor, h: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """Process one timestep.

        Args:
            x: (batch, input_dim) input.
            h: (batch, hidden_dim) previous hidden state.

        Returns:
            (output, new_h) — both (batch, hidden_dim).
        """
        ...

    @abstractmethod
    def initial_state(self, batch_size: int) -> torch.Tensor:
        """Return initial hidden state (batch, hidden_dim)."""
        ...

    @property
    @abstractmethod
    def hidden_dim(self) -> int:
        ...


class GRUCore(TemporalCore):
    """GRU-based temporal core wrapping nn.GRUCell."""

    def __init__(self, input_dim: int, hidden_dim: int):
        super().__init__()
        self._hidden_dim = hidden_dim
        self.cell = nn.GRUCell(input_dim, hidden_dim)

    @property
    def hidden_dim(self) -> int:
        return self._hidden_dim

    def forward(self, x: torch.Tensor, h: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        new_h = self.cell(x, h)
        return new_h, new_h

    def initial_state(self, batch_size: int) -> torch.Tensor:
        return torch.zeros(batch_size, self._hidden_dim)


class SSMCore(TemporalCore):
    """Simplified linear State-Space Model.

    h_t = diag(a) * h_{t-1} + B @ x_t
    output = C @ h_t

    Learnable parameters:
        a: (hidden_dim,) — diagonal state transition, initialized near 1.
        B: (hidden_dim, input_dim) — input projection.
        C: (hidden_dim, hidden_dim) — output projection.
    """

    def __init__(self, input_dim: int, hidden_dim: int):
        super().__init__()
        self._hidden_dim = hidden_dim
        self.input_dim = input_dim

        # Diagonal transition initialized near 1 for long memory
        self.a = nn.Parameter(torch.ones(hidden_dim) * 0.99 + torch.randn(hidden_dim) * 0.01)
        self.B = nn.Parameter(torch.randn(hidden_dim, input_dim) * (1.0 / input_dim ** 0.5))
        self.C = nn.Parameter(torch.randn(hidden_dim, hidden_dim) * (1.0 / hidden_dim ** 0.5))

    @property
    def hidden_dim(self) -> int:
        return self._hidden_dim

    def forward(self, x: torch.Tensor, h: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """One SSM step.

        Args:
            x: (batch, input_dim).
            h: (batch, hidden_dim).

        Returns:
            (output, new_h) — both (batch, hidden_dim).
        """
        # h_t = diag(a) * h_{t-1} + B @ x_t
        new_h = self.a * h + x @ self.B.T
        output = new_h @ self.C.T
        return output, new_h

    def initial_state(self, batch_size: int) -> torch.Tensor:
        return torch.zeros(batch_size, self._hidden_dim)
