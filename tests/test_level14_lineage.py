"""Contratos de linaje del Nivel 1.4.

El 1.4 desciende de `1.0 → 1.1 → 1.2`. El Nivel 1.3 queda fuera y en este árbol
no existe: comprobarlo lo convierte en propiedad verificada.
"""

from __future__ import annotations

import ast
import inspect
import subprocess
from pathlib import Path

import pytest

from terrario.level11.cue import CueSemantics
from terrario.level12.proximity import QualitativeDistanceModel
from terrario.level12.reference import ALL_TOKENS, DistanceTruth
from terrario.level14.carriers import (
    ALL_X, ALL_Y, CANONICAL_PSI, DirectionCarrier, ProximityCarrier, all_psi, invert,
)
from terrario.level14.inherited import (
    BaselineRegression, FrozenLevel12Core, FrozenProximity, reconstruct,
)

SEMILLA = 100000011
RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def core():
    return reconstruct(SEMILLA)


def test_el_nivel_13_no_existe_en_este_arbol():
    assert not (RAIZ / "terrario" / "level13").exists()


def test_ningun_modulo_del_14_importa_el_13():
    """Por AST. Buscar el texto cazaría la frase que dice que no existe."""
    ficheros = list((RAIZ / "terrario" / "level14").glob("*.py"))
    ficheros.append(RAIZ / "scripts" / "level14_conjunctive_binding.py")
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


def test_ninguna_pieza_heredada_expone_observe(core):
    assert not hasattr(core, "observe")
    for nombre, valor in inspect.getmembers(core):
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


def test_los_portadores_no_son_intenum():
    """`CueToken.C0 == Direction.UP` es cierto porque los dos son IntEnum. Aquí
    no puede pasar: tipos disjuntos y sin ordinal compartido."""
    assert not isinstance(DirectionCarrier.X0, int)
    assert not isinstance(ProximityCarrier.Y0, int)
    assert DirectionCarrier.X0 != ProximityCarrier.Y0
    assert len({*ALL_X} & {*ALL_Y}) == 0


def test_psi_son_veinticuatro_biyecciones():
    todas = all_psi()
    assert len(todas) == 24
    for psi in todas:
        assert len(set(psi.values())) == 4
        assert invert(psi)[psi[ALL_X[0]]] is ALL_X[0]
    assert CANONICAL_PSI in todas


def test_la_precondicion_del_baseline_puede_fallar(monkeypatch):
    from terrario.level14 import inherited
    original = inherited.orientation_babbling

    def degradado(*a, **k):
        s = original(*a, **k)
        s.experiences = s.experiences[:8]
        return s

    monkeypatch.setattr(inherited, "orientation_babbling", degradado)
    with pytest.raises(BaselineRegression, match="cobertura"):
        reconstruct(SEMILLA)


def test_las_semillas_del_14_no_pisan_nada():
    usadas = (set(range(20260919, 20260951)) | {31415926}
              | set(range(31415927, 31415959)) | set(range(70000019, 70000034))
              | set(range(80000011, 80000019)) | set(range(90000011, 90000026)))
    nuevas = set(range(100000011, 100000019)) | {s + 7 for s in range(100000011, 100000019)}
    assert not (nuevas & usadas)
