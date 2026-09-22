"""El mapa de composición primitiva · lo que se niega a sostener.

Every refusal here exists because the corresponding rule, written as prose,
is the failure mode this project keeps finding in its own history.
"""

from __future__ import annotations

import pytest

from terrario.lab.hypergraph.primitive_composition import (
    EXCLUDED, NONE_OUTPUT, CompositionStatus, Cost, DegreeOfFreedom, Hyperedge,
    BoundaryStatus, DerivationAuthority, DofStatus, MapRefused,
    MinimalityStatus, Primitive, Sourcing, delta_df, edges_v01,
    genuine_interaction, primitives_v01, replicated, unlocking_element,
)

W = "W-test"


def _edge(**cambios):
    base = dict(id="Hx", inputs=frozenset({"P01", "P02"}), world=W, scope="S",
                output="E900", status=CompositionStatus.HYPOTHESIS)
    return Hyperedge(**{**base, **cambios})


def _medida(antes, despues, dofs=frozenset(), **cambios):
    """Una arista cuyo instrumento SÍ corrió."""
    return _edge(dof_status=DofStatus.MEASURED, dof_measurement_ref="I-test/v1",
                 dof_before=antes, dof_after=despues,
                 new_degrees_of_freedom=dofs, **cambios)


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
    hallazgos = unlocking_element(edges_v01())
    assert len(hallazgos) == 1
    assert hallazgos[0]["element"] == "P04"
    assert hallazgos[0]["from_empty"] == "H002"
    assert hallazgos[0]["to_observed"] == "H003"
    assert hallazgos[0]["scope"].startswith("campaign-02d5c43")
    assert "not a universal unlocker" in hallazgos[0]["claim"]


def test_a_pair_that_does_not_share_scope_licenses_no_inference():
    """Different budget, organism or implementation means the two edges differ
    in more than the added element, and the inference would be about all of it
    at once."""
    vacio = _edge(id="V", inputs=frozenset({"P01"}), output=NONE_OUTPUT,
                  status=CompositionStatus.NO_EFFECT, evidence="x",
                  scope="presupuesto-10k")
    lleno = _edge(id="L", inputs=frozenset({"P01", "P02"}), output="E001",
                  status=CompositionStatus.OBSERVED, evidence="x",
                  scope="presupuesto-400k")
    assert unlocking_element([vacio, lleno]) == ()
    mismo = dataclasses_replace_scope(lleno, "presupuesto-10k")
    assert len(unlocking_element([vacio, mismo])) == 1


def dataclasses_replace_scope(edge, scope):
    import dataclasses
    return dataclasses.replace(edge, scope=scope)


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
    a = _medida(0, 1, {DegreeOfFreedom.STATE_DISCRIMINATION}, id="A",
                inputs=frozenset({"P01"}), output="E001",
                status=CompositionStatus.OBSERVED, evidence="x")
    b = _medida(0, 1, {DegreeOfFreedom.ACTION_RANGE}, id="B",
                inputs=frozenset({"P02"}), output="E002",
                status=CompositionStatus.OBSERVED, evidence="x")
    ab = _medida(0, 2, {DegreeOfFreedom.STATE_DISCRIMINATION,
                        DegreeOfFreedom.ACTION_RANGE}, id="AB",
                 inputs=frozenset({"P01", "P02"}), output="E003",
                 status=CompositionStatus.OBSERVED, evidence="x")
    assert genuine_interaction([a, b, ab], ab) == frozenset()


def test_a_degree_of_freedom_no_smaller_combination_showed_is_the_finding():
    a = _medida(0, 1, {DegreeOfFreedom.STATE_DISCRIMINATION}, id="A",
                inputs=frozenset({"P01"}), output="E001",
                status=CompositionStatus.OBSERVED, evidence="x")
    ab = _medida(0, 2, {DegreeOfFreedom.STATE_DISCRIMINATION,
                        DegreeOfFreedom.TEMPORAL_CONDITIONING}, id="AB",
                 inputs=frozenset({"P01", "P02"}), output="E003",
                 status=CompositionStatus.OBSERVED, evidence="x")
    assert genuine_interaction([a, ab], ab) == frozenset(
        {DegreeOfFreedom.TEMPORAL_CONDITIONING})


def test_a_smaller_combination_in_another_world_does_not_discount_the_excess():
    """Two worlds are two conditions here too."""
    a = _medida(0, 1, {DegreeOfFreedom.TEMPORAL_CONDITIONING}, id="A",
                inputs=frozenset({"P01"}), output="E001", world="W-otro",
                status=CompositionStatus.OBSERVED, evidence="x")
    ab = _medida(0, 1, {DegreeOfFreedom.TEMPORAL_CONDITIONING}, id="AB",
                 inputs=frozenset({"P01", "P02"}), output="E003",
                 status=CompositionStatus.OBSERVED, evidence="x")
    assert genuine_interaction([a, ab], ab) == frozenset(
        {DegreeOfFreedom.TEMPORAL_CONDITIONING})


