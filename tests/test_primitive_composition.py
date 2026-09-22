"""El mapa de composición primitiva · lo que se niega a sostener.

Every refusal here exists because the corresponding rule, written as prose,
is the failure mode this project keeps finding in its own history.
"""

from __future__ import annotations

import pytest

from terrario.lab.hypergraph.primitive_composition import (
    EXCLUDED, NONE_OUTPUT, CompositionStatus, Cost, DegreeOfFreedom, Hyperedge,
    MapRefused, Primitive, delta_df, edges_v01, genuine_interaction,
    primitives_v01, replicated, unlocking_element,
)

W = "W-test"


def _edge(**cambios):
    base = dict(id="Hx", inputs=frozenset({"P01", "P02"}), world=W, output="E900",
                status=CompositionStatus.HYPOTHESIS)
    return Hyperedge(**{**base, **cambios})


# --- un emergente no nace con nombre -------------------------------------------------

@pytest.mark.parametrize("nombre", ["attention", "REASONING", "agencia",
                                    "memoria_episodica", "theory_of_mind"])
def test_an_emergent_cannot_be_born_named_after_a_faculty(nombre):
    """Naming it on the day it appears is how a measurement becomes a theory
    without passing through evidence."""
    with pytest.raises(MapRefused, match="names a whole faculty"):
        _edge(output=nombre)


def test_an_emergent_must_be_an_E_number_or_nothing():
    with pytest.raises(MapRefused, match="neither NONE nor an E"):
        _edge(output="something_measurable")


def test_E_numbers_and_NONE_are_both_fine():
    assert _edge(output="E001").output == "E001"
    assert _edge(output=NONE_OUTPUT, status=CompositionStatus.NO_EFFECT,
                 evidence="x").output == NONE_OUTPUT


# --- el mundo viaja con la arista ------------------------------------------------------

def test_an_edge_without_a_world_is_refused():
    with pytest.raises(MapRefused, match="no world"):
        _edge(world="  ")


def test_the_same_composition_in_two_worlds_is_two_conditions_not_a_contradiction():
    """This is why the world travels with the edge at all."""
    aristas = edges_v01()
    a = next(e for e in aristas if e.id == "H004")
    b = next(e for e in aristas if e.id == "H005")
    assert a.inputs == b.inputs
    assert a.world != b.world
    assert a.status is CompositionStatus.OBSERVED
    assert b.status is CompositionStatus.NO_EFFECT
    assert CompositionStatus.CONTRADICTED not in {a.status, b.status}


# --- la ausencia de emergencia es un resultado -----------------------------------------

def test_no_effect_cannot_carry_an_output():
    with pytest.raises(MapRefused, match="something happened"):
        _edge(output="E001", status=CompositionStatus.NO_EFFECT, evidence="x")


def test_no_effect_cannot_carry_a_degree_of_freedom():
    with pytest.raises(MapRefused, match="something happened"):
        _edge(output=NONE_OUTPUT, status=CompositionStatus.NO_EFFECT, evidence="x",
              new_degrees_of_freedom={DegreeOfFreedom.ACTION_RANGE})


def test_observing_nothing_without_saying_no_effect_is_refused():
    """Absence of emergence has its own status; it is not a quiet blank."""
    with pytest.raises(MapRefused, match="absence of emergence is a result"):
        _edge(output=NONE_OUTPUT, status=CompositionStatus.OBSERVED, evidence="x")


def test_the_no_effect_row_is_what_identifies_the_unlocking_element():
    """`{A} -> nothing` is not a gap. It is the row that later names the
    element that unlocked the composition."""
    assert unlocking_element(edges_v01()) == (("P04", "H003"),)


def test_with_no_empty_row_nothing_is_identified_as_unlocking():
    solas = tuple(e for e in edges_v01() if e.status is not CompositionStatus.NO_EFFECT)
    assert unlocking_element(solas) == ()


# --- la replicación se calcula, no se declara --------------------------------------------

def test_an_edge_cannot_declare_itself_replicated():
    with pytest.raises(MapRefused, match="computed over several worlds"):
        _edge(status=CompositionStatus.REPLICATED, evidence="x")


