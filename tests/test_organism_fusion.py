"""Contratos de la fusión · cada gate con su fixture negativa.

La fusión no adquiere nada, así que lo único que puede fallar es la integridad:
que haya dos núcleos donde debe haber uno, que `M` derive, que una métrica
escriba, que el tick deje de hacer falta. Eso es lo que se prueba aquí.
"""

from __future__ import annotations

import ast
import inspect
import subprocess
from pathlib import Path

import pytest

from terrario.level11.cue import ALL_CUES, CueSemantics, CueToken
from terrario.level11.metrics import alignment_rate_expected
from terrario.level11.world import ALL_OBSERVATIONS, Direction
from terrario.level12.proximity import QualitativeDistanceModel
from terrario.level12.reference import ALL_TOKENS, DistanceTruth
from terrario.organism.agent import (
    H_IGNORANTE, Q_IGNORANTE, FusedAgent, NoMemory,
)
from terrario.organism.core import (
    BaselineRegression, FrozenOrganism, FrozenProximity, reconstruct,
)
from terrario.organism.experiment import O_PRESENT, run_seed
from terrario.organism.memory import MemoryContractError, MemoryPhase, OneStepCueMemory
from terrario.organism.metrics import (
    ORDEN, SEALED, SEALED_INTERACTION, interaction, joint_population_brier,
)

SEMILLA = 110000011
SEM = CueSemantics.identity()
RAIZ = Path(__file__).resolve().parent.parent
BLOB_M = "705239c:terrario/level13/memory.py"


@pytest.fixture(scope="module")
def organismo():
    return reconstruct(SEMILLA)


# --- F-2 · M no puede derivar ---------------------------------------------------

def test_la_memoria_es_copia_literal_del_original_congelado():
    """Es el idioma del repositorio: `level11/world.py` también es copia literal
    de `level1/world.py`, con contrato que lo comprueba."""
    congelado = subprocess.run(["git", "show", BLOB_M], cwd=RAIZ,
                               capture_output=True, text=True, check=True).stdout
    aqui = (RAIZ / "terrario" / "organism" / "memory.py").read_text(encoding="utf-8")
    assert aqui == congelado


def test_un_solo_byte_distinto_suspende_el_contrato(tmp_path):
    congelado = subprocess.run(["git", "show", BLOB_M], cwd=RAIZ,
                               capture_output=True, text=True, check=True).stdout
    alterado = congelado.replace("self._age = 1", "self._age = 2", 1)
    assert alterado != congelado


# --- F-0 · un solo núcleo --------------------------------------------------------

def test_todos_los_caminos_referencian_el_mismo_nucleo(organismo):
    """Por IDENTIDAD de objeto. Dos núcleos con la misma huella seguirían siendo
    dos cuerpos."""
    brazos = [FusedAgent(organismo, OneStepCueMemory()),
              FusedAgent(organismo, NoMemory(), use_h=False)]
    assert all(a.organism is organismo for a in brazos)


def test_dos_nucleos_distintos_suspenden_el_contrato(organismo):
    """La fixture negativa: reconstruir dos veces da huellas iguales y objetos
    distintos, que es exactamente el fallo que el gate busca."""
    otro = reconstruct(SEMILLA, verify=False)
    assert otro.fingerprints() == organismo.fingerprints()
    assert otro is not organismo
    assert not all(a.organism is organismo for a in
                   [FusedAgent(organismo, NoMemory()), FusedAgent(otro, NoMemory())])


# --- congelación ------------------------------------------------------------------

def test_ninguna_pieza_expone_observe(organismo):
    assert not hasattr(organismo, "observe")
    for nombre, valor in inspect.getmembers(organismo):
        if nombre.startswith("_"):
            continue
        assert not hasattr(valor, "observe"), f"{nombre} deja `observe` al alcance"


def test_el_envoltorio_de_proximidad_congela_de_verdad():
    """`H` es el modelo que nadie había envuelto: su `observe` sigue existiendo."""
    h = QualitativeDistanceModel()
    assert hasattr(h, "observe")
    envuelto = FrozenProximity(h)
    assert not hasattr(envuelto, "observe")
    antes = envuelto.digest()
    h.observe(ALL_TOKENS[0], DistanceTruth.NEAR)
    assert envuelto.digest() != antes and not envuelto.intact


def test_las_huellas_no_se_mueven_al_consultar(organismo):
    antes = organismo.fingerprints()
    agente = FusedAgent(organismo, OneStepCueMemory())
    joint_population_brier(agente, SEM, O_PRESENT)
    assert organismo.fingerprints() == antes and organismo.intact


# --- F-3 · la semántica sellada de M ------------------------------------------------

def test_leer_antes_del_tick_no_devuelve_nada():
    m = OneStepCueMemory()
    m.write(CueToken.C2)
    assert m.phase is MemoryPhase.HELD_0 and m.peek() is None


def test_un_tick_conserva_y_dos_expiran():
    m = OneStepCueMemory()
    m.write(CueToken.C2)
    m.tick()
    assert m.peek() is CueToken.C2
    m.tick()
    assert m.phase is MemoryPhase.EMPTY and m.peek() is None


