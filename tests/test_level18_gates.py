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

def _canonica(org):
    """Bloques, no etiquetas: {z0,z1} y {z1,z0} son la MISMA organización."""
    bloques = {}
    for sonda, etiqueta in org.items():
        bloques.setdefault(etiqueta, set()).add(sonda)
    return frozenset(frozenset(b) for b in bloques.values())


#: tres organizaciones: A y B son la misma módulo etiqueta; C es distinta
ORG_A = {"h1": "z0", "h2": "z0", "h3": "z1"}
ORG_B = {"h1": "z9", "h2": "z9", "h3": "z7"}      # permutación de etiquetas de A
ORG_C = {"h1": "z0", "h2": "z1", "h3": "z1"}

LIMPIO = "def observe(self, previous, command, following):\n    return previous\n"


def _puntuar(mapa):
    """`refit_and_score`: reestima el contenido con evidencia del mundo visitado,
    así que la pérdida depende de (forma de la organización, mundo)."""
    return lambda org, mundo: mapa[(_canonica(org), mundo)]


def test_l18_6_pasa_cuando_la_organizacion_no_es_intercambiable():
    orgs = {"W1": ORG_A, "W2": ORG_C}
    mapa = {(_canonica(ORG_A), "W1"): 0.20, (_canonica(ORG_C), "W1"): 0.55,
            (_canonica(ORG_C), "W2"): 0.22, (_canonica(ORG_A), "W2"): 0.58}
    r = _uno(gates.gate_no_supplied_partition, orgs, _canonica, _puntuar(mapa),
             {frozenset(("W1", "W2"))}, LIMPIO)
    assert r.passed, r.evidence


def test_l18_6_falla_con_una_particion_fijada_de_antemano():
    """El falsificador fuerte: el oráculo dice que los mundos exigen
    organizaciones distintas y el aprendiz produce la misma en los dos."""
    orgs = {"W1": ORG_A, "W2": ORG_B}          # misma forma canónica
    mapa = {(_canonica(ORG_A), "W1"): 0.20, (_canonica(ORG_A), "W2"): 0.20}
    r = _uno(gates.gate_no_supplied_partition, orgs, _canonica, _puntuar(mapa),
             {frozenset(("W1", "W2"))}, LIMPIO)
    assert not r.passed
    assert "colapsadas" in r.evidence and "ninguna" not in r.evidence.split("colapsadas")[1][:20]


def test_l18_6_falla_si_el_trasplante_estructural_no_cuesta():
    orgs = {"W1": ORG_A, "W2": ORG_C}
    mapa = {(_canonica(ORG_A), "W1"): 0.20, (_canonica(ORG_C), "W1"): 0.19,
            (_canonica(ORG_C), "W2"): 0.22, (_canonica(ORG_A), "W2"): 0.58}
    assert not _uno(gates.gate_no_supplied_partition, orgs, _canonica,
                    _puntuar(mapa), {frozenset(("W1", "W2"))}, LIMPIO).passed


def test_l18_6_NO_castiga_transferir_entre_mundos_que_comparten_estructura():
    """Dos mundos pueden necesitar legítimamente la misma partición. Un buen
    aprendiz la transfiere gratis y eso NO debe contar en su contra."""
    orgs = {"W1": ORG_A, "W2": ORG_B, "W3": ORG_C}   # W1≡W2 por etiquetas
    mapa = {(_canonica(ORG_A), "W1"): 0.20, (_canonica(ORG_A), "W2"): 0.21,
            (_canonica(ORG_A), "W3"): 0.60,
            (_canonica(ORG_C), "W3"): 0.19, (_canonica(ORG_C), "W1"): 0.55,
            (_canonica(ORG_C), "W2"): 0.56}
    incompatibles = {frozenset(("W1", "W3")), frozenset(("W2", "W3"))}
    r = _uno(gates.gate_no_supplied_partition, orgs, _canonica, _puntuar(mapa),
             incompatibles, LIMPIO)
    assert r.passed, r.evidence
    assert "exentos por estructura compartida 1" in r.evidence


def test_l18_6_la_permutacion_de_etiquetas_no_es_otra_organizacion():
    assert _canonica(ORG_A) == _canonica(ORG_B)
    assert _canonica(ORG_A) != _canonica(ORG_C)


