"""Immutable contracts for the live World2D protocol.

These records deliberately contain no scientific execution capability.  They
describe engineering-sandbox state and its transport only.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping

WORLDSTREAM_SCHEMA = "terrario.worldstream/v1"
TRACE_SCHEMA = "terrario.sandbox.trace/v2"


def _frozen(value: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return MappingProxyType(dict(value or {}))


class SessionState(StrEnum):
    CREATED = "CREATED"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    TERMINATED = "TERMINATED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    SESSION_LOST = "SESSION_LOST"


class ViewKind(StrEnum):
    WORLD_TRUTH_PRIVILEGED = "WORLD_TRUTH_PRIVILEGED"
    AGENT_OBSERVATION = "AGENT_OBSERVATION"
    OBSERVER_VIEW = "OBSERVER_VIEW"


class FrameOrigin(StrEnum):
    INITIAL_SNAPSHOT = "INITIAL_SNAPSHOT"
    TRANSITION_RESULT = "TRANSITION_RESULT"
    TRACE_CHECKPOINT = "TRACE_CHECKPOINT"
    RESYNC_SNAPSHOT = "RESYNC_SNAPSHOT"


@dataclass(frozen=True)
class ViewFrame:
    kind: ViewKind
    tick: int
    simulation_time: float
    status: str
    payload: Mapping[str, Any]
    provenance: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if self.tick < 0:
            raise ValueError("tick must be non-negative")
        if self.status not in {"SYNCHRONIZED", "STALE", "MISSING", "RESYNCING", "LOCAL_ERROR"}:
            raise ValueError("invalid view status")
        object.__setattr__(self, "payload", _frozen(self.payload))
        object.__setattr__(self, "provenance", _frozen(self.provenance))


@dataclass(frozen=True)
class WorldFrame:
    session_id: str
    world_instance_id: str
    scenario_id: str
    world_seed: int
    agent_identity: Mapping[str, Any]
    tick: int
    sequence: int
    simulation_time: float
    frame_origin: FrameOrigin
    trace_id: str
    views: tuple[ViewFrame, ...]
    schema_version: str = WORLDSTREAM_SCHEMA

    def __post_init__(self):
        if self.tick < 0 or self.sequence < 0:
            raise ValueError("tick and sequence must be non-negative")
        kinds = {view.kind for view in self.views}
        if kinds != set(ViewKind):
            raise ValueError("WorldFrame requires exactly the three epistemic views")
        if any(view.tick != self.tick for view in self.views):
            raise ValueError("WorldFrame views must be captured at one atomic tick")
        object.__setattr__(self, "agent_identity", _frozen(self.agent_identity))


@dataclass(frozen=True)
class FrameDelta:
    session_id: str
    base_sequence: int
    sequence: int
    tick: int
    operations: tuple[Mapping[str, Any], ...]
    schema_version: str = WORLDSTREAM_SCHEMA

    def __post_init__(self):
        if self.sequence <= self.base_sequence:
            raise ValueError("delta sequence must advance its base")
        object.__setattr__(self, "operations", tuple(_frozen(x) for x in self.operations))


@dataclass(frozen=True)
class TimelineEvent:
    session_id: str
    trace_id: str
    tick: int
    sequence: int
    event_type: str
    source: str
    payload: Mapping[str, Any]
    entity_id: str | None = None
    derived: bool = False
    schema_version: str = WORLDSTREAM_SCHEMA

    def __post_init__(self):
        object.__setattr__(self, "payload", _frozen(self.payload))


@dataclass(frozen=True)
class PlaybackCursor:
    trace_id: str
    tick: int
    sequence: int
    checkpoint_tick: int | None = None
    available_fields: tuple[str, ...] = ()
    schema_version: str = WORLDSTREAM_SCHEMA


@dataclass(frozen=True)
class TraceCheckpoint:
    trace_id: str
    tick: int
    sequence: int
    frame_hash: str
    path: str
    reason: str
    schema_version: str = TRACE_SCHEMA


@dataclass(frozen=True)
class SessionCommand:
    session_id: str
    command_id: str
    command: str
    expected_session_revision: int
    parameters: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = WORLDSTREAM_SCHEMA

    def __post_init__(self):
        if self.command not in {"START", "STEP", "PAUSE", "RESUME", "STOP"}:
            raise ValueError("unsupported session command")
        object.__setattr__(self, "parameters", _frozen(self.parameters))


@dataclass(frozen=True)
class SessionStatus:
    session_id: str
    state: SessionState
    revision: int
    tick: int
    sequence: int
    reason: str | None = None
    schema_version: str = WORLDSTREAM_SCHEMA


@dataclass(frozen=True)
class LiveSandboxSession:
    session_id: str
    world_instance_id: str
    scenario_id: str
    world_seed: int
    agent_identity: Mapping[str, Any]
    trace_id: str
    status: SessionStatus
    classification: str = "ENGINEERING_SANDBOX"
    scientific_evidence: bool = False
    schema_version: str = WORLDSTREAM_SCHEMA

    def __post_init__(self):
        if self.classification != "ENGINEERING_SANDBOX" or self.scientific_evidence:
            raise ValueError("live sessions cannot be scientific evidence")
        object.__setattr__(self, "agent_identity", _frozen(self.agent_identity))


@dataclass(frozen=True)
class StreamEnvelope:
    session_id: str
    sequence: int
    message_type: str
    tick: int
    payload: Mapping[str, Any]
    trace_id: str
    emitted_at: str
    schema_version: str = WORLDSTREAM_SCHEMA

    def __post_init__(self):
        allowed = {"SESSION_OPEN", "SNAPSHOT", "DELTA", "EVENT", "STATUS", "COMMAND_ACK", "HEARTBEAT", "GAP", "RESYNC", "SESSION_END"}
        if self.message_type not in allowed:
            raise ValueError("invalid stream message type")
        object.__setattr__(self, "payload", _frozen(self.payload))


@dataclass(frozen=True)
class ResyncRequest:
    session_id: str
    after_sequence: int
    last_frame_sequence: int
    reason: str
    schema_version: str = WORLDSTREAM_SCHEMA
