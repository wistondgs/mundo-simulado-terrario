"""Contratos del binding · cada gate con su fixture negativa.

La regla: un contrato que no puede fallar no es un contrato. Y aquí hay dos que
sólo existen porque la auditoría previa los encontró vacíos --el de orden, que
con `frozenset` no podía fallar, y el de identidad de atributo, que estaba
probado sólo en la mitad de los bancos--.
"""

from __future__ import annotations

from fractions import Fraction as F

import pytest

from terrario.level11.cue import ALL_CUES, CueSemantics, CueToken
from terrario.level12.reference import ALL_TOKENS, ProximityToken
from terrario.level14.agent import Level14Agent
from terrario.level14.binding import (
    ConjunctiveBinder, IndexBinder, OracleBinder, UniformBinder, train,
)
from terrario.level14.carriers import ALL_X, ALL_Y, CANONICAL_PSI, all_psi
from terrario.level14.experiment import run_seed
from terrario.level14.inherited import reconstruct
from terrario.level14.metrics import (
    SEALED_BS_FLOOR, SEALED_BS_FULL, SEALED_C_OK, SEALED_P_CORRECT, binding_brier,
    carrier_attribute_information, index_binder_accuracy, probability_correct,
    readout_mse, three_factor_probe,
)
from terrario.level14.scene import (
    BindingObservation, DirectionItem, ProximityItem, acquisition_bank,
    evaluation_bank, ordered_evaluation_bank, shuffled_acquisition_bank,
    single_reference_bank,
)

SEMILLA = 100000011
PSI = CANONICAL_PSI


@pytest.fixture(scope="module")
def core():
    return reconstruct(SEMILLA)


@pytest.fixture(scope="module")
def entrenado():
    b = ConjunctiveBinder()
    train(b, acquisition_bank(PSI))
    return b


# --- los bancos ------------------------------------------------------------------

def test_el_banco_de_adquisicion_tiene_sesenta_y_cuatro_escenas():
    assert len(acquisition_bank(PSI)) == 64


def test_el_banco_de_evaluacion_tiene_mil_setecientas_veintiocho():
    assert len(evaluation_bank(PSI)) == 1728
    assert len(ordered_evaluation_bank(PSI)) == 6912


def test_el_portador_no_carga_semantica_en_NINGUNO_de_los_dos_bancos():
    """La auditoría encontró que esto estaba probado sólo para la adquisición."""
    assert carrier_attribute_information(acquisition_bank(PSI), paired=True) == (0.0, 0.0)
    assert carrier_attribute_information(evaluation_bank(PSI)) == (0.0, 0.0)


def test_un_generador_con_portador_correlacionado_suspende_el_contrato():
    """FIXTURE NEGATIVA de `ATTRIBUTE_IDENTITY_LEAK`: X0 siempre con el mismo cue."""
    fugado = [(DirectionItem(x, ALL_CUES[ALL_X.index(x)]),
               ProximityItem(PSI[x], ALL_TOKENS[0])) for x in ALL_X]
    igx, _ = carrier_attribute_information(fugado, paired=True)
    assert igx == 2.0


# --- los valores sellados -----------------------------------------------------------

def test_la_asociacion_llega_a_diecisiete_veinteavos(entrenado):
    for x in ALL_X:
        assert entrenado.association(x, PSI[x]) == pytest.approx(float(F(17, 20)))
        for y in ALL_Y:
            if y is not PSI[x]:
                assert entrenado.association(x, y) == pytest.approx(float(F(1, 20)))


def test_la_probabilidad_de_binding_es_doscientos_ochenta_y_nueve_doscientos_noventa(entrenado, core):
    agente = Level14Agent(core, entrenado)
    obs, verdad = evaluation_bank(PSI)[0]
    assert probability_correct(agente, obs, verdad) == pytest.approx(SEALED_P_CORRECT)


