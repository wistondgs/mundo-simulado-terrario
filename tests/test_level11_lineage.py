"""Contratos del linaje 1.1 · que la copia siga siendo una copia, y esté limpia.

Una copia que se deja derivar en silencio es peor que un import: hereda la
apariencia del original sin heredar su evidencia. Estos contratos lo impiden.
"""

from __future__ import annotations

import ast
import hashlib
from pathlib import Path

import numpy as np
import pytest

from terrario import level11
from terrario.level11.measurement import Experiment, motor_babbling, situation_bank
from terrario.level11.measurement import brier as brier_11
from terrario.level11.models import ContingencyTable as Cases11
from terrario.level11.models import FactoredContingency as Features11
from terrario.level11.models import oracle_policy as oracle_11
from terrario.level11.world import ALL_OBSERVATIONS, Direction

#: Semilla de desarrollo declarada, común a los dos linajes. No pertenece a
#: ningún conjunto confirmatorio, y para eso existe.
DEV_SEED = 99999937

EVAL_OFFSET, SHUFFLE_OFFSET = 20_000_003, 10_000_003
NUCLEO = ("world.py", "models.py", "measurement.py")


def _sin_cabecera(path: Path) -> str:
    """El fichero sin el bloque de procedencia, que sí puede diferir."""
    lineas = path.read_text().splitlines()
    corte = next((i + 1 for i, l in enumerate(lineas)
                  if l.startswith("# ────") and i > 0), 0)
    return "\n".join(lineas[corte:]).strip()


def test_the_copy_is_still_a_copy():
    """Los tres módulos del núcleo deben coincidir con `level1` salvo la ruta.

    Si divergen, 1.1 deja de heredar lo que el Experimento 1 demostró, y lo hace
    sin avisar: los tests de 1.1 seguirían en verde midiendo otro organismo.
    """
    for nombre in NUCLEO:
        copia = _sin_cabecera(Path("terrario/level11") / nombre)
        original = (Path("terrario/level1") / nombre).read_text().replace(
            "terrario.level1.", "terrario.level11.").strip()
        assert copia == original, f"{nombre} se separó del original"


def test_the_seed_space_is_disjoint_from_everything_already_touched():
    """Incluidas las imágenes: dos bases disjuntas pueden colisionar al sumarles
    los desplazamientos de banco y permutación."""
    def universo(base: int, n: int) -> set[int]:
        s = {base + i for i in range(n)}
        return s | {x + EVAL_OFFSET for x in s} | {x + SHUFFLE_OFFSET for x in s}

    tocadas = (universo(20260919, 32) | universo(31415926, 33)
               | universo(99999937, 1) | universo(4242, 1)
               | universo(5000, 64) | universo(7000, 64))
    propio = universo(level11.SEED_SPACE.start,
                      len(level11.SEED_SPACE))
    assert not (propio & tocadas)


def _literales_numericos(path: Path) -> set[int]:
    """Los enteros que el CÓDIGO usa, no los que la prosa menciona.

    Escanear texto hace que un guardián cace su propia documentación: la
    cabecera que explica qué semillas están contaminadas las nombra, y un
    `str(s) in fuente` las encuentra ahí. Ya ocurrió dos veces hoy. El árbol
    sintáctico no tiene ese problema porque los comentarios no son nodos y las
    cadenas de documentación se saltan explícitamente.
    """
    arbol = ast.parse(path.read_text())
    docstrings = {ast.get_docstring(n, clean=False) for n in ast.walk(arbol)
                  if isinstance(n, (ast.Module, ast.ClassDef, ast.FunctionDef))}
    return {n.value for n in ast.walk(arbol)
            if isinstance(n, ast.Constant) and isinstance(n.value, int)
            and not isinstance(n.value, bool) and n.value not in docstrings}


def test_no_contaminated_seed_appears_in_the_package():
    """Ninguna semilla con resultados leídos puede usarse como literal aquí."""
    contaminadas = set(range(20260919, 20260951)) | set(range(31415926, 31415959))
    culpables = sorted(
        s for path in Path("terrario/level11").glob("*.py")
        for s in (_literales_numericos(path) & contaminadas))
    assert not culpables, f"semillas contaminadas en el paquete 1.1: {culpables}"


def test_the_reversal_did_not_travel_with_the_copy():
    """El reversal es un experimento sobre el ser anterior, con su preregistro
    sellado y su semilla quemada. Traerlo importaría la contaminación.

    Se comprueba por imports, no por texto: la cabecera explica precisamente que
    el reversal se queda fuera, así que nombrarlo es correcto y no debe fallar.
    """
    assert not (Path("terrario/level11") / "reversal.py").exists()
    for path in Path("terrario/level11").glob("*.py"):
        for nodo in ast.walk(ast.parse(path.read_text())):
            if isinstance(nodo, ast.ImportFrom) and nodo.module:
                assert "reversal" not in nodo.module, f"{path} importa el reversal"
            if isinstance(nodo, ast.Import):
                for alias in nodo.names:
                    assert "reversal" not in alias.name


def test_both_lineages_produce_the_identical_stream_on_the_dev_seed():
    """Equivalencia conductual, no sólo textual.

    Se usa la semilla de desarrollo declarada: mirarla no contamina ningún
    conjunto confirmatorio, y para eso se reservó.
    """
    from terrario.level1.measurement import motor_babbling as babbling_1

    cfg = Experiment(train_layouts=8, train_steps_per_layout=32)
    from terrario.level1.measurement import Experiment as Exp1
    cfg1 = Exp1(train_layouts=8, train_steps_per_layout=32)

    s11, v11 = motor_babbling(cfg, DEV_SEED)
    s1, v1 = babbling_1(cfg1, DEV_SEED)

    assert v11 == v1 == 0
    assert len(s11) == len(s1)
    huella = lambda s: hashlib.sha256(
        repr([(t.observation, int(t.direction), t.moved) for t in s]).encode()
    ).hexdigest()
    assert huella(s11) == huella(s1)


def test_the_inherited_invariants_hold_in_the_new_lineage():
    """Los invariantes analíticos del Experimento 1, revalidados aquí.

    No son resultados: son contratos. Que se cumplan demuestra que la copia
    heredó el organismo, no sólo sus ficheros.
    """
    cfg = Experiment(train_layouts=8, train_steps_per_layout=32,
                     test_layouts=8, test_positions_per_layout=16)
    banco = situation_bank(cfg, DEV_SEED, require_exit=False)
    con_salida = situation_bank(cfg, DEV_SEED, require_exit=True)

    ignorante = Cases11(frozen=True)
    assert brier_11(ignorante, banco)[0] == pytest.approx(0.25, abs=1e-12)

    rng = np.random.default_rng(DEV_SEED)
    movidos = sum(1 for o in con_salida if o[int(oracle_11(o, rng))] == 0)
    assert movidos == len(con_salida)          # el oráculo alcanza 1.0 exacto

    tabla = Cases11()
    assert tabla.predict((1, 1, 1, 1), Direction.UP) == 0.5   # par no visto

    stream, _ = motor_babbling(cfg, DEV_SEED)
    rasgos = Features11()
    for t in stream:
        rasgos.observe(t.observation, t.direction, t.moved)
    assert rasgos.visited_cells <= 4 + 4 * 4 * 2               # base + rasgos
    assert len(ALL_OBSERVATIONS) == 16
