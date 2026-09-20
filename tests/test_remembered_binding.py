"""Contratos de la fusión con memoria y binding · cada gate con su negativo."""

from __future__ import annotations

import ast
import inspect
import subprocess
from pathlib import Path

import pytest

from terrario.level11.cue import ALL_CUES, CueSemantics, CueToken
from terrario.level11.world import Direction
from terrario.level12.reference import ALL_TOKENS
from terrario.level14.binding import ConjunctiveBinder
from terrario.level14.carriers import ALL_X, CANONICAL_PSI
from terrario.remembered.agent import NoMemory, RememberedBindingAgent
from terrario.remembered.core import FrozenBinder, reconstruct
from terrario.remembered.experiment import O_PRESENT, run_seed
from terrario.remembered.memory import (
    MemoryContractError, MemoryPhase, OneStepCueMemory,
)
from terrario.remembered.metrics import (
    ORDEN, SEALED, build_scene, joint_population_brier, scene_bank,
)

SEMILLA = 120000011
SEM = CueSemantics.identity()
RAIZ = Path(__file__).resolve().parent.parent
BLOB_M = "705239c:terrario/level13/memory.py"


@pytest.fixture(scope="module")
def organismo():
    return reconstruct(SEMILLA)


@pytest.fixture(scope="module")
def reporte():
    return run_seed(SEMILLA)


# --- RB-0 · un solo núcleo -------------------------------------------------------

def test_todos_los_caminos_referencian_el_mismo_nucleo(organismo):
    brazos = [RememberedBindingAgent(organismo, OneStepCueMemory()),
              RememberedBindingAgent(organismo, NoMemory(), use_psi=False)]
    assert all(a.organism is organismo for a in brazos)


def test_dos_nucleos_con_la_misma_huella_siguen_siendo_dos(organismo):
    otro = reconstruct(SEMILLA, verify=False)
    assert otro.fingerprints() == organismo.fingerprints()
    assert otro is not organismo


# --- RB-1, RB-4 · congelación ------------------------------------------------------

def test_las_cinco_piezas_estan_y_ninguna_expone_observe(organismo):
    assert set(organismo.fingerprints()) == {"B", "Q", "H", "psi"}
    for nombre, valor in inspect.getmembers(organismo):
        if nombre.startswith("_"):
            continue
        assert not hasattr(valor, "observe")
        assert not hasattr(valor, "observe_single_reference")


def test_el_envoltorio_del_binder_congela_de_verdad():
    b = ConjunctiveBinder()
    assert hasattr(b, "observe_single_reference")
    envuelto = FrozenBinder(b)
    assert not hasattr(envuelto, "observe_single_reference")
    antes = envuelto.digest()
    b.observe_single_reference(ALL_X[0], CANONICAL_PSI[ALL_X[0]])
    assert envuelto.digest() != antes and not envuelto.intact


def test_las_huellas_no_se_mueven_al_consultar(organismo, reporte):
    assert reporte.lineage_intact
    assert organismo.intact


# --- RB-2, RB-3 · M sin deriva ------------------------------------------------------

def test_la_memoria_es_copia_literal_del_blob_congelado():
    congelado = subprocess.run(["git", "show", BLOB_M], cwd=RAIZ,
                               capture_output=True, text=True, check=True).stdout
    assert (RAIZ / "terrario" / "remembered" / "memory.py").read_text("utf-8") == congelado


def test_la_semantica_sellada_de_M_sobrevive():
    m = OneStepCueMemory()
    m.write(CueToken.C1)
    assert m.peek() is None
    m.tick()
    assert m.peek() is CueToken.C1
    h = m.fingerprint(); m.peek()
    assert m.fingerprint() == h
    m.tick()
    assert m.phase is MemoryPhase.EMPTY


@pytest.mark.parametrize("basura", [None, 0, "C0", Direction.UP])
def test_la_memoria_sigue_rechazando_lo_que_no_es_cuetoken(basura):
    with pytest.raises(MemoryContractError):
        OneStepCueMemory().write(basura)


# --- RB-6, RB-7 · el factorial ------------------------------------------------------

def test_los_cuatro_brazos_siguen_la_tabla_enmendada(reporte):
    for k in ORDEN:
        assert abs(reporte.joint[k] - SEALED[k]) < 1e-3


def test_psi_sin_memoria_no_aporta_absolutamente_nada(reporte):
    """`RB-7`. Es la estructura del resultado: sin saber cuál es la referencia
    diana, saber qué proximidad pertenece a cuál no sirve de nada."""
    assert reporte.psi_alone == 0.0
    assert reporte.joint[("OFF", "ON")] == reporte.joint[("OFF", "OFF")]


def test_la_interaccion_es_enteramente_superaditiva(reporte):
    base = reporte.joint[("OFF", "OFF")]
    sm = base - reporte.joint[("ON", "OFF")]
    am = base - reporte.joint[("ON", "ON")]
    assert am > sm > 0
    assert am - sm > 0.005


# --- RB-8 · el tick sigue haciendo falta ----------------------------------------------

def test_sin_el_tick_el_brazo_completo_cae_al_suelo(reporte):
    assert abs(reporte.skip_tick - reporte.joint[("OFF", "OFF")]) < 1e-12


# --- la operación declarada -------------------------------------------------------------

def test_la_localizacion_por_token_encuentra_la_diana(organismo):
    agente = RememberedBindingAgent(organismo, OneStepCueMemory())
    escena = build_scene(ALL_CUES[0], ALL_CUES[1], ALL_TOKENS[0], ALL_TOKENS[3])
    agente.reset(); agente.present(O_PRESENT, ALL_CUES[0]); agente.tick()
    diana = agente.target_item(escena)
    assert diana is not None and diana.cue is ALL_CUES[0]


def test_sin_memoria_no_hay_diana(organismo):
    agente = RememberedBindingAgent(organismo, NoMemory())
    escena = build_scene(ALL_CUES[0], ALL_CUES[1], ALL_TOKENS[0], ALL_TOKENS[3])
    assert agente.target_item(escena) is None


# --- RB-9 · pasividad e invariancia ---------------------------------------------------------

def test_el_banco_reducido_no_pierde_nada(reporte):
    """Los doce pares de portadores dan el mismo número: reducir el banco no
    eligió el resultado."""
    assert reporte.invariance == 0.0


def test_medir_no_mueve_la_huella_del_binder(reporte):
    assert reporte.binder_passive


# --- linaje -------------------------------------------------------------------------------------

def test_ningun_modulo_importa_el_nivel_13_por_ruta():
    """Por AST. `M` llega por copia literal verificada, no por import."""
    for ruta in (RAIZ / "terrario" / "remembered").glob("*.py"):
        arbol = ast.parse(ruta.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Import):
                for alias in nodo.names:
                    assert "level13" not in alias.name
            elif isinstance(nodo, ast.ImportFrom):
                assert "level13" not in (nodo.module or "")


def test_los_niveles_previos_estan_intactos():
    salida = subprocess.run(
        ["git", "diff", "--stat", "68d852d", "--", "terrario/level1",
         "terrario/level11", "terrario/level12", "terrario/level14"],
        cwd=RAIZ, capture_output=True, text=True, check=True)
    assert salida.stdout.strip() == ""


def test_la_campana_pasa_sus_diez_gates(reporte):
    assert reporte.passes, reporte.gates()
