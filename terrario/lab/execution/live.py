"""Bounded live observation plane for running scientific trials.

The publisher transports ScientificFrames already produced by the execution
runtime. It never modifies frames, never derives metrics, and never touches
agent, world, or execution state. Live frames are LIVE_UNSEALED: durability
and scientific evidence status come only from the sealed CAS trace, which
remains the authority for terminal playback.
"""
from __future__ import annotations

import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any, Mapping

LIVE_SCHEMA = "terrario.scientific-live/v1"

# Explicit live-observation configuration (bounded resources; no magic
# constants scattered through call sites).
LIVE_FRAME_RETENTION = 512
SUBSCRIBER_QUEUE_LIMIT = 256
MAX_SUBSCRIBERS_PER_ATTEMPT = 6
HEARTBEAT_INTERVAL_SECONDS = 5.0
MAX_LIVE_PAGE_SIZE = 256


class ScientificLiveError(RuntimeError): code = "SCIENTIFIC_LIVE_ERROR"
class LiveAttemptNotFound(ScientificLiveError): code = "ATTEMPT_NOT_FOUND"
class AttemptNotRunning(ScientificLiveError): code = "ATTEMPT_NOT_RUNNING"
class CursorInvalid(ScientificLiveError): code = "CURSOR_INVALID"
class CursorWrongAttempt(ScientificLiveError): code = "CURSOR_WRONG_ATTEMPT"
class CursorTooOld(ScientificLiveError): code = "CURSOR_TOO_OLD"
class LiveResyncRequired(ScientificLiveError): code = "RESYNC_REQUIRED"
class ContractMismatch(ScientificLiveError): code = "CONTRACT_MISMATCH"
class SubscriberLimit(ScientificLiveError): code = "SUBSCRIBER_LIMIT"


def validate_cursor(cursor: Mapping[str, Any]) -> Mapping[str, Any]:
    """A live cursor is attempt-bound and versioned; malformed input fails closed."""
    if not isinstance(cursor, Mapping): raise CursorInvalid("cursor must be an object")
    if cursor.get("schema_version") != LIVE_SCHEMA: raise CursorInvalid("cursor schema mismatch")
    for key in ("execution_id", "trial_intent_id", "attempt_id"):
        if not isinstance(cursor.get(key), str) or not cursor[key]: raise CursorInvalid(f"cursor missing {key}")
    if not isinstance(cursor.get("frame_sequence"), int) or cursor["frame_sequence"] < -1:
        raise CursorInvalid("cursor frame_sequence must be an integer >= -1")
    return cursor


@dataclass
class _LiveAttempt:
    execution_id: str
    trial_intent_id: str
    attempt_id: str
    identity: Mapping[str, Any]
    lock: threading.RLock = field(default_factory=threading.RLock)
    changed: threading.Condition = field(init=False)
    ring: deque = field(default_factory=lambda: deque(maxlen=LIVE_FRAME_RETENTION))
    latest_sequence: int = -1
    earliest_sequence: int = 0
    terminal: bool = False
    terminal_payload: Mapping[str, Any] | None = None
    subscribers: int = 0

    def __post_init__(self): self.changed = threading.Condition(self.lock)

    def cursor(self, frame_sequence: int) -> Mapping[str, Any]:
        return {"schema_version": LIVE_SCHEMA, "execution_id": self.execution_id,
                "trial_intent_id": self.trial_intent_id, "attempt_id": self.attempt_id,
                "frame_sequence": int(frame_sequence)}


