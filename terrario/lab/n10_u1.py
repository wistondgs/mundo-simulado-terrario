"""U1 · el primer organismo, bajo una forma causal que ya estaba sellada.

Two classes and a reason for the split.  `U1` is the mechanism, and its
`perceive` takes a cue value because that is what the sealed protocol in
`n10_u1_spec` says it takes; the specification was written first and is not
adjusted to fit this.  `U1Agent` is the only thing that touches the engine:
it pulls the cue out of an `Observation`, drives the corridor, and hands the
consequence back.  Keeping them apart means the sealed gates intervene on the
mechanism directly, with no world in the way, and the adapter has no
parameters of its own to hide anything in.

Nothing here is imported from `tests/`.  The reference in the test suite
exists to show the gates are satisfiable; this had to be written from the
contract instead, and then made to pass the same gates.

**The token is opaque and stays opaque.**  `tau_...` does not mean up, down,
good or bad.  All motor meaning lives in the four learned numbers, and the
proof that it does is that the same mechanism learns the normal contingency
and its inverse from one identical starting state.

**Ties are broken by a dedicated draw, not by the order of the actions.**
First-action-wins would be a preference nobody put in the table and nobody
could see in it, and the policy is run rather than inspected to check that
it is not there.

**The freeze is defended here and not delegated to the caller.**  A runner
that simply stops calling `learn` looks identical, from the outside, to one
that forgot to; under `EVALUATION` this refuses the update itself.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import numpy as np

from terrario.core.types import Action, ActionType, Direction
from terrario.lab import world_generator as gen
from terrario.lab.n10_instrument import feedback_of
from terrario.lab.n10_u1_spec import ACTIONS, DOWN, EMPTY, UP, opaque_token

U1_VERSION = "terrario.lab.n10-u1/v1"


class Mode(StrEnum):
    ACQUISITION = "ACQUISITION"
    EVALUATION = "EVALUATION"


@dataclass(frozen=True)
class U1Config:
    """Parámetros explícitos. Ninguno se busca todavía: primero se pregunta si
    el mecanismo aprende algo, y sólo después cuánto presupuesto necesita."""

    alpha: float = 0.3
    exploration: float = 0.2
    seed: int = 0


class U1:
    """Un token persistente, dos acciones y cuatro números que se aprenden."""

    def __init__(self, config: U1Config | None = None) -> None:
        self.config = config or U1Config()
        self.memory: str = EMPTY
        self.theta: dict[tuple[str, str], float] = {}
        self.mode: Mode = Mode.ACQUISITION

    # -- el protocolo que los gates intervienen ------------------------------

    @property
    def learning(self) -> bool:
        return self.mode is Mode.ACQUISITION

    @learning.setter
    def learning(self, valor: bool) -> None:
        self.mode = Mode.ACQUISITION if valor else Mode.EVALUATION

    def perceive(self, cue_value: float | None) -> None:
        """Un cue visible escribe el token. Lo demás no lo toca.

        No hay ninguna pregunta que este método pueda hacerle al mundo: recibe
        un valor percibido y nada más.
        """
        if cue_value is not None:
            self.memory = opaque_token(cue_value)

    def decide(self, rng: Any) -> str:
        if rng.random() < self.config.exploration:
            return ACTIONS[int(rng.integers(len(ACTIONS)))]
        arriba = self.theta.get((self.memory, UP), 0.0)
        abajo = self.theta.get((self.memory, DOWN), 0.0)
        if arriba == abajo:
            return ACTIONS[int(rng.integers(len(ACTIONS)))]
        return UP if arriba > abajo else DOWN

    def learn(self, action: str, consequence: float) -> None:
        """`consequence` es el delta. Nunca un nivel: después de que el aparato
        repone la energía, el nivel es el mismo se acertara o no."""
        if self.mode is Mode.EVALUATION:
            return
        clave = (self.memory, action)
        q = self.theta.get(clave, 0.0)
        self.theta[clave] = q + self.config.alpha * (float(consequence) - q)

    def theta_digest(self) -> str:
        plano = ";".join(f"{k[0]}|{k[1]}={self.theta[k]:.12g}"
                         for k in sorted(self.theta))
        return hashlib.sha256(plano.encode()).hexdigest()

    # -- congelación y clonado ----------------------------------------------

    def freeze(self) -> None:
        self.mode = Mode.EVALUATION

    def clone(self) -> "U1":
        """Un clon exacto de lo aprendido, para que los brazos difieran sólo
        en la intervención y no en tres entrenamientos distintos."""
        otro = U1(self.config)
        otro.memory = self.memory
        otro.theta = dict(self.theta)
        otro.mode = self.mode
        return otro

    def as_record(self) -> dict:
        return {"version": U1_VERSION, "mode": self.mode.value,
                "alpha": self.config.alpha, "exploration": self.config.exploration,
                "seed": self.config.seed, "memory": self.memory,
                "theta": {f"{k[0]}|{k[1]}": v for k, v in sorted(self.theta.items())},
                "theta_digest": self.theta_digest()}


class U1Agent:
    """Lo único que toca el motor: saca el cue de la observación y camina.

    La navegación por el pasillo y el discriminador de cue son SUMINISTRADOS
    y se declaran como tales. Lo que no se suministra es qué acción conviene
    bajo cada token.
    """

    def __init__(self, world: Any, config: U1Config | None = None) -> None:
        self.core = U1(config)
        self.world = world
        self._rng = np.random.default_rng(self.core.config.seed)
        self.column = 0
        self._doors_here = False
        self._pending: str | None = None
        self.decisions: list[tuple[int, str]] = []
        self.step = 0

    # -- protocolo de agente -------------------------------------------------

    def perceive(self, observation: Any) -> None:
        ch = observation.channels
        radio = gen.VIEW_RADIUS
        cue: float | None = None
        arriba = abajo = False
        for wx in range(2 * radio + 1):
            for wy in range(2 * radio + 1):
                if ch[0, wx, wy] <= 0.0:
                    continue
                marca = round(float(ch[2, wx, wy]), 2)
                fila = gen.ROW_PATH + wx - radio
                columna = self.column + wy - radio
                if marca == gen.MARK_CUE:
                    cue = round(float(ch[1, wx, wy]), 2)
                elif marca == gen.MARK_DOOR and columna == self.column:
                    arriba = arriba or fila == gen.ROW_CUE
                    abajo = abajo or fila == gen.ROW_ALT
        self.core.perceive(cue)
        self._doors_here = arriba and abajo

    def decide(self) -> Action:
        self.step += 1
        if self._doors_here:
            lado = self.core.decide(self._rng)
            self._pending = lado
            self.decisions.append((self.step - 1, lado))
            self._doors_here = False
            return Action(ActionType.CONSUME,
                          Direction.UP if lado == UP else Direction.DOWN)
        self.column += 1
        return Action(ActionType.MOVE, Direction.RIGHT)

    def learn(self, transition: Any) -> None:
        """Sólo aprende de la decisión que acaba de tomar, y sólo del delta."""
        if self._pending is None:
            return
        self.core.learn(self._pending, feedback_of(transition))
        self._pending = None

    def offer_targets(self, targets: Any) -> None:
        pass

    def get_internal_state(self) -> dict:
        return {"mode": self.core.mode.value}
