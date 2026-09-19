"""Contratos de linaje y de superficie del Nivel 1.3.

El Nivel 1.3 desciende de `1.0 → 1.1`. El Nivel 1.2 no participa, y en este árbol
ni siquiera existe: comprobarlo aquí convierte «no depende de 1.2» en propiedad
verificada y no en aserción del informe.
"""

from __future__ import annotations

import ast
import inspect
import subprocess
import textwrap
from pathlib import Path

import pytest

from terrario.level11.cue import ALL_CUES, CueSemantics, CueToken
from terrario.level11.orientation import DirectionalAssociation
from terrario.level11.world import Direction
from terrario.level13.agent import Level13Agent, PresentCueAgent
from terrario.level13.inherited import (
    BaselineRegression, FrozenDirectional, FrozenLevel11Core, cue_for, reconstruct,
)
from terrario.level13.memory import MemoryPhase, OneStepCueMemory
from terrario.level13.trials import O_PRESENT, O_QUERY, critical_bank

SEMILLA = 90000011
RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def core():
    return reconstruct(SEMILLA)


def test_el_nivel_12_no_existe_en_este_arbol():
    """La base es `ef67ee5`. Si `terrario/level12/` apareciera aquí,
    `LEVEL12_DEPENDENCY_DETECTED`."""
    assert not (RAIZ / "terrario" / "level12").exists()


def test_ningun_modulo_del_13_importa_el_12():
    """Recorre el AST, no el texto.

    La primera versión de este contrato hacía `grep level12` y caía contra su
    propia documentación --el docstring de `inherited.py` dice justamente que el
    Nivel 1.2 no existe en este árbol--. Un import es un nodo; una frase no.
    """
    ficheros = list((RAIZ / "terrario" / "level13").glob("*.py"))
    ficheros.append(RAIZ / "scripts" / "level13_one_step_persistence.py")
    for ruta in ficheros:
        arbol = ast.parse(ruta.read_text(encoding="utf-8"))
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Import):
                for alias in nodo.names:
                    assert "level12" not in alias.name, f"{ruta.name}: {alias.name}"
            elif isinstance(nodo, ast.ImportFrom):
                assert "level12" not in (nodo.module or ""), f"{ruta.name}: {nodo.module}"


def test_los_niveles_previos_estan_intactos():
    salida = subprocess.run(
        ["git", "diff", "--stat", "ef67ee5", "--", "terrario/level1",
         "terrario/level11"],
        cwd=RAIZ, capture_output=True, text=True, check=True)
    assert salida.stdout.strip() == "", f"niveles previos tocados:\n{salida.stdout}"


def test_el_nucleo_heredado_no_expone_observe_ni_act(core):
    """Dos envoltorios, no uno: `Q` también tiene `observe`. Y sin `act`, porque
    romper empates consumiría azar."""
    assert not hasattr(core, "observe")
    assert not hasattr(core, "act")
    assert not hasattr(core, "orientation") and not hasattr(core, "body")
    for nombre, valor in inspect.getmembers(core):
        if nombre.startswith("_"):
            continue
        assert not hasattr(valor, "observe"), f"{nombre} deja `observe` al alcance"


def test_el_envoltorio_direccional_congela_de_verdad():
    q = DirectionalAssociation()
    assert hasattr(q, "observe")
    envuelto = FrozenDirectional(q)
    assert not hasattr(envuelto, "observe")
    antes = envuelto.digest()
    q.observe(cue_for(CueSemantics.identity(), Direction.UP), Direction.UP,
              moved=1, physical=Direction.UP, semantics_direction=Direction.UP)
    assert envuelto.digest() != antes and not envuelto.intact


def test_la_consulta_no_acepta_cue_externo(core):
    """L13-1. Si `query` recibiera un `CueToken`, no habría nada que recordar."""
    agente = Level13Agent(core, OneStepCueMemory())
    assert list(inspect.signature(agente.query).parameters) == ["observation"]


def test_la_presentacion_no_puede_actuar(core):
    """L13-2. Es auditoría de la superficie de API: el banco no instancia mundo,
    así que no hay `Grid` que mutar. Lo que se verifica es que no exista camino."""
    agente = Level13Agent(core, OneStepCueMemory())
    assert agente.present(O_PRESENT, ALL_CUES[0]) is None
    assert not hasattr(agente, "act")
    assert not hasattr(agente, "step")
    # Por AST: buscar `act` en el texto cazaba la palabra «actúa» del docstring.
    arbol = ast.parse(textwrap.dedent(inspect.getsource(Level13Agent.present)))
    llamadas = {n.func.attr for n in ast.walk(arbol)
                if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert llamadas <= {"write"}, f"present llama a {llamadas - {'write'}}"


def test_la_huella_heredada_no_se_mueve_al_recordar(core):
    antes = core.fingerprint()
    agente = Level13Agent(core, OneStepCueMemory())
    for t in critical_bank():
        agente.reset()
        agente.present(t.o_present, t.stored_cue)
        agente.tick()
        agente.query(t.o_query)
        agente.reset()
    assert core.fingerprint() == antes and core.intact


@pytest.mark.parametrize("defecto,esperado", [
    ({"violations": 5}, "contrato físico"),
    ({"holdout_violations": 2}, "fugas del holdout"),
    ({"informative_minimum": 1}, "cobertura informativa"),
])
def test_la_precondicion_del_baseline_puede_fallar(monkeypatch, defecto, esperado):
    from terrario.level13 import inherited
    original = inherited.orientation_babbling

    def degradado(*args, **kwargs):
        stream = original(*args, **kwargs)
        for campo, valor in defecto.items():
            if campo == "informative_minimum":
                stream.experiences = stream.experiences[:8]
            else:
                setattr(stream, campo, valor)
        return stream

    monkeypatch.setattr(inherited, "orientation_babbling", degradado)
    with pytest.raises(BaselineRegression, match=esperado):
        reconstruct(SEMILLA)


def test_sin_degradar_la_precondicion_aprueba(core):
    assert core.intact


def test_las_semillas_del_13_no_pisan_las_anteriores():
    usadas = set(range(20260919, 20260951)) | {31415926} \
        | set(range(31415927, 31415959)) | set(range(70000019, 70000034)) \
        | set(range(80000011, 80000019))
    nuevas = set(range(90000011, 90000019)) | {s + 7 for s in range(90000011, 90000019)}
    assert not (nuevas & usadas)


def test_la_reconstruccion_es_reproducible():
    assert reconstruct(SEMILLA).fingerprint() == reconstruct(SEMILLA).fingerprint()
