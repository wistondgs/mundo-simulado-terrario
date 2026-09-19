"""El Nivel 1.1 completo, congelado y de sólo lectura.

Congelar el cuerpo no basta. `FrozenFactoredBody` no expone `observe`, pero
`DirectionalAssociation.observe` **sí existe** y `Level11Agent` publica
`self.orientation`: envolver el agente tal cual dejaría la mutación de `Q` al
alcance de un descuido. Hacen falta **dos** envoltorios.

No hay estado persistido del Nivel 1.1 en ninguna parte del repositorio --se
comprobó: ni `pickle`, ni `np.save`, ni `json.dump`--, así que el núcleo se
**reconstruye** con la receta determinista de `run_seed`, y se verifica antes de
congelarlo. Esa verificación es **precondición, no adquisición**: si la semilla
no reproduce un 1.1 competente, se excluye antes de que 1.2 empiece.

`terrario/level11/` no se modifica. Todo lo de aquí lo envuelve desde fuera.
"""

from __future__ import annotations

import hashlib
from typing import Any

import numpy as np

from terrario.level11.agent import Level11Agent
from terrario.level11.body import FrozenFactoredBody
from terrario.level11.cue import CueSemantics, CueToken
from terrario.level11.experiment import (
    N_ORIENTATION, train_body, train_orientation,
)
from terrario.level11.metrics import alignment_rate_expected, brier
from terrario.level11.orientation import DirectionalAssociation
from terrario.level11.stream import build_holdout, orientation_babbling
from terrario.level11.world import Direction, Observation


def cue_for(semantics: CueSemantics, direction: Direction) -> CueToken:
    """La inversa de `direction_of`. `CueSemantics` garantiza biyección.

    Vive aquí y no en `level11/` porque el Nivel 1.1 está cerrado. Lee sólo el
    campo público `mapping` de un dataclass congelado.
    """
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
    """Las dos adquisiciones previas, juntas y sin una sola vía de mutación.

    Expone exactamente `predict_body`, `predict_orientation`, `predict`, `act` y
    `fingerprint`. **No expone `observe`** --ni propio ni heredado-- y no publica
    los modelos mutables originales.
    """

    def __init__(self, body: FrozenFactoredBody,
                 orientation: FrozenDirectional) -> None:
        self._body = body
        self._orientation = orientation
        self._birth = self.fingerprint()

    def predict_body(self, observation: Observation, action: Direction) -> float:
        return self._body.predict(observation, action)

    def predict_orientation(self, cue: CueToken, action: Direction) -> float:
        return self._orientation.predict(cue, action)

    def predict(self, observation: Observation, cue: CueToken,
                action: Direction) -> float:
        """`B·Q`, la superficie del Nivel 1.1. La política 1.2 es ésta y sólo ésta."""
        return (self._body.predict(observation, action)
                * self._orientation.predict(cue, action))

    def act(self, observation: Observation, cue: CueToken,
            rng: np.random.Generator) -> Direction:
        values = np.asarray([self.predict(observation, cue, d) for d in Direction],
                            dtype=float)
        tied = np.flatnonzero(np.isclose(values, values.max()))
        return Direction(int(rng.choice(tied)))

    def fingerprint(self) -> str:
        h = hashlib.sha256()
        h.update(self._body.digest().encode())
        h.update(self._orientation.digest().encode())
        return h.hexdigest()

    @property
    def intact(self) -> bool:
        return self.fingerprint() == self._birth


class BaselineRegression(RuntimeError):
    """`LEVEL11_BASELINE_REGRESSION`. La semilla se excluye antes de 1.2."""


def reconstruct(seed: int, *, semantics: CueSemantics | None = None,
                verify: bool = True) -> FrozenLevel11Core:
    """La receta exacta de `level11.experiment.run_seed`, y después read-only."""
    semantics = semantics or CueSemantics.identity()
    holdout = build_holdout(semantics, seed=0)          # congelado, no por semilla

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
                f"semilla {seed}: cobertura informativa {stream.informative_minimum} < 30")
        compuesto = Level11Agent(body, q)
        bs = brier(compuesto, semantics).balanced
        if bs > 0.01:
            raise BaselineRegression(
                f"semilla {seed}: BS_balanced del compuesto 1.1 = {bs:.4f} > 0.01")
        if alignment_rate_expected(compuesto, semantics) < 0.999:
            raise BaselineRegression(f"semilla {seed}: R_align del compuesto 1.1 degradado")

    return FrozenLevel11Core(body, FrozenDirectional(q))
