"""Los dieciséis falsificadores de 1.8 · escritos ANTES que el learner.

Los gates hablan con protocolos mínimos, así que se ejercitan con dobles. Ésa es
la garantía que 1.7 no tuvo: el instrumento existe antes de que exista un
resultado que queramos proteger.
"""

from __future__ import annotations

import dataclasses

import numpy as np
import pytest

from terrario.level18 import gates
from terrario.level18.gates import GateEntry, GateReport, LedgerIncomplete


def _uno(fn, *args, **kwargs) -> gates.GateResult:
    reporte = GateReport()
    fn(reporte, *args, **kwargs)
    return reporte.results[0]


# ===========================================================================
# L18-6 · el primero, y el que más importa
# ===========================================================================

def _mundos():
    return ("W1", "W2", "W3")


def _aprendiz_que_aprende():
    """Su organización depende de la evidencia: cada mundo le deja otra cosa."""
    coste = {("W1", "W1"): 0.20, ("W1", "W2"): 0.55, ("W1", "W3"): 0.60,
             ("W2", "W1"): 0.58, ("W2", "W2"): 0.22, ("W2", "W3"): 0.57,
             ("W3", "W1"): 0.61, ("W3", "W2"): 0.59, ("W3", "W3"): 0.19}
    return (lambda w: w, lambda modelo, mundo: coste[(modelo, mundo)])


def _aprendiz_con_particion_fija():
    """Su organización NO depende de la evidencia: trasplanta sin coste."""
    return (lambda w: "fija", lambda modelo, mundo: 0.40)


LIMPIO = "def observe(self, previous, command, following):\n    return previous\n"


def test_l18_6_pasa_cuando_la_organizacion_depende_de_la_evidencia():
    ajustar, perdida = _aprendiz_que_aprende()
    r = _uno(gates.gate_no_supplied_partition, ajustar, perdida, _mundos(), LIMPIO)
    assert r.passed, r.evidence


def test_l18_6_falla_con_una_particion_fijada_de_antemano():
    """El falsificador fuerte: si la organización no depende de la evidencia,
    trasplantarla no cuesta nada, y eso es que se la dimos nosotros."""
    ajustar, perdida = _aprendiz_con_particion_fija()
    r = _uno(gates.gate_no_supplied_partition, ajustar, perdida, _mundos(), LIMPIO)
    assert not r.passed
    assert "+0.0000" in r.evidence


def test_l18_6_falla_si_una_sola_pareja_trasplanta_gratis():
    """No basta la media: se exige que TODA transferencia duela."""
    coste = {("W1","W1"):0.20,("W1","W2"):0.55,("W1","W3"):0.60,
             ("W2","W1"):0.19,("W2","W2"):0.22,("W2","W3"):0.57,   # <- mejora ajena
             ("W3","W1"):0.61,("W3","W2"):0.59,("W3","W3"):0.19}
    r = _uno(gates.gate_no_supplied_partition, lambda w: w,
             lambda m, w: coste[(m, w)], _mundos(), LIMPIO)
    assert not r.passed


@pytest.mark.parametrize("constante", sorted(gates.FORBIDDEN_CONSTANTS))
def test_l18_6_falla_ante_cualquier_constante_de_conteo_de_estados(constante):
    ajustar, perdida = _aprendiz_que_aprende()
    fuente = f"{constante} = 24\n" + LIMPIO
    r = _uno(gates.gate_no_supplied_partition, ajustar, perdida, _mundos(), fuente)
    assert not r.passed
    assert constante in r.evidence


# ===========================================================================
# L18-4 · conservación de masa
# ===========================================================================

def _heredado():
    return np.arange(16 * 4 * 16, dtype=float).reshape(16, 4, 16) + 1.0


def test_l18_4_pasa_cuando_el_reparto_conserva_la_masa():
    C = _heredado()
    assert _uno(gates.gate_mass_conservation, C, [C / 3, C / 3, C / 3]).passed


def test_l18_4_falla_si_un_split_FABRICA_evidencia():
    C = _heredado()
    r = _uno(gates.gate_mass_conservation, C, [C / 2, C / 2, C * 1e-3])
    assert not r.passed


def test_l18_4_falla_si_un_merge_DESTRUYE_evidencia():
    C = _heredado()
    assert not _uno(gates.gate_mass_conservation, C, [C / 3, C / 3]).passed


def test_l18_4_acepta_reparto_desigual_que_sume_y_rechaza_el_que_no():
    """El reparto no tiene por qué ser en partes iguales; tiene que SUMAR."""
    C = _heredado()
    assert _uno(gates.gate_mass_conservation, C, [C * 0.7, C * 0.3]).passed
    assert not _uno(gates.gate_mass_conservation, C, [C * 0.7, C * 0.4]).passed


