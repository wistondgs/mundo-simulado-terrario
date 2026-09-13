"""Durable, read-only scientific observation over sealed raw trace artifacts."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping

from terrario.lab.persistence import ArtifactNotFound

OBSERVATION_SCHEMA = "terrario.scientific-observation/v1"
MAX_PLAYBACK_PAGE = 256


class ScientificObservationError(RuntimeError): code = "SCIENTIFIC_OBSERVATION_ERROR"
class AttemptNotFound(ScientificObservationError): code = "ATTEMPT_NOT_FOUND"
class ResyncRequired(ScientificObservationError): code = "RESYNC_REQUIRED"
class TraceCorrupted(ScientificObservationError): code = "TRACE_CORRUPTED"

@dataclass(frozen=True)
class ScientificFrameCursor:
    execution_id: str; trial_intent_id: str; attempt_id: str; frame_sequence: int
    schema_version: str = OBSERVATION_SCHEMA

@dataclass(frozen=True)
class ScientificObservationSnapshot:
    cursor: ScientificFrameCursor; frame: Mapping[str, Any]; runtime_state: str; artifact_state: str
    schema_version: str = OBSERVATION_SCHEMA

@dataclass(frozen=True)
class ScientificPlaybackPage:
    cursor: ScientificFrameCursor; frames: tuple[Mapping[str, Any], ...]; next_sequence: int | None
    schema_version: str = OBSERVATION_SCHEMA


class ScientificObservationService:
    def __init__(self, execution_service, dispatcher=None): self.service, self.dispatcher = execution_service, dispatcher

    def attempts(self, execution_id: str):
        with self.service.artifacts._connect() as con:
            rows = con.execute("""SELECT attempts.*, intents.identity_json FROM run_attempts attempts JOIN trial_intents intents ON intents.trial_intent_id=attempts.trial_intent_id
                JOIN execution_jobs jobs ON jobs.trial_intent_id=intents.trial_intent_id JOIN execution_batches batches ON batches.batch_id=jobs.batch_id WHERE batches.idempotency_key=? ORDER BY attempts.started_at""", (execution_id,)).fetchall()
        return tuple({**dict(row), "identity": json.loads(row["identity_json"])} for row in rows)

    def snapshot(self, execution_id: str, trial_intent_id: str, attempt_id: str) -> Mapping[str, Any]:
        frames = self._frames(execution_id, trial_intent_id, attempt_id)
        if not frames: raise AttemptNotFound(attempt_id)
        frame = frames[-1]; return {"schema_version": OBSERVATION_SCHEMA, "cursor": self._cursor(execution_id, trial_intent_id, attempt_id, frame), "frame": frame, "runtime_state": frame["runtime_state"], "artifact_state": "CAS_SEALED"}

    def playback(self, execution_id: str, trial_intent_id: str, attempt_id: str, after: int = -1, limit: int = 128) -> Mapping[str, Any]:
        if not 1 <= limit <= MAX_PLAYBACK_PAGE: raise ValueError("playback page limit exceeded")
        all_frames = self._frames(execution_id, trial_intent_id, attempt_id)
        frames = [x for x in all_frames if int(x["frame_sequence"]) > int(after)][:limit]
        next_sequence = frames[-1]["frame_sequence"] if len(frames) == limit else None
        cursor = self._cursor(execution_id, trial_intent_id, attempt_id, frames[-1] if frames else {"frame_sequence": after})
        return {"schema_version": OBSERVATION_SCHEMA, "cursor": cursor, "frames": frames, "next_sequence": next_sequence, "mode": "PLAYBACK"}

    def _frames(self, execution_id, trial_intent_id, attempt_id):
        # A live in-memory view is only an accelerator; terminal truth is CAS.
        if self.dispatcher:
            live = self.dispatcher.frames_after(execution_id, trial_intent_id)
            if live and live[0]["identity"]["attempt_id"] == attempt_id: return list(live)
        with self.service.artifacts._connect() as con:
            row = con.execute("SELECT blob_hash FROM scientific_execution_artifacts WHERE execution_id=? AND trial_intent_id=? AND attempt_id=? AND artifact_type='SCIENTIFIC_TRACE' ORDER BY created_at DESC LIMIT 1", (execution_id, trial_intent_id, attempt_id)).fetchone()
        if row is None: raise AttemptNotFound(attempt_id)
        try: payload = json.loads(self.service.artifacts.blobs.read(row["blob_hash"]))
        except Exception as exc: raise TraceCorrupted(str(exc)) from exc
        frames = payload.get("frames")
        if not isinstance(frames, list) or any(x.get("identity", {}).get("attempt_id") != attempt_id for x in frames): raise TraceCorrupted("trace identity mismatch")
        return frames

    @staticmethod
    def _cursor(execution_id, trial_id, attempt_id, frame):
        return {"execution_id": execution_id, "trial_intent_id": trial_id, "attempt_id": attempt_id, "frame_sequence": int(frame["frame_sequence"]), "schema_version": OBSERVATION_SCHEMA}
