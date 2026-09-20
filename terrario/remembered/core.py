"""El organismo con las cinco capacidades · cuatro envoltorios y un registro.

`B`, `Q` y `H` vienen del núcleo congelado del Nivel 1.4; `ψ` se readquiere con
su banco determinista de 64 escenas y se congela aquí --nadie había construido un
envoltorio para el binder, porque el nivel que lo creó no lo necesitaba--; `M` no
tiene parámetros.

**Se reúnen procedimientos, no artefactos**, y «un solo núcleo» se comprueba por
identidad de objeto: dos núcleos con la misma huella seguirían siendo dos cuerpos.
"""

from __future__ import annotations

import hashlib

from terrario.level11.cue import CueSemantics, CueToken
from terrario.level11.world import Direction, Observation
from terrario.level12.reference import ProximityToken
from terrario.level14.binding import ConjunctiveBinder, train
from terrario.level14.carriers import (
    CANONICAL_PSI, DirectionCarrier, ProximityCarrier, Psi,
)
from terrario.level14.inherited import BaselineRegression, reconstruct as reconstruct_12
from terrario.level14.scene import acquisition_bank


class FrozenBinder:
    """`ψ` ya adquirida, sin `observe_single_reference`."""

    def __init__(self, trained: ConjunctiveBinder) -> None:
        self._inner = trained
        self._birth = self.digest()

    def association(self, x: DirectionCarrier, y: ProximityCarrier) -> float:
        return self._inner.association(x, y)

    def bind(self, scene):
        return self._inner.bind(scene)

    def digest(self) -> str:
        return self._inner.digest()

    @property
    def intact(self) -> bool:
        return self.digest() == self._birth


class FrozenRememberedOrganism:
    """Las cuatro estructuras aprendidas, juntas y sin una sola vía de mutación."""

    def __init__(self, core, binder: FrozenBinder) -> None:
        self._core = core
        self._binder = binder
        self._birth = self.fingerprint()

    def predict_body(self, observation: Observation, action: Direction) -> float:
        return self._core.predict_body(observation, action)

    def predict_orientation(self, cue: CueToken, action: Direction) -> float:
        return self._core.predict_orientation(cue, action)

    def predict_near(self, sensor: ProximityToken) -> float:
        return self._core.predict_near(sensor)

    def association(self, x: DirectionCarrier, y: ProximityCarrier) -> float:
        return self._binder.association(x, y)

    def bind(self, scene):
        return self._binder.bind(scene)

    def fingerprints(self) -> dict[str, str]:
        return {**self._core.fingerprints(), "psi": self._binder.digest()}

    def fingerprint(self) -> str:
        h = hashlib.sha256()
        for k, v in sorted(self.fingerprints().items()):
            h.update(k.encode()); h.update(v.encode())
        return h.hexdigest()

    @property
    def intact(self) -> bool:
        return self.fingerprint() == self._birth


def reconstruct(seed: int, *, psi: Psi | None = None,
                semantics: CueSemantics | None = None,
                verify: bool = True) -> FrozenRememberedOrganism:
    psi = psi or CANONICAL_PSI
    core = reconstruct_12(seed, semantics=semantics, verify=verify)
    binder = ConjunctiveBinder()
    train(binder, acquisition_bank(psi))
    if verify and abs(binder.association(*next(iter(psi.items()))) - 0.85) > 1e-12:
        raise BaselineRegression(f"semilla {seed}: ψ no alcanzó 17/20")
    return FrozenRememberedOrganism(core, FrozenBinder(binder))
