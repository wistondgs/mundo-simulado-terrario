"""Application service shared by HTTP, CLI, and the browser UI."""
from __future__ import annotations

import json
import platform
import subprocess
import sys
from dataclasses import replace
from pathlib import Path
from typing import Any, Mapping

from terrario.lab.experiment_composer import ExperimentDraft
from terrario.lab.metrics_observer import MetricRegistry, ObserverRegistry
from terrario.lab.models import thaw
from terrario.lab.persistence import ArtifactNotFound, ArtifactRepository, ProvenanceConflict
from terrario.lab.persistence.canonical import content_hash, plain
from terrario.lab.persistence.codecs import experiment_draft_from_payload, preregistration_draft_from_payload
from terrario.lab.preregistration.commitments import CommitmentBuilder
from terrario.lab.preregistration.domain import (
    AnalysisPlan, CausalDesignCommitment, CausalMode, ControlCommitment,
    AmendmentRecord, DeviationRecord, DeviationType, EndpointCommitment, EndpointRole,
    EnvironmentRequirement, ExclusionPolicy, ExclusionRule, ExposureKind, ExposureStatus,
    FailurePolicy, FailureRule, MetricCommitment, ObservedEnvironment,
    ObserverChannelCommitment, ObserverCommitment, Partition,
    PreregistrationDraft, PreregistrationNotReady, PreregistrationReadinessReport, ProtocolSnapshot,
    PreregistrationState, RandomizationPlan, ReplicationPlan, ReviewDecisionValue,
    SeedCommitment, SeedPartition, ScientificQuestionSnapshot, SoftwareManifest,
    StoppingRule, StorageTracePolicy, StudyIntent, assert_transition,
)
from terrario.lab.preregistration.repository import PreregistrationRepository
from terrario.lab.preregistration.validation import policy_snapshot_hash, validate_preregistration
from terrario.lab.world_authoring import compile_registry_world
from terrario.lab.world_registry import WorldScenarioRegistry


