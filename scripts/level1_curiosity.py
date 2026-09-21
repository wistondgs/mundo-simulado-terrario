#!/usr/bin/env python
"""EXPERIMENTO 4 · ¿elegir qué probar cambia lo que se aprende?

El Nivel 1 entrega a todos los seres el mismo flujo de actividad motora basal.
Este ser no puede aprovechar eso: su mecanismo es que la sorpresa dirija la
acción, y con un flujo impuesto no hay nada que dirigir.

Por eso se corre en dos modos, y la diferencia entre ambos ES el resultado:

    auto-dirigido   él elige. La curiosidad actúa.
    flujo compartido  recibe el manoteo motor. La curiosidad no puede actuar,
                      aunque la tabla de interés siga calculándose.

El segundo es la ablación del primero, y aísla ELEGIR de PREDECIR: los dos
tienen el mismo sustrato de conteo, el mismo prior y la misma cantidad de
experiencia. Lo único que cambia es quién decide el acto.

Contra ellos, los seres que ya estaban, sobre los mismos mundos y semillas.
El contraste ya no es pareado por experiencia --no puede serlo-- y eso se
declara en vez de disimularse.

    python scripts/level1_curiosity.py --semillas 16
"""

from __future__ import annotations

import argparse
import statistics
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.causal_bench import PairedResult  # noqa: E402
from terrario.level1.curiosity import PredictiveCuriosity, self_directed_stream  # noqa: E402
from terrario.level1.measurement import (  # noqa: E402
    Experiment, brier, motor_babbling, movement_rate, situation_bank,
)
from terrario.level1.models import (  # noqa: E402
    ContingencyTable, FactoredContingency, oracle_policy,
)

BASE_SEED = 20260919
EVAL_OFFSET = 20_000_003

#: Las mismas cuatro que retira el experimento 2, para leer la generalización
#: contra un resultado ya publicado y no contra otro recorte inventado aquí.
HELD_OUT = frozenset({(1, 0, 0, 0), (0, 1, 0, 0), (1, 1, 0, 0), (0, 0, 1, 1)})


def run_seed(cfg: Experiment, seed: int) -> dict:
    kw = {"prior_alpha": cfg.prior_alpha, "prior_beta": cfg.prior_beta}
    shared, violations = motor_babbling(cfg, seed)

    cases, features = ContingencyTable(**kw), FactoredContingency(**kw)
    frozen = ContingencyTable(**kw, frozen=True)
    ablated = PredictiveCuriosity(**kw)          # mismo ser, sin poder elegir
    for tr in shared:
        cases.observe(tr.observation, tr.direction, tr.moved)
        features.observe(tr.observation, tr.direction, tr.moved)
        ablated.observe(tr.observation, tr.direction, tr.moved)

    curious = PredictiveCuriosity(**kw)
    own, own_violations = self_directed_stream(curious, cfg, seed)

    # Generalización: los mismos seres sin ver nunca cuatro situaciones.
    partial_cases = ContingencyTable(**kw)
    partial_curious = PredictiveCuriosity(**kw)
    for tr in shared:
        if tr.observation in HELD_OUT:
            continue
        partial_cases.observe(tr.observation, tr.direction, tr.moved)

    eval_seed = seed + EVAL_OFFSET
    predict_bank = situation_bank(cfg, eval_seed, require_exit=False)
    act_bank = situation_bank(cfg, eval_seed, require_exit=True)

    def cover(model):
        return model.visited_cells

    return {
        "violations": violations + own_violations,
        "brier_cases": brier(cases, predict_bank)[0],
        "brier_features": brier(features, predict_bank)[0],
        "brier_ablated": brier(ablated, predict_bank)[0],
        "brier_curious": brier(curious, predict_bank)[0],
        "brier_frozen": brier(frozen, predict_bank)[0],
        # Conducta con `exploit`: argmax q, el mismo eje que el resto del banco.
        "move_cases": movement_rate(cases.act, act_bank, eval_seed),
        "move_features": movement_rate(features.act, act_bank, eval_seed),
        "move_ablated": movement_rate(ablated.exploit, act_bank, eval_seed),
        "move_curious": movement_rate(curious.exploit, act_bank, eval_seed),
        "move_frozen": movement_rate(frozen.act, act_bank, eval_seed),
        "move_oracle": movement_rate(oracle_policy, act_bank, eval_seed),
        "cells_cases": cover(cases), "cells_ablated": cover(ablated),
        "cells_curious": cover(curious),
        "surprises_ablated": ablated.surprises,
        "surprises_curious": curious.surprises,
        "steps": len(shared),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--semillas", type=int, default=16)
    args = ap.parse_args()
    cfg = Experiment(repetitions=args.semillas)
    rows = [run_seed(cfg, BASE_SEED + i) for i in range(args.semillas)]
    n = len(rows)
    mean = lambda k: statistics.fmean(float(r[k]) for r in rows)  # noqa: E731

    print("EXPERIMENTO 4 · Nivel 1.2 · elegir qué probar")
    print(f"  {n} semillas · {rows[0]['steps']} experiencias por semilla\n")
    print(f"  GATE 0 · violaciones del contrato físico: {sum(r['violations'] for r in rows)}"
          f" · oráculo = {mean('move_oracle'):.6f}\n")

    print("  PREDICCIÓN Y CONDUCTA")
    print("    Brier más bajo mejor. Ignorante = 0.250000, perfecto = 0.000000\n")
    print(f"    {'ser':<34}{'Brier':>12}{'conducta':>12}{'celdas':>10}{'sorpresas':>12}")
    print("    " + "-" * 80)
    for label, b, m, c, s in (
            ("aprende por casos", "brier_cases", "move_cases", "cells_cases", None),
            ("aprende por rasgos", "brier_features", "move_features", None, None),
            ("curioso · flujo compartido", "brier_ablated", "move_ablated",
             "cells_ablated", "surprises_ablated"),
            ("curioso · AUTO-DIRIGIDO", "brier_curious", "move_curious",
             "cells_curious", "surprises_curious"),
            ("congelado", "brier_frozen", "move_frozen", None, None)):
        cs = f"{mean(c):>10.1f}" if c else f"{'—':>10}"
        ss = f"{mean(s):>12.1f}" if s else f"{'—':>12}"
        print(f"    {label:<34}{mean(b):>12.6f}{mean(m):>12.4f}{cs}{ss}")

    print(f"\n\n  CONTRASTES PAREADOS · n = {n}")
    print("    El de arriba es la pregunta: elegir contra no poder elegir,")
    print("    con el mismo sustrato y la misma cantidad de experiencia.\n")
    print(f"    {'contraste':<38}{'media':>12}{'IC95%':>26}{'signo +':>10}")
    print("    " + "-" * 86)
    for label, a, b in (
            ("Brier: compartido − auto-dirigido", "brier_ablated", "brier_curious"),
            ("Brier: casos − auto-dirigido", "brier_cases", "brier_curious"),
            ("conducta: auto-dirigido − casos", "move_curious", "move_cases"),
            ("celdas: auto-dirigido − compartido", "cells_curious", "cells_ablated")):
        res = PairedResult(label, [float(r[a]) - float(r[b]) for r in rows])
        lo, hi = res.bootstrap()
        print(f"    {res.name:<38}{res.mean:>+12.6f}"
              f"{f'[{lo:+.6f}, {hi:+.6f}]':>26}{res.positive_fraction:>10.0%}")

    print("\n  La comparación NO es pareada por experiencia: el auto-dirigido")
    print("  provoca la suya. Mismo mundo y misma semilla, distinto recorrido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
