"""World model — predicts next latent state, energy delta, and done flag.

Takes (state_embedding, action_onehot) and predicts consequences.
"""

from __future__ import annotations

import torch
import torch.nn as nn
import torch.nn.functional as F

from terrario.core.types import TOTAL_ACTIONS


class WorldModel(nn.Module):
    """Predicts next state, energy change, and episode termination.

    Architecture:
        Linear(state_dim + action_dim, 256) → ReLU
        Linear(256, 256) → ReLU
        Heads:
            next_state_head: Linear(256, state_dim)
            energy_head: Linear(256, 1)
            done_head: Linear(256, 1)
    """

    def __init__(self, state_dim: int, action_dim: int = TOTAL_ACTIONS):
        super().__init__()
        self.state_dim = state_dim
        self.action_dim = action_dim

        self.backbone = nn.Sequential(
            nn.Linear(state_dim + action_dim, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
        )

        self.next_state_head = nn.Linear(256, state_dim)
        self.energy_head = nn.Linear(256, 1)
        self.done_head = nn.Linear(256, 1)

    def forward(
        self,
        state: torch.Tensor,
        action_onehot: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Predict consequences of taking an action in a state.

        Args:
            state: (batch, state_dim) or (state_dim,).
            action_onehot: (batch, action_dim) or (action_dim,).

        Returns:
            (next_state_pred, energy_pred, done_pred)
            next_state_pred: same batch dims as state, last dim = state_dim.
            energy_pred: (..., 1).
            done_pred: (..., 1) — logits, apply sigmoid for probability.
        """
        squeeze = state.dim() == 1
        if squeeze:
            state = state.unsqueeze(0)
            action_onehot = action_onehot.unsqueeze(0)

        x = torch.cat([state, action_onehot], dim=-1)
        features = self.backbone(x)

        next_state = self.next_state_head(features)
        energy = self.energy_head(features)
        done = self.done_head(features)

        if squeeze:
            next_state = next_state.squeeze(0)
            energy = energy.squeeze(0)
            done = done.squeeze(0)

        return next_state, energy, done

    def loss(
        self,
        state: torch.Tensor,
        action_onehot: torch.Tensor,
        next_state_target: torch.Tensor,
        energy_target: torch.Tensor,
        done_target: torch.Tensor,
    ) -> dict[str, torch.Tensor]:
        """Compute world model losses.

        Args:
            state: (batch, state_dim).
            action_onehot: (batch, action_dim).
            next_state_target: (batch, state_dim).
            energy_target: (batch,) or (batch, 1).
            done_target: (batch,) or (batch, 1) — 0.0 or 1.0.

        Returns:
            Dict with keys: loss_state, loss_energy, loss_done, loss_total.
        """
        next_state_pred, energy_pred, done_pred = self.forward(state, action_onehot)

        # Ensure targets have right shape
        if energy_target.dim() == 1:
            energy_target = energy_target.unsqueeze(-1)
        if done_target.dim() == 1:
            done_target = done_target.unsqueeze(-1)
        if energy_pred.dim() == 1:
            energy_pred = energy_pred.unsqueeze(-1)
        if done_pred.dim() == 1:
            done_pred = done_pred.unsqueeze(-1)

        loss_state = F.mse_loss(next_state_pred, next_state_target)
        loss_energy = F.mse_loss(energy_pred, energy_target)
        loss_done = F.binary_cross_entropy_with_logits(done_pred, done_target)

        return {
            "loss_state": loss_state,
            "loss_energy": loss_energy,
            "loss_done": loss_done,
            "loss_total": loss_state + loss_energy + loss_done,
        }
