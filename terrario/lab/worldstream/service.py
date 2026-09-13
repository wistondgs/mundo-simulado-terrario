"""Single-authority live session service layered on the bounded sandbox runtime."""
from __future__ import annotations

import hashlib
import json
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from terrario.lab.metrics_observer import ObserverRegistry
from terrario.lab.models import thaw
from terrario.lab.sandbox_runtime import RunState, SandboxService, SandboxValidationError
from terrario.observer.trace import TransitionTrace
from terrario.core.types import ActionType

from .contracts import (
    FrameOrigin, LiveSandboxSession, SessionCommand, SessionState, SessionStatus,
    StreamEnvelope, ViewFrame, ViewKind, WorldFrame,
)
from .trace import TraceArchive

MAX_ACTIVE_SESSIONS = 4
MAX_SUBSCRIBERS = 6
MAX_FRAME_BYTES = 16 * 1024 * 1024
MAX_TRACE_BYTES = 2 * 1024 * 1024 * 1024
SERVER_RING_SIZE = 2048


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _observation_payload(observation) -> dict[str, Any]:
    return {
        "channels": observation.channels.tolist(), "mask": observation.mask.tolist(),
        "agent_energy": observation.agent_energy, "time_fraction": observation.time_fraction,
    }


def _provenance_sidecar(world, agent_id: int, radius: int) -> dict[str, Any]:
    """Observer-only cell-to-object mapping; never supplied to the agent."""
    state = world._mutable_state()
    agent = state.agents[agent_id]
    cells: dict[str, list[int]] = {}
    for obj in state.objects.values():
        dx, dy = obj.pos.x - agent.pos.x, obj.pos.y - agent.pos.y
        if abs(dx) <= radius and abs(dy) <= radius:
            cells[f"{dx + radius},{dy + radius}"] = sorted([*cells.get(f"{dx + radius},{dy + radius}", []), obj.object_id])
    return {"classification": "OBSERVER_ONLY_FORENSIC", "mapping_kind": "EXPLICIT_VISIBILITY_PROVENANCE", "cell_object_ids": cells}


@dataclass
class _LiveContext:
    archive: TraceArchive
    lock: threading.RLock = field(default_factory=threading.RLock)
    changed: threading.Condition = field(init=False)
    ring: deque = field(default_factory=lambda: deque(maxlen=SERVER_RING_SIZE))
    revision: int = 0
    sequence: int = -1
    tick: int = 0
    last_frame_sequence: int = -1
    latest_frame: dict[str, Any] | None = None
    command_acks: dict[str, dict[str, Any]] = field(default_factory=dict)
    subscribers: int = 0
    worker: threading.Thread | None = None
    stop_requested: bool = False

    def __post_init__(self): self.changed = threading.Condition(self.lock)


class SessionConflict(SandboxValidationError):
    code = "SESSION_REVISION_CONFLICT"


