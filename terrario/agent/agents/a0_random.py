"""A0_RANDOM — uniformly random baseline agent.

No learning, no state, no memory. Selects actions uniformly at random.
"""

from __future__ import annotations

from typing import Any
import base64

import torch

from terrario.agent.base import AgentInterface
from terrario.core.contracts import Transition
from terrario.core.action_contract import (
    MAX_TARGET_SLOTS, TARGET_BEARING_OPERATIONS, AddressingMode, SelectorType)
from terrario.core.types import (
    NUM_DIRECTIONS, TOTAL_ACTIONS, Action, ActionType, Direction, Observation,
)


class A0Random(AgentInterface):
    """Uniformly random action selection. No internal state."""

    def __init__(self, generator: torch.Generator | None = None,
                 addressing_mode: str = "T0_DIRECTIONAL"):
        self._generator = generator or torch.Generator()
        # The chance baseline has to exist under BOTH contracts or the
        # comparison is between an organism and a different question. Note that
        # uniform choice is not equally lucky in the two: T0 draws a direction
        # from 5, T1 a slot from 16 of which few are ever occupied, so random
        # entity addressing is WORSE than random directional addressing. T1
        # buys expressiveness, not accuracy -- a learner has to earn the rest.
        self._addressing_mode = AddressingMode(addressing_mode)
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
        if self._addressing_mode is AddressingMode.T0_DIRECTIONAL:
            return Action.from_int(action_int)
        # v in Domain(s, O_t): only a target-bearing operation takes an entity.
        # MOVE and NOOP address space under every mode, or the arm measures a
        # paralysed organism instead of a differently-addressing one.
        operation = ActionType(action_int // NUM_DIRECTIONS)
        if operation not in TARGET_BEARING_OPERATIONS:
            return Action.from_int(action_int)
        slot = int(torch.randint(0, MAX_TARGET_SLOTS, (1,), generator=self._generator).item())
        return Action(
            action_type=operation,
            direction=Direction.NONE,
            selector_type=int(SelectorType.TARGET_ID),
            selector_value=slot,
        )

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

    def export_causal_state(self) -> dict[str, Any]:
        """All A0 state that can affect a future decision, explicitly encoded."""
        return {"schema_version": "terrario.agent-a0-causal/v1", "step": self._step,
                "generator_state": base64.b64encode(self._generator.get_state().numpy().tobytes()).decode("ascii")}

    def restore_causal_state(self, payload: dict[str, Any]) -> None:
        if payload.get("schema_version") != "terrario.agent-a0-causal/v1":
            raise ValueError("SCHEMA_MISMATCH: A0")
        encoded = payload.get("generator_state")
        if not isinstance(encoded, str) or not isinstance(payload.get("step"), int):
            raise ValueError("SNAPSHOT_INCOMPLETE: A0")
        raw = base64.b64decode(encoded.encode("ascii"), validate=True)
        self._generator.set_state(torch.frombuffer(bytearray(raw), dtype=torch.uint8).clone())
        self._step = payload["step"]
        self._trace.clear()
