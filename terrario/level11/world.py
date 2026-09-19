# ─────────────────────────────────────────────────────────────────────────────
# COPIA · Agente de Nivel 1.1
#
# Copiado literalmente de `terrario/level1/world.py` en `d278f59`, con el único
# cambio de la ruta del paquete. El comportamiento es idéntico por construcción:
# si estos ficheros divergieran del original, el 1.1 dejaría de heredar lo que el
# Experimento 1 demostró.
#
# **Por qué una copia y no un import.** El Nivel 1 está contaminado: sus semillas
# tienen resultados leídos, su desarme mecanístico miró la dirección del efecto, y
# el reversal vive en su mismo paquete. Importar de él ataría el linaje nuevo a
# esa historia; copiarlo lo separa de verdad, al precio de tener que mantener la
# equivalencia explícitamente.
# ─────────────────────────────────────────────────────────────────────────────

"""El mundo del Nivel 1 · rejilla, paredes y un cuerpo. Nada más.

No hay objetos, ni recursos, ni energía. Es deliberado: el primer experimento
pregunta si la experiencia motora produce conocimiento sobre las consecuencias
de los propios actos, y cualquier otra cosa en el mundo sería una explicación
alternativa del resultado.

La observación son cuatro bits --si la celda contigua está bloqueada en cada
dirección-- y nada más. Dieciséis configuraciones posibles. Al organismo **no**
se le programa la regla `bloqueado ⇒ no me desplazo`: ésa es exactamente la
contingencia que tiene que adquirir.

Las direcciones y sus deltas son los mismos que usa el motor del mundo grande
(`terrario/core/types.py`), para que un resultado de aquí siga significando lo
mismo si el ser se muda allí.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass

import numpy as np


class Direction(enum.IntEnum):
    """Mismo orden y mismos índices que el vocabulario motor del mundo grande."""

    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


DELTA: dict[Direction, tuple[int, int]] = {
    Direction.UP: (-1, 0),
    Direction.DOWN: (1, 0),
    Direction.LEFT: (0, -1),
    Direction.RIGHT: (0, 1),
}

#: Cuatro bits: uno por dirección, `1` si la celda contigua está bloqueada.
Observation = tuple[int, int, int, int]

#: Las dieciséis configuraciones sensoriales que este mundo puede producir.
ALL_OBSERVATIONS: tuple[Observation, ...] = tuple(
    (a, b, c, d) for a in (0, 1) for b in (0, 1) for c in (0, 1) for d in (0, 1)
)


@dataclass(frozen=True)
class Transition:
    """La experiencia elemental: lo que vi, lo que hice, y si me moví."""

    observation: Observation
    direction: Direction
    moved: int
    next_observation: Observation


class Grid:
    """Una rejilla con borde cerrado y paredes interiores al azar.

    El borde siempre está cerrado para que el cuerpo no pueda salirse y para que
    toda posición libre tenga al menos una dirección definida. Las paredes
    interiores son las que dan variedad sensorial.
    """

    def __init__(self, cells: np.ndarray, position: tuple[int, int]) -> None:
        self.cells = cells
        self.position = position

    @classmethod
    def random(cls, size: int, wall_probability: float,
               rng: np.random.Generator) -> Grid:
        if size < 5:
            raise ValueError(f"el lado debe ser >= 5; se pidió {size}")
        cells = np.zeros((size, size), dtype=np.uint8)
        cells[0, :] = cells[-1, :] = 1
        cells[:, 0] = cells[:, -1] = 1
        cells[1:-1, 1:-1] = (rng.random((size - 2, size - 2))
                             < wall_probability).astype(np.uint8)
        free = np.argwhere(cells == 0)
        if len(free) == 0:
            raise RuntimeError("la rejilla generada no tiene ninguna celda libre")
        row, col = free[int(rng.integers(len(free)))]
        return cls(cells, (int(row), int(col)))

    # --- lo que el organismo percibe ----------------------------------------

    def observe(self) -> Observation:
        """Los cuatro bits. Es todo lo que el ser recibe del mundo."""
        row, col = self.position
        return tuple(  # type: ignore[return-value]
            int(self.cells[row + DELTA[d][0], col + DELTA[d][1]] == 1)
            for d in Direction
        )

    # --- lo que el mundo hace con un acto ------------------------------------

    def step(self, direction: Direction) -> tuple[int, Observation]:
        """Intentar el desplazamiento. Devuelve `(me moví, lo que veo ahora)`."""
        row, col = self.position
        target = (row + DELTA[direction][0], col + DELTA[direction][1])
        if self.cells[target] == 1:
            return 0, self.observe()
        self.position = target
        return 1, self.observe()

    def relocate(self, rng: np.random.Generator) -> None:
        """Teletransportar a una celda libre cualquiera.

        Sirve para sondear: permite presentar la MISMA situación a brazos
        distintos en vez de dejar que cada uno visite lo que su propia conducta
        le lleve a visitar.
        """
        free = np.argwhere(self.cells == 0)
        row, col = free[int(rng.integers(len(free)))]
        self.position = (int(row), int(col))


def physics_contract(observation: Observation, direction: Direction) -> int:
    """Lo que la física DEBE producir: `movido = 1 - bloqueado`.

    En este mundo elemental el bit sensorial de la dirección elegida determina
    exactamente si el desplazamiento es posible. Es el GATE 0, y se comprueba
    contra el mundo en vez de suponerse: si alguna vez deja de cumplirse, el
    experimento no mide aprendizaje sino un defecto de instrumentación.
    """
    return 1 - observation[int(direction)]