# --- ΔDF, y que cero también es resultado --------------------------------------------------

def test_a_measured_rung_that_adds_nothing_reports_zero_and_says_who_measured():
    """A measured zero is a result: the rung added nothing the instrument can
    see, and that is worth writing down."""
    a = _medida(0, 1, {DegreeOfFreedom.STATE_DISCRIMINATION}, id="A",
                inputs=frozenset({"P01"}), output="E001",
                status=CompositionStatus.OBSERVED, evidence="x")
    escalera = [("N1.0", frozenset({"P01"})),
                ("N1.1", frozenset({"P01", "P02"}))]
    filas = delta_df(escalera, [a], W)
    assert filas[0]["dof_status"] == "MEASURED"
    assert filas[0]["delta_df"] is None, "the first rung has nothing to subtract from"
    assert filas[1]["delta_df"] == 0 and filas[1]["gained"] == []
    assert filas[1]["measurement_refs"] == ["I-test/v1"]


def test_an_unmeasured_rung_is_not_a_zero():
    """THE correction. The first version of this function returned 0 for a
    stage nobody had measured, one paragraph after the map said that writing
    zero there would invent a result."""
    escalera = [("N1.0", frozenset({"P01"}))]
    fila = delta_df(escalera, [_edge(id="A", inputs=frozenset({"P01"}))], W)[0]
    assert fila["dof_status"] == "NOT_MEASURED"
    assert fila["delta_df"] is None
    assert fila["df"] is None and fila["gained"] is None


def test_measured_zero_and_not_measured_are_never_the_same_row():
    """The mutant for the epistemological error itself.

    Two ladders over the same stage: in one the instrument ran and found no
    increase, in the other it never ran. If these ever compare equal, the map
    has lost the distinction it was corrected to hold."""
    escalera = [("S1", frozenset({"P01"})), ("S2", frozenset({"P01", "P02"}))]

    #: El instrumento corrió en los dos peldaños y no encontró aumento.
    medidas = [_medida(1, 1, id="A", inputs=frozenset({"P01"}), output="E001",
                       status=CompositionStatus.OBSERVED, evidence="x"),
               _medida(1, 1, id="AB", inputs=frozenset({"P01", "P02"}),
                       output="E002", status=CompositionStatus.OBSERVED,
                       evidence="x")]
    #: Las mismas dos composiciones, y nadie midió.
    sin_medir = [_edge(id="A", inputs=frozenset({"P01"}), output="E001",
                       status=CompositionStatus.OBSERVED, evidence="x"),
                 _edge(id="AB", inputs=frozenset({"P01", "P02"}), output="E002",
                       status=CompositionStatus.OBSERVED, evidence="x")]

    con = delta_df(escalera, medidas, W)[1]
    sin = delta_df(escalera, sin_medir, W)[1]

    assert con["dof_status"] == "MEASURED" and con["delta_df"] == 0
    assert sin["dof_status"] == "NOT_MEASURED" and sin["delta_df"] is None
    assert con != sin, "the two rows must never be the same row"
    assert medidas[0].delta_dof == 0 and sin_medir[0].delta_dof is None


def test_an_unmeasured_edge_cannot_carry_a_reading():
    for campo, valor in (("dof_measurement_ref", "I/v1"), ("dof_before", 0),
                         ("dof_after", 1)):
        with pytest.raises(MapRefused, match="NOT_MEASURED and carries"):
            _edge(**{campo: valor})


def test_an_unmeasured_edge_cannot_name_a_degree_of_freedom():
    """Naming one IS the measurement."""
    with pytest.raises(MapRefused, match="naming one IS the measurement"):
        _edge(new_degrees_of_freedom={DegreeOfFreedom.ACTION_RANGE})


def test_a_measured_edge_must_say_which_instrument_and_give_both_readings():
    with pytest.raises(MapRefused, match="no instrument reference"):
        _edge(dof_status=DofStatus.MEASURED, dof_before=0, dof_after=0)
    with pytest.raises(MapRefused, match="without both readings"):
        _edge(dof_status=DofStatus.MEASURED, dof_measurement_ref="I/v1",
              dof_before=0)


def test_a_measured_rise_must_name_what_rose():
    with pytest.raises(MapRefused, match="names none of them"):
        _medida(0, 2)


def test_naming_a_new_freedom_while_measuring_no_rise_is_refused():
    with pytest.raises(MapRefused, match="measured delta 0"):
        _medida(1, 1, {DegreeOfFreedom.ACTION_RANGE})


