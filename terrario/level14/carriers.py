"""Los portadores · dos alfabetos opacos y una biyección que hay que aprender.

**No son identidad de objeto.** Lo que persiste entre ensayos es la ligadura
`x ↔ ψ(x)` --un **canal**--, no la ligadura a un referente. La analogía exacta:
dos frecuencias de radio que se sabe que llevan la misma emisión. Saber cuáles se
emparejan es conocimiento real, `log₂(4!) = 4.585` bits, y no dice absolutamente
nada sobre qué se está emitiendo.

`Enum` y no `IntEnum`, y dos tipos disjuntos: sin ordinal compartido no se puede
confundir un portador con un atributo ni comparar los dos alfabetos por valor.
Ese descuido ya mordió una vez en este linaje --`CueToken.C0 == Direction.UP` es
cierto porque los dos son `IntEnum`--.
"""

from __future__ import annotations

import enum
from itertools import permutations


class DirectionCarrier(enum.Enum):
    """Acompaña a la señal direccional. `X0` no significa `UP`."""

    X0 = "x0"
    X1 = "x1"
    X2 = "x2"
    X3 = "x3"


class ProximityCarrier(enum.Enum):
    """Acompaña a la evidencia de proximidad. `Y2` no significa `NEAR`."""

    Y0 = "y0"
    Y1 = "y1"
    Y2 = "y2"
    Y3 = "y3"


ALL_X: tuple[DirectionCarrier, ...] = tuple(DirectionCarrier)
ALL_Y: tuple[ProximityCarrier, ...] = tuple(ProximityCarrier)

Psi = dict[DirectionCarrier, ProximityCarrier]

#: La del preregistro. El agente no la recibe: la aprende contando.
CANONICAL_PSI: Psi = {DirectionCarrier.X0: ProximityCarrier.Y2,
                      DirectionCarrier.X1: ProximityCarrier.Y0,
                      DirectionCarrier.X2: ProximityCarrier.Y3,
                      DirectionCarrier.X3: ProximityCarrier.Y1}


def all_psi() -> list[Psi]:
    """Las `4! = 24` biyecciones. Parametrizan el contrato «ψ no está cableada»."""
    return [dict(zip(ALL_X, orden)) for orden in permutations(ALL_Y)]


def invert(psi: Psi) -> dict[ProximityCarrier, DirectionCarrier]:
    inversa = {y: x for x, y in psi.items()}
    if len(inversa) != len(psi):
        raise ValueError("ψ debe ser biyectiva")
    return inversa
