"""La referencia latente del Nivel 1.2 · geometría que el organismo nunca ve.

La referencia **no es una celda del mundo**. Es un desplazamiento relativo
abstracto y axial: no bloquea, no colisiona, no puede tocarse y no altera la
física. Tenía que serlo. El mundo congelado es una rejilla de 7 con el borde
cerrado, luego su interior libre es 5x5, y desde el centro la distancia Manhattan
máxima a otra celda interior es **4**: exigir que la referencia cayera dentro
habría hecho `δ ∈ {5,6}` imposible salvo en la periferia, que es justo donde los
bits de pared valen 1. La clase de distancia habría quedado confundida con la
posición antes de correr nada.

**El sensor emite desde `δ`, no desde la etiqueta.** Si emitiera desde la clase,
la geometría entera sería decorativa: se podría borrar y el experimento daría el
mismo resultado. Promediando `δ` uniformemente dentro de cada clase las
marginales reproducen exactamente las selladas, así que el problema del organismo
no cambia --ve `s`, nunca `δ`-- pero la evidencia sí nace de la distancia.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass

import numpy as np

from terrario.level11.world import DELTA, Direction


class DistanceTruth(enum.Enum):
    """La clasificación del EXPERIMENTADOR. Nunca entra en `predict`."""

    NEAR = "N"
    FAR = "F"


class ProximityToken(enum.IntEnum):
    """Cuatro símbolos opacos. Lo único que el agente recibe del sensor.

    Sin orden semántico: `S3` no es «más» que `S0`. Un aprendiz que presuponga
    la escala falla la fixture de permutación.
    """

    S0 = 0
    S1 = 1
    S2 = 2
    S3 = 3


ALL_TOKENS: tuple[ProximityToken, ...] = tuple(ProximityToken)

#: `δ = 0` y `δ = 3` no se generan nunca. El margen se evita, no se filtra.
DELTA_NEAR: tuple[int, ...] = (1, 2)
DELTA_FAR: tuple[int, ...] = (4, 5, 6)

#: `P(s | δ)`. Oculta al agente y a todo lo que el agente toca.
EMISSION: dict[int, tuple[float, float, float, float]] = {
    1: (0.02, 0.08, 0.30, 0.60),
    2: (0.08, 0.22, 0.30, 0.40),
    4: (0.43, 0.28, 0.20, 0.09),
    5: (0.50, 0.30, 0.15, 0.05),
    6: (0.57, 0.32, 0.10, 0.01),
}

#: Selladas en `docs/LEVEL12_ORACULO_PREREGISTRADO.md` antes de existir el código.
SEALED_MARGINAL = {
    DistanceTruth.NEAR: (0.05, 0.15, 0.30, 0.50),
    DistanceTruth.FAR: (0.50, 0.30, 0.15, 0.05),
}


def deltas_of(truth: DistanceTruth) -> tuple[int, ...]:
    return DELTA_NEAR if truth is DistanceTruth.NEAR else DELTA_FAR


def class_of(delta: int) -> DistanceTruth:
    if delta in DELTA_NEAR:
        return DistanceTruth.NEAR
    if delta in DELTA_FAR:
        return DistanceTruth.FAR
    raise ValueError(f"δ={delta} no pertenece a ninguna clase; no debió generarse")


def marginal(truth: DistanceTruth) -> tuple[float, float, float, float]:
    """`P(s | clase)` promediando `δ` uniforme dentro de la clase."""
    ds = deltas_of(truth)
    return tuple(sum(EMISSION[d][k] for d in ds) / len(ds) for k in range(4))  # type: ignore[return-value]


@dataclass(frozen=True)
class Reference:
    """Sólo desplazamiento. No se guarda posición absoluta de nada.

    Que la referencia sea el offset y no un punto hace **estructuralmente
    imposible** derivar `p_t` de ella.
    """

    offset: tuple[int, int]
    direction: Direction
    delta: int
    truth: DistanceTruth


def build_reference(direction: Direction, delta: int) -> Reference:
    step = DELTA[direction]
    return Reference((step[0] * delta, step[1] * delta), direction, delta,
                     class_of(delta))


class ProximitySensor:
    """Emite desde `δ`. Sólo el mundo experimental lo construye."""

    def emit(self, delta: int, rng: np.random.Generator) -> ProximityToken:
        return ProximityToken(int(rng.choice(4, p=EMISSION[delta])))

    def emit_class_blind(self, delta: int,
                         rng: np.random.Generator) -> ProximityToken:
        """Fixture negativa de L12-11: ignora `δ` y emite desde la marginal.

        Es el generador que la enmienda prohíbe. Existe para que el contrato que
        exige dependencia de `δ` pueda fallar.
        """
        return ProximityToken(int(rng.choice(4, p=marginal(class_of(delta)))))


def _verify_sealed() -> None:
    """El preregistro es el contrato; el módulo no puede contradecirlo."""
    for d, row in EMISSION.items():
        if abs(sum(row) - 1.0) > 1e-12:
            raise ValueError(f"la fila δ={d} no suma 1: {sum(row)}")
        if len(row) != 4:
            raise ValueError(f"la fila δ={d} no tiene cuatro entradas")
    for truth, sellada in SEALED_MARGINAL.items():
        obtenida = marginal(truth)
        if max(abs(a - b) for a, b in zip(obtenida, sellada)) > 1e-12:
            raise ValueError(
                f"la marginal de {truth} cambió respecto del preregistro: "
                f"{obtenida} != {sellada}")


_verify_sealed()
