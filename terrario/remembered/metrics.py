"""Las medidas · enumeradas, cerradas y sin un solo RNG nuevo.

El banco se reduce a lo que de verdad mueve el número --observación, cue diana y
el par de sensores-- y hay un contrato aparte que comprueba lo que se ha dejado
fuera: los doce pares de portadores y los tres cues distractores dan **el mismo
resultado**. Reducir sin demostrar la invariancia sería elegir el banco después
de conocerlo.
"""

from __future__ import annotations

from itertools import product
from typing import Any

from terrario.level11.cue import ALL_CUES, CueSemantics
from terrario.level11.world import ALL_OBSERVATIONS, Direction, Observation
from terrario.level12.reference import (
    ALL_TOKENS, DistanceTruth, ProximityToken, marginal,
)
from terrario.level14.carriers import ALL_X, CANONICAL_PSI, Psi
from terrario.level14.scene import (
    BindingObservation, DirectionItem, ProximityItem,
)

#: Selladas en el preregistro, con cuerpo y orientación ideales.
#: Enmienda 1: la primera tabla ponderaba «alineada» al 1/2 en vez de al 1/4.
SEALED = {("ON", "ON"): 1345623 / 74008000, ("ON", "OFF"): 87 / 3520,
          ("OFF", "ON"): 747 / 14080, ("OFF", "OFF"): 747 / 14080}
SEALED_INTERACTION = 0.006533780131877635
ORDEN = (("ON", "ON"), ("ON", "OFF"), ("OFF", "ON"), ("OFF", "OFF"))


def build_scene(g_star, g_other, s_star, s_other, *, psi: Psi = CANONICAL_PSI,
                x_star=ALL_X[0], x_other=ALL_X[1]) -> BindingObservation:
    """Dos referencias. La diana lleva `g_star`; su proximidad es `s_star`."""
    return BindingObservation(
        frozenset((DirectionItem(x_star, g_star), DirectionItem(x_other, g_other))),
        frozenset((ProximityItem(psi[x_star], s_star),
                   ProximityItem(psi[x_other], s_other))))


def scene_bank(psi: Psi = CANONICAL_PSI, **kwargs) -> list:
    """`16 × 4 × 16 = 1024` consultas. `g'` se toma como el siguiente cue."""
    banco = []
    for o, g in product(ALL_OBSERVATIONS, ALL_CUES):
        g_otro = ALL_CUES[(int(g) + 1) % 4]
        for s1, s2 in product(ALL_TOKENS, ALL_TOKENS):
            banco.append((o, g, build_scene(g, g_otro, s1, s2, psi=psi, **kwargs),
                          s1, s2))
    return banco


def joint_population_brier(agent: Any, semantics: CueSemantics,
                           o_present: Observation, banco: list, *,
                           skip_tick: bool = False) -> float:
    """`BS` de `J_N` contra `T_N = 1[posible]·1[alineada con g*]·1[D* = N]`."""
    pn, pf = marginal(DistanceTruth.NEAR), marginal(DistanceTruth.FAR)
    pm = [(pn[k] + pf[k]) / 2 for k in range(4)]
    acc, triples = 0.0, 0
    for o, g, escena, s1, s2 in banco:
        agent.reset()
        agent.present(o_present, g)
        if not skip_tick:
            agent.tick()
        objetivo = semantics.direction_of(g)
        k, j = int(s1), int(s2)
        peso = pm[j]
        for a in Direction:
            t = (1 - o[int(a)]) * int(a == objetivo)
            jn, _ = agent.joint(o, escena, a)
            acc += peso * (0.5 * pn[k] * (jn - t) ** 2 + 0.5 * pf[k] * jn ** 2)
        agent.reset()
        triples += 4
    # La integración interna sobre (D, s*, s\') suma 1 por tripleta (o, g, a),
    # así que basta dividir por el número de tripletas.
    return acc / (triples / len(ALL_TOKENS) / len(ALL_TOKENS))


def interaction(tabla: dict) -> float:
    base = tabla[("OFF", "OFF")]
    return ((base - tabla[("ON", "ON")])
            - ((base - tabla[("ON", "OFF")]) + (base - tabla[("OFF", "ON")])))


def carrier_invariance(agent: Any, semantics: CueSemantics,
                       o_present: Observation, psi: Psi = CANONICAL_PSI) -> float:
    """Lo que el banco reducido deja fuera: los doce pares de portadores y los
    tres distractores deben dar el mismo número. Devuelve la dispersión."""
    valores = []
    for x1, x2 in ((a, b) for a in ALL_X for b in ALL_X if a is not b):
        banco = scene_bank(psi, x_star=x1, x_other=x2)[:64]
        valores.append(joint_population_brier(agent, semantics, o_present, banco))
    return max(valores) - min(valores)
