"""Lo que hay que medir además de quién acierta más.

Dos mecanismos que terminan con el mismo Brier no son el mismo resultado si uno
llegó con treinta experiencias y el otro con ocho mil, o si uno guarda sesenta y
cuatro números y el otro ocho mil ejemplares. Este módulo añade las medidas que
convierten «quién gana» en «qué compra cada uno y a qué precio».

Nada de aquí cambia el aprendizaje ni la trayectoria: todo son lecturas pasivas
sobre modelos ya entrenados, o reentrenamientos desde cero sobre PREFIJOS del
mismo flujo compartido. Un modelo nunca ve una experiencia distinta de las que
vería en la campaña completa; sólo ve menos.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Sequence

from terrario.level1.measurement import Predictor
from terrario.level1.world import Direction, Observation, Transition, physics_contract

#: Un par sensorimotor: lo que se vio y lo que se intentó.
Pair = tuple[Observation, Direction]


# --- qué patrones vio de verdad ----------------------------------------------

def seen_pairs(stream: Sequence[Transition]) -> frozenset[Pair]:
    """Los `(o, a)` que el flujo de entrenamiento contiene realmente.

    Se deriva del flujo entregado al modelo y no de la configuración, porque lo
    que importa es lo que el ser vio, no lo que el experimento pensaba retirar.
    """
    return frozenset((tr.observation, tr.direction) for tr in stream)


@dataclass(frozen=True)
class Generalisation:
    """Las dos condiciones del §17, que no son la misma pregunta.

    `known_pattern` (G-A): el mundo es otro pero el par `(o, a)` ya apareció.
    Mide independencia de coordenadas y de disposición, no extrapolación: un
    modelo que sólo memoriza puede aprobarla entera.

    `novel_pattern` (G-B): el par no apareció nunca. Aquí sí se separan los
    sesgos inductivos, y es donde una tabla devuelve su prior mientras un
    mecanismo que puntúa por parecido o por rasgos puede decir algo.

    Informarlas juntas ocultaría exactamente la diferencia que buscamos, así que
    van separadas y con su recuento al lado: una media sobre cero casos no es
    un cero, es la ausencia de medida.
    """

    known_pattern: float
    known_count: int
    novel_pattern: float
    novel_count: int


def brier_by_pattern(model: Predictor, bank: Sequence[Observation],
                     seen: frozenset[Pair]) -> Generalisation:
    """Brier partido según el par `(o, a)` haya sido visto o no en adquisición.

    Contrafactual como el Brier del banco: se evalúan las cuatro direcciones sin
    ejecutarlas, contra lo que la física produciría.
    """
    sums, counts = [0.0, 0.0], [0, 0]
    for observation in bank:
        for direction in Direction:
            bucket = 0 if (observation, direction) in seen else 1
            actual = physics_contract(observation, direction)
            sums[bucket] += (model.predict(observation, direction) - actual) ** 2
            counts[bucket] += 1
    return Generalisation(
        known_pattern=sums[0] / counts[0] if counts[0] else float("nan"),
        known_count=counts[0],
        novel_pattern=sums[1] / counts[1] if counts[1] else float("nan"),
        novel_count=counts[1],
    )


# --- cuánto tarda cada uno en saber -------------------------------------------

#: Potencias de dos. La resolución que importa está al principio: la diferencia
#: entre saber con 8 experiencias y con 64 es la pregunta, y entre 4096 y 8192
#: casi nunca lo es.
def checkpoints(total: int) -> tuple[int, ...]:
    """`0, 1, 2, 4, ... , total`, sin pasarse del horizonte real.

    Incluye `0` porque el estado sin experiencia es un dato --ambos mecanismos
    deben dar exactamente `0.25` ahí-- y `total` porque el final de la curva
    tiene que coincidir con la campaña completa o la curva mide otra cosa.
    """
    if total < 0:
        raise ValueError(f"el horizonte no puede ser negativo; se pidió {total}")
    marks, n = [0], 1
    while n < total:
        marks.append(n)
        n *= 2
    if total > 0:
        marks.append(total)
    return tuple(marks)


def learning_curve(build: Callable[[], object], stream: Sequence[Transition],
                   bank: Sequence[Observation],
                   marks: Sequence[int]) -> tuple[tuple[int, float], ...]:
    """`BS(n)` para un mecanismo, reentrenado desde cero sobre cada prefijo.

    Desde cero y no por instantáneas incrementales: un modelo que guarda
    ejemplares y otro que guarda conteos no tienen el mismo concepto de
    «instantánea», y copiar estado sería introducir una diferencia de
    implementación en mitad de la medida. Reentrenar sobre el prefijo da
    exactamente lo mismo que habría dado el modelo en ese punto, para los dos,
    porque ambos son incrementales y sin azar en la actualización.
    """
    from terrario.level1.measurement import brier

    curve = []
    for n in marks:
        model = build()
        for tr in stream[:n]:
            model.observe(tr.observation, tr.direction, tr.moved)  # type: ignore[attr-defined]
        curve.append((n, brier(model, bank)[0]))  # type: ignore[arg-type]
    return tuple(curve)


#: Lo que se informa cuando un mecanismo no alcanza el criterio dentro del
#: horizonte medido. No se extrapola: una curva que no cruzó el umbral no dice
#: dónde lo habría cruzado.
NOT_REACHED = "NOT_REACHED"


def n_star(curve: Sequence[tuple[int, float]], tau: float) -> int | str:
    """La primera cantidad de experiencia con `BS(n) <= tau`, o `NOT_REACHED`."""
    for n, score in curve:
        if score <= tau:
            return n
    return NOT_REACHED


# --- cuánto ocupa y cuánto cuesta preguntar -----------------------------------

@dataclass(frozen=True)
class Cost:
    """Lo que el mecanismo gasta, medido y no supuesto.

    `units` no es comparable entre mecanismos por su nombre --una celda de
    conteo y un ejemplar no son la misma cosa-- y por eso se informa junto a
    `unit_name`. `payload_bytes` cuenta sólo la carga útil declarada, no la
    sobrecarga del contenedor: con `dict` de Python esa sobrecarga es real pero
    es un detalle del intérprete, y mezclarla haría que el número dependiera de
    la versión de Python y no del algoritmo.
    """

    unit_name: str
    units: int
    payload_bytes: int
    nanoseconds_per_query: float
    queries: int


#: Un conteo Beta son dos flotantes de 64 bits.
_BYTES_PER_COUNT_CELL = 16


def counting_cost(model, bank: Sequence[Observation], *, repeats: int = 1) -> Cost:
    """Coste de un mecanismo que resume la experiencia en conteos."""
    units = int(model.visited_cells)
    return Cost("celdas de conteo", units, units * _BYTES_PER_COUNT_CELL,
                *_time_queries(model, bank, repeats))


def exemplar_cost(model, bank: Sequence[Observation], *, repeats: int = 1) -> Cost:
    """Coste de un mecanismo que conserva ejemplares."""
    return Cost("ejemplares", model.memory_items, model.memory_bytes,
                *_time_queries(model, bank, repeats))


def _time_queries(model: Predictor, bank: Sequence[Observation],
                  repeats: int) -> tuple[float, int]:
    """Nanosegundos por consulta de predicción, sobre el banco de evaluación.

    Sólo lee, así que no altera ninguna trayectoria y no entra en ningún gate
    cognitivo: es un dato de ingeniería que se informa aparte. Se cronometra el
    banco entero varias veces en vez de consultas sueltas porque una sola
    llamada está por debajo de la resolución útil del reloj.
    """
    if not bank:
        return float("nan"), 0
    started = time.perf_counter_ns()
    for _ in range(repeats):
        for observation in bank:
            for direction in Direction:
                model.predict(observation, direction)
    elapsed = time.perf_counter_ns() - started
    queries = repeats * len(bank) * len(Direction)
    return elapsed / queries, queries
