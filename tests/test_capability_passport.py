"""El pasaporte es un contrato, y su estado se calcula.

Un `status` escrito a mano es una opinión. Estos tests fijan que se derive de
condiciones comprobables, y que el orden de precedencia sea el de las
precondiciones reales: sin contrato no hay nada que juzgar, sin procedencia se
incumple L-1, con la intervención impura el efecto no es atribuible a nadie.
"""

import pytest

from terrario.lab.agent_composition import CONCEPTS
from terrario.lab.capability_passport import (
    REGISTRY, CapabilityPassport, PassportState, Purity, status_of,
)


def _pasaporte(**cambios):
    base = dict(
        concept_id="C", corpus_provenance=("fuente:1",), operational_definition="d",
        algorithm_id="A", algorithm_version="v1", capability_id="X-A1",
        inputs=("i",), outputs=("o",), internal_state=(), allowed_information=(),
        forbidden_information=(), expected_behavior="e", negative_prediction="n",
        required_world_property="w", primary_endpoint="tasa_oportunidad",
        secondary_endpoints=(), falsification_controls=("c",),
        intervention_purity=Purity.PURE, known_dependencies=(), known_confounders=(),
        composition_flag=None, demanding_world="D0",
    )
    base.update(cambios)
    return CapabilityPassport(**base)


def test_un_contrato_incompleto_no_es_un_contrato():
    assert status_of(_pasaporte(expected_behavior="")) is PassportState.PASSPORT_INCOMPLETE


def test_sin_procedencia_al_corpus_no_se_certifica():
    """L-1: ninguna capacidad entra sin conexión explícita con corpus y concepto."""
    assert status_of(_pasaporte(corpus_provenance=())) is PassportState.NO_CORPUS_PROVENANCE


def test_una_intervencion_impura_bloquea_aunque_todo_lo_demas_pase():
    assert status_of(_pasaporte(intervention_purity=Purity.IMPURE)) is (
        PassportState.INTERVENTION_IMPURE)


def test_sin_mundo_que_lo_exija_no_se_certifica():
    """Una ablación sin efecto en un mundo que no exige la capacidad no dice nada."""
    assert status_of(_pasaporte(demanding_world=None)) is PassportState.NO_WORLD_DEMANDS_IT


def test_sin_endpoint_calibrado_no_se_certifica():
    assert status_of(_pasaporte(primary_endpoint="PENDIENTE-lo-que-sea")) is (
        PassportState.NO_CALIBRATED_ENDPOINT)


def test_con_las_cinco_condiciones_queda_listo():
    """El control positivo: si nada pudiera pasar, el gate no mediría nada."""
    assert status_of(_pasaporte()) is PassportState.READY_FOR_CERTIFICATION


def test_la_bandera_de_un_pasaporte_debe_existir_en_el_catalogo():
    """El pasaporte y el catálogo de composición no pueden derivar en silencio."""
    with pytest.raises(ValueError, match="no está en el catálogo"):
        _pasaporte(composition_flag="use_lo_que_no_existe")


def test_todos_los_pasaportes_registrados_tienen_contrato_completo():
    """Lo que falta hoy es procedencia, mundo e instrumento -- no el contrato."""
    incompletos = {cid: p.missing() for cid, p in REGISTRY.items() if p.missing()}
    assert not incompletos, f"pasaportes sin contrato: {incompletos}"


def test_las_dos_capacidades_bloqueadas_lo_declaran_como_impureza():
    """WorldModel y Planner comparten intervención; medido, no supuesto."""
    assert REGISTRY["WM-A1"].intervention_purity is Purity.IMPURE
    assert REGISTRY["PLAN-A1"].intervention_purity is Purity.IMPURE
    # Sobre la población v1, que es de la que habla. Un pasaporte v2 derivado
    # hereda la pureza de su origen y contarlo aparte volvería a hacer de esto
    # un censo, que es justo lo que no afirma.
    puras = {cid for cid, p in REGISTRY.items()
             if p.intervention_purity is Purity.PURE and not p.is_v2}
    assert len(puras) == 7, f"se esperaban 7 puras, hay {len(puras)}: {sorted(puras)}"


def test_cada_bandera_del_catalogo_relevante_tiene_pasaporte():
    """`use_factored_action` queda fuera: es infraestructura, no una capacidad."""
    con_pasaporte = {p.composition_flag for p in REGISTRY.values() if p.composition_flag}
    del_catalogo = {c.key for c in CONCEPTS} - {"use_factored_action"}
    assert del_catalogo == con_pasaporte, (
        f"sin pasaporte: {sorted(del_catalogo - con_pasaporte)}; "
        f"sin concepto: {sorted(con_pasaporte - del_catalogo)}")
