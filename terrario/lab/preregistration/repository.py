"""Durable, append-only repository for preregistration governance."""
from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Any, Mapping

from terrario.lab.persistence import (
    ArtifactNotFound,
    ArtifactRepository,
    DuplicateArtifact,
    ProvenanceConflict,
)
from terrario.lab.persistence.canonical import canonical_json, content_hash, plain
from terrario.lab.preregistration.commitments import PreparedCommitment
from terrario.lab.preregistration.domain import (
    LockedPreregistration,
    PreregistrationAttestation,
    PreregistrationState,
    ReviewDecisionValue,
    StalePreregistration,
)


@dataclass(frozen=True)
class ReviewDecisionRecord:
    decision_id: str
    review_id: str
    artifact_version_id: str
    artifact_hash: str
    decision: str
    actor_id: str
    reason: str
    accepted_warning_hashes: tuple[str, ...]
    created_at: str


class PreregistrationRepository:
    def __init__(self, artifacts: ArtifactRepository):
        self.artifacts = artifacts

    def is_locked(self, preregistration_id: str) -> bool:
        with self.artifacts._connect() as connection:
            return connection.execute(
                "SELECT 1 FROM preregistration_locks WHERE preregistration_id=?", (preregistration_id,)
            ).fetchone() is not None

    def lock_row(self, preregistration_id: str) -> Mapping[str, Any] | None:
        with self.artifacts._connect() as connection:
            row = connection.execute(
                "SELECT * FROM preregistration_locks WHERE preregistration_id=?", (preregistration_id,)
            ).fetchone()
        return dict(row) if row else None

    def create_draft(self, preregistration_id: str, payload: Any, scientific_payload: Any,
                     actor_id: str, reason: str, parent_root_hash: str | None = None):
        record = self.artifacts.create_artifact(
            "Preregistration", payload, "terrario.lab.preregistration/v1",
            scientific_payload=scientific_payload, artifact_id=preregistration_id,
            classification="SCIENTIFIC_PREREGISTRATION_DRAFT", created_by=actor_id,
            reason=reason, initial_state=PreregistrationState.DRAFT.value,
        )
        self.append_chain(preregistration_id, "DRAFT_CREATED", {
            "version_id": record.version_id, "scientific_hash": record.scientific_hash,
            "parent_root_hash": parent_root_hash,
        }, actor_id)
        return record

    def derive_draft(self, preregistration_id: str, payload: Any, scientific_payload: Any,
                     expected_hash: str, actor_id: str, reason: str, delta: Any):
        if self.is_locked(preregistration_id):
            raise LockedPreregistration(preregistration_id)
        current = self.artifacts.current(preregistration_id, "Preregistration")
        if current.scientific_hash != expected_hash:
            raise StalePreregistration(expected_hash)
        record = self.artifacts.create_version(
            preregistration_id, payload, "terrario.lab.preregistration/v1",
            scientific_payload=scientific_payload, created_by=actor_id, reason=reason,
            delta=delta, parent_version_id=current.version_id,
            state=PreregistrationState.DRAFT.value,
            classification="SCIENTIFIC_PREREGISTRATION_DRAFT",
        )
        self.append_chain(preregistration_id, "DRAFT_DERIVED", {
            "version_id": record.version_id, "parent_version_id": current.version_id,
            "scientific_hash": record.scientific_hash, "delta": plain(delta),
        }, actor_id)
        return record

    def seal_candidate(
        self, preregistration_id: str, draft_payload: Any, prepared: PreparedCommitment,
        review_package: Mapping[str, Any], actor_id: str, reason: str,
    ):
        if self.is_locked(preregistration_id):
            raise LockedPreregistration(preregistration_id)
        package_bytes = canonical_json(review_package).encode("utf-8")
        package_blob = self.artifacts.register_blob(
            package_bytes, "application/vnd.terrario.preregistration-review+json",
        )
        package_hash = content_hash(review_package)
        now = self.artifacts.now()
        version_id = self.artifacts._identifier("version")
        package_id = self.artifacts._identifier("review-package")
        with self.artifacts.transaction() as connection:
            artifact = connection.execute(
                "SELECT kind FROM artifacts WHERE artifact_id=?", (preregistration_id,)
            ).fetchone()
            if artifact is None:
                raise ArtifactNotFound(preregistration_id)
            if connection.execute(
                "SELECT 1 FROM preregistration_locks WHERE preregistration_id=?", (preregistration_id,)
            ).fetchone():
                raise LockedPreregistration(preregistration_id)
            latest = connection.execute(
                "SELECT * FROM artifact_versions WHERE artifact_id=? ORDER BY version_number DESC LIMIT 1",
                (preregistration_id,),
            ).fetchone()
            duplicate = connection.execute(
                "SELECT version_id FROM artifact_versions WHERE kind='Preregistration' AND scientific_hash=?",
                (prepared.bundle_root_hash,),
            ).fetchone()
            if duplicate:
                raise DuplicateArtifact(f"Preregistration root already exists: {prepared.bundle_root_hash}")
            payload = {
                "draft": plain(draft_payload), "root_manifest": plain(prepared.root_manifest),
                "bundle_root_hash": prepared.bundle_root_hash,
                "components": plain(prepared.components), "review_package_hash": package_hash,
                "scientific_execution": False, "evidence_publication": False,
            }
            connection.execute(
                """INSERT INTO artifact_versions(
                    version_id,artifact_id,version_number,kind,schema_version,scientific_hash,
                    scientific_payload_json,payload_json,classification,parent_version_id,parent_hash,
                    delta_json,reason,created_at,created_by,sealed
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,1)""",
                (version_id, preregistration_id, int(latest["version_number"])+1, "Preregistration",
                 "terrario.lab.preregistration-bundle/v1", prepared.bundle_root_hash,
                 canonical_json(prepared.root_manifest), canonical_json(payload),
                 "SCIENTIFIC_PREREGISTRATION_CANDIDATE", latest["version_id"],
                 latest["scientific_hash"], canonical_json({"operation": "prepare_review"}),
                 reason, now, actor_id),
            )
            self.artifacts._insert_state_event(
                connection, version_id, 1, None, PreregistrationState.READY_FOR_REVIEW.value,
                actor_id, reason, now,
            )
            for descriptor in prepared.components:
                connection.execute(
                    """INSERT INTO preregistration_components(
                        component_id,bundle_version_id,role,ordinal,schema_version,content_hash,
                        cas_hash,source_artifact_version_id,source_scientific_hash,created_at
                    ) VALUES(?,?,?,?,?,?,?,?,?,?)""",
                    (self.artifacts._identifier("component"), version_id, descriptor.role,
                     descriptor.ordinal, descriptor.schema_version, descriptor.content_sha256,
                     descriptor.cas_sha256, descriptor.source_artifact_version_id,
                     descriptor.source_scientific_hash, now),
                )
            connection.execute(
                """INSERT INTO preregistration_review_packages(
                    review_package_id,bundle_version_id,package_hash,blob_hash,policy_snapshot_hash,created_at
                ) VALUES(?,?,?,?,?,?)""",
                (package_id, version_id, package_hash, package_blob.blob_hash,
                 str(review_package["readiness"]["policy_snapshot_hash"]), now),
            )
            event_hash = self._append_chain(connection, preregistration_id, "CANDIDATE_SEALED", {
                "version_id": version_id, "bundle_root_hash": prepared.bundle_root_hash,
                "review_package_hash": package_hash,
            }, actor_id, now)
            self.artifacts._insert_audit(
                connection, self.artifacts._identifier("correlation"), actor_id,
                "PREREGISTRATION_CANDIDATE_SEALED", "Preregistration", preregistration_id,
                {"version_id": version_id, "root": prepared.bundle_root_hash, "chain": event_hash}, now,
            )
        return self.artifacts.get_version(version_id)

    def create_review_request(self, version_id: str, review_kind: str, actor_id: str,
                              reason: str) -> Mapping[str, Any]:
        version = self.artifacts.get_version(version_id)
        now, review_id = self.artifacts.now(), self.artifacts._identifier("review")
        with self.artifacts.transaction() as connection:
            connection.execute(
                "INSERT INTO review_requests(review_id,artifact_version_id,review_kind,requested_by,reason,created_at) VALUES(?,?,?,?,?,?)",
                (review_id, version_id, review_kind, actor_id, reason, now),
            )
            if review_kind == "PREREGISTRATION":
                state = self._state_in_connection(connection, version_id)
                if state != PreregistrationState.READY_FOR_REVIEW.value:
                    raise ProvenanceConflict(f"review submission requires READY_FOR_REVIEW, got {state}")
                self.artifacts._insert_state_event(
                    connection, version_id, 2, state, PreregistrationState.REVIEW_IN_PROGRESS.value,
                    actor_id, reason, now,
                )
                self._append_chain(connection, version.artifact_id, "REVIEW_SUBMITTED", {
                    "review_id": review_id, "version_id": version_id, "root": version.scientific_hash,
                }, actor_id, now)
        return {"review_id": review_id, "artifact_version_id": version_id,
                "artifact_hash": version.scientific_hash, "review_kind": review_kind,
                "requested_by": actor_id, "reason": reason, "created_at": now}

    def record_review_decision(
        self, review_id: str, artifact_hash: str, decision: ReviewDecisionValue,
        actor_id: str, reason: str, accepted_findings: tuple[Mapping[str, str], ...] = (),
    ) -> ReviewDecisionRecord:
        now, decision_id = self.artifacts.now(), self.artifacts._identifier("decision")
        with self.artifacts.transaction() as connection:
            request = connection.execute("SELECT * FROM review_requests WHERE review_id=?", (review_id,)).fetchone()
            if request is None:
                raise ArtifactNotFound(review_id)
            version = connection.execute(
                "SELECT * FROM artifact_versions WHERE version_id=?", (request["artifact_version_id"],)
            ).fetchone()
            if version["scientific_hash"] != artifact_hash:
                raise StalePreregistration(artifact_hash)
            if request["review_kind"] == "PREREGISTRATION" and decision not in {
                ReviewDecisionValue.APPROVE_PREREGISTRATION,
                ReviewDecisionValue.REQUEST_CHANGES, ReviewDecisionValue.REJECT,
            }:
                raise ValueError("invalid preregistration review decision")
            if request["review_kind"] == "EXPERIMENT_DESIGN" and decision not in {
                ReviewDecisionValue.APPROVE_FOR_EXPERIMENT_DESIGN,
                ReviewDecisionValue.REQUEST_CHANGES, ReviewDecisionValue.REJECT,
            }:
                raise ValueError("invalid experiment design review decision")
            connection.execute(
                """INSERT INTO review_decisions(
                    decision_id,review_id,artifact_version_id,artifact_hash,decision,actor_id,reason,
                    supersedes_decision_id,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?)""",
                (decision_id, review_id, version["version_id"], artifact_hash,
                 decision.value, actor_id, reason, None, now),
            )
            for item in accepted_findings:
                connection.execute(
                    """INSERT INTO review_warning_acceptances(
                        acceptance_id,decision_id,finding_hash,rule_id,rule_version,created_at
                    ) VALUES(?,?,?,?,?,?)""",
                    (self.artifacts._identifier("warning-acceptance"), decision_id,
                     str(item["finding_hash"]), str(item["rule_id"]),
                     str(item["rule_version"]), now),
                )
            if request["review_kind"] == "PREREGISTRATION":
                state = self._state_in_connection(connection, version["version_id"])
                if state != PreregistrationState.REVIEW_IN_PROGRESS.value:
                    raise ProvenanceConflict(f"decision requires REVIEW_IN_PROGRESS, got {state}")
                sequence = self._next_state_sequence(connection, version["version_id"])
                self.artifacts._insert_state_event(
                    connection, version["version_id"], sequence, state,
                    PreregistrationState.REVIEWED.value, actor_id, reason, now, decision_id,
                )
                self._append_chain(connection, version["artifact_id"], "REVIEW_DECIDED", {
                    "decision_id": decision_id, "decision": decision.value,
                    "root": artifact_hash, "accepted_findings": plain(accepted_findings),
                }, actor_id, now)
        return ReviewDecisionRecord(decision_id, review_id, str(version["version_id"]),
                                    artifact_hash, decision.value, actor_id, reason,
                                    tuple(str(x["finding_hash"]) for x in accepted_findings), now)

    def approved_upstream(self, version_id: str) -> bool:
        with self.artifacts._connect() as connection:
            row = connection.execute(
                """SELECT 1 FROM review_decisions d JOIN review_requests r ON r.review_id=d.review_id
                WHERE d.artifact_version_id=? AND d.artifact_hash=(SELECT scientific_hash FROM artifact_versions WHERE version_id=?)
                AND r.review_kind='EXPERIMENT_DESIGN' AND d.decision='APPROVE_FOR_EXPERIMENT_DESIGN'
                ORDER BY d.created_at DESC LIMIT 1""", (version_id, version_id),
            ).fetchone()
        return row is not None

    def review_decision(self, decision_id: str) -> ReviewDecisionRecord:
        with self.artifacts._connect() as connection:
            row = connection.execute("SELECT * FROM review_decisions WHERE decision_id=?", (decision_id,)).fetchone()
            if row is None:
                raise ArtifactNotFound(decision_id)
            accepted = tuple(str(x[0]) for x in connection.execute(
                "SELECT finding_hash FROM review_warning_acceptances WHERE decision_id=? ORDER BY finding_hash",
                (decision_id,),
            ))
        return ReviewDecisionRecord(str(row["decision_id"]), str(row["review_id"]),
                                    str(row["artifact_version_id"]), str(row["artifact_hash"]),
                                    str(row["decision"]), str(row["actor_id"]), str(row["reason"]),
                                    accepted, str(row["created_at"]))

    def review_package(self, bundle_version_id: str) -> Mapping[str, Any]:
        with self.artifacts._connect() as connection:
            row = connection.execute(
                "SELECT * FROM preregistration_review_packages WHERE bundle_version_id=?",
                (bundle_version_id,),
            ).fetchone()
        if row is None:
            raise ArtifactNotFound(bundle_version_id)
        payload = json.loads(self.artifacts.blobs.read(str(row["blob_hash"])))
        return {**payload, "review_package_id": row["review_package_id"],
                "review_package_hash": row["package_hash"]}

    def lock(
        self, preregistration_id: str, bundle_version_id: str, expected_root: str,
        decision_id: str, actor_id: str, reason: str, current_warning_hashes: tuple[str, ...],
        idempotency_key: str | None,
    ) -> PreregistrationAttestation:
        request_hash = content_hash({
            "preregistration_id": preregistration_id, "bundle_version_id": bundle_version_id,
            "expected_root": expected_root, "decision_id": decision_id, "reason": reason,
            "warning_hashes": sorted(current_warning_hashes),
        })
        if idempotency_key:
            cached = self.command_result(idempotency_key, "LOCK", request_hash)
            if cached:
                return PreregistrationAttestation(**cached)
        now = self.artifacts.now()
        attestation_id = self.artifacts._identifier("attestation")
        with self.artifacts.transaction() as connection:
            version = connection.execute(
                "SELECT * FROM artifact_versions WHERE version_id=? AND artifact_id=?",
                (bundle_version_id, preregistration_id),
            ).fetchone()
            if version is None:
                raise ArtifactNotFound(bundle_version_id)
            if version["scientific_hash"] != expected_root:
                raise StalePreregistration(expected_root)
            existing = connection.execute(
                "SELECT attestation_id FROM preregistration_locks WHERE preregistration_id=?",
                (preregistration_id,),
            ).fetchone()
            if existing:
                raise LockedPreregistration(preregistration_id)
            decision = connection.execute(
                "SELECT * FROM review_decisions WHERE decision_id=?", (decision_id,)
            ).fetchone()
            if decision is None or decision["artifact_version_id"] != bundle_version_id \
                    or decision["artifact_hash"] != expected_root \
                    or decision["decision"] != ReviewDecisionValue.APPROVE_PREREGISTRATION.value:
                raise ProvenanceConflict("review decision does not approve this exact bundle root")
            accepted = tuple(sorted(str(x[0]) for x in connection.execute(
                "SELECT finding_hash FROM review_warning_acceptances WHERE decision_id=?", (decision_id,)
            )))
            if accepted != tuple(sorted(current_warning_hashes)):
                raise ProvenanceConflict("accepted warnings do not match current review findings")
            package = connection.execute(
                "SELECT * FROM preregistration_review_packages WHERE bundle_version_id=?", (bundle_version_id,)
            ).fetchone()
            if package is None:
                raise ProvenanceConflict("review package missing")
            state = self._state_in_connection(connection, bundle_version_id)
            if state != PreregistrationState.REVIEWED.value:
                raise ProvenanceConflict(f"lock requires REVIEWED, got {state}")
            chain_hash = self._append_chain(connection, preregistration_id, "PREREGISTRATION_LOCKED", {
                "bundle_version_id": bundle_version_id, "bundle_root_hash": expected_root,
                "review_decision_id": decision_id, "accepted_warning_hashes": accepted,
            }, actor_id, now)
            payload = {
                "attestation_id": attestation_id, "preregistration_id": preregistration_id,
                "bundle_version_id": bundle_version_id, "bundle_root_hash": expected_root,
                "review_decision_id": decision_id, "review_package_hash": str(package["package_hash"]),
                "actor_id": actor_id, "created_at": now, "reason": reason,
                "accepted_warning_hashes": list(accepted), "audit_event_hash": chain_hash,
                "signature_status": "UNSIGNED_LOCAL_ATTESTATION",
            }
            attestation_hash = content_hash(payload)
            connection.execute(
                """INSERT INTO preregistration_attestations(
                    attestation_id,preregistration_id,bundle_version_id,bundle_root_hash,
                    review_decision_id,review_package_hash,actor_id,reason,
                    accepted_warning_hashes_json,audit_event_hash,signature_status,
                    attestation_hash,payload_json,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (attestation_id, preregistration_id, bundle_version_id, expected_root,
                 decision_id, package["package_hash"], actor_id, reason, canonical_json(accepted),
                 chain_hash, "UNSIGNED_LOCAL_ATTESTATION", attestation_hash,
                 canonical_json(payload), now),
            )
            connection.execute(
                """INSERT INTO preregistration_locks(
                    preregistration_id,bundle_version_id,bundle_root_hash,review_decision_id,
                    attestation_id,actor_id,reason,idempotency_key,created_at
                ) VALUES(?,?,?,?,?,?,?,?,?)""",
                (preregistration_id, bundle_version_id, expected_root, decision_id,
                 attestation_id, actor_id, reason, idempotency_key, now),
            )
            sequence = self._next_state_sequence(connection, bundle_version_id)
            self.artifacts._insert_state_event(
                connection, bundle_version_id, sequence, state,
                PreregistrationState.PREREGISTERED_LOCKED.value, actor_id, reason, now, decision_id,
            )
            if idempotency_key:
                connection.execute(
                    "INSERT INTO preregistration_command_keys(idempotency_key,command_type,request_hash,response_json,created_at) VALUES(?,?,?,?,?)",
                    (idempotency_key, "LOCK", request_hash, canonical_json(payload), now),
                )
            self.artifacts._insert_audit(
                connection, self.artifacts._identifier("correlation"), actor_id,
                "PREREGISTRATION_LOCKED", "Preregistration", preregistration_id,
                {"root": expected_root, "attestation_id": attestation_id}, now,
            )
        return PreregistrationAttestation(**{**payload, "accepted_warning_hashes": accepted})

    def command_result(self, key: str, command_type: str, request_hash: str) -> Mapping[str, Any] | None:
        with self.artifacts._connect() as connection:
            row = connection.execute(
                "SELECT * FROM preregistration_command_keys WHERE idempotency_key=?", (key,)
            ).fetchone()
        if row is None:
            return None
        if row["command_type"] != command_type or row["request_hash"] != request_hash:
            raise ProvenanceConflict("idempotency key reused with different content")
        value = json.loads(row["response_json"])
        value["accepted_warning_hashes"] = tuple(value["accepted_warning_hashes"])
        return value

    def attestation(self, preregistration_id: str) -> Mapping[str, Any] | None:
        with self.artifacts._connect() as connection:
            row = connection.execute(
                "SELECT payload_json,attestation_hash FROM preregistration_attestations WHERE preregistration_id=?",
                (preregistration_id,),
            ).fetchone()
        return {**json.loads(row["payload_json"]), "attestation_hash": row["attestation_hash"]} if row else None

    def record_exposure(
        self, scenario_id: str, scenario_hash: str, world_seed: int, exposure_kind: str,
        actor_id: str, context_type: str, context_id: str,
        preregistration_root_hash: str | None = None,
    ) -> Mapping[str, Any]:
        now, exposure_id = self.artifacts.now(), self.artifacts._identifier("exposure")
        with self.artifacts.transaction() as connection:
            previous = connection.execute(
                """SELECT event_hash FROM exposure_records WHERE scenario_id=? AND scenario_hash=?
                AND world_seed=? ORDER BY occurred_at DESC,exposure_id DESC LIMIT 1""",
                (scenario_id, scenario_hash, world_seed),
            ).fetchone()
            previous_hash = str(previous["event_hash"]) if previous else None
            event = {
                "exposure_id": exposure_id, "scenario_id": scenario_id,
                "scenario_hash": scenario_hash, "world_seed": world_seed,
                "exposure_kind": exposure_kind, "actor_id": actor_id, "occurred_at": now,
                "context_type": context_type, "context_id": context_id,
                "preregistration_root_hash": preregistration_root_hash,
                "previous_event_hash": previous_hash,
            }
            event_hash = content_hash({"domain": "terrario-exposure-v1", "event": event})
            connection.execute(
                """INSERT INTO exposure_records(
                    exposure_id,scenario_id,scenario_hash,world_seed,exposure_kind,actor_id,
                    context_type,context_id,preregistration_root_hash,previous_event_hash,event_hash,occurred_at
                ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)""",
                (exposure_id, scenario_id, scenario_hash, world_seed, exposure_kind, actor_id,
                 context_type, context_id, preregistration_root_hash, previous_hash, event_hash, now),
            )
            self.artifacts._insert_audit(
                connection, self.artifacts._identifier("correlation"), actor_id,
                "EXPOSURE_RECORDED", "WorldSeed", f"{scenario_id}:{world_seed}",
                {"event_hash": event_hash, "kind": exposure_kind, "context": context_id}, now,
            )
        return {**event, "event_hash": event_hash}

    def exposures(self, scenario_id: str | None = None, world_seed: int | None = None) -> tuple[Mapping[str, Any], ...]:
        query, values = "SELECT * FROM exposure_records WHERE 1=1", []
        if scenario_id is not None:
            query += " AND scenario_id=?"; values.append(scenario_id)
        if world_seed is not None:
            query += " AND world_seed=?"; values.append(world_seed)
        query += " ORDER BY occurred_at,exposure_id"
        with self.artifacts._connect() as connection:
            return tuple(dict(row) for row in connection.execute(query, values))

    def append_chain(self, preregistration_id: str, event_type: str, payload: Any,
                     actor_id: str) -> str:
        now = self.artifacts.now()
        with self.artifacts.transaction() as connection:
            return self._append_chain(connection, preregistration_id, event_type, payload, actor_id, now)

    def _append_chain(self, connection: sqlite3.Connection, preregistration_id: str,
                      event_type: str, payload: Any, actor_id: str, now: str) -> str:
        previous = connection.execute(
            "SELECT sequence,event_hash FROM preregistration_audit_chain WHERE preregistration_id=? ORDER BY sequence DESC LIMIT 1",
            (preregistration_id,),
        ).fetchone()
        sequence = int(previous["sequence"])+1 if previous else 1
        previous_hash = str(previous["event_hash"]) if previous else None
        event_content = {
            "preregistration_id": preregistration_id, "sequence": sequence,
            "event_type": event_type, "payload": plain(payload), "actor_id": actor_id,
            "created_at": now,
        }
        event_hash = content_hash({
            "domain": "terrario-preregistration-audit-v1",
            "previous_event_hash": previous_hash, "event": event_content,
        })
        connection.execute(
            """INSERT INTO preregistration_audit_chain(
                chain_event_id,preregistration_id,sequence,event_type,event_payload_json,
                previous_event_hash,event_hash,actor_id,created_at
            ) VALUES(?,?,?,?,?,?,?,?,?)""",
            (self.artifacts._identifier("chain-event"), preregistration_id, sequence,
             event_type, canonical_json(payload), previous_hash, event_hash, actor_id, now),
        )
        return event_hash

    def audit_chain(self, preregistration_id: str) -> tuple[Mapping[str, Any], ...]:
        with self.artifacts._connect() as connection:
            rows = connection.execute(
                "SELECT * FROM preregistration_audit_chain WHERE preregistration_id=? ORDER BY sequence",
                (preregistration_id,),
            ).fetchall()
        return tuple({**dict(row), "event_payload": json.loads(row["event_payload_json"])} for row in rows)

    def verify_audit_chain(self, preregistration_id: str) -> bool:
        previous_hash = None
        for row in self.audit_chain(preregistration_id):
            content = {
                "preregistration_id": preregistration_id, "sequence": row["sequence"],
                "event_type": row["event_type"], "payload": row["event_payload"],
                "actor_id": row["actor_id"], "created_at": row["created_at"],
            }
            expected = content_hash({
                "domain": "terrario-preregistration-audit-v1",
                "previous_event_hash": previous_hash, "event": content,
            })
            if row["previous_event_hash"] != previous_hash or row["event_hash"] != expected:
                return False
            previous_hash = expected
        return True

    @staticmethod
    def _state_in_connection(connection: sqlite3.Connection, version_id: str) -> str | None:
        row = connection.execute(
            "SELECT to_state FROM artifact_state_events WHERE version_id=? ORDER BY sequence DESC LIMIT 1",
            (version_id,),
        ).fetchone()
        return str(row["to_state"]) if row else None

    @staticmethod
    def _next_state_sequence(connection: sqlite3.Connection, version_id: str) -> int:
        row = connection.execute(
            "SELECT MAX(sequence) FROM artifact_state_events WHERE version_id=?", (version_id,)
        ).fetchone()
        return int(row[0] or 0) + 1