class LiveSandboxService(SandboxService):
    """Adds versioned commands, a live ring, and v2 traces to SandboxService."""

    def __init__(self, storage_root: str | Path):
        super().__init__(storage_root)
        self.live_root = Path(storage_root) / "worldstream"
        self.live_root.mkdir(parents=True, exist_ok=True)
        self._live: dict[str, _LiveContext] = {}
        self._archives: dict[str, TraceArchive] = {}
        self._lost: dict[str, dict[str, Any]] = {}
        self.observers = ObserverRegistry()
        self._discover_lost_sessions()

    def _discover_lost_sessions(self):
        for path in self.storage.root.glob("sandbox-*.json"):
            try:
                payload = json.loads(path.read_text())
                if not payload.get("complete"):
                    self._lost[payload["sandbox_run_id"]] = payload
                trace_id = f"trace-{payload['sandbox_run_id'].removeprefix('sandbox-')}"
                trace_path = self.storage.root / "worldstream" / trace_id / "trace.v2.jsonl"
                if trace_path.exists():
                    archive = TraceArchive(self.storage.root / "worldstream", trace_id); archive.verify(); self._archives[trace_id] = archive
            except Exception:
                continue

    def create(self, spec, config, compiled):
        active = sum(run.state not in {RunState.COMPLETED, RunState.TERMINATED, RunState.FAILED} for run in self._runs.values())
        if active >= MAX_ACTIVE_SESSIONS:
            raise SandboxValidationError("active session limit reached")
        run = super().create(spec, config, compiled)
        trace_id = f"trace-{run.run_id.removeprefix('sandbox-')}"
        # Resolve from the compatibility storage root at creation time so test
        # harnesses and callers that relocate it keep every artifact isolated.
        ctx = _LiveContext(TraceArchive(self.storage.root / "worldstream", trace_id))
        self._live[run.run_id] = ctx
        self._archives[trace_id] = ctx.archive
        self._emit(run.run_id, "SESSION_OPEN", {"status": self._status_payload(run.run_id)})
        frame = self._capture_frame(run.run_id, FrameOrigin.INITIAL_SNAPSHOT)
        self._publish_frame(run.run_id, frame, snapshot=True)
        self._emit(run.run_id, "STATUS", self._status_payload(run.run_id))
        return run

    def _state(self, run_id: str) -> SessionState:
        state = self.get(run_id).state.value
        return SessionState(state if state in SessionState._value2member_map_ else ("READY" if state == "VALIDATED" else state))

    def _status_payload(self, run_id: str) -> dict[str, Any]:
        ctx = self._live[run_id]
        return thaw(SessionStatus(run_id, self._state(run_id), ctx.revision, ctx.tick, ctx.sequence, self.get(run_id).termination_reason))

    def describe(self, run_id: str) -> LiveSandboxSession:
        if run_id not in self._runs and run_id in self._lost:
            payload = self._lost[run_id]; spec = payload.get("spec", {}); trace_id = f"trace-{run_id.removeprefix('sandbox-')}"
            return LiveSandboxSession(run_id, str(spec.get("world_instance_hash", "NOT_AVAILABLE")), str(spec.get("scenario_id", "NOT_AVAILABLE")), int(spec.get("world_seed", 0)),
                {}, trace_id, SessionStatus(run_id, SessionState.SESSION_LOST, 0, len(payload.get("timeline", [])), -1, "PROCESS_RESTART_RUNTIME_NOT_RESTORABLE"))
        run, ctx, runtime = self.get(run_id), self._live[run_id], self._runtime[run_id]
        return LiveSandboxSession(run_id, run.spec.world_instance_hash, run.spec.scenario_id, run.spec.world_seed,
            dict(runtime["agent"].agent_identity), ctx.archive.trace_id,
            SessionStatus(run_id, self._state(run_id), ctx.revision, ctx.tick, ctx.sequence, run.termination_reason))

    def _capture_frame(self, run_id: str, origin: FrameOrigin) -> WorldFrame:
        run, ctx, runtime = self.get(run_id), self._live[run_id], self._runtime[run_id]
        world, scenario = runtime["world"], runtime["scenario"]
        radius, channels = scenario.get("view_radius", 2), scenario.get("num_channels", 4)
        observation = world.get_observation(0, radius, channels)
        agent_payload = _observation_payload(observation)
        truth = world.serialize()
        sidecar = _provenance_sidecar(world, 0, radius)
        profile_id = run.spec.trace_level if run.spec.trace_level in {p.profile_id for p in self.observers.profiles()} else "STANDARD"
        configured = set(self.observers.profile(profile_id).channels)
        captures = {
            "world": truth if "world" in configured else {"status": "MISSING"},
            "agent_energy": agent_payload["agent_energy"] if "agent_energy" in configured else "MISSING",
            "sensation": agent_payload if "sensation" in configured else "MISSING",
            "visibility_provenance": sidecar,
        }
        for channel in sorted(configured - set(captures)):
            captures[channel] = "MISSING"
        sim_time = float(truth["time"])
        views = (
            ViewFrame(ViewKind.WORLD_TRUTH_PRIVILEGED, ctx.tick, sim_time, "SYNCHRONIZED", truth, {"privileged": True}),
            ViewFrame(ViewKind.AGENT_OBSERVATION, ctx.tick, sim_time, "SYNCHRONIZED", agent_payload, {"identity_mapping": "NO DIRECT IDENTITY MAPPING"}),
            ViewFrame(ViewKind.OBSERVER_VIEW, ctx.tick, sim_time, "SYNCHRONIZED", captures, {"profile": profile_id, "observer_only": True}),
        )
        return WorldFrame(run_id, run.spec.world_instance_hash, run.spec.scenario_id, run.spec.world_seed,
            dict(runtime["agent"].agent_identity), ctx.tick, ctx.sequence + 1, sim_time, origin, ctx.archive.trace_id, views)

    def _emit(self, run_id: str, message_type: str, payload: dict[str, Any], tick: int | None = None) -> dict[str, Any]:
        ctx = self._live[run_id]
        with ctx.lock:
            ctx.sequence += 1
            envelope = thaw(StreamEnvelope(run_id, ctx.sequence, message_type, ctx.tick if tick is None else tick,
                payload, ctx.archive.trace_id, _now()))
            encoded = json.dumps(envelope, separators=(",", ":")).encode()
            if len(encoded) > MAX_FRAME_BYTES: raise SandboxValidationError("frame exceeds 16 MiB limit")
            if ctx.archive.trace_path.exists() and ctx.archive.trace_path.stat().st_size + len(encoded) > MAX_TRACE_BYTES:
                raise SandboxValidationError("trace exceeds 2 GiB limit")
            # Persist before visibility to subscribers.
            ctx.archive.append(sequence=ctx.sequence, tick=envelope["tick"], record_type=message_type, payload=envelope)
            ctx.ring.append(envelope); ctx.changed.notify_all()
            return envelope

    def _publish_frame(self, run_id: str, frame: WorldFrame, snapshot: bool = False):
        ctx = self._live[run_id]
        payload = thaw(frame)
        if snapshot:
            envelope = self._emit(run_id, "SNAPSHOT", {"frame": payload})
        else:
            envelope = self._emit(run_id, "DELTA", {"base_sequence": ctx.last_frame_sequence, "frame": payload, "operations": ({"op": "REPLACE_FRAME"},)})
        ctx.last_frame_sequence = envelope["sequence"]
        ctx.latest_frame = payload
        checkpoint_reason = "DELTA_EXCEEDS_50_PERCENT" if not snapshot else None
        if ctx.tick and ctx.tick % ctx.archive.checkpoint_interval == 0: checkpoint_reason = "INTERVAL"
        if self.get(run_id).state in {RunState.COMPLETED, RunState.TERMINATED}: checkpoint_reason = "TERMINAL"
        if checkpoint_reason: ctx.archive.checkpoint(ctx.tick, ctx.sequence, payload, checkpoint_reason)

    def step(self, run_id: str):
        return self._advance(run_id, continuous=False)

    def _advance(self, run_id: str, continuous: bool):
        ctx = self._live.get(run_id)
        if ctx is None: return super().step(run_id)
        with ctx.lock:
            run = self.get(run_id)
            runtime = self._runtime[run_id]
            scenario, world = runtime["scenario"], runtime["world"]
            before = _observation_payload(world.get_observation(0, scenario.get("view_radius", 2), scenario.get("num_channels", 4)))
            trace = super().step(run_id)
            if continuous and self.get(run_id).state == RunState.PAUSED and not ctx.stop_requested:
                super().resume(run_id)
            ctx.tick += 1
            after = _observation_payload(world.get_observation(0, scenario.get("view_radius", 2), scenario.get("num_channels", 4)))
            observer_trace = TransitionTrace(ctx.tick - 1,
                hashlib.sha256(json.dumps(before, sort_keys=True).encode()).hexdigest(),
                hashlib.sha256(json.dumps(after, sort_keys=True).encode()).hexdigest(),
                before, after, int(ActionType[trace.agent_action["action_type"]].value), trace.terminated,
                ctx.tick >= run.spec.step_limit, {"agent_events": list(trace.agent_events), "observer_events": list(trace.world_events)},
                dict(trace.agent_identity), {}, thaw(trace.observer_world), [], observer_annotations={"from_tick": ctx.tick - 1, "to_tick": ctx.tick},
                scientific_state=thaw(trace.scientific_state), sequence=ctx.sequence + 1,
                simulation_time=float(world.serialize()["time"]), frame_origin="TRANSITION_RESULT")
            transition_payload = {
                "transition": {**observer_trace.to_dict(), "from_tick": ctx.tick - 1, "to_tick": ctx.tick,
                    "action": thaw(trace.agent_action), "agent_events": list(trace.agent_events),
                    "world_events": list(trace.world_events)},
                "classification": "ENGINEERING_SANDBOX", "scientific_evidence": False,
            }
            self._emit(run_id, "EVENT", {"event": {"event_type": "ACTION", "source": "AgentInterface", "derived": False, **transition_payload}}, ctx.tick)
            for event in trace.world_events:
                self._emit(run_id, "EVENT", {"event": {"event_type": "OBSERVER", "source": "runtime", "derived": False, "value": event}}, ctx.tick)
            frame = self._capture_frame(run_id, FrameOrigin.TRANSITION_RESULT)
            self._publish_frame(run_id, frame)
            self._emit(run_id, "STATUS", self._status_payload(run_id), ctx.tick)
            if self.get(run_id).state in {RunState.COMPLETED, RunState.TERMINATED, RunState.FAILED}:
                self._emit(run_id, "SESSION_END", self._status_payload(run_id), ctx.tick)
            return trace

    def command(self, command: SessionCommand) -> dict[str, Any]:
        ctx = self._live[command.session_id]
        with ctx.lock:
            if command.command_id in ctx.command_acks:
                return ctx.command_acks[command.command_id]
            if command.expected_session_revision != ctx.revision:
                raise SessionConflict(f"expected revision {command.expected_session_revision}, current {ctx.revision}")
            if command.command == "STEP": self.step(command.session_id)
            elif command.command in {"START", "RESUME"}: self._start_worker(command.session_id)
            elif command.command == "PAUSE": self.pause(command.session_id)
            elif command.command == "STOP": self.stop(command.session_id)
            ctx.revision += 1
            ack = {"command_id": command.command_id, "accepted": True, "revision": ctx.revision,
                "status": self._status_payload(command.session_id)}
            ctx.command_acks[command.command_id] = ack
            self._emit(command.session_id, "COMMAND_ACK", ack)
            return ack

    def _start_worker(self, run_id: str):
        ctx, run = self._live[run_id], self.get(run_id)
        if run.state == RunState.PAUSED: super().resume(run_id)
        elif run.state == RunState.READY: run.transition(RunState.RUNNING); self.storage.write(run)
        elif run.state != RunState.RUNNING: raise SandboxValidationError(f"cannot start {run.state}")
        ctx.stop_requested = False
        if ctx.worker and ctx.worker.is_alive(): return
        def work():
            while not ctx.stop_requested and self.get(run_id).state == RunState.RUNNING:
                try:
                    self._advance(run_id, continuous=True)
                except Exception:
                    break
                time.sleep(0.03)
        ctx.worker = threading.Thread(target=work, name=f"worldstream-{run_id}", daemon=True); ctx.worker.start()

    def pause(self, run_id: str):
        ctx = self._live.get(run_id)
        if ctx: ctx.stop_requested = True
        run = super().pause(run_id)
        if ctx: self._emit(run_id, "STATUS", self._status_payload(run_id))
        return run

    def stop(self, run_id: str):
        ctx = self._live.get(run_id)
        if ctx: ctx.stop_requested = True
        run = super().stop(run_id)
        if ctx:
            self._emit(run_id, "STATUS", self._status_payload(run_id)); self._emit(run_id, "SESSION_END", self._status_payload(run_id))
            if ctx.latest_frame and ctx.last_frame_sequence >= 0:
                # A checkpoint names the authoritative frame it contains, not
                # the later STATUS/SESSION_END transport envelope.
                ctx.archive.checkpoint(ctx.tick, ctx.last_frame_sequence, ctx.latest_frame, "TERMINAL")
        return run

    def envelopes_after(self, run_id: str, after_sequence: int) -> list[dict[str, Any]]:
        ctx = self._live[run_id]
        with ctx.lock:
            if ctx.ring and after_sequence < ctx.ring[0]["sequence"] - 1:
                return [{"schema_version": "terrario.worldstream/v1", "session_id": run_id, "sequence": ctx.sequence,
                    "message_type": "GAP", "tick": ctx.tick, "trace_id": ctx.archive.trace_id, "emitted_at": _now(),
                    "payload": {"requested_after": after_sequence, "oldest_available": ctx.ring[0]["sequence"]}}]
            return [x for x in ctx.ring if x["sequence"] > after_sequence]

    def acquire_subscriber(self, run_id: str):
        ctx = self._live[run_id]
        with ctx.lock:
            if ctx.subscribers >= MAX_SUBSCRIBERS: raise SandboxValidationError("subscriber limit reached")
            ctx.subscribers += 1

    def release_subscriber(self, run_id: str):
        ctx = self._live.get(run_id)
        if ctx:
            with ctx.lock: ctx.subscribers = max(0, ctx.subscribers - 1)

    def archive(self, trace_id: str) -> TraceArchive | None:
        return self._archives.get(trace_id)

    def resync(self, run_id: str, reason: str) -> dict[str, Any]:
        ctx = self._live[run_id]
        with ctx.lock:
            frame = self._capture_frame(run_id, FrameOrigin.RESYNC_SNAPSHOT)
            envelope = self._emit(run_id, "RESYNC", {"reason": reason, "frame": thaw(frame)})
            ctx.last_frame_sequence = envelope["sequence"]; ctx.latest_frame = thaw(frame)
            return envelope

    def heartbeat(self, run_id: str) -> dict[str, Any]:
        return self._emit(run_id, "HEARTBEAT", {"revision": self._live[run_id].revision})
