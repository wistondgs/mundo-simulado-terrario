"""Los trece gates de 1.7 y sus fixtures negativas.

Una fixture que sólo falle por un `AttributeError`, por una aserción tautológica,
o por un mock que rompe también el control, **no cuenta**. Cada una de abajo
falla por la vía real del verificador y por la causa que el gate afirma controlar.
"""

from __future__ import annotations

import dataclasses
import pathlib

import numpy as np
import pytest

from terrario.level17 import gates
from terrario.level17.efference import (
    ALL_COMMANDS, CommandToken, EfferenceCopy,
)
from terrario.level17.gates import GateReport
from terrario.level17.life import live_two_phase
from terrario.level17.twin import state_kernels
from terrario.level17.wiring import ActuatorWiring

SEMILLAS = [150000011, 150000012, 150000013]     # CALIBRACIÓN · 160... sigue ciega


def _uno(funcion, *args, **kwargs) -> gates.GateResult:
    reporte = GateReport()
    funcion(reporte, *args, **kwargs)
    return reporte.results[0]


@pytest.fixture(scope="module")
def vida():
    return live_two_phase(150000011, 512, 512, post_steps=256)


def _kernels(intact=frozenset()):
    return lambda seed: state_kernels(seed, ActuatorWiring.sampled(seed), intact)


def _replay(seed, n):
    from terrario.level16.motor import EndogenousMotor
    from terrario.level16.world import motor_stream
    motor = EndogenousMotor(motor_stream(seed))
    return [ALL_COMMANDS[int(motor.next())] for _ in range(n)]


# ===========================================================================
# G0 · estructura
# ===========================================================================

def test_l17_0_pasa_sobre_el_arbol_real():
    assert _uno(gates.gate_lineage).passed


def test_l17_0_falla_si_aparece_una_capacidad_posterior(monkeypatch, tmp_path):
    (tmp_path / "level18").mkdir(parents=True)
    (tmp_path / "level17").mkdir()
    monkeypatch.setattr(gates, "PACKAGE", tmp_path / "level17")
    assert not _uno(gates.gate_lineage).passed


def test_l17_0_falla_si_el_codigo_heredado_cambio(monkeypatch):
    monkeypatch.setattr(gates, "INHERITED_FINGERPRINT", "0" * 64)
    resultado = _uno(gates.gate_lineage)
    assert not resultado.passed
    assert "CAMBIÓ" in resultado.evidence


def test_l17_1_pasa_sobre_el_par_correcto():
    resultado = _uno(gates.gate_world_pair, SEMILLAS, _kernels())
    assert resultado.passed, resultado.evidence


@pytest.mark.parametrize("intactas", [frozenset({0}), frozenset({0, 2})])
def test_l17_1_detecta_un_B_defectuoso_por_el_kernel_no_por_la_muestra(intactas):
    """Una sola acción causal en B ya levanta WORLD_PAIR_CONSTRUCTION_FAIL."""
    resultado = _uno(gates.gate_world_pair, SEMILLAS, _kernels(intactas))
    assert not resultado.passed
    assert "WORLD_PAIR_CONSTRUCTION_FAIL" in resultado.evidence


def test_l17_1_falla_si_las_dinamicas_marginales_difieren():
    def torcido(seed):
        a, b, sig = state_kernels(seed, ActuatorWiring.sampled(seed))
        b = np.roll(b, 1, axis=2)          # misma forma, otra dinámica
        return a, b, sig
    assert not _uno(gates.gate_world_pair, SEMILLAS, torcido).passed


def test_l17_2_pasa_sobre_una_vida_real(vida):
    assert _uno(gates.gate_action_provenance, vida, _replay).passed


def test_l17_2_detecta_UNA_sola_accion_sustituida_desde_fuera(vida):
    """Una acción cambiada después de emitirse rompe la reconstrucción."""
    adulterados = list(vida.all_commands)
    original = adulterados[391]
    adulterados[391] = next(c for c in ALL_COMMANDS if c is not original)
    falsa = dataclasses.replace(vida, all_commands=tuple(adulterados))
    resultado = _uno(gates.gate_action_provenance, falsa, _replay)
    assert not resultado.passed
    assert "t=391" in resultado.evidence


