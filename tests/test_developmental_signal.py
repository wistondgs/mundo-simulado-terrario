"""U2.1 · a wall that was hit is not a capability that was never attempted.

Level 1.8 ran and produced FAMILY_MISMATCH. Level 1.5 never ran. Writing both
as "reached a ceiling" would give the second the authority of the first, and
the ledger would say the organism hit a wall in an experiment that does not
exist.
"""

from __future__ import annotations

import pytest

from terrario.lab.developmental import gap_analysis, graph_from_ledger, terrario_graph
from terrario.lab.developmental_signal import (
    BlockerClass, DesignHold, ObservedCeiling, SignalOrigin, SignalRefused,
    design_holds, developmental_signals_v1, observed_ceilings,
)
from terrario.lab.question_type import QuestionType, Selection, derive_question
from terrario.lab.relation_ledger import EvidenceClass, Scope, relation_ledger_v1

AMBITO = Scope(world="w", organism="o", mechanism_family="f", campaign="c")


@pytest.fixture
def g():
    return graph_from_ledger(terrario_graph().capabilities, relation_ledger_v1())


@pytest.fixture
def signals():
    return developmental_signals_v1()


def _ceiling(**cambios) -> ObservedCeiling:
    base = dict(signal_id="OC-T", target_capability="T",
                source_result="FAMILY_MISMATCH", source_result_ref="ref",
                scope=AMBITO, rationale="la familia no lo expresa",
                blocker_class=BlockerClass.FAMILY_CANNOT_EXPRESS,
                source_evidence_refs=("una medida",),
                candidate_missing_precursors=frozenset({"X"}),
                non_claims=("no dice que X sea requisito",))
    return ObservedCeiling(**{**base, **cambios})


def _hold(**cambios) -> DesignHold:
    base = dict(signal_id="DH-T", target_capability="T",
                source_decision="FROZEN_BY_DESIGN", decision_ref="ref",
                scope=AMBITO, rationale="no está justificado intentarlo",
                unresolved_precursors=frozenset({"X"}),
                non_claims=("no hubo ejecución",))
    return DesignHold(**{**base, **cambios})


# --- 1 · un techo observado sin resultado de campaña ---------------------------------

def test_1_an_observed_ceiling_without_a_campaign_result_is_refused():
    with pytest.raises(SignalRefused, match="source_result"):
        _ceiling(source_result="   ")
    with pytest.raises(SignalRefused, match="read from nothing"):
        _ceiling(source_evidence_refs=())


# --- 2 · FROZEN_BY_DESIGN no puede ser un techo observado -----------------------------

def test_2_frozen_by_design_cannot_build_an_observed_ceiling():
    """A capability that was never attempted reached no ceiling."""
    with pytest.raises(SignalRefused, match="never attempted reached no ceiling"):
        _ceiling(source_result="FROZEN_BY_DESIGN")
    for marca in ("NOT_ATTEMPTED", "DESIGN_ONLY", "frozen"):
        with pytest.raises(SignalRefused, match="not an execution outcome"):
            _ceiling(source_result=marca)


# --- 3 · una congelación sin decisión -------------------------------------------------

def test_3_a_design_hold_without_a_decision_is_refused():
    with pytest.raises(SignalRefused, match="source_decision"):
        _hold(source_decision="  ")
    with pytest.raises(SignalRefused, match="decision_ref"):
        _hold(decision_ref="")


# --- 4 · y el simétrico: un resultado disfrazado de decisión --------------------------

def test_4_a_campaign_outcome_cannot_be_passed_off_as_a_decision():
    """Erasing that the experiment did happen is the mirror of contract 2."""
    for desenlace in ("FAMILY_MISMATCH", "POSITIVE", "verified"):
        with pytest.raises(SignalRefused, match="not a design decision"):
            _hold(source_decision=desenlace)


# --- 5 · ninguno puede llegar a causalidad -------------------------------------------

def test_5_both_kinds_can_only_ever_emit_hypotheses(signals):
    for signal in signals:
        emitidas = signal.emitted_claims()
        assert emitidas
        for claim in emitidas:
            assert claim.evidence is EvidenceClass.HYPOTHESIS
            assert not claim.is_measured
            assert claim.non_claim


# --- 6 · el censo de techos excluye las congelaciones ---------------------------------

def test_6_the_census_of_observed_ceilings_excludes_holds(signals):
    """The ledger must never say 1.5 hit a ceiling."""
    assert [c.signal_id for c in observed_ceilings(signals)] == ["OC-18"]
    assert [h.signal_id for h in design_holds(signals)] == ["DH-15"]
    assert "SELECTION" not in {c.target_capability for c in observed_ceilings(signals)}


# --- 7 · U3 conserva sus tres salidas, y ahora dice de dónde vienen -------------------

