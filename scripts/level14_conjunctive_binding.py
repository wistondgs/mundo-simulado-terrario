#!/usr/bin/env python3
"""`LEVEL1.4-CONJUNCTIVE-BINDING-01` · la campaña y sus gates.

    OMP_NUM_THREADS=2 python -u scripts/level14_conjunctive_binding.py

Oráculo sellado en `docs/LEVEL14_ORACULO_PREREGISTRADO.md` antes de existir este
guion. Ocho líneas base del Nivel 1.2; las 24 permutaciones de `ψ` son un
contrato de la suite, no una campaña: producen un solo valor distinto.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.level14.experiment import ORDEN, run_seed  # noqa: E402
from terrario.level14.inherited import BaselineRegression  # noqa: E402
from terrario.level14.metrics import (  # noqa: E402
    SEALED_BS_FLOOR, SEALED_BS_FULL, SEALED_MSE_FULL, SEALED_MSE_UNBOUND,
    SEALED_P_CORRECT,
)

SEEDS = tuple(range(100000011, 100000019))


def mean(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--semillas", type=int, default=len(SEEDS))
    args = p.parse_args()
    semillas = SEEDS[:args.semillas]

    print("LEVEL1.4-CONJUNCTIVE-BINDING-01")
    print(f"  base 7ac43fb · semillas {semillas[0]}…{semillas[-1]}")
    print("  banco de adquisición 64 · de evaluación 1728 · ordenado 6912")
    print(f"  sellados: P(correcto) = 289/290 = {SEALED_P_CORRECT:.9f} · "
          f"BS_FULL = 1/84100 = {SEALED_BS_FULL:.9f} · suelo = {SEALED_BS_FLOOR}")

    reportes, excluidas = [], []
    for s in semillas:
        try:
            reportes.append(run_seed(s))
        except BaselineRegression as e:
            excluidas.append((s, str(e)))

    if not reportes:
        print("\n  ninguna semilla utilizable")
        return 2

    print("\n  BINDING · mismos marginales, distinta relación\n")
    print(f"    {'brazo':<16}{'BS_binding':>14}{'Δ vs sellado':>15}"
          f"{'readout MSE':>14}{'ref H propia':>14}")
    for n in ORDEN:
        b = mean(r.brier[n] for r in reportes)
        sellado = SEALED_BS_FULL if n == "FULL_14" else (
            0.0 if n == "ORACLE" else SEALED_BS_FLOOR)
        print(f"    {n:<16}{b:>14.9f}{b - sellado:>+15.2e}"
              f"{mean(r.readout[n] for r in reportes):>14.6f}"
              f"{mean(r.readout_ref[n] for r in reportes):>14.6f}")
    print(f"\n    referencias con H* sellada: UNBOUND {SEALED_MSE_UNBOUND:.6f} · "
          f"FULL {SEALED_MSE_FULL:.3e}")

    print("\n  INTERVENCIÓN DE UNA SOLA VARIABLE\n")
    print(f"    {'se varía':<12}{'Q':>10}{'H':>10}{'C':>10}{'readout':>12}")
    for var in ("g", "s", "binding"):
        d = {k: mean(r.probe[var][k] for r in reportes) for k in ("Q", "H", "C", "readout")}
        print(f"    {var:<12}{d['Q']:>10.4f}{d['H']:>10.4f}{d['C']:>10.4f}"
              f"{d['readout']:>12.4f}")

    print("\n  EXCLUSIÓN DE ATAJOS E IDENTIDAD\n")
    print(f"    emparejar por índice (banco ordenado)   "
          f"{mean(r.index_accuracy for r in reportes):.4f}   (criterio 0.5)")
    print(f"    I(G;X), I(S;Y) en adquisición           "
          f"{max(r.info_acq for r in reportes)}")
    print(f"    I(G;X), I(S;Y) en evaluación            "
          f"{max(r.info_eval for r in reportes)}")
    print(f"    una sola referencia · BS de UNBOUND     "
          f"{mean(r.single_reference_brier for r in reportes):.4f}"
          f"   → no certifica binding")
    print(f"    huellas B/Q/H idénticas pre/post        "
          f"{all(r.lineage_intact for r in reportes)}")

    if excluidas:
        print("\n  EXCLUIDAS\n")
        for s, motivo in excluidas:
            print(f"    {s}  {motivo}")

    print("\n  GATES\n")
    fallos = []
    for nombre in reportes[0].gates():
        mal = [r.seed for r in reportes if not r.gates()[nombre]]
        print(f"    {'PASA' if not mal else 'FALLA':<6}{nombre}"
              + (f"   semillas {mal}" if mal else ""))
        if mal:
            fallos.append(nombre)

    print(f"\n  LEVEL14_STATUS = {'VERIFIED' if not fallos else 'FAILED'}")
    return 0 if not fallos else 1


if __name__ == "__main__":
    sys.exit(main())