def test_el_brier_del_brazo_completo_es_uno_ochenta_y_cuatro_mil_cien(entrenado, core):
    agente = Level14Agent(core, entrenado)
    assert binding_brier(agente, evaluation_bank(PSI)) == pytest.approx(
        SEALED_BS_FULL, abs=1e-15)


def test_el_oraculo_alcanza_cero(core):
    agente = Level14Agent(core, OracleBinder(PSI))
    assert binding_brier(agente, evaluation_bank(PSI)) == 0.0


@pytest.mark.parametrize("hacer", [
    lambda: UniformBinder(),
    lambda: ConjunctiveBinder(frozen=True),
])
def test_los_brazos_sin_canal_se_quedan_en_el_suelo(core, hacer):
    agente = Level14Agent(core, hacer())
    assert binding_brier(agente, evaluation_bank(PSI)) == SEALED_BS_FLOOR


def test_el_barajado_construye_independencia_exacta(core):
    """Cada `x` con cada `y` exactamente cuatro veces ⇒ `A_xy = 5` ⇒ `C = 1/4`.
    Varianza cero, a diferencia del barajado muestreado de 1.1 y 1.2."""
    b = ConjunctiveBinder()
    train(b, shuffled_acquisition_bank())
    for x in ALL_X:
        for y in ALL_Y:
            assert b.association(x, y) == 0.25
    assert binding_brier(Level14Agent(core, b), evaluation_bank(PSI)) == SEALED_BS_FLOOR


def test_barajar_registros_ENTEROS_no_destruiria_nada(core):
    """El defecto del Nivel 1.1: mover junto `(x,y)` conserva toda la relación."""
    banco = acquisition_bank(PSI)[::-1]
    b = ConjunctiveBinder()
    train(b, banco)
    assert binding_brier(Level14Agent(core, b), evaluation_bank(PSI)) == pytest.approx(
        SEALED_BS_FULL, abs=1e-15)


# --- C3 · las 24 permutaciones son contrato, no campaña -------------------------------

@pytest.mark.parametrize("psi", all_psi())
def test_ninguna_permutacion_de_psi_cambia_el_resultado(core, psi):
    b = ConjunctiveBinder()
    train(b, acquisition_bank(psi))
    assert binding_brier(Level14Agent(core, b), evaluation_bank(psi)) == pytest.approx(
        SEALED_BS_FULL, abs=1e-15)


# --- C4 · el atajo de índice -----------------------------------------------------------

def test_emparejar_por_indice_acierta_exactamente_la_mitad():
    assert index_binder_accuracy(ordered_evaluation_bank(PSI)) == 0.5


def test_sobre_conjuntos_el_atajo_de_indice_ni_siquiera_es_expresable():
    """Por eso el contrato de orden necesitaba una escena ordenada propia: con
    `frozenset` no puede fallar, y un gate que sólo puede aprobar no es un gate."""
    obs, _ = evaluation_bank(PSI)[0]
    assert not hasattr(obs.directions, "__getitem__")
    escena, _ = ordered_evaluation_bank(PSI)[0]
    assert IndexBinder().bind_ordered(escena) is not None


def test_el_orden_de_construccion_no_cambia_la_escena():
    obs, _ = evaluation_bank(PSI)[0]
    ds, ps = list(obs.directions), list(obs.proximities)
    assert BindingObservation(frozenset(ds[::-1]), frozenset(ps[::-1])) == obs


# --- C5 · cardinalidad -------------------------------------------------------------------

def test_dos_elementos_identicos_colapsan_y_el_contrato_lo_detecta():
    d = DirectionItem(ALL_X[0], ALL_CUES[0])
    p1 = ProximityItem(ALL_Y[0], ALL_TOKENS[0])
    p2 = ProximityItem(ALL_Y[1], ALL_TOKENS[1])
    with pytest.raises(ValueError, match="mismo tamaño"):
        BindingObservation(frozenset((d,)), frozenset((p1, p2)))


# --- falsabilidad del constructo ------------------------------------------------------------

