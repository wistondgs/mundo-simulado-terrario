"""Regression tests for SCIENTIFIC-LIVE-OBSERVABILITY-01."""
from pathlib import Path

import pytest

from terrario.lab.api import LabAPI
from terrario.lab.execution.live import (ContractMismatch, CursorInvalid, CursorTooOld, CursorWrongAttempt,
    LiveAttemptNotFound, ScientificLivePublisher, SubscriberLimit)
from terrario.lab.execution.observation import TraceCorrupted
from tests.test_preregistration_core import locked_flow
from tests.test_scientific_execution_gate import _execution


@pytest.fixture
def api(tmp_path):
    value = LabAPI(Path("."), data_root=tmp_path / ".terrario")
    locked_flow(value)
    return value


def _running(api):
    execution, _ = _execution(api)
    api.dispatch("POST", f"/api/v1/scientific-executions/{execution['execution_id']}/commands",
                 {"command": "START", "command_id": "live-start", "expected_revision": execution["revision"]})
    return execution


def _completed(api):
    execution = _running(api)
    api.scientific_execution_dispatcher.run(execution["execution_id"], max_trials=1)
    attempt = api.scientific_observations.attempts(execution["execution_id"])[0]
    return execution, attempt


def _live(api, execution, attempt):
    return api.scientific_execution_dispatcher.live, execution["execution_id"], attempt["trial_intent_id"], attempt["attempt_id"]


def _cursor(execution_id, trial_id, attempt_id, sequence):
    return {"schema_version": "terrario.scientific-live/v1", "execution_id": execution_id,
            "trial_intent_id": trial_id, "attempt_id": attempt_id, "frame_sequence": sequence}


def test_publish_tick_zero_and_later_frames(api):
    execution, attempt = _completed(api)
    live, eid, tid, aid = _live(api, execution, attempt)
    page = live.frames_after(eid, tid, aid, _cursor(eid, tid, aid, -1))
    assert page["frames"][0]["tick"] == 0 and page["frames"][0]["frame_sequence"] == 0
    assert len(page["frames"]) > 1


def test_monotonic_frame_sequence(api):
    execution, attempt = _completed(api)
    live, eid, tid, aid = _live(api, execution, attempt)
    page = live.frames_after(eid, tid, aid, _cursor(eid, tid, aid, -1))
    sequences = [f["frame_sequence"] for f in page["frames"]]
    assert sequences == list(range(len(sequences)))
    synthetic = ScientificLivePublisher()
    identity = {"execution_id": "e", "trial_intent_id": "t", "attempt_id": "a", "plan_hash": "p"}
    synthetic.begin_attempt(identity)
    synthetic.publish({"identity": identity, "frame_sequence": 0, "tick": 0, "runtime_state": "RUNNING",
                       "world_truth": {}, "agent_observation": {}, "observer_view": {}})
    with pytest.raises(ContractMismatch):
        synthetic.publish({"identity": identity, "frame_sequence": 5, "tick": 5, "runtime_state": "RUNNING",
                           "world_truth": {}, "agent_observation": {}, "observer_view": {}})
    forged = dict(identity, plan_hash="other-plan")
    with pytest.raises(ContractMismatch):
        synthetic.publish({"identity": forged, "frame_sequence": 1, "tick": 1, "runtime_state": "RUNNING",
                           "world_truth": {}, "agent_observation": {}, "observer_view": {}})


def test_bounded_retention_discards_oldest_live_only():
    live = ScientificLivePublisher(retention=4)
    identity = {"execution_id": "e", "trial_intent_id": "t", "attempt_id": "a", "plan_hash": "p"}
    live.begin_attempt(identity)
    for sequence in range(10):
        live.publish({"identity": identity, "frame_sequence": sequence, "tick": sequence,
                      "runtime_state": "RUNNING", "world_truth": {}, "agent_observation": {}, "observer_view": {}})
    snapshot = live.snapshot("e", "t", "a")
    assert snapshot["earliest_retained_sequence"] == 6 and snapshot["latest_sequence"] == 9
    with pytest.raises(CursorTooOld):
        live.frames_after("e", "t", "a", _cursor("e", "t", "a", 4))


