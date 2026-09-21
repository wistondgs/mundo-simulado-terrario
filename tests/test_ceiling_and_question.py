"""U2 and U3 on the two real ceilings, with the seven refusals.

The negative control matters as much as the two cases: if every result becomes
a ceiling and every target a question, the programme has bought two synonyms
for difficulty.
"""

from __future__ import annotations

import pytest

from terrario.lab.ceiling_probe import (
    BlockerClass, CeilingProbe, ProbeRefused, ceiling_probes_v1,
)
from terrario.lab.developmental import gap_analysis, graph_from_ledger, terrario_graph
from terrario.lab.question_type import QuestionType, Selection, derive_question
from terrario.lab.relation_ledger import (
    EvidenceClass, Scope, relation_ledger_v1,
)

AMBITO = Scope(world="w", organism="o", mechanism_family="f", campaign="c")


@pytest.fixture
def g():
    return graph_from_ledger(terrario_graph().capabilities, relation_ledger_v1())


@pytest.fixture
def probes():
    return ceiling_probes_v1()


def _probe(**cambios) -> CeilingProbe:
    base = dict(probe_id="CP-T", target_capability="T", source_result="NEG",
                source_result_ref="ref", scope=AMBITO,
                observed_blocker="algo bloqueó",
                blocker_class=BlockerClass.PRECURSOR_UNESTABLISHED,
                source_evidence_refs=("una medida",),
                candidate_missing_precursors=frozenset({"X"}),
                non_claims=("no dice que X sea requisito",))
    return CeilingProbe(**{**base, **cambios})


# --- U2 · las siete negativas ---------------------------------------------------------

def test_1_a_probe_without_a_source_scientific_result_is_refused():
    with pytest.raises(ProbeRefused, match="source_result"):
        _probe(source_result="  ")


def test_2_a_probe_without_scope_is_refused():
    with pytest.raises(TypeError):
        CeilingProbe(probe_id="x", target_capability="T", source_result="NEG",
                     source_result_ref="r", observed_blocker="b",
                     blocker_class=BlockerClass.PRECURSOR_UNESTABLISHED)


def test_3_a_probe_can_only_ever_emit_hypotheses(probes):
    """Structural, not reviewed: there is no path from a probe to a causal class.

    1.8 revealing that F(Z,A) cannot express the construct justifies naming
    EVSENS, REPUPD and HISTDIS. It does not license EVSENS REQUIRED_FOR
    PREDSTATE."""
    for probe in probes:
        for claim in probe.emitted_claims():
            assert claim.evidence is EvidenceClass.HYPOTHESIS
            assert not claim.is_measured
            assert claim.non_claim


def test_4_a_probe_read_from_nothing_is_refused():
    with pytest.raises(ProbeRefused, match="read from nothing"):
        _probe(source_evidence_refs=())


def test_5_a_probe_without_non_claims_is_refused():
    """Interpreting a blocker without saying what it does NOT license is how an
    interpretation becomes a theory."""
    with pytest.raises(ProbeRefused, match="does NOT license"):
        _probe(non_claims=())


def test_6_an_ordinary_negative_cannot_become_a_ceiling_for_free():
    """"The agent did not learn" is a result about the agent, not the ladder."""
    with pytest.raises(ProbeRefused, match="not developmental evidence"):
        _probe(blocker_class=BlockerClass.PERFORMANCE_ONLY)
    with pytest.raises(ProbeRefused, match="not developmental evidence"):
        _probe(blocker_class=BlockerClass.RESOURCE_OR_BUDGET)


def test_7_candidate_order_changes_neither_meaning_nor_output():
    """After the alphabetical failure: an ordering nobody chose must not carry
    meaning."""
    uno = _probe(candidate_missing_precursors=frozenset({"A", "B", "C"}),
                 candidate_family_questions=("q1", "q2"))
    otro = _probe(candidate_missing_precursors=frozenset({"C", "B", "A"}),
                  candidate_family_questions=("q2", "q1"))
    assert uno.content_identity == otro.content_identity
    assert uno.as_record() == otro.as_record()


