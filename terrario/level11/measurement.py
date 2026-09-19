# ─────────────────────────────────────────────────────────────────────────────
# COPIA · Agente de Nivel 1.1
#
# Copiado literalmente de `terrario/level1/measurement.py` en `d278f59`, con el único
# cambio de la ruta del paquete. El comportamiento es idéntico por construcción:
# si estos ficheros divergieran del original, el 1.1 dejaría de heredar lo que el
# Experimento 1 demostró.
#
# **Por qué una copia y no un import.** El Nivel 1 está contaminado: sus semillas
# tienen resultados leídos, su desarme mecanístico miró la dirección del efecto, y
# el reversal vive en su mismo paquete. Importar de él ataría el linaje nuevo a
# esa historia; copiarlo lo separa de verdad, al precio de tener que mantener la
# equivalencia explícitamente.
# ─────────────────────────────────────────────────────────────────────────────

"""Cómo se mide al Agente de Nivel 1, y por qué así y no de la otra forma.

**La lección que traemos del banco de sondas.** Si cada brazo se mide sobre los
estados que su propia conducta le lleva a visitar, parte de la diferencia entre
brazos es desplazamiento de distribución y no conocimiento. Aquí los brazos
reciben **las mismas situaciones**, construidas del mundo y no de la historia.

Y no es una precaución teórica: medido sobre 8.015 situaciones y 8 semillas, el
protocolo importa para exactamente un brazo, y es el control negativo.

    brazo         trayectoria propia   situaciones iguales     delta
    aprendiz                  1.0000                1.0000   +0.0000
    congelado                 0.6042                0.6042   -0.0000
    permutado                 0.3072                0.6673   +0.3600
    td                        1.0000                1.0000   +0.0000
    oraculo                   1.0000                1.0000   +0.0000

El mecanismo: el permutado es DETERMINISTA dada la observación. Si para una
observación elige una dirección bloqueada, no se mueve, vuelve a ver lo mismo,
vuelve a elegir lo mismo, y queda atrapado. El azar no se atasca porque vuelve a
sortear. Un `0.254` leído como «el control cae por debajo del azar» estaría
midiendo la trampa, no la ausencia de conocimiento.

**Separación del azar.** El generador del mundo y el de la política son
distintos. Si comparten uno, cada brazo consume azar de forma distinta y las
situaciones dejan de ser las mismas a partir del primer paso -- que es el mismo
defecto por otra puerta.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Protocol, Sequence

import numpy as np

from terrario.level11.world import (
    Direction, Grid, Observation, Transition, physics_contract,
)

#: Una política es una función de la situación al acto. El azar que consuma es
#: suyo, nunca el del mundo.
Policy = Callable[[Observation, np.random.Generator], Direction]


class Predictor(Protocol):
    def predict(self, observation: Observation, direction: Direction) -> float: ...


@dataclass(frozen=True)
class Experiment:
    """Los parámetros del experimento. Todo declarado, nada dentro de una firma."""

    grid_size: int = 7
    wall_probability: float = 0.25
    train_layouts: int = 128
    train_steps_per_layout: int = 64
    test_layouts: int = 128
    test_positions_per_layout: int = 32
    repetitions: int = 32
    prior_alpha: float = 1.0
    prior_beta: float = 1.0
    q_learning_rate: float = 0.20
    q_discount: float = 0.90


# --- la experiencia -----------------------------------------------------------

def motor_babbling(cfg: Experiment, seed: int) -> tuple[list[Transition], int]:
    """Actividad motora basal: acciones uniformes, sin objetivo ni recompensa.

    No representa motivación. Es lo que genera experiencia antes de que exista
    nada que la dirija. Devuelve también cuántas transiciones violaron el
    contrato físico: es el GATE 0, y se cuenta en vez de lanzar, para que el
    experimento pueda informarlo como resultado y no como caída.
    """
    rng = np.random.default_rng(seed)
    stream: list[Transition] = []
    violations = 0
    for _ in range(cfg.train_layouts):
        grid = Grid.random(cfg.grid_size, cfg.wall_probability, rng)
        for _ in range(cfg.train_steps_per_layout):
            observation = grid.observe()
            direction = Direction(int(rng.integers(len(Direction))))
            moved, next_observation = grid.step(direction)
            if moved != physics_contract(observation, direction):
                violations += 1
            stream.append(Transition(observation, direction, moved, next_observation))
    return stream, violations


# --- el banco de situaciones --------------------------------------------------

def situation_bank(cfg: Experiment, seed: int, *,
                   require_exit: bool) -> tuple[Observation, ...]:
    """Las situaciones que verán TODOS los brazos, construidas del mundo.

    `require_exit` separa dos bancos que NO son el mismo y que conviene no
    confundir:

    - **conducta** (`True`): sólo situaciones con salida. Preguntarle a un ser
      encerrado si se mueve no distingue ningún brazo del otro.
    - **predicción** (`False`): todas. La situación encerrada `(1,1,1,1)` es la
      más rara del mundo y por tanto la peor aprendida; quitarla del Brier lo
      mejora sin que nadie haya aprendido nada. Medido: filtrar bajó el Brier del
      aprendiz de `0.000826` a `0.000070`, doce veces, por pura selección.

    Los mundos son distintos de los de adquisición porque se generan con otra
    semilla.
    """
    rng = np.random.default_rng(seed)
    bank: list[Observation] = []
    for _ in range(cfg.test_layouts):
        grid = Grid.random(cfg.grid_size, cfg.wall_probability, rng)
        for _ in range(cfg.test_positions_per_layout):
            grid.relocate(rng)
            observation = grid.observe()
            if require_exit and not any(bit == 0 for bit in observation):
                continue
            bank.append(observation)
    return tuple(bank)


# --- predicción ---------------------------------------------------------------

def brier(model: Predictor, bank: Sequence[Observation],
          *, only: frozenset[Observation] | None = None) -> tuple[float, int]:
    """`(1/N) Σ (predicho − ocurrido)²` sobre las cuatro direcciones de cada situación.

    El resultado es contrafactual: se evalúan las cuatro direcciones sin
    ejecutarlas, contra lo que la física produciría. Por eso la medida es pasiva
    y no altera nada.

    Referencias que no hay que estimar porque son analíticas: un predictor que
    siempre dice `1/2` da exactamente `0.25`; uno perfecto da `0`.
    """
    total, squared = 0, 0.0
    for observation in bank:
        if only is not None and observation not in only:
            continue
        for direction in Direction:
            actual = physics_contract(observation, direction)
            squared += (model.predict(observation, direction) - actual) ** 2
            total += 1
    return (squared / total if total else float("nan")), total


# --- conducta -----------------------------------------------------------------

def movement_rate(policy: Policy, bank: Sequence[Observation], seed: int) -> float:
    """Fracción de situaciones con salida en las que el acto elegido desplaza.

    Un acto por situación, y las situaciones son las mismas para todo brazo. El
    azar de la política sale de su propio generador.
    """
    rng = np.random.default_rng(seed)
    moved = sum(1 for o in bank if o[int(policy(o, rng))] == 0)
    return moved / len(bank)


def movement_rate_along_trajectory(policy: Policy, cfg: Experiment,
                                   seed: int) -> float:
    """La misma medida dejando que la política visite lo que ella provoque.

    Se conserva para poder informar la diferencia con `movement_rate`, no porque
    sea la medida buena: es la que convierte el control negativo en una trampa.
    """
    rng = np.random.default_rng(seed)
    moved_total = opportunities = 0
    for _ in range(cfg.test_layouts):
        grid = Grid.random(cfg.grid_size, cfg.wall_probability, rng)
        for _ in range(cfg.test_positions_per_layout):
            observation = grid.observe()
            has_exit = any(bit == 0 for bit in observation)
            if has_exit:
                opportunities += 1
            moved, _ = grid.step(policy(observation, rng))
            if has_exit:
                moved_total += moved
    if opportunities == 0:
        raise RuntimeError("ninguna situación de evaluación tenía salida")
    return moved_total / opportunities