def test_bounded_subscriber_limit_enforced():
    live = ScientificLivePublisher(max_subscribers=2)
    identity = {"execution_id": "e", "trial_intent_id": "t", "attempt_id": "a", "plan_hash": "p"}
    live.begin_attempt(identity)
    live.acquire_subscriber("e", "t", "a"); live.acquire_subscriber("e", "t", "a")
    with pytest.raises(SubscriberLimit):
        live.acquire_subscriber("e", "t", "a")
    live.release_subscriber("e", "t", "a"); live.release_subscriber("e", "t", "a")
    live.acquire_subscriber("e", "t", "a")


def test_snapshot_running_attempt(api):
    execution = _running(api)
    live = api.scientific_execution_dispatcher.live
    identity = {"execution_id": execution["execution_id"], "trial_intent_id": "t-live", "attempt_id": "a-live",
                "plan_hash": execution["plan_hash"]}
    live.begin_attempt(identity)
    live.publish({"identity": identity, "frame_sequence": 0, "tick": 0, "runtime_state": "RUNNING",
                  "world_truth": {"time": 0}, "agent_observation": {}, "observer_view": {}})
    snapshot = live.snapshot(execution["execution_id"], "t-live", "a-live")
    assert snapshot["frame"]["tick"] == 0 and snapshot["terminal"] is False
    assert snapshot["artifact_state"] == "LIVE_UNSEALED"
    assert snapshot["earliest_retained_sequence"] == 0 and snapshot["latest_sequence"] == 0


def test_sse_stream_route_returns_live_page(api):
    execution, attempt = _completed(api)
    status, response = api.dispatch("GET", f"/api/v1/scientific-executions/{execution['execution_id']}/trials/{attempt['trial_intent_id']}/live/stream?attempt_id={attempt['attempt_id']}&after_sequence=-1")
    assert status == 200
    page = response["data"]
    assert page["mode"] == "LIVE" and page["frames"][0]["tick"] == 0
    assert page["terminal"] is True and page["terminal_state"]["artifact_state"] == "CAS_SEALED"


def test_reconnect_within_retention_no_duplication(api):
    execution, attempt = _completed(api)
    live, eid, tid, aid = _live(api, execution, attempt)
    first = live.frames_after(eid, tid, aid, _cursor(eid, tid, aid, -1))
    n = int(first["frames"][1]["frame_sequence"])
    # Reconnect from n: delivery resumes exactly at n+1, contiguous, no silent jump.
    resumed = live.frames_after(eid, tid, aid, _cursor(eid, tid, aid, n))
    tail = [int(f["frame_sequence"]) for f in resumed["frames"]]
    assert tail == list(range(n + 1, n + 1 + len(tail)))
    assert tail[-1] == int(first["frames"][-1]["frame_sequence"])


def test_stale_cursor_resync_required_via_api(api):
    execution, attempt = _completed(api)
    live, eid, tid, aid = _live(api, execution, attempt)
    live.retention = 2
    attempt_obj = live._attempt(eid, tid, aid)
    with attempt_obj.lock:
        while len(attempt_obj.ring) > 2: attempt_obj.ring.popleft()
        attempt_obj.earliest_sequence = int(attempt_obj.ring[0]["frame_sequence"])
    status, response = api.dispatch("GET", f"/api/v1/scientific-executions/{eid}/trials/{tid}/live/stream?attempt_id={aid}&after_sequence=0")
    assert status == 409 and response["error"]["code"] == "CURSOR_TOO_OLD"


def test_wrong_attempt_cursor_rejected(api):
    execution, attempt = _completed(api)
    live, eid, tid, aid = _live(api, execution, attempt)
    with pytest.raises(CursorWrongAttempt):
        live.frames_after(eid, tid, aid, _cursor(eid, tid, "other-attempt", 0))
    with pytest.raises(CursorInvalid):
        live.frames_after(eid, tid, aid, {"schema_version": "wrong", "frame_sequence": 0})


