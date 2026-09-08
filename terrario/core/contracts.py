"""Scientific boundary contracts shared by the experiment loop."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from terrario.core.types import Action, Consequence, Observation


@dataclass(frozen=True)
class Transition:
    """The complete agent-facing transition for one environment step.

    This is intentionally the only value passed to ``agent.learn`` by the
    controller. Convenience properties preserve the small agent API while
    keeping the full temporal relation auditable.
    """

    observation_t: Observation
    internal_state_ref: str | None
    action_t: Action
    consequence_t1: Consequence
    observation_t1: Observation
    terminated: bool
    truncated: bool
    step: int
    seed: int

    @property
    def energy_delta(self) -> float:
        return self.consequence_t1.energy_delta

    @property
    def events(self) -> list[str]:
        return self.consequence_t1.events

    @property
    def new_observation(self) -> Observation:
        return self.observation_t1

    @property
    def done(self) -> bool:
        return self.terminated or self.truncated


@dataclass(frozen=True)
class ImmutableObserverSnapshot:
    """A detached full-truth snapshot intended exclusively for observers."""

    step: int
    world_state_hash: str
    world: dict[str, Any]
