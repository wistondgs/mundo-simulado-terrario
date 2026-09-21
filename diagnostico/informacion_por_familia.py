#!/usr/bin/env python3
"""¿Cuánta situación hay en la historia de ACCIONES sola frente a (obs, acción)?

Es la medida que decide si «Z ignora la observación» es un detalle o la causa
raíz de LEARNER-18-v1. Situación verdadera como instrumento; el learner no la ve.
El estimador sesga a la baja con más contextos: se reporta el número de contextos
para que el lector lo vea.
"""
from __future__ import annotations

import sys
from collections import Counter

import numpy as np

sys.path.insert(0, ".")

from terrario.level16.motor import EndogenousMotor            # noqa: E402
from terrario.level16.temporal import OBSERVATION_INDEX       # noqa: E402
from terrario.level16.world import build_world, motor_stream  # noqa: E402
from terrario.level17.efference import ALL_COMMANDS           # noqa: E402
from terrario.level17.wiring import ActuatorWiring            # noqa: E402
from terrario.level18.life import situations                  # noqa: E402

STEPS = 60000
SEEDS = (150000011, 150000013, 150000015, 150000017, 150000019)
DEPTHS = (1, 2, 3, 4, 6)


def entropy(pairs) -> float:
    joint = Counter(pairs)
    marginal = Counter(y for y, _ in pairs)
    n = float(len(pairs))
    return -sum((c / n) * np.log(c / marginal[y]) for (y, _x), c in joint.items())


def main() -> None:
    print(f"=== información situacional por familia de historia · {STEPS} pasos · "
          f"{len(SEEDS)} mundos ===\n")
    print(f"{'k':>3} | {'H(C|A_k)':>9} {'ctx':>6} | {'H(C|OA_k)':>10} {'ctx':>7} | "
          f"{'H(C|O_k)':>9} {'ctx':>6} | {'H(C)':>7}")
    totals = {}
    for seed in SEEDS:
        grid = build_world(seed)
        wiring = ActuatorWiring.sampled(seed)
        motor = EndogenousMotor(motor_stream(seed))
        _ordered, index = situations(grid)
        trace, observation = [], grid.observe()
        for _ in range(STEPS):
            command = ALL_COMMANDS[int(motor.next())]
            situation = index[grid.position]
            _, following = grid.step(wiring.actuate(command))
            trace.append((situation, OBSERVATION_INDEX[observation],
                          ALL_COMMANDS.index(command)))
            observation = following
        base = entropy([(0, t[0]) for t in trace])
        for k in DEPTHS:
            def contexts(pick):
                return [(tuple(pick(trace[i - j]) for j in range(1, k + 1)),
                         trace[i][0]) for i in range(k, STEPS)]
            a = contexts(lambda t: t[2])
            oa = contexts(lambda t: (t[1], t[2]))
            o = contexts(lambda t: t[1])
            totals.setdefault(k, []).append(
                (entropy(a), len({x for x, _ in a}), entropy(oa),
                 len({x for x, _ in oa}), entropy(o), len({x for x, _ in o}), base))
    for k, rows in totals.items():
        m = np.mean(rows, axis=0)
        print(f"{k:>3} | {m[0]:>9.4f} {m[1]:>6.0f} | {m[2]:>10.4f} {m[3]:>7.0f} | "
              f"{m[4]:>9.4f} {m[5]:>6.0f} | {m[6]:>7.4f}")


if __name__ == "__main__":
    main()
