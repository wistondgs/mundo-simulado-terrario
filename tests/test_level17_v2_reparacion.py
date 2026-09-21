"""Fixtures de la reparación V2 · la defensa estructural contra otro D-4.

En V1 el runner ejecutaba **cero** de los trece gates y el «13/13» se construyó
en un script escrito después de abrir las semillas. Cada fixture de aquí atraviesa
la ruta real del verificador.
"""

from __future__ import annotations

from collections import Counter

import numpy as np
import pytest

from terrario.level17 import shuffled
from terrario.level17.campaign import (
    GateEntry, LedgerIncomplete, REQUIRED_GATES, run_campaign, verify_ledger,
)
from terrario.level17.efference import ALL_COMMANDS, EfferenceCopy

CAL = tuple(range(150000011, 150000030))     # CALIBRACIÓN · 170... sigue virgen


def _ledger_sano(seeds):
    entradas = [GateEntry(n, "campaign", True, "ok") for n in REQUIRED_GATES
                if n != "L17-8"]
    entradas += [GateEntry("L17-8", f"seed:{s}", True, "ok", null_size=32,
                           null_origin=tuple([s] * 32)) for s in seeds]
    return entradas


def test_el_ledger_sano_verifica():
    verify_ledger(_ledger_sano([1, 2, 3]), [1, 2, 3])


# --- 1 · el runner que no llama a L17-8 -------------------------------------

def test_un_runner_sin_L17_8_es_fatal():
    """Exactamente D-4. Ya no puede pasar inadvertido."""
    sin_nula = [e for e in _ledger_sano([1, 2]) if e.name != "L17-8"]
    with pytest.raises(LedgerIncomplete, match="L17-8"):
        verify_ledger(sin_nula, [1, 2])


def test_un_runner_al_que_le_falte_cualquier_gate_es_fatal():
    for ausente in REQUIRED_GATES:
        recortado = [e for e in _ledger_sano([1]) if e.name != ausente]
        with pytest.raises(LedgerIncomplete):
            verify_ledger(recortado, [1])


# --- 2 y 3 · el tamaño de la nula -------------------------------------------

@pytest.mark.parametrize("tamano", [31, 33, 8, 48])
def test_una_nula_que_no_sea_de_32_es_fatal(tamano):
    entradas = [e for e in _ledger_sano([1]) if e.name != "L17-8"]
    entradas.append(GateEntry("L17-8", "seed:1", True, "ok", null_size=tamano,
                              null_origin=tuple([1] * tamano)))
    with pytest.raises(LedgerIncomplete, match="permutaciones"):
        verify_ledger(entradas, [1])


# --- 4 · agrupada entre vidas ------------------------------------------------

def test_una_nula_de_32_pero_mezclada_entre_vidas_es_fatal():
    """32 muestras, número correcto, procedencia incorrecta."""
    entradas = [e for e in _ledger_sano([1, 2]) if e.name != "L17-8"]
    for semilla in (1, 2):
        entradas.append(GateEntry("L17-8", f"seed:{semilla}", True, "ok",
                                  null_size=32,
                                  null_origin=tuple([1] * 16 + [2] * 16)))
    with pytest.raises(LedgerIncomplete, match="mezcla vidas"):
        verify_ledger(entradas, [1, 2])


# --- 5 · sólo algunas vidas con nula -----------------------------------------

def test_si_solo_algunas_vidas_tienen_nula_es_fatal():
    """Fue D-3: seis de dieciséis."""
    entradas = [e for e in _ledger_sano([1, 2, 3]) if e.name != "L17-8"]
    entradas.append(GateEntry("L17-8", "seed:1", True, "ok", null_size=32,
                              null_origin=tuple([1] * 32)))
    with pytest.raises(LedgerIncomplete, match="una vez por vida"):
        verify_ledger(entradas, [1, 2, 3])


# --- 6 · una permutación que no conserva P_L(O,A) ----------------------------

def test_una_permutacion_que_no_conserva_Counter_OA_no_es_estratificada():
    from terrario.level17.life import live_two_phase
    vida = live_two_phase(150000011, 256, 512, post_steps=64)
    previos = [a for a, _, _ in vida.acquisition]
    comandos = [k for _, k, _ in vida.acquisition]

    estratificada = shuffled.stratified_permutation(
        previos, shuffled.stratified_stream(150000011, 1))
    antes = Counter(zip(previos, comandos))
    assert Counter((previos[t], comandos[estratificada[t]])
                   for t in range(len(previos))) == antes

    global_ = list(np.random.default_rng(0).permutation(len(previos)))
    assert Counter((previos[t], comandos[global_[t]])
                   for t in range(len(previos))) != antes