def test_con_una_sola_referencia_no_se_puede_certificar_binding(core):
    """`BINDING_CONSTRUCT_NOT_FALSIFIABLE`: hasta UNBOUND acierta siempre."""
    ciego = Level14Agent(core, UniformBinder())
    assert binding_brier(ciego, single_reference_bank(PSI)) == 0.0


def test_un_readout_sin_asignacion_no_distingue_los_dos_mundos(core, entrenado):
    """`BINDING_NOT_NECESSARY`.

    Se toma una escena y su gemela con el binding intercambiado --mismos
    marginales, distinta relación--. El readout CON asignación las separa; el
    readout que devuelve el CONJUNTO de proximidades, no. Si el gate aprobara con
    el segundo, estaríamos llamando binding a una tarea donde la relación no
    importa.
    """
    obs, _ = evaluation_bank(PSI)[0]
    ps = sorted(obs.proximities, key=lambda p: p.carrier.value)
    intercambiada = BindingObservation(
        obs.directions,
        frozenset((ProximityItem(ps[0].carrier, ps[1].sensor),
                   ProximityItem(ps[1].carrier, ps[0].sensor))))

    completo = Level14Agent(core, entrenado)
    con_asignacion = lambda e: [round(completo.bound_near_profile(e)[d], 9)
                                for d in sorted(e.directions,
                                                key=lambda d: d.carrier.value)]
    sin_asignacion = lambda e: sorted(round(core.predict_near(p.sensor), 9)
                                      for p in e.proximities)

    assert con_asignacion(obs) != con_asignacion(intercambiada)
    assert sin_asignacion(obs) == sin_asignacion(intercambiada)

    ciego = Level14Agent(core, UniformBinder())
    ciego_prof = lambda e: [round(ciego.bound_near_profile(e)[d], 9)
                            for d in sorted(e.directions, key=lambda d: d.carrier.value)]
    assert ciego_prof(obs) == ciego_prof(intercambiada)


# --- las sondas ---------------------------------------------------------------------------------

def test_cada_intervencion_mueve_su_factor_y_solo_el_suyo(core, entrenado):
    p = three_factor_probe(Level14Agent(core, entrenado), evaluation_bank(PSI))
    assert p["g"]["Q"] > 0.5 and p["g"]["H"] == 0.0 and p["g"]["C"] == 0.0
    assert p["s"]["H"] > 0.5 and p["s"]["Q"] == 0.0 and p["s"]["C"] == 0.0
    assert p["binding"]["readout"] > 0.0
    assert p["binding"]["Q"] == 0.0 and p["binding"]["H"] == 0.0
    assert p["binding"]["C"] == 0.0


def test_solo_el_binding_mueve_el_readout_sin_mover_ningun_factor(core, entrenado):
    """Es el discriminador: los atributos presentes son idénticos y sólo cambia
    la relación entre ellos."""
    p = three_factor_probe(Level14Agent(core, entrenado), evaluation_bank(PSI))
    assert p["g"]["readout"] == 0.0
    assert p["binding"]["readout"] > 0.1


# --- pasividad y firma ----------------------------------------------------------------------------

def test_la_firma_del_binder_solo_acepta_portadores():
    import inspect
    params = list(inspect.signature(ConjunctiveBinder.observe_single_reference).parameters)
    assert params == ["self", "x", "y"]
    anot = ConjunctiveBinder.observe_single_reference.__annotations__
    assert "Carrier" in anot["x"] and "Carrier" in anot["y"]


def test_medir_no_deja_huella(core, entrenado):
    antes = entrenado.digest()
    agente = Level14Agent(core, entrenado)
    binding_brier(agente, evaluation_bank(PSI))
    readout_mse(agente, evaluation_bank(PSI))
    assert entrenado.digest() == antes


def test_la_campana_completa_pasa_sus_gates():
    r = run_seed(SEMILLA)
    assert r.passes, r.gates()
