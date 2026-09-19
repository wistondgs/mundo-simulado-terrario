"""El Agente de Nivel 1.1 · dos conocimientos, un producto.

    J(o, g, a) = B(o, a) · Q(g, a)

El primer factor es el cuerpo del Nivel 1.0, congelado. El segundo es la única
adquisición nueva. El producto es `P(Z=1)`, la probabilidad de que la acción sea
a la vez **físicamente realizable** y **coincidente con la referencia**.

**La factorización la suministramos nosotros.** El organismo no la descubrió, y
eso limita lo que puede afirmarse: 1.1 demuestra que una adquisición nueva puede
montarse encima del conocimiento anterior sin modificarlo, no que el ser haya
inventado cómo combinarlas.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from terrario.level11.cue import CueToken
from terrario.level11.world import Direction, Observation


class ConstantOrientation:
    """`Q ≡ c`. Con `c = 0.5` es el brazo congelado; con `1.0`, BODY-ONLY puro."""

    def __init__(self, value: float = 0.5) -> None:
        self.value = value
        self.frozen = True

    def predict(self, cue: CueToken, action: Direction) -> float:
        return self.value

    def observe(self, *args: Any, **kwargs: Any) -> bool:
        return False


class Level11Agent:
    """Composición. Sin heurísticas, sin reglas sobre nombres de tokens."""

    def __init__(self, body: Any, orientation: Any, *, name: str = "COMPOSITE") -> None:
        self.body = body
        self.orientation = orientation
        self.name = name

    def predict(self, observation: Observation, cue: CueToken,
                action: Direction) -> float:
        return (self.body.predict(observation, action)
                * self.orientation.predict(cue, action))

    def act(self, observation: Observation, cue: CueToken,
            rng: np.random.Generator) -> Direction:
        values = np.asarray([self.predict(observation, cue, d) for d in Direction],
                            dtype=float)
        tied = np.flatnonzero(np.isclose(values, values.max()))
        return Direction(int(rng.choice(tied)))


class ConstantAgent:
    """Predice siempre el mismo número. Referencia obligatoria del informe.

    `ConstantAgent(0.0)` es el «siempre-cero» que empata en el total con brazos
    informados y con perfiles de fallo opuestos; `ConstantAgent(0.5)` es el
    ignorante. Ninguno de los dos se reporta como resultado: se reportan para que
    un `BS_total` no se lea como competencia.
    """

    def __init__(self, value: float, *, name: str) -> None:
        self.value = value
        self.name = name

    def predict(self, observation: Observation, cue: CueToken,
                action: Direction) -> float:
        return self.value

    def act(self, observation: Observation, cue: CueToken,
            rng: np.random.Generator) -> Direction:
        return Direction(int(rng.integers(len(Direction))))
