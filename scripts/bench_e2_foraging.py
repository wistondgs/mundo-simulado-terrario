#!/usr/bin/env python
"""E2 sobre el banco contrafactual · el primer protocolo de CAUSAL-CAPABILITY-BENCH-01.

Cinco fases y dos intervenciones causales:

    BIRTH        un organismo materializado, tres gemelos por `deepcopy`
    ACQUISITION  el mismo stream forzado para los tres; cada uno según su régimen
    FREEZE       `learning_enabled=False` para todos
    PROBE        examen autónomo con recurso no adyacente
    TRANSPLANT   un gemelo ingenuo recibe SÓLO los parámetros del aprendido
    RESTORE      al aprendido se le devuelven SÓLO los parámetros iniciales

La unidad estadística es el TRÍO, no la corrida. A0 queda fuera del
contrafactual --es otra arquitectura-- y sólo responde «¿mejor que el azar?».

Niveles de capacidad, y la conclusión nombra el máximo demostrado:

    F0 sin adquisición · F1 modelo adquirido · F2 persiste en probe congelado
    F3 lo adquirido CAUSA mejor conducta · F4 la experiencia se consigue sola

    python scripts/bench_e2_foraging.py --pares 16
"""

from __future__ import annotations

import argparse
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch  # noqa: E402
import torch.nn.functional as F_  # noqa: E402

from terrario.agent.agents import create_agent  # noqa: E402
from terrario.core.rng import RNGManager  # noqa: E402
from terrario.lab.causal_bench import (  # noqa: E402
    REGIME_INTERVENTIONS, BirthSnapshot, PairedResult, assert_birth_equivalence,
    restore_parameters, transplant_parameters, variance_components,
)
from terrario.world.transition import build_episode_components, run_step  # noqa: E402

sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from exp_adaptive_foraging_01 import (  # noqa: E402
    BASE, MAX_ENERGY, consume_advantage, force_action, live, planner_score_spread,
    rich_world, ring_world, _state_of,
)


@dataclass
class PairOutcome:
    pair_id: str
    consumes: dict[str, int]
    survived: dict[str, bool]
    advantage_before: dict[str, float]
    advantage_after: dict[str, float]
    tau_knowledge: dict[str, int | None]
    tau_behavior: dict[str, int | None]
    informative: int
    moved: dict[str, list[str]]


def acquire_with_tau(arm, stream, probe_scenario, *, sample_every: int = 25):
    """Adquisición, midiendo DÓNDE cruza la valoración de CONSUME sobre MOVE.

    `tau_knowledge` es el primer muestreo en que la ventaja se vuelve favorable
    y se queda. Separarlo de `tau_behavior` es lo que permite distinguir un
    cuello de aprendizaje de uno de utilización.
    """
    agent = arm.specimen
    before = consume_advantage(agent, _state_of(agent, probe_scenario))
    tau, stable_from = None, None
    for i, record in enumerate(stream):
        agent.adaptive_freeze.set_step(i)
        agent.perceive(record["observation"])
        agent.decide()
        force_action(agent, record["action_int"])
        agent.learn(record["transition"])
        if (i + 1) % sample_every == 0:
            advantage = consume_advantage(agent, _state_of(agent, probe_scenario))
            if advantage > 0:
                stable_from = i if stable_from is None else stable_from
            else:
                stable_from = None
    tau = stable_from
    after = consume_advantage(agent, _state_of(agent, probe_scenario))
    return before, after, tau