def test_replication_needs_two_worlds_and_is_computed():
    uno = _edge(id="H1", output="E001", status=CompositionStatus.OBSERVED,
                evidence="a", world="W-a")
    otro = _edge(id="H2", output="E001", status=CompositionStatus.OBSERVED,
                 evidence="b", world="W-b")
    assert replicated([uno]) == ()
    assert replicated([uno, otro]) == ((frozenset({"P01", "P02"}), "E001"),)


def test_the_same_world_twice_is_not_replication():
    uno = _edge(id="H1", output="E001", status=CompositionStatus.OBSERVED,
                evidence="a", world="W-a")
    bis = _edge(id="H2", output="E001", status=CompositionStatus.OBSERVED,
                evidence="a2", world="W-a")
    assert replicated([uno, bis]) == ()


def test_nothing_in_the_historical_import_is_replicated():
    assert replicated(edges_v01()) == ()


# --- interacción genuina · E003 > E001 + E002 ---------------------------------------------

def test_a_composition_that_is_the_union_of_its_parts_shows_no_excess():
    a = _edge(id="A", inputs=frozenset({"P01"}), output="E001",
              status=CompositionStatus.OBSERVED, evidence="x",
              new_degrees_of_freedom={DegreeOfFreedom.STATE_DISCRIMINATION})
    b = _edge(id="B", inputs=frozenset({"P02"}), output="E002",
              status=CompositionStatus.OBSERVED, evidence="x",
              new_degrees_of_freedom={DegreeOfFreedom.ACTION_RANGE})
    ab = _edge(id="AB", inputs=frozenset({"P01", "P02"}), output="E003",
               status=CompositionStatus.OBSERVED, evidence="x",
               new_degrees_of_freedom={DegreeOfFreedom.STATE_DISCRIMINATION,
                                       DegreeOfFreedom.ACTION_RANGE})
    assert genuine_interaction([a, b, ab], ab) == frozenset()


def test_a_degree_of_freedom_no_smaller_combination_showed_is_the_finding():
    a = _edge(id="A", inputs=frozenset({"P01"}), output="E001",
              status=CompositionStatus.OBSERVED, evidence="x",
              new_degrees_of_freedom={DegreeOfFreedom.STATE_DISCRIMINATION})
    ab = _edge(id="AB", inputs=frozenset({"P01", "P02"}), output="E003",
               status=CompositionStatus.OBSERVED, evidence="x",
               new_degrees_of_freedom={DegreeOfFreedom.STATE_DISCRIMINATION,
                                       DegreeOfFreedom.TEMPORAL_CONDITIONING})
    assert genuine_interaction([a, ab], ab) == frozenset(
        {DegreeOfFreedom.TEMPORAL_CONDITIONING})


def test_a_smaller_combination_in_another_world_does_not_discount_the_excess():
    """Two worlds are two conditions here too."""
    a = _edge(id="A", inputs=frozenset({"P01"}), output="E001", world="W-otro",
              status=CompositionStatus.OBSERVED, evidence="x",
              new_degrees_of_freedom={DegreeOfFreedom.TEMPORAL_CONDITIONING})
    ab = _edge(id="AB", inputs=frozenset({"P01", "P02"}), output="E003",
               status=CompositionStatus.OBSERVED, evidence="x",
               new_degrees_of_freedom={DegreeOfFreedom.TEMPORAL_CONDITIONING})
    assert genuine_interaction([a, ab], ab) == frozenset(
        {DegreeOfFreedom.TEMPORAL_CONDITIONING})


# --- ΔDF, y que cero también es resultado --------------------------------------------------

def test_a_rung_that_adds_nothing_reports_zero_rather_than_being_skipped():
    a = _edge(id="A", inputs=frozenset({"P01"}), output="E001",
              status=CompositionStatus.OBSERVED, evidence="x",
              new_degrees_of_freedom={DegreeOfFreedom.STATE_DISCRIMINATION})
    escalera = [("N1.0", frozenset({"P01"})),
                ("N1.1", frozenset({"P01", "P02"})),
                ("N1.2", frozenset({"P01", "P02", "P03"}))]
    filas = delta_df(escalera, [a], W)
    assert [f["delta_df"] for f in filas] == [1, 0, 0]
    assert filas[1]["gained"] == []