def test_terminal_event_after_sealing(api):
    execution, attempt = _completed(api)
    live, eid, tid, aid = _live(api, execution, attempt)
    snapshot = live.snapshot(eid, tid, aid)
    assert snapshot["terminal"] is True
    assert snapshot["terminal_state_payload"]["runtime_state"] == "COMPLETED"
    assert snapshot["terminal_state_payload"]["artifact_state"] == "CAS_SEALED"
    artifacts = api.scientific_executions.get(eid)["artifacts"]
    assert {a["artifact_type"] for a in artifacts} >= {"SCIENTIFIC_TRACE", "TRIAL_RESULT"}


def test_live_to_terminal_to_playback_provenance_continuity(api):
    execution, attempt = _completed(api)
    live, eid, tid, aid = _live(api, execution, attempt)
    live_page = live.frames_after(eid, tid, aid, _cursor(eid, tid, aid, -1))
    live.drop_attempt(eid, tid, aid)
    playback = api.scientific_observations.playback(eid, tid, aid)
    live_first, play_first = live_page["frames"][0], playback["frames"][0]
    for key in ("execution_id", "trial_intent_id", "attempt_id", "plan_hash", "preregistration_root_hash"):
        assert str(live_first["identity"][key]) == str(play_first["identity"][key])
    assert live_first["identity"]["plan_hash"] == execution["plan_hash"]
    assert live_first["frame_sequence"] == play_first["frame_sequence"] == 0
    assert live_first["tick"] == play_first["tick"] == 0
    assert live_first["cognitive_state"] == play_first["cognitive_state"]


def test_cognitive_state_stays_atomic_with_later_durable_frames(api):
    execution, attempt = _completed(api)
    live, eid, tid, aid = _live(api, execution, attempt)
    live_frames = live.frames_after(eid, tid, aid, _cursor(eid, tid, aid, -1))["frames"]
    api.scientific_execution_dispatcher.frames.clear()
    api.scientific_execution_dispatcher.live.drop_attempt(eid, tid, aid)
    durable = api.scientific_observations.playback(eid, tid, aid)["frames"]
    assert [(frame["frame_sequence"], frame["tick"], frame["cognitive_state"]) for frame in live_frames] == [
        (frame["frame_sequence"], frame["tick"], frame["cognitive_state"]) for frame in durable
    ]
    assert all(frame["cognitive_state"]["step"] != "NOT_APPLICABLE" for frame in durable)


def test_terminal_frame_keeps_its_atomic_cognitive_state_and_completed_contract(api):
    execution, attempt = _completed(api)
    frames = api.scientific_observations.playback(execution["execution_id"], attempt["trial_intent_id"], attempt["attempt_id"])["frames"]
    final = frames[-1]
    assert final["runtime_state"] == "COMPLETED"
    assert final["tick"] == final["world_truth"]["time"]
    assert final["cognitive_state"]["schema_version"] == "terrario.scientific-cognitive-transport/v1"


def test_publication_fault_fails_materialization_only_after_the_real_trial_runs(api, monkeypatch):
    execution = _running(api)
    dispatcher = api.scientific_execution_dispatcher
    published = []

    def fail_after_capture(frame):
        published.append(frame)
        raise RuntimeError("deterministic live publisher fault")

    monkeypatch.setattr(dispatcher.live, "publish", fail_after_capture)
    with pytest.raises(ValueError, match="OBSERVER_MATERIALIZATION_FAILED"):
        dispatcher.run(execution["execution_id"], max_trials=1)
    # The sink received a real initial ScientificFrame and then failed closed
    # only at materialization; it did not stop the controller trajectory.
    assert published and published[0]["frame_sequence"] == 0
    attempt = api.scientific_observations.attempts(execution["execution_id"])[0]
    assert attempt["projected_state"] == "MATERIALIZATION_FAILED"
    artifact_types = {artifact["artifact_type"] for artifact in api.scientific_executions.get(execution["execution_id"])["artifacts"]}
    assert "SCIENTIFIC_TRACE" not in artifact_types


