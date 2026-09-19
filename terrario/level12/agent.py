"""El Agente de Nivel 1.2 · tres conocimientos, una política que no cambia.

    J_N(o,g,s,a) = B(o,a) · Q(g,a) · H(s)
    J_F(o,g,s,a) = B(o,a) · Q(g,a) · (1 − H(s))

**La política motora sigue siendo la del Nivel 1.1**, literalmente:

    π_1.2(o,g,s) = π_1.1(o,g)

`s` no puede cambiar la acción, y eso **no es una limitación accidental**. Si
CERCA/LEJOS decidiera qué hacer, estaríamos añadiendo a la percepción de
distancia una regla sobre qué conducta le corresponde a cada clase --dos
adquisiciones en un decimal, y ninguna de las dos atribuible.
"""

from __future__ import annotations

from typing import Any

import numpy as np

from terrario.level11.cue import CueToken
from terrario.level11.world import Direction, Observation
from terrario.level12.reference import ProximityToken


class Level12Agent:
    """Núcleo 1.1 congelado más `H`. La única estructura que puede cambiar es `H`."""

    def __init__(self, core: Any, proximity: Any, *, name: str = "FULL_12") -> None:
        self._core = core
        self.proximity = proximity
        self.name = name

    # --- lo heredado, intacto ------------------------------------------------

    def predict_body(self, observation: Observation, action: Direction) -> float:
        return self._core.predict_body(observation, action)

    def predict_orientation(self, cue: CueToken, action: Direction) -> float:
        return self._core.predict_orientation(cue, action)

    def predict(self, observation: Observation, cue: CueToken,
                action: Direction) -> float:
        """`B·Q`. Es la superficie que puntúan las métricas del Nivel 1.1."""
        return self._core.predict(observation, cue, action)

    def act(self, observation: Observation, cue: CueToken,
            rng: np.random.Generator) -> Direction:
        """Delega exactamente. `s` no aparece ni como argumento."""
        return self._core.act(observation, cue, rng)

    def fingerprint(self) -> str:
        return self._core.fingerprint()

    @property
    def inherited_intact(self) -> bool:
        return self._core.intact

    # --- la adquisición nueva -------------------------------------------------

    def predict_near(self, sensor: ProximityToken) -> float:
        return self.proximity.predict_near(sensor)

    def predict_distance(self, view: Any) -> float:
        """Acepta la vista del organismo, que **no tiene** campo de verdad."""
        return self.proximity.predict_near(view.sensor)

    # --- la composición triple ------------------------------------------------

    def predict_joint(self, observation: Observation, cue: CueToken,
                      sensor: ProximityToken,
                      action: Direction) -> tuple[float, float]:
        """`(J_N, J_F)`. Son predicciones, no recompensas: no entran en ninguna
        función de valor y no tocan `act`."""
        base = self._core.predict(observation, cue, action)
        h = self.proximity.predict_near(sensor)
        return base * h, base * (1.0 - h)