def test_genuine_interaction_is_none_rather_than_empty_when_nobody_looked():
    """Empty would say «the composition is exactly the union of its parts»."""
    sin_medir = _edge(id="AB", inputs=frozenset({"P01", "P02"}), output="E003",
                      status=CompositionStatus.OBSERVED, evidence="x")
    assert genuine_interaction([sin_medir], sin_medir) is None
    medida = _medida(0, 1, {DegreeOfFreedom.ACTION_RANGE}, id="AB",
                     inputs=frozenset({"P01", "P02"}), output="E003",
                     status=CompositionStatus.OBSERVED, evidence="x")
    assert genuine_interaction([medida], medida) == frozenset(
        {DegreeOfFreedom.ACTION_RANGE})


def test_the_historical_import_measured_no_degrees_of_freedom_at_all():
    """Not a ladder of zeros. A ladder of NOT_MEASURED.

    The old programme asked whether a concrete organism acquired a concrete
    capability and never asked which degree of freedom widened, so nothing it
    produced can populate this column at all."""
    assert all(e.dof_status is DofStatus.NOT_MEASURED for e in edges_v01())
    assert all(e.delta_dof is None for e in edges_v01())
    escalera = [("S1", frozenset({"P03"})), ("S2", frozenset({"P03", "P04"}))]
    filas = delta_df(escalera, edges_v01(), "W-level1-grid")
    assert [f["dof_status"] for f in filas] == ["NOT_MEASURED", "NOT_MEASURED"]
    assert [f["delta_df"] for f in filas] == [None, None]
    assert 0 not in [f["delta_df"] for f in filas]


# --- frontera conocida no es minimalidad demostrada -------------------------------------

def test_a_cannot_is_a_boundary_and_not_a_proof_of_minimality():
    """A thing can state exactly what it cannot do and still decompose."""
    with pytest.raises(MapRefused, match="claims minimality with no basis"):
        Primitive(id="P99", name="x", can="a", cannot="b", detection="c",
                  minimality_status=MinimalityStatus.MINIMAL_UNDER_CURRENT_VOCABULARY)


def test_the_strong_claim_is_available_with_a_written_basis():
    prim = Primitive(id="P99", name="x", can="a", cannot="b", detection="c",
                     minimality_status=MinimalityStatus.MINIMAL_UNDER_CURRENT_VOCABULARY,
                     minimality_basis="no finer operational decomposition "
                                      "preserves the phenomenon under W-test")
    assert prim.minimality_status is MinimalityStatus.MINIMAL_UNDER_CURRENT_VOCABULARY


def test_none_of_the_twenty_claims_to_be_minimal():
    """v0.1 of an experimental vocabulary, not a claim about the atoms of
    intelligence. Every one has a boundary; not one has a demonstration that
    nothing finer preserves the phenomenon."""
    for prim in primitives_v01():
        assert prim.boundary_status is BoundaryStatus.BOUNDARY_KNOWN, prim.id
        assert prim.minimality_status is MinimalityStatus.NOT_ESTABLISHED, prim.id


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
        assert prim.sourcing is Sourcing.DERIVED_BY_DECOMPOSITION, prim.id
        assert prim.source_concept.strip(), prim.id
        assert prim.derivation_authority is DerivationAuthority.PROJECT_ANALYSIS
        assert prim.provenance.startswith("DECOMPOSED from"), prim.id


def test_the_seven_seeds_carry_their_frozen_campaign():
    semillas = [p for p in primitives_v01() if int(p.id[1:]) <= 7]
    assert len(semillas) == 7
    for prim in semillas:
        assert prim.sourcing is Sourcing.HISTORICALLY_OPERATIONALIZED, prim.id
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


# --- FASE E · procedencia · lo que el mapa se niega a sostener --------------------------

def test_a_decomposed_primitive_without_its_source_concept_is_refused():
    """Without it the record reads as «the corpus discovered P08», when what
    happened is that a source concept was cut up during analysis."""
    with pytest.raises(MapRefused, match="names no source concept"):
        Primitive(id="P98", name="x", can="a", cannot="b", detection="c",
                  sourcing=Sourcing.DERIVED_BY_DECOMPOSITION,
                  derivation_authority=DerivationAuthority.PROJECT_ANALYSIS)


def test_a_decomposition_that_declares_no_authority_for_the_cut_is_refused():
    """Who cut it is what separates analysis from attestation."""
    with pytest.raises(MapRefused, match="declares no authority for the cut"):
        Primitive(id="P98", name="x", can="a", cannot="b", detection="c",
                  sourcing=Sourcing.DERIVED_BY_DECOMPOSITION,
                  source_concept="use_curiosity / CURIO-A1")


