"""D5 · Disociación contra el motor real, y la observación COMPLETA.

El oráculo recorre el pasillo con `build_episode_components` y `run_step`, la
misma semántica que corre cualquier agente. Su única ventaja sobre un
organismo es que la facultad viene dada en vez de adquirida.

    memory=True    recuerda los cues que ya salieron de la ventana
    memory=False   sólo puede usar lo que ve AHORA

En el mundo exigente el cue está a `delay >= 3` columnas y el radio de visión
es 2: sin memoria no hay nada que leer y la elección es una moneda. En el
gemelo el cue está a una columna de las puertas, dentro de la ventana, y el
mismo oráculo amputado acierta. Eso es la disociación.

POR QUÉ SE GUARDA LA OBSERVACIÓN ENTERA

Declarar `I(A*; O) = 0` mirando sólo los canales de las puertas sería medir
una proyección. Una fuga puede entrar por cualquier canal visible: la
ocupación, la marca de otro objeto, la energía, el paso. `decision_records`
guarda el tensor completo que el motor entrega, más energía y paso, y la
puerta antifuga se calcula sobre eso.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np

from terrario.core.types import Action, ActionType, Direction
from terrario.lab import world_generator as gen
from terrario.world.transition import build_episode_components, run_step
from terrario.devworld.instances import DevWorld
from terrario.devworld.kernel import CUE_BOUNDARY

R = gen.VIEW_RADIUS


@dataclass
class _Seen:
    row: int
    column: int
    mark: float
    value: float


@dataclass(frozen=True)
class DecisionRecord:
    """Todo lo que el organismo tenía delante al elegir, y qué era correcto."""
    step: int
    observation: tuple[float, ...]   # el tensor visible entero, aplanado
    energy: float
    correct: str
    chosen: str


class DevOracle:
    """Mismo protocolo de agente que el oráculo diagnóstico."""

    def __init__(self, world: DevWorld, *, memory: bool, seed: int = 0) -> None:
        self.world = world
        self.memory = memory
        self.rng = np.random.default_rng(seed)
        self.config = {"hidden_dim": 1}
        self.column = 0
        self.step = 0
        self.energy = world.economy.initial_energy
        self._window: list[_Seen] = []
        self._known: set[tuple[int, int]] = set()
        self._memory: list[_Seen] = []
        self._doors_here = False
        self._last_obs: tuple[float, ...] = ()
        self.records: list[DecisionRecord] = []

    # -- protocolo ------------------------------------------------------------

    def perceive(self, observation: Any) -> None:
        ch = observation.channels
        self.energy = float(observation.agent_energy) * self.world.economy.max_energy
        self._last_obs = tuple(np.round(np.asarray(ch, dtype=float).ravel(), 3).tolist())
        self._window = []
        self._doors_here = False
        for wx in range(2 * R + 1):
            for wy in range(2 * R + 1):
                if ch[0, wx, wy] <= 0.0:
                    continue
                seen = _Seen(row=gen.ROW_PATH + wx - R, column=self.column + wy - R,
                             mark=round(float(ch[2, wx, wy]), 2),
                             value=round(float(ch[1, wx, wy]), 2))
                self._window.append(seen)
                key = (seen.row, seen.column)
                if key not in self._known and seen.mark in (gen.MARK_CUE, gen.MARK_DISTRACTOR):
                    self._known.add(key)
                    self._memory.append(seen)
        up = any(s.row == gen.ROW_CUE and s.column == self.column
                 and s.mark == gen.MARK_DOOR for s in self._window)
        down = any(s.row == gen.ROW_ALT and s.column == self.column
                   and s.mark == gen.MARK_DOOR for s in self._window)
        self._doors_here = up and down

    def offer_targets(self, targets: Any) -> None: pass
    def get_internal_state(self) -> dict: return {}
    def get_trace_events(self) -> list[dict[str, Any]]: return []
    def learn(self, transition: Any) -> None: pass

    @property
    def agent_identity(self) -> dict[str, Any]:
        return {"architecture_id": "DEVWORLD_ORACLE", "learning_enabled": False}

    def decide(self) -> Action:
        self.step += 1
        if self._doors_here:
            side = self._choose()
            st = self._station_at(self.column)
            if st is not None:
                self.records.append(DecisionRecord(
                    self.step - 1, self._last_obs, self.energy, st.designated, side))
            self._memory = []
            self._doors_here = False
            return Action(ActionType.CONSUME,
                          Direction.UP if side == "up" else Direction.DOWN)
        self.column += 1
        return Action(ActionType.MOVE, Direction.RIGHT)

    # -- la elección ----------------------------------------------------------

    def _station_at(self, column: int):
        return next((s for s in self.world.stations if s.door_column == column), None)

    def _choose(self) -> str:
        pool = self._memory if self.memory else self._window
        cues = sorted((s for s in pool if s.mark == gen.MARK_CUE),
                      key=lambda s: s.column)
        if not cues:
            return "up" if self.rng.random() < 0.5 else "down"
        return "up" if cues[-1].value > CUE_BOUNDARY else "down"


def run(world: DevWorld, *, memory: bool, seed: int = 0) -> DevOracle:
    oracle = DevOracle(world, memory=memory, seed=seed)
    comps = build_episode_components(world.scenario, duration_fallback=world.duration,
                                     strict_physics=True, with_lifecycle=False,
                                     world_seed=world.seed)
    for step in range(world.duration):
        out = run_step(comps, oracle, step, world_seed=world.seed, agent_seed=seed,
                       max_steps=world.duration, learning_enabled=False)
        if out.terminated or out.truncated:
            break
    return oracle


def accuracy(oracle: DevOracle) -> float:
    if not oracle.records:
        return float("nan")
    return sum(r.chosen == r.correct for r in oracle.records) / len(oracle.records)


def instrument_economy(stations: int, *, base: gen.Economy = gen.DEFAULT_ECONOMY
                       ) -> gen.Economy:
    """Una economía donde la muerte NO puede truncar la medición.

    Medido antes de esta corrección: en el mundo exigente de 24 estaciones, el
    oráculo SIN memoria elige al azar, pierde 6.0 por error, y con 20.0 de
    energía inicial muere tras cinco decisiones. Su marcador era 0.2000 sobre
    n=5, no sobre n=24: no medía «no recuerda», medía «no sobrevive».

    Es el reflejo del arreglo que el generador diagnóstico ya hizo por arriba
    --subir el techo para que no mordiera al oráculo perfecto--. Aquí hay que
    subir el suelo para que no muerda al amputado. Estos mundos son
    INSTRUMENTOS cuando se usa el oráculo; la economía real vuelve en D8.
    """
    worst = stations * base.loss + 4.0 * stations * base.step_energy_cost * 8
    return gen.Economy(initial_energy=max(base.initial_energy, worst + 50.0),
                       max_energy=base.max_energy, step_energy_cost=base.step_energy_cost,
                       gain=base.gain, loss=base.loss, safe=base.safe,
                       low_energy=base.low_energy)
