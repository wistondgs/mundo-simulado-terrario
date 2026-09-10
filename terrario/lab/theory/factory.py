"""CPU-only, review-gated scientific hypothesis and experiment design factory."""

from __future__ import annotations

import hashlib
import itertools
from dataclasses import dataclass, field, replace
from enum import StrEnum
from typing import Iterable, Mapping

from terrario.experiment.specs import ExperimentSpec
from terrario.lab.models import freeze
from terrario.lab.theory.models import HyperedgeCandidateRecord


GENERATOR_VERSION = "hypothesis-factory-0.1"


class ReviewState(StrEnum):
    GENERATED = "GENERATED"
    UNDER_REVIEW = "UNDER_REVIEW"
    REVISE = "REVISE"
    APPROVED_FOR_EXPERIMENT_DESIGN = "APPROVED_FOR_EXPERIMENT_DESIGN"
    APPROVED_FOR_EXECUTION = "APPROVED_FOR_EXECUTION"
    REJECTED = "REJECTED"


class Identification(StrEnum):
    STRONG = "STRONG_IDENTIFICATION"
    PARTIAL = "PARTIAL_IDENTIFICATION"
    DESCRIPTIVE = "DESCRIPTIVE_ONLY"
    INVALID = "INVALID_COMPARISON"


class OutcomeClass(StrEnum):
    SUPPORTS = "SUPPORTS"
    WEAKLY_SUPPORTS = "WEAKLY_SUPPORTS"
    MIXED = "MIXED"
    INCONCLUSIVE = "INCONCLUSIVE"
    WEAKENS = "WEAKENS"
    CONTRADICTS_IN_REGIME = "CONTRADICTS_IN_REGIME"
    EXPERIMENT_INVALID = "EXPERIMENT_INVALID"


def _id(prefix: str, *parts: object) -> str:
    material = "|".join(str(p) for p in parts)
    return f"{prefix}-{hashlib.sha256(material.encode()).hexdigest()[:16]}"


@dataclass(frozen=True)
class DesignProvenance:
    source_hyperedge_id: str
    source_claim_ids: tuple[str, ...]
    theory_snapshot_id: str
    source_artifact: str
    generator_version: str = GENERATOR_VERSION
    human_review_state: ReviewState = ReviewState.GENERATED
    modifications: tuple[str, ...] = ()

    def modified(self, delta: str) -> "DesignProvenance":
        return replace(self, modifications=(*self.modifications, delta))


@dataclass(frozen=True)
class PredictionSpec:
    id: str; hypothesis_id: str; observable: str; direction: str
    comparison: str; temporal_window: str; minimum_meaningful_effect: str | None
    expected_pattern: str; contradictory_pattern: str; ambiguous_pattern: str


@dataclass(frozen=True)
class FalsificationSpec:
    weakens: str; contradicts_in_regime: str
    compatible_not_diagnostic: str; requires_redesign: str


@dataclass(frozen=True)
class ConfounderSpec:
    id: str; category: str; description: str; critical: bool = True
    mitigation: str | None = None


@dataclass(frozen=True)
class RivalHypothesis:
    id: str; family_id: str; source_hyperedge_id: str
    proposed_mechanism: str; target_outcome: str; components: tuple[str, ...]
    assumptions: tuple[str, ...]; provenance: DesignProvenance
    predicted_observations: tuple[PredictionSpec, ...] = ()
    falsification: FalsificationSpec | None = None
    known_confounders: tuple[ConfounderSpec, ...] = ()
    epistemic_status: str = "SYSTEM_GENERATED_RIVAL"
    review_state: ReviewState = ReviewState.GENERATED
    kind: str = "STRUCTURAL_RIVAL"


@dataclass(frozen=True)
class AlternativeExplanation(RivalHypothesis):
    kind: str = "ALTERNATIVE_EXPLANATION"


@dataclass(frozen=True)
class NullHypothesis(RivalHypothesis):
    kind: str = "NULL_HYPOTHESIS"


