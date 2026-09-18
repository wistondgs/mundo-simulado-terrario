#!/usr/bin/env python
"""¿Exige cada mundo generado la capacidad que dice exigir?

Para cada capacidad: el mundo exigente y su control, corridos por la semántica
compartida con tres oráculos guionizados —completo, sin la facultad que el
eje exige, y ese mismo amputado en el control—. El mundo exige la capacidad
si el completo resuelve, el amputado cae y el amputado resuelve el control.

    python scripts/world_demand_check.py
    python scripts/world_demand_check.py --semillas 12
    python scripts/world_demand_check.py --conjunto EPMEM-A1 PLAST-A1
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab import world_generator as gen  # noqa: E402
from terrario.lab import world_oracles as orc  # noqa: E402


def _f(x: float | None) -> str:
    return "    —" if x is None else f"{x:.3f}"


def matriz(semillas: int) -> int:
    print(f"EXIGENCIA DE LOS MUNDOS GENERADOS — {gen.SEMANTICS_VERSION} · {semillas} semillas\n")
    print(f"  {'capacidad':<10}{'eje':<13}{'facultad':<13}{'completo':<11}{'amputado':<11}{'amp/ctrl':<11}{'exige'}")
    print("  " + "-" * 72)
    fallan = []
    for cap in gen.DEMAND_OF:
        v = orc.verdict_for(cap, seeds=range(semillas))
        print(f"  {cap:<10}{v.axis:<13}{str(v.faculty):<13}{_f(v.full_on_demanding):<11}"
              f"{_f(v.ablated_on_demanding):<11}{_f(v.ablated_on_control):<11}"
              f"{'—' if v.demands is None else ('si' if v.demands else 'NO')}   n={v.n_decisions}")
        if v.demands is False:
            fallan.append(cap)
    print()
    print("  completo   = oráculo con todas las facultades, en el mundo exigente")
    print("  amputado   = sin la facultad que el eje exige, en el mundo exigente")
    print("  amp/ctrl   = ese mismo amputado en el control (eje apagado)")
    print("  exige      = completo ≥ .95 · amputado ≤ .70 · amp/ctrl ≥ .95")
    print("  UNC no tiene facultad guionizable: su eje se comprueba en el mundo, no en el oráculo.")
    if fallan:
        print(f"\n  NO exigen lo que declaran: {', '.join(fallan)}")
        return 1
    return 0


def conjunto(caps: list[str], semillas: int) -> int:
    d = gen.demand_for(caps)
    print(f"CONJUNTO {caps} → {gen.generate(d, seed=0).describe()}\n")
    facs = sorted({orc.FACULTY_OF_AXIS[gen.DEMAND_OF[c][0]] for c in caps} - {None})
    filas: dict[str, list[float | None]] = {"completo": []}
    for f in facs:
        filas[f"sin {f}"] = []
    for seed in range(semillas):
        w = gen.world_for(caps, seed=seed)
        filas["completo"].append(orc.life_score(w, orc.FULL, seed=seed).accuracy)
        for f in facs:
            filas[f"sin {f}"].append(orc.life_score(w, orc.without(f), seed=seed).accuracy)
    for nombre, xs in filas.items():
        vals = [x for x in xs if x is not None]
        print(f"  {nombre:<18}{_f(sum(vals) / len(vals) if vals else None)}")
    print("\n  El conjunto exige todas si 'completo' resuelve y cada 'sin …' cae.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--semillas", type=int, default=6)
    parser.add_argument("--conjunto", nargs="+", default=None, metavar="CAP")
    args = parser.parse_args()
    return conjunto(args.conjunto, args.semillas) if args.conjunto else matriz(args.semillas)


if __name__ == "__main__":
    raise SystemExit(main())