def test_l18_4_distingue_coma_flotante_de_evidencia_fabricada():
    """Un residuo de representación pasa; una fabricación con significado, no."""
    C = _heredado()
    ruido = _uno(gates.gate_mass_conservation, C, [C / 3, C / 3, C / 3])
    assert ruido.passed
    assert float(ruido.evidence.split("absoluto ")[1].split(" ")[0]) < 1e-9

    C2 = C.copy(); C2[0, 0, 0] += 1e-4          # un diezmilésimo de conteo
    assert not _uno(gates.gate_mass_conservation, C, [C2]).passed


# ===========================================================================
# L18-7 · fuga de oráculo
# ===========================================================================

@pytest.mark.parametrize("fuente", [
    "def f(cell):\n    return cell\n",
    "def f(o):\n    return o.position\n",
    "from terrario.level17.shadow import AnalyticActionShadow\n",
    "from terrario.level16.structure import describe_world\n",
    "def f(o):\n    return ground_truth\n",
    "def f(x, y):\n    return x + y\n",
])
def test_l18_7_falla_ante_cada_forma_de_fuga(fuente):
    assert not _uno(gates.gate_no_oracle_leakage, fuente).passed


@pytest.mark.parametrize("fuente", [
    LIMPIO,
    "'''esta docstring nombra cell, position y oracle'''\ndef f(z):\n    return z\n",
    "d = {'a': 1}\nfor k in d.keys():\n    pass\n",
])
def test_l18_7_no_se_dispara_contra_prosa_ni_python_corriente(fuente):
    assert _uno(gates.gate_no_oracle_leakage, fuente).passed


# ===========================================================================
# L18-5 · la lesión exacta a 1.7
# ===========================================================================

def _obs():
    return [(0, 0, 0, 0), (0, 1, 0, 1), (1, 1, 0, 0)]


def test_l18_5_pasa_cuando_C18_cero_reproduce_1_7_bit_a_bit():
    tabla = {o: np.full(16, 1 / 16) for o in _obs()}
    r = _uno(gates.gate_incremental_invariant,
             lambda o, c: tabla[o], lambda o: tabla[o], _obs(), (0, 1, 2, 3))
    assert r.passed
    assert "0.000e+00" in r.evidence


def test_l18_5_falla_ante_un_residuo_minimo():
    """Volver *casi* a 1.7 no es volver a 1.7."""
    tabla = {o: np.full(16, 1 / 16) for o in _obs()}
    r = _uno(gates.gate_incremental_invariant,
             lambda o, c: tabla[o] + (1e-12 if c == 2 else 0.0),
             lambda o: tabla[o], _obs(), (0, 1, 2, 3))
    assert not r.passed


def test_l18_5_falla_si_la_prediccion_depende_del_comando_al_nacer():
    tabla = {o: np.full(16, 1 / 16) for o in _obs()}
    assert not _uno(gates.gate_incremental_invariant,
                    lambda o, c: tabla[o] * (1 + 0.01 * c),
                    lambda o: tabla[o], _obs(), (0, 1, 2, 3)).passed


# ===========================================================================
# L18-13 · el null que vive dentro del mundo
# ===========================================================================

def test_l18_13_pasa_si_no_inventa_donde_no_hay_ambiguedad():
    assert _uno(gates.gate_null_context, [0.0, -1e-12, -0.004]).passed


def test_l18_13_falla_si_mejora_donde_k_o_es_uno():
    r = _uno(gates.gate_null_context, [0.0, 0.031, -0.002])
    assert not r.passed
    assert "+3.100e-02" in r.evidence


# ===========================================================================
# L18-8 · paridad de trayectoria · sobrevive porque S0 no cambia
# ===========================================================================

def test_l18_8_pasa_cuando_los_seis_brazos_comparten_la_vida():
    assert _uno(gates.gate_trajectory_parity, ["abc123"] * 6).passed


def test_l18_8_falla_si_un_solo_brazo_vivio_otra_vida():
    r = _uno(gates.gate_trajectory_parity, ["abc123"] * 5 + ["def456"])
    assert not r.passed
    assert "2 hash distinto" in r.evidence


# ===========================================================================
# el resto de los dieciséis
# ===========================================================================

def test_l18_0_falla_si_aparece_una_capacidad_posterior(monkeypatch, tmp_path):
    (tmp_path / "level19").mkdir(parents=True)
    for c in ("level1", "level16", "level17"):
        (tmp_path / c).mkdir()
    monkeypatch.setattr(gates, "TERRARIO", tmp_path)
    assert not _uno(gates.gate_lineage).passed


def test_l18_0_falla_si_falta_un_predecesor(monkeypatch, tmp_path):
    (tmp_path / "level1").mkdir(parents=True)
    monkeypatch.setattr(gates, "TERRARIO", tmp_path)
    assert not _uno(gates.gate_lineage).passed


