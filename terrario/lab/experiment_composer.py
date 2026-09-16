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
class HypothesisExperimentCondition:
    """One named condition with an explicit, immutable execution binding.

    This remains a design contract, not authorization to execute.  The
    configuration exists so a later authorized execution cannot reconstruct an
    intervention from prose or silently run a default architecture instead.
    """

    condition_id: str
    intervention: str
    expected_pattern: str
    rationale: str
    agent_config: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not all((self.condition_id, self.intervention, self.expected_pattern, self.rationale)):
            raise ValueError("hypothesis experiment conditions require id, intervention, expectation, and rationale")
        if any(not isinstance(key, str) or not key.startswith("use_") or not isinstance(value, bool)
               for key, value in self.agent_config.items()):
            raise ValueError("condition agent_config accepts only explicit boolean use_* switches")
        object.__setattr__(self, "agent_config", MappingProxyType(dict(self.agent_config)))


@dataclass(frozen=True)
class TreatmentArm:
    """The indivisible intervention unit used by a paired CL-7 protocol.

    ``variant`` is descriptive metadata of an arm, never a second factorial
    axis.  Keeping this invariant in the domain layer prevents a caller (or a
    UI) from manufacturing the scientifically contradictory combinations.
    """

    arm_id: str
    variant: str
    immutable_config: Mapping[str, bool]

    def __post_init__(self) -> None:
        expected = {
            "PLANNER_PRESERVED": ("preserved", {"use_planner": True, "use_world_model": True}),
            "PLANNER_ABLATED": ("ablated", {"use_planner": False, "use_world_model": True}),
        }
        if self.arm_id not in expected:
            raise ValueError("unknown treatment arm")
        expected_variant, expected_config = expected[self.arm_id]
        config = dict(self.immutable_config)
        if self.variant != expected_variant or config != expected_config:
            raise ValueError("treatment arm has a contradictory immutable configuration")
        object.__setattr__(self, "immutable_config", MappingProxyType(config))

    @property
    def treatment_signature(self) -> str:
        return scientific_hash({"arm_id": self.arm_id, "variant": self.variant,
                                "immutable_config": dict(self.immutable_config)})


@dataclass(frozen=True)
class SeedPair:
    pair_id: str
    world_seed: int
    agent_seed: int

    def __post_init__(self) -> None:
        if not self.pair_id or not isinstance(self.world_seed, int) or not isinstance(self.agent_seed, int):
            raise ValueError("seed pairs require an identifier and integer world/agent seeds")


@dataclass(frozen=True)
class InitialStateFingerprint:
    """A path-independent split between paired state and treatment state."""

    pair_id: str
    shared_initial_state: Mapping[str, str]
    treatment_config: Mapping[str, bool]

    def __post_init__(self) -> None:
        shared = dict(self.shared_initial_state)
        required = {"world_state_hash", "world_rng_hash", "agent_parameter_hash",
                    "agent_memory_hash", "agent_rng_hash", "scenario_hash",
                    "difficulty_hash", "code_revision", "metric_spec_hash"}
        if set(shared) != required or any(not isinstance(value, str) or not value for value in shared.values()):
            raise ValueError("initial-state fingerprint is incomplete")
        config = dict(self.treatment_config)
        if config not in ({"use_planner": True, "use_world_model": True},
                          {"use_planner": False, "use_world_model": True}):
            raise ValueError("initial-state fingerprint has an invalid treatment configuration")
        object.__setattr__(self, "shared_initial_state", MappingProxyType(shared))
        object.__setattr__(self, "treatment_config", MappingProxyType(config))

    @property
    def shared_hash(self) -> str:
        return scientific_hash(dict(self.shared_initial_state))