# --- 7 · un B roto lo captura L17-1, NO L17-8 --------------------------------

def test_un_B_estructuralmente_roto_muere_en_L17_1_antes_de_vivir(monkeypatch):
    import terrario.level17.campaign as modulo
    from terrario.level17.campaign import CampaignInvalid
    from terrario.level17.twin import state_kernels
    from terrario.level17.wiring import ActuatorWiring

    monkeypatch.setattr(
        modulo, "state_kernels",
        lambda sd, w, intact=frozenset(): state_kernels(sd, w, frozenset({0})))
    with pytest.raises(CampaignInvalid, match="WORLD_PAIR_CONSTRUCTION_FAIL"):
        run_campaign(CAL, pairs_required=2)


# --- 8 · un B correcto con un aprendiz que filtra lo captura L17-8 -----------

def test_un_aprendiz_que_mira_la_consecuencia_lo_captura_L17_8():
    """B es correcto; el aprendiz fuga en **consulta**, que es donde importa.

    Una fuga que sólo está en entrenamiento no infla nada: las filas quedan
    indexadas por algo que en evaluación no llega, y el modelo sale peor. La que
    el gate tiene que cazar es la que está presente cuando se puntúa. En un B
    correcto ningún modelo condicionado por acción puede ganar, así que cualquier
    ventaja materialmente positiva es una invención, venga de donde venga.
    """
    from terrario.level16.temporal import OBSERVATION_INDEX
    from terrario.level17.campaign import _null_world_entry
    from terrario.level17.contingency import ActionContingencyModel
    from terrario.level17.twin import MarginalisedBody, twin_stream
    import dataclasses
    import terrario.level17.life as vida_modulo

    semilla = 150000011
    real = vida_modulo.build_world
    try:
        vida_modulo.build_world = lambda s: MarginalisedBody(real(s), twin_stream(s))
        vida_b = vida_modulo.live_two_phase(semilla, 512, 1024, post_steps=512)
    finally:
        vida_modulo.build_world = real

    honesta = _null_world_entry(semilla, vida_b, replicas=32)
    assert honesta.passed, honesta.evidence

    class MiraLaConsecuencia(ActionContingencyModel):
        def probability(self, previous, efference, following):
            base = super().probability(previous, efference, following)
            return min(1.0, base * 3.0)          # premia lo que de hecho ocurrió

    fugado = MiraLaConsecuencia(vida_b.inherited)
    for anterior, comando, siguiente in vida_b.acquisition:
        fugado.observe(anterior, EfferenceCopy(comando), siguiente)

    resultado = _null_world_entry(
        semilla, dataclasses.replace(vida_b, acquired=fugado), replicas=32)
    assert not resultado.passed, resultado.evidence
    assert "WORLD_B_OR_MODEL_NULL_FAIL" in resultado.evidence


# --- 9 · la baraja identidad falla por SU causa ------------------------------

def test_la_baraja_identidad_falla_por_SHUFFLE_NOT_DESTRUCTIVE():
    from terrario.level17.contingency import ActionContingencyModel
    from terrario.level17.gates import GateReport, gate_action_necessity
    from terrario.level17.life import live_two_phase

    vida = live_two_phase(150000011, 256, 512, post_steps=64)
    previos = [a for a, _, _ in vida.acquisition]
    comandos = [k for _, k, _ in vida.acquisition]
    siguientes = [c for _, _, c in vida.acquisition]

    identidad = ActionContingencyModel(vida.inherited)
    for anterior, comando, siguiente in vida.acquisition:
        identidad.observe(anterior, EfferenceCopy(comando), siguiente)
    auditoria = shuffled.audit(identidad, vida.inherited, previos, comandos,
                               siguientes, 150000011, replicas=32)
    reporte = GateReport()
    gate_action_necessity(reporte, auditoria, -0.002, 0.001)
    assert not reporte.results[0].passed
    assert "destructiva False" in reporte.results[0].evidence


# --- la ruta real, entera ----------------------------------------------------

def test_el_runner_ejecuta_los_trece_dentro_de_la_ruta():
    resultado = run_campaign(CAL, pairs_required=3)
    assert resultado.gates_executed == set(REQUIRED_GATES)
    nulas = [e for e in resultado.ledger if e.name == "L17-8"]
    assert len(nulas) == 3
    for entrada in nulas:
        propia = int(entrada.scope.split(":")[1])
        assert entrada.null_size == 32
        assert set(entrada.null_origin) == {propia}