class PreregistrationService:
    """Scientific governance only: this class deliberately has no run method."""

    CREATE_FIELDS = {
        "preregistration_id", "experiment_draft_version_id", "trial_matrix_version_id",
        "study_intent", "scientific_question", "causal_design", "endpoints",
        "analysis", "partitions", "randomization", "replication", "stopping",
        "exclusions", "failures", "storage", "environment_requirement",
        "observed_environment", "software", "ui_preferences", "reason",
    }
    FORBIDDEN_CLIENT_FIELDS = {"state", "approved", "locked", "actor", "actor_id", "created_by"}

    def __init__(self, root: str | Path, artifacts: ArtifactRepository,
                 metrics: MetricRegistry, observers: ObserverRegistry):
        self.root = Path(root).resolve()
        self.artifacts = artifacts
        self.repository = PreregistrationRepository(artifacts)
        self.commitments = CommitmentBuilder(artifacts)
        self.metrics, self.observers = metrics, observers

    def create(self, request: Mapping[str, Any], actor_id: str) -> Mapping[str, Any]:
        self._strict(request, self.CREATE_FIELDS)
        draft = self._assemble(request)
        record = self.repository.create_draft(
            draft.preregistration_id, plain(draft), draft.scientific_payload(), actor_id,
            str(request.get("reason", "preregistration draft creation")),
        )
        return self._view(record)

    def derive(self, preregistration_id: str, expected_hash: str,
               changes: Mapping[str, Any], reason: str, actor_id: str) -> Mapping[str, Any]:
        if self.FORBIDDEN_CLIENT_FIELDS & set(changes):
            raise ValueError("client cannot set governance fields")
        if self.repository.is_locked(preregistration_id):
            from terrario.lab.preregistration.domain import LockedPreregistration
            raise LockedPreregistration(preregistration_id)
        current = self.artifacts.current(preregistration_id, "Preregistration")
        state = self.artifacts.current_state(current.version_id)
        if state not in {PreregistrationState.DRAFT.value, PreregistrationState.REVIEWED.value}:
            raise ProvenanceConflict(f"derivation prohibited from state {state}")
        draft = self._draft_from_record(current)
        base = plain(draft)
        unknown = set(changes) - set(base)
        if unknown:
            raise ValueError(f"unknown preregistration changes: {sorted(unknown)}")
        base.update(plain(changes)); base["preregistration_id"] = preregistration_id
        child = preregistration_draft_from_payload(base)
        record = self.repository.derive_draft(preregistration_id, plain(child), child.scientific_payload(),
            expected_hash, actor_id, reason, {"changes": plain(changes)})
        return self._view(record)

    def validate_request(self, request: Mapping[str, Any]) -> Mapping[str, Any]:
        self._strict(request, self.CREATE_FIELDS)
        draft = self._assemble(request)
        report = self._readiness_for(draft)
        return {"draft": plain(draft), "scientific_hash": draft.scientific_hash,
                "readiness": self._report_payload(report), "persisted": False}

    def readiness(self, preregistration_id: str) -> Mapping[str, Any]:
        record = self.artifacts.current(preregistration_id, "Preregistration")
        return self._report_payload(self._readiness_for(self._draft_from_record(record)))

    def prepare_review(self, preregistration_id: str, expected_hash: str,
                       actor_id: str, reason: str) -> Mapping[str, Any]:
        current = self.artifacts.current(preregistration_id, "Preregistration")
        if self.artifacts.current_state(current.version_id) != PreregistrationState.DRAFT.value:
            raise ProvenanceConflict("review preparation requires DRAFT")
        if current.scientific_hash != expected_hash:
            from terrario.lab.preregistration.domain import StalePreregistration
            raise StalePreregistration(expected_hash)
        draft = self._draft_from_record(current)
        report = self._readiness_for(draft)
        if not report.complete:
            raise PreregistrationNotReady("blocking findings prevent review preparation")
        prepared = self.commitments.build(draft)
        package = {
            "schema_version": "terrario.lab.preregistration-review-package/v1",
            "preregistration_id": preregistration_id,
            "candidate_root_hash": prepared.bundle_root_hash,
            "summary": self._summary(draft),
            "scientific_question": plain(draft.scientific_question),
            "causal_design": plain(draft.causal_design),
            "protocol": plain(draft.protocol), "controls": plain(draft.protocol.controls),
            "metrics": plain(draft.metrics), "endpoints": plain(draft.endpoints),
            "observer": plain(draft.observer), "seeds": plain(draft.seeds),
            "partitions": plain(draft.partitions), "randomization": plain(draft.randomization),
            "replication": plain(draft.replication), "analysis": plain(draft.analysis),
            "stopping": plain(draft.stopping), "exclusions": plain(draft.exclusions),
            "failure_policy": plain(draft.failures), "storage": plain(draft.storage),
            "environment_requirement": plain(draft.environment_requirement),
            "observed_environment": plain(draft.observed_environment), "software": plain(draft.software),
            "readiness": self._report_payload(replace(report, candidate_hash=prepared.bundle_root_hash)),
            "scientific_diff": self._scientific_diff(current),
            "provenance": {
                "experiment_draft_version_id": draft.protocol.experiment_draft_version_id,
                "experiment_draft_hash": draft.protocol.experiment_draft_hash,
                "trial_matrix_version_id": draft.protocol.trial_matrix_version_id,
                "trial_matrix_hash": draft.protocol.trial_matrix_hash,
            },
            "automatic_approval": False, "scientific_execution": False,
        }
        sealed = self.repository.seal_candidate(preregistration_id, plain(draft), prepared,
                                                 package, actor_id, reason)
        return {**self._view(sealed), "bundle_root_hash": prepared.bundle_root_hash,
                "review_package": package}

    def submit(self, preregistration_id: str, actor_id: str, reason: str) -> Mapping[str, Any]:
        current = self.artifacts.current(preregistration_id, "Preregistration")
        return self.repository.create_review_request(current.version_id, "PREREGISTRATION", actor_id, reason)

    def request_experiment_review(self, experiment_version_id: str, actor_id: str,
                                  reason: str) -> Mapping[str, Any]:
        return self.repository.create_review_request(experiment_version_id, "EXPERIMENT_DESIGN", actor_id, reason)

    def decide(self, review_id: str, artifact_hash: str, decision: str, reason: str,
               warning_acceptances: tuple[Mapping[str, str], ...], actor_id: str) -> Mapping[str, Any]:
        row = self.repository.record_review_decision(review_id, artifact_hash,
            ReviewDecisionValue(decision), actor_id, reason, warning_acceptances)
        return plain(row)

    def lock(self, preregistration_id: str, expected_root: str, decision_id: str,
             reason: str, actor_id: str, idempotency_key: str | None) -> Mapping[str, Any]:
        current = self.artifacts.current(preregistration_id, "Preregistration")
        if current.scientific_hash != expected_root:
            from terrario.lab.preregistration.domain import StalePreregistration
            raise StalePreregistration(expected_root)
        draft = self._draft_from_record(current)
        report = self._readiness_for(draft)
        if not report.complete:
            raise PreregistrationNotReady("current validation has blocking findings")
        prepared = self.commitments.build(draft)
        if prepared.bundle_root_hash != expected_root:
            raise ProvenanceConflict("rebuilt root differs from reviewed root")
        warnings = tuple(sorted(f.finding_hash for f in report.findings if not f.blocking))
        return plain(self.repository.lock(preregistration_id, current.version_id, expected_root,
            decision_id, actor_id, reason, warnings, idempotency_key))

    def verify(self, preregistration_id: str) -> Mapping[str, Any]:
        current = self.artifacts.current(preregistration_id, "Preregistration")
        payload = current.payload
        root = payload.get("root_manifest") if isinstance(payload, Mapping) else None
        failures: list[str] = []
        warnings: list[str] = []
        schema_valid = current.schema_version == "terrario.lab.preregistration-bundle/v1"
        component_hashes_valid = cas_valid = root_hash_valid = False
        if not root:
            failures.append("BUNDLE_NOT_PREPARED")
        else:
            valid, commitment_failures = self.commitments.verify(root)
            failures.extend(commitment_failures)
            cas_valid = not any("CAS" in x for x in commitment_failures)
            component_hashes_valid = not any("COMPONENT" in x for x in commitment_failures)
            root_hash_valid = content_hash(root) == current.scientific_hash
            if not root_hash_valid:
                failures.append("ROOT_HASH_MISMATCH")
            roles = [str(x.get("role")) for x in root.get("components", ())]
            if tuple(roles) != self.commitments.ROLE_ORDER:
                failures.append("BUNDLE_COMPONENT_SET_INVALID")
            with self.artifacts._connect() as connection:
                stored = [dict(x) for x in connection.execute(
                    "SELECT * FROM preregistration_components WHERE bundle_version_id=? ORDER BY ordinal",
                    (current.version_id,))]
                package = connection.execute(
                    "SELECT * FROM preregistration_review_packages WHERE bundle_version_id=?", (current.version_id,)).fetchone()
            if len(stored) != len(root.get("components", ())): failures.append("COMPONENT_INDEX_INCOMPLETE")
            else:
                for descriptor, row in zip(root["components"], stored):
                    if any(str(descriptor.get(key)) != str(row[column]) for key, column in
                           (("role", "role"), ("content_sha256", "content_hash"), ("cas_sha256", "cas_hash"))):
                        failures.append(f"COMPONENT_INDEX_MISMATCH:{descriptor.get('role')}")
            if package is None: failures.append("REVIEW_PACKAGE_MISSING")
            elif not self.artifacts.blobs.verify(str(package["blob_hash"])): failures.append("REVIEW_PACKAGE_CAS_INVALID")
            elif content_hash(json.loads(self.artifacts.blobs.read(str(package["blob_hash"])))) != package["package_hash"]:
                failures.append("REVIEW_PACKAGE_HASH_INVALID")
        draft = self._draft_from_record(current)
        reference_valid = True
        for version_id, expected_hash, expected_kind in (
            (draft.protocol.experiment_draft_version_id, draft.protocol.experiment_draft_hash, "ExperimentDraft"),
            (draft.protocol.trial_matrix_version_id, draft.protocol.trial_matrix_hash, "TrialMatrix")):
            try: referenced = self.artifacts.get_version(version_id)
            except ArtifactNotFound: reference_valid = False; failures.append(f"REFERENCED_ARTIFACT_MISSING:{version_id}")
            else:
                if referenced.kind != expected_kind or referenced.scientific_hash != expected_hash:
                    reference_valid = False; failures.append(f"REFERENCED_ARTIFACT_MISMATCH:{version_id}")
        parent_valid, seen, cursor = True, set(), current
        while cursor.parent_version_id:
            if cursor.version_id in seen: parent_valid = False; failures.append("PARENT_LINEAGE_CYCLE"); break
            seen.add(cursor.version_id)
            try: parent = self.artifacts.get_version(cursor.parent_version_id)
            except ArtifactNotFound: parent_valid = False; failures.append("PARENT_VERSION_MISSING"); break
            if cursor.parent_hash != parent.scientific_hash or parent.artifact_id != current.artifact_id:
                parent_valid = False; failures.append("PARENT_LINEAGE_HASH_MISMATCH"); break
            cursor = parent
        if not self.repository.verify_audit_chain(preregistration_id):
            failures.append("AUDIT_CHAIN_INVALID")
        locked = self.repository.is_locked(preregistration_id)
        attestation = self.repository.attestation(preregistration_id)
        review_valid = immutable_valid = False
        if locked:
            lock = self.repository.lock_row(preregistration_id)
            if attestation is None or lock is None: failures.append("ATTESTATION_OR_LOCK_MISSING")
            else:
                review_valid = lock["bundle_version_id"] == current.version_id and lock["bundle_root_hash"] == current.scientific_hash
                review_valid = review_valid and attestation["review_decision_id"] == lock["review_decision_id"]
                if not review_valid: failures.append("REVIEW_LOCK_BINDING_INVALID")
                if content_hash({k:v for k,v in attestation.items() if k != "attestation_hash"}) != attestation["attestation_hash"]:
                    failures.append("ATTESTATION_HASH_INVALID")
                immutable_valid = self.artifacts.current_state(current.version_id) in {
                    PreregistrationState.PREREGISTERED_LOCKED.value,
                    PreregistrationState.SUPERSEDED.value, PreregistrationState.WITHDRAWN.value}
                if not immutable_valid: failures.append("LOCK_STATE_INVALID")
        else: warnings.append("NOT_LOCKED")
        report = {
                "preregistration_id": preregistration_id, "version_id": current.version_id,
                "root": current.scientific_hash, "status": "VERIFIED" if not failures else "INVALID",
                "valid": not failures, "schema_valid": schema_valid,
                "component_hashes_valid": component_hashes_valid, "root_hash_valid": root_hash_valid,
                "cas_valid": cas_valid, "review_binding_valid": review_valid,
                "immutable_status_valid": immutable_valid, "audit_chain_valid": "AUDIT_CHAIN_INVALID" not in failures,
                "parent_chain_valid": parent_valid, "referenced_artifacts_valid": reference_valid,
                "provenance_available": bool(draft.scientific_question.theory_snapshot_hash),
                "failures": failures, "warnings": warnings, "locked": locked,
                "attestation": attestation,
                "scientific_execution": False, "evidence_publication": False}
        if not schema_valid: report["failures"].append("UNSUPPORTED_BUNDLE_SCHEMA"); report["valid"] = False; report["status"] = "INVALID"
        return report

    def get(self, preregistration_id: str) -> Mapping[str, Any]:
        return self._view(self.artifacts.current(preregistration_id, "Preregistration"))

    def list(self) -> tuple[Mapping[str, Any], ...]:
        return tuple(self._view(x) for x in self.artifacts.list_artifacts("Preregistration"))

    def versions(self, preregistration_id: str) -> tuple[Mapping[str, Any], ...]:
        return tuple(self._view(x) for x in self.artifacts.versions(preregistration_id))

    def review_package(self, preregistration_id: str) -> Mapping[str, Any]:
        return self.repository.review_package(self.artifacts.current(preregistration_id).version_id)

    def trial_matrix(self, preregistration_id: str) -> Mapping[str, Any]:
        draft = self._draft_from_record(self.artifacts.current(preregistration_id))
        return self.artifacts.get_version(draft.protocol.trial_matrix_version_id).payload

    def record_exposure(self, scenario_id: str, scenario_hash: str, world_seed: int,
                        kind: str, actor_id: str, context_type: str, context_id: str,
                        root: str | None = None) -> Mapping[str, Any]:
        roots = [root] if root else []
        if not roots:
            for record in self.artifacts.list_artifacts("Preregistration"):
                if not self.repository.is_locked(record.artifact_id): continue
                draft = self._draft_from_record(record)
                if draft.protocol.scenario_id == scenario_id and draft.protocol.world_definition_hash == scenario_hash and world_seed in draft.seeds.world_seeds:
                    roots.append(record.scientific_hash)
        if not roots: roots = [None]
        rows = [self.repository.record_exposure(scenario_id, scenario_hash, world_seed,
            ExposureKind(kind).value, actor_id, context_type, context_id, bound_root) for bound_root in roots]
        return rows[-1] if len(rows) == 1 else {"records": rows}

    def exposure_records(self, scenario_id: str | None = None,
                         world_seed: int | None = None) -> tuple[Mapping[str, Any], ...]:
        return self.repository.exposures(scenario_id, world_seed)

    def audit_chain(self, preregistration_id: str) -> Mapping[str, Any]:
        return {"events": self.repository.audit_chain(preregistration_id),
                "valid": self.repository.verify_audit_chain(preregistration_id)}

    def withdraw(self, preregistration_id: str, reason: str, actor_id: str) -> Mapping[str, Any]:
        current = self.artifacts.current(preregistration_id)
        old = self.artifacts.current_state(current.version_id)
        assert_transition(PreregistrationState(old), PreregistrationState.WITHDRAWN)
        event = self.artifacts.append_state(current.version_id, PreregistrationState.WITHDRAWN.value,
            actor_id=actor_id, reason=reason)
        self.repository.append_chain(preregistration_id, "WITHDRAWN", {"reason": reason}, actor_id)
        return event

    def add_postlock_record(self, preregistration_id: str, kind: str,
                            payload: Mapping[str, Any], actor_id: str) -> Mapping[str, Any]:
        if not self.repository.is_locked(preregistration_id):
            raise ProvenanceConflict("post-lock record requires a locked preregistration")
        if kind not in {"PreregistrationAmendment", "ProtocolDeviation"}:
            raise ValueError("unsupported post-lock record")
        forbidden = self.FORBIDDEN_CLIENT_FIELDS & set(payload)
        if forbidden:
            raise ValueError("client cannot set authority fields")
        parent = self.artifacts.current(preregistration_id)
        now = self.artifacts.now()
        if kind == "ProtocolDeviation":
            required = {"deviation_type", "affected_component", "planned_behavior", "actual_behavior",
                        "reason", "scientific_impact_assessment", "disposition"}
            if set(payload) != required: raise ValueError(f"deviation requires exact fields: {sorted(required)}")
            value = plain(DeviationRecord(self.artifacts._identifier("deviation"), preregistration_id,
                parent.scientific_hash, DeviationType(payload["deviation_type"]),
                str(payload["affected_component"]), str(payload["planned_behavior"]), str(payload["actual_behavior"]),
                str(payload["reason"]), str(payload["scientific_impact_assessment"]),
                str(payload["disposition"]), actor_id, now))
        else:
            required = {"change_class", "reason", "delta"}
            if not required <= set(payload) or set(payload) - (required | {"child_preregistration_id"}):
                raise ValueError(f"amendment requires fields: {sorted(required)}")
            change_class = str(payload["change_class"]).upper()
            child_id = payload.get("child_preregistration_id")
            if change_class != "METADATA" and not child_id:
                raise ValueError("scientific/operational amendment requires child_preregistration_id")
            if child_id:
                source = plain(self._draft_from_record(parent)); delta = plain(payload["delta"])
                unknown = set(delta) - set(source)
                if unknown: raise ValueError(f"unknown amendment fields: {sorted(unknown)}")
                source.update(delta); source["preregistration_id"] = str(child_id)
                child = preregistration_draft_from_payload(source)
                self.repository.create_draft(str(child_id), plain(child), child.scientific_payload(), actor_id,
                    str(payload["reason"]), parent.scientific_hash)
            value = plain(AmendmentRecord(self.artifacts._identifier("amendment"), preregistration_id,
                parent.scientific_hash, change_class, str(payload["reason"]), actor_id, now,
                str(child_id) if child_id else None, plain(payload["delta"])))
            value["automatic_protocol_change"] = False
        stored = self.artifacts.create_artifact(kind, value, f"terrario.lab.{kind.casefold()}/v1",
            classification="POST_LOCK_GOVERNANCE_RECORD", created_by=actor_id,
            reason=str(payload.get("reason", kind)), initial_state="RECORDED", sealed=True)
        self.repository.append_chain(preregistration_id, kind.upper(), {"record_id": stored.artifact_id,
            "record_hash": stored.scientific_hash}, actor_id)
        return self._view(stored)

    def supersede(self, preregistration_id: str, child_id: str, reason: str, actor_id: str) -> Mapping[str, Any]:
        parent, child = self.artifacts.current(preregistration_id), self.artifacts.current(child_id)
        if not self.repository.is_locked(preregistration_id) or not self.repository.is_locked(child_id):
            raise ProvenanceConflict("supersede requires both parent and descendant locked")
        lineage = self.repository.audit_chain(child_id)
        if not any(x["event_type"] == "DRAFT_CREATED" and x["event_payload"].get("parent_root_hash") == parent.scientific_hash for x in lineage):
            raise ProvenanceConflict("child is not a declared descendant of the parent root")
        state = self.artifacts.current_state(parent.version_id)
        assert_transition(PreregistrationState(state), PreregistrationState.SUPERSEDED)
        event = self.artifacts.append_state(parent.version_id, PreregistrationState.SUPERSEDED.value,
            actor_id=actor_id, reason=reason)
        with self.artifacts.transaction() as connection:
            connection.execute("INSERT INTO artifact_links(link_id,source_version_id,target_version_id,relation,epistemic_status,provenance_json,created_at) VALUES(?,?,?,?,?,?,?)",
                (self.artifacts._identifier("link"), parent.version_id, child.version_id, "SUPERSEDED_BY",
                 "GOVERNANCE_LINEAGE", json.dumps({"reason": reason, "actor": actor_id}, sort_keys=True), self.artifacts.now()))
        self.repository.append_chain(preregistration_id, "SUPERSEDED", {"child_id": child_id, "child_root": child.scientific_hash}, actor_id)
        return event

    def export(self, preregistration_id: str) -> Mapping[str, Any]:
        current = self.artifacts.current(preregistration_id)
        base = self.artifacts.export_bundle(current.version_id)
        draft = self._draft_from_record(current)
        root = current.payload.get("root_manifest", {})
        components = {str(x["cas_sha256"]): json.loads(self.artifacts.blobs.read(str(x["cas_sha256"])))
                      for x in root.get("components", ())}
        if root: components[content_hash(root)] = root
        envelope = {"schema_version": "terrario.preregistration-portable/v1", "artifact_bundle": base,
            "artifact_lineage": [self.artifacts.export_bundle(x.version_id) for x in self.artifacts.versions(preregistration_id)],
            "referenced_artifacts": [self.artifacts.export_bundle(draft.protocol.experiment_draft_version_id),
                                     self.artifacts.export_bundle(draft.protocol.trial_matrix_version_id)],
            "review_package": self.repository.review_package(current.version_id) if current.sealed else None,
            "attestation": self.repository.attestation(preregistration_id),
            "audit_chain": self.repository.audit_chain(preregistration_id),
            "component_payloads": components,
            "external_attestation_is_local_approval": False}
        envelope["portable_hash"] = content_hash(envelope)
        return envelope

    def validate_portable(self, bundle: Mapping[str, Any]) -> Mapping[str, Any]:
        value = plain(bundle); supplied = value.pop("portable_hash", None)
        failures = []
        if value.get("schema_version") != "terrario.preregistration-portable/v1": failures.append("UNSUPPORTED_PORTABLE_SCHEMA")
        if supplied != content_hash(value): failures.append("PORTABLE_HASH_MISMATCH")
        try: validated = self.artifacts.validate_bundle(value.get("artifact_bundle") or {})
        except Exception as exc: failures.append(f"ARTIFACT_BUNDLE_INVALID:{exc}"); validated = None
        version = (value.get("artifact_bundle") or {}).get("version") or {}
        for section in ("artifact_lineage", "referenced_artifacts"):
            for item in value.get(section, ()):
                try: self.artifacts.validate_bundle(item)
                except Exception as exc: failures.append(f"{section.upper()}_INVALID:{exc}")
        lineage = value.get("artifact_lineage") or []
        for left, right in zip(lineage, lineage[1:]):
            if right["version"].get("parent_hash") != left["version"].get("scientific_hash"):
                failures.append("PORTABLE_PARENT_LINEAGE_INVALID")
        root = (version.get("payload") or {}).get("root_manifest") or {}
        components = value.get("component_payloads") or {}
        for descriptor in root.get("components", ()):
            digest = str(descriptor.get("cas_sha256", "")); payload = components.get(digest)
            if payload is None: failures.append(f"COMPONENT_MISSING:{descriptor.get('role')}")
            elif content_hash(payload) != digest or content_hash(payload) != descriptor.get("content_sha256"):
                failures.append(f"COMPONENT_TAMPERED:{descriptor.get('role')}")
        if root and content_hash(root) != version.get("scientific_hash"): failures.append("ROOT_HASH_MISMATCH")
        return {"valid": not failures, "failures": tuple(failures), "portable_hash": supplied,
                "artifact": validated, "external_attestation_is_local_approval": False,
                "scientific_execution": False}

    def import_portable(self, bundle: Mapping[str, Any], actor_id: str) -> Mapping[str, Any]:
        report = self.validate_portable(bundle)
        if not report["valid"]:
            raise ProvenanceConflict("portable bundle failed verification: " + ",".join(report["failures"]))
        for digest, payload in bundle["component_payloads"].items():
            manifest = self.artifacts.register_blob(json.dumps(payload, sort_keys=True, separators=(",", ":"),
                ensure_ascii=False, allow_nan=False).encode("utf-8"),
                "application/vnd.terrario.preregistration-component+json")
            if manifest.blob_hash != digest: raise ProvenanceConflict("component CAS digest changed during import")
        for reference in bundle.get("referenced_artifacts", ()):
            self.artifacts.import_bundle_exact(reference, actor_id)
        records = [self.artifacts.import_bundle_exact(item, actor_id) for item in bundle.get("artifact_lineage", ())]
        record = records[-1] if records else self.artifacts.import_bundle_exact(bundle["artifact_bundle"], actor_id)
        root = record.payload.get("root_manifest", {})
        review = bundle.get("review_package")
        with self.artifacts.transaction() as connection:
            indexed = connection.execute("SELECT 1 FROM preregistration_components WHERE bundle_version_id=?", (record.version_id,)).fetchone()
            if not indexed:
                now = self.artifacts.now()
                for descriptor in root.get("components", ()):
                    connection.execute("""INSERT INTO preregistration_components(
                        component_id,bundle_version_id,role,ordinal,schema_version,content_hash,cas_hash,
                        source_artifact_version_id,source_scientific_hash,created_at) VALUES(?,?,?,?,?,?,?,?,?,?)""",
                        (self.artifacts._identifier("component"), record.version_id, descriptor["role"], descriptor["ordinal"],
                         descriptor["schema_version"], descriptor["content_sha256"], descriptor["cas_sha256"],
                         descriptor.get("source_artifact_version_id"), descriptor.get("source_scientific_hash"), now))
                if review:
                    review_clean = {k:v for k,v in review.items() if k not in {"review_package_id", "review_package_hash"}}
                    blob = self.artifacts.register_blob.__self__.blobs.put_bytes(
                        json.dumps(review_clean, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode(),
                        "application/vnd.terrario.preregistration-review+json")
                    connection.execute("INSERT OR IGNORE INTO blob_manifests(blob_hash,relative_path,size_bytes,media_type,created_at) VALUES(?,?,?,?,?)",
                        (blob.blob_hash, blob.relative_path, blob.size_bytes, blob.media_type, now))
                    connection.execute("INSERT INTO preregistration_review_packages(review_package_id,bundle_version_id,package_hash,blob_hash,policy_snapshot_hash,created_at) VALUES(?,?,?,?,?,?)",
                        (self.artifacts._identifier("review-package"), record.version_id, content_hash(review_clean), blob.blob_hash,
                         review_clean["readiness"]["policy_snapshot_hash"], now))
        if self.artifacts.current_state(record.version_id) is None:
            self.artifacts.append_state(record.version_id, PreregistrationState.READY_FOR_REVIEW.value,
                actor_id=actor_id, reason="verified external bundle imported for local review")
        if not self.repository.audit_chain(record.artifact_id):
            self.repository.append_chain(record.artifact_id, "VERIFIED_EXTERNAL_IMPORT",
                {"portable_hash": bundle["portable_hash"], "external_attestation_trusted": False}, actor_id)
        return {**self._view(record), "imported_attestation_trusted": False,
                "requires_local_review_for_lock": True, "portable_hash": bundle["portable_hash"]}

    def review_requests(self) -> tuple[Mapping[str, Any], ...]:
        with self.artifacts._connect() as connection:
            # A human reviewer must see the immutable object they are deciding
            # about.  Returning only a version ID forces a client to guess or
            # reconstruct the decision binding and is unsafe for a local UI.
            rows = connection.execute(
                """SELECT r.*, v.kind AS artifact_kind, v.scientific_hash AS artifact_hash,
                          v.schema_version AS artifact_schema_version,
                          (SELECT d.decision FROM review_decisions d
                           WHERE d.review_id = r.review_id
                           ORDER BY d.created_at DESC, d.decision_id DESC LIMIT 1) AS latest_decision,
                          (SELECT d.decision_id FROM review_decisions d
                           WHERE d.review_id = r.review_id
                           ORDER BY d.created_at DESC, d.decision_id DESC LIMIT 1) AS latest_decision_id,
                          (SELECT d.created_at FROM review_decisions d
                           WHERE d.review_id = r.review_id
                           ORDER BY d.created_at DESC, d.decision_id DESC LIMIT 1) AS decided_at
                   FROM review_requests r
                   JOIN artifact_versions v ON v.version_id = r.artifact_version_id
                   ORDER BY r.created_at, r.review_id"""
            ).fetchall()
            return tuple(dict(x) for x in rows)

    def _assemble(self, request: Mapping[str, Any]) -> PreregistrationDraft:
        experiment_record = self.artifacts.get_version(str(request["experiment_draft_version_id"]))
        matrix_record = self.artifacts.get_version(str(request["trial_matrix_version_id"]))
        if experiment_record.kind != "ExperimentDraft" or matrix_record.kind != "TrialMatrix":
            raise ValueError("source versions must be ExperimentDraft and TrialMatrix")
        experiment = experiment_draft_from_payload(experiment_record.payload)
        world_entry = WorldScenarioRegistry(self.root).get(experiment.scenario_id)
        compiled_world = compile_registry_world(experiment.scenario_id, world_entry.source)
        matrix = matrix_record.payload
        if matrix.get("draft_hash") != experiment_record.scientific_hash:
            raise ProvenanceConflict("TrialMatrix does not belong to the exact ExperimentDraft")
        intent = StudyIntent(request.get("study_intent", "EXPLORATORY"))
        q = request.get("scientific_question") or {}
        causal = request.get("causal_design") or {"mode": "DESCRIPTIVE_ONLY"}
        self._reject_unknown(q, {"theory_snapshot_id", "theory_snapshot_hash", "hypothesis_id", "hypothesis_hash",
            "upstream_review_version_id", "upstream_review_hash", "rival_hypotheses", "null_hypothesis",
            "discriminating_prediction", "falsification_criteria", "interpretation_boundaries"}, "scientific_question")
        self._reject_unknown(causal, {"mode", "manipulated_variable", "intervention", "comparison", "control",
            "outcome", "estimand", "manipulation_check", "identification_assumptions", "known_confounders",
            "rival_predictions"}, "causal_design")
        channels = self.observers.expand(experiment.observer_profile)
        observer = ObserverCommitment(experiment.observer_profile, self.observers.profile(experiment.observer_profile).schema_version,
            tuple(ObserverChannelCommitment(x.channel_id, x.payload_schema, x.frequency,
                x.separation_class.value, x.availability) for x in channels), "FROZEN_PROFILE", (), "PROJECT_POLICY")
        seeds = SeedCommitment.materialize(experiment.world_seeds, experiment.agent_seeds,
            tuple(int(x) for x in (request.get("randomization") or {}).get("seeds", ())),
            tuple(int(x) for x in (request.get("randomization") or {}).get("replacement_seeds", ())))
        metrics = tuple(self._metric_commitment(x, seeds) for x in experiment.metric_ids)
        is_cl7 = any(metric.metric_id == "planned-action-evaluation-pathway" for metric in metrics)
        role = EndpointRole.EXPLORATORY if intent is StudyIntent.EXPLORATORY else EndpointRole.PRIMARY
        endpoints = tuple(EndpointCommitment(**{**x, "role": EndpointRole(x["role"])}) for x in request.get("endpoints", ())) or tuple(
            EndpointCommitment(f"endpoint-{i+1}", metric.metric_id, role,
                "PLANNER_PRESERVED-vs-PLANNER_ABLATED" if metric.metric_id == "planned-action-evaluation-pathway" else "agent-vs-control",
                "paired difference in pathway availability" if metric.metric_id == "planned-action-evaluation-pathway" else "difference in aggregate proxy",
                "REPORT_EFFECT_AND_UNCERTAINTY")
            for i, metric in enumerate(metrics))
        partition = Partition.HOLDOUT if intent in {StudyIntent.CONFIRMATORY, StudyIntent.REPLICATION} else Partition.EXPLORATORY_TEST
        partitions = tuple(SeedPartition(Partition(x["partition"]), str(x["seed_kind"]),
            tuple(int(v) for v in x["seeds"]), x.get("exception_reason")) for x in request.get("partitions", ())) or (
                SeedPartition(partition, "world", seeds.world_seeds), SeedPartition(partition, "agent", seeds.agent_seeds))
        controls = tuple(ControlCommitment(x.control_id, x.control_type, x.agent_id, x.contrast,
            content_hash(plain(x))) for x in experiment.controls)
        protocol = ProtocolSnapshot(experiment_record.version_id, experiment_record.scientific_hash,
            matrix_record.version_id, matrix_record.scientific_hash, experiment.scenario_id,
            experiment.scenario_hash, compiled_world.definition.content_hash,
            content_hash({"scenario": experiment.scenario_hash, "kind": "observation_contract"}),
            content_hash({"scenario": experiment.scenario_hash, "kind": "action_contract"}),
            content_hash({"scenario": experiment.scenario_hash, "manipulation_check": experiment.manipulation_check}),
            experiment.variant_ids, experiment.difficulty_fingerprint,
            experiment.agent_ids, {x: content_hash({"agent_id": x, "implementation": "registered"}) for x in experiment.agent_ids},
            controls, experiment.step_limit, experiment.repetitions,
            "SCENARIO_DECLARED", experiment.device_requirement)
        question = ScientificQuestionSnapshot(
            str(q.get("theory_snapshot_id", experiment.provenance.source_artifact)),
            str(q.get("theory_snapshot_hash", content_hash(experiment.provenance.source_artifact))),
            str(q.get("hypothesis_id", experiment.provenance.source_artifact)),
            str(q.get("hypothesis_hash", content_hash(experiment.provenance.source_artifact))),
            str(q.get("upstream_review_version_id", experiment_record.version_id)),
            str(q.get("upstream_review_hash", experiment_record.scientific_hash)),
            tuple(q.get("rival_hypotheses", ())), str(q.get("null_hypothesis", "No discriminating effect is observed.")),
            str(q.get("discriminating_prediction", "Report the preregistered contrast without automatic support claims.")),
            tuple(q.get("falsification_criteria", ("The preregistered contrast is absent or reversed.",))),
            tuple(q.get("interpretation_boundaries", ("Proxy outcomes do not establish a universal intelligence construct.",))))
        causal_design = CausalDesignCommitment(**{**causal, "mode": CausalMode(causal.get("mode", "DESCRIPTIVE_ONLY")),
            "identification_assumptions": tuple(causal.get("identification_assumptions", ())),
            "known_confounders": tuple(causal.get("known_confounders", ())),
            "rival_predictions": tuple(causal.get("rival_predictions", ()))})
        analysis_data = request.get("analysis") or {}
        self._reject_unknown(analysis_data, {"mode", "comparisons", "transformations", "grouping_variables",
            "aggregation", "effect_measure", "uncertainty_reporting", "statistical_method", "multiplicity_policy",
            "missing_data_policy", "sensitivity_analyses", "interpretation_boundary"}, "analysis")
        analysis = AnalysisPlan(str(analysis_data.get("mode", "DESCRIPTIVE_ONLY")),
            tuple(analysis_data.get("comparisons", (({"comparison_id": "PLANNER_PRESERVED-vs-PLANNER_ABLATED",
                "unit_of_analysis": "seed_pair", "pairing": "Pi preserved ↔ Pi ablated",
                "support_criterion": "all valid paired contrasts are positive",
                "contradiction_criterion": "any valid paired contrast is negative",
                "inconclusive_criterion": "a pair is NOT_EVALUABLE or contrast is zero"}
                if is_cl7 else {"comparison_id": "agent-vs-control", "paired_seeds": True}),))),
            tuple(analysis_data.get("transformations", ())),
            tuple(analysis_data.get("grouping_variables", ("seed_pair_id", "arm_id") if is_cl7 else ("condition_id", "variant_id"))),
            str(analysis_data.get("aggregation", "paired contrasts retained through analysis" if is_cl7 else "mean by condition with paired-seed detail")),
            str(analysis_data.get("effect_measure", "within-seed-pair preserved minus ablated proportion" if is_cl7 else "mean difference")),
            str(analysis_data.get("uncertainty_reporting", "interval and raw paired effects")),
            analysis_data.get("statistical_method"), str(analysis_data.get("multiplicity_policy", "NONE_EXPLICIT")),
            str(analysis_data.get("missing_data_policy", "NOT_EVALUABLE_INVALIDATES_PAIR_AND_IS_REPORTED" if is_cl7 else "REPORT_AND_MARK_INCOMPLETE")),
            tuple(analysis_data.get("sensitivity_analyses", ())),
            str(analysis_data.get("interpretation_boundary", "No automatic causal or evidential conclusion.")))
        total = int(matrix.get("total_trials", 0))
        estimate = self.observers.estimate(experiment.observer_profile, experiment.step_limit, total)
        requirement_data = request.get("environment_requirement") or {}
        self._reject_unknown(requirement_data, {"agent_device", "precision", "minimum_ram_bytes",
            "minimum_vram_bytes", "allow_dirty_tree"}, "environment_requirement")
        requirement = EnvironmentRequirement("cpu", str(requirement_data.get("agent_device", experiment.device_requirement)),
            "cpu", "cpu", str(requirement_data.get("precision", "float32")), True, "forbidden",
            requirement_data.get("minimum_ram_bytes"), requirement_data.get("minimum_vram_bytes"),
            bool(requirement_data.get("allow_dirty_tree", False)))
        return PreregistrationDraft(
            str(request.get("preregistration_id") or self.artifacts._identifier("preregistration")), intent, question,
            causal_design, protocol, metrics, endpoints, observer, seeds, partitions,
            RandomizationPlan("NONE", "1", None, (), (), (), tuple(str(x["trial_id"]) for x in matrix.get("cells", ()))),
            ReplicationPlan(experiment.world_seeds, tuple(f"rep-{x}" for x in experiment.world_seeds),
                total, tuple((*experiment.agent_ids, *(x.control_id for x in experiment.controls))), ("same pinned protocol",)),
            analysis, StoppingRule("FIXED_TRIAL_COUNT", total, matrix_record.scientific_hash, "1", {
                "exact_cell_count": 8 if is_cl7 else total,
                "exact_valid_terminal_attempts_required": 8 if is_cl7 else total,
                "technical_retry": "same cell only after nonterminal technical failure; maximum one retry",
                "scientific_rerun": "forbidden; an unfavorable valid terminal result is not retry-eligible",
                "terminal_execution_contract": ("terminal ScientificFrame", "sealed trace", "trace hash-chain valid",
                    "required metric events present", "no unresolved critical integrity error") if is_cl7 else (),
            }),
            ExclusionPolicy(tuple() if not is_cl7 else (
                ExclusionRule("TRACE_INTEGRITY_FAILURE", "sealed trace cannot be verified", "cell", "trace hash-chain invalid", "PRE_EXECUTION_POLICY"),
                ExclusionRule("PROTOCOL_MISMATCH", "committed identity/config differs", "cell", "identity or treatment signature mismatch", "PRE_EXECUTION_POLICY"),
                ExclusionRule("NONTERMINAL_EXECUTION", "terminal contract is unmet", "attempt", "attempt lacks terminal ScientificFrame", "PRE_EXECUTION_POLICY"),
                ExclusionRule("CORRUPTED_ARTIFACT", "required artifact cannot be decoded", "attempt", "artifact hash or codec verification fails", "PRE_EXECUTION_POLICY"),
            )), FailurePolicy(tuple(FailureRule(x, "HUMAN_REVIEW_REQUIRED") for x in
                ("PROCESS_CRASH", "TIMEOUT", "NUMERICAL_ERROR", "CORRUPTED_ARTIFACT", "INVALID_WORLD",
                 "INCOMPLETE_EPISODE", "HARDWARE_FAILURE", "INVALID_TRACE"))),
            StorageTracePolicy(("manifest", "analysis-input"), tuple(x.channel_id for x in channels),
                ("FINAL",), (), ("metric-summary",), "PRESERVE", estimate.classification, estimate.estimated_bytes),
            requirement, self._observed_environment(request.get("observed_environment")),
            self._software_manifest(request.get("software")), dict(request.get("ui_preferences") or {}))

    def _metric_commitment(self, metric_id: str, seeds: SeedCommitment) -> MetricCommitment:
        metric = self.metrics.get(metric_id)
        base = MetricCommitment(metric.metric_id, metric.schema_version, metric.implementation_ref,
            content_hash(metric.implementation_ref) if metric.implementation_ref else None,
            metric.construct, metric.proxy, metric.required_signals, metric.unit, metric.direction.value,
            metric.aggregation, metric.applicability, "ERROR", metric.limitations,
            metric.implementation_status.value, metric.construct_validation_status.value)
        if metric_id != "planned-action-evaluation-pathway":
            return base
        # Calibration is deliberately disjoint from the current confirmatory
        # matrix.  These are commitments, not a run and not a result.
        from terrario.lab.planning_trace_metric import specification, validate_construct
        report = validate_construct()
        calibration = {"world": (17,), "agent": (23,)}
        confirmatory = {"world": seeds.world_seeds, "agent": seeds.agent_seeds}
        return replace(base, specification_hash=specification()["metric_spec_hash"],
            calibration_report_id="CALIBRATION-PLANNING-TRACE-CONSTRUCT-V1",
            calibration_report_hash=report["calibration_report_hash"], calibration_seed_set=calibration,
            confirmatory_seed_set=confirmatory)

    def _readiness_for(self, draft: PreregistrationDraft) -> PreregistrationReadinessReport:
        matrix = self.artifacts.get_version(draft.protocol.trial_matrix_version_id).payload
        exposure = self._exposure_status(draft)
        findings = validate_preregistration(draft, matrix,
            upstream_review_approved=self.repository.approved_upstream(draft.protocol.experiment_draft_version_id),
            exposure_status=exposure)
        return PreregistrationReadinessReport(draft.preregistration_id, draft.scientific_hash,
            not any(x.blocking for x in findings), findings, int(matrix.get("total_trials", 0)),
            exposure, policy_snapshot_hash())

    def _exposure_status(self, draft: PreregistrationDraft) -> ExposureStatus:
        rows = [row for seed in draft.seeds.world_seeds for row in self.repository.exposures(draft.protocol.scenario_id, seed)]
        if not rows:
            return ExposureStatus.CONTAMINATION_REVIEW_REQUIRED
        root = self.repository.lock_row(draft.preregistration_id)
        if root and any(row.get("preregistration_root_hash") == root["bundle_root_hash"] for row in rows):
            return ExposureStatus.POSTLOCK_EXPOSED
        if all(row.get("exposure_kind") == ExposureKind.MANUAL_DECLARATION.value
               and row.get("context_type") == "VERIFIED_UNEXPOSED_INVENTORY" for row in rows):
            return ExposureStatus.UNEXPOSED
        return ExposureStatus.PREEXPOSED

    def _draft_from_record(self, record) -> PreregistrationDraft:
        payload = record.payload.get("draft", record.payload) if isinstance(record.payload, Mapping) else record.payload
        return preregistration_draft_from_payload(payload)

    def _view(self, record) -> Mapping[str, Any]:
        return {"preregistration_id": record.artifact_id, "version_id": record.version_id,
            "version_number": record.version_number, "scientific_hash": record.scientific_hash,
            "state": self.artifacts.current_state(record.version_id), "sealed": record.sealed,
            "classification": record.classification, "payload": record.payload,
            "locked": self.repository.is_locked(record.artifact_id), "etag": record.scientific_hash,
            "scientific_execution": False, "evidence_publication": False}

    @staticmethod
    def _report_payload(report: PreregistrationReadinessReport) -> Mapping[str, Any]:
        value = plain(report)
        value["findings"] = [{**plain(f), "blocking": f.blocking, "finding_hash": f.finding_hash} for f in report.findings]
        return value

    @staticmethod
    def _summary(draft: PreregistrationDraft) -> Mapping[str, Any]:
        return {"study_intent": draft.study_intent.value, "scenario": draft.protocol.scenario_id,
            "agents": draft.protocol.agent_ids, "controls": tuple(x.control_id for x in draft.protocol.controls),
            "primary_endpoints": tuple(x.endpoint_id for x in draft.endpoints if x.role is EndpointRole.PRIMARY),
            "world_seed_count": len(draft.seeds.world_seeds), "agent_seed_count": len(draft.seeds.agent_seeds),
            "automatic_approval": False}

    def _scientific_diff(self, current) -> Mapping[str, Any]:
        if not current.parent_version_id:
            return {"scientific": {"created": True}, "operational": {}, "metadata": {}, "ui_only": {}}
        parent = self.artifacts.get_version(current.parent_version_id)
        return {"scientific": {"parent_hash": parent.scientific_hash, "candidate_hash": current.scientific_hash,
            "changed": parent.scientific_hash != current.scientific_hash}, "operational": {}, "metadata": {}, "ui_only": {}}

    def _software_manifest(self, override: Any) -> SoftwareManifest:
        if override:
            return SoftwareManifest(**override)
        commit = self._git("rev-parse", "HEAD") or "UNKNOWN"
        status = self._git("status", "--porcelain")
        dirty = bool(status)
        diff_hash = content_hash(status) if dirty else None
        lock_files = [p for p in (self.root / "pyproject.toml", self.root / "requirements.txt") if p.exists()]
        dependency_hash = content_hash({str(p.relative_to(self.root)): p.read_text(errors="replace") for p in lock_files})
        return SoftwareManifest(commit, dirty, dependency_hash,
            {"preregistration": "v1", "experiment_draft": "v1", "trial_matrix": "v1"},
            {"metrics": "MetricRegistry", "observer": "ObserverRegistry"}, diff_hash)

    def _observed_environment(self, override: Any) -> ObservedEnvironment:
        if override:
            return ObservedEnvironment(**override)
        try:
            import torch
            torch_version, cuda_version = torch.__version__, torch.version.cuda
            available, count = torch.cuda.is_available(), torch.cuda.device_count()
        except Exception:
            torch_version, cuda_version, available, count = "UNAVAILABLE", None, False, 0
        return ObservedEnvironment(platform.platform(), platform.python_version(), torch_version,
            cuda_version, available, count, self.artifacts.now())

    def _git(self, *args: str) -> str:
        try:
            return subprocess.run(("git", *args), cwd=self.root, text=True,
                stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True, timeout=10).stdout.strip()
        except Exception:
            return ""

    @classmethod
    def _strict(cls, request: Mapping[str, Any], allowed: set[str]) -> None:
        forbidden = cls.FORBIDDEN_CLIENT_FIELDS & set(request)
        unknown = set(request) - allowed
        if forbidden or unknown:
            raise ValueError(f"invalid request fields; forbidden={sorted(forbidden)}, unknown={sorted(unknown)}")
        for required in ("experiment_draft_version_id", "trial_matrix_version_id"):
            if required not in request:
                raise ValueError(f"missing required field: {required}")

    @staticmethod
    def _reject_unknown(value: Mapping[str, Any], allowed: set[str], path: str) -> None:
        unknown = set(value) - allowed
        if unknown: raise ValueError(f"unknown fields at {path}: {sorted(unknown)}")
