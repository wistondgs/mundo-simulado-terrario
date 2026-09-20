"""El organismo que recuerda cuál era la referencia y recupera lo suyo.

    J_N(o, ĝ, escena, a) = B(o,a) · Q(ĝ,a) · ĥ(ĝ, escena)

`ĥ` es la creencia de proximidad **de la referencia diana**: la que lleva el cue
que se recordó. Sin `M` no hay diana y `Q` cae a su prior; sin `ψ` hay diana pero
la evidencia se mezcla.

**Operación declarada:** localizar el elemento direccional cuyo cue coincide con
el recordado es una comparación de identidad sobre tokens opacos --la misma que
hace `Q` al indexar su fila--, pero ningún readout anterior la tenía. Se
suministra por diseño, igual que la regla de composición, y **no es atención ni
búsqueda**.
"""

from __future__ import annotations

from typing import Any

from terrario.level11.cue import CueToken
from terrario.level11.world import Direction, Observation
from terrario.level14.scene import BindingObservation, DirectionItem

Q_IGNORANTE = 0.25


class RememberedBindingAgent:
    def __init__(self, organism: Any, memory: Any, *, use_psi: bool = True,
                 name: str = "M+ψ") -> None:
        self._organism = organism
        self.memory = memory
        self.use_psi = use_psi
        self.name = name

    # --- fases ----------------------------------------------------------------

    def present(self, observation: Observation, cue: CueToken) -> None:
        self.memory.write(cue)
        return None

    def tick(self) -> None:
        self.memory.tick()

    def reset(self) -> None:
        self.memory.reset()

    # --- la localización declarada ---------------------------------------------

    def target_item(self, scene: BindingObservation) -> DirectionItem | None:
        """El elemento cuyo cue coincide con el recordado. `None` si no hay."""
        recordado = self.memory.peek()
        if recordado is None:
            return None
        for d in scene.directions:
            if d.cue is recordado:
                return d
        return None

    # --- la consulta conjunta ---------------------------------------------------

    def target_near_belief(self, scene: BindingObservation) -> float:
        """`ĥ`. Sin diana o sin `ψ`, la evidencia se mezcla."""
        diana = self.target_item(scene)
        proximidades = sorted(scene.proximities, key=lambda p: p.carrier.value)
        mezcla = sum(self._organism.predict_near(p.sensor)
                     for p in proximidades) / len(proximidades)
        if diana is None or not self.use_psi:
            return mezcla
        creencia = 0.0
        for asignacion, p in self._organism.bind(scene):
            creencia += p * self._organism.predict_near(asignacion[diana].sensor)
        return creencia

    def joint(self, observation: Observation, scene: BindingObservation,
              action: Direction) -> tuple[float, float]:
        recordado = self.memory.peek()
        q = (Q_IGNORANTE if recordado is None
             else self._organism.predict_orientation(recordado, action))
        base = self._organism.predict_body(observation, action) * q
        h = self.target_near_belief(scene)
        return base * h, base * (1.0 - h)

    def fingerprints(self) -> dict[str, str]:
        return self._organism.fingerprints()

    @property
    def organism(self) -> Any:
        return self._organism


class NoMemory:
    def write(self, cue: CueToken) -> None: return None
    def tick(self) -> None: return None
    def peek(self) -> CueToken | None: return None
    def reset(self) -> None: return None