def test_l18_6_falla_si_el_banco_no_discrimina():
    """Sin ni un par verdaderamente incompatible el gate NO ES EVALUABLE."""
    orgs = {"W1": ORG_A, "W2": ORG_C}
    r = _uno(gates.gate_no_supplied_partition, orgs, _canonica,
             _puntuar({}), set(), LIMPIO)
    assert not r.passed
    assert "NO EVALUABLE" in r.evidence


@pytest.mark.parametrize("constante", sorted(gates.FORBIDDEN_CONSTANTS))
def test_l18_6_falla_ante_cualquier_constante_de_conteo_de_estados(constante):
    orgs = {"W1": ORG_A, "W2": ORG_C}
    mapa = {(_canonica(ORG_A), "W1"): 0.20, (_canonica(ORG_C), "W1"): 0.55,
            (_canonica(ORG_C), "W2"): 0.22, (_canonica(ORG_A), "W2"): 0.58}
    r = _uno(gates.gate_no_supplied_partition, orgs, _canonica, _puntuar(mapa),
             {frozenset(("W1", "W2"))}, f"{constante} = 24\n" + LIMPIO)
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


def test_l18_4_la_regla_esta_definida_cuando_la_masa_heredada_es_cero():
    """Una tolerancia puramente relativa no está definida en M = 0."""
    C = np.zeros((2, 2, 2))
    assert _uno(gates.gate_mass_conservation, C, [np.zeros((2, 2, 2))]).passed
    casi = np.zeros((2, 2, 2)); casi[0, 0, 0] = 1e-13
    assert _uno(gates.gate_mass_conservation, C, [casi]).passed      # redondeo
    algo = np.zeros((2, 2, 2)); algo[0, 0, 0] = 1e-6
    assert not _uno(gates.gate_mass_conservation, C, [algo]).passed  # fabricación


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


# ===========================================================================
# L18-16 · el gate que la Enmienda 01 añadió · BASELINE-PARITY
# ===========================================================================

def test_l18_16_pasa_cuando_el_comparador_sigue_aprendiendo():
    assert _uno(gates.gate_baseline_parity, 4096, 4096, "c17", "c17", False).passed


def test_l18_16_falla_si_el_comparador_se_congela():
    """El falsificador de la Enmienda 01. Contra un C_17 congelado el mecanismo
    'ganaba' +0.23 nats habiendo creado CERO estados."""
    r = _uno(gates.gate_baseline_parity, 4096, 4096, "c17", "c17", True)
    assert not r.passed
    assert "congelado True" in r.evidence


def test_l18_16_falla_si_no_reciben_las_mismas_oportunidades():
    assert not _uno(gates.gate_baseline_parity, 1024, 4096, "c17", "c17", False).passed


def test_l18_16_falla_si_no_parten_del_mismo_C17():
    assert not _uno(gates.gate_baseline_parity, 4096, 4096, "c17", "otro", False).passed


# ===========================================================================
# L18-17 · REFINEMENT-REVERSIBILITY · sellado por la Enmienda 02
# ===========================================================================

MASA = np.arange(32, dtype=float).reshape(2, 4, 4) + 1.0


def _episodios(refutados_vivos=0, justificados_deshechos=0):
    eps = [{"refuted": True, "merged": True} for _ in range(2)]
    eps += [{"refuted": False, "merged": False} for _ in range(2)]
    eps += [{"refuted": True, "merged": False} for _ in range(refutados_vivos)]
    eps += [{"refuted": False, "merged": True} for _ in range(justificados_deshechos)]
    return eps


def test_l18_17_pasa_cuando_lo_refutado_se_deshace_y_lo_justificado_sobrevive():
    assert _uno(gates.gate_refinement_reversibility, _episodios(), [],
                MASA, MASA.copy(), LIMPIO).passed


def test_l18_17_F1_un_split_refutado_que_sobrevive_es_irreversibilidad():
    """Exactamente el defecto de `acb6b14`: sabe separar y no sabe deshacer."""
    r = _uno(gates.gate_refinement_reversibility, _episodios(refutados_vivos=1), [],
             MASA, MASA.copy(), LIMPIO)
    assert not r.passed
    assert "refutados que siguen vivos 1" in r.evidence


def test_l18_17_F2_un_split_justificado_que_se_deshace_es_inestabilidad():
    r = _uno(gates.gate_refinement_reversibility,
             _episodios(justificados_deshechos=1), [], MASA, MASA.copy(), LIMPIO)
    assert not r.passed
    assert "justificados deshechos 1" in r.evidence