@dataclass(frozen=True)
class HypothesisFamily:
    id: str; source_hyperedge_id: str; target_outcome: str
    hypotheses: tuple[RivalHypothesis, ...]; design_questions: tuple[str, ...]
    provenance: DesignProvenance; review_state: ReviewState = ReviewState.GENERATED
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class InterventionSpec:
    id: str; intervention_type: str; target: str; manipulated_property: str
    preserved_properties: tuple[str, ...]; expected_side_effects: tuple[str, ...]
    confounds_introduced: tuple[str, ...]; reversible: bool; feasibility: str


@dataclass(frozen=True)
class ControlCondition:
    id: str; control_type: str; description: str; matched_properties: tuple[str, ...]
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class DiscriminatingPrediction:
    id: str; hypothesis_a: str; hypothesis_b: str; intervention_id: str
    predicted_under_a: str; predicted_under_b: str; diagnosticity_score: float
    assumptions: tuple[str, ...]


@dataclass(frozen=True)
class IdentifiabilityReport:
    status: Identification; checks: Mapping[str, bool]; warnings: tuple[str, ...]
    def __post_init__(self): object.__setattr__(self, "checks", freeze(self.checks))


@dataclass(frozen=True)
class CostEstimate:
    variants: int; paired_seeds: int; runs: int; estimated_wall_seconds: float
    storage_bytes: int; forensic_storage_bytes: int; required_device: str
    basis: str


@dataclass(frozen=True)
class ExperimentPriorityScore:
    discriminating_power: float; feasibility: float; theoretical_coverage: float
    causal_identifiability: float; estimated_cost: float
    expected_information_gain_proxy: float


@dataclass(frozen=True)
class ExperimentDesignDraft:
    id: str; version: int; family_id: str; target_hypotheses: tuple[str, ...]
    predictions: tuple[DiscriminatingPrediction, ...]
    interventions: tuple[InterventionSpec, ...]; controls: tuple[ControlCondition, ...]
    confounders: tuple[ConfounderSpec, ...]; seeds_strategy: str
    metrics: tuple[str, ...]; preregistered_thresholds: Mapping[str, str]
    falsification_rules: tuple[FalsificationSpec, ...]
    stopping_conditions: tuple[str, ...]; validity_gates: tuple[str, ...]
    required_capabilities: tuple[str, ...]; provenance: DesignProvenance
    identifiability: IdentifiabilityReport; cost: CostEstimate
    priority: ExperimentPriorityScore; review_state: ReviewState = ReviewState.GENERATED
    def __post_init__(self): object.__setattr__(self, "preregistered_thresholds", freeze(self.preregistered_thresholds))


class RivalHypothesisGenerator:
    def generate(self, edge: HyperedgeCandidateRecord, snapshot_id: str, source_claim_ids: Iterable[str] = ()) -> HypothesisFamily:
        provenance = DesignProvenance(edge.id, tuple(source_claim_ids), snapshot_id, edge.source_artifact)
        family_id = f"FAMILY-{edge.id}"
        rivals: list[RivalHypothesis] = []
        for size in range(1, len(edge.components) + 1):
            for components in itertools.combinations(edge.components, size):
                hid = _id("RIVAL", family_id, *components)
                falsification = FalsificationSpec(
                    f"removing {', '.join(components)} does not alter {edge.predicted_outcome}",
                    f"the predicted direction reverses in the declared regime for {', '.join(components)}",
                    f"all compared conditions show the same unresolved pattern for {edge.predicted_outcome}",
                    "the target outcome is not operationally observable or validity gates fail",
                )
                rivals.append(RivalHypothesis(
                    hid, family_id, edge.id, " + ".join(components), edge.predicted_outcome,
                    components, ("comparison conditions preserve non-target properties",), provenance,
                    falsification=falsification,
                    known_confounders=ConfounderRegistry().from_edge(edge),
                ))
        null_id = _id("NULL", family_id)
        rivals.append(NullHypothesis(
            null_id, family_id, edge.id, "none of the candidate components causally contributes",
            edge.predicted_outcome, (), ("a meaningful null comparison is domain-valid",), provenance,
            falsification=FalsificationSpec(
                "a reliable component-sensitive difference is observed", "a preregistered component effect is observed",
                "an underpowered null result", "the null condition changes non-target properties",
            ), known_confounders=ConfounderRegistry().from_edge(edge),
        ))
        questions = tuple(q for c in edge.components for q in (
            f"Is {c} necessary?", f"Is {c} sufficient?", f"Is {c} facilitating but non-necessary?",
            f"Does {c} matter only with another component?", f"Does {c} mediate another component -> {edge.predicted_outcome}?",
            f"Does {c} moderate another component -> {edge.predicted_outcome}?",
        ))
        warnings = _special_warnings(edge)
        return HypothesisFamily(family_id, edge.id, edge.predicted_outcome, tuple(rivals), questions, provenance, warnings=warnings)