def run_pair(pair_id: str, seed: int, *, acquisition_steps: int,
             probe_distance: int) -> PairOutcome | None:
    # --- BIRTH ---------------------------------------------------------------
    birth = BirthSnapshot.materialize(pair_id, BASE, seed=seed)
    arms = birth.triplet()
    assert_birth_equivalence(arms)

    # --- stream informativo, uno solo para los tres --------------------------
    scenario = rich_world(seed, duration=acquisition_steps)
    comps = build_episode_components(scenario, duration_fallback=acquisition_steps,
                                     strict_physics=True, with_lifecycle=False,
                                     world_seed=seed)
    RNGManager.set_global_determinism(seed)
    recorder = create_agent("A4_ADVANCED", dict(BASE), seed=seed)
    stream, informative = [], 0
    for step in range(acquisition_steps):
        out = run_step(comps, recorder, step, world_seed=seed, agent_seed=seed,
                       max_steps=acquisition_steps, learning_enabled=True)
        stream.append({"observation": out.observation_t,
                       "action_int": out.action.to_int(), "transition": out.transition})
        if out.target is not None and out.effects and out.energy_delta > 0:
            informative += 1
        if out.terminated or out.truncated:
            break
    if informative == 0:
        return None

    probe_scenario = rich_world(seed, duration=10)
    before, after, tau = {}, {}, {}
    for name, arm in arms.items():
        b, a, t = acquire_with_tau(arm, stream, probe_scenario)
        before[name], after[name], tau[name] = b, a, t

    moved = {name: sorted(k for k, v in birth.digest.items()
                          if k.startswith("adaptive.")
                          and __import__("terrario.lab.causal_bench", fromlist=["x"])
                          .causal_state_digest(arm.specimen)[k] != v)
             for name, arm in arms.items()}

    # --- FREEZE + PROBE ------------------------------------------------------
    probe = ring_world(probe_distance, seed)
    consumes, survived, tau_b = {}, {}, {}
    for name, arm in arms.items():
        life = live(arm.specimen, probe, seed=seed, learning=False)
        consumes[name], survived[name] = life.effective_consumes, life.survived
        tau_b[name] = life.first_consume

    # --- TRANSPLANTE y RESTAURACIÓN -----------------------------------------
    graft = transplant_parameters(arms["NORMAL"], birth)
    life = live(graft.specimen, ring_world(probe_distance, seed), seed=seed, learning=False)
    consumes["TRANSPLANT"], survived["TRANSPLANT"] = life.effective_consumes, life.survived
    tau_b["TRANSPLANT"] = life.first_consume

    undone = restore_parameters(arms["NORMAL"], birth)
    life = live(undone.specimen, ring_world(probe_distance, seed), seed=seed, learning=False)
    consumes["RESTORE"], survived["RESTORE"] = life.effective_consumes, life.survived
    tau_b["RESTORE"] = life.first_consume

    RNGManager.set_global_determinism(seed)
    life = live(create_agent("A0_RANDOM", {}, seed=seed),
                ring_world(probe_distance, seed), seed=seed, learning=False)
    consumes["A0"], survived["A0"] = life.effective_consumes, life.survived
    tau_b["A0"] = life.first_consume

    return PairOutcome(pair_id, consumes, survived, before, after, tau, tau_b,
                       informative, moved)