@dataclass(frozen=True)
class HypothesisExperimentMapping:
    """Inspectable CL-4 translation; it never asserts execution readiness."""

    schema_version: str
    hypothesis_semantic_id: str
    prediction: str
    independent_variable: str
    dependent_variable: str
    conditions: tuple[HypothesisExperimentCondition, ...]
    agent_capability: str
    scenario_rationale: str
    metric_id: str
    metric_rationale: str
    failure_criterion: str
    derivation_rule: str
    source_claim_ids: tuple[str, ...]
    field_rationales: Mapping[str, str]

    def __post_init__(self):
        required = (
            self.schema_version, self.hypothesis_semantic_id, self.prediction,
            self.independent_variable, self.dependent_variable, self.agent_capability,
            self.scenario_rationale, self.metric_id, self.metric_rationale,
            self.failure_criterion, self.derivation_rule,
        )
        if not all(required) or len(self.conditions) < 2 or not self.source_claim_ids:
            raise ValueError("hypothesis experiment mapping is incomplete")
        if len({item.condition_id for item in self.conditions}) != len(self.conditions):
            raise ValueError("hypothesis experiment condition identifiers must be unique")
        required_rationales = {"independent_variable", "dependent_variable", "control", "scenario", "metric", "failure_criterion"}
        if required_rationales - set(self.field_rationales) or any(not value for value in self.field_rationales.values()):
            raise ValueError("every scientific field requires an explicit rationale")
        object.__setattr__(self, "field_rationales", MappingProxyType(dict(self.field_rationales)))


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
    hypothesis_mapping: HypothesisExperimentMapping | None = None

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
            "hypothesis_mapping": self.hypothesis_mapping,
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
    agent_config: Mapping[str, Any] = field(default_factory=dict)
    expected_classification: str = "FUTURE_SCIENTIFIC_REVIEW_REQUIRED"
    arm_id: str | None = None
    seed_pair_id: str | None = None
    treatment_signature: str | None = None
    initial_state_fingerprint: InitialStateFingerprint | None = None

    def __post_init__(self):
        if any(not isinstance(key, str) or not key.startswith("use_") or not isinstance(value, bool)
               for key, value in self.agent_config.items()):
            raise ValueError("trial agent_config must be explicit boolean use_* bindings")
        object.__setattr__(self, "agent_config", MappingProxyType(dict(self.agent_config)))
        if self.arm_id is not None:
            arm = TreatmentArm(self.arm_id, self.variant_id, self.agent_config)
            if self.treatment_signature != arm.treatment_signature:
                raise ValueError("trial treatment signature does not match its arm")
            if not self.seed_pair_id or self.initial_state_fingerprint is None:
                raise ValueError("paired treatment trials require a seed pair and initial-state fingerprint")
            if self.initial_state_fingerprint.pair_id != self.seed_pair_id:
                raise ValueError("trial fingerprint belongs to another seed pair")


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
    treatment_arms: tuple[TreatmentArm, ...] = ()
    seed_pairs: tuple[SeedPair, ...] = ()
    semantic_hash: str | None = None

    def __post_init__(self) -> None:
        if not self.treatment_arms:
            return
        if {arm.arm_id for arm in self.treatment_arms} != {"PLANNER_PRESERVED", "PLANNER_ABLATED"}:
            raise ValueError("paired planner matrix requires exactly two treatment arms")
        expected = len(self.seed_pairs) * len(self.treatment_arms)
        if self.total_trials != expected or len(self.cells) != expected:
            raise ValueError("paired matrix cardinality is invalid")
        keys = {(cell.seed_pair_id, cell.arm_id) for cell in self.cells}
        if len(keys) != expected or any(None in key for key in keys):
            raise ValueError("paired matrix must contain one cell per pair and arm")
        if self.semantic_hash != _matrix_semantic_hash(self.cells, self.treatment_arms, self.seed_pairs):
            raise ValueError("paired matrix semantic hash mismatch")


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
    if draft.hypothesis_mapping is not None:
        mapping = draft.hypothesis_mapping
        if mapping.hypothesis_semantic_id != draft.provenance.source_artifact:
            add("INTEGRITY", "HYPOTHESIS_PROVENANCE_MISMATCH", "hypothesis_mapping.hypothesis_semantic_id", "mapping must resolve to the draft provenance", True, "CL-4")
        if mapping.metric_id not in draft.metric_ids:
            add("INTEGRITY", "HYPOTHESIS_METRIC_MISMATCH", "hypothesis_mapping.metric_id", "mapped metric must be selected by the draft", True, "CL-4")
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
    if draft.hypothesis_mapping is not None:
        # Treatment arms replace the historical variant × condition Cartesian
        # product.  A variant belongs to exactly one arm, so this branch is
        # always |world×agent| × 2, not |world×agent| × 2 × 2.
        if len(draft.agent_ids) != 1:
            raise ValueError("operational hypothesis mapping requires exactly one target agent")
        arms = _treatment_arms(draft.hypothesis_mapping.conditions)
        condition_by_arm = {arm.arm_id: next(item.condition_id for item in draft.hypothesis_mapping.conditions
                                              if dict(item.agent_config) == dict(arm.immutable_config))
                            for arm in arms}
        pairs = tuple(SeedPair(f"P{index}", world_seed, agent_seed) for index, (world_seed, agent_seed)
                      in enumerate(product(draft.world_seeds, draft.agent_seeds), start=1))
        blockers_by_condition = dict(cell_blockers or {})
        cells: list[TrialIntent] = []
        for pair in pairs:
            shared = _shared_initial_state(draft, pair)
            for arm in arms:
                condition = condition_by_arm[arm.arm_id]
                blockers = tuple(blockers_by_condition.get(condition, ()))
                status = "BLOCKED" if blockers else "READY_FOR_FUTURE_EXECUTION"
                fingerprint = InitialStateFingerprint(pair.pair_id, shared, arm.immutable_config)
                identity = scientific_hash((draft.content_hash, pair.pair_id, arm.treatment_signature))[:16]
                cells.append(TrialIntent(
                    f"trial-{identity}", arm.variant, condition, draft.agent_ids[0], pair.world_seed,
                    pair.agent_seed, 1, status, blockers, draft.metric_ids, draft.observer_profile,
                    arm.immutable_config, arm_id=arm.arm_id, seed_pair_id=pair.pair_id,
                    treatment_signature=arm.treatment_signature, initial_state_fingerprint=fingerprint,
                ))
        semantic_hash = _matrix_semantic_hash(cells, arms, pairs)
        warnings = ("COMBINATORIAL_EXPLOSION",) if len(cells) > warning_threshold else ()
        return TrialMatrix(draft.content_hash, len(arms), len(arms), len(draft.world_seeds),
            len(draft.agent_seeds), 1, len(cells), tuple(cells), warnings, False,
            arms, pairs, semantic_hash)

    variants = draft.variant_ids or (draft.scenario_id,)
    if draft.hypothesis_mapping is not None:  # pragma: no cover - guarded above
        raise AssertionError("operational mappings must use treatment arms")
    else:
        conditions = tuple((a, a, {}) for a in draft.agent_ids) + tuple((c.control_id, c.agent_id, {}) for c in draft.controls)
    blockers_by_condition = dict(cell_blockers or {})
    cells = []
    for variant, (condition, agent, agent_config), world_seed, agent_seed, repetition in product(
            variants, conditions, draft.world_seeds, draft.agent_seeds, range(1, draft.repetitions + 1)):
        blockers = tuple(blockers_by_condition.get(condition, ()))
        status = "BLOCKED" if blockers else "READY_FOR_FUTURE_EXECUTION"
        identity = scientific_hash((draft.content_hash, variant, condition, agent_config, world_seed, agent_seed, repetition))[:16]
        cells.append(TrialIntent(f"trial-{identity}", variant, condition, agent, world_seed, agent_seed,
            repetition, status, blockers, draft.metric_ids, draft.observer_profile, agent_config))
    total = len(variants) * len(conditions) * len(draft.world_seeds) * len(draft.agent_seeds) * draft.repetitions
    assert total == len(cells)
    warnings = ("COMBINATORIAL_EXPLOSION",) if total > warning_threshold else ()
    return TrialMatrix(draft.content_hash, len(variants), len(conditions), len(draft.world_seeds),
        len(draft.agent_seeds), draft.repetitions, total, tuple(cells), warnings)


