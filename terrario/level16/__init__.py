"""Agente de Nivel 1.6 · adquisición de estructura temporal del flujo sensorial.

Una sola adquisición: a partir de observaciones consecutivas producidas por su
propia vida motora, el ser aprende `P(o_{t+1} | o_t)`.

Lo que **no** hay aquí, y no es omisión sino contrato: identidad de la acción
dentro del aprendiz, copia eferente legible, recompensa, valor, novedad,
etiqueta de cambio, posición, estado oculto del mundo, y cualquier forma de
contingencia propia. Esto último pertenece a 1.7 y su ausencia es lo que hace
que un resultado aquí signifique algo.

El árbol donde vive este paquete no contiene `level11`, `level12`, `level13`,
`level14` ni las fusiones. La independencia respecto de B, Q, H, M y ψ es
estructural: esos módulos no existen en el disco.

Oráculo: `docs/LEVEL16_ORACULO_PREREGISTRADO.md` (9b0d39b) y sus enmiendas 01 y 02.
"""

from terrario.level16.motor import (  # noqa: F401
    EndogenousMotor, MotorContractError,
)
from terrario.level16.seeds import (  # noqa: F401
    LIVES_REQUIRED, SEED_WINDOW, SeedLedger, SeedPoolExhausted, SeedVerdict,
    consume_seeds,
)
from terrario.level16.structure import (  # noqa: F401
    WorldStructure, describe_world, is_nonworld,
)
from terrario.level16.world import (  # noqa: F401
    GRID_SIZE, WALL_PROBABILITY, build_world, motor_stream, shuffle_stream,
    world_stream,
)
