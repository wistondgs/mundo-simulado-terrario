#!/usr/bin/env python3
"""`ORGANISM-FUSION-REMEMBERED-BINDING-01` · la campaña y sus diez gates."""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.level14.inherited import BaselineRegression  # noqa: E402
from terrario.remembered.experiment import O_PRESENT, run_seed  # noqa: E402
from terrario.remembered.metrics import (  # noqa: E402
    ORDEN, SEALED, SEALED_INTERACTION, interaction,
)

SEEDS = tuple(range(120000011, 120000019))


def mean(xs):
    xs = list(xs); return sum(xs) / len(xs)


def main() -> int:
    print("ORGANISM-FUSION-REMEMBERED-BINDING-01")
    print("  base 68d852d · B + Q + H + M + ψ · ninguna adquisición nueva")
    print(f"  o_present = {O_PRESENT} → tick → escena de DOS referencias")
    print("  consulta: ¿cuál es la proximidad de la referencia cuyo cue recordé?")

    reportes, excluidas = [], []
    for s in SEEDS:
        try:
            reportes.append(run_seed(s))
        except BaselineRegression as e:
            excluidas.append((s, str(e)))
    if not reportes:
        print("\n  ninguna semilla utilizable"); return 2

    print("\n  FACTORIAL · Brier conjunto de J_N\n")
    print(f"    {'M':>5}{'ψ':>5}{'medido':>12}{'sellado':>12}{'Δ':>12}")
    for k in ORDEN:
        m = mean(r.joint[k] for r in reportes)
        print(f"    {k[0]:>5}{k[1]:>5}{m:>12.6f}{SEALED[k]:>12.6f}{m - SEALED[k]:>+12.6f}")

    base = mean(r.joint[("OFF", "OFF")] for r in reportes)
    sm = base - mean(r.joint[("ON", "OFF")] for r in reportes)
    sp = base - mean(r.joint[("OFF", "ON")] for r in reportes)
    am = base - mean(r.joint[("ON", "ON")] for r in reportes)
    print("\n  DEPENDENCIA\n")
    print(f"    mejora sólo M        {sm:>12.6f}")
    print(f"    mejora sólo ψ        {sp:>12.6f}   ← cero exacto: ψ sin M no aporta")
    print(f"    mejora conjunta      {am:>12.6f}")
    print(f"    INTERACCIÓN          {am - (sm + sp):>12.6f}   "
          f"(sellada {SEALED_INTERACTION:.6f})")

    print("\n  INTEGRIDAD\n")
    print(f"    un solo núcleo, por identidad de objeto   {all(r.single_core for r in reportes)}")
    print(f"    cinco huellas idénticas pre/post          {all(r.lineage_intact for r in reportes)}")
    print(f"    memory.py byte-idéntico al blob           {all(r.memory_literal for r in reportes)}")
    print(f"    semántica de M verificada                 {all(r.memory_semantics for r in reportes)}")
    print(f"    C(ψ(x)|x) = 17/20 tras la fusión          {all(r.psi_intact for r in reportes)}")
    print(f"    invariancia a los 12 pares de portadores  {max(r.invariance for r in reportes):.1e}")
    print(f"    sin el tick, el brazo completo cae a      {mean(r.skip_tick for r in reportes):.6f}")

    if excluidas:
        print("\n  EXCLUIDAS\n")
        for s, mo in excluidas: print(f"    {s}  {mo}")

    print("\n  GATES\n")
    fallos = []
    for n in reportes[0].gates():
        mal = [r.seed for r in reportes if not r.gates()[n]]
        print(f"    {'PASA' if not mal else 'FALLA':<6}{n}" + (f"   {mal}" if mal else ""))
        if mal: fallos.append(n)
    print(f"\n  REMEMBERED_BINDING_STATUS = {'VERIFIED' if not fallos else 'FAILED'}")
    return 0 if not fallos else 1


if __name__ == "__main__":
    sys.exit(main())
