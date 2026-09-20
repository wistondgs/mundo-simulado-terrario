"""Las medidas del Nivel 1.4 · enumeradas, cerradas y sin un solo RNG nuevo."""

from __future__ import annotations

import math
from collections import Counter
from fractions import Fraction as F
from typing import Any, Iterable

from terrario.level11.cue import ALL_CUES
from terrario.level12.reference import ALL_TOKENS
from terrario.level14.carriers import ALL_X, ALL_Y, Psi
from terrario.level14.scene import (
    BindingObservation, BindingTruth, DirectionItem, ProximityItem,
)

#: Sellados en `docs/LEVEL14_ORACULO_PREREGISTRADO.md`.
SEALED_C_OK = float(F(17, 20))
SEALED_P_CORRECT = float(F(289, 290))
SEALED_BS_FULL = float(F(1, 84100))
SEALED_BS_FLOOR = 0.25
SEALED_MSE_UNBOUND = 0.0650443832262014
SEALED_MSE_FULL = 3.093668643338949e-06


def probability_correct(agent: Any, scene: BindingObservation,
                        truth: BindingTruth) -> float:
    for asignacion, p in agent.bind(scene):
        if frozenset(asignacion.items()) == truth.pairs:
            return p
    return 0.0


def binding_brier(agent: Any, bank: Iterable[tuple]) -> float:
    """`(P(correcto) − 1)²` sobre un banco con paridad `A`/`B` exacta.

    Sin esa paridad sería un error cuadrático condicionado a que una de las dos
    asignaciones fuera la verdadera; con ella es el Brier.
    """
    bank = list(bank)
    return sum((probability_correct(agent, o, t) - 1.0) ** 2
               for o, t in bank) / len(bank)


def readout_mse(agent: Any, bank: Iterable[tuple]) -> float:
    """Error del perfil de proximidad ligado frente al que de verdad corresponde."""
    total, n = 0.0, 0
    for obs, verdad in bank:
        correcto = dict(verdad.pairs)
        perfil = agent.bound_near_profile(obs)
        for d, h in perfil.items():
            total += (h - agent.predict_near(correcto[d].sensor)) ** 2
            n += 1
    return total / n


def readout_reference(agent: Any, bank: Iterable[tuple], p_correct: float) -> float:
    """El mismo error en cerrado, con la `H` del propio organismo.

    Aísla el error de implementación del error heredado del Nivel 1.2, para no
    confundir calidad de 1.2 con calidad de 1.4.
    """
    total, n = 0.0, 0
    for obs, verdad in bank:
        correcto = dict(verdad.pairs)
        otros = {d: [p for p in obs.proximities if p is not correcto[d]]
                 for d in obs.directions}
        for d in obs.directions:
            if not otros[d]:
                continue
            delta = (agent.predict_near(correcto[d].sensor)
                     - agent.predict_near(otros[d][0].sensor))
            total += (delta * (1.0 - p_correct)) ** 2
            n += 1
    return total / n if n else 0.0


def _mutual_information(pairs: list[tuple]) -> float:
    n = len(pairs)
    px, py, pxy = (Counter(x for x, _ in pairs), Counter(y for _, y in pairs),
                   Counter(pairs))
    return sum((c / n) * math.log2((c / n) / ((px[x] / n) * (py[y] / n)))
               for (x, y), c in pxy.items())


def carrier_attribute_information(bank: Iterable[tuple], *, paired: bool = False
                                  ) -> tuple[float, float]:
    """`I(G ; X)` e `I(S ; Y)`. Cero en los DOS bancos, o el portador sería
    una etiqueta de atributo."""
    gx, sy = [], []
    if paired:
        for d, p in bank:
            gx.append((d.cue, d.carrier)); sy.append((p.sensor, p.carrier))
    else:
        for obs, _ in bank:
            for d in obs.directions:
                gx.append((d.cue, d.carrier))
            for p in obs.proximities:
                sy.append((p.sensor, p.carrier))
    return _mutual_information(gx), _mutual_information(sy)


def index_binder_accuracy(ordered_bank: Iterable[tuple]) -> float:
    """Emparejar por posición. Sobre el banco ordenado debe dar exactamente ½."""
    bank = list(ordered_bank)
    aciertos = sum(
        int(frozenset(zip(e.directions, e.proximities)) == verdad.pairs)
        for e, verdad in bank)
    return aciertos / len(bank)


def three_factor_probe(agent: Any, bank: Iterable[tuple]) -> dict[str, dict[str, float]]:
    """Intervención de una sola variable. Los ceros deben ser exactos.

    Cada factor se mide de forma **invariante a la permutación de portadores**
    --suma sobre los elementos de la escena-- para que intervenir en el binding no
    mueva `H` de rebote: el intercambio conserva el multiconjunto de sensores.

    `C` no se mueve con ninguna de las tres, porque sólo depende de portadores y
    los portadores nunca cambian. Lo que distingue al binding es que mueve el
    **readout ligado** y nada más.
    """
    from terrario.level11.world import Direction

    obs, _ = list(bank)[0]
    ds = sorted(obs.directions, key=lambda d: d.carrier.value)
    ps = sorted(obs.proximities, key=lambda p: p.carrier.value)
    accion = Direction.UP

    def medir(escenas: list[BindingObservation]) -> dict[str, float]:
        q, h, c, r = [], [], [], []
        for e in escenas:
            d0 = sorted(e.directions, key=lambda d: d.carrier.value)[0]
            q.append(sum(agent.predict_orientation(d.cue, accion) for d in e.directions))
            h.append(sum(agent.predict_near(p.sensor) for p in e.proximities))
            c.append(sum(agent.association(d.carrier, p.carrier)
                         for d, p in zip(sorted(e.directions, key=lambda d: d.carrier.value),
                                         sorted(e.proximities, key=lambda p: p.carrier.value))))
            r.append(agent.bound_near_profile(e)[d0])
        rango = lambda v: max(v) - min(v)
        return {"Q": rango(q), "H": rango(h), "C": rango(c), "readout": rango(r)}

    variar_g = [BindingObservation(
        frozenset((DirectionItem(ds[0].carrier, g), ds[1])), obs.proximities)
        for g in ALL_CUES if g != ds[1].cue]
    variar_s = [BindingObservation(
        obs.directions, frozenset((ProximityItem(ps[0].carrier, s), ps[1])))
        for s in ALL_TOKENS if s != ps[1].sensor]
    variar_binding = [obs, BindingObservation(
        obs.directions,
        frozenset((ProximityItem(ps[0].carrier, ps[1].sensor),
                   ProximityItem(ps[1].carrier, ps[0].sensor))))]

    return {"g": medir(variar_g), "s": medir(variar_s),
            "binding": medir(variar_binding)}
