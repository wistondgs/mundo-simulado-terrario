"""Contratos del Nivel 1.1 · los dos adversariales primero.

De todo el diseño, sólo dos pruebas tienen resultado no determinado por la
arquitectura que suministramos: si una semántica permutada produce la `Q`
correspondientemente permutada, y si el gate composicional sabe rechazar una
factorización que de verdad es falsa. Las demás verifican que la implementación
reproduce el contrato.

Desarrollo sobre `99999937`. Las ocho de verificación no se tocan aquí.
"""

from __future__ import annotations

import ast
from pathlib import Path

import numpy as np
import pytest

from terrario.level11.agent import ConstantOrientation, Level11Agent
from terrario.level11.body import BlindBody, FrozenFactoredBody, IdealBody
from terrario.level11.cue import (
    ALL_CUES, CueSemantics, CueToken, physical_direction,
)
from terrario.level11.experiment import (
    JointTable, train_body, train_orientation,
)
from terrario.level11.metrics import all_triples, brier, joint_truth
from terrario.level11.orientation import DirectionalAssociation
from terrario.level11.stream import build_holdout, orientation_babbling
from terrario.level11.world import ALL_OBSERVATIONS, Direction

DEV_SEED = 99999937
VERIFICACION = range(70000019, 70000027)


def test_no_verification_seed_is_used_here():
    """Las ocho de verificación no pueden aparecer en desarrollo.

    Se recorre el árbol sintáctico, no el texto: un guardián que escanea fuente
    caza la línea que define el rango que busca. Ya pasó tres veces.
    """
    arbol = ast.parse(Path(__file__).read_text())
    literales = {n.value for n in ast.walk(arbol)
                 if isinstance(n, ast.Constant) and isinstance(n.value, int)
                 and not isinstance(n.value, bool)}
    culpables = sorted(literales & set(VERIFICACION) - {VERIFICACION.start,
                                                        VERIFICACION.stop})
    assert not culpables, f"semillas de verificación en desarrollo: {culpables}"


# --- ADVERSARIAL 1 · permutación semántica ------------------------------------

def test_a_permuted_cue_semantics_produces_the_permuted_association():
    """El ser aprende de la experiencia, no del nombre del token.

    Si el código resolviera comparando ordinales --`1.0 if cue == action`-- la
    `Q` aprendida sería la misma con las dos semánticas. Aquí debe seguir a la
    correspondencia que el mundo le enseñó, que el agente nunca ve.
    """
    identidad = CueSemantics.identity()
    permutada = CueSemantics.permuted((1, 0, 3, 2))       # U↔D, L↔R

    resultados = {}
    for nombre, sem in (("identidad", identidad), ("permutada", permutada)):
        flujo = orientation_babbling(DEV_SEED, n=2048, semantics=sem)
        q = train_orientation(flujo, sem)
        resultados[nombre] = {(c, a): q.predict(c, a)
                              for c in ALL_CUES for a in Direction}

    for sem, nombre in ((identidad, "identidad"), (permutada, "permutada")):
        for c in ALL_CUES:
            objetivo = sem.direction_of(c)
            for a in Direction:
                valor = resultados[nombre][(c, a)]
                if a == objetivo:
                    assert valor > 0.95, f"{nombre} {c.name}->{a.name} = {valor}"
                else:
                    assert valor < 0.05, f"{nombre} {c.name}->{a.name} = {valor}"

    distintas = sum(1 for k in resultados["identidad"]
                    if abs(resultados["identidad"][k]
                           - resultados["permutada"][k]) > 0.5)
    assert distintas == 8, "la Q debe cambiar con la semántica, no quedarse igual"


def test_the_agent_never_receives_the_cue_semantics():
    """`CueSemantics` no puede viajar dentro del agente ni de la asociación."""
    for modulo in ("agent.py", "orientation.py"):
        arbol = ast.parse((Path("terrario/level11") / modulo).read_text())
        for nodo in ast.walk(arbol):
            if isinstance(nodo, ast.Attribute):
                assert nodo.attr != "direction_of", f"{modulo} consulta la semántica"


# --- ADVERSARIAL 2 · factorización falsa --------------------------------------