def test_l17_2_falla_si_el_motor_no_emitio_lo_que_se_vivio(vida):
    falsa = dataclasses.replace(vida, motor_emitted=vida.motor_emitted - 1)
    assert not _uno(gates.gate_action_provenance, falsa, _replay).passed


def test_l17_3_pasa_sobre_el_canal_real():
    assert _uno(gates.gate_efference_purity, EfferenceCopy).passed


@dataclasses.dataclass(frozen=True)
class _ConMovimiento:
    command: CommandToken
    moved: int = 0


@dataclasses.dataclass(frozen=True)
class _ConPosicion:
    command: CommandToken
    position: tuple = (0, 0)


@dataclasses.dataclass(frozen=True)
class _ConDireccionFisica:
    command: CommandToken
    direction: int = 0


@dataclasses.dataclass(frozen=True)
class _ConColision:
    command: CommandToken
    collided: bool = False


@pytest.mark.parametrize("contaminado", [
    _ConMovimiento, _ConPosicion, _ConDireccionFisica, _ConColision,
])
def test_l17_3_rechaza_cualquier_contaminacion_del_canal(contaminado):
    """Debe rechazarse aunque no afecte a ninguna métrica."""
    assert not _uno(gates.gate_efference_purity, contaminado).passed


def test_l17_3_falla_si_el_aprendiz_nombra_la_consecuencia(monkeypatch, tmp_path):
    falso = tmp_path / "level17"
    falso.mkdir()
    (falso / "contingency.py").write_text(
        "def observe(previous, efference, following, moved):\n    return moved\n")
    monkeypatch.setattr(gates, "PACKAGE", falso)
    assert not _uno(gates.gate_efference_purity, EfferenceCopy).passed


# ===========================================================================
# G1 · arquitectura incremental
# ===========================================================================

def _observaciones():
    from terrario.level1.world import ALL_OBSERVATIONS
    return list(ALL_OBSERVATIONS)


def test_l17_4_pasa_con_la_arquitectura_real(vida):
    from terrario.level17.contingency import ActionContingencyModel
    assert _uno(gates.gate_incremental_invariant, vida.inherited,
                ActionContingencyModel, _observaciones(),
                list(ALL_COMMANDS)).passed


def test_l17_4_falla_si_una_sola_celda_de_C17_nace_distinta(vida):
    """Rompe el nacimiento: al nacer ya no predice lo que predecía 1.6."""
    from terrario.level17.contingency import ActionContingencyModel

    def sucio(inherited):
        modelo = ActionContingencyModel(inherited)
        sesgo = modelo.acquired_snapshot()
        sesgo[3, 1, 7] = 1.0
        modelo.load_acquired(sesgo)
        return modelo

    assert not _uno(gates.gate_incremental_invariant, vida.inherited, sucio,
                    _observaciones(), list(ALL_COMMANDS)).passed


def test_l17_4_falla_si_la_lesion_deja_residuo(vida):
    """Rompe la restauración: vuelve *casi* a 1.6, que no es volver a 1.6."""
    from terrario.level17.contingency import ActionContingencyModel

    class ConResiduo(ActionContingencyModel):
        def lesion(self):
            residuo = np.zeros((16, 4, 16))
            residuo[0, 0, 0] = 1e-9
            self.load_acquired(residuo)

    assert not _uno(gates.gate_incremental_invariant, vida.inherited, ConResiduo,
                    _observaciones(), list(ALL_COMMANDS)).passed


def test_l17_5_pasa_sobre_una_vida_real(vida):
    assert _uno(gates.gate_baseline_parity, vida).passed


