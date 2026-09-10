"""Deterministic, non-executing scientific review of generated experiment portfolios."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, fields, is_dataclass, replace
from enum import Enum
from enum import StrEnum
from typing import Iterable, Mapping

from terrario.lab.theory.factory import ExperimentPortfolio, PortfolioEntry


REVIEWER_VERSION = "scientific-review-0.1"


class ConstructStatus(StrEnum):
    CLEAR = "CONSTRUCT_CLEAR"
    PARTIAL = "PARTIAL_AMBIGUITY"
    CIRCULAR = "CONSTRUCT_CIRCULARITY"
    NOT_OPERATIONALIZED = "NOT_OPERATIONALIZED"


class ProxyStatus(StrEnum):
    DIRECT = "DIRECT_OPERATIONALIZATION"
    REASONABLE = "REASONABLE_PROXY"
    WEAK = "WEAK_PROXY"
    MISLEADING = "MISLEADING_PROXY"
    NONE = "NO_PROXY"


class ScientificReadiness(StrEnum):
    READY = "SCIENTIFICALLY_READY"
    OPERATIONALIZATION = "NEEDS_OPERATIONALIZATION"
    CONTROL = "NEEDS_CONTROL"
    CAPABILITY = "NEEDS_NEW_CAPABILITY"
    THEORY = "THEORY_GAP"


@dataclass(frozen=True)
class OperationalizationRecord:
    construct: str
    role: str
    operational_proxy: str | None
    measurement: str | None
    intervention: str | None
    assumptions: tuple[str, ...]
    limitations: tuple[str, ...]
    mapping_confidence: str
    proxy_validity: ProxyStatus


@dataclass(frozen=True)
class MetricAuditRecord:
    name: str
    construct_targeted: str
    definition: str | None
    value_range: str | None
    direction: str | None
    sensitivity: str
    failure_modes: tuple[str, ...]
    potential_gaming: tuple[str, ...]
    confounds: tuple[str, ...]
    currently_implemented: bool


@dataclass(frozen=True)
class ManipulationCheckSpec:
    intervention_target: str
    check: str
    pass_condition: str
    failure_consequence: str = "INVALID_TREATMENT_ATTRIBUTION"


@dataclass(frozen=True)
class ExpectedInformationValueRecord:
    hypotheses_eliminable: str
    hypotheses_separated: str
    ambiguity_resolved: str
    uncertainty_remaining: str


@dataclass(frozen=True)
class HumanReviewDecision:
    options: tuple[str, ...] = ("APPROVE_FOR_IMPLEMENTATION", "REVISE", "REJECT", "DEFER")
    decision: str | None = None
    rationale: str | None = None


@dataclass(frozen=True)
class ScientificDesignReviewPackage:
    portfolio_id: str
    question: str
    theory_basis: str
    target_construct: str
    rivals: tuple[str, ...]
    null_model: str
    intervention: str
    controls: tuple[str, ...]
    confounders: tuple[str, ...]
    predictions: tuple[str, ...]
    falsifiers: tuple[str, ...]
    metrics: tuple[str, ...]
    expected_information_value: ExpectedInformationValueRecord
    identifiability_rating: str
    operationalization_gaps: tuple[str, ...]
    implementation_needs: tuple[str, ...]
    expected_cost: str
    major_interpretation_risks: tuple[str, ...]
    manipulation_checks: tuple[ManipulationCheckSpec, ...]
    replication_requirements: Mapping[str, str]
    negative_results_policy: Mapping[str, str]
    red_team_objections: tuple[str, ...]
    status: str = "READY_FOR_HUMAN_REVIEW"
    human_decision: HumanReviewDecision = HumanReviewDecision()


@dataclass(frozen=True)
class PortfolioScientificReview:
    portfolio_id: str
    technical_readiness: str
    scientific_readiness: ScientificReadiness
    constructs: Mapping[str, tuple[str, ...]]
    construct_status: ConstructStatus
    operationalizations: tuple[OperationalizationRecord, ...]
    rival_diagnosticity: Mapping[str, object]
    null_model_audit: Mapping[str, str]
    falsifiability_audit: Mapping[str, object]
    identifiability_audit: Mapping[str, object]
    intervention_purity: Mapping[str, object]
    control_adequacy: Mapping[str, object]
    metric_audit: tuple[MetricAuditRecord, ...]
    temporal_causality: Mapping[str, object]
    manipulation_checks: tuple[ManipulationCheckSpec, ...]
    information_value: ExpectedInformationValueRecord
    pareto_dimensions: Mapping[str, int]
    pareto_front: bool
    warnings: tuple[str, ...]
    deep_review: Mapping[str, object]


@dataclass(frozen=True)
class ScientificReviewReport:
    theory_snapshot: str
    portfolio_input_hash: str
    reviewer_version: str
    reviews: tuple[PortfolioScientificReview, ...]
    pareto_front: tuple[str, ...]
    top_candidates: tuple[str, ...]
    packages: tuple[ScientificDesignReviewPackage, ...]


_DETAILS = {
    "HYPERCAND-01": dict(status=ConstructStatus.PARTIAL, readiness=ScientificReadiness.OPERATIONALIZATION,
        roles=((),("prior knowledge","compositionality","learning-to-learn","causal world model"),(),(),(),("rapid generalization",)),
        proxies={"prior knowledge":"declared priors/training initialization","compositionality":"held-out recombination success","learning-to-learn":"adaptation curve across tasks","causal world model":"counterfactual prediction accuracy"},
        metric="sample efficiency on preregistered held-out task families", implemented=False,
        deep={"independence":"not established","prior_vs_exposure":"must match training exposure","compositionality":"requires an explicit held-out recombination protocol","rapid_generalization":"must be a learning curve, not endpoint accuracy","designs":("screening: main-effect matched ablations","fractional factorial: resolution-IV subset after interaction assumptions","sequential: screen, validate interactions, confirm"),"full_factorial":"16 cells before seeds; not recommended first"}),
    "HYPERCAND-02": dict(status=ConstructStatus.PARTIAL, readiness=ScientificReadiness.OPERATIONALIZATION,
        roles=((),("policy","environment weighting"),("agent","environment"),(),("percept","action"),("finite expected reward",)),
        proxies={"agent":"Terrario policy agent","environment":"finite preregistered environment suite","goal":"reward specification","percept":"recorded observation","action":"recorded action","value":"finite expected discounted reward"},
        metric="weighted expected reward over a finite environment suite", implemented=False,
        deep={"mathematical_target":"Legg-Hutter universal intelligence","empirical_scope":"FINITE_PROXY_ONLY","environment_family":"finite and preregistered","policy":"representable","expected_reward":"estimable with paired seeds","environment_weighting":"must be declared","complexity_proxy":"description-length proxy only","forbidden_label":"universal intelligence"}),
    "HYPERCAND-03": dict(status=ConstructStatus.CIRCULAR, readiness=ScientificReadiness.THEORY,
        roles=((),("plasticity",),("stability",),(),(),("retention","transfer","continual learning")),
        proxies={"plasticity":"change on new-task performance","stability":"bounded old-task degradation","retention":"old-task performance after learning","transfer":"held-out task performance"}, metric="separate retention and transfer curves", implemented=False,
        deep={"plasticity":"mechanism/capacity","stability":"constraint","retention":"outcome","transfer":"outcome/capacity","risk":"CONSTRUCT_CIRCULARITY_RISK"}),
    "HYPERCAND-04": dict(status=ConstructStatus.NOT_OPERATIONALIZED, readiness=ScientificReadiness.CAPABILITY,
        roles=((),("preparation","incubation","illumination","verification"),(),(),(),("creative achievement",)), proxies={}, metric="blinded novelty and utility score", implemented=False,
        deep={"causal_status":"historically descriptive only","candidate_designs":("stage omission","stage reorder","temporal interruption","alternative sequence","no-stage baseline"),"new_environment":"generative task with blinded novelty/utility evaluation and temporal process instrumentation"}),
    "HYPERCAND-05": dict(status=ConstructStatus.PARTIAL, readiness=ScientificReadiness.CAPABILITY,
        roles=((),("communication","coordination","division of labor"),("individual competence","shared memory","diversity"),(),("collective behavior",),("collective performance","cumulative culture")),
        proxies={"problem states":"shared multi-agent task state","actions":"per-agent action logs","preferences":"declared individual reward terms","shared memory":"common writable store","coordination":"time-resolved dependency between agents"}, metric="group transfer gain over matched independent agents", implemented=False,
        deep={"minimum_architecture":"multiple independently instrumented agents, constrained communication graph, private and shared memory, individual/group rewards, matched solo baseline","warning":"aggregate performance is not collective intelligence"}),
    "HYPERCAND-06": dict(status=ConstructStatus.NOT_OPERATIONALIZED, readiness=ScientificReadiness.CAPABILITY,
        roles=((),("iconic representation","categorical representation","sensory grounding"),(),(),("referential/compositional symbol use",),("meaningful symbols",)), proxies={}, metric="referential transfer to novel grounded contexts", implemented=False,
        deep={"perceptual_grounding":"partial grid observations exist","learned_categories":"not demonstrated","symbol_tokens":"internal labels do not suffice","referential_mapping":"not established","compositional_use":"not established","meaning_transfer":"not established","finding":"SEMANTIC_GROUNDING_NOT_ESTABLISHED"}),
    "HYPERCAND-07": dict(status=ConstructStatus.NOT_OPERATIONALIZED, readiness=ScientificReadiness.CAPABILITY,
        roles=((),("proof search","self-generated rewrite"),("axioms","utility","computational resources"),(),(),("certified self-rewrite",)), proxies={}, metric="verified utility improvement after reversible self-generated structural rewrite", implemented=False,
        deep={"ordinary_learning":"available only as ordinary updates","parameter_update":"not self-rewrite","meta_parameter_change":"not demonstrated","structural_self_modification":"missing","inspect":"missing","propose":"missing","execute":"missing","evaluate":"partial external evaluation","rollback":"missing","finding":"SELF_REWRITE_ENVIRONMENT_MISSING"}),
    "HYPERCAND-08": dict(status=ConstructStatus.PARTIAL, readiness=ScientificReadiness.CONTROL,
        roles=((),("world model","configurator"),("perception","memory","cost"),(),("actor","planning/action"),("autonomous planning/action",)),
        proxies={"perception":"AgentView observation channels","world model":"prediction state/model","memory":"recorded agent memory state","cost":"energy/action costs","actor":"policy action selection"}, metric="preregistered goal completion under OOD causal changes", implemented=False,
        deep={"component_mapping":{"perception":"EXACT","world model":"PARTIAL","memory":"PARTIAL","cost":"EXACT","actor":"PARTIAL","configurator":"MISSING"},"warning":"no existing component is renamed configurator by analogy"}),
}


def canonical_portfolio_payload(portfolio: ExperimentPortfolio) -> Mapping[str, object]:
    entries=[]
    for entry in portfolio.entries:
        entries.append({"portfolio_id": entry.family.source_hyperedge_id, "hyperedge": entry.family.source_hyperedge_id,
            "generator_version": entry.family.provenance.generator_version, "theory_snapshot": portfolio.snapshot_id,
            "review_state": entry.family.review_state.value, "family": _plain(entry.family), "design": _plain(entry.design) if entry.design else None,
            "technical_readiness": entry.readiness})
    return {"theory_snapshot":portfolio.snapshot_id,"entries":entries}


def payload_bytes(payload: Mapping[str, object]) -> bytes:
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",",":"), default=str).encode()


def _plain(value):
    if is_dataclass(value): return {f.name:_plain(getattr(value,f.name)) for f in fields(value)}
    if isinstance(value,Mapping): return {str(k):_plain(v) for k,v in value.items()}
    if isinstance(value,(tuple,list)): return [_plain(v) for v in value]
    if isinstance(value,Enum): return value.value
    return value


def review_portfolio(portfolio: ExperimentPortfolio) -> ScientificReviewReport:
    raw=payload_bytes(canonical_portfolio_payload(portfolio)); digest=hashlib.sha256(raw).hexdigest()
    provisional=[_review_entry(e) for e in portfolio.entries]
    fronts=_pareto_front(provisional)
    reviewed=tuple(_replace_front(r, r.portfolio_id in fronts) for r in provisional)
    # Selection is restricted to the non-dominated front; preference only makes output order deterministic.
    top=tuple(x for x in ("HYPERCAND-02","HYPERCAND-01","HYPERCAND-08") if x in fronts)[:3]
    packages=tuple(_package(next(r for r in reviewed if r.portfolio_id == pid), next(e for e in portfolio.entries if e.family.source_hyperedge_id == pid)) for pid in top)
    return ScientificReviewReport(portfolio.snapshot_id,digest,REVIEWER_VERSION,reviewed,tuple(sorted(fronts)),top,packages)


def _review_entry(entry: PortfolioEntry) -> PortfolioScientificReview:
    pid=entry.family.source_hyperedge_id; d=_DETAILS[pid]; components=tuple(sorted({c for h in entry.family.hypotheses for c in h.components}))
    roles=d["roles"]; labels=("constructs","mechanisms","resources","states","behaviors","outcomes")
    constructs={label:tuple(value) for label,value in zip(labels,roles)}
    ops=tuple(_operation(c,d) for c in components)
    null={"type":"absence of causal contribution / no difference under matched intervention","quality":"PARTIAL","limitation":"environmental and unmodeled alternative mechanisms remain compatible"}
    rival={"pair_count":len(entry.family.hypotheses)*(len(entry.family.hypotheses)-1)//2,"diagnostic_pairs":len(entry.design.predictions),"shared_predictions":"many subset rivals share direction","divergent_predictions":"component sensitivity under matched intervention","required_intervention":"independent component manipulation","observable":d["metric"],"status":"PARTIAL_RIVAL_DIAGNOSTICITY"}
    fals={"complete_fields":all(h.falsification and h.falsification.weakens and h.falsification.contradicts_in_regime and h.falsification.compatible_not_diagnostic and h.falsification.requires_redesign for h in entry.family.hypotheses),"pseudo_falsifiable":True,"reason":"thresholds and operational metrics remain undeclared, allowing post-hoc reinterpretation"}
    changing=("target availability","capacity","compute","representation distribution","temporal dynamics")
    ident={"classification":"DESCRIPTIVE_COMPARISON","variables_checked":("architecture","trainable parameters","total parameters","compute","observations","memory","optimization","training exposure","action space","environment","seed","opportunity distribution"),"unmatched":changing[1:],"causal_claim_allowed":False}
    purity={"target_effect":"component availability","side_effects":changing[1:],"classification":"LOW_INTERVENTION_PURITY","reason":"generated ablations do not yet specify matched substitution or sham implementation"}
    control={"classification":"DESCRIPTIVE_ONLY","adequate":False,"matching_required":("compute","parameters","experience","information access","seed","world"),"warning":"A4 vs A0 remains DESCRIPTIVE_ONLY without real matching"}
    metric=(MetricAuditRecord(d["metric"],entry.family.target_outcome,None,None,None,"UNKNOWN_UNTIL_PILOT",("construct underrepresentation","endpoint-only inference"),("reward/benchmark overfitting",),("task family","threshold selection"),d["implemented"]),)
    temporal={"required":any(x in (pid,entry.family.target_outcome.lower()) for x in ("HYPERCAND-03","HYPERCAND-04","learning","planning")),"cause_before_effect":"NOT_YET_SPECIFIED","windows":"PREREGISTRATION_REQUIRED","checks":("intervention timing","latency","persistence","delayed effects","carryover")}
    manip=tuple(ManipulationCheckSpec(c,f"instrument {c} access/state before and after intervention",f"target-specific signal changes while matched non-target signals remain within preregistered tolerance") for c in components)
    info=ExpectedInformationValueRecord("null or component-containing rivals after a valid component-sensitive result","subset rival versus null for manipulated components","whether a declared component contributes in the tested regime","necessity, sufficiency, external validity, and alternative mechanisms remain unresolved")
    dims=_dimensions(pid,d)
    warnings=tuple(dict.fromkeys((*entry.warnings,"NO_AUTOMATIC_APPROVAL","METRIC_NOT_IMPLEMENTED","UNMITIGATED_INTERVENTION_SIDE_EFFECTS")))
    return PortfolioScientificReview(pid,entry.readiness,d["readiness"],constructs,d["status"],ops,rival,null,fals,ident,purity,control,metric,temporal,manip,info,dims,False,warnings,d["deep"])


def _operation(component: str, detail: Mapping[str, object]) -> OperationalizationRecord:
    proxy=detail["proxies"].get(component); status=ProxyStatus.REASONABLE if proxy else ProxyStatus.NONE
    return OperationalizationRecord(component,"component",proxy,f"instrument {proxy}" if proxy else None,f"matched manipulation of {component}" if proxy else None,
        ("proxy isolates the named construct",) if proxy else (), ("construct-to-proxy mapping requires human validation",), "PARTIAL" if proxy else "NONE",status)


def _dimensions(pid: str, detail: Mapping[str, object]) -> Mapping[str, int]:
    table={"HYPERCAND-01":(2,2,1,3,1,3,3,3,1),"HYPERCAND-02":(2,3,2,3,3,2,3,3,2),"HYPERCAND-03":(1,2,1,2,2,2,3,2,1),"HYPERCAND-04":(1,2,1,2,1,1,2,2,1),"HYPERCAND-05":(2,2,1,3,1,1,3,3,1),"HYPERCAND-06":(1,2,1,2,1,2,3,2,1),"HYPERCAND-07":(1,3,1,2,1,1,3,3,2),"HYPERCAND-08":(2,3,2,3,2,2,3,3,2)}
    keys=("construct_clarity","falsifiability","identifiability","discriminating_power","implementation_ease","cost_efficiency","theoretical_relevance","information_value","interpretation_safety")
    return dict(zip(keys,table[pid]))


def _pareto_front(reviews: Iterable[PortfolioScientificReview]) -> set[str]:
    reviews=tuple(reviews); front=set()
    for a in reviews:
        av=tuple(a.pareto_dimensions.values())
        dominated=any(all(x>=y for x,y in zip(b.pareto_dimensions.values(),av)) and any(x>y for x,y in zip(b.pareto_dimensions.values(),av)) for b in reviews if b is not a)
        if not dominated: front.add(a.portfolio_id)
    return front


def _replace_front(r: PortfolioScientificReview, value: bool) -> PortfolioScientificReview:
    return replace(r, pareto_front=value)


def _package(review: PortfolioScientificReview, entry: PortfolioEntry) -> ScientificDesignReviewPackage:
    replication={"minimum_paired_seeds":"4 exploratory","confirmatory_seeds":"independent set, count fixed by prospective power/sensitivity analysis","determinism":"config/code/snapshot hashes and deterministic replay required","randomization":"preregister condition order and seed allocation","restart_policy":"restart only for preregistered infrastructure failure","invalid_run_policy":"exclude only by blinded validity gates","evidence_retention":"retain raw events, manifests, exclusions, and forensic windows"}
    negative={"null_result":"inconclusive unless manipulation and sensitivity checks pass","failure_to_learn":"validity/feasibility failure, not automatic refutation","failure_to_interact":"opportunity or interface failure until checked","unstable_agent":"invalid run under preregistered stability gate","no_behavioral_disruption":"weakens only after a successful manipulation check","failed_manipulation_check":"invalid treatment attribution"}
    objections=("construct-to-proxy mapping may be circular or incomplete","metric may reward benchmark-specific behavior","generated ablation changes capacity/compute/distribution","controls are specifications rather than implemented matched controls","environmental or alternative mechanisms can explain the same outcome","current predictions distinguish mainly each rival from the null, not every rival pair")
    return ScientificDesignReviewPackage(review.portfolio_id,f"Which declared components contribute to {entry.family.target_outcome} in a bounded Terrario regime?",entry.family.provenance.source_artifact,entry.family.target_outcome,
        tuple(h.id for h in entry.family.hypotheses if h.kind != "NULL_HYPOTHESIS"),next(h.id for h in entry.family.hypotheses if h.kind == "NULL_HYPOTHESIS"),"matched component intervention with manipulation check",tuple(c.control_type for c in entry.design.controls),tuple(c.description for c in entry.design.confounders),tuple(p.predicted_under_a+" vs "+p.predicted_under_b for p in entry.design.predictions),tuple(f.contradicts_in_regime for f in entry.design.falsification_rules),tuple(m.name for m in review.metric_audit),review.information_value,review.identifiability_audit["classification"],tuple(o.construct for o in review.operationalizations if o.proxy_validity == ProxyStatus.NONE),("implement metric","implement matched controls","instrument manipulation checks"),f"{entry.design.cost.runs} assumption-based runs; {entry.design.cost.estimated_wall_seconds}s estimated",review.warnings,review.manipulation_checks,replication,negative,objections)