class ScientificLivePublisher:
    """Attempt-scoped bounded live frame publication with subscriber tracking."""

    def __init__(self, retention: int = LIVE_FRAME_RETENTION, max_subscribers: int = MAX_SUBSCRIBERS_PER_ATTEMPT):
        self.retention, self.max_subscribers = retention, max_subscribers
        self._attempts: dict[str, _LiveAttempt] = {}
        self._lock = threading.RLock()

    def _key(self, execution_id: str, trial_intent_id: str, attempt_id: str) -> str:
        return f"{execution_id}:{trial_intent_id}:{attempt_id}"

    def begin_attempt(self, identity: Mapping[str, Any]) -> None:
        key = self._key(identity["execution_id"], identity["trial_intent_id"], identity["attempt_id"])
        with self._lock:
            self._attempts[key] = _LiveAttempt(identity["execution_id"], identity["trial_intent_id"],
                                               identity["attempt_id"], dict(identity), ring=deque(maxlen=self.retention))

    def publish(self, frame: Mapping[str, Any]) -> None:
        """Publish one atomic ScientificFrame; identity binding is verified, never inferred."""
        identity = frame.get("identity") if isinstance(frame, Mapping) else None
        identity = identity if isinstance(identity, Mapping) else getattr(frame, "identity", None)
        identity = identity if isinstance(identity, Mapping) else (identity.__dict__ if identity is not None else None)
        if not identity: raise ContractMismatch("live frame lacks scientific identity")
        key = self._key(identity["execution_id"], identity["trial_intent_id"], identity["attempt_id"])
        with self._lock: attempt = self._attempts.get(key)
        if attempt is None: raise LiveAttemptNotFound(key)
        payload = frame if isinstance(frame, Mapping) else frame.__dict__
        with attempt.lock:
            if attempt.terminal: raise AttemptNotRunning("attempt already terminal")
            sequence = int(payload["frame_sequence"])
            if sequence != attempt.latest_sequence + 1:
                raise ContractMismatch(f"non-monotonic frame_sequence {sequence} after {attempt.latest_sequence}")
            for field_name in ("execution_id", "trial_intent_id", "attempt_id", "plan_hash"):
                if str(identity.get(field_name)) != str(attempt.identity.get(field_name)):
                    raise ContractMismatch(f"frame identity mismatch on {field_name}")
            attempt.ring.append(dict(payload))
            attempt.latest_sequence = sequence
            attempt.earliest_sequence = int(attempt.ring[0]["frame_sequence"])
            attempt.changed.notify_all()

    def end_attempt(self, execution_id: str, trial_intent_id: str, attempt_id: str,
                    terminal_state: str, artifact_state: str) -> None:
        """Terminal event is emitted only after the caller sealed the required artifacts."""
        attempt = self._attempt(execution_id, trial_intent_id, attempt_id)
        with attempt.lock:
            if attempt.terminal: return
            attempt.terminal = True
            attempt.terminal_payload = {"runtime_state": terminal_state, "artifact_state": artifact_state,
                                        "frame_sequence": attempt.latest_sequence}
            attempt.changed.notify_all()

    def _attempt(self, execution_id: str, trial_intent_id: str, attempt_id: str) -> _LiveAttempt:
        with self._lock: attempt = self._attempts.get(self._key(execution_id, trial_intent_id, attempt_id))
        if attempt is None: raise LiveAttemptNotFound(attempt_id)
        return attempt

    def has_attempt(self, execution_id: str, trial_intent_id: str, attempt_id: str) -> bool:
        with self._lock: return self._key(execution_id, trial_intent_id, attempt_id) in self._attempts

    def _check_cursor(self, attempt: _LiveAttempt, cursor: Mapping[str, Any]) -> int:
        validate_cursor(cursor)
        for key, expected in (("execution_id", attempt.execution_id), ("trial_intent_id", attempt.trial_intent_id),
                              ("attempt_id", attempt.attempt_id)):
            if cursor[key] != expected: raise CursorWrongAttempt(f"cursor {key} does not match attempt")
        return int(cursor["frame_sequence"])

    def frames_after(self, execution_id: str, trial_intent_id: str, attempt_id: str,
                     cursor: Mapping[str, Any], limit: int = MAX_LIVE_PAGE_SIZE) -> Mapping[str, Any]:
        """Resume within retention; a cursor older than retention fails explicitly."""
        if not 1 <= limit <= MAX_LIVE_PAGE_SIZE: raise ValueError("live page limit exceeded")
        attempt = self._attempt(execution_id, trial_intent_id, attempt_id)
        with attempt.lock:
            after = self._check_cursor(attempt, cursor)
            if after < -1: raise CursorInvalid("frame_sequence below -1")
            if attempt.ring and after < attempt.earliest_sequence - 1:
                raise CursorTooOld(f"requested {after}, earliest retained {attempt.earliest_sequence}")
            frames = [x for x in attempt.ring if int(x["frame_sequence"]) > after][:limit]
            return {"schema_version": LIVE_SCHEMA, "mode": "LIVE",
                    "cursor": attempt.cursor(frames[-1]["frame_sequence"] if frames else after),
                    "frames": frames, "terminal": attempt.terminal,
                    "terminal_state": attempt.terminal_payload if attempt.terminal else None,
                    "earliest_retained_sequence": attempt.earliest_sequence,
                    "latest_sequence": attempt.latest_sequence}

    def snapshot(self, execution_id: str, trial_intent_id: str, attempt_id: str) -> Mapping[str, Any]:
        """Authoritative live attach point: latest frame plus retention/terminal state."""
        attempt = self._attempt(execution_id, trial_intent_id, attempt_id)
        with attempt.lock:
            if not attempt.ring: raise LiveAttemptNotFound("attempt has no live frames yet")
            frame = attempt.ring[-1]
            return {"schema_version": LIVE_SCHEMA, "mode": "LIVE_SNAPSHOT",
                    "cursor": attempt.cursor(frame["frame_sequence"]), "frame": frame,
                    "runtime_state": frame["runtime_state"],
                    "artifact_state": attempt.terminal_payload["artifact_state"] if attempt.terminal else "LIVE_UNSEALED",
                    "terminal": attempt.terminal,
                    "terminal_state_payload": attempt.terminal_payload,
                    "earliest_retained_sequence": attempt.earliest_sequence,
                    "latest_sequence": attempt.latest_sequence}

    def wait_for_frames(self, execution_id: str, trial_intent_id: str, attempt_id: str,
                        after: int, timeout: float = 1.0) -> bool:
        """Block a subscriber briefly until newer frames or terminal arrive."""
        attempt = self._attempt(execution_id, trial_intent_id, attempt_id)
        deadline = time.monotonic() + timeout
        with attempt.changed:
            while attempt.latest_sequence <= after and not attempt.terminal:
                remaining = deadline - time.monotonic()
                if remaining <= 0: return False
                attempt.changed.wait(timeout=remaining)
            return attempt.latest_sequence > after or attempt.terminal

    def acquire_subscriber(self, execution_id: str, trial_intent_id: str, attempt_id: str) -> None:
        attempt = self._attempt(execution_id, trial_intent_id, attempt_id)
        with attempt.lock:
            if attempt.subscribers >= self.max_subscribers: raise SubscriberLimit("scientific subscriber limit reached")
            attempt.subscribers += 1

    def release_subscriber(self, execution_id: str, trial_intent_id: str, attempt_id: str) -> None:
        try: attempt = self._attempt(execution_id, trial_intent_id, attempt_id)
        except LiveAttemptNotFound: return
        with attempt.lock: attempt.subscribers = max(0, attempt.subscribers - 1)

    def drop_attempt(self, execution_id: str, trial_intent_id: str, attempt_id: str) -> None:
        """Release bounded live memory; terminal truth remains the sealed CAS trace."""
        with self._lock: self._attempts.pop(self._key(execution_id, trial_intent_id, attempt_id), None)
