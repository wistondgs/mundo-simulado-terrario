"""Contracts for the typed ledger, and the three refusals that are structural.

Each refusal exists because a textual prohibition of the same thing already
failed somewhere in this project.
"""

from __future__ import annotations

import pytest

from terrario.lab.relation_ledger import (
    CAUSAL_CLASSES, EffectForm, EpistemicStatus, EvidenceClass, HypothesisOrigin,
    LedgerRefused, RelationClaim, RelationSemantics, Scope, meets_policy,
    relation_ledger_v1,
)

AMBITO = Scope(world="w", organism="o", mechanism_family="f", campaign="c")


def _claim(**cambios) -> RelationClaim:
    base = dict(precursors=frozenset({"A"}), target="B",
                semantics=RelationSemantics.REQUIRES, effect=EffectForm.NECESSARY,
                evidence=EvidenceClass.VERIFIED_CODE,
                status=EpistemicStatus.SUPPORTED, basis="porque el código lo dice")
    return RelationClaim(**{**base, **cambios})


# --- M2 · el scope se rechaza, no se pide -------------------------------------------

def test_a_causal_claim_without_scope_is_refused():
    """A relation measured in one world is not a law, and prose saying so has
    never stopped anyone."""
    with pytest.raises(LedgerRefused, match="no scope"):
        _claim(evidence=EvidenceClass.MEASURED_FACTORIAL, evidence_ref="ref")


def test_the_same_claim_with_scope_is_accepted():
    assert _claim(evidence=EvidenceClass.MEASURED_FACTORIAL,
                  evidence_ref="ref", scope=AMBITO).is_measured


def test_a_scope_missing_its_world_is_refused():
    with pytest.raises(ValueError, match="non-empty world"):
        Scope(world="  ", organism="o", mechanism_family="f", campaign="c")


# --- la afirmación que el ledger existe para refusar ---------------------------------

def test_an_executed_class_without_an_evidence_ref_is_refused():
    with pytest.raises(LedgerRefused, match="no evidence_ref"):
        _claim(evidence=EvidenceClass.MEASURED_LESION, scope=AMBITO)


def test_a_deterministic_replication_also_needs_its_reference():
    """The class exists because 1.6 produced it; it still has to point at the
    replay that was run."""
    with pytest.raises(LedgerRefused, match="no evidence_ref"):
        _claim(evidence=EvidenceClass.REPLICATED_DETERMINISTIC)
    assert _claim(evidence=EvidenceClass.REPLICATED_DETERMINISTIC,
                  evidence_ref="1.6 · réplica celda a celda 5e-5").is_read


# --- M3 · procedencia de hipótesis ---------------------------------------------------

def test_a_hypothesis_without_a_stated_origin_is_refused():
    """Otherwise the ban on a model deciding causal necessity is unauditable:
    a generated candidate and a human one become the same row."""
    with pytest.raises(LedgerRefused, match="no stated origin"):
        _claim(evidence=EvidenceClass.HYPOTHESIS, status=EpistemicStatus.UNRESOLVED)


def test_every_hypothesis_in_the_ledger_names_who_proposed_it():
    for claim in relation_ledger_v1():
        if claim.evidence is EvidenceClass.HYPOTHESIS:
            assert claim.origin is not HypothesisOrigin.NOT_A_HYPOTHESIS, claim.claim_id


def test_the_ladder_of_18_is_marked_as_derived_from_its_negative():
    derivadas = [c for c in relation_ledger_v1()
                 if c.origin is HypothesisOrigin.DERIVED_FROM_NEGATIVE]
    assert {c.precursors for c in derivadas} == {
        frozenset({"EVSENS"}), frozenset({"REPUPD"}), frozenset({"HISTDIS"})}


# --- M4 · una supersesión nombra a su sucesora ----------------------------------------

def test_a_superseded_claim_must_name_its_successor():
    """1.5 went through four supersessions and which one governed had to be
    reconciled by hand."""
    with pytest.raises(LedgerRefused, match="does not name its successor"):
        _claim(status=EpistemicStatus.SUPERSEDED)
    assert _claim(status=EpistemicStatus.SUPERSEDED, superseded_by="REL-099")


# --- dirección y forma ------------------------------------------------------------------

def test_the_direction_is_stated_not_implied():
    assert _claim().label() == "B --REQUIRES--> A"


def test_a_capability_cannot_be_its_own_precursor():
    with pytest.raises(LedgerRefused, match="its own precursor"):
        _claim(precursors=frozenset({"B"}))


def test_a_claim_without_a_basis_is_refused():
    with pytest.raises(LedgerRefused, match="guess wearing a type"):
        _claim(basis="   ")


# --- U4 · la política es por tipo de afirmación -----------------------------------------

def test_structural_presence_clears_on_code_and_causal_necessity_does_not():
    """Requiring an experiment to check that a branch exists would be as wrong
    as accepting a code reading as a causal fact."""
    estructural = _claim(effect=EffectForm.FACILITATING,
                         evidence=EvidenceClass.VERIFIED_CODE)
    causal = _claim(effect=EffectForm.NECESSARY, evidence=EvidenceClass.VERIFIED_CODE)
    assert meets_policy(estructural)
    assert not meets_policy(causal)


def test_synergy_needs_a_factorial_specifically():
    lesion = _claim(effect=EffectForm.SYNERGISTIC,
                    evidence=EvidenceClass.MEASURED_LESION,
                    evidence_ref="ref", scope=AMBITO)
    factorial = _claim(effect=EffectForm.SYNERGISTIC,
                       evidence=EvidenceClass.MEASURED_FACTORIAL,
                       evidence_ref="ref", scope=AMBITO)
    assert not meets_policy(lesion) and meets_policy(factorial)


def test_a_contradicted_claim_never_meets_policy():
    assert not meets_policy(_claim(effect=EffectForm.NECESSARY,
                                   evidence=EvidenceClass.MEASURED_FACTORIAL,
                                   status=EpistemicStatus.CONTRADICTED,
                                   evidence_ref="ref", scope=AMBITO))


# --- el inventario real -------------------------------------------------------------------

def test_every_causal_row_of_the_ledger_carries_its_scope():
    for claim in relation_ledger_v1():
        if claim.evidence in CAUSAL_CLASSES:
            assert claim.scope is not None, claim.claim_id
            assert claim.non_claim, f"{claim.claim_id} mide y no dice qué NO afirma"


def test_the_only_measured_edge_says_it_is_not_a_universal_law():
    medida = next(c for c in relation_ledger_v1() if c.claim_id == "REL-001")
    assert "universal" in medida.non_claim
    assert medida.scope.campaign == "organism-remembered-binding-01"


def test_claim_ids_are_unique():
    ids = [c.claim_id for c in relation_ledger_v1()]
    assert len(ids) == len(set(ids)) == 15
