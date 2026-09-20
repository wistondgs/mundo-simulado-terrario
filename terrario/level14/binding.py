"""La única adquisición del Nivel 1.4 · `C(y|x)`, dieciséis contadores.

**La firma está cerrada a portadores.** `observe_single_reference` no acepta cue,
sensor, dirección, `NEAR/FAR` ni identificador alguno: así no puede reaprender lo
que ya saben `Q` y `H`, y la separación deja de depender de la disciplina de quien
llama.

La inferencia **no lee `g` ni `s`**: es puramente de portadores. Y las
asignaciones se enumeran ordenando por el **nombre** del portador, nunca por la
posición en que llegaron — de lo contrario el orden de presentación sería el que
decide, que es justo el atajo que hay que excluir.
"""

from __future__ import annotations

import hashlib

import numpy as np

from terrario.level14.carriers import (
    ALL_X, ALL_Y, DirectionCarrier, ProximityCarrier, Psi,
)
from terrario.level14.scene import BindingObservation, DirectionItem, ProximityItem

Assignment = dict[DirectionItem, ProximityItem]


def _assignments(scene: BindingObservation) -> list[Assignment]:
    """Las asignaciones posibles, en orden canónico por nombre de portador."""
    ds = sorted(scene.directions, key=lambda d: d.carrier.value)
    ps = sorted(scene.proximities, key=lambda p: p.carrier.value)
    if len(ds) == 1:
        return [{ds[0]: ps[0]}]
    return [{ds[0]: ps[0], ds[1]: ps[1]}, {ds[0]: ps[1], ds[1]: ps[0]}]


class ConjunctiveBinder:
    """`C(y|x) = A_xy / Σ_y' A_xy'`. Prior 1 en las dieciséis celdas."""

    def __init__(self, *, prior: float = 1.0, frozen: bool = False) -> None:
        self.prior = prior
        self.frozen = frozen
        self._counts = np.full((4, 4), prior, dtype=float)

    def observe_single_reference(self, x: DirectionCarrier,
                                 y: ProximityCarrier) -> bool:
        if self.frozen:
            return False
        self._counts[ALL_X.index(x), ALL_Y.index(y)] += 1
        return True

    def association(self, x: DirectionCarrier, y: ProximityCarrier) -> float:
        fila = self._counts[ALL_X.index(x)]
        return float(fila[ALL_Y.index(y)] / fila.sum())

    def bind(self, scene: BindingObservation) -> list[tuple[Assignment, float]]:
        opciones = _assignments(scene)
        pesos = [np.prod([self.association(d.carrier, p.carrier)
                          for d, p in a.items()]) for a in opciones]
        total = float(sum(pesos))
        if total <= 0:
            return [(a, 1.0 / len(opciones)) for a in opciones]
        return [(a, float(w) / total) for a, w in zip(opciones, pesos)]

    def digest(self) -> str:
        return hashlib.sha256(self._counts.tobytes()).hexdigest()


class UniformBinder(ConjunctiveBinder):
    """`UNBOUND` · no recibe `C(y|x)`. Por simetría reparte mitad y mitad."""

    def association(self, x: DirectionCarrier, y: ProximityCarrier) -> float:
        return 0.25

    def observe_single_reference(self, x, y) -> bool:
        return False


class BlindBinder(ConjunctiveBinder):
    """`SINGLE_G` / `SINGLE_D` · sólo ve una modalidad, luego no discrimina."""

    def __init__(self, *, ignore: str) -> None:
        super().__init__()
        if ignore not in ("direction", "proximity"):
            raise ValueError(ignore)
        self.ignore = ignore

    def association(self, x: DirectionCarrier, y: ProximityCarrier) -> float:
        if self.ignore == "direction":
            return float(self._counts[:, ALL_Y.index(y)].sum()
                         / self._counts.sum())
        return float(self._counts[ALL_X.index(x)].sum() / self._counts.sum())


class OracleBinder(ConjunctiveBinder):
    """Conoce `ψ`. **No aprende.** Es el techo, y vale exactamente `0`."""

    def __init__(self, psi: Psi) -> None:
        super().__init__()
        self.psi = psi

    def association(self, x: DirectionCarrier, y: ProximityCarrier) -> float:
        return 1.0 if self.psi[x] is y else 0.0

    def observe_single_reference(self, x, y) -> bool:
        return False


class IndexBinder:
    """FIXTURE NEGATIVA · empareja por posición. Sobre la escena ordenada acierta
    exactamente la mitad; sobre una escena de conjuntos no es ni expresable."""

    def bind_ordered(self, scene) -> Assignment:
        return dict(zip(scene.directions, scene.proximities))


def train(binder: ConjunctiveBinder,
          bank: list[tuple[DirectionItem, ProximityItem]]) -> None:
    for d, p in bank:
        binder.observe_single_reference(d.carrier, p.carrier)
