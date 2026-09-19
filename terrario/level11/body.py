"""El cuerpo del Nivel 1.0, de sólo lectura.

`FactoredContingency` tiene un flag `frozen`, y confiar en él bastaría si nadie
se equivocara nunca. Este envoltorio no expone `observe`: **el método que no
existe no se puede llamar por descuido**, y eso es lo único que garantiza que la
única adquisición de 1.1 sea la direccional.

Si la huella del cuerpo cambia durante la adquisición 1.1, el experimento pierde
su propiedad central --saber exactamente qué adquisición produjo cualquier
cambio-- y el resultado es `BODY_MODEL_MUTATED`.
"""

from __future__ import annotations

import hashlib
from typing import Any, Protocol

from terrario.level11.world import Direction, Observation


class BodyModel(Protocol):
    """Lo único que 1.1 necesita del cuerpo. No depende de qué lo implemente."""

    def predict(self, observation: Observation, action: Direction) -> float: ...


class FrozenFactoredBody:
    """Envuelve un cuerpo ya entrenado y expone `predict` y nada más."""

    def __init__(self, trained: Any) -> None:
        self._inner = trained
        self._birth_digest = self.digest()

    def predict(self, observation: Observation, action: Direction) -> float:
        return self._inner.predict(observation, action)

    def digest(self) -> str:
        """Huella de los suficientes estadísticos del cuerpo."""
        h = hashlib.sha256()
        for name in ("_belief", "_base", "_feature"):
            store = getattr(self._inner, name, None)
            if store is None:
                continue
            h.update(name.encode())
            for key in sorted(store, key=repr):
                h.update(repr(key).encode())
                h.update(repr(store[key]).encode())
        return h.hexdigest()

    @property
    def intact(self) -> bool:
        return self.digest() == self._birth_digest


class IdealBody:
    """`B(o,a) = 1 − o[a]`. El cuerpo perfecto, para el oráculo analítico."""

    def predict(self, observation: Observation, action: Direction) -> float:
        return 1.0 - observation[int(action)]

    def digest(self) -> str:
        return "ideal"

    @property
    def intact(self) -> bool:
        return True


class BlindBody:
    """`B ≡ 1`. Usado por CUE-ONLY: cree que todo movimiento es realizable."""

    def predict(self, observation: Observation, action: Direction) -> float:
        return 1.0

    def digest(self) -> str:
        return "blind"

    @property
    def intact(self) -> bool:
        return True