def test_7_u3_keeps_its_three_outputs_and_names_their_provenance(g, signals):
    esperado = {
        "PREDSTATE": (QuestionType.FAMILY_PROBE, Selection.UNRESOLVED,
                      "ObservedCeiling:OC-18"),
        "SELECTION": (QuestionType.LESION_PROBE, Selection.RESOLVED,
                      "DesignHold:DH-15"),
        "PSI_USEFUL": (QuestionType.NONE_REQUIRED, Selection.RESOLVED, ""),
    }
    for target, (tipo, seleccion, procedencia) in esperado.items():
        q = derive_question(target, signals, gap_analysis(g, target))
        assert q.question_type is tipo, target
        assert q.selection is seleccion, target
        assert q.provenance == procedencia, target
    q18 = derive_question("PREDSTATE", signals, gap_analysis(g, "PREDSTATE"))
    assert set(q18.candidate_dimensions) == {"EVSENS", "REPUPD", "HISTDIS"}
    assert derive_question("SELECTION", signals,
                           gap_analysis(g, "SELECTION")).candidate_dimensions == ("PSI",)


def test_7b_a_hold_cannot_produce_a_family_probe():
    """Only an execution can report that a family failed to express something."""
    from terrario.lab.developmental import GapReport

    hold = _hold(candidate_family_questions=("¿puede la familia expresarlo?",))
    gap = GapReport(target="T", known=(), unknown=(), contradicted=(),
                    next_question=None, next_precursor=None, premature=True,
                    reason="", tied_candidates=("X",))
    q = derive_question("T", (hold,), gap)
    assert q.question_type is not QuestionType.FAMILY_PROBE


# --- 8 · el orden no cambia nada -------------------------------------------------------

def test_8_candidate_order_changes_neither_identity_nor_derivation():
    uno = _ceiling(candidate_missing_precursors=frozenset({"A", "B", "C"}),
                   candidate_family_questions=("q1", "q2"))
    otro = _ceiling(candidate_missing_precursors=frozenset({"C", "B", "A"}),
                    candidate_family_questions=("q2", "q1"))
    assert uno.content_identity == otro.content_identity
    assert uno.as_record() == otro.as_record()

    h1 = _hold(unresolved_precursors=frozenset({"A", "B"}))
    h2 = _hold(unresolved_precursors=frozenset({"B", "A"}))
    assert h1.content_identity == h2.content_identity


# --- 9 · un negativo corriente sigue sin ascender -------------------------------------

def test_9_performance_and_budget_blockers_are_still_refused():
    for clase in (BlockerClass.PERFORMANCE_ONLY, BlockerClass.RESOURCE_OR_BUDGET):
        with pytest.raises(SignalRefused, match="not developmental evidence"):
            _ceiling(blocker_class=clase)


# --- 10 · el control negativo ----------------------------------------------------------

def test_10_the_positive_control_generates_neither_signal_nor_question(g, signals):
    assert not [s for s in signals if s.target_capability == "PSI_USEFUL"]
    assert not gap_analysis(g, "PSI_USEFUL").premature
    q = derive_question("PSI_USEFUL", signals, gap_analysis(g, "PSI_USEFUL"))
    assert q.question_type is QuestionType.NONE_REQUIRED


# --- la demostración que se pidió explícitamente ---------------------------------------

def test_frozen_by_design_is_not_an_observed_ceiling(signals):
    dh = next(h for h in design_holds(signals) if h.signal_id == "DH-15")
    oc = next(c for c in observed_ceilings(signals) if c.signal_id == "OC-18")

    assert dh.origin is SignalOrigin.DESIGN_DECISION
    assert oc.origin is SignalOrigin.OBSERVED_EXECUTION
    assert dh.as_record()["signal_kind"] == "DESIGN_HOLD"
    assert oc.as_record()["signal_kind"] == "OBSERVED_CEILING"
    # 1.5 no tiene resultado científico, porque no hubo campaña
    assert "scientific_result" not in dh.as_record()
    assert oc.as_record()["scientific_result"] == "FAMILY_MISMATCH"
    # y lo dice en su propio non_claim
    assert any("no hubo ejecución" in n for n in dh.non_claims)


def test_no_new_causal_claim_was_created(signals):
    """U2.1 creates interpretations, never evidence."""
    from terrario.lab.relation_ledger import CAUSAL_CLASSES

    emitidas = [c for s in signals for c in s.emitted_claims()]
    assert emitidas
    assert not [c for c in emitidas if c.evidence in CAUSAL_CLASSES]
    del_ledger = [c for c in relation_ledger_v1() if c.evidence in CAUSAL_CLASSES]
    assert len(del_ledger) == 3  # las mismas tres de U1, ni una más
