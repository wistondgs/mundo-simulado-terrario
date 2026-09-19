#!/usr/bin/env python
"""EXPERIMENTO 2 · Agente de Nivel 1 · contingencia sensorimotora elemental.

Pregunta, y nada más que ésta:

    ¿Puede un ser descubrir, a partir de sus propios actos y de lo que le pasa
    después, qué efecto motor produce cada acción en cada situación sensorial?

No se prueba motivación, ni hambre, ni valencia, ni navegación, ni planificación.
Sólo `(o, a) → se movió`.

**Por qué es el experimento 2.** El 1 fue la implementación de referencia,
independiente del repositorio, corrida sin tocar nada. Éste es el mismo diseño
adaptado al proyecto: reutiliza `PairedResult` en vez de otro bootstrap, informa
los seis gates en vez de cuatro, y mide la conducta sobre situaciones idénticas
para todos los brazos. Los números del 1 quedan como referencia contra la que
comparar.

    python scripts/level1_sensorimotor_contingency.py --semillas 32
"""

from __future__ import annotations

import argparse
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.causal_bench import PairedResult  # noqa: E402
from terrario.level1.measurement import (  # noqa: E402
    Experiment, brier, motor_babbling, movement_rate,
    movement_rate_along_trajectory, situation_bank,
)
from terrario.level1.models import (  # noqa: E402
    ContingencyTable, FactoredContingency, TabularQ, oracle_policy,
)
from terrario.level1.world import ALL_OBSERVATIONS  # noqa: E402

BASE_SEED = 20260919
EVAL_OFFSET = 20_000_003
SHUFFLE_OFFSET = 10_000_003

#: Cuatro de las dieciséis, retiradas del entrenamiento. Con ellas el GATE 3
#: deja de ser un gate vacío --que con un solo brazo sólo podía aprobar por
#: ausencia de prueba-- y pasa a ser el discriminador del experimento:
#:
#:     ¿la experiencia produjo una TABLA o produjo una REGLA?
#:
#: Las cuatro tienen salida, así que también sirven para medir conducta.
HELD_OUT = frozenset({(1, 0, 0, 0), (0, 1, 0, 0), (1, 1, 0, 0), (0, 0, 1, 1)})


@dataclass
class SeedResult:
    violations: int
    # --- adquisición con las dieciséis observaciones disponibles -------------
    brier_cases: float
    brier_features: float
    brier_frozen: float
    brier_permuted: float
    move_cases: float
    move_features: float
    move_frozen: float
    move_permuted: float
    move_td: float
    move_oracle: float
    traj_cases: float
    traj_frozen: float
    traj_permuted: float
    # --- el discriminador: entrenados SIN ver cuatro de las dieciséis --------
    held_brier_cases: float
    held_brier_features: float
    held_move_cases: float
    held_move_features: float
    held_move_td: float
    held_move_frozen: float
    held_move_oracle: float


