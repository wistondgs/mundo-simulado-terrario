"""El mundo B físico · el gemelo marginalizado sobre la acción.

    T_B(s'|s,a)  =  (1/4) · Σ_b T_A(s'|s,b)      para toda a

El organismo sigue generando y viendo su comando; el mundo ejecuta internamente
una dirección sorteada con independencia de él. Verificado en la transición 1.6→1.7
al nivel del kernel de estados: A y B comparten topología, dinámica marginal,
estacionaria e `I(O;O')` **exacta**, y difieren sólo en que `I_B(A;O'|O) = 0`.

Es el control limpio del nivel: si `M_1` mejorase en B, la mejora no podría venir
de la acción --allí no hay nada que saber sobre ella-- sino de tener cuatro veces
más parámetros.

El flujo `[semilla, 65]` es propio de B: no toca ni el mundo, ni el motor, ni el
cableado, ni nada de 1.6.
"""

from __future__ import annotations

import numpy as np

from terrario.level1.world import Direction, Grid

_TWIN = 65


def twin_stream(seed: int) -> np.random.Generator:
    return np.random.default_rng([seed, _TWIN])


class MarginalisedBody:
    """Una rejilla que ignora el comando y sortea el actuador.

    Expone la misma interfaz que `Grid` en lo que la vida usa (`observe`,
    `step`), de modo que la fase P y la fase A no saben en qué mundo están.
    """

    def __init__(self, grid: Grid, rng: np.random.Generator) -> None:
        self._grid = grid
        self._rng = rng

    @property
    def position(self):
        return self._grid.position

    def observe(self):
        return self._grid.observe()

    def step(self, direction: Direction):
        """El comando llega y se descarta: el mundo elige por su cuenta."""
        del direction
        return self._grid.step(Direction(int(self._rng.integers(4))))