def test_l18_17_F3_la_fusion_no_puede_perder_ni_fabricar_masa():
    perdida = MASA.copy(); perdida[0, 0, 0] -= 1e-4
    assert not _uno(gates.gate_refinement_reversibility, _episodios(), [],
                    MASA, perdida, LIMPIO).passed
    fabricada = MASA.copy(); fabricada[1, 2, 3] += 1e-4
    assert not _uno(gates.gate_refinement_reversibility, _episodios(), [],
                    MASA, fabricada, LIMPIO).passed
    ruido = MASA.copy(); ruido[0, 0, 0] += 1e-13
    assert _uno(gates.gate_refinement_reversibility, _episodios(), [],
                MASA, ruido, LIMPIO).passed


def test_l18_17_F4_ninguna_ruta_puede_apuntar_a_un_hijo_que_ya_no_existe():
    r = _uno(gates.gate_refinement_reversibility, _episodios(),
             [(3, 1, 7)], MASA, MASA.copy(), LIMPIO)
    assert not r.passed
    assert "rutas colgantes 1" in r.evidence


def test_l18_17_F5_renombrar_los_hijos_no_cambia_la_decision():
    """Los episodios se juzgan por su contenido, no por qué etiqueta llevan."""
    con_nombres = [dict(e, label=f"z{i}") for i, e in enumerate(_episodios())]
    otros = [dict(e, label=f"w{99 - i}") for i, e in enumerate(_episodios())]
    uno = _uno(gates.gate_refinement_reversibility, con_nombres, [], MASA, MASA.copy(), LIMPIO)
    dos = _uno(gates.gate_refinement_reversibility, otros, [], MASA, MASA.copy(), LIMPIO)
    assert uno.passed and dos.passed
    assert uno.evidence == dos.evidence


@pytest.mark.parametrize("constante", sorted(gates.FORBIDDEN_MERGE_CONSTANTS))
def test_l18_17_falla_ante_cualquier_umbral_humano_de_fusion(constante):
    r = _uno(gates.gate_refinement_reversibility, _episodios(), [], MASA,
             MASA.copy(), f"{constante} = 3\n" + LIMPIO)
    assert not r.passed
    assert constante in r.evidence


# ===========================================================================
# L18-18 · el tiempo causal de Z
# ===========================================================================

def _paso(before=0, after=1, sum_=1.0, scored=0.5, coordinate=0.5, recomputed=None):
    return {"before": before, "after": after, "sum": sum_, "scored": scored,
            "coordinate": coordinate,
            "recomputed": after if recomputed is None else recomputed}


def _pasos_sanos(n=8):
    return [_paso(before=i % 3, after=(i + 1) % 3) for i in range(n)]


def test_l18_18_pasa_sobre_un_recorrido_honesto():
    informe = GateReport()
    gates.gate_causal_time_of_state(informe, _pasos_sanos())
    assert informe.results[-1].passed


def test_l18_18_sin_pasos_no_certifica_nada():
    informe = GateReport()
    gates.gate_causal_time_of_state(informe, [])
    assert not informe.results[-1].passed


def test_l18_18_detecta_la_fuga_del_futuro():
    """Si la distribución no suma 1 antes de revelar O_t+1, algo la condicionó."""
    malos = _pasos_sanos()
    malos[3] = _paso(before=1, after=2, sum_=0.87)
    informe = GateReport()
    gates.gate_causal_time_of_state(informe, malos)
    assert not informe.results[-1].passed


def test_l18_18_detecta_el_estado_desalineado():
    malos = _pasos_sanos()
    malos[2] = _paso(before=0, after=1, recomputed=7)
    informe = GateReport()
    gates.gate_causal_time_of_state(informe, malos)
    assert not informe.results[-1].passed


def test_l18_18_detecta_el_automata_absorbente():
    """El defecto de `acb6b14`: entrar en un estado y no salir jamás."""
    informe = GateReport()
    gates.gate_causal_time_of_state(
        informe, [_paso(before=4, after=4) for _ in range(8)])
    assert not informe.results[-1].passed


# ===========================================================================
# L18-19 · puntuar no aprende
# ===========================================================================

_ANTES = {"updates": 4096, "splits": 16, "merges": 12, "states": (0, 1, 2),
          "routing": 44, "prior": "abc", "evidence": "def"}


def test_l18_19_pasa_cuando_puntuar_no_toca_nada():
    informe = GateReport()
    gates.gate_score_is_not_update(informe, _ANTES, dict(_ANTES), 2048)
    assert informe.results[-1].passed


