"""A campaign that survives a power cut must also be able to finish.

Long screening campaigns run for hours, so an interruption is expected rather
than exceptional. The ledger already protected the trials that had completed;
what it did not do was return the trial that was IN FLIGHT to the queue, so a
run could resume, work through everything else, and never reach "all
COMPLETED".
"""
from pathlib import Path

from terrario.lab.api import LabAPI
from tests.test_preregistration_core import locked_flow
from tests.test_scientific_execution_gate import _execution


def _started(tmp_path):
    api = LabAPI(Path("."), data_root=tmp_path / ".terrario")
    locked_flow(api)
    execution, _ = _execution(api)
    status, started = api.dispatch("POST", f"/api/v1/scientific-executions/{execution['execution_id']}/commands", {
        "command": "START", "command_id": "recovery-start", "expected_revision": execution["revision"]})
    assert status == 200
    return api, execution["execution_id"]


def _jobs(api, execution_id):
    with api.artifacts._connect() as con:
        return {str(r["job_id"]): str(r["projected_state"]) for r in con.execute(
            """SELECT jobs.job_id, jobs.projected_state FROM execution_jobs jobs
               JOIN execution_batches batches ON batches.batch_id=jobs.batch_id
               WHERE batches.idempotency_key=?""", (execution_id,))}


def _cut_the_power(api, execution_id):
    """Claim a trial and then vanish, the way a worker does when the lights go out."""
    claimed = api.scientific_execution_dispatcher._claim(execution_id, "worker-que-se-muere")
    assert claimed is not None
    with api.artifacts.transaction() as con:
        con.execute("UPDATE scientific_executions SET lease_expires_at=? WHERE execution_id=?",
                    ("2000-01-01T00:00:00.000000Z", execution_id))
    return claimed


def test_an_interrupted_trial_goes_back_to_the_queue(tmp_path):
    api, execution_id = _started(tmp_path)
    claimed = _cut_the_power(api, execution_id)
    assert _jobs(api, execution_id)[str(claimed["job_id"])] == "CLAIMED"

    api.scientific_executions.recover_expired_leases("recuperacion")

    # Back in the queue: without this the campaign can never close.
    assert _jobs(api, execution_id)[str(claimed["job_id"])] == "READY"


def test_the_abandoned_attempt_is_failed_rather_than_reused(tmp_path):
    # Never a silent replay: the interrupted attempt stays in the record as
    # failed, and the re-claim creates a new one beside it.
    api, execution_id = _started(tmp_path)
    claimed = _cut_the_power(api, execution_id)
    api.scientific_executions.recover_expired_leases("recuperacion")
    with api.artifacts._connect() as con:
        state = con.execute("SELECT projected_state FROM run_attempts WHERE attempt_id=?",
                            (claimed["attempt_id"],)).fetchone()[0]
    assert state == "FAILED"


def test_the_release_is_written_to_the_ledger(tmp_path):
    api, execution_id = _started(tmp_path)
    claimed = _cut_the_power(api, execution_id)
    api.scientific_executions.recover_expired_leases("recuperacion")
    with api.artifacts._connect() as con:
        kinds = [r[0] for r in con.execute(
            "SELECT event_type FROM scientific_execution_events WHERE execution_id=?", (execution_id,))]
    assert "TRIAL_RELEASED_AFTER_LEASE_LOSS" in kinds


def test_recovery_is_idempotent(tmp_path):
    # Recovery runs on restart, and a restart can happen twice in a row.
    api, execution_id = _started(tmp_path)
    _cut_the_power(api, execution_id)
    api.scientific_executions.recover_expired_leases("recuperacion")
    before = _jobs(api, execution_id)
    api.scientific_executions.recover_expired_leases("recuperacion")
    assert _jobs(api, execution_id) == before


def test_a_completed_trial_is_never_dragged_back_into_the_queue(tmp_path):
    # The whole point is that finished work survives. A recovery that re-queued
    # completed trials would turn a power cut into lost hours.
    api, execution_id = _started(tmp_path)
    api.scientific_execution_dispatcher.run(execution_id, max_trials=1)
    done = [job for job, state in _jobs(api, execution_id).items() if state == "COMPLETED"]
    assert done
    _cut_the_power(api, execution_id)
    api.scientific_executions.recover_expired_leases("recuperacion")
    after = _jobs(api, execution_id)
    assert all(after[job] == "COMPLETED" for job in done)
