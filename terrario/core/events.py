"""Event base classes for the Terrario event system."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Event:
    """Base event with automatic timestamp."""
    event_type: str = ""
    timestamp: float = field(default_factory=time.monotonic)
    data: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.event_type:
            self.event_type = self.__class__.__name__


@dataclass
class WorldEvent(Event):
    """Event originating from the world."""
    step: int = 0
    rules_version: int = 0


@dataclass
class AgentEvent(Event):
    """Event originating from the agent."""
    step: int = 0
    agent_id: int = 0


@dataclass
class RuleChangeEvent(WorldEvent):
    """Fired when the ChangeScheduler modifies rules."""
    old_version: int = 0
    new_version: int = 0
    reason: str = ""


@dataclass
class MemoryEvent(AgentEvent):
    """Fired on memory read/write operations."""
    operation: str = ""  # "read" or "write"
    query_norm: float = 0.0
    result_norm: float = 0.0
    memory_size: int = 0


@dataclass
class LearningEvent(AgentEvent):
    """Fired on each learning update."""
    loss_total: float = 0.0
    loss_components: dict[str, float] = field(default_factory=dict)
    grad_norms: dict[str, float] = field(default_factory=dict)
    param_norms: dict[str, float] = field(default_factory=dict)
    learning_rate: float = 0.0
