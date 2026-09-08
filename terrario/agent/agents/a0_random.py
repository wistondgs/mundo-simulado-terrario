"""A0_RANDOM — uniformly random baseline agent.

No learning, no state, no memory. Selects actions uniformly at random.
"""

from __future__ import annotations

from typing import Any

import torch

from terrario.agent.base import AgentInterface
from terrario.core.contracts import Transition
from terrario.core.types import TOTAL_ACTIONS, Action, Observation


class A0Random(AgentInterface):
    """Uniformly random action selection. No internal state."""

    def __init__(self, generator: torch.Generator | None = None):
        self._generator = generator or torch.Generator()
        self._trace: list[dict[str, Any]] = []
        self._step: int = 0

    def perceive(self, observation: Observation) -> None:
        self._trace.append({
            "op": "perceive",
            "step": self._step,
            "obs_hash": observation.obs_hash(),
        })

    def decide(self) -> Action:
        action_int = int(torch.randint(0, TOTAL_ACTIONS, (1,), generator=self._generator).item())
        self._trace.append({
            "op": "decide",
            "step": self._step,
            "action_int": action_int,
        })
        return Action.from_int(action_int)

    def learn(self, consequence: Transition) -> None:
        self._trace.append({
            "op": "learn",
            "step": self._step,
            "energy_delta": consequence.energy_delta,
            "done": consequence.done,
        })
        self._step += 1

    def get_internal_state(self) -> dict[str, Any]:
        return {"step": self._step, "agent_type": "A0_RANDOM"}

    def get_trace_events(self) -> list[dict[str, Any]]:
        events = list(self._trace)
        self._trace.clear()
        return events

    def reset(self) -> None:
        self._step = 0
        self._trace.clear()

    def get_parameters(self) -> dict[str, torch.Tensor]:
        return {}

    def set_parameters(self, params: dict[str, torch.Tensor]) -> None:
        pass

    def parameter_count(self) -> int:
        return 0
