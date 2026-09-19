"""Oráculos con facultades desmontables, para que un mundo generado se falsee.

Un mundo que «exige memoria» es una afirmación; hay que probarla. La prueba es
un organismo guionizado que resuelve el mundo con todas sus facultades y deja
de resolverlo cuando se le quita exactamente la que el eje dice exigir. Si el
oráculo sin memoria sigue acertando, el mundo no exige memoria por mucho que
la docstring lo diga.

Los oráculos leen la ventana de observación REAL -- la misma que recibe A4 --
y nada más. Lo que saben del mundo es lo que un oráculo puede saber: las
reglas, el mapeo cue→lado, el paso de la inversión. Lo que no pueden hacer es
mirar el estado: el canal 3 sigue oculto también para ellos. Su única ventaja
sobre un organismo es que las facultades vienen dadas en vez de adquiridas.

Facultades y el eje que cada una vuelve irrelevante:

    memory       retener cues que ya salieron de la ventana      → delay
    order        recordar el orden, no sólo el conjunto           → sequence
    filter       distinguir cue de distractor                     → distractors
    mapping      saber qué lado señala cada valor                 → hidden
    homeostasis  elegir la segura cuando la energía es baja       → risk
    inversion    saber cuándo se invierte el mapeo                → inversion

`novelty` no tiene facultad aquí: lo que UNC produce es una señal de
incertidumbre, y un guion no la tiene. Ese eje se comprueba en el mundo (hay
estaciones novedosas en la proporción declarada), no en el oráculo.
"""

from __future__ import annotations

from dataclasses import dataclass, fields, replace
from typing import Any, Iterable

import numpy as np

from terrario.core.types import Action, ActionType, Direction
from terrario.lab import world_generator as gen
from terrario.world.transition import build_episode_components, run_step

R = gen.VIEW_RADIUS


@dataclass(frozen=True)
class Faculties:
    memory: bool = True
    order: bool = True
    filter: bool = True
    mapping: bool = True
    homeostasis: bool = True
    inversion: bool = True


FULL = Faculties()
FACULTY_NAMES: tuple[str, ...] = tuple(f.name for f in fields(Faculties))

#: Qué facultad vuelve irrelevante cada eje. `novelty` no tiene: ver docstring.
FACULTY_OF_AXIS: dict[str, str | None] = {
    "delay": "memory", "sequence": "order", "distractors": "filter",
    "hidden": "mapping", "risk": "homeostasis", "inversion": "inversion",
    "novelty": None,
}


def without(faculty: str) -> Faculties:
    if faculty not in FACULTY_NAMES:
        raise KeyError(f"facultad desconocida {faculty!r}; hay {FACULTY_NAMES}")
    return replace(FULL, **{faculty: False})


@dataclass
class _Seen:
    row: int
    column: int
    mark: float
    value: float


class Oracle:
    """Avanza por el pasillo y, ante dos puertas, elige con lo que tiene.

    Lleva la cuenta de su propia columna por integración de camino: sabe qué
    hizo. Eso le permite reconocer un objeto que ya vio y no volver a
    apuntarlo, que es lo que hace posible «primera aparición» sin mirar el
    estado del mundo.
    """

    def __init__(self, world: gen.GeneratedWorld, faculties: Faculties = FULL, *,
                 seed: int = 0) -> None:
        self.world = world
        self.f = faculties
        self.rng = np.random.default_rng(seed)
        self.config = {"hidden_dim": 1}
        self.column = 0
        self.step = 0
        self.energy = world.economy.initial_energy
        self._window: list[_Seen] = []
        self._known: set[tuple[int, int]] = set()
        self._memory: list[_Seen] = []
        self._doors_here: dict[str, float] | None = None
        self.choices: list[tuple[int, str]] = []

    # -- protocolo de agente --------------------------------------------------

    def perceive(self, observation: Any) -> None:
        ch = observation.channels
        self.energy = float(observation.agent_energy) * self.world.economy.max_energy
        self._window = []
        self._doors_here = None
        for wx in range(2 * R + 1):
            for wy in range(2 * R + 1):
                if ch[0, wx, wy] <= 0.0:
                    continue
                seen = _Seen(row=gen.ROW_PATH + wx - R, column=self.column + wy - R,
                             mark=round(float(ch[2, wx, wy]), 2),
                             value=round(float(ch[1, wx, wy]), 2))
                self._window.append(seen)
                key = (seen.row, seen.column)
                if key not in self._known and seen.mark in (gen.MARK_CUE, gen.MARK_DISTRACTOR, gen.MARK_NOVEL):
                    self._known.add(key)
                    self._memory.append(seen)
        up = next((s for s in self._window if s.row == gen.ROW_CUE and s.column == self.column
                   and s.mark == gen.MARK_DOOR), None)
        down = next((s for s in self._window if s.row == gen.ROW_ALT and s.column == self.column
                     and s.mark == gen.MARK_DOOR), None)
        if up is not None and down is not None:
            # canal 2 de cada puerta: la marca visible cuando `hidden` es False
            self._doors_here = {"up": float(ch[3, R - 1, R]), "down": float(ch[3, R + 1, R])}

    def offer_targets(self, targets: Any) -> None:
        pass

    def get_internal_state(self) -> dict:
        return {}

    @property
    def agent_identity(self) -> dict[str, Any]:
        """Minimal observer identity for running the same oracle through Lab surfaces."""
        return {"architecture_id": "DIAGNOSTIC_ORACLE", "learning_enabled": False}

    def get_trace_events(self) -> list[dict[str, Any]]:
        return []

    def learn(self, transition: Any) -> None:
        pass

    def decide(self) -> Action:
        self.step += 1
        if self._doors_here is not None:
            side = self._choose()
            self.choices.append((self.step - 1, side))
            self._memory = []
            self._doors_here = None
            return Action(ActionType.CONSUME, Direction.UP if side == "up" else Direction.DOWN)
        self.column += 1
        return Action(ActionType.MOVE, Direction.RIGHT)

    # -- la elección ----------------------------------------------------------

    def _cues(self) -> list[_Seen]:
        pool = self._memory if self.f.memory else [s for s in self._window if s.mark != gen.MARK_DOOR]
        pool = sorted(pool, key=lambda s: s.column)
        if self.f.filter:
            pool = [s for s in pool if s.mark in (gen.MARK_CUE, gen.MARK_NOVEL)]
        return pool

    def _designated(self) -> str | None:
        """El lado que el mundo señala, según lo que el oráculo puede leer."""
        assert self._doors_here is not None
        marks = self._doors_here
        if marks["up"] != marks["down"]:                 # hidden=False: se lee
            return "up" if marks["up"] > marks["down"] else "down"
        if not self.f.mapping:
            return None
        cues = self._cues()
        n = self.world.demand.sequence
        if not cues:
            return None
        if any(s.mark == gen.MARK_NOVEL for s in cues[-n:]):
            return None
        if n == 1:
            return "up" if cues[-1].value >= 0.5 else "down"
        last = cues[-n:]
        if len(last) < n:
            return None
        values = [s.value for s in last]
        if not self.f.order:
            values = list(self.rng.permutation(values))
        return "up" if values == sorted(values) else "down"

    def _choose(self) -> str:
        designated = self._designated()
        if designated is None:
            return "up" if self.rng.random() < 0.5 else "down"
        inverted = (self.f.inversion and self.world.inversion_step is not None
                    and self.step - 1 >= self.world.inversion_step)
        if self.world.demand.risk:
            if self.f.homeostasis and self.energy <= self.world.economy.low_energy:
                return gen._other(designated)
            return designated
        return gen._other(designated) if inverted else designated


