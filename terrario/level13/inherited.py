"""El Nivel 1.1 completo, congelado y de sólo lectura.

Escrito aquí y no importado de ningún otro decimal: el Nivel 1.3 desciende de
`1.0 → 1.1`, y `terrario/level12/` **no existe en este árbol**. La duplicación
entre linajes es deliberada, igual que `level11/world.py` es copia literal de
`level1/world.py`.

Dos envoltorios, no uno. Congelar el cuerpo no basta: `DirectionalAssociation`
también tiene `observe`, y el agente del 1.1 publicaba `self.orientation`.

**Sin `act`.** El núcleo expone puntuaciones, nunca una acción elegida: romper
empates consumiría azar, y en 1.1 muestrear ese desempate ya produjo `0.5000`
frente a una esperanza de `0.4688`. El Nivel 1.3 no añade RNG y ninguna métrica
consume azar.
"""

from __future__ import annotations

import hashlib

from terrario.level11.agent import Level11Agent
from terrario.level11.body import FrozenFactoredBody
from terrario.level11.cue import CueSemantics, CueToken
from terrario.level11.experiment import N_ORIENTATION, train_body, train_orientation
from terrario.level11.metrics import alignment_rate_expected, brier
from terrario.level11.orientation import DirectionalAssociation
from terrario.level11.stream import build_holdout, orientation_babbling
from terrario.level11.world import Direction, Observation


def cue_for(semantics: CueSemantics, direction: Direction) -> CueToken:
    for cue, d in semantics.mapping.items():
        if d == direction:
            return cue
    raise ValueError(f"ninguna señal significa {direction}")


class FrozenDirectional:
    """Envuelve `Q` ya adquirida y expone `predict` y nada más."""

    def __init__(self, trained: DirectionalAssociation) -> None:
        self._inner = trained
        self._birth_digest = self.digest()

    def predict(self, cue: CueToken, action: Direction) -> float:
        return self._inner.predict(cue, action)

    def digest(self) -> str:
        h = hashlib.sha256()
        store = self._inner._belief
        for key in sorted(store, key=repr):
            h.update(repr(key).encode())
            h.update(repr(store[key]).encode())
        return h.hexdigest()

    @property
    def intact(self) -> bool:
        return self.digest() == self._birth_digest


class FrozenLevel11Core:
    """`B` y `Q` congelados. Sin `observe`, sin `act`, sin modelos publicados."""

    def __init__(self, body: FrozenFactoredBody,
                 orientation: FrozenDirectional) -> None:
        self._body = body
        self._orientation = orientation
        self._birth = self.fingerprint()

    def predict_body(self, observation: Observation, action: Direction) -> float:
        return self._body.predict(observation, action)

    def predict_orientation(self, cue: CueToken, action: Direction) -> float:
        return self._orientation.predict(cue, action)

    def joint_scores(self, observation: Observation,
                     cue: CueToken) -> tuple[float, ...]:
        """`J(o,g,a) = B(o,a)·Q(g,a)` para las cuatro acciones."""
        return tuple(self._body.predict(observation, a)
                     * self._orientation.predict(cue, a) for a in Direction)

    def body_scores(self, observation: Observation) -> tuple[float, ...]:
        """`B(o,a)` a secas. Lo único de que dispone un brazo sin memoria: no se
        inventa un cue, ni un token neutral, ni una orientación media."""
        return tuple(self._body.predict(observation, a) for a in Direction)

    def fingerprint(self) -> str:
        h = hashlib.sha256()
        h.update(self._body.digest().encode())
        h.update(self._orientation.digest().encode())
        return h.hexdigest()

    @property
    def intact(self) -> bool:
        return self.fingerprint() == self._birth


class BaselineRegression(RuntimeError):
    """`LEVEL11_BASELINE_REGRESSION`. La semilla se excluye antes de 1.3."""


def reconstruct(seed: int, *, semantics: CueSemantics | None = None,
                verify: bool = True) -> FrozenLevel11Core:
    """La receta determinista de `level11.experiment.run_seed`, y después
    read-only. Verificar es **precondición, no adquisición**."""
    semantics = semantics or CueSemantics.identity()
    holdout = build_holdout(semantics, seed=0)

    body = train_body(seed)
    stream = orientation_babbling(seed + 7, n=N_ORIENTATION, semantics=semantics,
                                  holdout=holdout)
    q = train_orientation(stream, semantics)

    if verify:
        if stream.violations:
            raise BaselineRegression(
                f"semilla {seed}: {stream.violations} violaciones del contrato físico")
        if stream.holdout_violations:
            raise BaselineRegression(
                f"semilla {seed}: {stream.holdout_violations} fugas del holdout")
        if stream.informative_minimum < 30:
            raise BaselineRegression(
                f"semilla {seed}: cobertura informativa "
                f"{stream.informative_minimum} < 30")
        compuesto = Level11Agent(body, q)
        bs = brier(compuesto, semantics).balanced
        if bs > 0.01:
            raise BaselineRegression(
                f"semilla {seed}: BS_balanced del compuesto 1.1 = {bs:.4f} > 0.01")
        if alignment_rate_expected(compuesto, semantics) < 0.999:
            raise BaselineRegression(
                f"semilla {seed}: R_align del compuesto 1.1 degradado")

    return FrozenLevel11Core(body, FrozenDirectional(q))
