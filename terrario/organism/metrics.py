"""Las medidas de la fusión · cerradas, sin banco empírico y sin RNG.

El Brier conjunto se integra sobre `D` y sobre `s | D` con las marginales
selladas del Nivel 1.2, igual que allí: sin ruido de banco, sin azar de
evaluación y exactamente comparable con las referencias analíticas.

La referencia no se elige: se **calcula** con cuerpo y orientación ideales y una
`H` dada. Con `H*` sale la tabla sellada; con la `H` del propio organismo sale la
referencia que aísla el error de `B` y `Q` del error de `H`.
"""

from __future__ import annotations

from fractions import Fraction as F
from itertools import product
from typing import Any, Callable

from terrario.level11.cue import ALL_CUES, CueSemantics
from terrario.level11.world import ALL_OBSERVATIONS, Direction, Observation
from terrario.level12.reference import ALL_TOKENS, DistanceTruth, marginal
from terrario.organism.agent import H_IGNORANTE, Q_IGNORANTE

#: Selladas en `docs/ORGANISM_FUSION_HM_01_PREREGISTRADO.md`, cuerpo y orientación ideales.
SEALED = {("ON", "ON"): float(F(1, 55)), ("ON", "OFF"): float(F(181, 3520)),
          ("OFF", "ON"): float(F(1, 32)), ("OFF", "OFF"): float(F(7, 128))}
SEALED_INTERACTION = float(F(69, 7040))
ORDEN = (("ON", "ON"), ("OFF", "ON"), ("ON", "OFF"), ("OFF", "OFF"))


def joint_population_brier(agent: Any, semantics: CueSemantics,
                           o_present: Observation, *,
                           skip_tick: bool = False) -> float:
    """`BS` de `J_N` contra `T_N = 1[posible]·1[alineada]·1[D=N]`.

    La posibilidad y la alineación se toman de la FÍSICA y del cue **presentado**,
    no de la creencia del agente: si el cuerpo se equivoca o la memoria pierde el
    token, aquí se paga.
    """
    pn, pf = marginal(DistanceTruth.NEAR), marginal(DistanceTruth.FAR)
    acc = 0.0
    casos = 0
    for o, g in product(ALL_OBSERVATIONS, ALL_CUES):
        agent.reset()
        agent.present(o_present, g)
        if not skip_tick:
            agent.tick()
        objetivo = semantics.direction_of(g)
        for a in Direction:
            t = (1 - o[int(a)]) * int(a == objetivo)
            for k, s in enumerate(ALL_TOKENS):
                jn, _ = agent.joint(o, s, a)
                acc += 0.5 * pn[k] * (jn - t) ** 2 + 0.5 * pf[k] * jn ** 2
            casos += 1
        agent.reset()
    return acc / casos


def ideal_reference(h_predict: Callable[[Any], float], semantics: CueSemantics,
                    *, use_h: bool, use_m: bool) -> float:
    """La misma cantidad con `B` y `Q` **ideales**. Con `H*` da la tabla sellada."""
    pn, pf = marginal(DistanceTruth.NEAR), marginal(DistanceTruth.FAR)
    acc = 0.0
    casos = 0
    for o, g in product(ALL_OBSERVATIONS, ALL_CUES):
        objetivo = semantics.direction_of(g)
        for a in Direction:
            m = 1 - o[int(a)]
            al = int(a == objetivo)
            q = al if use_m else Q_IGNORANTE
            t = m * al
            for k, s in enumerate(ALL_TOKENS):
                h = h_predict(s) if use_h else H_IGNORANTE
                jn = m * q * h
                acc += 0.5 * pn[k] * (jn - t) ** 2 + 0.5 * pf[k] * jn ** 2
            casos += 1
    return acc / casos


def interaction(tabla: dict[tuple[str, str], float]) -> float:
    """Mejora conjunta menos la suma de las mejoras individuales."""
    base = tabla[("OFF", "OFF")]
    return ((base - tabla[("ON", "ON")])
            - ((base - tabla[("ON", "OFF")]) + (base - tabla[("OFF", "ON")])))


def cue_observation_information(semantics: CueSemantics) -> float:
    """`I(G ; o_query)` sobre el banco enumerado. Cero por construcción: `o`
    recorre las dieciséis con independencia del cue."""
    from collections import Counter
    import math
    pares = [(g, o) for o in ALL_OBSERVATIONS for g in ALL_CUES]
    n = len(pares)
    pg, po, pgo = (Counter(g for g, _ in pares), Counter(o for _, o in pares),
                   Counter(pares))
    return sum((c / n) * math.log2((c / n) / ((pg[g] / n) * (po[o] / n)))
               for (g, o), c in pgo.items())
