#!/usr/bin/env python
"""EXPERIMENTO 3 · el ser propio contra un método externo ya probado.

Mismo mundo, misma experiencia, mismo instrumento, dos mecanismos de
aprendizaje. Nada más cambia, y ésa es toda la afirmación:

    el ser propio       experiencia → conteos Beta-Bernoulli
    el carril externo   experiencia → ejemplares, voto por vecino más próximo

Lo que se pregunta no es quién gana. El Brier final es una de siete columnas, y
la más fácil de malinterpretar: dos mecanismos que terminan iguales no son el
mismo resultado si uno llegó con treinta experiencias y el otro con ocho mil, o
si uno guarda sesenta y cuatro números y el otro ocho mil casos.

**«Propio» son dos seres, no uno.** El que aprende por casos y el que aprende
por rasgos difieren tanto entre sí como del carril externo, así que informar un
único «nuestro» escondería el resultado. Se contrastan los dos.

**Esto no es la campaña científica.** Es la comparación de integración: verifica
que los tres mecanismos son medibles bajo condiciones idénticas y produce la
primera ficha. Las diferencias pequeñas no son hallazgos.

    python scripts/level1_transfer_nearest_neighbor.py --semillas 8
"""

from __future__ import annotations

import argparse
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.causal_bench import PairedResult  # noqa: E402
from terrario.level1.comparison import (  # noqa: E402
    Cost, Generalisation, brier_by_pattern, checkpoints, counting_cost,
    exemplar_cost, learning_curve, n_star, seen_pairs,
)
from terrario.level1.external import NearestNeighborForwardModel  # noqa: E402
from terrario.level1.measurement import (  # noqa: E402
    Experiment, brier, motor_babbling, movement_rate, situation_bank,
)
from terrario.level1.models import (  # noqa: E402
    ContingencyTable, FactoredContingency, oracle_policy,
)

BASE_SEED = 20260919
EVAL_OFFSET = 20_000_003

#: Las mismas cuatro que retira el experimento 2, para que el contraste de
#: generalización se lea contra un resultado ya publicado y no contra otro
#: recorte inventado aquí.
HELD_OUT = frozenset({(1, 0, 0, 0), (0, 1, 0, 0), (1, 1, 0, 0), (0, 0, 1, 1)})

#: Puntos de lectura de la curva, DECLARADOS y no calibrados. `0.125` es la
#: mitad del camino desde la ignorancia analítica (`0.25`) hasta la perfección;
#: los otros dos son más exigentes. No hay criterio empírico que diga cuál es
#: «saber»: por eso se informan tres y no se elige uno.
THRESHOLDS = (0.125, 0.05, 0.01)

#: Los mecanismos comparables. El congelado y el permutado siguen siendo los
#: controles del banco; aquí entran para que la ficha tenga suelo.
ARMS = ("casos", "rasgos", "externo", "congelado", "permutado")


@dataclass
class SeedResult:
    brier: dict[str, float]
    move: dict[str, float]
    curve: dict[str, tuple[tuple[int, float], ...]]
    generalisation: dict[str, Generalisation]
    cost: dict[str, Cost]
    move_oracle: float
    violations: int
    stream_length: int


def _build(cfg: Experiment) -> dict[str, object]:
    kw = {"prior_alpha": cfg.prior_alpha, "prior_beta": cfg.prior_beta}
    return {
        "casos": ContingencyTable(**kw),
        "rasgos": FactoredContingency(**kw),
        "externo": NearestNeighborForwardModel(),
        "congelado": ContingencyTable(**kw, frozen=True),
    }


