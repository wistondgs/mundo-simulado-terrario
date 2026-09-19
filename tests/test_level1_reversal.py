"""Contratos del reversal · los siete que pueden fallar de verdad.

Cada uno trae su caso positivo **y** su fixture negativa. Un gate que sólo sabe
aprobar no es un gate, y el orden --física primero, aprendizaje después, el
contrato analítico al final-- es el del protocolo.

Ninguno usa semillas confirmatorias. El desarrollo corre sobre `99999937`.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from terrario.level1.models import ContingencyTable
from terrario.level1.reversal import (
    ACQUISITION_THRESHOLD, EMATable, FLOOR_TOLERANCE, MAPPING_A, MAPPING_B,
    acquired, brier_under, floor_check, movement_rate_under, outcome_under,
    phased_babbling, random_movement_rate, switch_effectiveness,
)
from terrario.level1.world import ALL_OBSERVATIONS, Direction

DEV_SEED = 99999937
CONFIRMATORY = range(31415927, 31415959)


def test_no_confirmatory_seed_is_used_for_development():
    """Guardián del propio fichero: si una confirmatoria aparece aquí, la corrida
    deja de ser confirmatoria y nadie se entera.

    Se excluye la línea que DEFINE el rango, o el guardián se detecta a sí mismo
    -- que es exactamente lo que hizo la primera vez que corrió.
    """
    lineas = [l for l in Path(__file__).read_text().splitlines()
              if not l.startswith("CONFIRMATORY")]
    cuerpo = "\n".join(lineas)
    culpables = [s for s in CONFIRMATORY if str(s) in cuerpo]
    assert not culpables, f"semillas confirmatorias usadas en desarrollo: {culpables}"


# --- T07 · REV-1 debe poder fallar --------------------------------------------

def test_t07_rev1_fails_when_the_mapping_does_not_change():
    """Sin reversal, `R_switch` debe ser exactamente cero.

    Si el gate aprobara también con `m_B = m_A`, estaría certificando la
    existencia del brazo y no la existencia de la intervención.
    """
    bank = list(ALL_OBSERVATIONS)
    sin_reversal = switch_effectiveness(bank, MAPPING_A, MAPPING_A)
    con_reversal = switch_effectiveness(bank, MAPPING_A, MAPPING_B)

    assert sin_reversal == 0.0                  # fixture negativa: REV-1 cae
    assert con_reversal > 0.0                   # caso positivo: REV-1 pasa
    assert con_reversal == pytest.approx(0.5)   # 8 de 16 por dirección, exacto


# --- T09 · un solo refresh en la frontera -------------------------------------

def test_t09_exactly_one_layout_refresh_at_the_phase_boundary():
    """El riesgo concreto: que la primera transición B regenere la rejilla otra
    vez porque el contador siga valiendo `n_A`."""
    n_a, n_b = 256, 256
    stream = phased_babbling(DEV_SEED, n_a=n_a, n_b=n_b, steps_per_layout=64)

    en_frontera = [e for e in stream.events
                   if e.name == "layout_refresh" and e.step == n_a]
    assert len(en_frontera) == 1

    switches = [e for e in stream.events if e.name == "switch"]
    assert len(switches) == 1 and switches[0].step == n_a

    orden = [e.name for e in stream.events if e.step == n_a]
    assert orden == ["layout_refresh", "snapshot", "switch"]

    assert stream.world_before == stream.world_after
    assert len(stream.transitions) == n_a + n_b
    assert stream.violations == 0


# --- T24 · el readout usa el mapeo vigente ------------------------------------

def test_t24_readout_applies_the_current_mapping_not_the_old_physics():
    """Situación donde `o[π(o)] = 0` pero `o[m_B(π(o))] = 1`.

    Medir `o[π(o)]` después del reversal daría la competencia de un mundo que ya
    no existe, y el error sería silencioso: el número sale bonito.
    """
    o = (0, 1, 1, 1)                     # arriba libre, el resto bloqueado
    assert o[int(Direction.UP)] == 0                   # bajo la física vieja: pasa
    assert o[int(MAPPING_B[Direction.UP])] == 1        # bajo la nueva: choca

    politica = lambda obs, rng: Direction.UP
    rng = np.random.default_rng(0)

    bajo_vieja = movement_rate_under(politica, [o], rng, MAPPING_A)
    bajo_nueva = movement_rate_under(politica, [o], np.random.default_rng(0), MAPPING_B)

    assert bajo_vieja == 1.0        # lo que mediría una evaluación despistada
    assert bajo_nueva == 0.0        # lo que de verdad le pasa al cuerpo


# --- T25 · la conducta puede quedar POR DEBAJO del azar -----------------------

def test_t25_behaviour_can_fall_below_chance_analytically():
    """Microcaso determinista, sin muestreo.

    Un ser que aprendió `C_A` tiene un argmax único `d*`. Si tras el reversal
    `o[m_B(d*)] = 1`, su política determinista obtiene exactamente cero, mientras
    una uniforme obtiene la fracción de direcciones libres.

    Importa porque yo había predicho «cae a ≈ azar». Si el instrumento no pudiera
    representar un resultado por debajo del azar, esa predicción sería
    irrefutable por construcción, que es justo lo que no queremos.
    """
    o = (0, 1, 1, 1)
    ser = ContingencyTable()
    for _ in range(200):                                  # aprende C_A
        for d in Direction:
            ser.observe(o, d, outcome_under(o, d, MAPPING_A))

    rng = np.random.default_rng(DEV_SEED)
    elegido = ser.act(o, rng)
    assert elegido == Direction.UP                        # argmax único

    r_politica = movement_rate_under(ser.act, [o], np.random.default_rng(DEV_SEED),
                                     MAPPING_B)
    r_azar = random_movement_rate([o], MAPPING_B)

    libres = sum(1 for d in Direction if outcome_under(o, d, MAPPING_B) == 1)
    assert libres == 1                                    # sólo ABAJO→ARRIBA sale
    assert r_azar == pytest.approx(0.25)
    assert r_politica == 0.0
    assert r_politica < r_azar                            # anticorrelación, no azar


# --- T17 · REV-2 debe poder fallar --------------------------------------------

def test_t17_rev2_fails_for_a_learner_that_did_not_acquire():
    """Certificar REV-2 enseñando sólo el caso positivo dejaría pasar semillas
    que nunca llegaron a la línea de salida, y su fracaso posterior se leería
    como falta de plasticidad."""
    bank = list(ALL_OBSERVATIONS)

    ignorante = ContingencyTable()
    assert brier_under(ignorante, bank, MAPPING_A) == pytest.approx(0.25)
    assert not acquired(brier_under(ignorante, bank, MAPPING_A))   # PRECONDITION_FAILED

    apenas = ContingencyTable()
    for _ in range(2):
        for o in bank:
            for d in Direction:
                apenas.observe(o, d, outcome_under(o, d, MAPPING_A))
    assert not acquired(brier_under(apenas, bank, MAPPING_A))      # sigue cayendo

    competente = ContingencyTable()
    for _ in range(200):
        for o in bank:
            for d in Direction:
                competente.observe(o, d, outcome_under(o, d, MAPPING_A))
    assert acquired(brier_under(competente, bank, MAPPING_A))      # caso positivo


# --- T20 · el control positivo debe poder fallar ------------------------------

def test_t20_positive_control_fails_when_its_update_is_blocked():
    """REV-4 tiene que detectar readaptación, no la mera existencia del brazo.

    El mismo EMA, con la escritura bloqueada tras el switch, no puede readaptar.
    Si el gate siguiera aprobando, estaría certificando que el brazo existe.
    """
    bank = list(ALL_OBSERVATIONS)

    def entrenar(modelo, mapping, vueltas):
        for _ in range(vueltas):
            for o in bank:
                for d in Direction:
                    modelo.observe(o, d, outcome_under(o, d, mapping))

    vivo = EMATable()
    entrenar(vivo, MAPPING_A, 40)
    antes = brier_under(vivo, bank, MAPPING_B)
    entrenar(vivo, MAPPING_B, 40)
    despues = brier_under(vivo, bank, MAPPING_B)
    assert despues < antes                      # caso positivo: readapta
    assert despues < ACQUISITION_THRESHOLD

    congelado = EMATable()
    entrenar(congelado, MAPPING_A, 40)
    congelado.frozen = True
    antes_c = brier_under(congelado, bank, MAPPING_B)
    entrenar(congelado, MAPPING_B, 40)
    despues_c = brier_under(congelado, bank, MAPPING_B)
    assert despues_c == antes_c                 # fixture negativa: REV-4 cae
    assert despues_c > ACQUISITION_THRESHOLD


# --- T23 · FLOOR_VIOLATED debe poder dispararse -------------------------------

def test_t23_floor_violated_fires_on_an_artificial_inconsistency():
    """Sin este caso el suelo sería una referencia, no un contrato.

    `FLOOR_VIOLATED` no dice «el organismo superó su teoría»: dice que el
    predictor, la instrumentación y la referencia no concuerdan entre sí.
    """
    assert floor_check(0.0070, 0.0070) == "CONSISTENT"
    assert floor_check(0.0070 + FLOOR_TOLERANCE / 2, 0.0070) == "CONSISTENT"
    assert floor_check(0.0090, 0.0070) == "ABOVE_REFERENCE"
    assert floor_check(0.0050, 0.0070) == "FLOOR_VIOLATED"

    # Un predictor imposible: acierta la verdad exactamente mientras sus propios
    # suficientes estadísticos implican un error mayor.
    bank = list(ALL_OBSERVATIONS)

    class Imposible:
        def predict(self, o, d):
            return float(outcome_under(o, d, MAPPING_B))

    observado = brier_under(Imposible(), bank, MAPPING_B)
    referencia = 0.0070
    assert observado == 0.0
    assert floor_check(observado, referencia) == "FLOOR_VIOLATED"