def test_l17_5_falla_si_NO_ACTION_se_congela_al_final_de_P(vida):
    """La fixture que protege el hallazgo que salvó el diseño.

    Congelar NO-ACTION en `M_0^W` reintroduce el confundido: `D_C` volvería a
    mezclar información de la acción con simplemente más datos.
    """
    from terrario.level16.temporal import TemporalModel
    congelado = TemporalModel()
    congelado.load(vida.inherited.snapshot())
    congelado.freeze()
    falsa = dataclasses.replace(vida, no_action=congelado)
    resultado = _uno(gates.gate_baseline_parity, falsa)
    assert not resultado.passed
    assert "siguió aprendiendo False" in resultado.evidence


def test_l17_5_falla_si_no_action_ve_menos_muestras(vida):
    from terrario.level16.temporal import TemporalModel
    corto = TemporalModel()
    corto.load(vida.inherited.snapshot())
    for anterior, _comando, siguiente in vida.acquisition[:100]:
        corto.observe(anterior, siguiente)
    corto.freeze()
    assert not _uno(gates.gate_baseline_parity,
                    dataclasses.replace(vida, no_action=corto)).passed


# ===========================================================================
# G2 · instrumentos
# ===========================================================================

def _exposicion(vida):
    from terrario.level16.world import build_world
    from terrario.level17 import exposure
    from terrario.level17.shadow import AnalyticActionShadow
    sombra = AnalyticActionShadow(build_world(vida.seed), vida.wiring)
    return (exposure.measure(vida.visits, sombra.divergence_matrix(),
                             sombra.p_reference),
            sombra.divergence_matrix(), sombra.p_reference)


def _recontar(vida):
    from terrario.level16.temporal import OBSERVATION_INDEX
    conteo = np.zeros((16, 4))
    for anterior, comando, _siguiente in vida.acquisition:
        conteo[OBSERVATION_INDEX[anterior], ALL_COMMANDS.index(comando)] += 1
    return conteo


def test_l17_6_pasa_con_los_instrumentos_reales(vida):
    exp, div, ref = _exposicion(vida)
    assert _uno(gates.gate_exposure, vida, exp, div, ref, _recontar).passed


def test_l17_6_detecta_un_contador_que_omite_un_contexto(vida):
    """Omitir un `(o,a)` del contador dejándolo en la vida es inconsistencia."""
    exp, div, ref = _exposicion(vida)
    torcido = vida.visits.copy()
    torcido[int(np.argmax(torcido.max(axis=1))), 0] = 0.0
    falsa = dataclasses.replace(vida, visits=torcido)
    assert not _uno(gates.gate_exposure, falsa, exp, div, ref, _recontar).passed


def test_l17_6_NO_falla_por_cobertura_baja():
    """Una C_OA baja es un resultado experimental, no un defecto de instrumento."""
    corta = live_two_phase(150000011, 512, 48, post_steps=64)
    exp, div, ref = _exposicion(corta)
    resultado = _uno(gates.gate_exposure, corta, exp, div, ref, _recontar)
    assert exp.weighted_coverage < 0.95, exp.weighted_coverage
    assert resultado.passed


# ===========================================================================
# G3 · falsificadores
# ===========================================================================

def _baraja(vida, arm=None):
    from terrario.level17 import shuffled
    previos = [a for a, _, _ in vida.acquisition]
    comandos = [k for _, k, _ in vida.acquisition]
    siguientes = [c for _, _, c in vida.acquisition]
    brazo = arm if arm is not None else shuffled.build(
        vida.inherited, previos, comandos, siguientes, vida.seed, 0)
    return shuffled.audit(brazo, vida.inherited, previos, comandos, siguientes,
                          vida.seed, replicas=8)


def test_l17_9_pasa_con_la_baraja_real(vida):
    assert _uno(gates.gate_action_necessity, _baraja(vida), -0.002, 0.001).passed