# --- Correr una vida --------------------------------------------------------

def run_life(world: gen.GeneratedWorld, agent: Any, *, agent_seed: int = 0) -> list[Any]:
    """Una vida entera por la semántica compartida. Devuelve los `StepOutcome`."""
    comps = build_episode_components(world.scenario, duration_fallback=world.duration,
                                     strict_physics=True, with_lifecycle=False,
                                     world_seed=world.seed)
    outcomes = []
    for step in range(world.duration):
        out = run_step(comps, agent, step, world_seed=world.seed, agent_seed=agent_seed,
                       max_steps=world.duration, learning_enabled=False)
        outcomes.append(out)
        if out.terminated or out.truncated:
            break
    return outcomes


def life_score(world: gen.GeneratedWorld, faculties: Faculties = FULL, *,
               seed: int = 0) -> gen.Score:
    """Aciertos Y viabilidad. La traza ya venía con `terminated` y la energía
    de cada paso; hasta la reparación de 2026-09-18 esta función la tiraba."""
    oracle = Oracle(world, faculties, seed=seed)
    outcomes = run_life(world, oracle, agent_seed=seed)
    base = gen.score(world, gen.consumptions_from(world, outcomes))
    return replace(base, viability=gen.viability_from(world, outcomes))


@dataclass(frozen=True)
class DemandVerdict:
    """Lo que la matriz dice de una capacidad: si su mundo exige su facultad."""

    capability: str
    axis: str
    faculty: str | None
    full_on_demanding: float | None
    ablated_on_demanding: float | None
    ablated_on_control: float | None
    n_decisions: int

    @property
    def demands(self) -> bool | None:
        """True si el oráculo completo resuelve el mundo, el amputado no, y el
        amputado sí resuelve el control. None si no hay facultad que amputar."""
        if self.faculty is None:
            return None
        if None in (self.full_on_demanding, self.ablated_on_demanding, self.ablated_on_control):
            return False
        return (self.full_on_demanding >= 0.95 and self.ablated_on_demanding <= 0.7
                and self.ablated_on_control >= 0.95)


def _mean(xs: Iterable[float | None]) -> float | None:
    vals = [x for x in xs if x is not None]
    return sum(vals) / len(vals) if vals else None


def verdict_for(capability: str, *, seeds: Iterable[int] = range(6),
                stations: int = 8) -> DemandVerdict:
    axis, _ = gen.DEMAND_OF[capability]
    faculty = FACULTY_OF_AXIS[axis]
    seeds = list(seeds)
    full_d, abl_d, abl_c, n = [], [], [], 0
    def metric(s: gen.Score, w: gen.GeneratedWorld) -> float | None:
        if axis == "risk":
            return s.modulation if w.demand.risk else s.accuracy
        if axis == "inversion" and w.inversion_step is not None:
            return s.accuracy_after
        return s.accuracy

    for seed in seeds:
        d = gen.world_for([capability], seed=seed, stations=stations)
        c = gen.control_for([capability], capability, seed=seed, stations=stations)
        sd = life_score(d, FULL, seed=seed)
        full_d.append(metric(sd, d))
        n += sd.decisions
        if faculty is not None:
            abl_d.append(metric(life_score(d, without(faculty), seed=seed), d))
            abl_c.append(metric(life_score(c, without(faculty), seed=seed), c))
    return DemandVerdict(capability, axis, faculty, _mean(full_d),
                         _mean(abl_d) if faculty else None,
                         _mean(abl_c) if faculty else None, n)
