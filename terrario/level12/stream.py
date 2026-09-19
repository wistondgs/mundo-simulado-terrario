"""La experiencia del Nivel 1.2 · la clase se decide antes de mirar el mundo.

**`D` nunca se elige a partir de `o` ni de `g`.** El par `(D,G)` sale de una
lista factorial exacta --256 instancias de cada una de las ocho combinaciones--
barajada antes de empezar. Si la clase se decidiera mirando la rejilla, la
geometría local predeciría la distancia y el gate correspondiente estaría
midiendo un defecto del generador.

**`g` no se sortea aparte: `g = φ⁻¹(G)`.** El cue SIGNIFICA la dirección en la
que está la referencia. Sortearlo con su propio azar habría roto el significado
que el Nivel 1.1 le dio: el cue apunta a la referencia, el sensor dice a qué
distancia está, y los dos canales describen el mismo objeto externo.

**Dos tipos, no un campo opcional.** El organismo recibe `DistanceObservation`,
que no tiene dónde guardar la verdad. `DistanceTrainingRecord` la guarda aparte.
La fuga deja de ser cuestión de disciplina y pasa a ser un `AttributeError`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from terrario.level11.cue import CueSemantics, CueToken
from terrario.level11.world import Direction, Grid, Observation
from terrario.level12.inherited import cue_for
from terrario.level12.reference import (
    ALL_TOKENS, DistanceTruth, ProximitySensor, ProximityToken, Reference,
    build_reference, deltas_of,
)

#: Congelado en el preregistro.
N_DISTANCE = 2048
MIN_INFORMATIVE = 30


@dataclass(frozen=True)
class DistanceObservation:
    """Lo ÚNICO que llega a `predict`. No hay campo donde esconder la verdad."""

    observation: Observation
    cue: CueToken
    sensor: ProximityToken


@dataclass(frozen=True)
class DistanceTrainingRecord:
    """Registro del experimento. El agente nunca lo recibe."""

    view: DistanceObservation
    truth: DistanceTruth
    reference: Reference


@dataclass
class DistanceStream:
    records: list[DistanceTrainingRecord]
    physics_violations: int

    def coverage(self) -> dict[tuple[DistanceTruth, ProximityToken], int]:
        conteo = {(t, s): 0 for t in DistanceTruth for s in ALL_TOKENS}
        for r in self.records:
            conteo[(r.truth, r.view.sensor)] += 1
        return conteo

    @property
    def informative_minimum(self) -> int:
        return min(self.coverage().values())

    def views(self) -> list[DistanceObservation]:
        return [r.view for r in self.records]


def factorial_pairs(n: int) -> list[tuple[DistanceTruth, Direction]]:
    """`n/8` instancias exactas de cada `(D,G)`. Balance por construcción."""
    if n % 8:
        raise ValueError(f"{n} no es divisible entre las ocho combinaciones (D,G)")
    por_celda = n // 8
    return [(t, g) for t in DistanceTruth for g in Direction
            for _ in range(por_celda)]


def build_stream(seed: int, semantics: CueSemantics, *, n: int = N_DISTANCE,
                 confound: str | None = None, delta_blind: bool = False,
                 grid_size: int = 7, wall_probability: float = 0.25,
                 steps_per_layout: int = 64) -> DistanceStream:
    """El generador aprobado. `confound` y `delta_blind` construyen las fixtures
    negativas: sin ellas los gates de independencia no podrían fallar nunca."""
    rng_pairing = np.random.default_rng([seed, 21])
    rng_reference = np.random.default_rng([seed, 22])
    rng_sensor = np.random.default_rng([seed, 23])
    rng_world = np.random.default_rng([seed, 26])

    pares = factorial_pairs(n)
    orden = rng_pairing.permutation(len(pares))
    pares = [pares[i] for i in orden]

    sensor = ProximitySensor()
    emit = sensor.emit_class_blind if delta_blind else sensor.emit

    registros: list[DistanceTrainingRecord] = []
    violaciones = 0
    grid: Grid | None = None
    paso = 0

    while len(registros) < n:
        grid = Grid.random(grid_size, wall_probability, rng_world)
        for _ in range(steps_per_layout):
            if len(registros) >= n:
                break
            observation = grid.observe()
            truth, direction = pares[len(registros)]

            if confound == "direction":
                # FIXTURE NEGATIVA: la clase la decide la dirección.
                truth = (DistanceTruth.NEAR if direction in (Direction.UP, Direction.DOWN)
                         else DistanceTruth.FAR)
            elif confound == "body":
                # FIXTURE NEGATIVA: la clase la decide la geometría local.
                truth = (DistanceTruth.FAR if sum(observation) >= 2
                         else DistanceTruth.NEAR)

            opciones = deltas_of(truth)
            delta = int(opciones[int(rng_reference.integers(len(opciones)))])
            reference = build_reference(direction, delta)
            cue = cue_for(semantics, direction)
            token = emit(delta, rng_sensor)

            registros.append(DistanceTrainingRecord(
                DistanceObservation(observation, cue, token), truth, reference))

            action = Direction(int(rng_world.integers(len(Direction))))
            antes = grid.position
            moved, _ = grid.step(action)
            if moved != (1 - observation[int(action)]):
                violaciones += 1
            paso += 1

    return DistanceStream(registros, violaciones)


def train_distance(stream: DistanceStream, model, *,
                   shuffle_rng: np.random.Generator | None = None) -> None:
    """Con `shuffle_rng` el aprendiz ve el sensor de OTRO ensayo mientras la
    verdad sigue siendo la del suyo.

    **No se baraja sensor y significado juntos.** Ése fue exactamente el defecto
    del control negativo del Nivel 1.1: un reetiquetado consistente conserva toda
    la información y el control acaba empatando con el brazo que controla.
    """
    vistos = [r.view.sensor for r in stream.records]
    if shuffle_rng is not None:
        idx = shuffle_rng.permutation(len(vistos))
        vistos = [vistos[i] for i in idx]
    for r, sensor_visto in zip(stream.records, vistos, strict=True):
        model.observe(sensor_visto, r.truth)
