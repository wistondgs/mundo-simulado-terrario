"""S0 · la fuente motora endógena.

Es sustrato suministrado, no adquisición: el organismo nace con un generador
que produce sus actos y no aprende nada sobre ellos durante 1.6. Lo que importa
científicamente no es su sofisticación --es uniforme a propósito-- sino de quién
es. Tres propiedades lo definen:

* el generador **pertenece al organismo**: no hay cinta de acciones, ni maestro,
  ni currículo, ni nada fuera del cuerpo que decida qué se hace;
* su estado **forma parte de la serialización** del ser, de modo que dos seres
  con el mismo estado tienen el mismo futuro, incluidos los actos estocásticos;
* lleva la cuenta de lo emitido, para que la procedencia de cada acto sea
  verificable contra el número de pasos vividos en vez de asumida.

La copia eferente existe en el cuerpo --`last_action`-- porque el cuerpo la
tiene; lo que el contrato prohíbe es que el aprendiz la lea. Sin esa frontera
A1 derivaría hacia `P(o'|o,a)`, que ya es contingencia propia y pertenece a 1.7.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from terrario.level1.world import Direction


class MotorContractError(RuntimeError):
    """Se intentó producir un acto por una vía que no es la fuente del ser."""


class EndogenousMotor:
    """El generador de actos del organismo, con su propio azar."""

    def __init__(self, rng: np.random.Generator) -> None:
        if not isinstance(rng, np.random.Generator):
            raise MotorContractError(
                "la fuente motora exige un Generator propio; se recibió "
                f"{type(rng).__name__}"
            )
        self._rng = rng
        self._emitted = 0

    @property
    def emitted(self) -> int:
        """Cuántos actos ha producido. Es la prueba de procedencia."""
        return self._emitted

    def next(self) -> Direction:
        """Un acto. Uniforme sobre las cuatro direcciones."""
        self._emitted += 1
        return Direction(int(self._rng.integers(4)))

    # --- serialización ------------------------------------------------------

    def state(self) -> dict[str, Any]:
        """El estado completo: el del generador y la cuenta de emisiones."""
        return {"rng": self._rng.bit_generator.state, "emitted": self._emitted}

    def restore(self, state: dict[str, Any]) -> None:
        """Devolver al ser al estado exacto del que salió esa fotografía."""
        if set(state) != {"rng", "emitted"}:
            raise MotorContractError(
                "una fotografía de la fuente motora sin el estado del generador "
                "no reproduce la vida; claves recibidas: " + repr(sorted(state))
            )
        self._rng.bit_generator.state = state["rng"]
        self._emitted = int(state["emitted"])