def test_the_historical_import_yields_a_ladder_of_zeros():
    """The finding of this whole import, and it is not a bug in the ladder.

    The old programme measured whether a concrete organism acquired a concrete
    capability. It never asked which degree of freedom widened, so nothing it
    produced can populate this column -- which is exactly why the new
    programme has to run its own experiments rather than re-read the old ones."""
    escalera = [("S1", frozenset({"P03"})), ("S2", frozenset({"P03", "P04"}))]
    filas = delta_df(escalera, edges_v01(), "W-level1-grid")
    assert [f["delta_df"] for f in filas] == [0, 0]
    assert all(not e.new_degrees_of_freedom for e in edges_v01())


# --- las primitivas responden seis preguntas y ninguna más --------------------------------

def test_there_are_twenty_and_they_are_P01_to_P20():
    p = primitives_v01()
    assert [x.id for x in p] == [f"P{n:02d}" for n in range(1, 21)]


def test_every_primitive_says_what_it_cannot_do():
    """A primitive that only says what it can do grows in the reader's head
    until it is a faculty again."""
    for prim in primitives_v01():
        assert prim.cannot.strip(), prim.id
        assert prim.detection.strip(), prim.id
        assert prim.provenance.strip(), prim.id


def test_a_primitive_missing_one_of_the_six_questions_is_refused():
    with pytest.raises(MapRefused, match="is not yet minimal"):
        Primitive(id="P99", name="x", can="something", cannot="",
                  detection="looking")


def test_a_primitive_id_must_be_P_and_digits():
    with pytest.raises(MapRefused, match="P followed by digits"):
        Primitive(id="attention", name="x", can="a", cannot="b", detection="c")


def test_requirements_point_at_primitives_that_exist():
    ids = {p.id for p in primitives_v01()}
    for prim in primitives_v01():
        assert set(prim.requires) <= ids, prim.id


def test_the_thirteen_decomposed_say_they_were_decomposed():
    """Their source concept is cited and the cutting is declared as mine, not
    read off the corpus."""
    nuevas = [p for p in primitives_v01() if int(p.id[1:]) >= 8]
    assert len(nuevas) == 13
    for prim in nuevas:
        assert prim.provenance.startswith("DECOMPOSED from"), prim.id


def test_the_seven_seeds_carry_their_frozen_campaign():
    semillas = [p for p in primitives_v01() if int(p.id[1:]) <= 7]
    assert len(semillas) == 7
    for prim in semillas:
        assert "HISTORICAL seed" in prim.provenance, prim.id


def test_what_was_excluded_is_written_down_with_its_reason():
    """A map that lists only what got in gives nobody a way to check the
    exclusion criterion."""
    assert len(EXCLUDED) == 5
    for nombre, razon in EXCLUDED:
        assert nombre.strip() and len(razon) > 40


# --- lo que el mapa no dice --------------------------------------------------------------

def test_the_map_declares_no_target_and_no_final_architecture():
    import ast
    import inspect

    from terrario.lab.hypergraph import primitive_composition

    arbol = ast.parse(inspect.getsource(primitive_composition))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Expr) and isinstance(nodo.value, ast.Constant) \
                and isinstance(nodo.value.value, str):
            nodo.value.value = ""
    codigo = ast.unparse(arbol)
    for prohibido in ("TARGET_CAPABILITY", "FINAL_ARCHITECTURE", "INTELLIGENCE_LEVEL",
                      "EXPECTED_", "GOAL_"):
        assert prohibido not in codigo, prohibido


def test_there_are_exactly_six_statuses():
    assert len(list(CompositionStatus)) == 6


def test_edges_carry_no_cost_of_the_old_ontology():
    """This map does not import the theory-operational vocabulary on purpose:
    it was designed for a question that has been retired."""
    import inspect

    from terrario.lab.hypergraph import primitive_composition

    fuente = inspect.getsource(primitive_composition)
    for viejo in ("theory_operational", "TheoryOperationalHyperedge",
                  "HyperedgeCandidateRecord", "EpistemicStatus"):
        assert f"import {viejo}" not in fuente and f"{viejo}(" not in fuente
