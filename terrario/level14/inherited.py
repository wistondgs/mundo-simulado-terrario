"""El Nivel 1.2 completo, congelado · **tres** envoltorios.

Cada nivel de este linaje ha congelado lo que heredaba y ha dejado mutable lo que
añadía: 1.1 congeló `B`, 1.2 congeló `Q`, y nadie construyó nunca el de `H`
--`QualitativeDistanceModel.observe` existe y `Level12Agent` publica
`self.proximity`--. Envolver el agente dejaría `core.proximity.observe(...)` al
alcance de un descuido.
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
from terrario.level12.metrics import max_oracle_deviation, population_brier
from terrario.level12.proximity import QualitativeDistanceModel
from terrario.level12.reference import ProximityToken
from terrario.level12.stream import N_DISTANCE, build_stream, train_distance


class FrozenDirectional:
    def __init__(self, trained: DirectionalAssociation) -> None:
        self._inner = trained
        self._birth = self.digest()

    def predict(self, cue: CueToken, action: Direction) -> float:
        return self._inner.predict(cue, action)

    def digest(self) -> str:
        h = hashlib.sha256()
        for key in sorted(self._inner._belief, key=repr):
            h.update(repr(key).encode())
            h.update(repr(self._inner._belief[key]).encode())
        return h.hexdigest()

    @property
    def intact(self) -> bool:
        return self.digest() == self._birth


class FrozenProximity:
    """`H` ya adquirida, sin `observe`. El envoltorio que faltaba en el linaje."""

    def __init__(self, trained: QualitativeDistanceModel) -> None:
        self._inner = trained
        self._birth = self.digest()

    def predict_near(self, sensor: ProximityToken) -> float:
        return self._inner.predict_near(sensor)

    def posteriors(self) -> tuple[float, ...]:
        return self._inner.posteriors()

    def digest(self) -> str:
        return self._inner.digest()

    @property
    def intact(self) -> bool:
        return self.digest() == self._birth


class FrozenLevel12Core:
    def __init__(self, body: FrozenFactoredBody, orientation: FrozenDirectional,
                 proximity: FrozenProximity) -> None:
        self._body = body
        self._orientation = orientation
        self._proximity = proximity
        self._birth = self.fingerprint()

    def predict_body(self, observation: Observation, action: Direction) -> float:
        return self._body.predict(observation, action)

    def predict_orientation(self, cue: CueToken, action: Direction) -> float:
        return self._orientation.predict(cue, action)

    def predict_near(self, sensor: ProximityToken) -> float:
        return self._proximity.predict_near(sensor)

    def posteriors(self) -> tuple[float, ...]:
        return self._proximity.posteriors()

    def fingerprints(self) -> dict[str, str]:
        return {"B": self._body.digest(), "Q": self._orientation.digest(),
                "H": self._proximity.digest()}

    def fingerprint(self) -> str:
        h = hashlib.sha256()
        for k, v in sorted(self.fingerprints().items()):
            h.update(k.encode()); h.update(v.encode())
        return h.hexdigest()

    @property
    def intact(self) -> bool:
        return self.fingerprint() == self._birth


class BaselineRegression(RuntimeError):
    """`LEVEL12_PRECONDITION_NOT_VERIFIED`. La celda se excluye antes de 1.4."""


def reconstruct(seed: int, *, semantics: CueSemantics | None = None,
                verify: bool = True) -> FrozenLevel12Core:
    semantics = semantics or CueSemantics.identity()
    holdout = build_holdout(semantics, seed=0)

    body = train_body(seed)
    flujo_q = orientation_babbling(seed + 7, n=N_ORIENTATION, semantics=semantics,
                                   holdout=holdout)
    q = train_orientation(flujo_q, semantics)
    flujo_h = build_stream(seed, semantics, n=N_DISTANCE)
    h = QualitativeDistanceModel()
    train_distance(flujo_h, h)

    if verify:
        if flujo_q.violations or flujo_h.physics_violations:
            raise BaselineRegression(f"semilla {seed}: contrato físico roto")
        if flujo_q.holdout_violations:
            raise BaselineRegression(f"semilla {seed}: fugas del holdout")
        if min(flujo_q.informative_minimum, flujo_h.informative_minimum) < 30:
            raise BaselineRegression(f"semilla {seed}: cobertura insuficiente")
        compuesto = Level11Agent(body, q)
        if brier(compuesto, semantics).balanced > 0.01:
            raise BaselineRegression(f"semilla {seed}: Nivel 1.1 degradado")
        if alignment_rate_expected(compuesto, semantics) < 0.999:
            raise BaselineRegression(f"semilla {seed}: R_align degradado")
        if population_brier(h.predict_near) > 0.1480:
            raise BaselineRegression(f"semilla {seed}: Nivel 1.2 fuera de tolerancia")
        if max_oracle_deviation(h.predict_near) > 0.10:
            raise BaselineRegression(f"semilla {seed}: H fuera de tolerancia")

    return FrozenLevel12Core(body, FrozenDirectional(q), FrozenProximity(h))
