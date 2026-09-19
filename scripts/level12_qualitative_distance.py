#!/usr/bin/env python3
"""`LEVEL1.2-QUALITATIVE-DISTANCE-01` · la campaña y sus once gates.

    OMP_NUM_THREADS=2 python -u scripts/level12_qualitative_distance.py

Oráculo sellado en `docs/LEVEL12_ORACULO_PREREGISTRADO.md` antes de existir este
guion. Ocho realizaciones; sin bootstrap y sin intervalos, porque ocho
realizaciones no son una muestra poblacional: son ocho comprobaciones de que el
mecanismo se reproduce.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.level12.experiment import (
    BS_TOLERANCE, DEVIATION_TOLERANCE, run_seed,
)
from terrario.level12.inherited import BaselineRegression
from terrario.level12.metrics import (
    ACCURACY_ORACLE, BS_IGNORANT, BS_JOINT_ORACLE, BS_ORACLE, ORACLE,
)
from terrario.level12.stream import MIN_INFORMATIVE

SEEDS = tuple(range(80000011, 80000019))
ORDEN = ("FULL_12", "BAYES_ORACLE", "SENSOR_ONLY", "SHUFFLED_DISTANCE",
         "NO_DISTANCE", "FROZEN_DISTANCE")


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--semillas", type=int, default=len(SEEDS))
    args = p.parse_args()
    semillas = SEEDS[:args.semillas]

    print("LEVEL1.2-QUALITATIVE-DISTANCE-01")
    print(f"  semillas {semillas[0]}…{semillas[-1]}  ·  N = 2048  ·  "
          f"BS* = {BS_ORACLE:.6f}  ·  ignorante = {BS_IGNORANT:.3f}")
    print(f"  umbrales preregistrados: BS ≤ {BS_TOLERANCE}  ·  "
          f"max|Δ| ≤ {DEVIATION_TOLERANCE}  ·  cobertura ≥ {MIN_INFORMATIVE}")
    print(f"  oráculo H*(S0..S3) = " + "  ".join(f"{x:.6f}" for x in ORACLE))

    reportes = []
    excluidas = []
    for s in semillas:
        try:
            r = run_seed(s)
        except BaselineRegression as e:
            excluidas.append((s, f"LEVEL11_BASELINE_REGRESSION · {e}"))
            continue
        if r.informative_minimum < MIN_INFORMATIVE:
            excluidas.append((s, "INSUFFICIENT_DISTANCE_DOSE"))
            continue
        reportes.append(r)

    if not reportes:
        print("\n  ninguna semilla utilizable")
        return 2

    print("\n  PREDICCIÓN · Brier poblacional de distancia\n")
    print(f"    {'brazo':<20}{'BS_pop':>10}{'Δ vs BS*':>11}{'max|Δ_k|':>11}"
          f"{'bal.acc':>10}{'J_N':>11}")
    for n in ORDEN:
        bs = mean(r.brier[n] for r in reportes)
        print(f"    {n:<20}{bs:>10.6f}{bs - BS_ORACLE:>+11.6f}"
              f"{mean(r.deviation[n] for r in reportes):>11.4f}"
              f"{mean(r.balanced_acc[n] for r in reportes):>10.4f}"
              f"{mean(r.joint[n][0] for r in reportes):>11.6f}")
    print(f"\n    referencias analíticas: BS* = {BS_ORACLE:.6f} · "
          f"ignorante = {BS_IGNORANT:.6f} · Accuracy* = {ACCURACY_ORACLE:.2f} · "
          f"J_N* = {BS_JOINT_ORACLE:.6f}")

    print("\n  POSTERIORS · H(S_k) frente al oráculo sellado\n")
    print(f"    {'token':<8}{'H medido':>12}{'H*':>12}{'Δ':>11}")
    for k in range(4):
        h = mean(r.posteriors["FULL_12"][k] for r in reportes)
        print(f"    S{k:<7}{h:>12.6f}{ORACLE[k]:>12.6f}{h - ORACLE[k]:>+11.6f}")

    print("\n  INTEGRACIÓN · intervención de una sola variable\n")
    print(f"    {'brazo':<20}{'varía o':>22}{'varía g':>22}{'varía s':>22}")
    print(f"    {'':<20}{'B / Q / H':>22}{'B / Q / H':>22}{'B / Q / H':>22}")
    for n in ("FULL_12", "NO_DISTANCE", "SENSOR_ONLY"):
        fila = ""
        for var in ("o", "g", "s"):
            d = {k: mean(r.probe[n].by_input[var][k] for r in reportes)
                 for k in "BQH"}
            fila += f"{d['B']:>7.3f}{d['Q']:>7.3f}{d['H']:>8.3f}"
        print(f"    {n:<20}{fila}")

    print("\n  INTEGRIDAD\n")
    print(f"    linaje 1.1 intacto en las {len(reportes)}      "
          f"{all(r.inherited_intact for r in reportes)}")
    print(f"    R_align idéntico pre/post           "
          f"{all(r.motor_preserved for r in reportes)}  "
          f"({reportes[0].align_before:.4f})")
    print(f"    violaciones del contrato físico     "
          f"{sum(r.physics_violations for r in reportes)}")
    print(f"    cobertura informativa mínima        "
          f"{min(r.informative_minimum for r in reportes)}   (criterio ≥ {MIN_INFORMATIVE})")
    print(f"    P(CERCA | g) exacto en las {len(reportes)}      "
          f"{all(all(v == 0.5 for v in r.direction_table.values()) for r in reportes)}")
    print(f"    asociación D↔o dentro del envelope  "
          f"{all(r.body_stat <= r.body_envelope for r in reportes)}  "
          f"(máx {max(r.body_stat for r in reportes):.2f} vs "
          f"{min(r.body_envelope for r in reportes):.2f})")
    print(f"    separación sensor↔δ mínima          "
          f"{min(r.delta_separation for r in reportes):.4f}   (criterio ≥ 0.10)")

    if excluidas:
        print("\n  EXCLUIDAS\n")
        for s, motivo in excluidas:
            print(f"    {s}  {motivo}")

    print("\n  GATES\n")
    fallos = []
    for nombre in reportes[0].gates():
        ok = [r.seed for r in reportes if not r.gates()[nombre]]
        print(f"    {'PASA' if not ok else 'FALLA':<6}{nombre}"
              + (f"   semillas {ok}" if ok else ""))
        if ok:
            fallos.append(nombre)

    estado = "VERIFIED" if not fallos else "FAILED"
    print(f"\n  LEVEL12_STATUS = {estado}")
    if not fallos:
        peor = max(r.deviation["FULL_12"] for r in reportes)
        print(f"  mayor desviación del oráculo {peor:.4f} · "
              f"tolerancia {DEVIATION_TOLERANCE}")
        print(f"  peor BS_pop {max(r.brier['FULL_12'] for r in reportes):.6f} · "
              f"tolerancia {BS_TOLERANCE}")
    return 0 if not fallos else 1


def mean(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs)


if __name__ == "__main__":
    sys.exit(main())
