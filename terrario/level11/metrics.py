"""Cómo se mide el Nivel 1.1 · estratos antes que promedios.

El total sobre las 256 tripletas **no distingue mecanismos opuestos**: medido
analíticamente, BODY-ONLY, CUE-ONLY, FROZEN y un predictor que diga siempre cero
empatan los cuatro en `0.1250`, con perfiles de fallo inversos. Por eso la
métrica primaria es la balanceada sobre los tres estratos, y el total nunca se
reporta sin su referencia de siempre-cero al lado.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Sequence

import numpy as np

from terrario.level11.cue import ALL_CUES, CueSemantics, CueToken
from terrario.level11.world import ALL_OBSERVATIONS, Direction, Observation

Triple = tuple[Observation, CueToken, Direction]


def joint_truth(observation: Observation, cue: CueToken, action: Direction,
                semantics: CueSemantics) -> int:
    """`Z* = 1` si la acción es realizable **y** coincide con la referencia.

    Se calcula desde la física y desde la semántica del experimento, nunca
    comparando los índices de los dos enums.
    """
    target = semantics.direction_of(cue)
    realizable = observation[int(action)] == 0
    return int(realizable and action == target)


def stratum(observation: Observation, cue: CueToken, action: Direction,
            semantics: CueSemantics) -> str:
    target = semantics.direction_of(cue)
    if action != target:
        return "C"
    return "A" if observation[int(target)] == 0 else "B"


def all_triples() -> list[Triple]:
    return [(o, g, a) for o in ALL_OBSERVATIONS for g in ALL_CUES for a in Direction]


@dataclass(frozen=True)
class BrierReport:
    total: float
    a: float
    b: float
    c: float
    counts: dict[str, int]

    @property
    def balanced(self) -> float:
        """Primaria. Cada error conceptual pesa igual."""
        return (self.a + self.b + self.c) / 3


def brier(agent: Any, semantics: CueSemantics,
          triples: Sequence[Triple] | None = None) -> BrierReport:
    triples = list(triples) if triples is not None else all_triples()
    acc: dict[str, list[float]] = {"A": [], "B": [], "C": []}
    total: list[float] = []
    for o, g, a in triples:
        error = (agent.predict(o, g, a) - joint_truth(o, g, a, semantics)) ** 2
        total.append(error)
        acc[stratum(o, g, a, semantics)].append(error)
    mean = lambda xs: float(np.mean(xs)) if xs else float("nan")
    return BrierReport(mean(total), mean(acc["A"]), mean(acc["B"]), mean(acc["C"]),
                       {k: len(v) for k, v in acc.items()})


def actionable_pairs(semantics: CueSemantics) -> list[tuple[Observation, CueToken]]:
    """Situaciones donde la dirección indicada está libre.

    Sólo aquí existe una acción correcta de Nivel 1.1. En las bloqueadas no se
    puntúa conducta: elegir un desvío sería navegación, que es otra habilidad.
    """
    return [(o, g) for o in ALL_OBSERVATIONS for g in ALL_CUES
            if o[int(semantics.direction_of(g))] == 0]


def alignment_rate(agent: Any, semantics: CueSemantics,
                   rng: np.random.Generator) -> float:
    """`R_align`. **No es adaptación.**

    Es cumplimiento de una correspondencia direccional especificada por el
    experimentador. Ashby rechaza «responde correctamente a un estímulo» como
    definición de conducta adaptativa precisamente porque «correctamente» no
    significa nada salvo conformarse a lo que el experimentador espera.
    """
    pares = actionable_pairs(semantics)
    aciertos = sum(1 for o, g in pares
                   if agent.act(o, g, rng) == semantics.direction_of(g))
    return aciertos / len(pares) if pares else float("nan")


def alignment_rate_expected(agent: Any, semantics: CueSemantics) -> float:
    """`R_align` **en cerrado**, promediando el desempate en vez de sortearlo.

    Un brazo cuyas cuatro puntuaciones empatan --el congelado, el ignorante, el
    siempre-cero-- elige uniformemente entre los empatados, y muestrear esa
    elección mete ruido en una cantidad que es exactamente calculable. Medido:
    la versión muestreada devolvió `0.5000` para BODY-ONLY donde la esperanza es
    `0.4688`, y esa diferencia se habría leído como discrepancia con el oráculo.

    Las referencias no necesitan barra de error.
    """
    pares = actionable_pairs(semantics)
    if not pares:
        return float("nan")
    total = 0.0
    for o, g in pares:
        objetivo = semantics.direction_of(g)
        valores = [agent.predict(o, g, d) for d in Direction]
        maximo = max(valores)
        empatados = [d for d, v in zip(Direction, valores)
                     if np.isclose(v, maximo)]
        total += sum(1 for d in empatados if d == objetivo) / len(empatados)
    return total / len(pares)


@dataclass(frozen=True)
class FactorialProbe:
    """El 2×2 · intervención causal local, sin semillas.

        cue compatible / incompatible  ×  dirección libre / bloqueada

    Variar `g` con `o` fijo demuestra uso de la señal; variar `o` con `g` fijo
    demuestra uso del cuerpo. Es evidencia por situación, no un promedio.
    """

    cue_sensitivity: float
    body_sensitivity: float
    cells: dict[str, float]


def factorial_probe(agent: Any, semantics: CueSemantics) -> FactorialProbe:
    celdas: dict[str, list[float]] = {
        "libre_compatible": [], "libre_incompatible": [],
        "bloqueada_compatible": [], "bloqueada_incompatible": []}
    for o, g, a in all_triples():
        objetivo = semantics.direction_of(g)
        compat = "compatible" if a == objetivo else "incompatible"
        estado = "libre" if o[int(a)] == 0 else "bloqueada"
        celdas[f"{estado}_{compat}"].append(agent.predict(o, g, a))
    media = {k: float(np.mean(v)) if v else float("nan") for k, v in celdas.items()}

    # sensibilidad al cue: misma o y misma a, cue que la señala frente a cue que no
    cue_delta = media["libre_compatible"] - media["libre_incompatible"]
    # sensibilidad al cuerpo: mismo cue compatible, dirección libre frente a bloqueada
    body_delta = media["libre_compatible"] - media["bloqueada_compatible"]
    return FactorialProbe(cue_delta, body_delta, media)
