#!/usr/bin/env python3
"""Aplicación MECÁNICA de la regla sellada en §10 + Enmienda 03.

No elige `T`. Recorre la escalera sellada en orden ascendente y reporta, peldaño
a peldaño, si (a), (b) y (c) se cumplen a la vez. El primero que las cumpla las
tres ES el presupuesto. Si ninguno, la cláusula de agotamiento decide.

Dieciséis vidas, las que §10 nombra. Márgenes PAREADOS: los brazos comparten
mundo, cableado, motor, banco y masa heredada.
"""
from __future__ import annotations

import sys

import numpy as np

sys.path.insert(0, ".")

from terrario.level18.life import live                      # noqa: E402

SEEDS = tuple(range(150000011, 150000027))      # las DIECISÉIS de §10
LADDER = (64, 256, 1024, 4096)                  # Enmienda 03 §3
ALIASING = 0.3427                               # §3 del oráculo


def main() -> None:
    print(f"=== regla sellada · {len(SEEDS)} vidas · escalera {LADDER} ===\n")
    rows = {t: [live(s, t) for s in SEEDS] for t in LADDER}

    print(f"{'T':>6} {'L(C17)':>8} {'L(FD1)':>8} {'L(FULL)':>8} {'L(ORAC)':>8} | "
          f"{'ΔL':>8} {'ΔL/0.3427':>10}")
    for t in LADDER:
        r = rows[t]
        m = lambda k: float(np.mean([x[k] for x in r]))
        delta = m("l_c17") - m("l_full")
        print(f"{t:>6} {m('l_c17'):>8.4f} {m('l_depth1'):>8.4f} {m('l_full'):>8.4f} "
              f"{m('l_oracle'):>8.4f} | {delta:>+8.4f} {delta/ALIASING:>10.3f}")

    print(f"\n=== (a) margen PAREADO sobre FIXED-DEPTH-1 · m_i = L(FD1)_i − L(FULL)_i ===\n")
    print(f"{'T':>6} {'media(m)':>10} {'sd(m)':>9} {'2·sd':>9} {'(a) 2sd':>9} | "
          f"{'2sd/√N':>9} {'(a) ES':>8} | {'gana':>6}")
    veredicto = {}
    for t in LADDER:
        r = rows[t]
        margins = np.array([x["l_depth1"] - x["l_full"] for x in r])
        mean, sd = float(margins.mean()), float(margins.std(ddof=1))
        literal = mean >= 2 * sd
        error = mean >= 2 * sd / np.sqrt(len(margins))
        wins = int((margins > 0).sum())
        veredicto[t] = {"a": literal, "a_es": error, "mean": mean, "sd": sd,
                        "wins": wins}
        print(f"{t:>6} {mean:>+10.4f} {sd:>9.4f} {2*sd:>9.4f} "
              f"{'CUMPLE' if literal else 'no':>9} | {2*sd/np.sqrt(len(margins)):>9.4f} "
              f"{'CUMPLE' if error else 'no':>8} | {wins:>3}/{len(margins)}")

    print(f"\n=== (b) saturación  y  (c) hambre de cobertura ===\n")
    print(f"{'T':>6} {'ΔL/0.3427':>10} {'(b)<0.90':>9} | {'hambre FULL':>12} "
          f"{'hambre FD1':>11} {'(c)':>8}")
    for t in LADDER:
        r = rows[t]
        m = lambda k: float(np.mean([x[k] for x in r]))
        fraction = (m("l_c17") - m("l_full")) / ALIASING
        hf, hd = m("hungry_full"), m("hungry_depth")
        veredicto[t]["b"] = fraction < 0.90
        veredicto[t]["c"] = hf <= hd
        print(f"{t:>6} {fraction:>10.3f} {'CUMPLE' if fraction < 0.90 else 'no':>9} | "
              f"{hf:>12.4f} {hd:>11.4f} {'CUMPLE' if hf <= hd else 'no':>8}")

    print(f"\n=== organización y coste ===\n")
    print(f"{'T':>6} {'activos':>8} {'máx':>6} {'ocupad':>7} {'splits':>7} "
          f"{'merges':>7} {'revert':>7} {'1er spl':>8} {'superv':>8} | "
          f"{'celdas':>9} {'upd/ep':>7} {'seg':>6}")
    for t in LADDER:
        r = rows[t]
        m = lambda k: float(np.mean([x[k] for x in r]))
        survivals = [v for x in r for v in x["survival"]]
        firsts = [x["first_split"] for x in r if x["first_split"] is not None]
        episodes = sum(x["splits"] for x in r)
        print(f"{t:>6} {m('states'):>8.1f} {m('max_states'):>6.1f} "
              f"{m('occupied'):>7.1f} {m('splits'):>7.1f} {m('merges'):>7.1f} "
              f"{m('reverted'):>7.1f} "
              f"{(np.mean(firsts) if firsts else float('nan')):>8.1f} "
              f"{(np.mean(survivals) if survivals else float('nan')):>8.1f} | "
              f"{m('cells_held'):>9,.0f} "
              f"{(sum(x['updates'] for x in r)/episodes if episodes else float('nan')):>7.1f} "
              f"{m('seconds'):>6.2f}")

    print(f"\n=== la regla, aplicada ===\n")
    elegido = None
    for t in LADDER:
        v = veredicto[t]
        todas = v["a"] and v["b"] and v["c"]
        print(f"  T={t:>5}  (a) {'sí' if v['a'] else 'NO':>2}  "
              f"(b) {'sí' if v['b'] else 'NO':>2}  (c) {'sí' if v['c'] else 'NO':>2}"
              f"   →  {'CUMPLE LAS TRES' if todas else 'descartado'}")
        if todas and elegido is None:
            elegido = t
    print()
    if elegido is None:
        print("  NINGÚN peldaño de la escalera cumple las tres.")
        print("  Enmienda 03 §3 · cláusula de agotamiento → un solo peldaño más: 16384")
    else:
        print(f"  MENOR T que cumple las tres:  T_18 = {elegido}")


if __name__ == "__main__":
    main()
