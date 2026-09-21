"""The two acceptance tests are the two ceilings.

A gap analyser that does not flag 1.5 and 1.8 as premature is wrong, whatever
else it does: those are the two targets the project actually reached for too
early, and they are the only ground truth available for this instrument.
"""

from __future__ import annotations

import pytest

from terrario.lab.developmental import (
    Capability, CapabilityState, DependencyKind, DevelopmentalEdge,
    DevelopmentalGraph, EvidenceState, gap_analysis, terrario_graph,
)


@pytest.fixture
def g():
    return terrario_graph()


# --- las dos pruebas de aceptación --------------------------------------------------

def test_level_15_is_flagged_premature(g):
    r = gap_analysis(g, "SELECTION")
    assert r.premature
    assert "none measured" in r.reason
    assert len(r.unknown) >= 5


def test_level_18_is_flagged_premature(g):
    r = gap_analysis(g, "PREDSTATE")
    assert r.premature
    assert len(r.unknown) >= 3


def test_the_contradicted_edge_of_18_survives_as_information(g):
    """A negative is not a failure: what 1.8 refuted belongs in the graph."""
    r = gap_analysis(g, "PREDSTATE")
    assert any("F(Z,A)" in c for c in r.contradicted)
    assert g.capabilities["PREDSTATE"].state is CapabilityState.NEGATIVE


def test_the_frozen_target_is_a_target_not_a_failure(g):
    assert g.capabilities["SELECTION"].state is CapabilityState.FROZEN_TARGET


# --- lo que hace que el veredicto signifique algo -------------------------------------

def test_a_target_with_one_measured_precursor_is_not_premature(g):
    """Otherwise `premature` would just mean "advanced", and every hard target
    would be flagged for ever."""
    r = gap_analysis(g, "PSI_USEFUL")
    assert not r.premature
    assert any("RB-7" in k for k in r.known)


def test_measured_and_read_are_not_the_same_evidence(g):
    """The distinction the whole programme rests on.

    `psi REQUIRES M` was measured -- psi's solo improvement is exactly zero.
    `M REQUIRES SELECTION` was read -- the temporal channel is a retention by
    construction, which is true and says nothing about acquirability."""
    medida = next(e for e in g.into("PSI_USEFUL")
                  if e.kind is DependencyKind.REQUIRES)
    leida = next(e for e in g.into("SELECTION")
                 if e.kind is DependencyKind.REQUIRES)
    assert medida.evidence is EvidenceState.MEASURED and medida.experiment
    assert leida.evidence is EvidenceState.READ and leida.experiment is None
    assert not gap_analysis(g, "PSI_USEFUL").premature
    assert gap_analysis(g, "SELECTION").premature


def test_an_edge_cannot_claim_measured_without_an_experiment():
    """The mutant for the one claim this module exists to refuse."""
    with pytest.raises(ValueError, match="claims MEASURED with no experiment"):
        DevelopmentalEdge(frozenset({"A"}), "B", DependencyKind.REQUIRES,
                          EvidenceState.MEASURED, basis="porque sí")


def test_an_edge_without_a_stated_basis_is_refused():
    with pytest.raises(ValueError, match="guess wearing a type"):
        DevelopmentalEdge(frozenset({"A"}), "B", DependencyKind.REQUIRES,
                          EvidenceState.CANDIDATE, basis="   ")


# --- la honestidad del "siguiente experimento" -----------------------------------------

def test_ties_are_reported_instead_of_resolved_by_the_alphabet(g):
    """A question chosen alphabetically and presented as derived would be worse
    than no question: it would look like the graph knew something."""
    for target, minimo in (("SELECTION", 5), ("PREDSTATE", 3)):
        r = gap_analysis(g, target)
        assert len(r.tied_candidates) >= minimo
        assert "the choice is yours" in r.next_question


def test_a_demonstrated_precursor_of_unknown_necessity_asks_for_a_lesion(g):
    """psi exists, so the question is not whether it can be acquired.

    It is whether removing it stops the target being acquirable -- requirement
    or scaffolding -- and that is a lesion, not an acquisition."""
    r = gap_analysis(g, "SELECTION")
    assert r.lesion_candidates == ("PSI",)
    assert "PSI" not in r.tied_candidates


def test_the_next_precursor_is_never_a_demonstrated_one(g):
    for target in ("SELECTION", "PREDSTATE"):
        r = gap_analysis(g, target)
        assert r.next_precursor not in g.demonstrated()


# --- genealogía y desarrollo son dos grafos --------------------------------------------

def test_chronology_is_not_dependency(g):
    """1.6 deliberately inherited nothing cognitive from 1.4, so the fact that
    it came afterwards is not an edge."""
    precursores_de_tempreg = {p for e in g.into("TEMPREG") for p in e.precursors}
    assert "PSI" not in precursores_de_tempreg
    assert g.into("TEMPREG") == ()
    # y sin embargo su genealogía está registrada
    assert "1.6" in g.capabilities["TEMPREG"].origin


def test_an_edge_to_an_unknown_capability_is_refused(g):
    with pytest.raises(ValueError, match="do not exist"):
        g.link(DevelopmentalEdge(frozenset({"NO_EXISTE"}), "SELECTION",
                                 DependencyKind.REQUIRES, EvidenceState.CANDIDATE,
                                 basis="inventada"))


def test_a_target_nobody_mapped_is_premature_too():
    """Silence is not evidence of readiness."""
    g = DevelopmentalGraph()
    g.add(Capability("X", "algo", CapabilityState.CANDIDATE))
    r = gap_analysis(g, "X")
    assert r.premature and "not in the graph yet" in r.reason
