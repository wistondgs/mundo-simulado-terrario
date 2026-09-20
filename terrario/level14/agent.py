"""El Agente de Nivel 1.4 · el binder decide qué va con qué, y nada más.

Tras inferir el binding el organismo **no crea semántica nueva**: consulta `Q`
para la dirección y `H` para la proximidad, las dos congeladas. El binder sólo
decide *qué `s` corresponde a qué `g`*.

    ĥ_d  = Σ_b P(b|O) · H(s asignado a d por b)
    V(a) = Σ_d Q(cue de d, a) · ĥ_d

`V` es **diagnóstico**: no es recompensa y no es política motora nueva.
"""

from __future__ import annotations

from typing import Any

from terrario.level11.world import Direction
from terrario.level14.scene import BindingObservation, DirectionItem


class Level14Agent:
    """Núcleo 1.2 congelado más `C(y|x)`. La única estructura que cambia es `A_xy`."""

    def __init__(self, core: Any, binder: Any, *, name: str = "FULL_14") -> None:
        self._core = core
        self.binder = binder
        self.name = name

    def bind(self, scene: BindingObservation):
        return self.binder.bind(scene)

    def bound_near_profile(self, scene: BindingObservation
                           ) -> dict[DirectionItem, float]:
        perfil = {d: 0.0 for d in scene.directions}
        for asignacion, p in self.bind(scene):
            for d, prox in asignacion.items():
                perfil[d] += p * self._core.predict_near(prox.sensor)
        return perfil

    def directional_profile(self, scene: BindingObservation) -> tuple[float, ...]:
        perfil = self.bound_near_profile(scene)
        return tuple(sum(self._core.predict_orientation(d.cue, a) * h
                         for d, h in perfil.items()) for a in Direction)

    # --- lo heredado, para las sondas -----------------------------------------

    def predict_orientation(self, cue, action) -> float:
        return self._core.predict_orientation(cue, action)

    def predict_near(self, sensor) -> float:
        return self._core.predict_near(sensor)

    def association(self, x, y) -> float:
        return self.binder.association(x, y)

    def fingerprints(self) -> dict[str, str]:
        return self._core.fingerprints()

    @property
    def core(self) -> Any:
        return self._core
