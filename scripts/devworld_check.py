#!/usr/bin/env python
"""D4 y D6 sobre el mundo de desarrollo, y el diagnóstico como referencia.

    python scripts/devworld_check.py --estaciones 512
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from terrario.lab import world_generator as diag          # noqa: E402
from terrario.devworld import exposure, instances         # noqa: E402
from terrario.devworld.kernel import MEMORY               # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--estaciones", type=int, default=512)
    ap.add_argument("--ventana", type=int, default=64)
    ap.add_argument("--semilla", type=int, default=0)
    a = ap.parse_args()

    w, ctrl = instances.twin(MEMORY, seed=a.semilla, stations=a.estaciones)

    print(f"MUNDO DE DESARROLLO · {w.describe()}\n")

    # --- D3, otra vez: el gemelo sigue siendo quirúrgico a esta escala
    diffs = instances.twin_difference(w, ctrl)
    non_cue = [d for d in diffs if "NO-CUE" in d or "canales" in d
               or "anchura" in d or "duración" in d or "reglas" in d
               or "número de objetos" in d]
    print(f"  D3 · gemelo: {len(diffs)} diferencias, {len(non_cue)} de ellas NO son "
          f"la columna del cue  ->  {'FALLA' if non_cue else 'PASA'}")

    # --- D4 · exposición
    e = exposure.measure(w)
    d0 = diag.world_for(["EPMEM-A1"], seed=a.semilla, stations=8)
    print(f"\n  D4 · EXPOSICIÓN")
    print(f"      {'':22}{'pasos':>8}{'eventos':>9}{'1 cada':>9}{'V_inc':>8}{'V_sol':>8}")
    print(f"      {'desarrollo':22}{e.steps:>8}{e.informative:>9}"
          f"{e.steps_per_event:>9.1f}{e.v_inc:>8}{e.v_sol:>8}")
    ds = {round(st.cue_values[0], 4) for st in d0.stations}
    print(f"      {'diagnóstico (EPMEM)':22}{d0.duration:>8}{len(d0.stations):>9}"
          f"{d0.duration/len(d0.stations):>9.1f}{len(d0.stations):>8}{len(ds):>8}")
    print(f"\n      V_sol es la cuenta que decide: situaciones distintas relevantes")
    print(f"      para la solución. V_inc puede crecer por variedad cosmética.")

    # --- D4 · saturación
    print(f"\n  D4 · SATURACIÓN · ventanas de {a.ventana} estaciones")
    print(f"      {'ventana':>8}{'rango':>14}{'nuevos V_sol':>14}{'acum':>7}"
          f"{'banda':>9}{'bits sobre z':>14}")
    wins = exposure.saturation(w, window=a.ventana)
    for win in wins:
        print(f"      {win.index:>8}{f'{win.first}-{win.last}':>14}{win.new_sol:>14}"
              f"{win.cum_sol:>7}{win.band:>9.4f}{win.rule_bits:>14.2f}")
    info = exposure.still_informative(wins)
    print(f"\n      ¿sigue llegando información sobre la REGLA en las ventanas")
    print(f"      tardías?  {'SI' if info else 'NO — el mundo se agotó'}")

    # --- D6 · fugas
    print(f"\n  D6 · PUERTA ANTIFUGA · I(Y ; N) contra nulo por barajado, 400 sorteos")
    print(f"      {'variable incidental':26}{'I obs':>9}{'nulo μ':>9}{'nulo p95':>10}{'':>8}")
    verdicts = exposure.leak_gate(w.stations, seed=a.semilla)
    for v in verdicts:
        print(f"      {v.variable:26}{v.mutual_information:>9.4f}{v.null_mean:>9.4f}"
              f"{v.null_p95:>10.4f}{'FUGA' if v.leaks else 'limpia':>8}")

    leaks = [v for v in verdicts if v.leaks]
    print(f"\n  ESTADO · D3 {'FALLA' if non_cue else 'PASA'} · "
          f"D4 {'PASA' if info else 'FALLA'} · D6 {'FALLA' if leaks else 'PASA'}")
    return 1 if (non_cue or leaks or not info) else 0


if __name__ == "__main__":
    raise SystemExit(main())