def test_l17_9_falla_con_la_baraja_identidad(vida):
    """El brazo que NO baraja conserva la dependencia entera."""
    from terrario.level17.contingency import ActionContingencyModel
    identidad = ActionContingencyModel(vida.inherited)
    for anterior, comando, siguiente in vida.acquisition:
        identidad.observe(anterior, EfferenceCopy(comando), siguiente)
    resultado = _uno(gates.gate_action_necessity, _baraja(vida, identidad),
                     -0.002, 0.001)
    assert not resultado.passed
    assert "destructiva False" in resultado.evidence


def test_l17_9_falla_si_la_baraja_conserva_ventaja(vida):
    assert not _uno(gates.gate_action_necessity, _baraja(vida), 0.4, 0.001).passed


def test_l17_9_falla_si_el_canal_falso_conserva_ventaja(vida):
    assert not _uno(gates.gate_action_necessity, _baraja(vida), -0.002, 0.4).passed


def test_l17_9_el_auditor_consume_el_modelo_que_recibe(vida):
    """Fixture del bug ya encontrado: si reconstruyera el brazo internamente,
    una fixture sólo podría falsificarlo rompiendo también la nula."""
    from terrario.level17 import shuffled
    from terrario.level17.contingency import ActionContingencyModel
    identidad = ActionContingencyModel(vida.inherited)
    for anterior, comando, siguiente in vida.acquisition:
        identidad.observe(anterior, EfferenceCopy(comando), siguiente)
    honesta = _baraja(vida)
    corrupta = _baraja(vida, identidad)
    assert honesta.null_mean == pytest.approx(corrupta.null_mean)
    assert corrupta.observed > honesta.observed
    assert shuffled.row_spread(identidad) == pytest.approx(corrupta.observed)


def test_l17_10_pasa_sobre_el_paquete_real():
    assert _uno(gates.gate_opaque_mapping).passed


def test_l17_10_falla_si_el_aprendiz_cablea_una_direccion(monkeypatch, tmp_path):
    falso = tmp_path / "level17"
    falso.mkdir()
    (falso / "contingency.py").write_text(
        "from terrario.level17.wiring import ActuatorWiring\n"
        "UP = 0\n\ndef predict(o, a):\n    return UP\n")
    (falso / "efference.py").write_text("class CommandToken:\n    pass\n")
    (falso / "wiring.py").write_text("")
    monkeypatch.setattr(gates, "PACKAGE", falso)
    assert not _uno(gates.gate_opaque_mapping).passed


# ===========================================================================
# G4 · localización causal
# ===========================================================================

def _puntuar(vida):
    def score(modelo):
        return -float(np.mean([np.log(modelo.probability(a, EfferenceCopy(k), c))
                               for a, k, c in vida.post]))
    return score


def test_l17_11_pasa_sobre_el_modelo_real(vida):
    from terrario.level17.contingency import ActionContingencyModel
    modelo = ActionContingencyModel(vida.inherited)
    for anterior, comando, siguiente in vida.acquisition:
        modelo.observe(anterior, EfferenceCopy(comando), siguiente)
    assert _uno(gates.gate_internal_localization, modelo, vida.inherited,
                _puntuar(vida)).passed


def test_l17_11_falla_si_la_lesion_arrasa_tambien_lo_heredado(vida):
    """Aunque la competencia se desplome: no aisló la capacidad de 1.7."""
    from terrario.level17.contingency import ActionContingencyModel

    class LesionDestructiva(ActionContingencyModel):
        def lesion(self):
            super().lesion()
            self._inherited = np.ones((16, 16))       # arrasa M_0^W

    modelo = LesionDestructiva(vida.inherited)
    for anterior, comando, siguiente in vida.acquisition:
        modelo.observe(anterior, EfferenceCopy(comando), siguiente)
    resultado = _uno(gates.gate_internal_localization, modelo, vida.inherited,
                     _puntuar(vida))
    assert not resultado.passed
    assert "M_0^W intacto False" in resultado.evidence