class PredictionCompiler:
    def compile(self, hypothesis: RivalHypothesis) -> PredictionSpec:
        if not hypothesis.target_outcome.strip(): raise ValueError("target outcome is required")
        mechanism = " + ".join(hypothesis.components) or "null condition"
        return PredictionSpec(
            _id("PRED", hypothesis.id), hypothesis.id, hypothesis.target_outcome, "DIFFERENCE_EXPECTED",
            "target intervention versus matched control", "PREDECLARATION_REQUIRED", None,
            f"outcome pattern differs as predicted when manipulating {mechanism}",
            f"outcome pattern opposes the prediction for {mechanism}",
            "difference is below a preregistered meaningful effect or validity is uncertain",
        )


class InterventionDesigner:
    TYPES = ("ABLATION", "SUBSTITUTION", "FREEZE", "NOISE", "DELAY", "CAPACITY_LIMIT", "INFORMATION_REMOVAL", "ENVIRONMENTAL_CHANGE", "TRANSFER", "PLACEBO", "SHAM")
    def design(self, family: HypothesisFamily) -> tuple[InterventionSpec, ...]:
        components = sorted({c for h in family.hypotheses for c in h.components})
        return tuple(InterventionSpec(
            _id("INT", family.id, c), "ABLATION", c, "availability",
            ("environment", "seed", "training exposure"), ("capacity may change",),
            ("compute", "parameter count"), True, "CAPABILITY_REVIEW_REQUIRED",
        ) for c in components)


class ControlDesigner:
    TYPES = ("baseline", "placebo/sham", "equal-compute", "equal-parameter", "frozen-learning", "architecture-matched", "random", "temporal", "transfer-only")
    def design(self, family: HypothesisFamily) -> tuple[ControlCondition, ...]:
        return (
            ControlCondition(_id("CTRL", family.id, "baseline"), "baseline", "matched full condition", ("seed", "environment", "training exposure")),
            ControlCondition(_id("CTRL", family.id, "sham"), "placebo/sham", "sham manipulation", ("compute", "parameter count", "information access")),
            ControlCondition(_id("CTRL", family.id, "compute"), "equal-compute", "compute-matched control", ("compute budget",)),
            ControlCondition(_id("CTRL", family.id, "parameters"), "equal-parameter", "parameter-count-matched control", ("parameter count",)),
            ControlCondition(_id("CTRL", family.id, "frozen"), "frozen-learning", "disable learning while preserving evaluation", ("architecture", "evaluation exposure")),
            ControlCondition(_id("CTRL", family.id, "architecture"), "architecture-matched", "change only the target mechanism", ("architecture", "parameter count")),
            ControlCondition(_id("CTRL", family.id, "random"), "random", "randomized non-target manipulation", ("manipulation magnitude",), ("A4 versus A0 is not a clean causal control unless capacity, information, compute, and training are matched",)),
            ControlCondition(_id("CTRL", family.id, "temporal"), "temporal", "matched pre/post temporal control", ("elapsed time", "exposure")),
            ControlCondition(_id("CTRL", family.id, "transfer"), "transfer-only", "evaluate held-out transfer without additional learning", ("training history",)),
        )


