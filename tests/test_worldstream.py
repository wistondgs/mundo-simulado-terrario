import json
from concurrent.futures import ThreadPoolExecutor

import pytest

from terrario.lab.sandbox_runtime import derive_sandbox, make_spec
from terrario.lab.world_authoring import compile_registry_world
from terrario.lab.world_registry import WorldScenarioRegistry, configuration_for
from terrario.lab.worldstream.contracts import SessionCommand
from terrario.lab.worldstream.service import LiveSandboxService, SessionConflict
from terrario.lab.worldstream.trace import TraceArchive, TraceIntegrityError
from terrario.lab.api import LabAPI


def live(tmp_path, steps=4):
    entry = WorldScenarioRegistry(".").get("D2")
    compiled = compile_registry_world("D2", entry.source)
    config = derive_sandbox(configuration_for(entry))
    spec = make_spec(config, compiled, 42, 1000045, steps)
    service = LiveSandboxService(tmp_path)
    run = service.create(spec, config, compiled)
    return service, run


def test_tick_zero_and_atomic_three_views(tmp_path):
    service, run = live(tmp_path)
    initial = service._live[run.run_id].latest_frame
    assert initial["tick"] == 0
    assert {x["kind"] for x in initial["views"]} == {
        "WORLD_TRUTH_PRIVILEGED", "AGENT_OBSERVATION", "OBSERVER_VIEW"}
    assert {x["tick"] for x in initial["views"]} == {0}
    agent = next(x for x in initial["views"] if x["kind"] == "AGENT_OBSERVATION")
    assert set(agent["payload"]) == {"channels", "mask", "agent_energy", "time_fraction"}
    assert agent["provenance"]["identity_mapping"] == "NO DIRECT IDENTITY MAPPING"


def test_transition_records_observation_t_and_t1_then_frame_t1(tmp_path):
    service, run = live(tmp_path)
    service.command(SessionCommand(run.run_id, "once", "STEP", 0))
    ctx = service._live[run.run_id]
    assert ctx.tick == 1 and ctx.latest_frame["tick"] == 1
    event = next(x for x in ctx.ring if x["message_type"] == "EVENT")
    transition = event["payload"]["event"]["transition"]
    assert transition["from_tick"] == 0 and transition["to_tick"] == 1
    assert set(transition["observation_t"]) == set(transition["observation_t1"])


def test_revision_conflict_and_idempotent_command(tmp_path):
    service, run = live(tmp_path)
    command = SessionCommand(run.run_id, "same", "STEP", 0)
    first = service.command(command); second = service.command(command)
    assert first == second and service._live[run.run_id].tick == 1
    with pytest.raises(SessionConflict):
        service.command(SessionCommand(run.run_id, "stale", "STEP", 0))


def test_observer_profile_does_not_change_agent_observation(tmp_path):
    left, a = live(tmp_path / "left")
    right, b = live(tmp_path / "right")
    right.get(b.run_id).spec = __import__("dataclasses").replace(right.get(b.run_id).spec, trace_level="FULL_DEBUG")
    left.step(a.run_id); right.step(b.run_id)
    la = next(x for x in left._live[a.run_id].latest_frame["views"] if x["kind"] == "AGENT_OBSERVATION")
    ra = next(x for x in right._live[b.run_id].latest_frame["views"] if x["kind"] == "AGENT_OBSERVATION")
    assert la["payload"] == ra["payload"]


def test_trace_hash_chain_index_seek_and_rebuild(tmp_path):
    archive = TraceArchive(tmp_path, "trace-test")
    archive.append(sequence=0, tick=0, record_type="SNAPSHOT", payload={"n": 0})
    archive.append(sequence=1, tick=1, record_type="EVENT", payload={"n": 1})
    assert archive.verify()["records"] == 2
    assert archive.seek(1)["sequence"] == 1
    archive.index_path.unlink(); archive.rebuild_index()
    assert archive.read(after_sequence=0)[0]["sequence"] == 1


def test_hash_chain_corruption_is_terminal_integrity_failure(tmp_path):
    archive = TraceArchive(tmp_path, "trace-test")
    archive.append(sequence=0, tick=0, record_type="SNAPSHOT", payload={"n": 0})
    row = json.loads(archive.trace_path.read_text()); row["payload"]["n"] = 9
    archive.trace_path.write_text(json.dumps(row) + "\n")
    with pytest.raises(TraceIntegrityError): archive.verify()


def test_ring_gap_is_explicit(tmp_path):
    service, run = live(tmp_path)
    ctx = service._live[run.run_id]
    ctx.ring = __import__("collections").deque(list(ctx.ring)[-1:], maxlen=1)
    assert service.envelopes_after(run.run_id, -1)[0]["message_type"] == "GAP"


def test_versioned_api_create_command_seek_and_legacy_adapter(tmp_path):
    api = LabAPI(".", data_root=tmp_path / "artifacts")
    api.sandbox.storage.root = tmp_path / "sandbox"
    headers = {"Host": "127.0.0.1:8765", "Origin": "http://127.0.0.1:8765",
        "X-CSRF-Token": api.api_v1.csrf_token}
    status, session = api.dispatch("POST", "/api/v1/world-stream/sessions",
        {"world_id": "D2", "step_limit": 2}, headers)
    assert status == 201 and session["schema_version"] == "terrario.worldstream/v1"
    sid = session["session_id"]
    status, ack = api.dispatch("POST", f"/api/v1/world-stream/sessions/{sid}/commands",
        {"command_id": "api-step", "command": "STEP", "expected_session_revision": 0}, headers)
    assert status == 200 and ack["revision"] == 1
    status, stream = api.dispatch("GET", f"/api/v1/world-stream/sessions/{sid}/stream?after_sequence=-1")
    assert status == 200 and any(x["message_type"] == "DELTA" for x in stream["stream"])
    assert api.dispatch("GET", f"/api/sandbox/{sid}/trace")[0] == 200


def test_restart_marks_non_restorable_session_lost_and_keeps_trace(tmp_path):
    service, run = live(tmp_path)
    service.step(run.run_id)
    trace_id = service.describe(run.run_id).trace_id
    restarted = LiveSandboxService(tmp_path)
    description = restarted.describe(run.run_id)
    assert description.status.state.value == "SESSION_LOST"
    assert restarted.archive(trace_id).verify()["valid"]


def test_subscriber_limit_is_enforced_and_released(tmp_path):
    service, run = live(tmp_path)
    for _ in range(6): service.acquire_subscriber(run.run_id)
    with pytest.raises(ValueError): service.acquire_subscriber(run.run_id)
    for _ in range(6): service.release_subscriber(run.run_id)
    assert service._live[run.run_id].subscribers == 0
