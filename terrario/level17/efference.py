"""La copia eferente · el comando, y sólo el comando, antes de la consecuencia.

El canal nuevo de 1.7. Tres exigencias, y las tres son sobre lo que **no** lleva:

* es el **comando emitido**, no la acción ejecutada. Si `A_0` contra una pared no
  desplaza al cuerpo, la copia sigue diciendo `A_0` y nunca «`A_0` que falló».
* se genera **antes** de conocer `O_{t+1}`. Construirla después permitiría que
  codificara consecuencia.
* el token es **opaco**. El aprendiz recibe `A_0…A_3` y nunca `UP/DOWN/LEFT/RIGHT`:
  la correspondencia con los actuadores físicos es una biyección por semilla que
  el aprendiz no ve. Si el contenido estuviera escondido en la semántica del
  token, permutar la biyección no costaría nada y el nivel no demostraría
  adquisición.

Nada en la copia puede codificar movimiento, éxito, colisión, dirección
desplazada ni consecuencia. Lo contrario sería entregar parte del resultado junto
con la acción.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass


#: Alias declarado aquí, en la frontera del aprendiz, y no importado de la
#: física: así `contingency.py` no importa NADA de `terrario.level1.world` y la
#: opacidad del token deja de ser una promesa para ser estructura.
Observation = tuple[int, int, int, int]


class EfferenceContractError(RuntimeError):
    """Se ofreció como copia eferente algo que no es un comando opaco."""


class CommandToken(enum.Enum):
    """Los cuatro comandos, sin semántica direccional.

    `Enum` y no `IntEnum`: un token no debe poder compararse ni sumarse con un
    índice de dirección por accidente.
    """

    A0 = "A0"
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"


#: Orden canónico. Es el índice de la tabla, no una dirección.
ALL_COMMANDS: tuple[CommandToken, ...] = tuple(CommandToken)

COMMAND_INDEX: dict[CommandToken, int] = {
    command: index for index, command in enumerate(ALL_COMMANDS)
}


@dataclass(frozen=True)
class EfferenceCopy:
    """El comando emitido. Un campo, y ninguno más.

    Que la clase tenga exactamente un atributo es el contrato: no hay dónde
    escribir `moved`, `succeeded` ni `displacement` sin cambiar el tipo.
    """

    command: CommandToken

    def __post_init__(self) -> None:
        if not isinstance(self.command, CommandToken):
            raise EfferenceContractError(
                "la copia eferente lleva un comando opaco; llegó "
                f"{type(self.command).__name__}. No es una dirección, ni un "
                "índice, ni un resultado.")

    @property
    def index(self) -> int:
        return COMMAND_INDEX[self.command]
