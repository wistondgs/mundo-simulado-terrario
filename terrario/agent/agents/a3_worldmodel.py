"""A3_WORLD_MODEL — agent with world model but no episodic or long-term memory.

Encoder → GRUCore → WorldModel + PolicyHead.
Learns world model predictions + policy via REINFORCE.
"""

from __future__ import annotations

from typing import Any

import torch
import torch.nn.functional as F

from terrario.agent.base import AgentInterface
from terrario.agent.encoder import PerceptualEncoder
from terrario.agent.policy import PolicyHead
from terrario.agent.temporal import GRUCore
from terrario.agent.world_model import WorldModel
from terrario.core.contracts import Transition
from terrario.core.types import TOTAL_ACTIONS, Action, Observation


class A3WorldModel(AgentInterface):
    """World model agent: encoder → GRU → world model + policy head.

    Has temporal state and world model but NO episodic memory, NO long-term memory.
    Learns world model (next state, energy, done) + policy via REINFORCE.
    """

    def __init__(
        self,
        num_channels: int = 4,
        view_size: int = 5,
        latent_dim: int = 128,
        hidden_dim: int = 256,
        lr: float = 3e-4,
        generator: torch.Generator | None = None,
    ):
        self._generator = generator or torch.Generator()
        self._trace: list[dict[str, Any]] = []
        self._step: int = 0

        self.latent_dim = latent_dim
        self.hidden_dim = hidden_dim

        self.encoder = PerceptualEncoder(num_channels, view_size, latent_dim)
        self.temporal_core = GRUCore(latent_dim, hidden_dim)
        self.world_model = WorldModel(hidden_dim, TOTAL_ACTIONS)
        self.policy_head = PolicyHead(hidden_dim)

        self._optimizer = torch.optim.Adam(
            list(self.encoder.parameters())
            + list(self.temporal_core.parameters())
            + list(self.world_model.parameters())
            + list(self.policy_head.parameters()),
            lr=lr,
        )

        # Temporal state
        self._hidden: torch.Tensor = self.temporal_core.initial_state(1)

        # State tracking for world model learning
        self._last_latent: torch.Tensor | None = None
        self._last_hidden: torch.Tensor | None = None
        self._last_action: int = 0
        self._last_log_prob: torch.Tensor | None = None
        self.last_prediction_error: float | None = None
        self._last_prediction: dict[str, float] = {}

    def perceive(self, observation: Observation) -> None:
        self._last_latent = self.encoder.encode_observation(observation.channels)
        self._trace.append({
            "op": "perceive",
            "step": self._step,
            "latent_norm": self._last_latent.norm().item(),
        })

    def decide(self) -> Action:
        if self._last_latent is None:
            action_int = int(torch.randint(0, TOTAL_ACTIONS, (1,), generator=self._generator).item())
            return Action.from_int(action_int)

        # Update temporal state
        x = self._last_latent.unsqueeze(0)
        self._last_hidden = self._hidden.clone()
        output, self._hidden = self.temporal_core(x, self._hidden)
        self._hidden = self._hidden.detach()
        h = output.squeeze(0)

        logits = self.policy_head(h)
        action_int, log_prob, probs = self.policy_head.sample(
            logits, temperature=1.0, generator=self._generator
        )

        self._last_log_prob = log_prob
        self._last_action = action_int

        self._trace.append({
            "op": "decide",
            "step": self._step,
            "action_int": action_int,
            "log_prob": log_prob.item(),
            "hidden_norm": self._hidden.norm().item(),
        })
        return Action.from_int(action_int)

    def learn(self, consequence: Transition) -> None:
        if self._last_hidden is None or self._last_latent is None:
            self._step += 1
            return

        # World model loss: predict next hidden state, energy, done
        h_prev = self._last_hidden.squeeze(0)  # (hidden_dim,)
        action_onehot = torch.zeros(TOTAL_ACTIONS, device=h_prev.device, dtype=h_prev.dtype)
        action_onehot[self._last_action] = 1.0
        with torch.no_grad():
            _, energy_prediction, done_prediction = self.world_model(h_prev, action_onehot)
            self.last_prediction_error = abs(float(energy_prediction.item()) - consequence.energy_delta)
            self._last_prediction = {
                "energy": float(energy_prediction.item()),
                "done_probability": float(torch.sigmoid(done_prediction).item()),
                "prediction_error": self.last_prediction_error,
            }

        # Target for next_state: the current hidden state (after transition)
        next_state_target = self._hidden.squeeze(0).detach()
        energy_target = torch.tensor([consequence.energy_delta], device=h_prev.device, dtype=h_prev.dtype)
        done_target = torch.tensor([1.0 if consequence.done else 0.0], device=h_prev.device, dtype=h_prev.dtype)

        wm_losses = self.world_model.loss(
            h_prev.unsqueeze(0),
            action_onehot.unsqueeze(0),
            next_state_target.unsqueeze(0),
            energy_target,
            done_target,
        )

        # Policy loss: REINFORCE
        policy_loss = torch.tensor(0.0, device=h_prev.device)
        if self._last_log_prob is not None:
            reward = consequence.energy_delta
            policy_loss = -self._last_log_prob * reward

        total_loss = wm_losses["loss_total"] + policy_loss

        self._optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(
            [p for m in [self.encoder, self.temporal_core, self.world_model, self.policy_head]
             for p in m.parameters() if p.grad is not None],
            1.0,
        )
        self._optimizer.step()

        self._trace.append({
            "op": "learn",
            "step": self._step,
            "wm_loss": wm_losses["loss_total"].item(),
            "wm_loss_state": wm_losses["loss_state"].item(),
            "wm_loss_energy": wm_losses["loss_energy"].item(),
            "wm_loss_done": wm_losses["loss_done"].item(),
            "policy_loss": policy_loss.item() if isinstance(policy_loss, torch.Tensor) else policy_loss,
            "total_loss": total_loss.item(),
            "done": consequence.done,
        })

        self._step += 1

    def get_internal_state(self) -> dict[str, Any]:
        return {
            "step": self._step,
            "agent_type": "A3_WORLD_MODEL",
            "hidden_norm": self._hidden.norm().item(),
            "latent_norm": self._last_latent.norm().item() if self._last_latent is not None else 0.0,
        }

    def get_scientific_state(self) -> dict[str, Any]:
        """Detached observer-only state; never used by action selection input."""
        return {
            "latent": self._last_latent.detach().clone() if self._last_latent is not None else None,
            "temporal": self._hidden.detach().clone(),
            "prediction": dict(self._last_prediction),
            "prediction_error": self.last_prediction_error,
        }

    def get_trace_events(self) -> list[dict[str, Any]]:
        events = list(self._trace)
        self._trace.clear()
        return events

    def reset(self) -> None:
        self._step = 0
        self._trace.clear()
        self._hidden = self.temporal_core.initial_state(1)
        self._last_latent = None
        self._last_hidden = None
        self._last_action = 0
        self._last_log_prob = None
        self.last_prediction_error = None
        self._last_prediction = {}

    def get_parameters(self) -> dict[str, torch.Tensor]:
        params: dict[str, torch.Tensor] = {}
        for prefix, module in [
            ("encoder", self.encoder),
            ("temporal_core", self.temporal_core),
            ("world_model", self.world_model),
            ("policy_head", self.policy_head),
        ]:
            for name, p in module.named_parameters():
                params[f"{prefix}.{name}"] = p.detach().clone()
        return params

    def set_parameters(self, params: dict[str, torch.Tensor]) -> None:
        with torch.no_grad():
            for prefix, module in [
                ("encoder", self.encoder),
                ("temporal_core", self.temporal_core),
                ("world_model", self.world_model),
                ("policy_head", self.policy_head),
            ]:
                for name, p in module.named_parameters():
                    key = f"{prefix}.{name}"
                    if key in params:
                        p.copy_(params[key])

    def parameter_count(self) -> int:
        return (
            sum(p.numel() for p in self.encoder.parameters())
            + sum(p.numel() for p in self.temporal_core.parameters())
            + sum(p.numel() for p in self.world_model.parameters())
            + sum(p.numel() for p in self.policy_head.parameters())
        )