def test_l18_19_sin_pasos_puntuados_seria_vacio():
    informe = GateReport()
    gates.gate_score_is_not_update(informe, _ANTES, dict(_ANTES), 0)
    assert not informe.results[-1].passed


def test_l18_19_detecta_cualquier_aprendizaje_durante_el_scoring():
    for campo, nuevo in (("updates", 4097), ("splits", 17), ("merges", 13),
                         ("states", (0, 1, 2, 3)), ("routing", 45),
                         ("prior", "otro"), ("evidence", "otro")):
        despues = dict(_ANTES)
        despues[campo] = nuevo
        informe = GateReport()
        gates.gate_score_is_not_update(informe, _ANTES, despues, 2048)
        assert not informe.results[-1].passed, campo


# ===========================================================================
# El ledger · las seis clases que faltaban
# ===========================================================================

RUNNER = "terrario.level18.campaign.run"
VIDAS = (11, 12)


def _contrato(**cambios):
    base = {"runner": RUNNER, "lives": VIDAS, "once": ("L18-0",),
            "per_life": tuple(n for n in gates.REQUIRED_GATES if n != "L18-0"),
            "completed": True}
    base.update(cambios)
    return gates.CampaignContract(**base)


def _ledger_contractual():
    entradas = [GateEntry("L18-0", "campaign", True, "ok", None, RUNNER)]
    for vida in VIDAS:
        for nombre in gates.REQUIRED_GATES:
            if nombre != "L18-0":
                entradas.append(
                    GateEntry(nombre, f"seed:{vida}", True, "ok", vida, RUNNER))
    return entradas


def test_el_ledger_contractual_verifica():
    gates.verify_ledger(_ledger_contractual(), _contrato())


def test_una_vida_que_falta_es_fatal():
    sin_vida = [e for e in _ledger_contractual() if e.life != 12]
    with pytest.raises(LedgerIncomplete, match="falta la vida 12"):
        gates.verify_ledger(sin_vida, _contrato())


def test_una_semilla_inesperada_es_fatal():
    intruso = _ledger_contractual() + [
        GateEntry("L18-1", "seed:99", True, "ok", 99, RUNNER)]
    with pytest.raises(LedgerIncomplete, match="no está en el contrato"):
        gates.verify_ledger(intruso, _contrato())


def test_un_gate_duplicado_en_la_misma_vida_es_fatal():
    doble = _ledger_contractual() + [
        GateEntry("L18-1", "seed:11", True, "ok", 11, RUNNER)]
    with pytest.raises(LedgerIncomplete, match="aparece 2 veces"):
        gates.verify_ledger(doble, _contrato())


def test_un_gate_de_campana_repetido_es_fatal():
    doble = _ledger_contractual() + [
        GateEntry("L18-0", "campaign", True, "ok", None, RUNNER)]
    with pytest.raises(LedgerIncomplete, match="de campaña y aparece 2 veces"):
        gates.verify_ledger(doble, _contrato())


def test_un_resultado_parcial_es_fatal():
    for roto in (GateEntry("L18-1", "seed:11", None, "ok", 11, RUNNER),
                 GateEntry("L18-1", "seed:11", True, "", 11, RUNNER)):
        parcial = [e for e in _ledger_contractual()
                   if not (e.name == "L18-1" and e.life == 11)] + [roto]
        with pytest.raises(LedgerIncomplete, match="resultado parcial"):
            gates.verify_ledger(parcial, _contrato())


def test_una_procedencia_que_no_es_la_ruta_congelada_es_fatal():
    """`D-4` exacto: el número era correcto y el gate corrió fuera de la ruta."""
    ajeno = [e for e in _ledger_contractual()
             if not (e.name == "L18-1" and e.life == 11)]
    ajeno.append(GateEntry("L18-1", "seed:11", True, "ok", 11,
                           "scripts/lo_calculo_despues.py"))
    with pytest.raises(LedgerIncomplete, match="procedencia"):
        gates.verify_ledger(ajeno, _contrato())


def test_una_campana_no_completada_no_emite_veredicto():
    with pytest.raises(LedgerIncomplete, match="sin declararse completa"):
        gates.verify_ledger(_ledger_contractual(), _contrato(completed=False))


def test_un_contrato_que_no_cubre_los_gates_es_fatal():
    incompleto = _contrato(per_life=tuple(
        n for n in gates.REQUIRED_GATES if n not in ("L18-0", "L18-19")))
    with pytest.raises(LedgerIncomplete, match="no cubre"):
        gates.verify_ledger(_ledger_contractual(), incompleto)
