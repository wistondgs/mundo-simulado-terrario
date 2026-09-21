"""Typed scientific preregistration contracts.

These contracts describe commitments only. Nothing in this module can execute a
trial or publish evidence.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping

from terrario.lab.persistence.canonical import content_hash, plain
from terrario.lab.preregistration.gate_manifest import GateManifest, manifest_from_payload

SCHEMA_VERSION = "terrario.lab.preregistration/v1"
CANONICALIZATION_PROFILE = "terrario-canonical-json-v1"


class StudyIntent(StrEnum):
    EXPLORATORY = "EXPLORATORY"
    CONFIRMATORY = "CONFIRMATORY"
    REPLICATION = "REPLICATION"
    ABLATION = "ABLATION"
    STRESS_TEST = "STRESS_TEST"
    METHOD_VALIDATION = "METHOD_VALIDATION"


class CausalMode(StrEnum):
    CAUSAL = "CAUSAL"
    DESCRIPTIVE_ONLY = "DESCRIPTIVE_ONLY"


class EndpointRole(StrEnum):
    PRIMARY = "PRIMARY"
    SECONDARY = "SECONDARY"
    DIAGNOSTIC = "DIAGNOSTIC"
    EXPLORATORY = "EXPLORATORY"


class Partition(StrEnum):
    TRAIN = "TRAIN"
    DEVELOPMENT = "DEVELOPMENT"
    EXPLORATORY_TEST = "EXPLORATORY_TEST"
    CONFIRMATORY_TEST = "CONFIRMATORY_TEST"
    TRANSFER = "TRANSFER"
    HOLDOUT = "HOLDOUT"


class PreregistrationState(StrEnum):
    DRAFT = "DRAFT"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    REVIEW_IN_PROGRESS = "REVIEW_IN_PROGRESS"
    REVIEWED = "REVIEWED"
    PREREGISTERED_LOCKED = "PREREGISTERED_LOCKED"
    SUPERSEDED = "SUPERSEDED"
    WITHDRAWN = "WITHDRAWN"


class ReviewDecisionValue(StrEnum):
    APPROVE_PREREGISTRATION = "APPROVE_PREREGISTRATION"
    APPROVE_FOR_EXPERIMENT_DESIGN = "APPROVE_FOR_EXPERIMENT_DESIGN"
    REQUEST_CHANGES = "REQUEST_CHANGES"
    REJECT = "REJECT"


class FindingSeverity(StrEnum):
    STRUCTURAL_ERROR = "STRUCTURAL_ERROR"
    SCHEMA_ERROR = "SCHEMA_ERROR"
    INTEGRITY_ERROR = "INTEGRITY_ERROR"
    REFERENCE_ERROR = "REFERENCE_ERROR"
    SCIENTIFIC_WARNING = "SCIENTIFIC_WARNING"
    EXPOSURE_WARNING = "EXPOSURE_WARNING"
    RESOURCE_WARNING = "RESOURCE_WARNING"

    @property
    def blocking(self) -> bool:
        return self in {
            self.STRUCTURAL_ERROR, self.SCHEMA_ERROR, self.INTEGRITY_ERROR,
            self.REFERENCE_ERROR,
        }


class ExposureKind(StrEnum):
    PREVIEWED = "PREVIEWED"
    SANDBOXED = "SANDBOXED"
    INSPECTED = "INSPECTED"
    ANALYZED = "ANALYZED"
    MANUAL_DECLARATION = "MANUAL_DECLARATION"


class ExposureStatus(StrEnum):
    UNEXPOSED = "UNEXPOSED"
    PREEXPOSED = "PREEXPOSED"
    POSTLOCK_EXPOSED = "POSTLOCK_EXPOSED"
    CONTAMINATION_REVIEW_REQUIRED = "CONTAMINATION_REVIEW_REQUIRED"


class DeviationType(StrEnum):
    PROTOCOL_DEVIATION = "PROTOCOL_DEVIATION"
    SEED_DEVIATION = "SEED_DEVIATION"
    METRIC_DEVIATION = "METRIC_DEVIATION"
    OBSERVER_DEVIATION = "OBSERVER_DEVIATION"
    ANALYSIS_DEVIATION = "ANALYSIS_DEVIATION"
    ENVIRONMENT_DEVIATION = "ENVIRONMENT_DEVIATION"
    EXCLUSION_DEVIATION = "EXCLUSION_DEVIATION"
    FAILURE_HANDLING_DEVIATION = "FAILURE_HANDLING_DEVIATION"


class PreregistrationError(RuntimeError):
    code = "PREREGISTRATION_ERROR"


class PreregistrationNotReady(PreregistrationError):
    code = "PREREGISTRATION_NOT_READY"


class LockedPreregistration(PreregistrationError):
    code = "LOCKED_ARTIFACT"


class StalePreregistration(PreregistrationError):
    code = "STALE_ARTIFACT_HASH"


class InvalidTransition(PreregistrationError):
    code = "INVALID_PREREGISTRATION_TRANSITION"


class BundleIntegrityError(PreregistrationError):
    code = "BUNDLE_INTEGRITY_ERROR"


def frozen_mapping(value: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return MappingProxyType(dict(value or {}))


@dataclass(frozen=True)
class ScientificQuestionSnapshot:
    theory_snapshot_id: str
    theory_snapshot_hash: str
    hypothesis_id: str
    hypothesis_hash: str
    upstream_review_version_id: str
    upstream_review_hash: str
    rival_hypotheses: tuple[str, ...]
    null_hypothesis: str
    discriminating_prediction: str
    falsification_criteria: tuple[str, ...]
    interpretation_boundaries: tuple[str, ...] = ()
    schema_version: str = f"{SCHEMA_VERSION}/scientific-question"


@dataclass(frozen=True)
class CausalDesignCommitment:
    mode: CausalMode
    manipulated_variable: str | None = None
    intervention: str | None = None
    comparison: str | None = None
    control: str | None = None
    outcome: str | None = None
    estimand: str | None = None
    manipulation_check: str | None = None
    identification_assumptions: tuple[str, ...] = ()
    known_confounders: tuple[str, ...] = ()
    rival_predictions: tuple[str, ...] = ()
    schema_version: str = f"{SCHEMA_VERSION}/causal-design"


@dataclass(frozen=True)
class ControlCommitment:
    control_id: str
    control_type: str
    agent_id: str
    contrast: str
    source_hash: str


@dataclass(frozen=True)
class MetricCommitment:
    metric_id: str
    definition_version: str
    implementation_identity: str | None
    implementation_hash: str | None
    construct: str
    proxy: str
    required_signals: tuple[str, ...]
    unit: str
    directionality: str
    aggregation: str
    applicable_population: tuple[str, ...]
    missing_data_behavior: str
    limitations: tuple[str, ...]
    implementation_status: str
    validation_status: str
    specification_hash: str | None = None
    #: The canonical instrument this metric is frozen to, as an
    #: `instrument_registry.InstrumentRef` record.  A name is not enough: the
    #: whole point of freezing is that the ruler cannot be revised after the
    #: protocol locks without the change being visible as drift.
    instrument_ref: Mapping[str, Any] | None = None
    calibration_report_id: str | None = None
    calibration_report_hash: str | None = None
    calibration_seed_set: Mapping[str, tuple[int, ...]] = field(default_factory=dict)
    confirmatory_seed_set: Mapping[str, tuple[int, ...]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        def freeze(value: Mapping[str, tuple[int, ...]]) -> Mapping[str, tuple[int, ...]]:
            return MappingProxyType({str(key): tuple(int(seed) for seed in seeds) for key, seeds in value.items()})
        object.__setattr__(self, "calibration_seed_set", freeze(self.calibration_seed_set))
        object.__setattr__(self, "confirmatory_seed_set", freeze(self.confirmatory_seed_set))


@dataclass(frozen=True)
class EndpointCommitment:
    endpoint_id: str
    metric_id: str
    role: EndpointRole
    comparison_id: str
    estimand: str
    decision_rule: str


@dataclass(frozen=True)
class ObserverChannelCommitment:
    channel_id: str
    schema: str
    frequency: int
    separation_class: str
    availability: str


@dataclass(frozen=True)
class ObserverCommitment:
    profile_id: str
    profile_schema_version: str
    channels: tuple[ObserverChannelCommitment, ...]
    trace_policy: str
    forensic_windows: tuple[Mapping[str, Any], ...]
    retention: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "forensic_windows", tuple(frozen_mapping(x) for x in self.forensic_windows))


@dataclass(frozen=True)
class SeedCommitment:
    world_seeds: tuple[int, ...]
    agent_seeds: tuple[int, ...]
    randomization_seeds: tuple[int, ...]
    replacement_seeds: tuple[int, ...]
    world_seed_hash: str
    agent_seed_hash: str
    randomization_seed_hash: str
    replacement_seed_hash: str

    @classmethod
    def materialize(
        cls, world: tuple[int, ...], agent: tuple[int, ...],
        randomization: tuple[int, ...] = (), replacement: tuple[int, ...] = (),
    ) -> "SeedCommitment":
        return cls(world, agent, randomization, replacement, content_hash(world),
                   content_hash(agent), content_hash(randomization), content_hash(replacement))


@dataclass(frozen=True)
class SeedPartition:
    partition: Partition
    seed_kind: str
    seeds: tuple[int, ...]
    exception_reason: str | None = None


@dataclass(frozen=True)
class RandomizationPlan:
    algorithm: str
    algorithm_version: str
    randomization_seed: int | None
    blocks: tuple[str, ...]
    strata: tuple[str, ...]
    constraints: tuple[str, ...]
    materialized_order: tuple[str, ...]


@dataclass(frozen=True)
class ReplicationPlan:
    independent_seeds: tuple[int, ...]
    replication_groups: tuple[str, ...]
    minimum_valid_trials: int
    conditions: tuple[str, ...]
    expected_invariances: tuple[str, ...]


@dataclass(frozen=True)
class AnalysisPlan:
    mode: str
    comparisons: tuple[Mapping[str, Any], ...]
    transformations: tuple[Mapping[str, Any], ...]
    grouping_variables: tuple[str, ...]
    aggregation: str
    effect_measure: str
    uncertainty_reporting: str
    statistical_method: str | None
    multiplicity_policy: str
    missing_data_policy: str
    sensitivity_analyses: tuple[str, ...]
    interpretation_boundary: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "comparisons", tuple(frozen_mapping(x) for x in self.comparisons))
        object.__setattr__(self, "transformations", tuple(frozen_mapping(x) for x in self.transformations))


@dataclass(frozen=True)
class StoppingRule:
    rule_type: str
    fixed_trial_count: int | None
    fixed_seed_hash: str | None
    rule_version: str
    parameters: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "parameters", frozen_mapping(self.parameters))


@dataclass(frozen=True)
class ExclusionRule:
    rule_id: str
    reason: str
    target: str
    objective_condition: str
    scope: str


@dataclass(frozen=True)
class ExclusionPolicy:
    rules: tuple[ExclusionRule, ...]
    post_hoc_disposition: str = "POST_HOC_DEVIATION"


@dataclass(frozen=True)
class FailureRule:
    failure_type: str
    disposition: str


@dataclass(frozen=True)
class FailurePolicy:
    rules: tuple[FailureRule, ...]


@dataclass(frozen=True)
class StorageTracePolicy:
    required_artifacts: tuple[str, ...]
    required_traces: tuple[str, ...]
    checkpoints: tuple[str, ...]
    forensic_windows: tuple[str, ...]
    summary_outputs: tuple[str, ...]
    retention: str
    estimate_classification: str
    estimated_bytes: int | None


@dataclass(frozen=True)
class EnvironmentRequirement:
    world_device: str
    agent_device: str
    observer_device: str
    analysis_device: str
    precision: str
    deterministic_algorithms: bool
    fallback_policy: str
    minimum_ram_bytes: int | None = None
    minimum_vram_bytes: int | None = None
    allow_dirty_tree: bool = False


@dataclass(frozen=True)
class ObservedEnvironment:
    operating_system: str
    python_version: str
    torch_version: str
    cuda_compiled_version: str | None
    cuda_available: bool
    device_count: int
    captured_at: str


@dataclass(frozen=True)
class SoftwareManifest:
    git_commit: str
    dirty_tree: bool
    dependency_hash: str
    schema_versions: Mapping[str, str]
    implementation_identities: Mapping[str, str]
    dirty_diff_hash: str | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "schema_versions", frozen_mapping(self.schema_versions))
        object.__setattr__(self, "implementation_identities", frozen_mapping(self.implementation_identities))


@dataclass(frozen=True)
class ProtocolSnapshot:
    experiment_draft_version_id: str
    experiment_draft_hash: str
    trial_matrix_version_id: str
    trial_matrix_hash: str
    scenario_id: str
    scenario_hash: str
    world_definition_hash: str
    observation_contract_hash: str
    action_contract_hash: str
    interventions_hash: str
    variant_ids: tuple[str, ...]
    difficulty_fingerprint: str
    agent_ids: tuple[str, ...]
    agent_identity_hashes: Mapping[str, str]
    controls: tuple[ControlCommitment, ...]
    step_limit: int
    repetitions: int
    termination_semantics: str
    device_requirement: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "agent_identity_hashes", frozen_mapping(self.agent_identity_hashes))


@dataclass(frozen=True)
class PreregistrationDraft:
    preregistration_id: str
    study_intent: StudyIntent
    scientific_question: ScientificQuestionSnapshot
    causal_design: CausalDesignCommitment
    protocol: ProtocolSnapshot
    metrics: tuple[MetricCommitment, ...]
    endpoints: tuple[EndpointCommitment, ...]
    observer: ObserverCommitment
    seeds: SeedCommitment
    partitions: tuple[SeedPartition, ...]
    randomization: RandomizationPlan
    replication: ReplicationPlan
    analysis: AnalysisPlan
    stopping: StoppingRule
    exclusions: ExclusionPolicy
    failures: FailurePolicy
    storage: StorageTracePolicy
    environment_requirement: EnvironmentRequirement
    observed_environment: ObservedEnvironment
    software: SoftwareManifest
    ui_preferences: Mapping[str, Any] = field(default_factory=dict)
    schema_version: str = SCHEMA_VERSION
    #: What each gate certifies, frozen before the run that evaluates it.
    #: Optional because the ten sealed roles predate it and 141 bundles are
    #: already committed without one; a draft that carries it seals a v2 bundle.
    #: Declared LAST on purpose: `PreregistrationService._assemble` constructs
    #: this dataclass positionally, so inserting a field anywhere earlier
    #: silently shifts every argument after it.
    gates: GateManifest | None = None

    def __post_init__(self) -> None:
        object.__setattr__(self, "ui_preferences", frozen_mapping(self.ui_preferences))
        # Accept a stored payload as well as a manifest, and rebuild it through
        # the codec that recomputes identity rather than trusting the stored
        # hash.  An empty mapping means "no gates", not "a manifest of none".
        if isinstance(self.gates, Mapping):
            object.__setattr__(self, "gates",
                               manifest_from_payload(self.gates) if self.gates else None)

    def scientific_payload(self) -> Mapping[str, Any]:
        value = plain(self)
        value.pop("preregistration_id", None)
        value.pop("ui_preferences", None)
        if value.get("gates") is None:
            # Absent rather than null, so a draft without gates hashes exactly as
            # it did before this field existed.  A new optional field must not
            # move the scientific identity of everything already sealed.
            value.pop("gates", None)
        return value

    @property
    def scientific_hash(self) -> str:
        return content_hash(self.scientific_payload())


@dataclass(frozen=True)
class ComponentDescriptor:
    role: str
    ordinal: int
    schema_version: str
    content_sha256: str
    cas_sha256: str
    source_artifact_version_id: str | None = None
    source_scientific_hash: str | None = None


@dataclass(frozen=True)
class PreregistrationBundle:
    preregistration_id: str
    bundle_version_id: str
    bundle_root_hash: str
    root_manifest: Mapping[str, Any]
    components: tuple[ComponentDescriptor, ...]
    schema_version: str = f"{SCHEMA_VERSION}/bundle"

    def __post_init__(self) -> None:
        object.__setattr__(self, "root_manifest", frozen_mapping(self.root_manifest))


@dataclass(frozen=True)
class ValidationFinding:
    rule_id: str
    rule_version: str
    severity: FindingSeverity
    path: str
    description: str
    source: str
    details: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "details", frozen_mapping(self.details))

    @property
    def blocking(self) -> bool:
        return self.severity.blocking

    @property
    def finding_hash(self) -> str:
        return content_hash(plain(self))


@dataclass(frozen=True)
class PreregistrationReadinessReport:
    preregistration_id: str
    candidate_hash: str
    complete: bool
    findings: tuple[ValidationFinding, ...]
    trial_count: int
    exposure_status: ExposureStatus
    policy_snapshot_hash: str
    schema_version: str = f"{SCHEMA_VERSION}/readiness"


@dataclass(frozen=True)
class PreregistrationReviewPackage:
    preregistration_id: str
    candidate_root_hash: str
    review_package_hash: str
    summary: Mapping[str, Any]
    readiness: PreregistrationReadinessReport
    scientific_diff: Mapping[str, Any]
    provenance: Mapping[str, Any]
    schema_version: str = f"{SCHEMA_VERSION}/review-package"

    def __post_init__(self) -> None:
        object.__setattr__(self, "summary", frozen_mapping(self.summary))
        object.__setattr__(self, "scientific_diff", frozen_mapping(self.scientific_diff))
        object.__setattr__(self, "provenance", frozen_mapping(self.provenance))


@dataclass(frozen=True)
class PreregistrationAttestation:
    attestation_id: str
    preregistration_id: str
    bundle_version_id: str
    bundle_root_hash: str
    review_decision_id: str
    review_package_hash: str
    actor_id: str
    created_at: str
    reason: str
    accepted_warning_hashes: tuple[str, ...]
    audit_event_hash: str
    signature_status: str = "UNSIGNED_LOCAL_ATTESTATION"

    @property
    def attestation_hash(self) -> str:
        return content_hash(plain(self))


@dataclass(frozen=True)
class ReviewDecision:
    decision_id: str
    review_id: str
    artifact_version_id: str
    artifact_hash: str
    decision: ReviewDecisionValue
    actor_id: str
    reason: str
    accepted_warning_hashes: tuple[str, ...]
    created_at: str


@dataclass(frozen=True)
class ExposureRecord:
    exposure_id: str
    scenario_id: str
    scenario_hash: str
    world_seed: int
    exposure_kind: ExposureKind
    actor_id: str
    occurred_at: str
    context_type: str
    context_id: str
    preregistration_root_hash: str | None
    previous_event_hash: str | None
    event_hash: str


@dataclass(frozen=True)
class AmendmentRecord:
    amendment_id: str
    preregistration_id: str
    parent_root_hash: str
    change_class: str
    reason: str
    actor_id: str
    created_at: str
    child_preregistration_id: str | None
    delta: Mapping[str, Any]

    def __post_init__(self) -> None:
        object.__setattr__(self, "delta", frozen_mapping(self.delta))


@dataclass(frozen=True)
class DeviationRecord:
    deviation_id: str
    preregistration_id: str
    preregistration_root_hash: str
    deviation_type: DeviationType
    affected_component: str
    planned_behavior: str
    actual_behavior: str
    reason: str
    scientific_impact_assessment: str
    disposition: str
    actor_id: str
    created_at: str


@dataclass(frozen=True)
class PreregistrationVerificationReport:
    preregistration_id: str
    status: str
    schema_valid: bool
    component_hashes_valid: bool
    root_hash_valid: bool
    cas_valid: bool
    review_binding_valid: bool
    immutable_status_valid: bool
    audit_chain_valid: bool
    parent_chain_valid: bool
    provenance_available: bool
    failures: tuple[str, ...]
    warnings: tuple[str, ...]


ALLOWED_TRANSITIONS: Mapping[PreregistrationState, frozenset[PreregistrationState]] = {
    PreregistrationState.DRAFT: frozenset({PreregistrationState.READY_FOR_REVIEW}),
    PreregistrationState.READY_FOR_REVIEW: frozenset({PreregistrationState.REVIEW_IN_PROGRESS}),
    PreregistrationState.REVIEW_IN_PROGRESS: frozenset({PreregistrationState.REVIEWED}),
    PreregistrationState.REVIEWED: frozenset({PreregistrationState.DRAFT, PreregistrationState.PREREGISTERED_LOCKED}),
    PreregistrationState.PREREGISTERED_LOCKED: frozenset({PreregistrationState.SUPERSEDED, PreregistrationState.WITHDRAWN}),
    PreregistrationState.SUPERSEDED: frozenset(),
    PreregistrationState.WITHDRAWN: frozenset(),
}


def assert_transition(current: PreregistrationState, target: PreregistrationState) -> None:
    if target not in ALLOWED_TRANSITIONS[current]:
        raise InvalidTransition(f"{current.value} -> {target.value} is prohibited")
