"""Reversal de contingencia sensorimotora · LEVEL1-SENSORIMOTOR-REVERSAL-01.

El Experimento 1 estableció que el ser adquiere una contingencia
`(observación, comando) → se movió`. Éste pregunta qué hace ese mismo mecanismo
cuando la contingencia deja de describir el mundo.

**La intervención es una sola variable.** Cambia el mapeo del comando al acto
físico, y nada más:

    m_A = identidad          m_B = {ARRIBA↔ABAJO, IZQUIERDA↔DERECHA}

El mundo ejecuta `m(a)`; el ser registra **`a`**. Si registrara `m(a)`, la
contingencia sería idéntica antes y después y el reversal desaparecería.

**El switch es un evento ENTRE transiciones, no una transición.** Con
`n_A = 2048` y rejilla nueva cada 64 pasos, `2048 mod 64 == 0`, así que la
frontera de fase coincide con una renovación programada. Si se dejaran juntas,
en ese instante cambiarían dos cosas --el mapeo y el mundo entero-- y el shock
predictivo mediría las dos mezcladas. El orden obligatorio las separa:

    transición 2047  ─ última de fase A, íntegra bajo C_A
    LAYOUT_REFRESH   ─ el que tocaba por calendario; no es el switch
    snapshot W*, K*  ─ el mundo que existe a ambos lados
    SWITCH           ─ sólo el mapeo: sin azar, sin acto, sin aprendizaje
    transición 2048  ─ primera de fase B, desde el MISMO W*

La huella `F = hash(W*, K*)` debe coincidir antes y después del switch. El mapeo
no entra en ella: es precisamente la variable intervenida, y se registra aparte.

**Conocimiento presente pero mal indexado.** Bajo este reversal se cumple

    P_B(y | o, d) = P_A(y | o, m_B(d))

es decir: la contingencia nueva ya está dentro del ser, bajo otras etiquetas
motoras. Ninguno de los dos mecanismos tiene operador de reetiquetado, así que
los dos deben reconstruir contando. Lo que se mide es **reaprendizaje bajo
reetiquetado causal sin mecanismo explícito de reetiquetado**, no la capacidad
de inferir la permutación.
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, Sequence

import numpy as np

from terrario.level1.world import (
    ALL_OBSERVATIONS, Direction, Grid, Observation, Transition,
)

#: El mapeo antes del reversal: cada comando hace lo que dice.
MAPPING_A: dict[Direction, Direction] = {d: d for d in Direction}

#: El mapeo después: los cuatro actuadores invertidos. Es una involución.
MAPPING_B: dict[Direction, Direction] = {
    Direction.UP: Direction.DOWN,
    Direction.DOWN: Direction.UP,
    Direction.LEFT: Direction.RIGHT,
    Direction.RIGHT: Direction.LEFT,
}

Mapping = dict[Direction, Direction]


def outcome_under(observation: Observation, command: Direction,
                  mapping: Mapping) -> int:
    """`y = 1 − o[m(a)]`. El contrato físico, leído a través del mapeo."""
    return 1 - observation[int(mapping[command])]


def flips_under(observation: Observation, command: Direction,
                before: Mapping, after: Mapping) -> bool:
    """¿Esta celda cambia de respuesta con el reversal?

    Es todo o nada por celda: como `o` está fijo dentro de una celda, o toda
    visita posterior contradice, o toda confirma. No hay mezcla por celda.
    """
    return outcome_under(observation, command, before) != \
        outcome_under(observation, command, after)


def switch_effectiveness(bank: Sequence[Observation], before: Mapping,
                         after: Mapping) -> float:
    """`R_switch`: fracción de pares evaluados cuyo resultado cambia.

    Se deriva del banco ejecutado, nunca de una constante: si el mapeo nuevo no
    cambia ningún resultado, el experimento no tiene intervención.
    """
    total = flipped = 0
    for observation in bank:
        for command in Direction:
            total += 1
            flipped += flips_under(observation, command, before, after)
    return flipped / total if total else float("nan")


# --- la huella del switch -----------------------------------------------------

def world_digest(grid: Grid, rng: np.random.Generator) -> str:
    """`W*`: la rejilla, la posición y el estado del azar."""
    h = hashlib.sha256()
    h.update(np.ascontiguousarray(grid.cells).tobytes())
    h.update(repr(grid.position).encode())
    h.update(json.dumps(rng.bit_generator.state, sort_keys=True,
                        default=str).encode())
    return h.hexdigest()


def learner_digest(model: Any) -> str:
    """`K*`: los suficientes estadísticos, sean del tipo que sean."""
    h = hashlib.sha256()
    for name in ("_belief", "_base", "_feature", "_value"):
        store = getattr(model, name, None)
        if store is None:
            continue
        h.update(name.encode())
        for key in sorted(store, key=repr):
            h.update(repr(key).encode())
            h.update(repr(store[key]).encode())
    h.update(f"frozen={getattr(model, 'frozen', None)}".encode())
    return h.hexdigest()


# --- el flujo por fases -------------------------------------------------------

@dataclass(frozen=True)
class BoundaryEvent:
    """Un evento de la frontera de fase, registrado para poder auditarlo."""

    name: str
    step: int


@dataclass
class PhasedStream:
    """La experiencia maestra: una sola, consumida por los cuatro brazos REV.

    La actividad motora basal es **independiente de la política** --los actos son
    uniformes-- así que un solo flujo grabado sirve para todos, y la identidad de
    transiciones entre brazos se garantiza por construcción, no por coincidencia.
    """

    transitions: list[Transition]
    events: list[BoundaryEvent]
    violations: int
    switch_index: int | None
    world_before: str | None
    world_after: str | None

    def phase_a(self) -> list[Transition]:
        return self.transitions[:self.switch_index] if self.switch_index \
            else list(self.transitions)

    def phase_b(self) -> list[Transition]:
        return self.transitions[self.switch_index:] if self.switch_index else []

    def digest(self) -> str:
        """Para `STREAM_PARITY_FAILED`: dos brazos con distinta huella no
        recibieron la misma experiencia, por mucho que compartan semilla."""
        h = hashlib.sha256()
        for t in self.transitions:
            h.update(repr((t.observation, int(t.direction), t.moved,
                           t.next_observation)).encode())
        return h.hexdigest()


def phased_babbling(seed: int, *, n_a: int, n_b: int, grid_size: int = 7,
                    wall_probability: float = 0.25,
                    steps_per_layout: int = 64,
                    mapping_before: Mapping = MAPPING_A,
                    mapping_after: Mapping | None = MAPPING_B) -> PhasedStream:
    """Generar la experiencia con el switch como evento entre transiciones.

    `mapping_after = None` produce la condición STABLE: misma frontera de fase y
    misma renovación programada de rejilla, sin cambio de mapeo. Eso es lo que
    permite a STABLE falsar que la forma caída→recuperación venga del mero paso
    del tiempo o de la estructura de checkpoints.
    """
    rng = np.random.default_rng(seed)
    transitions: list[Transition] = []
    events: list[BoundaryEvent] = []
    violations = 0
    mapping = mapping_before
    pending_switch = mapping_after is not None
    switch_index: int | None = None
    world_before = world_after = None
    total = n_a + n_b

    while len(transitions) < total:
        grid = Grid.random(grid_size, wall_probability, rng)
        events.append(BoundaryEvent("layout_refresh", len(transitions)))

        # La frontera de fase se procesa DESPUÉS de la renovación programada y
        # ANTES de la primera transición de la fase siguiente. El switch no
        # consume azar, no observa, no actúa y no toca al aprendiz.
        if pending_switch and len(transitions) == n_a:
            world_before = world_digest(grid, rng)
            events.append(BoundaryEvent("snapshot", len(transitions)))
            mapping = mapping_after           # la única mutación del evento
            events.append(BoundaryEvent("switch", len(transitions)))
            world_after = world_digest(grid, rng)
            switch_index = len(transitions)
            pending_switch = False
        elif mapping_after is None and len(transitions) == n_a:
            # STABLE recibe la misma frontera protocolaria, sin switch.
            events.append(BoundaryEvent("phase_boundary_no_switch",
                                        len(transitions)))
            switch_index = len(transitions)

        for _ in range(steps_per_layout):
            if len(transitions) >= total:
                break
            observation = grid.observe()
            command = Direction(int(rng.integers(len(Direction))))
            moved, next_observation = grid.step(mapping[command])
            if moved != outcome_under(observation, command, mapping):
                violations += 1
            # Se registra el COMANDO, jamás el acto remapeado.
            transitions.append(Transition(observation, command, moved,
                                          next_observation))

    return PhasedStream(transitions, events, violations, switch_index,
                        world_before, world_after)


# --- el control positivo ------------------------------------------------------

class EMATable:
    """Tabla sobre `(o,a)` con actualización por error reciente.

    `q ← q + η(y − q)`. Tabular a propósito: comparte representación con
    `ContingencyTable` y cambia **sólo** la regla temporal, de modo que el
    contraste con CASES aísla la regla y el contraste FEATURES−CASES aísla la
    representación. Si este control usara rasgos, ninguno de los dos quedaría
    identificado.

    Su papel no es representar nuestra teoría: es demostrar que el instrumento
    **puede** detectar readaptación. Si no revierte, un fracaso de CASES o
    FEATURES no significa nada.
    """

    def __init__(self, *, rate: float = 0.2, initial: float = 0.5,
                 frozen: bool = False) -> None:
        self.rate = rate
        self.initial = initial
        self.frozen = frozen
        self._value: dict[tuple[Observation, Direction], float] = {}

    def predict(self, observation: Observation, direction: Direction) -> float:
        """No escribe: consulta con valor por defecto, como el resto del banco."""
        return self._value.get((observation, direction), self.initial)

    def observe(self, observation: Observation, direction: Direction,
                moved: int) -> None:
        if self.frozen:
            return
        key = (observation, direction)
        current = self._value.get(key, self.initial)
        self._value[key] = current + self.rate * (moved - current)

    def act(self, observation: Observation, rng: np.random.Generator) -> Direction:
        values = np.asarray([self.predict(observation, d) for d in Direction],
                            dtype=float)
        tied = np.flatnonzero(np.isclose(values, values.max()))
        return Direction(int(rng.choice(tied)))

    @property
    def visited_cells(self) -> int:
        return len(self._value)


# --- referencias independientes del predictor ---------------------------------
#
# §21 del contrato: no se valida `predict()` llamando a `predict()`. Estas
# funciones reconstruyen la predicción desde los suficientes estadísticos
# CONTADOS SOBRE EL FLUJO, no leídos del modelo. Detectan por tanto dos cosas
# distintas: un error de cálculo en el predictor, y un error de contabilidad en
# el modelo. Lo que NO pueden detectar es un error compartido por ambos, porque
# la independencia es de cómputo y no de datos.

CellCounts = dict[tuple[Observation, Direction], tuple[int, int]]
FeatureCounts = dict[tuple[Direction, int, int], tuple[int, int]]
BaseCounts = dict[Direction, tuple[int, int]]


def count_cases(transitions: Sequence[Transition]) -> CellCounts:
    """`(α_incremento, β_incremento)` por celda `(o,d)`, desde el flujo."""
    counts: dict[tuple[Observation, Direction], list[int]] = {}
    for t in transitions:
        cell = counts.setdefault((t.observation, t.direction), [0, 0])
        cell[0 if t.moved else 1] += 1
    return {k: (v[0], v[1]) for k, v in counts.items()}


def count_features(transitions: Sequence[Transition]
                   ) -> tuple[BaseCounts, FeatureCounts]:
    """Los dos almacenes de `FactoredContingency`, contados por separado.

    Se devuelven separados porque su densidad de actualización es distinta --el
    acumulador base recibe una actualización por transición sobre 4 celdas; los
    rasgos, cuatro sobre 32-- y resumir ambos como «FEATURES» esconde un factor
    de dos entre ellos.
    """
    base: dict[Direction, list[int]] = {}
    feature: dict[tuple[Direction, int, int], list[int]] = {}
    for t in transitions:
        slot = base.setdefault(t.direction, [0, 0])
        slot[0 if t.moved else 1] += 1
        for position, value in enumerate(t.observation):
            cell = feature.setdefault((t.direction, position, value), [0, 0])
            cell[0 if t.moved else 1] += 1
    return ({k: (v[0], v[1]) for k, v in base.items()},
            {k: (v[0], v[1]) for k, v in feature.items()})


def reference_cases(counts: CellCounts, observation: Observation,
                    direction: Direction, *, prior: float = 1.0) -> float:
    """`(1+α)/(2+α+β)` desde los conteos, sin tocar el modelo."""
    alpha, beta = counts.get((observation, direction), (0, 0))
    return (prior + alpha) / (2 * prior + alpha + beta)


def _logit(alpha: float, beta: float) -> float:
    return math.log(alpha) - math.log(beta)


def reference_features(base: BaseCounts, feature: FeatureCounts,
                       observation: Observation, direction: Direction,
                       *, prior: float = 1.0) -> float:
    """La misma suma de log-momios que usa `predict`, recompuesta aparte."""
    b_alpha, b_beta = base.get(direction, (0, 0))
    base_logit = _logit(prior + b_alpha, prior + b_beta)
    total = base_logit
    for position, value in enumerate(observation):
        f_alpha, f_beta = feature.get((direction, position, value), (0, 0))
        total += _logit(prior + f_alpha, prior + f_beta) - base_logit
    return 1.0 / (1.0 + math.exp(-total))


def reference_brier(predict: Callable[[Observation, Direction], float],
                    bank: Sequence[Observation], mapping: Mapping
                    ) -> float:
    """El Brier que la referencia implica, sobre el mismo banco y mapeo."""
    total = squared = 0
    for observation in bank:
        for command in Direction:
            truth = outcome_under(observation, command, mapping)
            squared += (predict(observation, command) - truth) ** 2
            total += 1
    return squared / total if total else float("nan")


# --- medición bajo el mapeo vigente -------------------------------------------

def policy_rng(seed: int, arm: str, checkpoint: int) -> np.random.Generator:
    """Azar del readout, derivado y aislado.

    Nunca se comparte con el generador del flujo ni con el del mundo: una sonda
    que consumiera de ellos haría divergir a los brazos por el mero hecho de
    medirlos, y con dieciséis checkpoints ese sesgo sería sistemático.
    """
    material = int(hashlib.sha256(
        f"{seed}|{arm}|{checkpoint}".encode()).hexdigest()[:16], 16)
    return np.random.default_rng(material)


def brier_under(model: Any, bank: Sequence[Observation],
                mapping: Mapping) -> float:
    """`BS_total`: las cuatro direcciones, tome la que tome. Gobierna `τ`."""
    return reference_brier(model.predict, bank, mapping)


def brier_split(model: Any, bank: Sequence[Observation], mapping: Mapping,
                rng: np.random.Generator) -> tuple[float, float]:
    """`(BS_chosen, BS_unchosen)`.

    En el Experimento 1 el 75 % del Brier total es conocimiento que la conducta
    nunca usa, y allí los dos números coinciden. Bajo reversal no tienen por qué:
    las celdas que voltean y las direcciones que el ser toma no son las mismas.
    """
    chosen_sq = other_sq = 0.0
    chosen_n = other_n = 0
    for observation in bank:
        picked = model.act(observation, rng)
        for command in Direction:
            truth = outcome_under(observation, command, mapping)
            error = (model.predict(observation, command) - truth) ** 2
            if command == picked:
                chosen_sq += error; chosen_n += 1
            else:
                other_sq += error; other_n += 1
    return (chosen_sq / chosen_n if chosen_n else float("nan"),
            other_sq / other_n if other_n else float("nan"))


def movement_rate_under(policy: Callable[[Observation, np.random.Generator], Direction],
                        bank: Sequence[Observation], rng: np.random.Generator,
                        mapping: Mapping) -> float:
    """Fracción de situaciones con salida en que el comando elegido NO choca.

    El mapeo se aplica al acto, no a la creencia: el ser elige `ARRIBA` creyendo
    que avanza y el mundo lo manda `ABAJO`. Medir `o[π(o)]` en vez de
    `o[m(π(o))]` después del reversal daría la competencia de un mundo que ya no
    existe.
    """
    moved = sum(1 for o in bank
                if outcome_under(o, policy(o, rng), mapping) == 1)
    return moved / len(bank) if bank else float("nan")


def effective_dose(phase_b: Sequence[Transition], before: Mapping,
                   after: Mapping) -> tuple[int, float, CellCounts]:
    """Cuánto reversal recibió DE HECHO, no cuánto duró la fase.

    Devuelve `(D_REV, ρ_REV, conteos por celda)`. La dosis es todo o nada por
    celda: dentro de una celda `o` está fijo, luego o toda visita contradice o
    toda confirma.
    """
    contradicting = 0
    per_cell: dict[tuple[Observation, Direction], list[int]] = {}
    for t in phase_b:
        cell = per_cell.setdefault((t.observation, t.direction), [0, 0])
        if flips_under(t.observation, t.direction, before, after):
            contradicting += 1
            cell[0] += 1
        else:
            cell[1] += 1
    rho = contradicting / len(phase_b) if phase_b else float("nan")
    return contradicting, rho, {k: (v[0], v[1]) for k, v in per_cell.items()}
