"""El mundo B físico · el gemelo marginalizado sobre la acción.

    T_B(s'|s,a)  =  (1/4) · Σ_b T_A(s'|s,b)      para toda a

El organismo sigue generando y viendo su comando; el mundo ejecuta internamente
una dirección sorteada con independencia de él. Verificado en la transición 1.6→1.7
al nivel del kernel de estados: A y B comparten topología, dinámica marginal,
estacionaria e `I(O;O')` **exacta**, y difieren sólo en que `I_B(A;O'|O) = 0`.

Es el control limpio del nivel: si `M_1` mejorase en B, la mejora no podría venir
de la acción --allí no hay nada que saber sobre ella-- sino de tener cuatro veces
más parámetros.

El flujo `[semilla, 65]` es propio de B y **nunca se comparte con S0**: si el
efecto del mundo saliera del mismo azar que el comando, podría aparecer
dependencia comando–efecto precisamente en el mundo cuyo contrato es
`D_W = 0`. Tampoco toca el mundo, el cableado, la baraja ni las nulas.

Su estado es **serializable**, como el de la fuente motora: una vida de B no es
reproducible si el azar que decide el actuador no forma parte de la fotografía.
"""

from __future__ import annotations

import numpy as np

from terrario.level1.world import Direction, Grid

class TwinContractError(RuntimeError):
    """Se violó el contrato del mundo gemelo."""


_TWIN = 65


def twin_stream(seed: int) -> np.random.Generator:
    return np.random.default_rng([seed, _TWIN])


class MarginalisedBody:
    """Una rejilla que ignora el comando y sortea el actuador.

    Expone la misma interfaz que `Grid` en lo que la vida usa (`observe`,
    `step`), de modo que la fase P y la fase A no saben en qué mundo están.
    """

    def __init__(self, grid: Grid, rng: np.random.Generator) -> None:
        if not isinstance(rng, np.random.Generator):
            raise TwinContractError(
                "el efecto de B exige un Generator propio; se recibió "
                f"{type(rng).__name__}")
        self._grid = grid
        self._rng = rng
        self._draws = 0

    @property
    def position(self):
        return self._grid.position

    def observe(self):
        return self._grid.observe()

    def step(self, direction: Direction):
        """El comando llega y se descarta: el mundo elige por su cuenta."""
        del direction
        self._draws += 1
        return self._grid.step(Direction(int(self._rng.integers(4))))

    # --- serialización ------------------------------------------------------

    @property
    def draws(self) -> int:
        """Cuántas veces el mundo eligió. Debe igualar los pasos vividos."""
        return self._draws

    def state(self) -> dict:
        return {"rng": self._rng.bit_generator.state, "draws": self._draws}

    def restore(self, state: dict) -> None:
        if set(state) != {"rng", "draws"}:
            raise TwinContractError(
                "una fotografía del efecto de B sin el estado de su generador no "
                f"reproduce la vida; claves: {sorted(state)}")
        self._rng.bit_generator.state = state["rng"]
        self._draws = int(state["draws"])