def report(pairs: Sequence[PairOutcome]) -> int:
    names = ["NORMAL", "PARAMETRIC", "FULL", "TRANSPLANT", "RESTORE", "A0"]
    print(f"\n\nRESULTADO  ·  {len(pairs)} tríos contrafactuales\n")
    print(f"  {'brazo':<13}{'consumos media':>16}{'mediana':>10}"
          f"{'sobreviven':>13}{'1er consumo':>14}")
    print("  " + "-" * 68)
    for name in names:
        values = [p.consumes[name] for p in pairs]
        firsts = [p.tau_behavior[name] for p in pairs if p.tau_behavior[name] is not None]
        print(f"  {name:<13}{statistics.fmean(values):>16.2f}"
              f"{statistics.median(values):>10.1f}"
              f"{f'{sum(p.survived[name] for p in pairs)}/{len(pairs)}':>13}"
              f"{(f'{statistics.fmean(firsts):.0f}' if firsts else '—'):>14}")

    print("\n\n  ADQUISICIÓN INTERNA  ·  ventaja CONSUME − MOVE\n")
    print(f"  {'brazo':<13}{'antes':>12}{'después':>12}{'cruza a favorable':>22}")
    print("  " + "-" * 59)
    for name in ("NORMAL", "PARAMETRIC", "FULL"):
        b = statistics.fmean(p.advantage_before[name] for p in pairs)
        a = statistics.fmean(p.advantage_after[name] for p in pairs)
        crossed = sum(1 for p in pairs
                      if p.advantage_before[name] <= 0 < p.advantage_after[name])
        print(f"  {name:<13}{b:>+12.5f}{a:>+12.5f}{f'{crossed}/{len(pairs)}':>22}")

    print("\n\n  ESTADÍSTICA PAREADA  ·  la unidad es el trío\n")
    print(f"  {'estimando':<26}{'media':>9}{'mediana':>9}{'IC95%':>22}"
          f"{'signo +':>10}{'un par lo domina':>18}")
    print("  " + "-" * 96)
    verdicts = {}
    for label, left, right in (("Δ NORMAL − FULL", "NORMAL", "FULL"),
                               ("Δ PARAMETRIC − FULL", "PARAMETRIC", "FULL"),
                               ("Δ NORMAL − PARAMETRIC", "NORMAL", "PARAMETRIC"),
                               ("Δ TRANSPLANT − FULL", "TRANSPLANT", "FULL"),
                               ("Δ NORMAL − RESTORE", "NORMAL", "RESTORE"),
                               ("Δ NORMAL − A0", "NORMAL", "A0")):
        result = PairedResult(label, [float(p.consumes[left] - p.consumes[right])
                                      for p in pairs])
        lo, hi = result.bootstrap()
        verdicts[label] = (result, lo, hi)
        print(f"  {label:<26}{result.mean:>+9.2f}{result.median:>+9.1f}"
              f"{f'[{lo:+.2f}, {hi:+.2f}]':>22}"
              f"{result.positive_fraction:>10.0%}"
              f"{('SÍ' if result.dominated_by_one_pair else 'no'):>18}")

    components = variance_components({n: [float(p.consumes[n]) for p in pairs]
                                      for n in ("NORMAL", "PARAMETRIC", "FULL")})
    print(f"\n  varianza entre pares {components['between_pair']:.1f} · "
          f"dentro del par {components['within_pair']:.1f} · "
          f"fracción entre pares {components['between_fraction']:.1%}")

    # --- Nivel demostrado ----------------------------------------------------
    crossed = sum(1 for p in pairs
                  if p.advantage_before["NORMAL"] <= 0 < p.advantage_after["NORMAL"])
    f1 = crossed >= 0.8 * len(pairs)
    f2 = all("adaptive.parameters" in p.moved["NORMAL"] for p in pairs)
    nf, lo_nf, _ = verdicts["Δ NORMAL − FULL"]
    f3 = lo_nf > 0 and not nf.dominated_by_one_pair
    level = "F0"
    if f1:
        level = "F1"
    if f1 and f2:
        level = "F2"
    if f1 and f2 and f3:
        level = "F3"
    print(f"\n\n  NIVEL MÁXIMO DEMOSTRADO = {level}")
    print(f"    F1 modelo adquirido          {'sí' if f1 else 'no'}  "
          f"({crossed}/{len(pairs)} cruzan)")
    print(f"    F2 persiste al probe         {'sí' if f2 else 'no'}")
    print(f"    F3 causa mejor conducta      {'sí' if f3 else 'no'}  "
          f"(IC del estimando primario {'excluye' if lo_nf > 0 else 'incluye'} el cero)")
    print(f"    F4 adquisición autónoma      no evaluado en este protocolo (E2-C)")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pares", type=int, default=16)
    parser.add_argument("--pasos", type=int, default=300)
    parser.add_argument("--distancia", type=int, default=3)
    args = parser.parse_args()

    print(f"E2 sobre CAUSAL-CAPABILITY-BENCH-01 · {args.pares} tríos · "
          f"adquisición {args.pasos} pasos · probe a distancia {args.distancia}")
    pairs, skipped = [], 0
    for index in range(args.pares):
        outcome = run_pair(f"pair-{index:03d}", index,
                           acquisition_steps=args.pasos, probe_distance=args.distancia)
        if outcome is None:
            skipped += 1
            print(f"  pair-{index:03d}: sin experiencia informativa — descartado")
            continue
        pairs.append(outcome)
        print(f"  pair-{index:03d}: {outcome.informative} informativos · "
              f"N={outcome.consumes['NORMAL']} P={outcome.consumes['PARAMETRIC']} "
              f"F={outcome.consumes['FULL']} T={outcome.consumes['TRANSPLANT']} "
              f"R={outcome.consumes['RESTORE']} A0={outcome.consumes['A0']}")
    if skipped:
        print(f"\n  {skipped} pares descartados por falta de experiencia informativa")
    if not pairs:
        print("\n  INSUFFICIENT_INFORMATION: ningún par produjo experiencia informativa")
        return 2
    return report(pairs)


if __name__ == "__main__":
    raise SystemExit(main())
