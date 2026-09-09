"""Isolated UI control state, never connected to campaign mutation APIs."""

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class SandboxSession:
    session_id: str; step: int = 0; playing: bool = False; speed: float = 1.0; locked_campaign: bool = False

    def _guard(self):
        if self.locked_campaign: raise PermissionError("locked campaigns are READ_ONLY")
    def play(self): self._guard(); return replace(self, playing=True)
    def pause(self): self._guard(); return replace(self, playing=False)
    def single_step(self): self._guard(); return replace(self, step=self.step + 1, playing=False)
    def reset(self): self._guard(); return replace(self, step=0, playing=False)
    def set_speed(self, speed: float):
        self._guard()
        if not 0.1 <= speed <= 16: raise ValueError("speed must be between 0.1 and 16")
        return replace(self, speed=speed)
    def edit_config(self, **changes): self._guard(); return dict(changes)