def test_l18_1_falla_si_lo_heredado_se_movio():
    assert _uno(gates.gate_inherited_frozen, ("a" * 64, "b" * 64),
                ("a" * 64, "b" * 64)).passed
    assert not _uno(gates.gate_inherited_frozen, ("a" * 64, "b" * 64),
                    ("a" * 64, "c" * 64)).passed


def test_l18_2_falla_si_el_aprendiz_nombra_la_politica():
    assert _uno(gates.gate_action_provenance, 100, 100, LIMPIO).passed
    assert not _uno(gates.gate_action_provenance, 99, 100, LIMPIO).passed
    assert not _uno(gates.gate_action_provenance, 100, 100,
                    "def f(policy):\n    return policy\n").passed


def test_l18_3_falla_si_el_canal_lleva_algo_mas():
    @dataclasses.dataclass(frozen=True)
    class Limpia:
        command: int

    @dataclasses.dataclass(frozen=True)
    class Sucia:
        command: int
        moved: int = 0

    assert _uno(gates.gate_efference_purity, Limpia).passed
    assert not _uno(gates.gate_efference_purity, Sucia).passed


def test_l18_9_no_falla_por_cobertura_baja_pero_si_por_inconsistencia():
    inst = {"visits": [[1, 2], [3, 4]], "coverage": 0.41, "counts_min": 0, "rate": 0.8}
    assert _uno(gates.gate_exposure, inst, [[1, 2], [3, 4]]).passed
    assert not _uno(gates.gate_exposure, inst, [[1, 2], [3, 9]]).passed


def test_l18_10_falla_si_el_intervalo_cruza_el_cero():
    assert _uno(gates.gate_predictive_disambiguation, [0.30] * 8 + [0.28] * 8).passed
    assert not _uno(gates.gate_predictive_disambiguation,
                    [0.4, -0.3, 0.5, -0.4, 0.2, -0.1]).passed
    assert not _uno(gates.gate_predictive_disambiguation, [0.9]).passed


def test_l18_10_la_unidad_es_la_vida_no_la_transicion():
    vidas = [0.05, -0.04, 0.06, -0.05]
    assert not _uno(gates.gate_predictive_disambiguation, vidas).passed
    assert _uno(gates.gate_predictive_disambiguation, vidas * 500).passed
    assert "n = 4 vidas" in _uno(gates.gate_predictive_disambiguation, vidas).evidence


def test_l18_11_y_12_exigen_margen_en_TODAS_las_vidas():
    assert _uno(gates.gate_not_explained_by_depth_one, [0.1, 0.2, 0.15]).passed
    assert not _uno(gates.gate_not_explained_by_depth_one, [0.1, -0.01, 0.15]).passed
    assert _uno(gates.gate_not_explained_by_observations, [0.1, 0.2, 0.15]).passed
    assert not _uno(gates.gate_not_explained_by_observations, [0.1, -0.01, 0.15]).passed


def test_l18_14_falla_si_la_lesion_toca_lo_heredado():
    assert _uno(gates.gate_internal_localization, 0.5, 0.9, 0.5, "h", "h").passed
    r = _uno(gates.gate_internal_localization, 0.5, 0.9, 0.5, "h", "OTRA")
    assert not r.passed
    assert "heredado intacto False" in r.evidence


def test_l18_14_falla_si_restaurar_no_devuelve_el_mismo_valor():
    assert not _uno(gates.gate_internal_localization,
                    0.5, 0.9, 0.5000001, "h", "h").passed


def test_l18_15_falla_si_evaluar_mueve_la_huella_o_el_replay_diverge():
    assert _uno(gates.gate_passivity_replay, "h", "h", ["r"] * 3).passed
    assert not _uno(gates.gate_passivity_replay, "h", "OTRA", ["r"] * 3).passed
    assert not _uno(gates.gate_passivity_replay, "h", "h", ["r", "r", "z"]).passed


# ===========================================================================
# D-4 heredado · el meta-verificador
# ===========================================================================

def _ledger_completo():
    return [GateEntry(n, "campaign", True, "ok") for n in gates.REQUIRED_GATES]


def test_el_ledger_completo_verifica():
    gates.verify_ledger(_ledger_completo())


def test_falta_cualquiera_de_los_dieciseis_y_es_fatal():
    for ausente in gates.REQUIRED_GATES:
        recortado = [e for e in _ledger_completo() if e.name != ausente]
        with pytest.raises(LedgerIncomplete, match=ausente):
            gates.verify_ledger(recortado)


def test_un_gate_no_reconocido_es_fatal():
    con_extra = _ledger_completo() + [GateEntry("L18-99", "campaign", True, "ok")]
    with pytest.raises(LedgerIncomplete, match="no reconocidos"):
        gates.verify_ledger(con_extra)


def test_un_alcance_que_no_cuadra_es_fatal():
    ledger = _ledger_completo()
    with pytest.raises(LedgerIncomplete, match="alcances"):
        gates.verify_ledger(ledger, expected_scopes={"L18-10": {"seed:1", "seed:2"}})
