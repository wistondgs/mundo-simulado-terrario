"""A1 · la única adquisición de 1.6.

Una tabla asociativa temporal de 16 x 16 y una sola operación plástica: ver dos
observaciones consecutivas y sumar uno donde corresponde. Todo el contenido
--qué sigue a qué en este mundo-- aparece por experiencia; lo suministrado es la
capacidad de asociar en el tiempo, el prior y la regla de actualización.

No hay generalización entre observaciones, y es deliberado: con 256 celdas
independientes, cualquier competencia medida procede de haber vivido las
transiciones, no de una estructura que se las regale.

La frontera está en la firma. `observe` acepta dos observaciones y nada más: un
acto, un bit de cambio o una posición no son tuplas de cuatro bits y la tabla los
rechaza. Sin esa frontera A1 derivaría hacia `P(o'|o,a)`, que es contingencia
propia y pertenece a 1.7.
"""

from __future__ import annotations

import hashlib

import numpy as np

from terrario.level1.world import ALL_OBSERVATIONS, Observation

#: Índice canónico de cada observación. Fijo: la tabla no puede crecer.
OBSERVATION_INDEX: dict[Observation, int] = {
    observation: index for index, observation in enumerate(ALL_OBSERVATIONS)
}

#: Prior simétrico. `alpha_0 = 1` hace que el ser sin experiencia prediga
#: uniforme, y por tanto que la pérdida del brazo FROZEN valga exactamente
#: `log 16 = 2.7726`, que es el valor analítico que el oráculo ya traía.
PRIOR = 1.0


class TemporalContractError(RuntimeError):
    """Se le ofreció a la tabla algo que no es una observación."""


def _checked(candidate: object, role: str) -> int:
    """La aduana. Devuelve el índice, o explica por qué eso no entra."""
    if not isinstance(candidate, tuple) or len(candidate) != 4:
        raise TemporalContractError(
            f"{role} debe ser una observación de cuatro bits; llegó "
            f"{type(candidate).__name__}. A1 no recibe actos, copia eferente, "
            "posición ni etiquetas de cambio."
        )
    if any(bit not in (0, 1) for bit in candidate):
        raise TemporalContractError(
            f"{role} tiene componentes que no son bits: {candidate!r}")
    index = OBSERVATION_INDEX.get(candidate)  # type: ignore[arg-type]
    if index is None:
        raise TemporalContractError(
            f"{role} no pertenece al espacio sensorial: {candidate!r}")
    return index


class TemporalModel:
    """`P(o_{t+1} | o_t)` contada, no entrenada."""

    def __init__(self, prior: float = PRIOR) -> None:
        if prior <= 0:
            raise TemporalContractError(
                f"el prior debe ser positivo para que la predicción esté definida; se pidió {prior}")
        self._prior = float(prior)
        self._counts = np.full((16, 16), float(prior))
        self._updates = 0
        self._frozen = False

    # --- la única operación plástica ----------------------------------------

    def observe(self, previous: Observation, following: Observation) -> None:
        """Dos observaciones consecutivas. Es todo lo que el aprendiz ve."""
        if self._frozen:
            raise TemporalContractError(
                "la tabla está congelada; actualizarla después del freeze "
                "rompe la separación entre adquisición y evaluación")
        self._counts[_checked(previous, "la observación anterior"),
                     _checked(following, "la observación siguiente")] += 1.0
        self._updates += 1

    # --- lectura ------------------------------------------------------------

    def predict(self, previous: Observation) -> np.ndarray:
        """Las dieciséis probabilidades de lo que viene. Nunca inserta nada."""
        fila = self._counts[_checked(previous, "la observación anterior")]
        return fila / fila.sum()

    def probability(self, previous: Observation, following: Observation) -> float:
        return float(self.predict(previous)[_checked(following, "la observación siguiente")])

    def change_probability(self, previous: Observation) -> float:
        """`q(o) = 1 - P(o|o)`. Métrica **secundaria** del oráculo §7."""
        index = _checked(previous, "la observación anterior")
        return float(1.0 - self.predict(previous)[index])

    # --- estado -------------------------------------------------------------

    @property
    def updates(self) -> int:
        """Cuántas veces se actualizó. Distingue `no aprendió` de `no corrió`."""
        return self._updates

    @property
    def frozen(self) -> bool:
        return self._frozen

    def freeze(self) -> None:
        self._frozen = True

    def fingerprint(self) -> str:
        """Huella del estado aprendido. Prueba que el congelado no se movió."""
        return hashlib.sha256(np.ascontiguousarray(self._counts).tobytes()).hexdigest()

    def snapshot(self) -> np.ndarray:
        """Copia del estado, para la intervención causal `M_T -> M_0 -> M_T`."""
        return self._counts.copy()

    def load(self, counts: np.ndarray) -> None:
        """Sustituir el estado aprendido sin tocar nada más del organismo."""
        if counts.shape != (16, 16):
            raise TemporalContractError(
                f"el estado de A1 es una tabla 16x16; llegó {counts.shape}")
        self._counts = counts.copy()

    @classmethod
    def naive(cls, prior: float = PRIOR) -> TemporalModel:
        """El ser sin experiencia: `M_0`. Predice uniforme."""
        return cls(prior=prior)