def run_seed(cfg: Experiment, seed: int) -> SeedResult:
    stream, violations = motor_babbling(cfg, seed)
    kw = {"prior_alpha": cfg.prior_alpha, "prior_beta": cfg.prior_beta}

    cases = ContingencyTable(**kw)
    features = FactoredContingency(**kw)
    frozen = ContingencyTable(**kw, frozen=True)
    permuted = ContingencyTable(**kw)
    td = TabularQ(learning_rate=cfg.q_learning_rate, discount=cfg.q_discount)

    for tr in stream:
        cases.observe(tr.observation, tr.direction, tr.moved)
        features.observe(tr.observation, tr.direction, tr.moved)
        td.observe(tr)

    # Control negativo: la misma cantidad de experiencia y la misma marginal de
    # resultados, con la correspondencia (o,a) ↔ resultado destruida.
    shuffle_rng = np.random.default_rng(seed + SHUFFLE_OFFSET)
    outcomes = np.asarray([tr.moved for tr in stream], dtype=np.int8)
    shuffle_rng.shuffle(outcomes)
    for tr, moved in zip(stream, outcomes, strict=True):
        permuted.observe(tr.observation, tr.direction, int(moved))

    # El discriminador: los mismos seres, sin ver nunca cuatro observaciones.
    partial_cases = ContingencyTable(**kw)
    partial_features = FactoredContingency(**kw)
    partial_td = TabularQ(learning_rate=cfg.q_learning_rate, discount=cfg.q_discount)
    for tr in stream:
        if tr.observation in HELD_OUT:
            continue
        partial_cases.observe(tr.observation, tr.direction, tr.moved)
        partial_features.observe(tr.observation, tr.direction, tr.moved)
        partial_td.observe(tr)

    eval_seed = seed + EVAL_OFFSET
    # Dos bancos, y no son el mismo: la predicción se mide sobre TODAS las
    # situaciones --incluida la encerrada, que es la más rara y la peor
    # aprendida--; la conducta sólo sobre las que tienen salida.
    predict_bank = situation_bank(cfg, eval_seed, require_exit=False)
    act_bank = situation_bank(cfg, eval_seed, require_exit=True)
    held_bank = tuple(o for o in act_bank if o in HELD_OUT)

    return SeedResult(
        violations=violations,
        brier_cases=brier(cases, predict_bank)[0],
        brier_features=brier(features, predict_bank)[0],
        brier_frozen=brier(frozen, predict_bank)[0],
        brier_permuted=brier(permuted, predict_bank)[0],
        move_cases=movement_rate(cases.act, act_bank, eval_seed),
        move_features=movement_rate(features.act, act_bank, eval_seed),
        move_frozen=movement_rate(frozen.act, act_bank, eval_seed),
        move_permuted=movement_rate(permuted.act, act_bank, eval_seed),
        move_td=movement_rate(td.act, act_bank, eval_seed),
        move_oracle=movement_rate(oracle_policy, act_bank, eval_seed),
        traj_cases=movement_rate_along_trajectory(cases.act, cfg, eval_seed),
        traj_frozen=movement_rate_along_trajectory(frozen.act, cfg, eval_seed),
        traj_permuted=movement_rate_along_trajectory(permuted.act, cfg, eval_seed),
        held_brier_cases=brier(partial_cases, predict_bank, only=HELD_OUT)[0],
        held_brier_features=brier(partial_features, predict_bank, only=HELD_OUT)[0],
        held_move_cases=movement_rate(partial_cases.act, held_bank, eval_seed),
        held_move_features=movement_rate(partial_features.act, held_bank, eval_seed),
        held_move_td=movement_rate(partial_td.act, held_bank, eval_seed),
        held_move_frozen=movement_rate(frozen.act, held_bank, eval_seed),
        held_move_oracle=movement_rate(oracle_policy, held_bank, eval_seed),
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--semillas", type=int, default=32)
    args = parser.parse_args()

    cfg = Experiment(repetitions=args.semillas)
    rows = [run_seed(cfg, BASE_SEED + i) for i in range(args.semillas)]
    n = len(rows)

    def col(name: str) -> list[float]:
        return [float(getattr(r, name)) for r in rows]

    def mean(name: str) -> float:
        return statistics.fmean(col(name))

    def contrast(name: str, better: str, worse: str) -> PairedResult:
        return PairedResult(name, [w - b for b, w in zip(col(better), col(worse))])

    print("EXPERIMENTO 2 · contingencia sensorimotora del Agente de Nivel 1")
    print(f"  {n} semillas · {cfg.train_layouts}×{cfg.train_steps_per_layout} "
          f"pasos de actividad motora basal · mundos de prueba disjuntos\n")

    print("  ADQUISICIÓN — con las dieciséis situaciones disponibles")
    print("    Brier, más bajo mejor. Referencias analíticas:")
    print("      ignorante (siempre 1/2) = 0.250000     perfecto = 0.000000\n")
    print(f"    {'brazo':<26}{'Brier':>12}{'conducta':>12}{'trayectoria':>14}")
    print("    " + "-" * 64)
    for label, b, m, j in (
            ("aprende por casos", "brier_cases", "move_cases", "traj_cases"),
            ("aprende por rasgos", "brier_features", "move_features", None),
            ("congelado", "brier_frozen", "move_frozen", "traj_frozen"),
            ("permutado", "brier_permuted", "move_permuted", "traj_permuted"),
            ("td (techo externo)", None, "move_td", None),
            ("oráculo (techo físico)", None, "move_oracle", None)):
        bs = f"{mean(b):>12.6f}" if b else f"{'—':>12}"
        js = f"{mean(j):>14.4f}" if j else f"{'—':>14}"
        print(f"    {label:<26}{bs}{mean(m):>12.4f}{js}")

    print("\n\n  EL DISCRIMINADOR — los mismos seres, entrenados SIN ver cuatro")
    print("    de las dieciséis situaciones, y medidos sólo sobre esas cuatro.\n")
    print(f"    {'brazo':<26}{'Brier':>12}{'conducta':>12}")
    print("    " + "-" * 50)
    for label, b, m in (
            ("aprende por casos", "held_brier_cases", "held_move_cases"),
            ("aprende por rasgos", "held_brier_features", "held_move_features"),
            ("td (techo externo)", None, "held_move_td"),
            ("congelado", None, "held_move_frozen"),
            ("oráculo (techo físico)", None, "held_move_oracle")):
        bs = f"{mean(b):>12.6f}" if b else f"{'—':>12}"
        print(f"    {label:<26}{bs}{mean(m):>12.4f}")

    contrasts = {
        "GATE_1_ADQUISICION": contrast(
            "Brier: congelado − casos", "brier_cases", "brier_frozen"),
        "GATE_2_DEPENDENCIA_CAUSAL": contrast(
            "Brier: permutado − casos", "brier_cases", "brier_permuted"),
        "GATE_3_GENERALIZACION": contrast(
            "Brier retirado: casos − rasgos", "held_brier_features", "held_brier_cases"),
        "GATE_4_USO_CONDUCTUAL": PairedResult(
            "conducta: casos − congelado",
            [c - f for c, f in zip(col("move_cases"), col("move_frozen"))]),
        "GATE_5_CONTROL_POSITIVO": PairedResult(
            "conducta: td − congelado",
            [t_ - f for t_, f in zip(col("move_td"), col("move_frozen"))]),
        "GATE_6_USO_DE_LA_REGLA": PairedResult(
            "conducta retirada: rasgos − td",
            [r - t_ for r, t_ in zip(col("held_move_features"), col("held_move_td"))]),
    }

    print(f"\n\n  CONTRASTES PAREADOS  ·  n = {n}\n")
    print(f"    {'contraste':<34}{'media':>10}{'IC95%':>24}{'signo +':>10}")
    print("    " + "-" * 78)
    gates: dict[str, bool] = {}
    for gate, result in contrasts.items():
        lo, hi = result.bootstrap()
        gates[gate] = lo > 0.0
        print(f"    {result.name:<34}{result.mean:>+10.6f}"
              f"{f'[{lo:+.6f}, {hi:+.6f}]':>24}{result.positive_fraction:>10.0%}")

    violations = sum(r.violations for r in rows)
    oracle = mean("move_oracle")
    gates["GATE_0_INTEGRIDAD_FISICA"] = violations == 0 and abs(oracle - 1.0) < 1e-12
    print(f"\n  GATE 0 · contrato físico: {violations} violaciones en "
          f"{n * cfg.train_layouts * cfg.train_steps_per_layout} transiciones · "
          f"oráculo = {oracle:.6f}")

    print("\n  GATES\n")
    for gate in sorted(gates):
        print(f"    {gate:<32}{'PASA' if gates[gate] else 'FALLA'}")

    if not gates["GATE_0_INTEGRIDAD_FISICA"]:
        status = "FALLO_DE_MUNDO_O_INSTRUMENTO"
    elif not gates["GATE_5_CONTROL_POSITIVO"]:
        status = "CONTROL_POSITIVO_FALLIDO"
    elif all(gates.values()):
        status = "PASA"
    else:
        status = "FALLA"
    print(f"\n  ESTADO · {status}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
