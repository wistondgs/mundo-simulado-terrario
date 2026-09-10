"""Review-bounded ExperimentDraft and non-executing TrialMatrix models."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from enum import StrEnum
from itertools import product
from types import MappingProxyType
from typing import Any, Mapping

from terrario.lab.metrics_observer import MetricRegistry, ObserverRegistry
from terrario.lab.capabilities import assess_compatibility
from terrario.lab.world_contracts import ScenarioDefinition, canonical_json, scientific_hash

SCHEMA_VERSION = "terrario.lab.experiment-draft/v1"


class DraftState(StrEnum):
    DRAFT = "DRAFT"
    INCOMPLETE = "INCOMPLETE"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    REVIEW_BLOCKED = "REVIEW_BLOCKED"
    PREREGISTRATION_READY = "PREREGISTRATION_READY"


@dataclass(frozen=True)
class ControlCondition:
    control_id: str
    control_type: str
    agent_id: str
    contrast: str
    availability: str = "AVAILABLE"


@dataclass(frozen=True)
class DraftProvenance:
    creator: str
    reason: str
    source_artifact: str
    source_review_state: str
    parent_id: str | None = None
    parent_hash: str | None = None
    changed_fields: tuple[str, ...] = ()
    created_at: str = "RUNTIME"


@dataclass(frozen=True)
class ExperimentDraft:
    draft_id: str
    schema_version: str
    state: DraftState
    scenario_id: str
    scenario_hash: str
    variant_ids: tuple[str, ...]
    difficulty_fingerprint: str
    agent_ids: tuple[str, ...]
    controls: tuple[ControlCondition, ...]
    metric_ids: tuple[str, ...]
    observer_profile: str
    observer_channels: tuple[str, ...]
    world_seeds: tuple[int, ...]
    agent_seeds: tuple[int, ...]
    repetitions: int
    step_limit: int
    device_requirement: str
    required_ground_truth: tuple[str, ...]
    available_ground_truth: tuple[str, ...]
    available_signals: tuple[str, ...]
    manipulation_check: str | None
    transfer_phase: Mapping[str, Any] | None
    provenance: DraftProvenance
    ui_preferences: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        object.__setattr__(self, "ui_preferences", MappingProxyType(dict(self.ui_preferences)))
        if self.transfer_phase is not None:
            object.__setattr__(self, "transfer_phase", MappingProxyType(dict(self.transfer_phase)))

    def scientific_payload(self) -> dict[str, Any]:
        data = {
            "schema_version": self.schema_version, "scenario_id": self.scenario_id,
            "scenario_hash": self.scenario_hash, "variant_ids": self.variant_ids,
            "difficulty_fingerprint": self.difficulty_fingerprint, "agent_ids": self.agent_ids,
            "controls": self.controls, "metric_ids": self.metric_ids,
            "observer_profile": self.observer_profile, "observer_channels": self.observer_channels,
            "world_seeds": self.world_seeds, "agent_seeds": self.agent_seeds,
            "repetitions": self.repetitions, "step_limit": self.step_limit,
            "device_requirement": self.device_requirement,
            "required_ground_truth": self.required_ground_truth,
            "available_ground_truth": self.available_ground_truth,
            "available_signals": self.available_signals,
            "manipulation_check": self.manipulation_check, "transfer_phase": self.transfer_phase,
        }
        return data

    @property
    def content_hash(self) -> str:
        return scientific_hash(self.scientific_payload())

    def derive(self, reason: str, **changes) -> "ExperimentDraft":
        editable = {f.name for f in self.__dataclass_fields__.values()} - {"draft_id", "provenance"}
        forbidden = set(changes) - editable
        if forbidden: raise ValueError(f"unsupported draft fields: {sorted(forbidden)}")
        candidate = replace(self, **changes)
        changed = tuple(sorted(k for k in changes if canonical_json(getattr(self, k)) != canonical_json(getattr(candidate, k))))
        provenance = DraftProvenance("lab-user", reason, self.provenance.source_artifact,
            self.provenance.source_review_state, self.draft_id, self.content_hash, changed)
        return replace(candidate, draft_id=f"{self.draft_id}.next", provenance=provenance)


@dataclass(frozen=True)
class DraftFinding:
    category: str
    code: str
    path: str
    message: str
    blocking: bool
    rule_source: str


@dataclass(frozen=True)
class TrialIntent:
    trial_id: str
    variant_id: str
    condition_id: str
    agent_id: str
    world_seed: int
    agent_seed: int
    repetition: int
    status: str
    blockers: tuple[str, ...]
    metric_ids: tuple[str, ...]
    observer_profile: str
    expected_classification: str = "FUTURE_SCIENTIFIC_REVIEW_REQUIRED"


@dataclass(frozen=True)
class TrialMatrix:
    draft_hash: str
    variants: int
    agent_control_conditions: int
    world_seeds: int
    agent_seeds: int
    repetitions: int
    total_trials: int
    cells: tuple[TrialIntent, ...]
    warnings: tuple[str, ...]
    execution_performed: bool = False


def validate_draft(draft: ExperimentDraft, scenario: ScenarioDefinition,
                   metric_registry: MetricRegistry, observer_registry: ObserverRegistry) -> tuple[DraftFinding, ...]:
    rows: list[DraftFinding] = []
    def add(category, code, path, message, blocking, source):
        rows.append(DraftFinding(category, code, path, message, blocking, source))
    if draft.schema_version != SCHEMA_VERSION: add("STRUCTURAL", "INCOMPATIBLE_SCHEMA", "schema_version", "unsupported schema", True, SCHEMA_VERSION)
    if not draft.scenario_id or draft.scenario_hash != scenario.content_hash: add("STRUCTURAL", "MISSING_REFERENCE", "scenario", "scenario reference/hash mismatch", True, "ScenarioDefinition.content_hash")
    if not draft.agent_ids: add("STRUCTURAL", "MISSING_REFERENCE", "agent_ids", "at least one agent is required", True, "ExperimentDraft")
    for agent_id in draft.agent_ids:
        if agent_id.upper().split("_")[0] not in {"A0", "A1", "A2", "A3", "A4"}:
            add("COMPATIBILITY", "INVALID_INTERFACE", f"agent.{agent_id}", "agent has no registered Terrario interface", True, "AgentFactory")
            continue
        compatibility = assess_compatibility(scenario, agent_id)
        if compatibility.status == "UNVERIFIED":
            add("SCIENTIFIC", "CAPABILITY_UNVERIFIED", f"agent.{agent_id}", "required capability could not be verified", False, "CompatibilityEngine")
    if not draft.world_seeds or not draft.agent_seeds or len(set(draft.world_seeds)) != len(draft.world_seeds) or len(set(draft.agent_seeds)) != len(draft.agent_seeds):
        add("STRUCTURAL", "INVALID_SEED_SET", "seeds", "seed sets must be explicit, nonempty and unique", True, "SeedPolicy")
    if draft.step_limit <= 0 or draft.repetitions <= 0: add("STRUCTURAL", "INVALID_LIMIT", "limits", "positive limits required", True, "ExperimentDraft")
    if draft.device_requirement not in {"cpu", "cuda"}: add("COMPATIBILITY", "UNSUPPORTED_DEVICE", "device_requirement", "unknown device", True, "AgentFactory")
    if draft.device_requirement == "cuda": add("SCIENTIFIC", "BLOCKED_CUDA", "device_requirement", "CUDA path remains blocked and was not probed", True, "LAB-UI-02C scope")
    if not draft.metric_ids: add("SCIENTIFIC", "METRIC_MISSING", "metric_ids", "no outcome metric selected", True, "DesignReview")
    observer_signals = set(draft.observer_channels) | set(draft.available_signals)
    for metric_id in draft.metric_ids:
        try: metric = metric_registry.get(metric_id)
        except KeyError:
            add("COMPATIBILITY", "METRIC_MISSING", f"metric.{metric_id}", "unknown metric", True, "MetricRegistry"); continue
        applicability = metric_registry.applicability(metric_id, scenario, observer_signals)
        if applicability.status == "MISSING_REQUIRED_SIGNAL": add("COMPATIBILITY", "MISSING_REQUIRED_SIGNAL", f"metric.{metric_id}", f"missing {applicability.missing_signals}", True, "MetricApplicability")
        if applicability.status == "IMPLEMENTATION_UNAVAILABLE": add("SCIENTIFIC", "WEAK_PROXY", f"metric.{metric_id}", "metric is proposed/unavailable", True, "MetricDefinition.implementation_status")
        if metric.construct_validation_status != "VALIDATED_FOR_CONSTRUCT": add("SCIENTIFIC", "METRIC_NOT_VALIDATED", f"metric.{metric_id}", "implementation is not construct validation", False, "MetricDefinition.construct_validation_status")
        if metric.direction in {"DESCRIPTIVE_ONLY", "NO_ORDERING"}: add("SCIENTIFIC", "DESCRIPTIVE_ONLY", f"metric.{metric_id}", "metric does not define an ordered outcome", False, "MetricDefinition.direction")
    try: expected_channels = observer_registry.profile(draft.observer_profile).channels
    except KeyError: add("COMPATIBILITY", "OBSERVER_PROFILE_INCOMPATIBLE", "observer_profile", "unknown profile", True, "ObserverRegistry")
    else:
        if tuple(draft.observer_channels) != tuple(expected_channels): add("COMPATIBILITY", "OBSERVER_PROFILE_INCOMPATIBLE", "observer_channels", "profile must expand to exact registered channels", True, "ObserverRegistry.expand")
    missing_truth = set(draft.required_ground_truth) - set(draft.available_ground_truth)
    if missing_truth: add("SCIENTIFIC", "GROUND_TRUTH_MISSING", "available_ground_truth", f"missing {sorted(missing_truth)}", True, "ScenarioDefinition.required_ground_truth")
    if not draft.controls: add("SCIENTIFIC", "NO_CONTROL", "controls", "no explicit contrast control", True, "ScientificReview")
    elif any(not c.contrast.strip() for c in draft.controls): add("SCIENTIFIC", "NO_CONTROL", "controls.contrast", "control contrast must be explicit", True, "ControlCondition")
    if scenario.interventions and not draft.manipulation_check: add("SCIENTIFIC", "NO_MANIPULATION_CHECK", "manipulation_check", "structured intervention requires a check", True, "ScenarioDefinition.interventions")
    if draft.provenance.source_review_state != "APPROVED_FOR_EXPERIMENT_DESIGN":
        add("SCIENTIFIC", "REVIEW_REQUIRED", "provenance.source_review_state", "upstream review cannot be upgraded by Composer", True, "ScientificReview")
        add("SCIENTIFIC", "DESIGN_NOT_APPROVED", "state", "draft remains non-executable", True, "LAB-UI-02C boundary")
    add("SCIENTIFIC", "NOT_PREREGISTERED", "state", "preregistration remains a future gate", False, "LAB-UI-02C boundary")
    return tuple(rows)


def state_for(findings: tuple[DraftFinding, ...]) -> DraftState:
    if any(x.blocking and x.category == "STRUCTURAL" for x in findings): return DraftState.INCOMPLETE
    if any(x.code in {"REVIEW_REQUIRED", "DESIGN_NOT_APPROVED"} for x in findings): return DraftState.REVIEW_BLOCKED
    if any(x.blocking for x in findings): return DraftState.READY_FOR_REVIEW
    return DraftState.PREREGISTRATION_READY


def draft_diff(parent: ExperimentDraft, child: ExperimentDraft) -> dict[str, Any]:
    scientific = {}
    for key in parent.scientific_payload():
        left, right = parent.scientific_payload()[key], child.scientific_payload()[key]
        if canonical_json(left) != canonical_json(right): scientific[key] = {"from": left, "to": right}
    ui = {} if canonical_json(parent.ui_preferences) == canonical_json(child.ui_preferences) else {"ui_preferences": {"from": dict(parent.ui_preferences), "to": dict(child.ui_preferences)}}
    return {"scientific": scientific, "ui": ui, "hash_changed": parent.content_hash != child.content_hash}


def build_trial_matrix(draft: ExperimentDraft, cell_blockers: Mapping[str, tuple[str, ...]] | None = None,
                       warning_threshold: int = 500) -> TrialMatrix:
    variants = draft.variant_ids or (draft.scenario_id,)
    conditions = tuple((a, a) for a in draft.agent_ids) + tuple((c.control_id, c.agent_id) for c in draft.controls)
    blockers_by_condition = dict(cell_blockers or {})
    cells = []
    for variant, (condition, agent), world_seed, agent_seed, repetition in product(
            variants, conditions, draft.world_seeds, draft.agent_seeds, range(1, draft.repetitions + 1)):
        blockers = tuple(blockers_by_condition.get(condition, ()))
        status = "BLOCKED" if blockers else "READY_FOR_FUTURE_EXECUTION"
        identity = scientific_hash((draft.content_hash, variant, condition, world_seed, agent_seed, repetition))[:16]
        cells.append(TrialIntent(f"trial-{identity}", variant, condition, agent, world_seed, agent_seed,
            repetition, status, blockers, draft.metric_ids, draft.observer_profile))
    total = len(variants) * len(conditions) * len(draft.world_seeds) * len(draft.agent_seeds) * draft.repetitions
    assert total == len(cells)
    warnings = ("COMBINATORIAL_EXPLOSION",) if total > warning_threshold else ()
    return TrialMatrix(draft.content_hash, len(variants), len(conditions), len(draft.world_seeds),
        len(draft.agent_seeds), draft.repetitions, total, tuple(cells), warnings)