def test_a_probe_that_proposes_nothing_is_refused():
    with pytest.raises(ProbeRefused, match="not a probe"):
        _probe(candidate_missing_precursors=frozenset(), candidate_lesions=frozenset(),
               candidate_family_questions=())


def test_the_scientific_result_survives_beside_the_interpretation(probes):
    """Two facts, not one replacing the other."""
    cp18 = next(p for p in probes if p.probe_id == "CP-18")
    registro = cp18.as_record()
    assert registro["scientific_result"] == "FAMILY_MISMATCH"
    assert registro["developmental_interpretation"] == "CEILING_PROBE"


# --- U3 · 1.8 ---------------------------------------------------------------------------

def test_18_derives_a_family_probe_and_orders_nothing(g, probes):
    q = derive_question("PREDSTATE", probes, gap_analysis(g, "PREDSTATE"))
    assert q.question_type is QuestionType.FAMILY_PROBE
    assert set(q.candidate_dimensions) == {"EVSENS", "REPUPD", "HISTDIS"}
    assert q.selection is Selection.UNRESOLVED


def test_18_does_not_propose_acquiring_the_target_or_one_candidate(g, probes):
    q = derive_question("PREDSTATE", probes, gap_analysis(g, "PREDSTATE"))
    assert q.question_type is not QuestionType.ACQUISITION_PROBE
    assert "PREDSTATE" not in q.candidate_dimensions
    assert len(q.candidate_dimensions) == 3


def test_18_never_turns_its_candidates_into_requirements(probes):
    from terrario.lab.relation_ledger import EffectForm, RelationSemantics

    cp18 = next(p for p in probes if p.probe_id == "CP-18")
    for claim in cp18.emitted_claims():
        assert claim.semantics is RelationSemantics.UNKNOWN_RELATION
        assert claim.effect is EffectForm.UNRESOLVED


# --- U3 · 1.5 ----------------------------------------------------------------------------

def test_15_derives_a_lesion_probe_on_psi(g, probes):
    q = derive_question("SELECTION", probes, gap_analysis(g, "SELECTION"))
    assert q.question_type is QuestionType.LESION_PROBE
    assert q.candidate_dimensions == ("PSI",)


def test_15_keeps_its_five_candidates_and_selects_none(g):
    r = gap_analysis(g, "SELECTION")
    assert r.premature
    assert set(r.tied_candidates) == {"LIMRET", "FUTVAL", "TEMPCRED", "SELPOL", "COADAPT"}


def test_15_asks_the_lesion_before_any_acquisition(g, probes):
    """psi is present, so «can it be acquired?» is the wrong question about the
    right object."""
    q = derive_question("SELECTION", probes, gap_analysis(g, "SELECTION"))
    assert q.question_type is not QuestionType.ACQUISITION_PROBE


# --- los dos controles --------------------------------------------------------------------

def test_the_positive_control_survives_u2_and_u3(g, probes):
    assert not gap_analysis(g, "PSI_USEFUL").premature
    q = derive_question("PSI_USEFUL", probes, gap_analysis(g, "PSI_USEFUL"))
    assert q.question_type is QuestionType.NONE_REQUIRED


def test_a_sufficiently_measured_dependency_generates_no_ceiling_probe(probes):
    """If every result ends up a ceiling, the label is vacuous.

    PSI_USEFUL's dependency on M is measured, scoped and supported, and no
    probe exists for it."""
    assert not [p for p in probes if p.target_capability == "PSI_USEFUL"]


def test_a_family_probe_outranks_a_lesion_when_both_would_apply():
    """No precursor repairs a mechanism that cannot state the construct."""
    from terrario.lab.developmental import GapReport

    familia = _probe(probe_id="CP-F", target_capability="T",
                     blocker_class=BlockerClass.FAMILY_CANNOT_EXPRESS,
                     candidate_family_questions=("¿puede la familia expresarlo?",))
    gap = GapReport(target="T", known=(), unknown=(), contradicted=(),
                    next_question=None, next_precursor=None, premature=True,
                    reason="", tied_candidates=("A",), lesion_candidates=("B",))
    q = derive_question("T", (familia,), gap)
    assert q.question_type is QuestionType.FAMILY_PROBE
