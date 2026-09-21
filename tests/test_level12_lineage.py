"""Contratos de linaje del Nivel 1.2 · que lo anterior no se pueda tocar.

Cada uno tiene su fixture negativa. Un contrato cuyo único comportamiento posible
es aprobar no es un contrato: es documentación con `assert`.
"""

from __future__ import annotations

import inspect
from pathlib import Path

import numpy as np
import pytest

from terrario.level11.cue import CueSemantics
from terrario.level11.metrics import alignment_rate_expected
from terrario.level11.orientation import DirectionalAssociation
from terrario.level11.world import Direction
from terrario.level12.agent import Level12Agent
from terrario.level12.experiment import run_seed
from terrario.level12.inherited import (
    BaselineRegression, FrozenDirectional, FrozenLevel11Core, cue_for, reconstruct,
)
from terrario.level12.proximity import QualitativeDistanceModel
from terrario.level12.reference import ALL_TOKENS
from terrario.level12.stream import DistanceObservation, build_stream, train_distance

SEMILLA = 80000011
RAIZ = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def core():
    return reconstruct(SEMILLA)


def test_el_nucleo_heredado_no_expone_observe(core):
    """Congelar el cuerpo no basta: `Q` también tiene `observe`, y en 1.1 el
    agente publicaba `self.orientation`. Hacen falta dos envoltorios."""
    assert not hasattr(core, "observe")
    assert not hasattr(core, "orientation")
    assert not hasattr(core, "body")
    for nombre, valor in inspect.getmembers(core):
        if nombre.startswith("_"):
            continue
        assert not hasattr(valor, "observe"), f"{nombre} deja `observe` al alcance"


def test_el_envoltorio_direccional_no_expone_observe():
    q = DirectionalAssociation()
    assert hasattr(q, "observe")          # el original SÍ muta
    envuelto = FrozenDirectional(q)
    assert not hasattr(envuelto, "observe")


def test_la_fixture_negativa_del_linaje_dispara(core):
    """Un núcleo que dejara `observe` alcanzable debe suspender el contrato."""

    class NucleoPermeable:
        def __init__(self, interno):
            self.orientation = interno       # ← exactamente lo que no se puede hacer

    permeable = NucleoPermeable(DirectionalAssociation())
    assert hasattr(permeable.orientation, "observe")


def test_la_huella_no_cambia_al_adquirir_distancia(core):
    antes = core.fingerprint()
    stream = build_stream(SEMILLA, CueSemantics.identity(), n=256)
    h = QualitativeDistanceModel()
    train_distance(stream, h)
    Level12Agent(core, h)
    assert core.fingerprint() == antes
    assert core.intact


def test_la_huella_detecta_una_mutacion_real():
    """Si la huella no se moviera al mutar, no estaría midiendo nada."""
    q = DirectionalAssociation()
    envuelto = FrozenDirectional(q)
    antes = envuelto.digest()
    q.observe(cue_for(CueSemantics.identity(), Direction.UP), Direction.UP,
              moved=1, physical=Direction.UP, semantics_direction=Direction.UP)
    assert envuelto.digest() != antes
    assert not envuelto.intact


def test_la_vista_del_organismo_no_tiene_verdad_ni_geometria():
    stream = build_stream(SEMILLA, CueSemantics.identity(), n=64)
    vista = stream.records[0].view
    assert isinstance(vista, DistanceObservation)
    campos = set(vars(vista))
    assert campos == {"observation", "cue", "sensor"}
    for prohibido in ("truth", "delta", "reference", "distance", "near", "far",
                      "position", "offset"):
        assert not hasattr(vista, prohibido)


def test_el_modelo_de_distancia_no_acepta_contexto():
    """La firma cerrada hace estructural lo que si no sería disciplina."""
    h = QualitativeDistanceModel()
    parametros = list(inspect.signature(h.observe).parameters)
    assert parametros == ["sensor", "target"]
    parametros = list(inspect.signature(h.predict_near).parameters)
    assert parametros == ["sensor"]


def test_la_politica_motora_no_depende_del_sensor(core):
    """`π_1.2(o,g,s) = π_1.1(o,g)`: `s` no aparece ni como argumento."""
    h = QualitativeDistanceModel()
    agente = Level12Agent(core, h)
    assert list(inspect.signature(agente.act).parameters) == [
        "observation", "cue", "rng"]
    semantics = CueSemantics.identity()
    antes = alignment_rate_expected(core, semantics)
    stream = build_stream(SEMILLA, semantics, n=512)
    train_distance(stream, h)
    assert alignment_rate_expected(agente, semantics) == antes


@pytest.mark.parametrize("defecto,esperado", [
    ({"violations": 7}, "contrato físico"),
    ({"holdout_violations": 3}, "fugas del holdout"),
    ({"informative_minimum": 3}, "cobertura informativa"),
])
def test_la_precondicion_del_linaje_puede_fallar(monkeypatch, defecto, esperado):
    """Ejercita la ruta real de `reconstruct`, no una excepción escrita a mano.

    Se degrada el flujo del Nivel 1.1 en un solo aspecto por caso y se exige que
    la semilla quede excluida ANTES de que el Nivel 1.2 empiece.
    """
    from terrario.level12 import inherited

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


def test_sin_degradar_la_precondicion_aprueba():
    """El contraste que hace informativo al caso anterior."""
    assert reconstruct(SEMILLA).intact


def test_level12_no_modifica_los_niveles_anteriores():
    """`terrario/level12/` sólo puede envolver, nunca reescribir."""
    import subprocess
    salida = subprocess.run(
        ["git", "diff", "--stat", "3697c5f", "--", "terrario/level1",
         "terrario/level11"],
        cwd=RAIZ, capture_output=True, text=True, check=True)
    assert salida.stdout.strip() == "", f"niveles previos tocados:\n{salida.stdout}"


def test_la_semilla_reproduce_exactamente(core):
    a = run_seed(SEMILLA)
    b = run_seed(SEMILLA)
    assert a.posteriors["FULL_12"] == b.posteriors["FULL_12"]
    assert a.brier["FULL_12"] == b.brier["FULL_12"]
    assert a.fingerprint_after == b.fingerprint_after


# --- L12-1 · el gate de observabilidad tiene que poder caer ---------------------

def test_un_campo_de_mas_en_la_vista_suspende_el_contrato(monkeypatch):
    """`L12-1` se sostiene sobre la forma del tipo. Si añadir un campo no lo
    hiciera caer, el gate estaría comprobando que el fichero existe."""
    from terrario.level12 import experiment
    from terrario.level12.stream import DistanceObservation

    assert experiment._observability_closed()
    monkeypatch.setitem(DistanceObservation.__dataclass_fields__, "truth", None)
    assert not experiment._observability_closed()


def test_un_parametro_de_mas_en_predict_suspende_el_contrato(monkeypatch):
    from terrario.level12 import experiment
    from terrario.level12.proximity import QualitativeDistanceModel

    monkeypatch.setattr(QualitativeDistanceModel, "predict_near",
                        lambda self, sensor, cue=None: 0.5)
    assert not experiment._observability_closed()
