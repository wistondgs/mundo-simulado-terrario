#!/usr/bin/env python3
"""RONDA C · misma regla v2, learner conforme, ventana nueva.

La regla NO se reescribe aquí: se IMPORTA de la Ronda B. Así «v2 intacta» es
estructural y no una afirmación. Lo único distinto es la ventana --sellada en la
Enmienda 07-- y el learner, ahora conforme con la Enmienda 02 desambiguada por
la Enmienda 06.
"""
from __future__ import annotations

import sys

import numpy as np

sys.path.insert(0, ".")

from diagnostico.calibracion_ronda_b import (                 # noqa: E402
    ALIASING, EXHAUSTION, LADDER, NEEDED, evaluate, lcb,
)
from terrario.level16.world import build_world                # noqa: E402
from terrario.level18.life import live, situations            # noqa: E402

WINDOW_START = 200000011          # Enmienda 07 §2 · verificada virgen


def seeds() -> tuple[int, ...]:
    chosen, candidate = [], WINDOW_START
    while len(chosen) < NEEDED:
        ordered, _index = situations(build_world(candidate))
        if len(ordered) >= 2:
            chosen.append(candidate)
        else:
            print(f"  semilla {candidate} descartada: mundo sin situaciones")
        candidate += 1
    return tuple(chosen)


def main() -> None:
    chosen = seeds()
    print(f"=== RONDA C · regla v2 IMPORTADA de la Ronda B · learner conforme ===")
    print(f"    {len(chosen)} vidas {chosen[0]}…{chosen[-1]}\n")

    verdicts = {}
    print(f"{'T':>6} {'L(C17)':>8} {'L(FD1)':>8} {'L(C18)':>8} {'L(ORAC)':>8} | "
          f"{'media(m)':>9} {'LCB95(m)':>9} {'gana':>6} | {'ΔL/.3427':>9} "
          f"{'LCB95(o)':>9}")
    for t in LADDER + (EXHAUSTION,):
        rows = [live(s, t) for s in chosen]
        v = evaluate(rows)
        verdicts[t] = v
        mean = lambda k: float(np.mean([x[k] for x in rows]))
        marker = "  ← agotamiento" if t == EXHAUSTION else ""
        print(f"{t:>6} {mean('l_c17'):>8.4f} {mean('l_depth1'):>8.4f} "
              f"{mean('l_full'):>8.4f} {mean('l_oracle'):>8.4f} | "
              f"{v['m']:>+9.4f} {v['m_lcb']:>+9.4f} {v['wins']:>3}/{len(chosen)} | "
              f"{v['fraction']:>9.3f} {v['o_lcb']:>+9.4f}{marker}")

    print(f"\n=== la regla v2, aplicada ===\n")
    picked = None
    for t in LADDER + (EXHAUSTION,):
        v = verdicts[t]
        three = v["a"] and v["b"] and v["c"]
        print(f"  T={t:>5}  (a) LCB95(m)>0 {'sí' if v['a'] else 'NO':>2}  "
              f"(b) <0.90 {'sí' if v['b'] else 'NO':>2}  "
              f"(c) LCB95(o)>0 {'sí' if v['c'] else 'NO':>2}"
              f"   →  {'CUMPLE LAS TRES' if three else 'descartado'}")
        if three and picked is None:
            picked = t
    print()
    if picked is None:
        print("  NINGÚN peldaño cumple las tres, agotamiento incluido.")
        print("  Enmienda 04 §6 · SE DEJA DE MODIFICAR LA ESTADÍSTICA.")
        print("  Enmienda 07 §4 · salida A · se vuelve al MECANISMO.")
    else:
        print(f"  MENOR T que cumple las tres:  T_18 = {picked}")


if __name__ == "__main__":
    main()