class ConfounderRegistry:
    CATEGORIES = ("compute", "parameter count", "observation access", "action access", "memory capacity", "training exposure", "reward differences", "initialization", "seed mismatch", "environment mismatch", "leakage", "survival bias", "opportunity availability", "metric artifact", "threshold artifact")
    def from_edge(self, edge: HyperedgeCandidateRecord) -> tuple[ConfounderSpec, ...]:
        values = edge.confounders or self.CATEGORIES
        return tuple(ConfounderSpec(_id("CONF", edge.id, value), value if value in self.CATEGORIES else "domain-specific", value) for value in values)


class CausalIdentifiabilityAudit:
    KEYS = ("single_target_change", "capacity_matched", "information_matched", "compute_matched", "training_matched", "paired_seeds", "identical_environment")
    def audit(self, checks: Mapping[str, bool]) -> IdentifiabilityReport:
        complete = {key: bool(checks.get(key, False)) for key in self.KEYS}
        passed = sum(complete.values())
        status = Identification.STRONG if passed == len(self.KEYS) else Identification.PARTIAL if passed >= 5 else Identification.DESCRIPTIVE if passed >= 2 else Identification.INVALID
        warnings = () if status == Identification.STRONG else ("causal language must be limited to the achieved identification level",)
        return IdentifiabilityReport(status, complete, warnings)


class ExperimentCostEstimator:
    def estimate(self, variants: int, seeds: int, *, observed_seconds_per_run: float | None = None, bytes_per_run: int | None = None, forensic: bool = False, required_device: str = "CPU") -> CostEstimate:
        runs = variants * seeds; seconds = observed_seconds_per_run if observed_seconds_per_run is not None else 300.0
        storage = bytes_per_run if bytes_per_run is not None else 20 * 1024 * 1024
        return CostEstimate(variants, seeds, runs, runs * seconds, runs * storage, runs * storage * 2 if forensic else 0, required_device, "OBSERVED_BASED" if observed_seconds_per_run is not None and bytes_per_run is not None else "ASSUMPTION_BASED")


class ExperimentDesignCompiler:
    def compile(self, family: HypothesisFamily, paired_seeds: int = 4) -> ExperimentDesignDraft:
        if family.review_state != ReviewState.APPROVED_FOR_EXPERIMENT_DESIGN:
            raise PermissionError("family must be APPROVED_FOR_EXPERIMENT_DESIGN")
        interventions = InterventionDesigner().design(family); controls = ControlDesigner().design(family)
        hypotheses = tuple(replace(h, predicted_observations=(PredictionCompiler().compile(h),)) for h in family.hypotheses)
        discriminating = _discriminating(hypotheses, interventions)
        ident = CausalIdentifiabilityAudit().audit({"paired_seeds": True, "identical_environment": True})
        cost = ExperimentCostEstimator().estimate(len(interventions) + len(controls), paired_seeds)
        priority = ExperimentPriorityScore(0.7, 0.5, 1.0, 0.3, 0.4, 0.6)
        provenance = replace(family.provenance, human_review_state=family.review_state)
        return ExperimentDesignDraft(
            _id("DESIGN", family.id, 1), 1, family.id, tuple(h.id for h in hypotheses), discriminating,
            interventions, controls, tuple({c.id: c for h in hypotheses for c in h.known_confounders}.values()),
            "paired seeds; exact count requires preregistration", (family.target_outcome,), {},
            tuple(h.falsification for h in hypotheses if h.falsification),
            ("stop on invalid comparison",), ("metric exists", "observer available", "provenance complete"),
            _required_capabilities(family), provenance, ident, cost, priority,
        )

    def to_experiment_spec(self, design: ExperimentDesignDraft, *, scenario_path: str, seeds: list[int], agent_id: str) -> ExperimentSpec:
        errors = DesignValidator().validate(design, for_execution=True)
        if errors: raise PermissionError("design is not executable: " + "; ".join(errors))
        return ExperimentSpec(f"{design.id}:full", design.family_id, "full", agent_id, {}, scenario_path, seeds)


