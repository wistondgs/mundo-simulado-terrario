"""Una vida · adquirir, congelar, continuar, y recién entonces evaluar.

La separación es el corazón del nivel. Si se puntuara sobre las transiciones con
las que la tabla se actualizó, «predecir» sería recitar. El banco POST se genera
después del congelado, en el **mismo mundo**, continuando el mismo flujo motor:
es futuro real del organismo y no lo ha visto.

Tampoco se puntúa contra un banco poblacional de muchos mundos. Eso mediría
generalización entre mundos, que el nivel no declara, y medido invierte el signo
del resultado: a 16 384 pasos el organismo sale peor que congelado. Se conserva
como diagnóstico exploratorio y nunca como gate (oráculo §8).

La paridad entre brazos no se impone: es estructural. La fuente motora no lee la
tabla --`motor.py` no importa `temporal.py`-- así que los cuatro brazos reciben
por construcción la misma trayectoria. El hash está para demostrarlo, no para
conseguirlo.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass

from terrario.level1.world import Direction, Observation
from terrario.level16.motor import EndogenousMotor
from terrario.level16.structure import WorldStructure, describe_world
from terrario.level16.world import build_world, motor_stream

#: Presupuesto de adquisición. El más bajo con la curva ya saturada: de 4k a 16k
#: la ganancia es 0.027 nats. No es un mínimo demostrado, es un presupuesto.
ACQUISITION_STEPS = 4096

#: Transiciones nuevas del banco POST.
POST_STEPS = 2048


@dataclass(frozen=True)
class Instruments:
    """Lo que se mide de una vida. Nada de esto realimenta la política."""

    component_size: int
    reachable_observations: int
    reachable_transitions: int
    changing_transitions: int
    change_rate: float
    move_rate: float
    motor_emitted: int
    trajectory_hash: str
    stratum: str


@dataclass(frozen=True)
class Life:
    """Una vida entera: lo vivido, lo congelado y el futuro con que se juzga."""

    seed: int
    structure: WorldStructure
    previous: tuple[Observation, ...]
    following: tuple[Observation, ...]
    post_previous: tuple[Observation, ...]
    post_following: tuple[Observation, ...]
    instruments: Instruments

    @property
    def acquisition(self) -> tuple[tuple[Observation, Observation], ...]:
        return tuple(zip(self.previous, self.following))

    @property
    def post(self) -> tuple[tuple[Observation, Observation], ...]:
        return tuple(zip(self.post_previous, self.post_following))


def live(seed: int, steps: int = ACQUISITION_STEPS,
         post_steps: int = POST_STEPS) -> Life:
    """Vivir una vida y devolverla entera. No hay modelo aquí: sólo el cuerpo.

    Que esta función no reciba ni construya una `TemporalModel` es el modo de
    garantizar que la trayectoria no dependa de lo que se haya aprendido.
    """
    grid = build_world(seed)
    structure = describe_world(seed, grid)
    motor = EndogenousMotor(motor_stream(seed))

    huella = hashlib.sha256()
    previous: list[Observation] = []
    following: list[Observation] = []
    post_previous: list[Observation] = []
    post_following: list[Observation] = []
    movidos = 0

    observacion = grid.observe()
    for indice in range(steps + post_steps):
        direccion: Direction = motor.next()
        movido, siguiente = grid.step(direccion)
        huella.update(bytes([int(direccion), movido, *observacion, *siguiente]))
        destino = (previous, following) if indice < steps else (post_previous,
                                                                post_following)
        destino[0].append(observacion)
        destino[1].append(siguiente)
        movidos += movido
        observacion = siguiente

    cambios = sum(1 for a, b in zip(previous, following) if a != b)
    instrumentos = Instruments(
        component_size=structure.component_size,
        reachable_observations=len(structure.observations),
        reachable_transitions=len(structure.transitions),
        changing_transitions=structure.changing_transitions,
        change_rate=cambios / steps,
        move_rate=movidos / (steps + post_steps),
        motor_emitted=motor.emitted,
        trajectory_hash=huella.hexdigest(),
        stratum=structure.stratum,
    )
    return Life(seed, structure, tuple(previous), tuple(following),
                tuple(post_previous), tuple(post_following), instrumentos)