def test_durable_playback_after_service_reconstruction(api):
    execution, attempt = _completed(api)
    eid, tid, aid = execution["execution_id"], attempt["trial_intent_id"], attempt["attempt_id"]
    api.scientific_execution_dispatcher.frames.clear()
    api.scientific_execution_dispatcher.live.drop_attempt(eid, tid, aid)
    from terrario.lab.execution.observation import ScientificObservationService
    rebuilt = ScientificObservationService(api.scientific_executions)
    page = rebuilt.playback(eid, tid, aid)
    assert page["mode"] == "PLAYBACK" and page["frames"][0]["tick"] == 0
    assert page["frames"][0]["identity"]["plan_hash"] == execution["plan_hash"]


def test_corrupt_trace_fails_closed(api, tmp_path):
    execution, attempt = _completed(api)
    eid, tid, aid = execution["execution_id"], attempt["trial_intent_id"], attempt["attempt_id"]
    api.scientific_execution_dispatcher.frames.clear()
    api.scientific_execution_dispatcher.live.drop_attempt(eid, tid, aid)
    with api.artifacts._connect() as con:
        row = con.execute("SELECT blob_hash FROM scientific_execution_artifacts WHERE execution_id=? AND attempt_id=? AND artifact_type='SCIENTIFIC_TRACE'", (eid, aid)).fetchone()
    target = api.artifacts.blobs.destination(row["blob_hash"])
    target.write_bytes(b'{"frames": [{"identity": {"attempt_id": "FORGED"}}]}')
    with pytest.raises(TraceCorrupted):
        api.scientific_observations.playback(eid, tid, aid)


def test_cross_trial_isolation(api):
    execution, attempt = _completed(api)
    live, eid, tid, aid = _live(api, execution, attempt)
    with pytest.raises(LiveAttemptNotFound):
        live.snapshot(eid, "other-trial", aid)
    with pytest.raises(LiveAttemptNotFound):
        live.snapshot("other-execution", tid, aid)
    status, response = api.dispatch("GET", f"/api/v1/scientific-executions/{eid}/trials/{tid}/live?attempt_id=forged-attempt")
    assert status == 404


def test_subscriber_cleanup_on_release(api):
    execution, attempt = _completed(api)
    live, eid, tid, aid = _live(api, execution, attempt)
    live.acquire_subscriber(eid, tid, aid)
    live.release_subscriber(eid, tid, aid)
    assert live._attempt(eid, tid, aid).subscribers == 0
    live.release_subscriber(eid, tid, aid)
    assert live._attempt(eid, tid, aid).subscribers == 0


def test_slow_subscriber_does_not_block_publication():
    live = ScientificLivePublisher(retention=8)
    identity = {"execution_id": "e", "trial_intent_id": "t", "attempt_id": "a", "plan_hash": "p"}
    live.begin_attempt(identity)
    live.acquire_subscriber("e", "t", "a")  # subscriber that never reads
    import time
    start = time.monotonic()
    for sequence in range(50):
        live.publish({"identity": identity, "frame_sequence": sequence, "tick": sequence,
                      "runtime_state": "RUNNING", "world_truth": {}, "agent_observation": {}, "observer_view": {}})
    assert time.monotonic() - start < 2.0
    assert live.snapshot("e", "t", "a")["latest_sequence"] == 49


def test_publish_after_terminal_rejected():
    live = ScientificLivePublisher()
    identity = {"execution_id": "e", "trial_intent_id": "t", "attempt_id": "a", "plan_hash": "p"}
    live.begin_attempt(identity)
    live.publish({"identity": identity, "frame_sequence": 0, "tick": 0, "runtime_state": "RUNNING",
                  "world_truth": {}, "agent_observation": {}, "observer_view": {}})
    live.end_attempt("e", "t", "a", "COMPLETED", "CAS_SEALED")
    from terrario.lab.execution.live import AttemptNotRunning
    with pytest.raises(AttemptNotRunning):
        live.publish({"identity": identity, "frame_sequence": 1, "tick": 1, "runtime_state": "RUNNING",
                      "world_truth": {}, "agent_observation": {}, "observer_view": {}})


def test_live_package_has_no_evidence_or_sandbox_imports():
    source = (Path("terrario/lab/execution/live.py").read_text()
              + Path("terrario/lab/execution/dispatcher.py").read_text())
    for forbidden in ("theory.store", "EvidenceRecord", "add_evidence(", "sandbox_runtime", "run_experiment_specs"):
        assert forbidden not in source