class DesignValidator:
    def validate(self, design: ExperimentDesignDraft, *, for_execution: bool = False) -> tuple[str, ...]:
        errors: list[str] = []
        if not any(h.startswith("NULL-") for h in design.target_hypotheses): errors.append("null/rival required")
        if not design.falsification_rules: errors.append("falsification required")
        if not design.controls: errors.append("control required")
        if any(c.critical and not c.mitigation for c in design.confounders): errors.append("critical confounders unaddressed")
        if not design.metrics or any(not m.strip() for m in design.metrics): errors.append("observable metric required")
        if design.identifiability.status == Identification.INVALID: errors.append("comparison invalid")
        if not design.provenance.source_hyperedge_id or not design.provenance.theory_snapshot_id: errors.append("provenance missing")
        if not design.required_capabilities: errors.append("experimental capability missing")
        if for_execution and design.review_state != ReviewState.APPROVED_FOR_EXECUTION: errors.append("APPROVED_FOR_EXECUTION required")
        return tuple(errors)


class DesignRepository:
    def __init__(self): self._designs: dict[tuple[str, int], ExperimentDesignDraft] = {}
    def save(self, design: ExperimentDesignDraft) -> None:
        key=(design.id, design.version)
        if key in self._designs: raise ValueError("approved/versioned designs are immutable")
        self._designs[key]=design
    def revise(self, design: ExperimentDesignDraft, delta: str) -> ExperimentDesignDraft:
        return replace(design, id=design.id.rsplit("-v", 1)[0]+f"-v{design.version+1}", version=design.version+1, review_state=ReviewState.REVISE, provenance=design.provenance.modified(delta))


@dataclass(frozen=True)
class PortfolioEntry:
    family: HypothesisFamily; design: ExperimentDesignDraft | None; blockers: tuple[str, ...]
    readiness: str; warnings: tuple[str, ...]


@dataclass(frozen=True)
class ExperimentPortfolio:
    snapshot_id: str; entries: tuple[PortfolioEntry, ...]
    def search(self, readiness: str) -> tuple[PortfolioEntry, ...]: return tuple(e for e in self.entries if e.readiness == readiness)


def build_portfolio(edges: Iterable[HyperedgeCandidateRecord], snapshot_id: str) -> ExperimentPortfolio:
    generator=RivalHypothesisGenerator(); entries=[]
    for edge in edges:
        family=generator.generate(edge, snapshot_id)
        reviewed=replace(family, review_state=ReviewState.APPROVED_FOR_EXPERIMENT_DESIGN)
        design=ExperimentDesignCompiler().compile(reviewed)
        blockers=("HUMAN_REVIEW_REQUIRED", *DesignValidator().validate(design))
        readiness="NEW_ENVIRONMENT_REQUIRED" if any("NEW_ENVIRONMENT" in x for x in design.required_capabilities) else "GPU_REQUIRED" if any("GPU" in x for x in design.required_capabilities) else "CPU_READY"
        entries.append(PortfolioEntry(family, replace(design, review_state=ReviewState.GENERATED), tuple(dict.fromkeys(blockers)), readiness, family.warnings))
    return ExperimentPortfolio(snapshot_id, tuple(entries))


def structural_dry_run(design: ExperimentDesignDraft, available_metrics: Iterable[str], available_capabilities: Iterable[str]) -> Mapping[str, object]:
    metrics=set(available_metrics); capabilities=set(available_capabilities)
    checks={"metrics_available": set(design.metrics) <= metrics, "capabilities_available": set(design.required_capabilities) <= capabilities, "review_gate_preserved": design.review_state != ReviewState.APPROVED_FOR_EXECUTION}
    return freeze({"artifact_type": "ENGINEERING_DRY_RUN", "scientific_evidence": False, "status": "PASS" if all(checks.values()) else "BLOCKED", "checks": checks})


