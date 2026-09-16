"""Durable scientific-execution orchestration with raw-artifact-only outputs."""
from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from terrario.lab.execution.domain import (
    AuthorizationScope, ExecutionAuthorization, ExecutionConflict, ExecutionEnvironmentSnapshot,
    ExecutionNotReady, ExecutionSoftwareSnapshot, ExecutionState, ExecutionUnauthorized,
    ExecutionVerificationReport, InvalidExecutionTransition, RawRunArtifact, ResourceCeiling,
    ScientificExecutionPlan, VerificationClass, assert_transition,
)
from terrario.lab.persistence import ArtifactNotFound, ArtifactRepository, ProvenanceConflict
from terrario.lab.persistence.canonical import canonical_json, content_hash, plain
from terrario.lab.preregistration.domain import PreregistrationState


class ScientificExecutionService:
    """The sole execution entry point.

    This service intentionally has no dependency on sandbox, EvidenceGraph,
    reference graph, theory, review, or legacy evidence-producing helpers.
    """

    def __init__(self, root: str | Path, artifacts: ArtifactRepository, preregistrations):
        self.root, self.artifacts, self.preregistrations = Path(root).resolve(), artifacts, preregistrations

    def request(self, preregistration_root_hash: str, actor_id: str) -> Mapping[str, Any]:
        preregistration_id = self._exact_locked_preregistration(preregistration_root_hash)
        execution_id, now = self._id("execution"), self.artifacts.now()
        with self.artifacts.transaction() as con:
            con.execute("""INSERT INTO scientific_executions(
                execution_id,preregistration_id,preregistration_root_hash,state,created_by,created_at)
                VALUES(?,?,?,?,?,?)""", (execution_id, preregistration_id, preregistration_root_hash,
                    ExecutionState.REQUESTED.value, actor_id, now))
            self._event(con, execution_id, "REQUESTED", {"preregistration_root_hash": preregistration_root_hash}, actor_id, now)
        return self.get(execution_id)

    def authorize(self, request: Mapping[str, Any], actor_id: str) -> Mapping[str, Any]:
        allowed = {"preregistration_root_hash", "scope_type", "max_execution_count", "resource_ceiling", "reason", "expires_at", "replication_group_id"}
        unknown = set(request) - allowed
        if unknown: raise ValueError(f"unknown authorization fields: {sorted(unknown)}")
        root = self._hex(request["preregistration_root_hash"], "preregistration_root_hash")
        self._exact_locked_preregistration(root)
        scope = AuthorizationScope(str(request["scope_type"]))
        count = int(request["max_execution_count"])
        if count < 1 or (scope is AuthorizationScope.ONE_EXECUTION and count != 1) or (scope is AuthorizationScope.N_EXECUTIONS and count < 2):
            raise ValueError("authorization scope and max_execution_count disagree")
        expiry = request.get("expires_at")
        group = request.get("replication_group_id")
        if scope is AuthorizationScope.UNTIL_EXPIRY and not expiry: raise ValueError("UNTIL_EXPIRY requires expires_at")
        if scope is AuthorizationScope.REPLICATION_SERIES and not group: raise ValueError("REPLICATION_SERIES requires replication_group_id")
        ceiling = ResourceCeiling.from_payload(request["resource_ceiling"])
        now, auth_id = self.artifacts.now(), self._id("authorization")
        auth = ExecutionAuthorization(auth_id, root, actor_id, scope, count, ceiling, now,
                                      str(request["reason"]), str(expiry) if expiry else None,
                                      str(group) if group else None)
        with self.artifacts.transaction() as con:
            con.execute("""INSERT INTO scientific_execution_authorizations(
                authorization_id,preregistration_root_hash,authorization_hash,actor_id,scope_type,max_execution_count,
                replication_group_id,expires_at,resource_ceiling_json,reason,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?)""", (auth_id, root, auth.authorization_hash, actor_id, scope.value,
                count, auth.replication_group_id, auth.expires_at, canonical_json(plain(ceiling)), auth.reason, now))
            con.execute("INSERT INTO scientific_execution_authorization_events(event_id,authorization_id,event_type,payload_json,actor_id,created_at) VALUES(?,?,?,?,?,?)",
                        (self._id("authorization-event"), auth_id, "CREATED", canonical_json({"authorization_hash": auth.authorization_hash}), actor_id, now))
        return self.authorization(auth_id)

    def bind_authorization(self, execution_id: str, authorization_id: str, expected_revision: int, actor_id: str) -> Mapping[str, Any]:
        with self.artifacts.transaction() as con:
            row = self._execution(con, execution_id)
            self._revision(row, expected_revision)
            if row["state"] != ExecutionState.REQUESTED.value: raise ExecutionConflict("authorization can only bind a REQUESTED execution")
            auth = self._authorization(con, authorization_id)
            if auth["preregistration_root_hash"] != row["preregistration_root_hash"]: raise ExecutionUnauthorized("authorization root differs")
            if self._revoked(con, authorization_id): raise ExecutionUnauthorized("authorization is revoked")
            assert_transition(row["state"], ExecutionState.VALIDATING)
            self._transition(con, row, ExecutionState.VALIDATING, "VALIDATING", {}, actor_id)
            self._readiness_or_raise(str(row["preregistration_root_hash"]))
            row = self._execution(con, execution_id)
            assert_transition(row["state"], ExecutionState.AUTHORIZED)
            self._transition(con, row, ExecutionState.AUTHORIZED, "AUTHORIZED", {"authorization_id": authorization_id}, actor_id,
                             authorization_id=authorization_id)
        return self.get(execution_id)

    def plan(self, execution_id: str, expected_revision: int, actor_id: str) -> Mapping[str, Any]:
        with self.artifacts.transaction() as con:
            row = self._execution(con, execution_id); self._revision(row, expected_revision)
            if row["state"] != ExecutionState.AUTHORIZED.value: raise ExecutionConflict("planning requires AUTHORIZED")
            readiness = self._readiness_or_raise(str(row["preregistration_root_hash"]))
            auth = self._authorization(con, str(row["authorization_id"]))
            environment, software = self._snapshots()
            record = self.artifacts.current(str(row["preregistration_id"]), "Preregistration")
            allow_dirty = bool(record.payload["draft"].get("environment_requirement", {}).get("allow_dirty_tree", False))
            self._validate_environment(auth, environment, software, allow_dirty)
            plan = self._build_plan(str(row["preregistration_id"]), str(row["preregistration_root_hash"]), environment, software)
            execution_root = content_hash({"schema_version": "terrario.lab.scientific-execution-root/v1",
                "execution_id": execution_id, "preregistration_root_hash": row["preregistration_root_hash"],
                "authorization_hash": auth["authorization_hash"], "plan_hash": plan.plan_hash,
                "environment_hash": environment.content_hash, "software_hash": software.content_hash})
            assert_transition(row["state"], ExecutionState.PLANNED)
            self._transition(con, row, ExecutionState.PLANNED, "PLAN_SEALED", {"plan_hash": plan.plan_hash, "execution_root_hash": execution_root}, actor_id,
                plan_hash=plan.plan_hash, execution_root_hash=execution_root, plan_json=canonical_json(plain(plan)),
                environment_snapshot_json=canonical_json(plain(environment)), software_snapshot_json=canonical_json(plain(software)),
                readiness_json=canonical_json(readiness))
            self._materialize_trials(con, execution_id, plan, self.artifacts.now())
            row = self._execution(con, execution_id)
            assert_transition(row["state"], ExecutionState.READY)
            self._transition(con, row, ExecutionState.READY, "READY", {"plan_hash": plan.plan_hash}, actor_id)
        return self.get(execution_id)

    def command(self, execution_id: str, command_id: str, expected_revision: int, command: str, actor_id: str) -> Mapping[str, Any]:
        command = str(command).upper()
        if command not in {"START", "PAUSE", "RESUME", "CANCEL"}: raise ValueError("unsupported execution command")
        with self.artifacts.transaction() as con:
            old = con.execute("SELECT response_json FROM scientific_execution_commands WHERE command_id=?", (command_id,)).fetchone()
            if old: return json.loads(old["response_json"])
            row = self._execution(con, execution_id); self._revision(row, expected_revision)
            state = ExecutionState(row["state"])
            if command == "START":
                if state is not ExecutionState.READY: raise ExecutionConflict("START requires READY")
                self._readiness_or_raise(str(row["preregistration_root_hash"]))
                self._consume_authorization(con, row, actor_id)
                target, event = ExecutionState.RUNNING, "STARTED"
                # Lease ownership is acquired in the same BEGIN IMMEDIATE
                # transaction that consumes the authorization.
                lease_updates = {"lease_owner": f"execution-worker:{execution_id}", "lease_expires_at": self._lease_expiry(60)}
            elif command == "PAUSE":
                if state is not ExecutionState.RUNNING: raise ExecutionConflict("PAUSE requires RUNNING")
                target, event, lease_updates = ExecutionState.PAUSING, "PAUSE_REQUESTED", {}
            elif command == "RESUME":
                if state is not ExecutionState.PAUSED: raise ExecutionConflict("RESUME requires PAUSED")
                target, event, lease_updates = ExecutionState.RUNNING, "RESUMED", {"lease_expires_at": self._lease_expiry(60)}
            else:
                if state not in {ExecutionState.REQUESTED, ExecutionState.VALIDATING, ExecutionState.AUTHORIZED, ExecutionState.PLANNED, ExecutionState.READY, ExecutionState.RUNNING, ExecutionState.PAUSED, ExecutionState.PAUSING}:
                    raise ExecutionConflict("CANCEL is unavailable in terminal state")
                target, event, lease_updates = (ExecutionState.STOPPING if state in {ExecutionState.RUNNING, ExecutionState.PAUSED, ExecutionState.PAUSING} else ExecutionState.CANCELLED), "CANCEL_REQUESTED", {}
            assert_transition(state.value, target)
            self._transition(con, row, target, event, {"command_id": command_id}, actor_id, **lease_updates)
            response = self._view(self._execution(con, execution_id), con)
            con.execute("INSERT INTO scientific_execution_commands(command_id,execution_id,command_type,expected_revision,response_json,created_at) VALUES(?,?,?,?,?,?)",
                        (command_id, execution_id, command, expected_revision, canonical_json(response), self.artifacts.now()))
        return response

    def certify_safe_boundary(self, execution_id: str, actor_id: str) -> Mapping[str, Any]:
        """Worker callback: PAUSING/STOPPING only settle after a safe boundary."""
        with self.artifacts.transaction() as con:
            row = self._execution(con, execution_id); state = ExecutionState(row["state"])
            if state is ExecutionState.PAUSING: self._transition(con, row, ExecutionState.PAUSED, "PAUSED_AT_SAFE_BOUNDARY", {}, actor_id)
            elif state is ExecutionState.STOPPING: self._transition(con, row, ExecutionState.CANCELLED, "CANCELLED_AT_SAFE_BOUNDARY", {}, actor_id, completed_at=self.artifacts.now(), lease_owner=None, lease_expires_at=None)
            else: raise ExecutionConflict("execution is not awaiting a safe boundary")
        return self.get(execution_id)

    def record_raw_artifact(self, execution_id: str, artifact_type: str, payload: bytes, actor_id: str,
                            trial_intent_id: str | None = None, attempt_id: str | None = None) -> Mapping[str, Any]:
        """Seal raw bytes in CAS; this method deliberately accepts no evidence fields."""
        blob = self.artifacts.register_blob(payload, "application/vnd.terrario.scientific-raw")
        descriptor = RawRunArtifact(str(artifact_type), blob.blob_hash, blob.size_bytes, trial_intent_id, attempt_id)
        with self.artifacts.transaction() as con:
            self._execution(con, execution_id)
            con.execute("""INSERT INTO scientific_execution_artifacts(artifact_id,execution_id,trial_intent_id,attempt_id,artifact_type,schema_version,blob_hash,size_bytes,descriptor_hash,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(execution_id,attempt_id,artifact_type,blob_hash) DO NOTHING""",
                (self._id("raw-artifact"), execution_id, trial_intent_id, attempt_id, descriptor.artifact_type, descriptor.schema_version,
                 blob.blob_hash, blob.size_bytes, descriptor.descriptor_hash, self.artifacts.now()))
            self._event(con, execution_id, "RAW_ARTIFACT_SEALED", plain(descriptor), actor_id, self.artifacts.now())
        return plain(descriptor)

    def complete(self, execution_id: str, actor_id: str) -> Mapping[str, Any]:
        with self.artifacts.transaction() as con:
            row = self._execution(con, execution_id)
            if row["state"] != ExecutionState.RUNNING.value: raise ExecutionConflict("completion requires RUNNING")
            self._readiness_or_raise(str(row["preregistration_root_hash"]))
            descriptors = self._artifacts(con, execution_id)
            root = content_hash({"schema_version": "terrario.lab.scientific-execution-artifact-root/v1", "artifacts": descriptors})
            self._transition(con, row, ExecutionState.COMPLETED, "COMPLETED", {"artifact_root_hash": root}, actor_id,
                             artifact_root_hash=root, completed_at=self.artifacts.now(), lease_owner=None, lease_expires_at=None)
        return self.get(execution_id)

    def fail(self, execution_id: str, failure: Mapping[str, Any], actor_id: str, abort: bool = False) -> Mapping[str, Any]:
        with self.artifacts.transaction() as con:
            row = self._execution(con, execution_id)
            state = ExecutionState.ABORTED if abort else ExecutionState.FAILED
            assert_transition(row["state"], state)
            self._transition(con, row, state, "ABORTED" if abort else "FAILED", {"failure": plain(failure)}, actor_id, completed_at=self.artifacts.now(), lease_owner=None, lease_expires_at=None)
        return self.get(execution_id)

    def deviation(self, execution_id: str, deviation_type: str, payload: Mapping[str, Any], actor_id: str) -> Mapping[str, Any]:
        if not deviation_type or set(payload) & {"evidence", "conclusion", "interpretation"}: raise ValueError("deviation must be operational, not evidentiary")
        now, deviation_id = self.artifacts.now(), self._id("execution-deviation")
        with self.artifacts.transaction() as con:
            self._execution(con, execution_id)
            con.execute("INSERT INTO scientific_execution_deviations(deviation_id,execution_id,deviation_type,payload_json,actor_id,created_at) VALUES(?,?,?,?,?,?)",
                        (deviation_id, execution_id, deviation_type, canonical_json(plain(payload)), actor_id, now))
            self._event(con, execution_id, "DEVIATION_RECORDED", {"deviation_id": deviation_id, "type": deviation_type}, actor_id, now)
        return {"deviation_id": deviation_id, "execution_id": execution_id, "deviation_type": deviation_type, "created_at": now}

    def verify(self, execution_id: str) -> Mapping[str, Any]:
        with self.artifacts.transaction() as con:
            row = self._execution(con, execution_id)
            events = [dict(x) for x in con.execute("SELECT * FROM scientific_execution_events WHERE execution_id=? ORDER BY sequence", (execution_id,))]
            chain_ok = self._verify_event_chain(events)
            artifacts = self._artifacts(con, execution_id)
            cas_ok = all(self.artifacts.blobs.verify(x["blob_hash"]) for x in artifacts)
            prereg_ok = self._readiness(str(row["preregistration_root_hash"]))["ready"]
            state = ExecutionState(row["state"])
            deviations = con.execute("SELECT COUNT(*) FROM scientific_execution_deviations WHERE execution_id=?", (execution_id,)).fetchone()[0]
            if state is ExecutionState.ABORTED: classification = VerificationClass.ABORTED
            elif state is not ExecutionState.COMPLETED: classification = VerificationClass.INCOMPLETE
            elif not (chain_ok and cas_ok and prereg_ok): classification = VerificationClass.FAIL
            elif deviations: classification = VerificationClass.DEVIATED
            else: classification = VerificationClass.PASS
            report = ExecutionVerificationReport(execution_id, classification,
                {"event_chain": chain_ok, "cas": cas_ok, "preregistration": prereg_ok, "execution_root": bool(row["execution_root_hash"]), "plan": bool(row["plan_hash"])},
                tuple(x for x, ok in (("EVENT_CHAIN_INVALID", chain_ok), ("CAS_INVALID", cas_ok), ("PREREGISTRATION_INVALID", prereg_ok)) if not ok))
            con.execute("INSERT INTO scientific_execution_verifications(verification_id,execution_id,report_hash,report_json,created_at) VALUES(?,?,?,?,?)",
                        (self._id("execution-verification"), execution_id, report.report_hash, canonical_json(plain(report)), self.artifacts.now()))
        return plain(report)

    def get(self, execution_id: str) -> Mapping[str, Any]:
        with self.artifacts._connect() as con: return self._view(self._execution(con, execution_id), con)

    def list(self) -> tuple[Mapping[str, Any], ...]:
        with self.artifacts._connect() as con:
            return tuple(self._view(row, con) for row in con.execute("SELECT * FROM scientific_executions ORDER BY created_at,execution_id"))

    def authorization(self, authorization_id: str) -> Mapping[str, Any]:
        with self.artifacts._connect() as con:
            row = self._authorization(con, authorization_id)
            return {**dict(row), "resource_ceiling": json.loads(row["resource_ceiling_json"]), "revoked": self._revoked(con, authorization_id)}

    def revoke(self, authorization_id: str, reason: str, actor_id: str) -> Mapping[str, Any]:
        with self.artifacts.transaction() as con:
            row = self._authorization(con, authorization_id)
            if self._revoked(con, authorization_id): raise ExecutionConflict("authorization already revoked")
            con.execute("INSERT INTO scientific_execution_authorization_events(event_id,authorization_id,event_type,payload_json,actor_id,created_at) VALUES(?,?,?,?,?,?)",
                        (self._id("authorization-event"), authorization_id, "REVOKED", canonical_json({"reason": reason}), actor_id, self.artifacts.now()))
            return {"authorization_id": authorization_id, "revoked": True, "authorization_hash": row["authorization_hash"]}

    def renew_lease(self, execution_id: str, owner: str) -> Mapping[str, Any]:
        """A worker may renew only its existing lease; ownership never changes."""
        with self.artifacts.transaction() as con:
            row = self._execution(con, execution_id)
            if row["lease_owner"] != owner or ExecutionState(row["state"]) not in {ExecutionState.RUNNING, ExecutionState.PAUSING}:
                raise ExecutionConflict("lease owner or state mismatch")
            con.execute("UPDATE scientific_executions SET lease_expires_at=? WHERE execution_id=?", (self._lease_expiry(60), execution_id))
            self._event(con, execution_id, "LEASE_RENEWED", {"owner": owner}, owner, self.artifacts.now())
        return self.get(execution_id)

    def recover_expired_leases(self, actor_id: str = "recovery") -> tuple[Mapping[str, Any], ...]:
        """Idempotently mark interrupted active runs; never silently replay work."""
        recovered = []
        with self.artifacts.transaction() as con:
            rows = con.execute("SELECT * FROM scientific_executions WHERE state IN ('RUNNING','PAUSING','STOPPING') AND lease_expires_at IS NOT NULL AND lease_expires_at < ?", (self.artifacts.now(),)).fetchall()
            for row in rows:
                target = ExecutionState.RECOVERY_REQUIRED if row["state"] in {"RUNNING", "PAUSING"} else ExecutionState.ABORTED
                self._transition(con, row, target, "LEASE_EXPIRED", {"previous_owner": row["lease_owner"]}, actor_id, lease_owner=None, lease_expires_at=None, **({"completed_at": self.artifacts.now()} if target is ExecutionState.ABORTED else {}))
                recovered.append(str(row["execution_id"]))
        return tuple(self.get(item) for item in recovered)

    def export_bundle(self, execution_id: str) -> Mapping[str, Any]:
        """Produce a portable ZIP without reclassifying raw data as evidence."""
        with self.artifacts._connect() as con:
            row = self._execution(con, execution_id)
            execution = self._view(row, con)
            authorization = self.authorization(str(row["authorization_id"])) if row["authorization_id"] else None
            preregistration = self.preregistrations.export(str(row["preregistration_id"]))
            blobs = {item["blob_hash"]: self.artifacts.blobs.read(item["blob_hash"]) for item in execution["artifacts"]}
        payload = {"schema_version": "terrario.scientific-execution-bundle/v1", "execution": execution,
                   "authorization": authorization, "preregistration": preregistration}
        manifest = {"schema_version": "terrario.scientific-execution-bundle-manifest/v1",
                    "payload_hash": content_hash(payload), "blobs": {digest: content_hash(bytes_.hex()) for digest, bytes_ in blobs.items()}}
        path = self.artifacts.data_root / "exports" / f"scientific-execution-{execution_id}.zip"
        with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("bundle.json", canonical_json(payload)); archive.writestr("manifest.json", canonical_json(manifest))
            for digest, bytes_ in blobs.items(): archive.writestr(f"blobs/{digest}", bytes_)
        return {"execution_id": execution_id, "archive_path": str(path), "manifest": manifest, "scientific_execution": True, "evidence_publication": False}

    def validate_bundle(self, archive_path: str | Path) -> Mapping[str, Any]:
        path = Path(archive_path).resolve()
        if not path.is_file(): raise ArtifactNotFound(str(path))
        failures = []
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
            if {"bundle.json", "manifest.json"} - names: failures.append("BUNDLE_MEMBERS_MISSING")
            for name in names:
                member = Path(name)
                if member.is_absolute() or ".." in member.parts: failures.append("UNSAFE_ARCHIVE_PATH")
            if not failures:
                bundle, manifest = json.loads(archive.read("bundle.json")), json.loads(archive.read("manifest.json"))
                if manifest.get("schema_version") != "terrario.scientific-execution-bundle-manifest/v1" or content_hash(bundle) != manifest.get("payload_hash"): failures.append("BUNDLE_HASH_INVALID")
                for digest, expected in manifest.get("blobs", {}).items():
                    name = f"blobs/{digest}"
                    if name not in names or content_hash(archive.read(name).hex()) != expected: failures.append(f"BLOB_INVALID:{digest}")
        return {"valid": not failures, "failures": tuple(failures), "schema_version": "terrario.scientific-execution-bundle/v1"}

    # ---- internal integrity -------------------------------------------------
    def _exact_locked_preregistration(self, root: str) -> str:
        root = self._hex(root, "preregistration_root_hash")
        with self.artifacts._connect() as con:
            row = con.execute("""SELECT versions.artifact_id,versions.version_id FROM artifact_versions versions
                JOIN preregistration_locks locks ON locks.preregistration_id=versions.artifact_id
                WHERE versions.kind='Preregistration' AND versions.scientific_hash=?
                  AND locks.bundle_version_id=versions.version_id AND locks.bundle_root_hash=?""", (root, root)).fetchone()
        if row is None: raise ExecutionNotReady("unknown or unlocked preregistration root")
        if self.artifacts.current_state(row["version_id"]) != PreregistrationState.PREREGISTERED_LOCKED.value:
            raise ExecutionNotReady("preregistration root is not currently PREREGISTERED_LOCKED")
        report = self.preregistrations.verify(str(row["artifact_id"]))
        if not report["valid"] or report["root"] != root: raise ExecutionNotReady("preregistration verification failed")
        return str(row["artifact_id"])

    def _readiness(self, root: str) -> Mapping[str, Any]:
        try:
            prereg_id = self._exact_locked_preregistration(root)
            current = self.artifacts.current(prereg_id, "Preregistration")
            draft = current.payload["draft"]
            matrix = self.artifacts.get_version(draft["protocol"]["trial_matrix_version_id"]).payload
            blockers: list[str] = []
            scenario = str(draft["protocol"]["scenario_id"])
            for cell in matrix.get("cells", ()):
                # A treatment arm binds its intervention in agent_config and runs on
                # the base scenario. TreatmentArm.variant ("preserved"/"ablated") is
                # descriptive metadata by the composer's own contract, never a world
                # variant awaiting binding; reading it as one blocked every paired
                # CL-7 protocol at bind-authorization, after all four human gates.
                if cell.get("arm_id") in {"PLANNER_PRESERVED", "PLANNER_ABLATED"} and cell.get("agent_config"):
                    continue
                if str(cell.get("variant_id", "")) not in {scenario, f"{scenario}-base"}: blockers.append("UNRESOLVED_VARIANT_BINDING")
            return {"ready": not blockers, "preregistration_id": prereg_id, "root": root, "blockers": sorted(set(blockers))}
        except Exception as exc:
            return {"ready": False, "root": root, "blockers": [getattr(exc, "code", "PREREGISTRATION_INVALID")]}

    def _readiness_or_raise(self, root: str) -> Mapping[str, Any]:
        report = self._readiness(root)
        if not report["ready"]: raise ExecutionNotReady("; ".join(report["blockers"]))
        return report

    def _build_plan(self, preregistration_id: str, root: str, environment, software) -> ScientificExecutionPlan:
        record = self.artifacts.current(preregistration_id, "Preregistration")
        draft = record.payload["draft"]
        matrix = self.artifacts.get_version(draft["protocol"]["trial_matrix_version_id"]).payload
        trials = tuple({
            **{k: cell[k] for k in ("trial_id", "variant_id", "condition_id", "agent_id", "world_seed", "agent_seed", "repetition", "metric_ids", "observer_profile")},
            # Historical generic matrices had no intervention configuration.
            # They are safe only as an explicit empty binding; operational
            # mappings receive an immutable nonempty config from the compiler.
            "agent_config": dict(cell.get("agent_config") or {}),
        } for cell in matrix["cells"])
        protocol = {key: draft["protocol"][key] for key in ("scenario_id", "scenario_hash", "world_definition_hash", "observation_interface_hash", "action_interface_hash", "intervention_schema_hash", "agent_ids", "agent_identity_hashes", "controls", "step_limit", "repetitions", "termination", "device_requirement") if key in draft["protocol"]}
        protocol.update({"randomization": draft["randomization"], "stopping": draft["stopping"], "failures": draft["failures"], "exclusions": draft["exclusions"], "observer": draft["observer"], "metrics": draft["metrics"]})
        return ScientificExecutionPlan(root, str(draft["protocol"]["trial_matrix_hash"]), len(trials), trials, protocol, environment.content_hash, software.content_hash)

    def _snapshots(self):
        status = self._git("status", "--porcelain")
        commit = self._git("rev-parse", "HEAD") or "UNKNOWN"
        env = ExecutionEnvironmentSnapshot({"os": platform.platform(), "kernel": platform.release(), "python": sys.version,
            "cpu_count": os.cpu_count(), "locale": os.environ.get("LC_ALL") or os.environ.get("LANG", "C"), "timezone": datetime.now().astimezone().tzname(), "determinism": {"pythonhashseed": os.environ.get("PYTHONHASHSEED", "UNSET")}})
        software = ExecutionSoftwareSnapshot({"commit": commit, "dirty": bool(status), "dirty_hash": content_hash(status) if status else None,
            "package_lock_hash": content_hash({p.name: p.read_text(errors="replace") for p in (self.root / "pyproject.toml", self.root / "package-lock.json", self.root / "requirements.txt") if p.exists()}),
            "schemas": {"execution": "v1", "preregistration": "v1", "trial_matrix": "v1"}})
        return env, software

    def _validate_environment(self, auth: Mapping[str, Any], environment, software, allow_dirty: bool = False) -> None:
        ceiling = json.loads(auth["resource_ceiling_json"])
        if software.values["dirty"] and not allow_dirty: raise ExecutionNotReady("DIRTY_WORKTREE_BLOCKED")
        if environment.values["cpu_count"] is not None and int(ceiling["cpu_cores"]) > int(environment.values["cpu_count"]): raise ExecutionNotReady("CPU_CEILING_UNAVAILABLE")
        if ceiling["gpu_devices"]: raise ExecutionNotReady("GPU_REQUIRED_UNAVAILABLE")

    def _materialize_trials(self, con, execution_id: str, plan: ScientificExecutionPlan, now: str) -> None:
        batch = self._id("execution-batch")
        con.execute("INSERT INTO execution_batches(batch_id,execution_plan_version_id,idempotency_key,created_at) VALUES(?,?,?,?)", (batch, plan.plan_hash, execution_id, now))
        for identity in plan.trial_identities:
            intent = self._id("trial-intent")
            con.execute("INSERT INTO trial_intents(trial_intent_id,execution_plan_version_id,identity_json,required_device,created_at) VALUES(?,?,?,?,?)", (intent, plan.plan_hash, canonical_json(identity), "cpu", now))
            con.execute("INSERT INTO execution_jobs(job_id,batch_id,trial_intent_id,idempotency_key,required_device,projected_state,created_at) VALUES(?,?,?,?,?,?,?)", (self._id("execution-job"), batch, intent, f"{execution_id}:{identity['trial_id']}", "cpu", "READY", now))

    def _consume_authorization(self, con, row, actor: str) -> None:
        if row["authorization_consumed"]: return
        auth = self._authorization(con, str(row["authorization_id"]))
        if self._revoked(con, auth["authorization_id"]): raise ExecutionUnauthorized("authorization revoked")
        if auth["expires_at"] and auth["expires_at"] <= self.artifacts.now(): raise ExecutionUnauthorized("authorization expired")
        changed = con.execute("UPDATE scientific_execution_authorizations SET consumed_execution_count=consumed_execution_count+1 WHERE authorization_id=? AND consumed_execution_count < max_execution_count", (auth["authorization_id"],)).rowcount
        if changed != 1: raise ExecutionUnauthorized("authorization quota exhausted")
        con.execute("UPDATE scientific_executions SET authorization_consumed=1 WHERE execution_id=?", (row["execution_id"],))
        con.execute("INSERT INTO scientific_execution_authorization_events(event_id,authorization_id,event_type,payload_json,actor_id,created_at) VALUES(?,?,?,?,?,?)", (self._id("authorization-event"), auth["authorization_id"], "CONSUMED", canonical_json({"execution_id": row["execution_id"]}), actor, self.artifacts.now()))

    def _transition(self, con, row, target, event_type, payload, actor, **updates):
        assert_transition(str(row["state"]), target)
        values = {"state": target.value, "revision": int(row["revision"]) + 1, **updates}
        assignments = ",".join(f"{key}=?" for key in values)
        con.execute(f"UPDATE scientific_executions SET {assignments} WHERE execution_id=?", (*values.values(), row["execution_id"]))
        self._event(con, str(row["execution_id"]), event_type, {"from": row["state"], "to": target.value, **plain(payload)}, actor, self.artifacts.now())

    def _event(self, con, execution_id, event_type, payload, actor, now):
        prev = con.execute("SELECT sequence,event_hash FROM scientific_execution_events WHERE execution_id=? ORDER BY sequence DESC LIMIT 1", (execution_id,)).fetchone()
        sequence, previous = (int(prev["sequence"]) + 1, str(prev["event_hash"])) if prev else (1, None)
        event_hash = content_hash({"execution_id": execution_id, "sequence": sequence, "event_type": event_type, "payload": plain(payload), "previous_event_hash": previous, "actor_id": actor, "created_at": now})
        con.execute("INSERT INTO scientific_execution_events(event_id,execution_id,sequence,event_type,payload_json,previous_event_hash,event_hash,actor_id,created_at) VALUES(?,?,?,?,?,?,?,?,?)", (self._id("execution-event"), execution_id, sequence, event_type, canonical_json(plain(payload)), previous, event_hash, actor, now))

    @staticmethod
    def _verify_event_chain(events):
        previous = None
        for expected, event in enumerate(events, 1):
            if event["sequence"] != expected or event["previous_event_hash"] != previous: return False
            actual = content_hash({"execution_id": event["execution_id"], "sequence": event["sequence"], "event_type": event["event_type"], "payload": json.loads(event["payload_json"]), "previous_event_hash": previous, "actor_id": event["actor_id"], "created_at": event["created_at"]})
            if actual != event["event_hash"]: return False
            previous = actual
        return bool(events)

    def _view(self, row, con):
        value = dict(row)
        for key in ("environment_snapshot_json", "software_snapshot_json", "readiness_json", "plan_json"):
            if value.get(key): value[key.removesuffix("_json")] = json.loads(value.pop(key))
            else: value.pop(key, None)
        value["artifacts"] = self._artifacts(con, str(row["execution_id"]))
        value["events"] = tuple({**dict(x), "payload": json.loads(x["payload_json"])} for x in con.execute("SELECT * FROM scientific_execution_events WHERE execution_id=? ORDER BY sequence", (row["execution_id"],)))
        value["scientific_execution"] = True; value["evidence_publication"] = False
        return value

    def _artifacts(self, con, execution_id):
        return tuple({k: v for k, v in dict(row).items() if k != "artifact_id"} for row in con.execute("SELECT * FROM scientific_execution_artifacts WHERE execution_id=? ORDER BY created_at,artifact_id", (execution_id,)))

    @staticmethod
    def _revision(row, expected):
        if int(row["revision"]) != int(expected): raise ExecutionConflict("stale expected_revision")

    @staticmethod
    def _hex(value, name):
        value = str(value)
        if len(value) != 64 or any(x not in "0123456789abcdef" for x in value): raise ValueError(f"{name} must be a SHA-256 hex digest")
        return value

    @staticmethod
    def _id(prefix): return f"{prefix}-{uuid.uuid4().hex}"
    @staticmethod
    def _lease_expiry(seconds):
        from datetime import timedelta
        return (datetime.now(timezone.utc) + timedelta(seconds=seconds)).isoformat().replace("+00:00", "Z")
    @staticmethod
    def _execution(con, execution_id):
        row = con.execute("SELECT * FROM scientific_executions WHERE execution_id=?", (execution_id,)).fetchone()
        if row is None: raise ArtifactNotFound(execution_id)
        return row
    @staticmethod
    def _authorization(con, authorization_id):
        row = con.execute("SELECT * FROM scientific_execution_authorizations WHERE authorization_id=?", (authorization_id,)).fetchone()
        if row is None: raise ArtifactNotFound(authorization_id)
        return row
    @staticmethod
    def _revoked(con, authorization_id):
        return con.execute("SELECT 1 FROM scientific_execution_authorization_events WHERE authorization_id=? AND event_type='REVOKED'", (authorization_id,)).fetchone() is not None
    def _git(self, *args):
        try: return subprocess.run(("git", *args), cwd=self.root, text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True, timeout=10).stdout.strip()
        except Exception: return ""
