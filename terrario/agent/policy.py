"""Policy head and planner for action selection.

PolicyHead: maps state to action logits.
Planner: uses WorldModel for H-step rollouts to refine action selection.
"""

from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn
import torch.nn.functional as F

from terrario.core.types import TOTAL_ACTIONS


class PolicyHead(nn.Module):
    """Maps state embedding to action logits.

    Architecture: Linear(state_dim, 256) → ReLU → Linear(256, TOTAL_ACTIONS)
    """

    def __init__(self, state_dim: int):
        super().__init__()
        self.state_dim = state_dim

        self.net = nn.Sequential(
            nn.Linear(state_dim, 256),
            nn.ReLU(),
            nn.Linear(256, TOTAL_ACTIONS),
        )

    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """Compute action logits.

        Args:
            state: (batch, state_dim) or (state_dim,).

        Returns:
            (batch, TOTAL_ACTIONS) or (TOTAL_ACTIONS,) logits.
        """
        return self.net(state)

    def sample(
        self,
        logits: torch.Tensor,
        temperature: float = 1.0,
        generator: torch.Generator | None = None,
    ) -> tuple[int, torch.Tensor, torch.Tensor]:
        """Sample an action from the policy distribution.

        Args:
            logits: (TOTAL_ACTIONS,) action logits.
            temperature: sampling temperature (higher = more random).
            generator: torch.Generator for reproducibility.

        Returns:
            (action_int, log_prob, probs)
        """
        if temperature <= 0:
            temperature = 1e-8
        scaled = logits / temperature
        probs = F.softmax(scaled, dim=-1)
        if generator is not None:
            # Keep the campaign RNG on CPU so seeded action draws are portable
            # across CPU and CUDA execution.
            _ = torch.rand(probs.shape, generator=generator)
            action = torch.multinomial(probs.detach().cpu(), 1, generator=generator).item()
        else:
            action = torch.distributions.Categorical(probs).sample().item()
        log_prob = torch.log(probs[action] + 1e-8)
        return action, log_prob, probs

    def greedy(self, logits: torch.Tensor) -> int:
        """Select the action with highest logit.

        Args:
            logits: (TOTAL_ACTIONS,) action logits.

        Returns:
            action_int.
        """
        return logits.argmax().item()


class Planner:
    """Model-based planner using H-step rollouts through the WorldModel.

    Samples random action sequences, evaluates them with the world model,
    and returns the first action of the best sequence.
    """

    def __init__(self, generator: torch.Generator | None = None):
        self._generator = generator or torch.Generator()
        self._trace: list[dict[str, Any]] = []

    def plan(
        self,
        state: torch.Tensor,
        world_model: nn.Module,
        horizon: int = 5,
        num_candidates: int = 10,
    ) -> tuple[int, dict[str, Any]]:
        """Plan the best action via random shooting.

        Args:
            state: (state_dim,) current state embedding.
            world_model: WorldModel instance for rollouts.
            horizon: number of steps to look ahead.
            num_candidates: number of random action sequences to try.

        Returns:
            (best_action_int, trace_info)
        """
        best_action = 0
        best_score = float("-inf")
        all_rollouts: list[dict[str, Any]] = []

        with torch.no_grad():
            for candidate_idx in range(num_candidates):
                # Sample random action sequence
                actions = torch.randint(
                    0, TOTAL_ACTIONS, (horizon,), generator=self._generator
                ).tolist()

                # Rollout through world model
                sim_state = state.clone()
                total_energy = 0.0
                done_prob_accum = 0.0

                for step, action_int in enumerate(actions):
                    action_onehot = torch.zeros(TOTAL_ACTIONS, device=state.device, dtype=state.dtype)
                    action_onehot[action_int] = 1.0

                    next_state, energy_pred, done_pred = world_model(sim_state, action_onehot)

                    total_energy += energy_pred.item()
                    done_prob = torch.sigmoid(done_pred).item()
                    done_prob_accum += done_prob

                    sim_state = next_state

                    # Early termination if done is very likely
                    if done_prob > 0.9:
                        break

                # Score: total predicted energy minus done penalty
                score = total_energy - 10.0 * done_prob_accum

                rollout_info = {
                    "candidate": candidate_idx,
                    "actions": actions,
                    "total_energy": total_energy,
                    "done_prob": done_prob_accum,
                    "score": score,
                }
                all_rollouts.append(rollout_info)

                if score > best_score:
                    best_score = score
                    best_action = actions[0]

        trace = {
            "op": "plan",
            "horizon": horizon,
            "num_candidates": num_candidates,
            "best_action": best_action,
            "best_score": best_score,
            "rollouts": all_rollouts,
        }
        self._trace.append(trace)
        return best_action, trace

    def get_trace(self) -> list[dict[str, Any]]:
        """Return and clear accumulated trace events."""
        events = list(self._trace)
        self._trace.clear()
        return events
