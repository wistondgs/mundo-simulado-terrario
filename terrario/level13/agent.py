"""El Agente de Nivel 1.3 · el Nivel 1.1 intacto, consultado con un token recordado.

Las cuatro fases son operaciones separadas a propósito. Una función monolítica
que las mezclara haría imposible construir la fixture que omite el tick, y esa
fixture es lo único que certifica que la capacidad es **persistencia a través de
un intervalo** y no un registro consultable al instante.

`present` no actúa y no devuelve nada. Si el agente actuara durante la
presentación, el pasado quedaría escrito en el mundo --acción, desplazamiento,
bits de pared alterados-- y la consulta podría resolverse leyendo el presente en
vez de recordando.
"""

from __future__ import annotations

from typing import Any

from terrario.level11.cue import CueToken
from terrario.level11.world import Observation


class Level13Agent:
    """Núcleo 1.1 congelado más un registro de un paso. Nada más."""

    def __init__(self, core: Any, memory: Any, *, name: str = "FULL_13") -> None:
        self._core = core
        self.memory = memory
        self.name = name

    # --- las cuatro fases -----------------------------------------------------

    def present(self, observation: Observation, cue: CueToken) -> None:
        """Escribe. **No actúa, no mueve nada, no devuelve nada.**"""
        self.memory.write(cue)
        return None

    def tick(self) -> None:
        self.memory.tick()

    def query(self, observation: Observation) -> tuple[float, ...]:
        """No recibe cue externo. Lee la memoria sin consumirla."""
        cue = self.memory.peek()
        if cue is None:
            return self._core.body_scores(observation)
        return self._core.joint_scores(observation, cue)

    def reset(self) -> None:
        """La única operación que borra."""
        self.memory.reset()

    # --- lo heredado, para las sondas -------------------------------------------

    def predict_body(self, observation: Observation, action: Any) -> float:
        return self._core.predict_body(observation, action)

    def predict_orientation(self, cue: CueToken, action: Any) -> float:
        return self._core.predict_orientation(cue, action)

    def fingerprint(self) -> str:
        return self._core.fingerprint()

    @property
    def inherited_intact(self) -> bool:
        return self._core.intact


class PresentCueAgent:
    """CONTROL POSITIVO · el cue sigue **externamente presente** en la consulta.

    No es memoria: es el techo. Guarda el cue en un atributo llano para que nadie
    lo confunda con el registro, y su consulta devuelve exactamente lo que el
    Nivel 1.1 devolvería con la señal delante.
    """

    def __init__(self, core: Any, *, name: str = "PRESENT_CUE") -> None:
        self._core = core
        self._external_cue: CueToken | None = None
        self.name = name

    def present(self, observation: Observation, cue: CueToken) -> None:
        self._external_cue = cue
        return None

    def tick(self) -> None:
        return None

    def query(self, observation: Observation) -> tuple[float, ...]:
        if self._external_cue is None:
            return self._core.body_scores(observation)
        return self._core.joint_scores(observation, self._external_cue)

    def reset(self) -> None:
        self._external_cue = None

    def predict_body(self, observation: Observation, action: Any) -> float:
        return self._core.predict_body(observation, action)

    def predict_orientation(self, cue: CueToken, action: Any) -> float:
        return self._core.predict_orientation(cue, action)

    def fingerprint(self) -> str:
        return self._core.fingerprint()

    @property
    def inherited_intact(self) -> bool:
        return self._core.intact
