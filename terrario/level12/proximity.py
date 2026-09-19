"""La única adquisición nueva del Nivel 1.2 · `H(s) = P(CERCA | s)`.

Cuatro acumuladores Beta-Bernoulli, uno por token, con el mismo prior que el
cuerpo y que la orientación. Nada más.

**La firma está cerrada a cuatro entradas.** `observe` no acepta observación,
señal, acción, coordenadas ni `δ`: la separación entre adquisiciones deja de
depender de la disciplina de quien llama. Y los acumuladores son arrays de tamaño
fijo, no un diccionario, así que **`predict` no puede insertar la celda que
lee** --el defecto que en el Nivel 1.0 contaminó toda huella de estado deja de
ser expresable.

El techo de esta adquisición **no es cero**. El sensor es ambiguo por diseño y el
mejor predictor posible se queda en `8/55`. Es lo genuinamente nuevo frente a
1.0 y 1.1, donde la respuesta perfecta existía.
"""

from __future__ import annotations

import hashlib
from fractions import Fraction

import numpy as np

from terrario.level12.reference import (
    ALL_TOKENS, DistanceTruth, ProximityToken, marginal,
)


class QualitativeDistanceModel:
    """`H(s) = α_s / (α_s + β_s)`. Cuatro parámetros, nada indexado por contexto."""

    def __init__(self, *, prior_alpha: float = 1.0, prior_beta: float = 1.0,
                 frozen: bool = False) -> None:
        self.prior_alpha = prior_alpha
        self.prior_beta = prior_beta
        self.frozen = frozen
        self._alpha = np.full(4, prior_alpha, dtype=float)
        self._beta = np.full(4, prior_beta, dtype=float)

    def predict_near(self, sensor: ProximityToken) -> float:
        k = int(sensor)
        return float(self._alpha[k] / (self._alpha[k] + self._beta[k]))

    def observe(self, sensor: ProximityToken, target: DistanceTruth) -> bool:
        """`target` es señal de aprendizaje, no recompensa: no tiene valor y no
        entra en ninguna política. Llega DESPUÉS de producida la observación."""
        if self.frozen:
            return False
        k = int(sensor)
        if target is DistanceTruth.NEAR:
            self._alpha[k] += 1
        else:
            self._beta[k] += 1
        return True

    def coverage(self) -> dict[tuple[DistanceTruth, ProximityToken], int]:
        return {
            **{(DistanceTruth.NEAR, s): int(self._alpha[int(s)] - self.prior_alpha)
               for s in ALL_TOKENS},
            **{(DistanceTruth.FAR, s): int(self._beta[int(s)] - self.prior_beta)
               for s in ALL_TOKENS},
        }

    @property
    def informative_minimum(self) -> int:
        return min(self.coverage().values())

    def posteriors(self) -> tuple[float, ...]:
        return tuple(self.predict_near(s) for s in ALL_TOKENS)

    def digest(self) -> str:
        h = hashlib.sha256()
        for arr in (self._alpha, self._beta):
            h.update(np.asarray(arr, dtype=float).tobytes())
        return h.hexdigest()


class ConstantDistance:
    """`H ≡ c`. Con `0.5` es NO_DISTANCE: exactamente el agente 1.1."""

    def __init__(self, value: float = 0.5) -> None:
        self.value = value
        self.frozen = True

    def predict_near(self, sensor: ProximityToken) -> float:
        return self.value

    def posteriors(self) -> tuple[float, ...]:
        return tuple(self.value for _ in ALL_TOKENS)

    def digest(self) -> str:
        return f"constante:{self.value!r}"


class BayesDistanceOracle:
    """`H*(s)` desde la matriz de emisión. **No aprende y no ve la verdad.**

    Usar el `D*` real como oráculo de predicción daría Brier cero y excedería la
    información accesible al organismo: el techo correcto es éste.
    """

    def __init__(self) -> None:
        n = [Fraction(x).limit_denominator(10_000)
             for x in marginal(DistanceTruth.NEAR)]
        f = [Fraction(x).limit_denominator(10_000)
             for x in marginal(DistanceTruth.FAR)]
        self.exact = tuple(n[k] / (n[k] + f[k]) for k in range(4))
        self.frozen = True

    def predict_near(self, sensor: ProximityToken) -> float:
        return float(self.exact[int(sensor)])

    def posteriors(self) -> tuple[float, ...]:
        return tuple(self.predict_near(s) for s in ALL_TOKENS)

    def digest(self) -> str:
        return "oraculo-bayes"


class OrdinalPrior(QualitativeDistanceModel):
    """Fixture negativa de L12-4: presupone que el token trae escala.

    Nace creyendo `H(S_k) = k/3` en vez de `1/2`. Con la semántica permutada su
    creencia inicial apunta al token equivocado. Existe para que el contrato de
    invariancia al nombre pueda fallar.
    """

    def __init__(self, *, strength: float = 400.0) -> None:
        super().__init__()
        for k in range(4):
            p = k / 3
            self._alpha[k] = 1.0 + strength * p
            self._beta[k] = 1.0 + strength * (1 - p)
