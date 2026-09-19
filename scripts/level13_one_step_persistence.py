#!/usr/bin/env python3
"""`LEVEL1.3-ONE-STEP-REFERENCE-PERSISTENCE-01` · la campaña y sus gates.

    OMP_NUM_THREADS=2 python -u scripts/level13_one_step_persistence.py

Oráculo sellado en `docs/LEVEL13_ORACULO_PREREGISTRADO.md` antes de existir este
guion. Ocho reconstrucciones del baseline 1.1; sin bootstrap y sin intervalos.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.level13.experiment import FLOOR, run_seed  # noqa: E402
from terrario.level13.inherited import BaselineRegression  # noqa: E402
from terrario.level13.metrics import memory_information  # noqa: E402
from terrario.level13.trials import O_PRESENT, O_QUERY  # noqa: E402

SEEDS = tuple(range(90000011, 90000019))
ORDEN = ("FULL_13", "PRESENT_CUE", "SHUFFLED_HISTORY", "NO_MEMORY",
         "FROZEN_13", "TICK_OMITIDO")


def mean(xs) -> float:
    xs = list(xs)
    return sum(xs) / len(xs)


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--semillas", type=int, default=len(SEEDS))
    args = p.parse_args()
    semillas = SEEDS[:args.semillas]

    print("LEVEL1.3-ONE-STEP-REFERENCE-PERSISTENCE-01")
    print(f"  base ef67ee5 · semillas {semillas[0]}…{semillas[-1]}")
    print(f"  o_present = {O_PRESENT}  →  tick  →  o_query = {O_QUERY}")
    print(f"  suelo sellado de toda política sin historia: {FLOOR}")

    reportes, excluidas = [], []
    for s in semillas:
        try:
            reportes.append(run_seed(s))
        except BaselineRegression as e:
            excluidas.append((s, f"LEVEL11_BASELINE_REGRESSION · {e}"))

    if not reportes:
        print("\n  ninguna semilla utilizable")
        return 2

    print("\n  USO DE LA HISTORIA · banco crítico, mismo presente\n")
    print(f"    {'brazo':<22}{'R_history':>11}{'vs suelo':>11}")
    for n in ORDEN:
        r = mean(x.rate[n] for x in reportes)
        print(f"    {n:<22}{r:>11.4f}{r - FLOOR:>+11.4f}")

    print("\n  CANAL TEMPORAL\n")
    f = mean(x.fidelity for x in reportes)
    print(f"    fidelidad del contenido  F_M        {f:.4f}")
    print(f"    información en memoria   I(G;M)     {memory_information(f):.4f} bits")
    print(f"    paridad de política      D_π        {max(x.parity for x in reportes):.1e}")
    print(f"    fuga del presente        I(G;o_q)   {max(x.leakage_query for x in reportes):.4f} bits")
    print(f"    fuga de la presentación  I(G;o_p)   {max(x.leakage_present for x in reportes):.4f} bits")

    print("\n  SONDA DEL PRESENTE · cue recordado fijo, cambia sólo o\n")
    print(f"    score con la dirección recordada LIBRE      "
          f"{mean(x.body['libre'] for x in reportes):.4f}")
    print(f"    score con la dirección recordada BLOQUEADA  "
          f"{mean(x.body['bloqueada'] for x in reportes):.4f}")
    print(f"    movimiento de Q al cambiar o                "
          f"{max(x.body['delta_q'] for x in reportes):.1e}")

    print("\n  INTEGRIDAD\n")
    print(f"    linaje 1.1 intacto en las {len(reportes)}       "
          f"{all(x.inherited_intact for x in reportes)}")
    print(f"    retención exacta en los 4 cues       "
          f"{all(x.retention_exact for x in reportes)}")
    print(f"    horizonte contenido tras 2 ticks     "
          f"{all(x.horizon_contained for x in reportes)}")
    print(f"    ensayos que empiezan EMPTY           "
          f"{min(x.reset_integrity for x in reportes):.2f}")
    print(f"    leer no consume                      "
          f"{all(x.memory_passive for x in reportes)}")

    if excluidas:
        print("\n  EXCLUIDAS\n")
        for s, motivo in excluidas:
            print(f"    {s}  {motivo}")

    print("\n  GATES\n")
    fallos = []
    for nombre in reportes[0].gates():
        mal = [x.seed for x in reportes if not x.gates()[nombre]]
        print(f"    {'PASA' if not mal else 'FALLA':<6}{nombre}"
              + (f"   semillas {mal}" if mal else ""))
        if mal:
            fallos.append(nombre)

    estado = "VERIFIED" if not fallos else "FAILED"
    print(f"\n  LEVEL13_STATUS = {estado}")
    return 0 if not fallos else 1


if __name__ == "__main__":
    sys.exit(main())
