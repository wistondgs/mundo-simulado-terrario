from terrario.lab.api import LabAPI
from functools import lru_cache
from terrario.lab.theory.scientific_review import (
    ConstructStatus, HumanReviewDecision, ProxyStatus, ScientificReadiness,
    canonical_portfolio_payload, payload_bytes, review_portfolio,
)


@lru_cache(maxsize=1)
def report(): return review_portfolio(LabAPI(".").experiment_portfolio)
def review(pid): return next(r for r in report().reviews if r.portfolio_id == pid)


def test_portfolio_freeze_is_deterministic_and_complete():
    api=LabAPI("."); a=payload_bytes(canonical_portfolio_payload(api.experiment_portfolio)); b=payload_bytes(canonical_portfolio_payload(api.experiment_portfolio))
    assert a == b and len(report().reviews) == 8 and len(report().portfolio_input_hash) == 64


def test_construct_circularity_is_not_resolved_by_invention():
    assert review("HYPERCAND-03").construct_status == ConstructStatus.CIRCULAR
    assert review("HYPERCAND-04").construct_status == ConstructStatus.NOT_OPERATIONALIZED


def test_proxy_validity_keeps_construct_separate_from_proxy():
    ops=review("HYPERCAND-02").operationalizations
    assert all(o.operational_proxy != o.construct for o in ops if o.operational_proxy)
    assert {o.proxy_validity for o in ops} <= {ProxyStatus.REASONABLE,ProxyStatus.NONE}


def test_rival_quantity_is_not_diagnosticity():
    audit=review("HYPERCAND-02").rival_diagnosticity
    assert audit["pair_count"] > audit["diagnostic_pairs"] and audit["status"] == "PARTIAL_RIVAL_DIAGNOSTICITY"


def test_null_model_has_scope_and_limitation():
    audit=review("HYPERCAND-01").null_model_audit
    assert "no difference" in audit["type"] and "alternative" in audit["limitation"]


def test_intervention_purity_records_target_and_side_effects():
    audit=review("HYPERCAND-08").intervention_purity
    assert audit["target_effect"] and audit["side_effects"] and audit["classification"] == "LOW_INTERVENTION_PURITY"


def test_causal_identification_lists_all_changed_dimensions():
    audit=review("HYPERCAND-08").identifiability_audit
    assert audit["classification"] == "DESCRIPTIVE_COMPARISON" and len(audit["variables_checked"]) == 12 and not audit["causal_claim_allowed"]


def test_temporal_hypotheses_require_ordering_and_windows():
    audit=review("HYPERCAND-04").temporal_causality
    assert audit["required"] and audit["cause_before_effect"] == "NOT_YET_SPECIFIED" and "carryover" in audit["checks"]


def test_hypercand08_component_mapping_does_not_rename_configurator():
    mapping=review("HYPERCAND-08").deep_review["component_mapping"]
    assert mapping["configurator"] == "MISSING" and set(mapping.values()) <= {"EXACT","PARTIAL","ANALOGICAL","MISSING"}


def test_every_intervention_has_a_manipulation_check():
    for r in report().reviews:
        assert r.manipulation_checks and all(x.pass_condition and x.failure_consequence == "INVALID_TREATMENT_ATTRIBUTION" for x in r.manipulation_checks)


def test_negative_results_are_not_automatic_refutations():
    for package in report().packages:
        assert "not automatic refutation" in package.negative_results_policy["failure_to_learn"]
        assert "invalid" in package.negative_results_policy["failed_manipulation_check"]


def test_pareto_selection_uses_only_non_dominated_candidates():
    result=report(); assert 0 < len(result.top_candidates) <= 3
    assert set(result.top_candidates) <= set(result.pareto_front)


def test_red_team_objections_are_preserved_in_review_package():
    assert all(len(p.red_team_objections) >= 6 and p.status == "READY_FOR_HUMAN_REVIEW" for p in report().packages)


def test_human_review_gate_has_no_automatic_decision():
    for package in report().packages:
        assert isinstance(package.human_decision,HumanReviewDecision)
        assert package.human_decision.decision is None and package.human_decision.rationale is None


def test_technical_and_scientific_readiness_are_independent():
    r=review("HYPERCAND-07")
    assert r.technical_readiness == "CPU_READY" and r.scientific_readiness == ScientificReadiness.CAPABILITY
