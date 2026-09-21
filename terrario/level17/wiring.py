"""El cableado del actuador · la biyección que el aprendiz no ve.

`φ : CommandToken -> Direction`, sorteada por semilla. El organismo emite
comandos opacos; el cuerpo los convierte en desplazamientos físicos. El aprendiz
está del lado del comando y nunca ve `φ`.

De aquí sale el control de generalidad más fuerte del nivel: el **mismo** código
del aprendiz debe adquirir las veinticuatro correspondencias posibles. Si sólo
funcionara con la identidad, el contenido estaría escondido en la semántica del
token y no habría sido adquirido.

El flujo `[semilla, 64]` no colisiona con los de 1.6 --mundo `0`, motor `1`,
baraja `2`, nulas `3..10`-- y por tanto **cablear no altera ninguna trayectoria**
de la fase predecesora.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from terrario.level1.world import Direction
from terrario.level17.efference import ALL_COMMANDS, CommandToken

#: Índice de flujo propio de 1.7. Ver módulo `terrario.level16.world`.
_WIRING = 64


def wiring_stream(seed: int) -> np.random.Generator:
    """Flujo del cableado. Disjunto de todos los de 1.6."""
    return np.random.default_rng([seed, _WIRING])


@dataclass(frozen=True)
class ActuatorWiring:
    """Una de las veinticuatro biyecciones comando → dirección."""

    mapping: tuple[Direction, ...]

    @classmethod
    def sampled(cls, seed: int) -> ActuatorWiring:
        orden = wiring_stream(seed).permutation(4)
        return cls(tuple(Direction(int(i)) for i in orden))

    @classmethod
    def identity(cls) -> ActuatorWiring:
        return cls(tuple(Direction(i) for i in range(4)))

    def actuate(self, command: CommandToken) -> Direction:
        """Lo que el cuerpo hace con el comando. El aprendiz no llama a esto."""
        return self.mapping[ALL_COMMANDS.index(command)]

    def command_for(self, direction: Direction) -> CommandToken:
        """Inversa. Sólo para instrumentación; nunca en la vía del aprendiz."""
        return ALL_COMMANDS[self.mapping.index(direction)]