def classify_outcome(*, valid: bool, expected: bool | None, contradictory: bool = False, mixed: bool = False, weak: bool = False) -> OutcomeClass:
    if not valid: return OutcomeClass.EXPERIMENT_INVALID
    if mixed: return OutcomeClass.MIXED
    if contradictory: return OutcomeClass.CONTRADICTS_IN_REGIME
    if expected is None: return OutcomeClass.INCONCLUSIVE
    if expected: return OutcomeClass.WEAKLY_SUPPORTS if weak else OutcomeClass.SUPPORTS
    return OutcomeClass.WEAKENS


def transition_review(value, state: ReviewState):
    allowed={ReviewState.GENERATED:{ReviewState.UNDER_REVIEW,ReviewState.REJECTED},ReviewState.UNDER_REVIEW:{ReviewState.REVISE,ReviewState.APPROVED_FOR_EXPERIMENT_DESIGN,ReviewState.REJECTED},ReviewState.REVISE:{ReviewState.UNDER_REVIEW},ReviewState.APPROVED_FOR_EXPERIMENT_DESIGN:{ReviewState.APPROVED_FOR_EXECUTION,ReviewState.REVISE,ReviewState.REJECTED},ReviewState.APPROVED_FOR_EXECUTION:set(),ReviewState.REJECTED:set()}
    if state not in allowed[value.review_state]: raise PermissionError(f"invalid review transition {value.review_state} -> {state}")
    provenance=replace(value.provenance,human_review_state=state)
    return replace(value,review_state=state,provenance=provenance)


def _discriminating(hypotheses: tuple[RivalHypothesis, ...], interventions: tuple[InterventionSpec, ...]) -> tuple[DiscriminatingPrediction, ...]:
    null=next(h for h in hypotheses if isinstance(h,NullHypothesis)); result=[]
    for h in hypotheses:
        if h is null or not h.components: continue
        intervention=next(i for i in interventions if i.target == h.components[0])
        score=round(1/len(h.components),3)
        result.append(DiscriminatingPrediction(_id("DISC",h.id,null.id),h.id,null.id,intervention.id,"component-sensitive change","no component-sensitive change",score,("valid matched intervention",)))
    return tuple(result)


def _special_warnings(edge: HyperedgeCandidateRecord) -> tuple[str, ...]:
    if edge.original_id == "HYPERCAND-01": return ("FACTORIAL_COST_EXPLOSION", "COMPARE_SCREENING_FRACTIONAL_SEQUENTIAL_AND_ADAPTIVE_DESIGNS_BEFORE_FULL_FACTORIAL")
    if edge.original_id == "HYPERCAND-03": return ("CONSTRUCT_CIRCULARITY_RISK", "SEPARATE_RETENTION_AND_TRANSFER_AS_MECHANISM_VS_OUTCOME")
    if edge.original_id == "HYPERCAND-04": return ("HISTORICAL_DESCRIPTIVE_STRUCTURE", "DO_NOT_ASSUME_STAGE_ORDER_IS_CAUSAL_OR_NECESSARY")
    if "collect" in (edge.level+" "+edge.predicted_outcome).lower(): return ("AGGREGATE_PERFORMANCE_IS_NOT_COLLECTIVE_INTELLIGENCE",)
    return ()


def _required_capabilities(family: HypothesisFamily) -> tuple[str, ...]:
    text=(family.target_outcome+" "+" ".join(h.proposed_mechanism for h in family.hypotheses)).lower()
    caps=["OBSERVER", "METRIC_OPERATIONALIZATION"]
    if any(x in text for x in ("collective","communication","cultural","group")): caps.append("NEW_ENVIRONMENT_COLLECTIVE")
    if any(x in text for x in ("language","creative","conscious")): caps.append("NEW_ENVIRONMENT_REQUIRED")
    if "rapid generalization" in text or "continual learning" in text: caps.append("GPU_FOR_FULL_SCALE")
    return tuple(caps)
