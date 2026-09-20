"""`python -m factory <orden>` · la contabilidad del linaje, consultable.

La fábrica no diseña, no sella y no interpreta. Contesta cuatro preguntas que
hoy se contestan releyendo cuatro documentos y acordándose de la conversación
en la que se dijeron.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from factory.catalog import Catalog
from factory.gates import reconcile
from factory.seeds import SeedRegistry
from factory.vacuity import scan


def _plan(args) -> int:
    c = Catalog.load(args.catalog) if args.catalog else Catalog.load()
    p = c.plan()
    nombre = lambda nid: c.nodes[nid].name

    print("VERIFICADO")
    for nid in p.done:
        n = c.nodes[nid]
        marca = f"{n.decimal:>4} " if n.decimal else "     "
        print(f" {marca}{nid:<22} {n.name}")

    print("\nLISTO · todas sus dependencias están verificadas en un solo árbol")
    for nid in p.ready:
        print(f"      {nid:<22} {nombre(nid)}")
    if not p.ready:
        print("      --")

    print("\nCOMPOSICIÓN PRIMERO · las dependencias existen, pero en árboles distintos")
    for nid, arboles in p.needs_composition.items():
        falta = sorted(set(c.nodes[nid].requires))
        print(f"      {nid:<22} {nombre(nid)}")
        print(f"      {'':<22} exige {falta}")
        print(f"      {'':<22} reunir {list(arboles)} · no consume decimal")
    if not p.needs_composition:
        print("      --")

    print("\nBLOQUEADO")
    for nid, faltan in p.blocked.items():
        print(f"      {nid:<22} falta {list(faltan)}")
    if not p.blocked:
        print("      --")

    huecos = c.gaps()
    if huecos:
        print("\nHUECOS DEL CICLO · estado declarado sin el artefacto que lo sostiene")
        for nid, sin in huecos.items():
            print(f"      {nid:<22} {list(sin)}")
    return 0


def _seeds(args) -> int:
    r = SeedRegistry.load()
    choques = r.collisions()
    print(f"{len(r.campaigns)} campañas · {len(r.used())} semillas registradas")
    for c in r.campaigns.values():
        print(f"      {c.id:<14} {c.size():>5}  {c.note}")
    print("\nCOLISIONES")
    if choques:
        for (a, b), comun in choques.items():
            print(f"      {a} ∩ {b} = {comun[:8]}{'…' if len(comun) > 8 else ''}")
    else:
        print("      ninguna")
    if args.reserve:
        inicio, fin = r.reserve(args.reserve)
        print(f"\nSIGUIENTE BLOQUE LIBRE de {args.reserve}: {inicio}…{fin - 1}")
    return 1 if choques else 0


def _gates(args) -> int:
    c = Catalog.load()
    objetivos = []
    if args.campaign:
        objetivos = [args.campaign]
    else:
        objetivos = [nid for nid, n in c.nodes.items() if n.gate_sources]
    fallo = 0
    for nid in objetivos:
        n = c.nodes[nid]
        if not n.gate_sources:
            print(f"{nid}: sin fuentes de gates declaradas")
            continue
        raiz = Path(n.worktree)
        rec = reconcile(raiz / n.gate_sources["oracle_doc"],
                        raiz / n.gate_sources["module"])
        print(f"### {nid} · {n.name}")
        print(rec.report())
        print()
        fallo |= 0 if rec.ok else 1
    return fallo


def _vacuity(args) -> int:
    hallazgos = []
    for ruta in args.paths:
        hallazgos.extend(scan(ruta, todos=args.all))
    for f in hallazgos:
        print(f)
    print(f"{len(hallazgos)} aserciones que no pueden fallar"
          if hallazgos else "ninguna aserción vacua")
    return 1 if any(f.kind != "self_comparison_call" for f in hallazgos) else 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="factory", description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("plan", help="qué está listo, qué exige componer antes")
    p.add_argument("--catalog", type=Path, default=None)
    p.set_defaults(fn=_plan)

    p = sub.add_parser("seeds", help="registro de semillas y colisiones")
    p.add_argument("--reserve", type=int, default=0,
                   help="propone el siguiente bloque libre de N semillas")
    p.set_defaults(fn=_seeds)

    p = sub.add_parser("gates", help="inventario sellado contra inventario evaluado")
    p.add_argument("--campaign", default=None)
    p.set_defaults(fn=_gates)

    p = sub.add_parser("vacuity", help="aserciones que no pueden fallar")
    p.add_argument("paths", nargs="+", type=Path)
    p.add_argument("--all", action="store_true",
                   help="incluye las informativas (f(g()) == f(g()))")
    p.set_defaults(fn=_vacuity)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    sys.exit(main())
