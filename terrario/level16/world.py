"""El mundo de 1.6 y la cuarentena de flujos aleatorios.

La física no se reimplementa: es la del Nivel 1.0, importada tal cual desde
`terrario.level1.world`. Los parámetros tampoco se eligen aquí --se heredan del
experimento canónico del 1.0 (`terrario/level1/measurement.py:52,55`)-- y están
escritos en la Enmienda 02 precisamente para que dejen de ser un grado de
libertad de quien implementa.

La cuarentena de flujos es lo que hace determinista la regla de consumo de
semillas: evaluar si un mundo es degenerado no puede alterar la vida que ese
mundo produciría. Se consigue derivando tres flujos disjuntos de la misma
semilla en vez de compartir uno solo.
"""

from __future__ import annotations

import numpy as np

from terrario.level1.world import Grid

#: Lado de la rejilla. Nivel 1.0 canónico.
GRID_SIZE = 7

#: Densidad de paredes interiores. Nivel 1.0 canónico.
WALL_PROBABILITY = 0.25

#: Índices de los flujos derivados. Ver Enmienda 01 §5.
_WORLD, _MOTOR, _SHUFFLE = 0, 1, 2


def world_stream(seed: int) -> np.random.Generator:
    """Flujo que construye la rejilla y sortea la celda natal."""
    return np.random.default_rng([seed, _WORLD])


def motor_stream(seed: int) -> np.random.Generator:
    """Flujo de la fuente motora del organismo. Nunca lo toca el evaluador."""
    return np.random.default_rng([seed, _MOTOR])


def shuffle_stream(seed: int) -> np.random.Generator:
    """Flujo del control TEMPORAL-SHUFFLED. Jamás participa de la trayectoria."""
    return np.random.default_rng([seed, _SHUFFLE])


def build_world(seed: int) -> Grid:
    """La rejilla de esta semilla, con su cuerpo ya colocado.

    Llamarla dos veces con la misma semilla da mundos idénticos, y hacerlo no
    consume nada del flujo motor: ésa es la propiedad que permite evaluar el
    predicado de degeneración antes de decidir si la vida se corre.
    """
    return Grid.random(GRID_SIZE, WALL_PROBABILITY, world_stream(seed))
