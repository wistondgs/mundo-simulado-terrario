"""Uncertainty estimation via ensemble of prediction heads.

Uses K prediction heads; variance across the ensemble estimates uncertainty.
"""

from __future__ import annotations

import torch
import torch.nn as nn


class UncertaintyEstimator(nn.Module):
    """Ensemble of K prediction heads for uncertainty estimation.

    Each head is a small MLP: Linear(state_dim + action_dim, 128) → ReLU → Linear(128, 1).
    Uncertainty = variance across ensemble predictions.
    """

    def __init__(self, state_dim: int, action_dim: int, ensemble_size: int = 5):
        super().__init__()
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.ensemble_size = ensemble_size

        self.heads = nn.ModuleList([
            nn.Sequential(
                nn.Linear(state_dim + action_dim, 128),
                nn.ReLU(),
                nn.Linear(128, 1),
            )
            for _ in range(ensemble_size)
        ])

    def predict(
        self,
        state: torch.Tensor,
        action_onehot: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """Predict with uncertainty.

        Args:
            state: (batch, state_dim) or (state_dim,).
            action_onehot: (batch, action_dim) or (action_dim,).

        Returns:
            (mean_prediction, variance, all_predictions)
            mean_prediction: (batch, 1) or (1,).
            variance: (batch, 1) or (1,).
            all_predictions: (ensemble_size, batch, 1) or (ensemble_size, 1).
        """
        squeeze = state.dim() == 1
        if squeeze:
            state = state.unsqueeze(0)
            action_onehot = action_onehot.unsqueeze(0)

        x = torch.cat([state, action_onehot], dim=-1)

        preds = torch.stack([head(x) for head in self.heads], dim=0)  # (K, batch, 1)

        mean = preds.mean(dim=0)  # (batch, 1)
        var = preds.var(dim=0, unbiased=False)  # (batch, 1)

        if squeeze:
            mean = mean.squeeze(0)
            var = var.squeeze(0)
            preds = preds.squeeze(1)

        return mean, var, preds
