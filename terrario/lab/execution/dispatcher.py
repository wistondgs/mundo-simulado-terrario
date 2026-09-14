"""Idempotent scientific execution-plane dispatcher."""
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Mapping

from terrario.lab.execution.live import ScientificLivePublisher
from terrario.lab.execution.runtime import ScientificTrialIdentity, run_materialized_trial
from terrario.lab.persistence.canonical import canonical_json


class ScientificExecutionDispatcher:
    """Claims a reserved job once, materializes it, and seals only raw bytes."""
    def __init__(self, service, live: ScientificLivePublisher | None = None):
        self.service = service; self.frames: dict[str, list[dict[str, Any]]] = {}
        self.live = live if live is not None else ScientificLivePublisher()

    def run(self, execution_id: str, worker_id: str = "scientific-dispatcher", max_trials: int | None = None) -> Mapping[str, Any]:
        completed = 0
        while True:
            if max_trials is not None and completed >= max_trials: break
            claimed = self._claim(execution_id, worker_id)
            if claimed is None: break
            self._run_claimed(execution_id, claimed, worker_id)
            completed += 1
        return self.service.get(execution_id)

    def frames_after(self, execution_id: str, trial_intent_id: str, after: int = -1) -> tuple[Mapping[str, Any], ...]:
        return tuple(x for x in self.frames.get(f"{execution_id}:{trial_intent_id}", ()) if int(x["frame_sequence"]) > after)

    def _claim(self, execution_id, worker_id):
        with self.service.artifacts.transaction() as con:
            row = con.execute("""SELECT jobs.*, intents.identity_json FROM execution_jobs jobs
                JOIN execution_batches batches ON batches.batch_id=jobs.batch_id
                JOIN trial_intents intents ON intents.trial_intent_id=jobs.trial_intent_id
                WHERE batches.idempotency_key=? AND jobs.projected_state='READY' ORDER BY jobs.job_id LIMIT 1""", (execution_id,)).fetchone()
            if row is None: return None
            if con.execute("UPDATE execution_jobs SET projected_state='CLAIMED',lease_owner=? WHERE job_id=? AND projected_state='READY'", (worker_id, row["job_id"])).rowcount != 1: return None
            attempt_id = self.service._id("trial-attempt")
            con.execute("INSERT INTO run_attempts(attempt_id,trial_intent_id,ordinal,projected_state,worker_id,started_at) VALUES(?,?,?,?,?,?)", (attempt_id, row["trial_intent_id"], 1, "RUNNING", worker_id, self.service.artifacts.now()))
            self.service._event(con, execution_id, "TRIAL_CLAIMED", {"trial_intent_id": row["trial_intent_id"], "attempt_id": attempt_id, "job_id": row["job_id"]}, worker_id, self.service.artifacts.now())
            return {**dict(row), "attempt_id": attempt_id, "identity": json.loads(row["identity_json"])}

    def _run_claimed(self, execution_id, claim, worker_id):
        try:
            execution = self.service.get(execution_id); plan = execution["plan"]
            identity_row = claim["identity"]
            if execution["plan_hash"] != plan["plan_hash"] if "plan_hash" in plan else False: raise ValueError("INVALID_PLAN_HASH")
            scenario_id = str(plan["protocol"]["scenario_id"]).lower()
            scenario_path = self.service.root / "scenarios" / {"d0":"d0_differences.yaml","d1":"d1_objects.yaml","d2":"d2_properties.yaml","d3":"d3_causality.yaml","d4":"d4_change.yaml"}[scenario_id]
            identity = ScientificTrialIdentity(execution_id, claim["trial_intent_id"], claim["attempt_id"], execution["plan_hash"], execution["preregistration_root_hash"], execution["software_snapshot"]["content_hash"] if "content_hash" in execution["software_snapshot"] else execution["software_snapshot"].get("values", {}).get("commit", "UNKNOWN"), plan["protocol"]["scenario_hash"], str(identity_row["agent_id"]), int(identity_row["world_seed"]), int(identity_row["agent_seed"]))
            key = f"{execution_id}:{claim['trial_intent_id']}"; self.frames[key] = []
            self.live.begin_attempt(identity.__dict__)
            def sink(frame):
                payload = asdict(frame)
                self.frames[key].append(payload)
                self.live.publish(payload)
            result = run_materialized_trial(self.service.artifacts.data_root / "runtime" / execution_id / claim["attempt_id"], identity, scenario_path=scenario_path, observer_profile=str(identity_row["observer_profile"]), step_limit=int(plan["protocol"]["step_limit"]), frame_sink=sink)
            self.service.record_raw_artifact(execution_id, "SCIENTIFIC_TRACE", canonical_json({"identity": identity.__dict__, "frames": self.frames[key]}).encode(), worker_id, claim["trial_intent_id"], claim["attempt_id"])
            self.service.record_raw_artifact(execution_id, "TRIAL_RESULT", canonical_json(result).encode(), worker_id, claim["trial_intent_id"], claim["attempt_id"])
            with self.service.artifacts.transaction() as con:
                con.execute("UPDATE run_attempts SET projected_state='COMPLETED',finished_at=? WHERE attempt_id=?", (self.service.artifacts.now(), claim["attempt_id"]))
                con.execute("UPDATE execution_jobs SET projected_state='COMPLETED',lease_owner=NULL WHERE job_id=?", (claim["job_id"],))
                self.service._event(con, execution_id, "TRIAL_COMPLETED", {"trial_intent_id": claim["trial_intent_id"], "attempt_id": claim["attempt_id"]}, worker_id, self.service.artifacts.now())
            # Terminal is signaled only after the raw artifacts are sealed and the
            # attempt state is durable, so LIVE never claims terminality early.
            self.live.end_attempt(execution_id, claim["trial_intent_id"], claim["attempt_id"], "COMPLETED", "CAS_SEALED")
        except Exception as exc:
            with self.service.artifacts.transaction() as con:
                con.execute("UPDATE run_attempts SET projected_state='MATERIALIZATION_FAILED',finished_at=? WHERE attempt_id=?", (self.service.artifacts.now(), claim["attempt_id"]))
                con.execute("UPDATE execution_jobs SET projected_state='FAILED',lease_owner=NULL WHERE job_id=?", (claim["job_id"],))
                self.service._event(con, execution_id, "TRIAL_MATERIALIZATION_FAILED", {"trial_intent_id": claim["trial_intent_id"], "attempt_id": claim["attempt_id"], "reason": str(exc)}, worker_id, self.service.artifacts.now())
            if self.live.has_attempt(execution_id, claim["trial_intent_id"], claim["attempt_id"]):
                self.live.end_attempt(execution_id, claim["trial_intent_id"], claim["attempt_id"], "MATERIALIZATION_FAILED", "TRACE_UNAVAILABLE")
            raise
