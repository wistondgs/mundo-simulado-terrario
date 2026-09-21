#!/usr/bin/env python
"""P1 — qué le falta a cada capacidad para poder certificarse.

`status_of` devuelve la PRIMERA condición que bloquea, que es lo correcto para un
gate: o pasa o no pasa. Pero para planificar hace falta lo contrario — saber
cuántas condiciones fallan y cuáles, porque una capacidad a la que sólo le falta
procedencia está mucho más cerca que otra a la que le falta procedencia, mundo,
instrumento y pureza.

Este comprobador evalúa las cinco condiciones de forma independiente y las
presenta como matriz. No sustituye al gate: lo hace planificable.

    python scripts/passport_check.py
    python scripts/passport_check.py --detalle HOMEO-A1
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.capability_passport import (  # noqa: E402
    REGISTRY, CapabilityPassport, PassportState, Purity, status_of,
)


def condiciones(passport: CapabilityPassport) -> dict[str, tuple[bool, str]]:
    """Las cinco, evaluadas por separado en vez de en cascada."""
    faltan = passport.missing()
    from terrario.lab import instrument_registry as registry

    endpoint_ok = registry.state_of(passport.primary_endpoint) in registry.REPORTABLE_STATES
    return {
        "contrato": (not faltan,
                     "completo" if not faltan else f"faltan {', '.join(faltan)}"),
        "procedencia": (bool(passport.corpus_provenance),
                        f"{len(passport.corpus_provenance)} fuente(s)"
                        if passport.corpus_provenance else "ninguna — L-1 incumplida"),
        "pureza": (passport.intervention_purity is Purity.PURE,
                   passport.intervention_purity.value),
        "mundo": (passport.demanding_world is not None,
                  passport.demanding_world or "ninguno lo exige"),
        "instrumento": (endpoint_ok,
                        passport.primary_endpoint if endpoint_ok
                        else f"{passport.primary_endpoint} no reportable"),
    }


def informe() -> int:
    print(f"PASAPORTES DE CAPACIDAD — {len(REGISTRY)} registrados\n")
    orden = ["contrato", "procedencia", "pureza", "mundo", "instrumento"]
    print(f"  {'capacidad':<13}{'concepto':<30}" + "".join(f"{c:<13}" for c in orden))
    print("  " + "-" * 108)

    faltantes: dict[str, int] = {c: 0 for c in orden}
    for cid, passport in REGISTRY.items():
        evaluado = condiciones(passport)
        celdas = ""
        for condicion in orden:
            cumple, _ = evaluado[condicion]
            celdas += f"{'si' if cumple else 'NO':<13}"
            if not cumple:
                faltantes[condicion] += 1
        print(f"  {cid:<13}{passport.concept_id[:29]:<30}{celdas}")

    print()
    for condicion in orden:
        n = faltantes[condicion]
        if n:
            print(f"  {condicion:<13} falla en {n} de {len(REGISTRY)}")

    listas = [c for c, p in REGISTRY.items()
              if status_of(p) is PassportState.READY_FOR_CERTIFICATION]
    print(f"\n  listas para certificar: {len(listas)} de {len(REGISTRY)}"
          + (f" — {', '.join(listas)}" if listas else ""))

    if faltantes["procedencia"] == len(REGISTRY):
        print("\n  Ninguna capacidad tiene procedencia al corpus. No es un descuido de")
        print("  redacción: `Concept.corpus_block` es un entero que ningún fichero lee.")
        print("  L-1 está incumplida por el catálogo entero, y hasta repararlo ninguna")
        print("  capacidad puede certificarse aunque todo lo demás pase.")
    return 0 if listas else 1


def detalle(capability_id: str) -> int:
    passport = REGISTRY.get(capability_id)
    if passport is None:
        print(f"no hay pasaporte {capability_id!r}; hay: {', '.join(REGISTRY)}")
        return 2
    print(f"{passport.capability_id} · {passport.concept_id}")
    print(f"  algoritmo   {passport.algorithm_id} {passport.algorithm_version}")
    print(f"  estado      {status_of(passport).value}\n")
    for condicion, (cumple, porque) in condiciones(passport).items():
        print(f"  [{'x' if cumple else ' '}] {condicion:<13} {porque}")
    print(f"\n  definición operacional\n      {passport.operational_definition}")
    print(f"\n  el mundo debe exigir\n      {passport.required_world_property}")
    print(f"\n  predicción negativa\n      {passport.negative_prediction}")
    if passport.known_confounders:
        print("\n  confusores conocidos")
        for confusor in passport.known_confounders:
            print(f"      {confusor}")
    if passport.notes:
        print(f"\n  notas\n      {passport.notes}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--detalle", default=None, help="un capability_id")
    args = parser.parse_args()
    return detalle(args.detalle) if args.detalle else informe()


if __name__ == "__main__":
    raise SystemExit(main())
