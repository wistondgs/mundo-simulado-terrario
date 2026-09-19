"""El organismo fusionado · las cuatro capacidades en una misma consulta.

    J_N(o, ĝ, s, a) = B(o,a) · Q(ĝ,a) · H(s)
    J_F(o, ĝ, s, a) = B(o,a) · Q(ĝ,a) · [1 − H(s)]

«este comando es físicamente realizable, corresponde a la dirección que vi hace
un tick, y va con una referencia probablemente cercana».

Cuando una capacidad se apaga, su factor toma **su prior ignorante**, no una
constante arbitraria: sin proximidad adquirida, `P(CERCA) = ½` --que es el
`NO_DISTANCE` sellado del 1.2--; sin cue recordado, `P(alineada) = ¼`, una
dirección entre cuatro. Así los cuatro brazos siguen siendo probabilidades.

**La política motora no cambia.** El Nivel 1.2 dejó cerrado que la distancia no
modifica la acción; esta prueba es predictiva y no conductual.
"""

from __future__ import annotations

from typing import Any

from terrario.level11.cue import CueToken
from terrario.level11.world import Direction, Observation
from terrario.level12.reference import ProximityToken

#: Priors ignorantes de cada factor apagado.
Q_IGNORANTE = 0.25
H_IGNORANTE = 0.5


class FusedAgent:
    """Un solo `FrozenOrganism` y un registro de un tick. Nada más."""

    def __init__(self, organism: Any, memory: Any, *, use_h: bool = True,
                 use_m: bool = True, name: str = "H+M") -> None:
        self._organism = organism
        self.memory = memory
        self.use_h = use_h
        self.use_m = use_m
        self.name = name

    # --- las fases del ensayo -------------------------------------------------

    def present(self, observation: Observation, cue: CueToken) -> None:
        self.memory.write(cue)
        return None

    def tick(self) -> None:
        self.memory.tick()

    def reset(self) -> None:
        self.memory.reset()

    # --- los factores ---------------------------------------------------------

    def _q(self, action: Direction) -> float:
        if not self.use_m:
            return Q_IGNORANTE
        cue = self.memory.peek()
        return Q_IGNORANTE if cue is None else self._organism.predict_orientation(
            cue, action)

    def _h(self, sensor: ProximityToken) -> float:
        return (self._organism.predict_near(sensor) if self.use_h
                else H_IGNORANTE)

    # --- la consulta conjunta --------------------------------------------------

    def joint(self, observation: Observation, sensor: ProximityToken,
              action: Direction) -> tuple[float, float]:
        base = self._organism.predict_body(observation, action) * self._q(action)
        h = self._h(sensor)
        return base * h, base * (1.0 - h)

    def query(self, observation: Observation,
              sensor: ProximityToken) -> tuple[tuple[float, float], ...]:
        return tuple(self.joint(observation, sensor, a) for a in Direction)

    # --- superficie heredada, para preservación motora ---------------------------

    def predict(self, observation: Observation, cue: CueToken,
                action: Direction) -> float:
        return self._organism.predict(observation, cue, action)

    def fingerprints(self) -> dict[str, str]:
        return self._organism.fingerprints()

    @property
    def organism(self) -> Any:
        """Para comprobar por IDENTIDAD que hay un solo núcleo."""
        return self._organism


class NoMemory:
    """Sin persistencia: `peek` no devuelve nunca nada."""

    def write(self, cue: CueToken) -> None:
        return None

    def tick(self) -> None:
        return None

    def peek(self) -> CueToken | None:
        return None

    def reset(self) -> None:
        return None