def test_leer_no_consume():
    m = OneStepCueMemory()
    m.write(CueToken.C3)
    m.tick()
    huella = m.fingerprint()
    for _ in range(5):
        assert m.peek() is CueToken.C3
    assert m.fingerprint() == huella


@pytest.mark.parametrize("basura", [None, 0, "C0", Direction.UP])
def test_escribir_solo_acepta_cuetoken(basura):
    with pytest.raises(MemoryContractError):
        OneStepCueMemory().write(basura)


# --- F-5 y F-6 · el factorial ---------------------------------------------------------

@pytest.fixture(scope="module")
def reporte():
    return run_seed(SEMILLA)


def test_los_cuatro_brazos_son_distintos_y_estan_ordenados(reporte):
    valores = [reporte.joint[k] for k in ORDEN]
    assert valores == sorted(valores)
    assert len(set(valores)) == 4


def test_la_interaccion_es_superaditiva(reporte):
    assert reporte.measured_interaction > 0
    assert abs(reporte.measured_interaction - SEALED_INTERACTION) < 0.001


def test_los_valores_siguen_a_la_tabla_sellada(reporte):
    for k in ORDEN:
        assert abs(reporte.joint[k] - SEALED[k]) < 0.001


def test_apagar_una_capacidad_deja_su_prior_ignorante(organismo):
    """Ni constante arbitraria ni cue inventado: el prior de cada factor."""
    sin_m = FusedAgent(organismo, NoMemory(), use_m=False)
    sin_h = FusedAgent(organismo, OneStepCueMemory(), use_h=False)
    assert sin_m._q(Direction.UP) == Q_IGNORANTE
    assert sin_h._h(ALL_TOKENS[0]) == H_IGNORANTE


# --- F-9 · el tick sigue haciendo falta --------------------------------------------------

def test_sin_el_tick_el_brazo_completo_cae_al_brazo_sin_memoria(organismo, reporte):
    """La semántica de 1.3 sobrevive a la fusión: omitir el tick deja `peek` en
    nada, el factor direccional vuelve a su prior y las dos cosas coinciden."""
    assert reporte.skip_tick > reporte.joint[("ON", "ON")]
    assert abs(reporte.skip_tick - reporte.joint[("ON", "OFF")]) < 1e-12


# --- F-7 · sin fuga -----------------------------------------------------------------------

def test_la_consulta_no_filtra_el_cue(reporte):
    assert reporte.leakage == 0.0


def test_un_banco_que_codificara_el_cue_si_filtraria():
    """Fixture negativa: si `o_query` dependiera del cue, la información sería 2 bits."""
    from terrario.organism.metrics import cue_observation_information
    import math
    from collections import Counter
    pares = [(g, ALL_OBSERVATIONS[int(g)]) for g in ALL_CUES]
    n = len(pares)
    pg, po, pgo = Counter(g for g, _ in pares), Counter(o for _, o in pares), Counter(pares)
    fuga = sum((c / n) * math.log2((c / n) / ((pg[g] / n) * (po[o] / n)))
               for (g, o), c in pgo.items())
    assert fuga == 2.0
    assert cue_observation_information(SEM) == 0.0


# --- F-8 · la política no cambia -------------------------------------------------------------

def test_la_politica_motora_es_identica(reporte):
    assert reporte.align_before == reporte.align_after


# --- linaje ---------------------------------------------------------------------------------

def test_ningun_modulo_de_la_fusion_importa_el_nivel_13():
    """Por AST, no por texto: un import es un nodo y una frase no. La primera
    versión de esta guarda en 1.3 cazó su propia documentación."""
    ficheros = list((RAIZ / "terrario" / "organism").glob("*.py"))
    ficheros.append(RAIZ / "scripts" / "organism_fusion_hm.py")
    for ruta in ficheros:
        arbol = ast.parse(ruta.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Import):
                for alias in nodo.names:
                    assert "level13" not in alias.name
            elif isinstance(nodo, ast.ImportFrom):
                assert "level13" not in (nodo.module or "")


def test_los_niveles_previos_estan_intactos():
    salida = subprocess.run(
        ["git", "diff", "--stat", "7ac43fb", "--", "terrario/level1",
         "terrario/level11", "terrario/level12"],
        cwd=RAIZ, capture_output=True, text=True, check=True)
    assert salida.stdout.strip() == ""


def test_las_semillas_de_la_fusion_no_pisan_nada():
    usadas = (set(range(20260919, 20260951)) | {31415926}
              | set(range(31415927, 31415959)) | set(range(70000019, 70000034))
              | set(range(80000011, 80000019)) | set(range(90000011, 90000026))
              | set(range(100000011, 100000026)))
    nuevas = set(range(110000011, 110000019)) | {s + 7 for s in range(110000011, 110000019)}
    assert not (nuevas & usadas)


def test_la_precondicion_puede_fallar(monkeypatch):
    from terrario.organism import core
    original = core.orientation_babbling

    def degradado(*a, **k):
        s = original(*a, **k)
        s.experiences = s.experiences[:8]
        return s

    monkeypatch.setattr(core, "orientation_babbling", degradado)
    with pytest.raises(BaselineRegression, match="cobertura de orientación"):
        reconstruct(SEMILLA)