def run_seed(cfg: Experiment, seed: int, *, cost_repeats: int) -> SeedResult:
    stream, violations = motor_babbling(cfg, seed)
    eval_seed = seed + EVAL_OFFSET
    predict_bank = situation_bank(cfg, eval_seed, require_exit=False)
    act_bank = situation_bank(cfg, eval_seed, require_exit=True)

    # Adquisición: el mismo flujo, una vez, a todos.
    models = _build(cfg)
    for tr in stream:
        for model in models.values():
            model.observe(tr.observation, tr.direction, tr.moved)  # type: ignore[attr-defined]

    # Control negativo de contingencia: misma experiencia, correspondencia rota.
    import numpy as np
    permuted = ContingencyTable(prior_alpha=cfg.prior_alpha, prior_beta=cfg.prior_beta)
    outcomes = np.asarray([tr.moved for tr in stream], dtype=np.int8)
    np.random.default_rng(seed + 10_000_003).shuffle(outcomes)
    for tr, moved in zip(stream, outcomes, strict=True):
        permuted.observe(tr.observation, tr.direction, int(moved))
    models["permutado"] = permuted

    # Generalización: los mismos mecanismos entrenados SIN cuatro situaciones.
    partial_stream = [tr for tr in stream if tr.observation not in HELD_OUT]
    partial = _build(cfg)
    for tr in partial_stream:
        for model in partial.values():
            model.observe(tr.observation, tr.direction, tr.moved)  # type: ignore[attr-defined]
    seen = seen_pairs(partial_stream)

    marks = checkpoints(len(stream))
    builders = {
        "casos": lambda: ContingencyTable(prior_alpha=cfg.prior_alpha,
                                          prior_beta=cfg.prior_beta),
        "rasgos": lambda: FactoredContingency(prior_alpha=cfg.prior_alpha,
                                              prior_beta=cfg.prior_beta),
        "externo": NearestNeighborForwardModel,
    }

    return SeedResult(
        brier={a: brier(models[a], predict_bank)[0] for a in ARMS},  # type: ignore[arg-type]
        move={a: movement_rate(models[a].act, act_bank, eval_seed) for a in ARMS},  # type: ignore[attr-defined]
        curve={a: learning_curve(b, stream, predict_bank, marks)
               for a, b in builders.items()},
        generalisation={a: brier_by_pattern(partial[a], predict_bank, seen)  # type: ignore[arg-type]
                        for a in builders},
        cost={
            "casos": counting_cost(models["casos"], predict_bank, repeats=cost_repeats),
            "rasgos": counting_cost(models["rasgos"], predict_bank, repeats=cost_repeats),
            "externo": exemplar_cost(models["externo"], predict_bank, repeats=cost_repeats),
        },
        move_oracle=movement_rate(oracle_policy, act_bank, eval_seed),
        violations=violations,
        stream_length=len(stream),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--semillas", type=int, default=8)
    parser.add_argument("--repeticiones-coste", type=int, default=1,
                        help="pasadas del banco al cronometrar la predicción")
    args = parser.parse_args()

    cfg = Experiment(repetitions=args.semillas)
    rows = [run_seed(cfg, BASE_SEED + i, cost_repeats=args.repeticiones_coste)
            for i in range(args.semillas)]
    n = len(rows)
    mean = statistics.fmean

    print("EXPERIMENTO 3 · Agente de Nivel 1 propio contra vecino más próximo (externo)")
    print(f"  {n} semillas · {rows[0].stream_length} experiencias por semilla · "
          f"flujo compartido, un solo manoteo motor por semilla\n")
    print("  GATE 0 · contrato físico: "
          f"{sum(r.violations for r in rows)} violaciones · "
          f"oráculo = {mean([r.move_oracle for r in rows]):.6f}\n")

    print("  PREDICCIÓN Y CONDUCTA — con las dieciséis situaciones disponibles")
    print("    Brier, más bajo mejor. Ignorante = 0.250000, perfecto = 0.000000\n")
    print(f"    {'mecanismo':<26}{'Brier':>12}{'conducta':>12}")
    print("    " + "-" * 50)
    for arm in ARMS:
        print(f"    {arm:<26}{mean([r.brier[arm] for r in rows]):>12.6f}"
              f"{mean([r.move[arm] for r in rows]):>12.4f}")

    print("\n\n  CUÁNTO TARDA CADA UNO EN SABER — Brier contra experiencias vistas\n")
    marks = [m for m, _ in rows[0].curve["casos"]]
    print(f"    {'n':>8}" + "".join(f"{a:>14}" for a in rows[0].curve))
    print("    " + "-" * (8 + 14 * len(rows[0].curve)))
    for i, mark in enumerate(marks):
        cells = "".join(f"{mean([r.curve[a][i][1] for r in rows]):>14.6f}"
                        for a in rows[0].curve)
        print(f"    {mark:>8}{cells}")

    print(f"\n    n*(τ) · primera n con Brier ≤ τ. Umbrales declarados, no calibrados.\n")
    print(f"    {'τ':>8}" + "".join(f"{a:>14}" for a in rows[0].curve))
    print("    " + "-" * (8 + 14 * len(rows[0].curve)))
    for tau in THRESHOLDS:
        cells = ""
        for arm in rows[0].curve:
            reached = [n_star(r.curve[arm], tau) for r in rows]
            numeric = [x for x in reached if isinstance(x, int)]
            cells += (f"{statistics.fmean(numeric):>14.0f}"
                      if len(numeric) == len(reached) else f"{'NOT_REACHED':>14}")
        print(f"    {tau:>8.3f}{cells}")

    print("\n\n  GENERALIZACIÓN — entrenados sin ver cuatro de las dieciséis")
    print("    G-A: el par (o,a) ya apareció, el mundo es otro.")
    print("    G-B: el par nunca apareció. Sólo aquí se separan los sesgos.\n")
    g0 = rows[0].generalisation
    print(f"    {'mecanismo':<26}{'G-A Brier':>12}{'G-B Brier':>12}{'casos G-B':>12}")
    print("    " + "-" * 62)
    for arm in g0:
        print(f"    {arm:<26}"
              f"{mean([r.generalisation[arm].known_pattern for r in rows]):>12.6f}"
              f"{mean([r.generalisation[arm].novel_pattern for r in rows]):>12.6f}"
              f"{g0[arm].novel_count:>12}")

    print("\n\n  LO QUE CUESTA — medido, no supuesto\n")
    print(f"    {'mecanismo':<26}{'unidades':>12}{'bytes':>12}{'ns/consulta':>14}  unidad")
    print("    " + "-" * 78)
    for arm in rows[0].cost:
        c0 = rows[0].cost[arm]
        print(f"    {arm:<26}{mean([r.cost[arm].units for r in rows]):>12.0f}"
              f"{mean([r.cost[arm].payload_bytes for r in rows]):>12.0f}"
              f"{mean([r.cost[arm].nanoseconds_per_query for r in rows]):>14.0f}"
              f"  {c0.unit_name}")

    print(f"\n\n  CONTRASTES PAREADOS  ·  n = {n}")
    print("    Δ > 0 favorece al carril externo; Δ < 0 favorece al mecanismo propio.\n")
    print(f"    {'contraste':<34}{'media':>12}{'IC95%':>26}{'signo +':>10}")
    print("    " + "-" * 82)
    for label, own in (("Brier: casos − externo", "casos"),
                       ("Brier: rasgos − externo", "rasgos")):
        result = PairedResult(label, [r.brier[own] - r.brier["externo"] for r in rows])
        lo, hi = result.bootstrap()
        print(f"    {result.name:<34}{result.mean:>+12.6f}"
              f"{f'[{lo:+.6f}, {hi:+.6f}]':>26}{result.positive_fraction:>10.0%}")
    for label, own in (("G-B Brier: casos − externo", "casos"),
                       ("G-B Brier: rasgos − externo", "rasgos")):
        result = PairedResult(label, [r.generalisation[own].novel_pattern
                                      - r.generalisation["externo"].novel_pattern
                                      for r in rows])
        lo, hi = result.bootstrap()
        print(f"    {result.name:<34}{result.mean:>+12.6f}"
              f"{f'[{lo:+.6f}, {hi:+.6f}]':>26}{result.positive_fraction:>10.0%}")

    print("\n  Esta corrida verifica integración, no establece un hallazgo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