def test_l17_11_falla_si_restaurar_no_devuelve_el_mismo_valor(vida):
    from terrario.level17.contingency import ActionContingencyModel

    class RestauracionSucia(ActionContingencyModel):
        def load_acquired(self, deviations):
            super().load_acquired(deviations + 1e-6)

    modelo = RestauracionSucia(vida.inherited)
    for anterior, comando, siguiente in vida.acquisition:
        modelo.observe(anterior, EfferenceCopy(comando), siguiente)
    assert not _uno(gates.gate_internal_localization, modelo, vida.inherited,
                    _puntuar(vida)).passed


def test_l17_12_pasa_con_la_vida_real(vida):
    from terrario.level17.contingency import ActionContingencyModel
    modelo = ActionContingencyModel(vida.inherited)
    for anterior, comando, siguiente in vida.acquisition:
        modelo.observe(anterior, EfferenceCopy(comando), siguiente)
    replay = lambda: live_two_phase(150000011, 128, 128,
                                    post_steps=32).trajectory_hash
    assert _uno(gates.gate_passivity_replay, modelo, _puntuar(vida), replay).passed


def test_l17_12_falla_si_evaluar_incrementa_un_contador(vida):
    from terrario.level17.contingency import ActionContingencyModel
    modelo = ActionContingencyModel(vida.inherited)
    base = _puntuar(vida)

    def entrometido(m):
        m._updates += 1
        return base(m)

    replay = lambda: live_two_phase(150000011, 128, 128,
                                    post_steps=32).trajectory_hash
    assert not _uno(gates.gate_passivity_replay, modelo, entrometido, replay).passed


def test_l17_12_falla_si_el_replay_no_es_determinista(vida):
    """Protege contra el falso negativo que apareció probando la serialización:
    si el azar de B queda fuera de la foto, dos vidas «idénticas» divergen."""
    from itertools import count

    from terrario.level17.contingency import ActionContingencyModel
    modelo = ActionContingencyModel(vida.inherited)
    contador = count()
    assert not _uno(gates.gate_passivity_replay, modelo, _puntuar(vida),
                    lambda: f"hash-{next(contador)}").passed


# ===========================================================================
# estadísticos · sólo fixtures sintéticas. NADA de 160...
# ===========================================================================

def test_l17_7_pasa_con_un_conjunto_claramente_positivo():
    resultado = _uno(gates.gate_action_acquisition, [0.55] * 8 + [0.50] * 8)
    assert resultado.passed
    assert "n = 16 pares" in resultado.evidence


def test_l17_7_falla_si_el_intervalo_cruza_el_cero():
    assert not _uno(gates.gate_action_acquisition,
                    [0.5, -0.4, 0.6, -0.5, 0.3, -0.2, 0.4, -0.3]).passed


def test_l17_7_falla_con_un_conjunto_negativo():
    assert not _uno(gates.gate_action_acquisition, [-0.2] * 16).passed


def test_l17_7_la_unidad_es_el_par_no_la_transicion():
    """Los mismos valores repetidos como si fueran transiciones independientes
    estrecharían el intervalo hasta hacer pasar lo que no debe pasar."""
    pares = [0.05, -0.04, 0.06, -0.05]
    assert not _uno(gates.gate_action_acquisition, pares).passed
    inflado = pares * 500                      # tratar transiciones como unidades
    assert _uno(gates.gate_action_acquisition, inflado).passed
    assert "n = 4 pares" in _uno(gates.gate_action_acquisition, pares).evidence


def test_l17_7_exige_al_menos_dos_pares():
    assert not _uno(gates.gate_action_acquisition, [0.9]).passed


def test_l17_8_pasa_si_B_cae_dentro_de_su_nula():
    nula = list(np.random.default_rng(0).normal(0.0, 0.01, 32))
    assert _uno(gates.gate_null_world, -0.011, nula).passed


def test_l17_8_falla_si_B_aparece_anormalmente_positivo():
    nula = list(np.random.default_rng(0).normal(0.0, 0.01, 32))
    resultado = _uno(gates.gate_null_world, 0.35, nula)
    assert not resultado.passed
    assert "WORLD_B_OR_MODEL_NULL_FAIL" in resultado.evidence
