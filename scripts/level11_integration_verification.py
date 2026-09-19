#!/usr/bin/env python
"""`LEVEL1.1-INTEGRATION-VERIFICATION-01`

No es una campaña confirmatoria. Los resultados positivos están determinados por
la arquitectura que suministramos --COMPOSITE contra controles que sabemos
analíticamente que pierden información-- así que la pregunta es si la
implementación reproduce el mecanismo, no si funciona.

El oráculo está sellado en `docs/LEVEL11_ORACULO_PREREGISTRADO.md`. Ocho
realizaciones independientes lo comprueban. **Sin bootstrap, sin intervalos, sin
significancia**: ocho realizaciones no son una muestra poblacional.

    python scripts/level11_integration_verification.py
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.level11.experiment import MIN_INFORMATIVE, run_seed  # noqa: E402

SEEDS = range(70000019, 70000027)

#: Sellado antes de correr. `balanced` por brazo, con cuerpo y Q ideales.
ORACULO = {
    "COMPOSITE": 0.000, "BODY-ONLY": 0.125, "CUE-ONLY": 0.333,
    "FROZEN": 0.125, "SIEMPRE-CERO": 0.333, "IGNORANTE": 0.250,
}
ORACULO_ALIGN = {
    "COMPOSITE": 1.0000, "BODY-ONLY": 0.4688, "CUE-ONLY": 1.0000,
    "FROZEN": 0.4688, "SIEMPRE-CERO": 0.2500, "IGNORANTE": 0.2500,
}
TOLERANCIA = 0.02


def main() -> int:
    informes = [run_seed(s) for s in SEEDS]
    n = len(informes)
    brazos = list(informes[0].brier)
    media = lambda f: statistics.fmean(f(r) for r in informes)

    print("LEVEL1.1-INTEGRATION-VERIFICATION-01")
    print(f"  {n} realizaciones · semillas {SEEDS.start}…{SEEDS.stop - 1}")
    print("  sin bootstrap, sin intervalos: no es una muestra poblacional\n")

    print("  PREDICCIÓN · Brier por estrato. Primaria: balanced.")
    print("  A = acción del cue y libre · B = acción del cue y bloqueada · C = otra acción\n")
    print(f"    {'brazo':<14}{'total':>8}{'A':>8}{'B':>8}{'C':>8}"
          f"{'balanced':>10}{'oráculo':>9}{'Δ':>8}")
    print("    " + "-" * 73)
    desviaciones = []
    for b in brazos:
        bal = media(lambda r: r.brier[b].balanced)
        esperado = ORACULO.get(b)
        delta = f"{bal - esperado:+.3f}" if esperado is not None else "—"
        if esperado is not None:
            desviaciones.append(abs(bal - esperado))
        print(f"    {b:<14}{media(lambda r: r.brier[b].total):>8.4f}"
              f"{media(lambda r: r.brier[b].a):>8.3f}"
              f"{media(lambda r: r.brier[b].b):>8.3f}"
              f"{media(lambda r: r.brier[b].c):>8.3f}{bal:>10.3f}"
              f"{esperado if esperado is not None else float('nan'):>9.3f}{delta:>8}")
    print(f"\n    referencia obligatoria · siempre-cero en total = "
          f"{media(lambda r: r.brier['SIEMPRE-CERO'].total):.4f}")

    print("\n  CONDUCTA · R_align sobre estados accionables, en cerrado\n")
    print(f"    {'brazo':<14}{'medido':>9}{'oráculo':>9}{'Δ':>8}")
    print("    " + "-" * 40)
    for b in brazos:
        val = media(lambda r: r.alignment[b])
        esp = ORACULO_ALIGN.get(b)
        d = f"{val - esp:+.4f}" if esp is not None else "—"
        if esp is not None:
            desviaciones.append(abs(val - esp))
        print(f"    {b:<14}{val:>9.4f}"
              f"{esp if esp is not None else float('nan'):>9.4f}{d:>8}")

    print("\n  HOLDOUT · 16 pares (o,g) nunca vistos juntos\n")
    print(f"    {'brazo':<14}{'balanced':>10}")
    print("    " + "-" * 26)
    for b in ("COMPOSITE", "JOINT-TABLE", "FROZEN", "SHUFFLED"):
        print(f"    {b:<14}{media(lambda r: r.brier_holdout[b].balanced):>10.3f}")

    print("\n  PROBE 2×2 · intervención causal por situación\n")
    print(f"    {'brazo':<14}{'sensib. cue':>13}{'sensib. cuerpo':>16}")
    print("    " + "-" * 44)
    for b in informes[0].probe:
        print(f"    {b:<14}{media(lambda r: r.probe[b].cue_sensitivity):>13.3f}"
              f"{media(lambda r: r.probe[b].body_sensitivity):>16.3f}")

    cobertura = min(r.informative_minimum for r in informes)
    cuerpos = all(r.body_intact for r in informes)
    fisica = sum(r.physics_violations for r in informes)
    fugas = sum(r.holdout_violations for r in informes)
    peor = max(desviaciones)

    print(f"\n  INTEGRIDAD\n")
    print(f"    cobertura informativa mínima   {cobertura}  (criterio ≥ {MIN_INFORMATIVE})")
    print(f"    cuerpo intacto en las {n}         {cuerpos}")
    print(f"    violaciones del contrato       {fisica}")
    print(f"    fugas del holdout              {fugas}")
    print(f"    mayor desviación del oráculo   {peor:.4f}  (tolerancia {TOLERANCIA})")

    fallos = []
    if cobertura < MIN_INFORMATIVE:
        fallos.append("INSUFFICIENT_ORIENTATION_DOSE")
    if not cuerpos:
        fallos.append("BODY_MODEL_MUTATED")
    if fisica or fugas:
        fallos.append("MEASUREMENT_NOT_PASSIVE")
    if peor > TOLERANCIA:
        fallos.append("INTEGRATION_MODEL_MISMATCH")

    estado = "VERIFIED" if not fallos else " · ".join(fallos)
    print(f"\n  LEVEL11_STATUS = {estado}")
    return 0 if not fallos else 1


if __name__ == "__main__":
    raise SystemExit(main())