def _treatment_arms(conditions: tuple[HypothesisExperimentCondition, ...]) -> tuple[TreatmentArm, ...]:
    """Derive, then validate, the only CL-7 treatment arm vocabulary."""
    configs = {tuple(sorted(dict(item.agent_config).items())) for item in conditions}
    expected = {
        (("use_planner", True), ("use_world_model", True)),
        (("use_planner", False), ("use_world_model", True)),
    }
    if configs != expected or len(conditions) != 2:
        raise ValueError("operational mapping must declare preserved and ablated planner arms exactly once")
    return (
        TreatmentArm("PLANNER_PRESERVED", "preserved", {"use_planner": True, "use_world_model": True}),
        TreatmentArm("PLANNER_ABLATED", "ablated", {"use_planner": False, "use_world_model": True}),
    )


def _shared_initial_state(draft: ExperimentDraft, pair: SeedPair) -> dict[str, str]:
    """Commit deterministic pre-treatment state; no local data-root enters it."""
    basis = {"scenario_hash": draft.scenario_hash, "difficulty_hash": draft.difficulty_fingerprint,
             "world_seed": pair.world_seed, "agent_seed": pair.agent_seed, "agent_id": draft.agent_ids[0],
             "draft_hash": draft.content_hash}
    metric_hash = scientific_hash({"metric_ids": draft.metric_ids})
    if draft.metric_ids == ("planned-action-evaluation-pathway",):
        # The frozen instrument hash, rather than an incidental list hash,
        # binds each initial-state fingerprint to the calibrated construct.
        from terrario.lab.planning_trace_metric import specification
        metric_hash = str(specification()["metric_spec_hash"])
    return {
        "world_state_hash": scientific_hash({**basis, "component": "world-state"}),
        "world_rng_hash": scientific_hash({"world_seed": pair.world_seed, "component": "world-rng"}),
        "agent_parameter_hash": scientific_hash({"agent_id": draft.agent_ids[0], "component": "parameters"}),
        "agent_memory_hash": scientific_hash({"agent_id": draft.agent_ids[0], "component": "initial-memory"}),
        "agent_rng_hash": scientific_hash({"agent_seed": pair.agent_seed, "component": "agent-rng"}),
        "scenario_hash": draft.scenario_hash,
        "difficulty_hash": draft.difficulty_fingerprint,
        "code_revision": scientific_hash({"experiment_schema": draft.schema_version, "agent_id": draft.agent_ids[0]}),
        "metric_spec_hash": metric_hash,
    }


def _matrix_semantic_hash(cells: list[TrialIntent] | tuple[TrialIntent, ...], arms: tuple[TreatmentArm, ...],
                          pairs: tuple[SeedPair, ...]) -> str:
    """Hash sorted semantic projections, deliberately independent of row order."""
    return scientific_hash({
        "treatment_arms": sorted(({"arm_id": arm.arm_id, "variant": arm.variant,
                                     "immutable_config": dict(arm.immutable_config),
                                     "treatment_signature": arm.treatment_signature} for arm in arms), key=lambda x: x["arm_id"]),
        "seed_pairs": sorted(({"pair_id": pair.pair_id, "world_seed": pair.world_seed,
                                "agent_seed": pair.agent_seed} for pair in pairs), key=lambda x: x["pair_id"]),
        "cells": sorted(({"pair_id": cell.seed_pair_id, "arm_id": cell.arm_id,
                           "world_seed": cell.world_seed, "agent_seed": cell.agent_seed,
                           "shared_initial_state": dict(cell.initial_state_fingerprint.shared_initial_state),
                           "treatment_signature": cell.treatment_signature} for cell in cells),
                        key=lambda x: (str(x["pair_id"]), str(x["arm_id"]))),
    })
