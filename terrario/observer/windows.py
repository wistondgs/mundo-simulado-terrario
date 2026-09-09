"""Forensic capture windows centered on observer-known causal events."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ForensicWindowPolicy:
    change_step: int
    pre_steps: int = 100
    change_before: int = 25
    change_after: int = 125
    recovery_after: int = 400

    def label(self, step: int) -> str | None:
        if self.change_step - self.change_before <= step <= self.change_step + self.change_after:
            return "change"
        if self.change_step - self.pre_steps <= step < self.change_step:
            return "pre_change"
        if self.change_step + self.change_after < step <= self.change_step + self.recovery_after:
            return "recovery"
        return None

    def should_capture(self, step: int) -> bool:
        return self.label(step) is not None
