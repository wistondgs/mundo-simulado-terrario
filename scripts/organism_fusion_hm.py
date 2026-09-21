#!/usr/bin/env python3
"""`ORGANISM-FUSION-HM-01` · la campaña y sus gates.

    OMP_NUM_THREADS=2 python -u scripts/organism_fusion_hm.py

Preregistro sellado en `docs/ORGANISM_FUSION_HM_01_PREREGISTRADO.md` antes de
existir este guion. Ocho reconstrucciones; sin bootstrap y sin intervalos.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.organism.core import BaselineRegression  # noqa: E402
from terrario.organism.experiment import O_PRESENT, run_seed  # noqa: E402
from terrario.organism.metrics import (  # noqa: E402
    ORDEN, SEALED, SEALED_INTERACTION,
)

SEEDS = tuple(range(110000011, 110000019))


def mean(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--semillas", type=int, default=len(SEEDS))
    args = p.parse_args()

    print("ORGANISM-FUSION-HM-01")
    print(f"  base 7ac43fb · semillas {SEEDS[0]}…{SEEDS[:args.semillas][-1]}")
    print(f"  o_present = {O_PRESENT} → tick → o_query recorre las 16")
    print("  no hay adquisición nueva: sólo se reúnen capacidades verificadas")

    reportes, excluidas = [], []
    for s in SEEDS[:args.semillas]:
        try:
            reportes.append(run_seed(s))
        except BaselineRegression as e:
            excluidas.append((s, str(e)))

    if not reportes:
        print("\n  ninguna semilla utilizable")
        return 2

    print("\n  FACTORIAL · Brier poblacional conjunto de J_N\n")
    print(f"    {'H':>5}{'M':>5}{'medido':>12}{'ref H propia':>15}"
          f"{'sellado':>11}{'Δ vs sellado':>14}")
    for k in ORDEN:
        m = mean(r.joint[k] for r in reportes)
        print(f"    {k[0]:>5}{k[1]:>5}{m:>12.6f}"
              f"{mean(r.reference[k] for r in reportes):>15.6f}"
              f"{SEALED[k]:>11.6f}{m - SEALED[k]:>+14.6f}")

    base = mean(r.joint[("OFF", "OFF")] for r in reportes)
    solo_h = base - mean(r.joint[("ON", "OFF")] for r in reportes)
    solo_m = base - mean(r.joint[("OFF", "ON")] for r in reportes)
    ambas = base - mean(r.joint[("ON", "ON")] for r in reportes)
    inter = mean(r.measured_interaction for r in reportes)

    print("\n  INTERACCIÓN\n")
    print(f"    mejora sólo H                {solo_h:>12.6f}")
    print(f"    mejora sólo M                {solo_m:>12.6f}")
    print(f"    suma de las dos              {solo_h + solo_m:>12.6f}")
    print(f"    mejora conjunta              {ambas:>12.6f}")
    print(f"    INTERACCIÓN                  {inter:>12.6f}   "
          f"(sellada {SEALED_INTERACTION:.6f})")
    print(f"    razón conjunta / suma        {ambas / (solo_h + solo_m):>12.6f}")

    print("\n  INTEGRIDAD\n")
    print(f"    un solo núcleo, por identidad de objeto   "
          f"{all(r.single_core for r in reportes)}")
    print(f"    huellas B/Q/H idénticas pre/post          "
          f"{all(r.lineage_intact for r in reportes)}")
    print(f"    semántica de M verificada                 "
          f"{all(r.memory_semantics for r in reportes)}")
    print(f"    R_align idéntico pre/post                 "
          f"{all(r.align_before == r.align_after for r in reportes)}  "
          f"({reportes[0].align_before:.4f})")
    print(f"    I(G ; o_query)                            "
          f"{max(r.leakage for r in reportes):.4f} bits")
    print(f"    sin el tick, el brazo completo cae a      "
          f"{mean(r.skip_tick for r in reportes):.6f}   "
          f"(= el brazo sin memoria)")

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

    print("\n  FIXTURAS NEGATIVAS SELLADAS\n")
    for nombre in reportes[0].negative_fixtures():
        mal = [r.seed for r in reportes if not r.negative_fixtures()[nombre]]
        print(f"    {'CAE' if not mal else 'NO CAE':<6}{nombre}"
              + (f"   semillas {mal}" if mal else ""))
        if mal:
            fallos.append(nombre)

    print(f"\n  FUSION_STATUS = {'VERIFIED' if not fallos else 'FAILED'}")
    return 0 if not fallos else 1


if __name__ == "__main__":
    sys.exit(main())
