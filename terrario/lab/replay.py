"""Offline cursor over recorded timeline data."""

from __future__ import annotations

from dataclasses import dataclass, replace

from terrario.lab.models import NOT_APPLICABLE, RunTimeline, TimelinePoint


@dataclass(frozen=True)
class OfflineReplay:
    timeline: RunTimeline; position: int = 0

    @property
    def current(self) -> TimelinePoint | None:
        return self.timeline.points[self.position] if self.timeline.points else None

    def forward(self): return replace(self, position=min(self.position + 1, max(0, len(self.timeline.points) - 1)))
    def backward(self): return replace(self, position=max(0, self.position - 1))
    def reset(self): return replace(self, position=0)
    def jump(self, target: str):
        predicates = {
            "causal-change": lambda p: p.causal_change is True,
            "first-interaction": lambda p: p.action != NOT_APPLICABLE,
            "recovery": lambda p: p.causal_competence != NOT_APPLICABLE and p.causal_competence >= .9,
            "forensic-window": lambda p: p.checkpoint != NOT_APPLICABLE,
        }
        predicate = predicates[target]
        index = next((i for i, point in enumerate(self.timeline.points) if predicate(point)), self.position)
        return replace(self, position=index)
