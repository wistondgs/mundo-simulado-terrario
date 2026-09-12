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
    DeviationRecord, DeviationType, EndpointCommitment, EndpointRole,
    EnvironmentRequirement, ExclusionPolicy, ExposureKind, ExposureStatus,
    FailurePolicy, FailureRule, MetricCommitment, ObservedEnvironment,
    ObserverChannelCommitment, ObserverCommitment, Partition,
    PreregistrationDraft, PreregistrationNotReady, PreregistrationReadinessReport, ProtocolSnapshot,
    PreregistrationState, RandomizationPlan, ReplicationPlan, ReviewDecisionValue,
    SeedCommitment, SeedPartition, ScientificQuestionSnapshot, SoftwareManifest,
    StoppingRule, StorageTracePolicy, StudyIntent, assert_transition,
)
from terrario.lab.preregistration.repository import PreregistrationRepository
from terrario.lab.preregistration.validation import policy_snapshot_hash, validate_preregistration


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
        current = self.artifacts.current(preregistration_id, "Preregistration")
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
        if not root:
            failures.append("BUNDLE_NOT_PREPARED")
        else:
            valid, commitment_failures = self.commitments.verify(root)
            failures.extend(commitment_failures)
            if content_hash(root) != current.scientific_hash:
                failures.append("ROOT_HASH_MISMATCH")
        if not self.repository.verify_audit_chain(preregistration_id):
            failures.append("AUDIT_CHAIN_INVALID")
        locked = self.repository.is_locked(preregistration_id)
        if locked and self.repository.attestation(preregistration_id) is None:
            failures.append("ATTESTATION_MISSING")
        return {"preregistration_id": preregistration_id, "version_id": current.version_id,
                "root": current.scientific_hash, "valid": not failures,
                "failures": failures, "locked": locked,
                "attestation": self.repository.attestation(preregistration_id),
                "scientific_execution": False, "evidence_publication": False}

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
        return self.repository.record_exposure(scenario_id, scenario_hash, world_seed,
            ExposureKind(kind).value, actor_id, context_type, context_id, root)

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
        value = {"preregistration_id": preregistration_id, "parent_root_hash": parent.scientific_hash,
                 **plain(payload), "recorded_by": actor_id, "recorded_at": self.artifacts.now(),
                 "automatic_protocol_change": False}
        stored = self.artifacts.create_artifact(kind, value, f"terrario.lab.{kind.casefold()}/v1",
            classification="POST_LOCK_GOVERNANCE_RECORD", created_by=actor_id,
            reason=str(payload.get("reason", kind)), initial_state="RECORDED", sealed=True)
        self.repository.append_chain(preregistration_id, kind.upper(), {"record_id": stored.artifact_id,
            "record_hash": stored.scientific_hash}, actor_id)
        return self._view(stored)

    def export(self, preregistration_id: str) -> Mapping[str, Any]:
        current = self.artifacts.current(preregistration_id)
        base = self.artifacts.export_bundle(current.version_id)
        root = current.payload.get("root_manifest", {})
        components = {str(x["cas_sha256"]): json.loads(self.artifacts.blobs.read(str(x["cas_sha256"])))
                      for x in root.get("components", ())}
        envelope = {"schema_version": "terrario.preregistration-portable/v1", "artifact_bundle": base,
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
        record = self.artifacts.import_bundle(bundle["artifact_bundle"], actor_id)
        return {**self._view(record), "imported_attestation_trusted": False,
                "requires_local_review_for_lock": True, "portable_hash": bundle["portable_hash"]}

    def review_requests(self) -> tuple[Mapping[str, Any], ...]:
        with self.artifacts._connect() as connection:
            rows = connection.execute("SELECT * FROM review_requests ORDER BY created_at,review_id").fetchall()
            return tuple(dict(x) for x in rows)

    def _assemble(self, request: Mapping[str, Any]) -> PreregistrationDraft:
        experiment_record = self.artifacts.get_version(str(request["experiment_draft_version_id"]))
        matrix_record = self.artifacts.get_version(str(request["trial_matrix_version_id"]))
        if experiment_record.kind != "ExperimentDraft" or matrix_record.kind != "TrialMatrix":
            raise ValueError("source versions must be ExperimentDraft and TrialMatrix")
        experiment = experiment_draft_from_payload(experiment_record.payload)
        matrix = matrix_record.payload
        if matrix.get("draft_hash") != experiment_record.scientific_hash:
            raise ProvenanceConflict("TrialMatrix does not belong to the exact ExperimentDraft")
        intent = StudyIntent(request.get("study_intent", "EXPLORATORY"))
        q = request.get("scientific_question") or {}
        causal = request.get("causal_design") or {"mode": "DESCRIPTIVE_ONLY"}
        metrics = tuple(self._metric_commitment(x) for x in experiment.metric_ids)
        role = EndpointRole.EXPLORATORY if intent is StudyIntent.EXPLORATORY else EndpointRole.PRIMARY
        endpoints = tuple(EndpointCommitment(**{**x, "role": EndpointRole(x["role"])}) for x in request.get("endpoints", ())) or tuple(
            EndpointCommitment(f"endpoint-{i+1}", metric.metric_id, role, "agent-vs-control",
                "difference in aggregate proxy", "REPORT_EFFECT_AND_UNCERTAINTY")
            for i, metric in enumerate(metrics))
        channels = self.observers.expand(experiment.observer_profile)
        observer = ObserverCommitment(experiment.observer_profile, self.observers.profile(experiment.observer_profile).schema_version,
            tuple(ObserverChannelCommitment(x.channel_id, x.payload_schema, x.frequency,
                x.separation_class.value, x.availability) for x in channels), "FROZEN_PROFILE", (), "PROJECT_POLICY")
        seeds = SeedCommitment.materialize(experiment.world_seeds, experiment.agent_seeds,
            tuple(int(x) for x in (request.get("randomization") or {}).get("seeds", ())),
            tuple(int(x) for x in (request.get("randomization") or {}).get("replacement_seeds", ())))
        partition = Partition.HOLDOUT if intent in {StudyIntent.CONFIRMATORY, StudyIntent.REPLICATION} else Partition.EXPLORATORY_TEST
        partitions = tuple(SeedPartition(Partition(x["partition"]), str(x["seed_kind"]),
            tuple(int(v) for v in x["seeds"]), x.get("exception_reason")) for x in request.get("partitions", ())) or (
                SeedPartition(partition, "world", seeds.world_seeds), SeedPartition(partition, "agent", seeds.agent_seeds))
        controls = tuple(ControlCommitment(x.control_id, x.control_type, x.agent_id, x.contrast,
            content_hash(plain(x))) for x in experiment.controls)
        protocol = ProtocolSnapshot(experiment_record.version_id, experiment_record.scientific_hash,
            matrix_record.version_id, matrix_record.scientific_hash, experiment.scenario_id,
            experiment.scenario_hash, experiment.variant_ids, experiment.difficulty_fingerprint,
            experiment.agent_ids, controls, experiment.step_limit, experiment.repetitions,
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
        analysis = AnalysisPlan(str(analysis_data.get("mode", "DESCRIPTIVE_ONLY")),
            tuple(analysis_data.get("comparisons", ({"comparison_id": "agent-vs-control", "paired_seeds": True},))),
            str(analysis_data.get("effect_measure", "mean difference")),
            str(analysis_data.get("uncertainty_reporting", "interval and raw paired effects")),
            analysis_data.get("statistical_method"), str(analysis_data.get("multiplicity_policy", "NONE_EXPLICIT")),
            str(analysis_data.get("missing_data_policy", "REPORT_AND_MARK_INCOMPLETE")),
            tuple(analysis_data.get("sensitivity_analyses", ())),
            str(analysis_data.get("interpretation_boundary", "No automatic causal or evidential conclusion.")))
        total = int(matrix.get("total_trials", 0))
        estimate = self.observers.estimate(experiment.observer_profile, experiment.step_limit, total)
        requirement_data = request.get("environment_requirement") or {}
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
            analysis, StoppingRule("FIXED_TRIAL_COUNT", total, matrix_record.scientific_hash, "1", {}),
            ExclusionPolicy(()), FailurePolicy(tuple(FailureRule(x, "HUMAN_REVIEW_REQUIRED") for x in
                ("PROCESS_CRASH", "NUMERICAL_ERROR", "HARDWARE_FAILURE", "TIMEOUT", "INVALID_TRACE", "CORRUPTED_OUTPUT"))),
            StorageTracePolicy(("manifest", "analysis-input"), tuple(x.channel_id for x in channels),
                ("FINAL",), (), ("metric-summary",), "PRESERVE", estimate.classification, estimate.estimated_bytes),
            requirement, self._observed_environment(request.get("observed_environment")),
            self._software_manifest(request.get("software")), dict(request.get("ui_preferences") or {}))

    def _metric_commitment(self, metric_id: str) -> MetricCommitment:
        metric = self.metrics.get(metric_id)
        return MetricCommitment(metric.metric_id, metric.schema_version, metric.implementation_ref,
            content_hash(metric.implementation_ref) if metric.implementation_ref else None,
            metric.construct, metric.proxy, metric.required_signals, metric.unit, metric.direction.value,
            metric.aggregation, metric.applicability, "ERROR", metric.limitations,
            metric.implementation_status.value, metric.construct_validation_status.value)

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
