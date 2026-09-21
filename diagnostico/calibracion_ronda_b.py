#!/usr/bin/env python3
"""RONDA B · regla de la Enmienda 04, sobre la ventana virgen 190000011…

No elige nada: recorre la escalera sellada y reporta el primer peldaño que
cumpla las tres. Las condiciones son cotas inferiores PAREADAS, con la forma que
§7 línea 158 del oráculo ya había fijado — no se escoge método aquí.
"""
from __future__ import annotations

import sys

import numpy as np

sys.path.insert(0, ".")

from terrario.level18.life import live, situations                 # noqa: E402
from terrario.level16.world import build_world                     # noqa: E402

WINDOW_START = 190000011        # Enmienda 04 §5 · verificada virgen
NEEDED = 16
LADDER = (64, 256, 1024, 4096)
EXHAUSTION = 16384
ALIASING = 0.3427
Z95 = 1.96


def lcb(values) -> float:
    values = np.asarray(values, dtype=float)
    return float(values.mean() - Z95 * values.std(ddof=1) / np.sqrt(len(values)))


def seeds() -> tuple[int, ...]:
    """Consumo ascendente, sin saltos. Sólo una condición ESTRUCTURAL anterior a
    la vida provoca reemplazo: un mundo sin sitio donde moverse no es una vida."""
    chosen, candidate = [], WINDOW_START
    while len(chosen) < NEEDED:
        ordered, _index = situations(build_world(candidate))
        if len(ordered) >= 2:
            chosen.append(candidate)
        else:
            print(f"  semilla {candidate} descartada: mundo sin situaciones")
        candidate += 1
    return tuple(chosen)


def evaluate(rows) -> dict:
    margin = np.array([x["l_depth1"] - x["l_full"] for x in rows])
    oracle = np.array([x["l_c17"] - x["l_oracle"] for x in rows])
    delta = float(np.mean([x["l_c17"] - x["l_full"] for x in rows]))
    return {"m": float(margin.mean()), "m_lcb": lcb(margin), "m_sd": float(margin.std(ddof=1)),
            "wins": int((margin > 0).sum()), "delta": delta,
            "fraction": delta / ALIASING, "o_lcb": lcb(oracle),
            "a": lcb(margin) > 0, "b": delta / ALIASING < 0.90, "c": lcb(oracle) > 0}


def main() -> None:
    chosen = seeds()
    print(f"=== RONDA B · Enmienda 04 · {len(chosen)} vidas "
          f"{chosen[0]}…{chosen[-1]} ===\n")

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
    chosen_t = None
    for t in LADDER + (EXHAUSTION,):
        v = verdicts[t]
        all_three = v["a"] and v["b"] and v["c"]
        print(f"  T={t:>5}  (a) LCB95(m)>0 {'sí' if v['a'] else 'NO':>2}  "
              f"(b) <0.90 {'sí' if v['b'] else 'NO':>2}  "
              f"(c) LCB95(o)>0 {'sí' if v['c'] else 'NO':>2}"
              f"   →  {'CUMPLE LAS TRES' if all_three else 'descartado'}")
        if all_three and chosen_t is None and t in LADDER:
            chosen_t = t
    if chosen_t is None and verdicts[EXHAUSTION]["a"] and verdicts[EXHAUSTION]["b"] \
            and verdicts[EXHAUSTION]["c"]:
        chosen_t = EXHAUSTION
    print()
    if chosen_t is None:
        print("  NINGÚN peldaño cumple las tres, agotamiento incluido.")
        print("  Enmienda 04 §6 · SE DEJA DE MODIFICAR LA ESTADÍSTICA.")
    else:
        print(f"  MENOR T que cumple las tres:  T_18 = {chosen_t}")
        print(f"  (Enmienda 04 §4: la (a) v2 habría seleccionado 4096 en la Ronda A;"
              f" léase este resultado sabiéndolo.)")


if __name__ == "__main__":
    main()
