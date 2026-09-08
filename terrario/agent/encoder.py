"""Perceptual encoder — maps raw observation channels to a latent embedding.

No semantic labels, no global coordinates. The encoder sees only a local
window of raw perceptual channels and produces a fixed-size latent vector.
"""

from __future__ import annotations

import math

import numpy as np
import torch
import torch.nn as nn


class PerceptualEncoder(nn.Module):
    """Convolutional encoder: (C, H, W) → (latent_dim,).

    Architecture:
        Conv2d(C, 32, 3, padding=1) → ReLU
        Conv2d(32, 64, 3, padding=1) → ReLU
        Conv2d(64, 64, 3, stride=2, padding=1) → ReLU
        Flatten → Linear(64*H'*W', latent_dim) → LayerNorm
    """

    def __init__(
        self,
        in_channels: int,
        view_size: int,
        latent_dim: int = 128,
    ):
        super().__init__()
        self.in_channels = in_channels
        self.view_size = view_size
        self.latent_dim = latent_dim

        # After stride-2 conv: ceil(view_size / 2)
        reduced = math.ceil(view_size / 2)
        flat_dim = 64 * reduced * reduced

        self.conv = nn.Sequential(
            nn.Conv2d(in_channels, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, kernel_size=3, stride=2, padding=1),
            nn.ReLU(),
        )
        self.head = nn.Sequential(
            nn.Flatten(),
            nn.Linear(flat_dim, latent_dim),
            nn.LayerNorm(latent_dim),
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Encode an observation window.

        Args:
            x: (batch, C, H, W) or (C, H, W) tensor.

        Returns:
            (batch, latent_dim) or (latent_dim,) latent embedding.
        """
        squeeze = x.dim() == 3
        if squeeze:
            x = x.unsqueeze(0)
        features = self.conv(x)
        out = self.head(features)
        if squeeze:
            out = out.squeeze(0)
        return out

    def encode_observation(self, channels: np.ndarray) -> torch.Tensor:
        """Convenience: encode a numpy observation array to latent.

        Args:
            channels: (C, H, W) numpy array from Observation.channels.

        Returns:
            (latent_dim,) tensor.
        """
        x = torch.from_numpy(channels).float()
        with torch.no_grad():
            return self.forward(x)
