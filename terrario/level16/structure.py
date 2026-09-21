"""El predicado de degeneración, y por qué se calcula sobre el mundo.

Un mundo no sirve para preguntar si se adquiere estructura temporal cuando no
hay estructura temporal que adquirir. El oráculo lo define estructuralmente:

    N-MUNDO  <=>  |O_alcanzables| < 2   ó   ninguna transición alcanzable cambia

Deliberadamente **no** se excluye por tamaño. Un bolsillo de cuatro celdas puede
enseñar perfectamente `P(o'|o)`; descartarlo sería seleccionar mundos favorables,
que es justo lo que este criterio existe para impedir. Los estratos se reportan
siempre, y un mundo pequeño pero no degenerado se conserva.

Las dos ramas del predicado son, de hecho, la misma condición: sobre un
componente conexo, `|O| >= 2` obliga a que algún par adyacente difiera, y
cruzarlo ya es una transición que cambia. La disyunción se conserva porque así
la selló el oráculo, pero la segunda rama no es un guardián independiente y no
admite fixture negativa propia. Verificado además en 30 000 mundos: cero casos.

La propiedad decisiva es *cuándo* se evalúa: esto es función exclusiva de la
rejilla y la celda natal, no requiere que el organismo exista y no consume un
solo paso de vida. Por eso el veredicto de una semilla está determinado antes de
que haya nada que rescatar a posteriori (Enmienda 01 §3).
"""

from __future__ import annotations

from dataclasses import dataclass

from terrario.level1.world import DELTA, Direction, Grid, Observation


def _signature(grid: Grid, cell: tuple[int, int]) -> Observation:
    """Los cuatro bits que se verían desde esa celda."""
    row, col = cell
    return tuple(  # type: ignore[return-value]
        int(grid.cells[row + DELTA[d][0], col + DELTA[d][1]] == 1)
        for d in Direction
    )


@dataclass(frozen=True)
class WorldStructure:
    """Todo lo que se puede saber del mundo sin vivirlo."""

    seed: int
    component_size: int
    observations: frozenset[Observation]
    transitions: frozenset[tuple[Observation, Observation]]

    @property
    def changing_transitions(self) -> int:
        """Transiciones alcanzables en las que la observación cambia."""
        return sum(1 for a, b in self.transitions if a != b)

    @property
    def stratum(self) -> str:
        """Estrato por tamaño del componente natal. Se reporta, no se filtra."""
        if self.component_size <= 3:
            return "<=3"
        return "4-6" if self.component_size <= 6 else ">6"


def describe_world(seed: int, grid: Grid) -> WorldStructure:
    """Recorrer el componente natal y enumerar lo que el mundo puede producir."""
    seen = {grid.position}
    stack = [grid.position]
    while stack:
        row, col = stack.pop()
        for direction in Direction:
            target = (row + DELTA[direction][0], col + DELTA[direction][1])
            if grid.cells[target] == 0 and target not in seen:
                seen.add(target)
                stack.append(target)

    signature = {cell: _signature(grid, cell) for cell in seen}
    transitions = set()
    for cell in seen:
        row, col = cell
        for direction in Direction:
            target = (row + DELTA[direction][0], col + DELTA[direction][1])
            landing = target if grid.cells[target] == 0 else cell
            transitions.add((signature[cell], signature[landing]))

    return WorldStructure(
        seed=seed,
        component_size=len(seen),
        observations=frozenset(signature.values()),
        transitions=frozenset(transitions),
    )


def is_nonworld(structure: WorldStructure) -> bool:
    """El predicado, literal: menos de dos observaciones, o ningún cambio."""
    return len(structure.observations) < 2 or structure.changing_transitions == 0
