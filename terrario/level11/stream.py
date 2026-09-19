"""La experiencia del Nivel 1.1 · cuatro azares separados y un holdout que se respeta.

La adquisición es actividad motora basal, igual que en 1.0: los actos son
uniformes y **no dependen de la política**, así que un flujo grabado sirve para
todos los brazos. Lo nuevo es la señal, y con ella tres cuidados.

**La dirección física se deriva de las posiciones, nunca del comando.** Hoy
coinciden, pero esa coincidencia es una propiedad del mundo actual y no del
contrato; depender de ella dejaría el experimento a merced de cualquier remapeo
futuro y haría indistinguible «aprendió» de «los enums están alineados».

**Cuatro generadores, no uno.** Mundo, acto, señal y lectura. Si compartieran
uno, la señal quedaría correlacionada con el mundo por el orden de consumo, y
`g ⊥ o` es exactamente lo que hace que la tarea exija las dos entradas.

**El holdout se esquiva sorteando otra señal, jamás cambiando el mundo.** Si al
tropezar con un par retenido se regenerara la rejilla, el holdout modificaría la
distribución de observaciones y dejaría de ser sólo una retirada de
combinaciones.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Iterable, Sequence

import numpy as np

from terrario.level11.cue import (
    ALL_CUES, CueSemantics, CueToken, physical_direction,
)
from terrario.level11.world import (
    ALL_OBSERVATIONS, Direction, Grid, Observation, Transition,
)


@dataclass(frozen=True)
class OrientationExperience:
    """La experiencia del 1.0 más la señal y lo que el cuerpo hizo de verdad."""

    base: Transition
    cue: CueToken
    physical: Direction | None

    @property
    def observation(self) -> Observation:
        return self.base.observation

    @property
    def action(self) -> Direction:
        return self.base.direction

    @property
    def moved(self) -> int:
        return self.base.moved


# --- el holdout composicional -------------------------------------------------

def build_holdout(semantics: CueSemantics, *, seed: int = 0,
                  attempts: int = 500_000) -> frozenset[tuple[Observation, CueToken]]:
    """16 pares `(o, g)` retirados, con las cuatro restricciones a la vez.

        · exactamente uno por observación   → las 16 observaciones ceden una señal
        · exactamente cuatro por señal      → ninguna señal desaparece del todo
        · ocho accionables y ocho bloqueados → el holdout no sesga hacia un estrato

    Sin la última, el holdout podría quedarse sólo con estados bloqueados y la
    transferencia se mediría donde la conducta no cuenta.
    """
    rng = np.random.default_rng(seed)
    for _ in range(attempts):
        elegidos = [ALL_CUES[int(rng.integers(4))] for _ in ALL_OBSERVATIONS]
        if set(Counter(elegidos).values()) != {4}:
            continue
        accionables = sum(1 for o, g in zip(ALL_OBSERVATIONS, elegidos)
                          if o[int(semantics.direction_of(g))] == 0)
        if accionables == 8:
            return frozenset(zip(ALL_OBSERVATIONS, elegidos))
    raise RuntimeError("no se encontró un holdout que cumpla las cuatro restricciones")


# --- el flujo -----------------------------------------------------------------

@dataclass
class OrientationStream:
    experiences: list[OrientationExperience]
    violations: int
    holdout_violations: int
    redraws: int

    def coverage(self) -> dict[tuple[CueToken, Direction], int]:
        """Evidencia **informativa** por asociación: sólo las que se movieron."""
        conteo = {(c, a): 0 for c in ALL_CUES for a in Direction}
        for e in self.experiences:
            if e.moved and e.physical is not None:
                conteo[(e.cue, e.action)] += 1
        return conteo

    @property
    def informative_minimum(self) -> int:
        return min(self.coverage().values())


def orientation_babbling(
    seed: int, *, n: int, semantics: CueSemantics,
    holdout: Iterable[tuple[Observation, CueToken]] = (),
    grid_size: int = 7, wall_probability: float = 0.25,
    steps_per_layout: int = 64,
) -> OrientationStream:
    """Actividad motora basal con señal externa independiente del mundo."""
    retenidos = frozenset(holdout)
    rng_world = np.random.default_rng([seed, 1])
    rng_action = np.random.default_rng([seed, 2])
    rng_cue = np.random.default_rng([seed, 3])

    experiencias: list[OrientationExperience] = []
    violaciones = fugas = resorteos = 0

    while len(experiencias) < n:
        grid = Grid.random(grid_size, wall_probability, rng_world)
        for _ in range(steps_per_layout):
            if len(experiencias) >= n:
                break
            observation = grid.observe()

            cue = ALL_CUES[int(rng_cue.integers(4))]
            while (observation, cue) in retenidos:   # se resortea la SEÑAL
                cue = ALL_CUES[int(rng_cue.integers(4))]
                resorteos += 1
            if (observation, cue) in retenidos:
                fugas += 1

            action = Direction(int(rng_action.integers(len(Direction))))
            antes = grid.position
            moved, next_observation = grid.step(action)
            fisica = physical_direction(antes, grid.position)

            if moved != (1 - observation[int(action)]):
                violaciones += 1
            if bool(moved) != (fisica is not None):
                violaciones += 1

            experiencias.append(OrientationExperience(
                Transition(observation, action, moved, next_observation),
                cue, fisica))

    return OrientationStream(experiencias, violaciones, fugas, resorteos)
