"""Las medidas del Nivel 1.2. Todas pasivas; casi todas cerradas.

**El modelo no se puntúa sobre el flujo con el que se entrenó.** Y no hace falta
un banco empírico adicional: las marginales del sensor están selladas, así que el
riesgo poblacional se calcula en cerrado. Eso elimina de golpe el ruido de banco,
el RNG de evaluación y la tentación de elegir el umbral después de mirar.

La única medida que usa azar es el envelope nulo de L12-6, y lo usa porque
`P(D|o)=0.5` es una **esperanza, no una identidad muestral**: el balance
factorial fija `P(D|G)` exactamente, pero los conteos de clase dentro de cada
observación fluctúan. Exigir igualdad exacta ahí sería exigir que no hubiera
azar.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from itertools import product

import numpy as np

from terrario.level11.cue import ALL_CUES, CueSemantics, CueToken
from terrario.level11.world import ALL_OBSERVATIONS, Direction, Observation
from terrario.level12.reference import (
    ALL_TOKENS, DELTA_NEAR, DistanceTruth, ProximityToken, marginal,
)

#: Sellados en `docs/LEVEL12_ORACULO_PREREGISTRADO.md`.
ORACLE = (1 / 11, 1 / 3, 2 / 3, 10 / 11)
BS_ORACLE = 8 / 55
BS_IGNORANT = 0.25
ACCURACY_ORACLE = 0.8
#: Derivado del oráculo sellado: `E[posible ∧ alineada] · BS* = (1/8)(8/55)`.
BS_JOINT_ORACLE = 1 / 55


# --- predicción de distancia --------------------------------------------------

def population_brier(predict_near) -> float:
    """`BS_pop = ½ Σ P(s|N)(H−1)² + ½ Σ P(s|F)H²`. Sin banco y sin RNG."""
    pn, pf = marginal(DistanceTruth.NEAR), marginal(DistanceTruth.FAR)
    total = 0.0
    for k, s in enumerate(ALL_TOKENS):
        h = predict_near(s)
        total += 0.5 * pn[k] * (h - 1.0) ** 2 + 0.5 * pf[k] * h ** 2
    return total


def max_oracle_deviation(predict_near) -> float:
    return max(abs(predict_near(s) - ORACLE[int(s)]) for s in ALL_TOKENS)


def confusion(predict_near) -> dict[tuple[DistanceTruth, DistanceTruth], float]:
    """Matriz de confusión poblacional. Filas: verdad. Columnas: decisión."""
    pn, pf = marginal(DistanceTruth.NEAR), marginal(DistanceTruth.FAR)
    m = {(t, d): 0.0 for t in DistanceTruth for d in DistanceTruth}
    for k, s in enumerate(ALL_TOKENS):
        decision = (DistanceTruth.NEAR if predict_near(s) >= 0.5
                    else DistanceTruth.FAR)
        m[(DistanceTruth.NEAR, decision)] += 0.5 * pn[k]
        m[(DistanceTruth.FAR, decision)] += 0.5 * pf[k]
    return m


def balanced_accuracy(predict_near) -> float:
    m = confusion(predict_near)
    sens = m[(DistanceTruth.NEAR, DistanceTruth.NEAR)] / 0.5
    spec = m[(DistanceTruth.FAR, DistanceTruth.FAR)] / 0.5
    return (sens + spec) / 2


# --- integración --------------------------------------------------------------

@dataclass(frozen=True)
class SingleVariableProbe:
    """Cuánto se mueve cada factor cuando se interviene en una sola entrada.

    Los ceros tienen que ser **exactos**: un factor que se mueve cuando varía una
    entrada que no le pertenece es `PREVIOUS_KNOWLEDGE_MUTATED`.
    """

    by_input: dict[str, dict[str, float]]

    def zeros_exact(self, tol: float = 0.0) -> bool:
        b = self.by_input
        return (b["o"]["Q"] <= tol and b["o"]["H"] <= tol
                and b["g"]["B"] <= tol and b["g"]["H"] <= tol
                and b["s"]["B"] <= tol and b["s"]["Q"] <= tol)


def single_variable_probe(agent) -> SingleVariableProbe:
    ejes = {"o": ALL_OBSERVATIONS, "g": ALL_CUES, "s": ALL_TOKENS}
    salida: dict[str, dict[str, float]] = {}
    for var, valores in ejes.items():
        d = {"B": 0.0, "Q": 0.0, "H": 0.0}
        for a, o, g, s in product(Direction, ALL_OBSERVATIONS, ALL_CUES, ALL_TOKENS):
            if var == "o" and o != ALL_OBSERVATIONS[0]:
                continue
            if var == "g" and g != ALL_CUES[0]:
                continue
            if var == "s" and s != ALL_TOKENS[0]:
                continue
            bs, qs, hs = [], [], []
            for v in valores:
                oo = v if var == "o" else o
                gg = v if var == "g" else g
                ss = v if var == "s" else s
                bs.append(agent.predict_body(oo, a))
                qs.append(agent.predict_orientation(gg, a))
                hs.append(agent.predict_near(ss))
            d["B"] = max(d["B"], max(bs) - min(bs))
            d["Q"] = max(d["Q"], max(qs) - min(qs))
            d["H"] = max(d["H"], max(hs) - min(hs))
        salida[var] = d
    return SingleVariableProbe(salida)


def joint_population_brier(agent, semantics: CueSemantics) -> tuple[float, float]:
    """Brier poblacional de `J_N` y `J_F` contra el indicador triple.

    `T_N = 1[movimiento posible] · 1[acción alineada] · 1[D=N]`, con la
    posibilidad tomada de la FÍSICA y no de la creencia del agente: si el cuerpo
    se equivoca, aquí se paga.
    """
    pn, pf = marginal(DistanceTruth.NEAR), marginal(DistanceTruth.FAR)
    acc_n = acc_f = 0.0
    casos = 0
    for o, g, a in product(ALL_OBSERVATIONS, ALL_CUES, Direction):
        posible = 1 - o[int(a)]
        alineada = int(a == semantics.direction_of(g))
        t = posible * alineada
        for k, s in enumerate(ALL_TOKENS):
            jn, jf = agent.predict_joint(o, g, s, a)
            acc_n += 0.5 * pn[k] * (jn - t) ** 2 + 0.5 * pf[k] * (jn - 0.0) ** 2
            acc_f += 0.5 * pn[k] * (jf - 0.0) ** 2 + 0.5 * pf[k] * (jf - t) ** 2
        casos += 1
    return acc_n / casos, acc_f / casos


# --- auditoría del generador ---------------------------------------------------

def direction_class_table(stream) -> dict[CueToken, float]:
    """`P(D = CERCA | g)`. Debe ser `0.5` EXACTO: el balance factorial lo fija."""
    conteo: dict[CueToken, list[int]] = defaultdict(lambda: [0, 0])
    for r in stream.records:
        conteo[r.view.cue][0 if r.truth is DistanceTruth.NEAR else 1] += 1
    return {c: v[0] / (v[0] + v[1]) for c, v in sorted(conteo.items())}


def body_association(stream) -> float:
    """`Σ_o n_o (p̂(N|o) − p̄)²`. Cuánta asociación `D↔o` hay en esta realización."""
    conteo: dict[Observation, list[int]] = defaultdict(lambda: [0, 0])
    for r in stream.records:
        conteo[r.view.observation][0 if r.truth is DistanceTruth.NEAR else 1] += 1
    total = sum(sum(v) for v in conteo.values())
    global_p = sum(v[0] for v in conteo.values()) / total
    return sum(sum(v) * (v[0] / sum(v) - global_p) ** 2 for v in conteo.values())


def body_association_envelope(stream, *, rng: np.random.Generator,
                              permutations: int = 10_000) -> np.ndarray:
    """Envelope nulo por permutación de `D` respecto del flujo de `o`.

    Se construye ANTES de mirar resultados y el criterio es su percentil 99.9.
    El umbral no se elige después de ver las ocho semillas.
    """
    obs = [r.view.observation for r in stream.records]
    etiquetas = np.array([r.truth is DistanceTruth.NEAR for r in stream.records])
    indice: dict[Observation, list[int]] = defaultdict(list)
    for i, o in enumerate(obs):
        indice[o].append(i)
    global_p = etiquetas.mean()
    fuera = np.empty(permutations)
    for p in range(permutations):
        barajadas = etiquetas[rng.permutation(len(etiquetas))]
        fuera[p] = sum(len(ix) * (barajadas[ix].mean() - global_p) ** 2
                       for ix in indice.values())
    return fuera


def delta_sensor_separation(stream) -> float:
    """`max_k |P̂(s|δ=1) − P̂(s|δ=2)|`. Cero si el sensor ignora la distancia.

    Es el contrato que convierte «el sensor depende de δ» en propiedad medida en
    vez de declaración. Sin él, la geometría volvería a ser decorativa.
    """
    conteo: dict[int, np.ndarray] = {d: np.zeros(4) for d in DELTA_NEAR}
    for r in stream.records:
        d = r.reference.delta
        if d in conteo:
            conteo[d][int(r.view.sensor)] += 1
    a, b = (conteo[d] / max(conteo[d].sum(), 1) for d in DELTA_NEAR)
    return float(np.abs(a - b).max())


def empirical_brier(predict_near, records) -> float:
    """Brier sobre registros concretos. **Sólo para fixtures.**

    El mundo nominal se puntúa con `population_brier`, que es cerrado. Pero una
    fixture cambia las marginales del sensor, y entonces las constantes selladas
    ya no describen su mundo: ahí hay que contar. No usar para los brazos.
    """
    total = 0.0
    for r in records:
        y = 1.0 if r.truth is DistanceTruth.NEAR else 0.0
        total += (predict_near(r.view.sensor) - y) ** 2
    return total / len(records)


class ContextualDistanceModel:
    """`H(s, g)`. Existe ÚNICAMENTE dentro de la fixture de factorización falsa.

    **No es un organismo.** Es la línea base que debe ganar cuando la igualdad
    `P(D|s,g) = P(D|s)` es falsa: sin ella, el gate composicional no podría
    rechazar nada y aprobaría por ausencia de prueba.
    """

    def __init__(self) -> None:
        self._belief: dict[tuple[ProximityToken, CueToken], list[float]] = {}

    def predict(self, sensor: ProximityToken, cue: CueToken) -> float:
        a, b = self._belief.get((sensor, cue), (1.0, 1.0))
        return a / (a + b)

    def observe(self, sensor: ProximityToken, cue: CueToken,
                target: DistanceTruth) -> None:
        key = (sensor, cue)
        if key not in self._belief:
            self._belief[key] = [1.0, 1.0]
        self._belief[key][0 if target is DistanceTruth.NEAR else 1] += 1
