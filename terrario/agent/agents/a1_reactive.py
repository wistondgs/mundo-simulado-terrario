"""A1_REACTIVE — reactive agent with encoder → policy head, no temporal state.

Learns via REINFORCE. No memory, no world model, no temporal core.
π(obs) → action.
"""

from __future__ import annotations

from typing import Any

import torch

from terrario.agent.base import AgentInterface
from terrario.agent.encoder import PerceptualEncoder
from terrario.agent.policy import PolicyHead
from terrario.core.contracts import Transition
from terrario.core.types import TOTAL_ACTIONS, Action, Observation


class A1Reactive(AgentInterface):
    """Reactive agent: encoder → policy head → action.

    No temporal state, no memory, no world model.
    Learns via REINFORCE with energy_delta as reward signal.
    """

    def __init__(
        self,
        num_channels: int = 4,
        view_size: int = 5,
        latent_dim: int = 128,
        lr: float = 3e-4,
        generator: torch.Generator | None = None,
    ):
        self._generator = generator or torch.Generator()
        self._trace: list[dict[str, Any]] = []
        self._step: int = 0

        self.encoder = PerceptualEncoder(num_channels, view_size, latent_dim)
        self.policy_head = PolicyHead(latent_dim)

        self._optimizer = torch.optim.Adam(
            list(self.encoder.parameters()) + list(self.policy_head.parameters()),
            lr=lr,
        )

        # REINFORCE state
        self._last_log_prob: torch.Tensor | None = None
        self._last_action: int = 0
        self._last_latent: torch.Tensor | None = None

    def perceive(self, observation: Observation) -> None:
        self._last_latent = self.encoder.encode_observation(observation.channels)
        self._trace.append({
            "op": "perceive",
            "step": self._step,
            "latent_norm": self._last_latent.norm().item(),
        })

    def decide(self) -> Action:
        if self._last_latent is None:
            # No observation yet — random action
            action_int = int(torch.randint(0, TOTAL_ACTIONS, (1,), generator=self._generator).item())
            return Action.from_int(action_int)

        logits = self.policy_head(self._last_latent)
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
            "max_prob": probs.max().item(),
        })
        return Action.from_int(action_int)

    def learn(self, consequence: Transition) -> None:
        if self._last_log_prob is not None:
            # REINFORCE: -log_prob * reward
            reward = consequence.energy_delta
            loss = -self._last_log_prob * reward

            self._optimizer.zero_grad()
            loss.backward()
            self._optimizer.step()

            self._trace.append({
                "op": "learn",
                "step": self._step,
                "loss": loss.item(),
                "reward": reward,
                "done": consequence.done,
            })

        self._step += 1

    def get_internal_state(self) -> dict[str, Any]:
        return {
            "step": self._step,
            "agent_type": "A1_REACTIVE",
            "latent_norm": self._last_latent.norm().item() if self._last_latent is not None else 0.0,
        }

    def get_trace_events(self) -> list[dict[str, Any]]:
        events = list(self._trace)
        self._trace.clear()
        return events

    def reset(self) -> None:
        self._step = 0
        self._trace.clear()
        self._last_log_prob = None
        self._last_action = 0
        self._last_latent = None

    def get_parameters(self) -> dict[str, torch.Tensor]:
        params: dict[str, torch.Tensor] = {}
        for name, p in self.encoder.named_parameters():
            params[f"encoder.{name}"] = p.detach().clone()
        for name, p in self.policy_head.named_parameters():
            params[f"policy_head.{name}"] = p.detach().clone()
        return params

    def set_parameters(self, params: dict[str, torch.Tensor]) -> None:
        with torch.no_grad():
            for name, p in self.encoder.named_parameters():
                key = f"encoder.{name}"
                if key in params:
                    p.copy_(params[key])
            for name, p in self.policy_head.named_parameters():
                key = f"policy_head.{name}"
                if key in params:
                    p.copy_(params[key])

    def parameter_count(self) -> int:
        return sum(p.numel() for p in self.encoder.parameters()) + \
               sum(p.numel() for p in self.policy_head.parameters())
