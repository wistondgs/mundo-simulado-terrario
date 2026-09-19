"""La señal externa del Nivel 1.1 · tokens opacos y su semántica, separadas.

El agente recibe `C0, C1, C2, C3` y **nunca** la tabla que dice qué dirección
física significa cada uno. La separación no es estética: sin ella, resolver 1.1
es comparar dos enums, y una implementación que devuelva `1.0 if cue == action`
pasaría todos los gates sin haber aprendido nada.

Con tokens opacos esa solución **no se puede escribir**, y además el test de
permutación semántica pasa a ser expresable: se cambia la correspondencia, el
agente no se entera, y su conocimiento debe seguir a la experiencia y no al
nombre del token.

La semántica pertenece al experimento. `CueSemantics` no se pasa al agente, no
se consulta desde `predict` y no viaja dentro de ninguna experiencia.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass

from terrario.level11.world import DELTA, Direction


class CueToken(enum.IntEnum):
    """Cuatro símbolos sin significado. Lo único que el agente ve de la señal."""

    C0 = 0
    C1 = 1
    C2 = 2
    C3 = 3


ALL_CUES: tuple[CueToken, ...] = tuple(CueToken)


@dataclass(frozen=True)
class CueSemantics:
    """Qué dirección física significa cada token. **Del experimento, no del ser.**

    `identity()` es la correspondencia por defecto; `permuted()` existe para el
    test anti-atajo. Un aprendiz correcto rinde igual con las dos, porque
    aprende de lo que le pasa y no de cómo se llaman las cosas.
    """

    mapping: dict[CueToken, Direction]

    @classmethod
    def identity(cls) -> CueSemantics:
        return cls({CueToken(i): Direction(i) for i in range(4)})

    @classmethod
    def permuted(cls, order: tuple[int, int, int, int]) -> CueSemantics:
        if sorted(order) != [0, 1, 2, 3]:
            raise ValueError(f"no es una permutación de las cuatro: {order}")
        return cls({CueToken(i): Direction(d) for i, d in enumerate(order)})

    def direction_of(self, cue: CueToken) -> Direction:
        return self.mapping[cue]

    def __post_init__(self) -> None:
        if set(self.mapping) != set(ALL_CUES):
            raise ValueError("faltan tokens en la correspondencia")
        if len(set(self.mapping.values())) != 4:
            raise ValueError("la correspondencia debe ser biyectiva")


def physical_direction(before: tuple[int, int],
                       after: tuple[int, int]) -> Direction | None:
    """La dirección que el cuerpo recorrió DE HECHO, desde las posiciones.

    Nunca se asume `dirección física = comando`, aunque hoy coincidan: esa
    coincidencia es una propiedad del mundo actual, no del contrato, y
    depender de ella dejaría el experimento a merced de un remapeo futuro.
    Devuelve `None` si no hubo desplazamiento.
    """
    delta = (after[0] - before[0], after[1] - before[1])
    if delta == (0, 0):
        return None
    for direction, step in DELTA.items():
        if step == delta:
            return direction
    raise ValueError(f"desplazamiento que no corresponde a ninguna dirección: {delta}")