def test_claiming_directly_sourced_with_no_claim_id_is_refused():
    """Direct sourcing means a citable claim exists -- id, locator and hash."""
    with pytest.raises(MapRefused, match="DIRECTLY_SOURCED with no claim id"):
        Primitive(id="P98", name="x", can="a", cannot="b", detection="c",
                  sourcing=Sourcing.DIRECTLY_SOURCED)


def test_a_claim_id_on_something_that_is_not_directly_sourced_is_refused():
    with pytest.raises(MapRefused, match="does not claim to be directly sourced"):
        Primitive(id="P98", name="x", can="a", cannot="b", detection="c",
                  sourcing=Sourcing.HISTORICALLY_OPERATIONALIZED,
                  corpus_claim_id="C-HEA-015-01")


def test_a_source_concept_without_a_decomposition_is_refused():
    with pytest.raises(MapRefused, match="not DERIVED_BY_DECOMPOSITION"):
        Primitive(id="P98", name="x", can="a", cannot="b", detection="c",
                  sourcing=Sourcing.HISTORICALLY_OPERATIONALIZED,
                  source_concept="use_curiosity / CURIO-A1")


def test_an_edge_without_a_scope_is_refused():
    """It was declared mandatory in prose and never checked, which made the
    scope gate VACUOUS: two edges both left at the default compared equal and
    licensed an inference with no conditions at all."""
    with pytest.raises(MapRefused, match="no scope"):
        _edge(scope="")


def test_two_scopeless_edges_can_no_longer_fake_a_matched_pair():
    """The defect the previous test describes, shown as behaviour."""
    with pytest.raises(MapRefused, match="no scope"):
        _edge(id="V", inputs=frozenset({"P01"}), output=NONE_OUTPUT,
              status=CompositionStatus.NO_EFFECT, evidence="x", scope="")


# --- FASE E · la prueba positiva · ida y vuelta sin pérdida -----------------------------

def test_a_decomposed_primitive_serialises_and_reconstructs_without_loss():
    """source concept → decomposition Pxx → boundary known → minimality not
    established, through a record and back."""
    original = Primitive(
        id="P97", name="leer_el_propio_error", can="read its own error",
        cannot="act on it", requires=("P06",), cost=Cost.MEDIUM,
        detection="behaviour varies with the error at fixed observation",
        provenance="DECOMPOSED from B5 metacognición · capa 2",
        sourcing=Sourcing.DERIVED_BY_DECOMPOSITION,
        source_concept="B5 metacognición · HEA-017 · C-HEA-017-01",
        derivation_authority=DerivationAuthority.PROJECT_ANALYSIS,
        boundary_status=BoundaryStatus.BOUNDARY_KNOWN,
        minimality_status=MinimalityStatus.NOT_ESTABLISHED)

    registro = original.as_record()
    assert registro["sourcing"] == "DERIVED_BY_DECOMPOSITION"
    assert registro["source_concept"].startswith("B5 metacognición")
    assert registro["derivation_authority"] == "PROJECT_ANALYSIS"
    assert registro["boundary_status"] == "BOUNDARY_KNOWN"
    assert registro["minimality_status"] == "NOT_ESTABLISHED"
    assert registro["corpus_claim_id"] == ""

    vuelta = Primitive.from_record(registro)
    assert vuelta == original
    assert vuelta.as_record() == registro


def test_every_one_of_the_twenty_survives_the_round_trip():
    for prim in primitives_v01():
        assert Primitive.from_record(prim.as_record()) == prim, prim.id


# --- FASE C · la clasificación real, sin simetría fabricada -----------------------------

def test_not_one_primitive_is_directly_sourced():
    """Audited one by one across the frozen trees: seven sealed campaigns and
    thirteen decompositions, and ZERO citable corpus claims. The concept space
    of P04 is named as a declared corpus hole by the inventory itself."""
    assert not [p for p in primitives_v01() if p.sourcing is Sourcing.DIRECTLY_SOURCED]
    assert not [p for p in primitives_v01() if p.corpus_claim_id]


def test_the_seven_seeds_are_operationalized_and_that_is_a_weaker_claim():
    """Built, run and gated is not the same as attested by a source. Saying
    HISTORICALLY_OPERATIONALIZED says what happened, not what the corpus
    supports."""
    semillas = [p for p in primitives_v01() if int(p.id[1:]) <= 7]
    assert all(p.sourcing is Sourcing.HISTORICALLY_OPERATIONALIZED for p in semillas)
    assert all(not p.corpus_claim_id for p in semillas)


def test_P01_is_the_one_rung_with_no_sealed_oracle_and_says_so():
    """Audited independently and NOT smoothed into the others: 1.0 has seven
    sealed gates and no pre-registered oracle document, unlike 1.1 to 1.7."""
    p01 = next(p for p in primitives_v01() if p.id == "P01")
    assert "NO sealed pre-registered oracle" in p01.provenance