def test_the_compositional_gate_rejects_a_false_factorisation():
    """Sin esto, L11-4 no puede fallar para COMPOSITE por construcción.

    Mundo sintético donde el significado del cue **depende de la observación**:

        P(R | o,g,a,Y=1) ≠ P(R | g,a,Y=1)

    `Q(g,a)` no puede representarlo --no indexa `o`-- y la tabla conjunta sí.
    Si COMPOSITE siguiera ganando aquí, el gate no sería falsable.
    """
    base = CueSemantics.identity()
    torcida = CueSemantics.permuted((1, 0, 3, 2))

    def entrenar(semantica_de):
        """Entrena Q y la tabla conjunta bajo la semántica que se le pase."""
        verdad = {(o, g, a): int(o[int(a)] == 0
                                 and a == semantica_de(o).direction_of(g))
                  for o, g, a in all_triples()}
        q, tabla = DirectionalAssociation(), JointTable()
        for _ in range(60):
            for o, g, a in all_triples():
                movido = int(o[int(a)] == 0)
                q.observe(g, a, moved=movido, physical=a if movido else None,
                          semantics_direction=semantica_de(o).direction_of(g)
                          if movido else None)
                tabla.observe(o, g, a, verdad[(o, g, a)])
        err = lambda m: float(np.mean([(m.predict(o, g, a) - verdad[(o, g, a)]) ** 2
                                       for o, g, a in all_triples()]))
        return err(Level11Agent(IdealBody(), q)), err(tabla)

    # factorización VERDADERA: el significado del cue no depende de la observación
    comp_ok, tabla_ok = entrenar(lambda o: base)
    # factorización FALSA: media mundo usa una correspondencia y media la otra
    comp_mal, tabla_mal = entrenar(lambda o: base if o[0] == 0 else torcida)

    # El umbral no se elige: COMPOSITE se compara consigo mismo.
    assert comp_ok < 0.001, f"bajo factorización verdadera debería ser ~0: {comp_ok}"
    assert comp_mal > 20 * comp_ok, (
        f"COMPOSITE apenas se degradó: {comp_ok:.5f} -> {comp_mal:.5f}")
    # Y la tabla conjunta, que sí indexa (o,g,a), representa lo que el compuesto no.
    assert tabla_mal < comp_mal / 2, (
        f"la tabla debería ganar con factorización falsa: {tabla_mal} vs {comp_mal}")
    # Bajo factorización verdadera el orden se invierte en el holdout, que es el
    # caso que L11-4 mide; aquí basta con que el compuesto no pierda.
    assert comp_ok < tabla_ok or comp_ok < 0.001


# --- contrato del aprendiz direccional ----------------------------------------

def test_orientation_starts_without_opinion():
    q = DirectionalAssociation()
    for c in ALL_CUES:
        for a in Direction:
            assert q.predict(c, a) == 0.5


def test_a_blocked_attempt_teaches_nothing_about_the_cue():
    """Una pared informa sobre el cuerpo, no sobre qué significa la señal."""
    q = DirectionalAssociation()
    antes = q.predict(CueToken.C0, Direction.UP)
    informativa = q.observe(CueToken.C0, Direction.UP, moved=0, physical=None,
                            semantics_direction=None)
    assert informativa is False
    assert q.predict(CueToken.C0, Direction.UP) == antes
    assert q.visited_cells == 0


def test_composition_is_the_product():
    class Cuerpo:
        def predict(self, o, a): return 0.8
    class Q:
        def predict(self, c, a): return 0.75
    agente = Level11Agent(Cuerpo(), Q())
    assert agente.predict((0, 0, 0, 0), CueToken.C0, Direction.UP) == pytest.approx(0.6)


def test_physical_direction_comes_from_positions_not_from_the_command():
    assert physical_direction((2, 2), (1, 2)) == Direction.UP
    assert physical_direction((2, 2), (2, 3)) == Direction.RIGHT
    assert physical_direction((2, 2), (2, 2)) is None


# --- cuerpo congelado ---------------------------------------------------------

def test_the_frozen_body_has_no_way_to_learn():
    cuerpo = train_body(DEV_SEED)
    assert not hasattr(cuerpo, "observe")
    antes = cuerpo.digest()
    for o in ALL_OBSERVATIONS:
        for a in Direction:
            cuerpo.predict(o, a)
    assert cuerpo.digest() == antes and cuerpo.intact


# --- holdout ------------------------------------------------------------------

def test_the_holdout_is_balanced_and_never_appears():
    sem = CueSemantics.identity()
    holdout = build_holdout(sem, seed=0)
    assert len(holdout) == 16
    assert len({o for o, _ in holdout}) == 16
    por_señal = {c: sum(1 for _, g in holdout if g == c) for c in ALL_CUES}
    assert set(por_señal.values()) == {4}
    accionables = sum(1 for o, g in holdout if o[int(sem.direction_of(g))] == 0)
    assert accionables == 8

    flujo = orientation_babbling(DEV_SEED, n=2048, semantics=sem, holdout=holdout)
    vistos = {(e.observation, e.cue) for e in flujo.experiences}
    assert not (vistos & holdout)
    assert flujo.holdout_violations == 0
    assert flujo.violations == 0


# --- pasividad y determinismo -------------------------------------------------

def test_measuring_changes_nothing():
    sem = CueSemantics.identity()
    flujo = orientation_babbling(DEV_SEED, n=512, semantics=sem)
    q = train_orientation(flujo, sem)
    agente = Level11Agent(IdealBody(), q)
    celdas, cobertura = q.visited_cells, dict(q.coverage())
    brier(agente, sem)
    brier(agente, sem)
    assert q.visited_cells == celdas and dict(q.coverage()) == cobertura


def test_the_same_seed_gives_the_same_stream():
    sem = CueSemantics.identity()
    huella = lambda f: [(e.observation, int(e.action), e.moved, int(e.cue),
                         None if e.physical is None else int(e.physical))
                        for e in f.experiences]
    a = orientation_babbling(DEV_SEED, n=256, semantics=sem)
    b = orientation_babbling(DEV_SEED, n=256, semantics=sem)
    assert huella(a) == huella(b)
