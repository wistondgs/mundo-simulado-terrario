#!/usr/bin/env python
"""¿Desgaste o co-adaptación? El experimento que separa telómero de Dobzhansky-Muller.

Propuse que la anomalía de DISCOVERY-32 -- `theta` inicial servido con estado
adaptativo aprendido saliendo PEOR que el nacimiento -- no es desgaste sino
incompatibilidad entre piezas co-adaptadas. Las dos lecturas hacen predicciones
opuestas y baratas de separar:

    DESGASTE            el daño de `M` sobre theta_0 es CONSTANTE: `M` está
                        deteriorada, y lo está igual venga del paso 50 o del 300.

    CO-ADAPTACIÓN       el daño ESCALA con la divergencia: `M` del paso 50 es
                        casi compatible con theta_0 y apenas daña; `M` del paso
                        300 se co-adaptó a un theta que el huésped no tiene.

Se guardan checkpoints de `M` durante la adquisición y cada uno se transplanta
sobre un clon INGENUO del mismo nacimiento. Todos congelados, mismo probe.

Control de emparejamiento: `M_t` sobre `theta_t` -- las dos piezas del mismo
momento. Si la co-adaptación es real, el emparejado no debe dañar en ningún
punto de la trayectoria, mientras el desemparejado empeora con t.

    python scripts/test_dmi_coadaptation.py --nacimientos 8
"""

from __future__ import annotations

import argparse
import copy
import statistics
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch  # noqa: E402

from terrario.agent.adaptive_freeze import AdaptiveFreeze  # noqa: E402
from terrario.agent.agents import create_agent  # noqa: E402
from terrario.core.rng import RNGManager  # noqa: E402
from terrario.lab.causal_bench import (  # noqa: E402
    REGIME_INTERVENTIONS, BirthSnapshot, PairedResult, clone_specimen,
)
from terrario.lab.diagnostic_probes import build_probe_bank, read_bank  # noqa: E402
from terrario.world.transition import build_episode_components, run_step  # noqa: E402

sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
from exp_adaptive_foraging_01 import (  # noqa: E402
    BASE, force_action, live, rich_world, ring_world,
)

#: Disjuntas de DISCOVERY-32 (0..31) y de la confirmatoria (1000+).
SEED_BASE = 5000
FRACTIONS = (0.0, 0.25, 0.5, 0.75, 1.0)


def _graft_M(host: Any, M: torch.Tensor) -> None:
    with torch.no_grad():
        host.longterm_memory.M.data.copy_(M)


def _graft_theta(host: Any, parameters: dict[str, torch.Tensor]) -> None:
    host.set_parameters({k: v for k, v in parameters.items()
                         if k != "longterm_memory.M"})


def run_birth(index: int, *, acquisition_steps: int, probe_distance: int):
    seed = SEED_BASE + index
    bank = build_probe_bank()
    birth = BirthSnapshot.materialize(f"dmi-{index:03d}", BASE, seed=seed)

    # --- stream informativo ---------------------------------------------------
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

    # --- NORMAL adquiere, guardando checkpoints de (theta, M) ----------------
    learner = birth.twin("NORMAL", REGIME_INTERVENTIONS["NORMAL"])
    agent = learner.specimen
    marks = {int(f * (len(stream) - 1)) for f in FRACTIONS}
    checkpoints: dict[int, dict[str, Any]] = {}
    for i, entry in enumerate(stream):
        if i in marks:
            checkpoints[i] = {
                "M": agent.longterm_memory.M.detach().clone(),
                "theta": {k: v.clone() for k, v in agent.get_parameters().items()},
            }
        agent.adaptive_freeze.set_step(i)
        agent.perceive(entry["observation"])
        agent.decide()
        force_action(agent, entry["action_int"])
        agent.learn(entry["transition"])
    last = len(stream) - 1
    checkpoints[last] = {"M": agent.longterm_memory.M.detach().clone(),
                         "theta": {k: v.clone() for k, v in agent.get_parameters().items()}}

    # --- Cuánto divergió `M` en cada punto ------------------------------------
    M0 = checkpoints[min(checkpoints)]["M"]
    divergence = {i: float((c["M"] - M0).norm()) for i, c in checkpoints.items()}

    # --- Transplantes: `M_t` sobre theta_0 (desemparejado) y sobre theta_t ----
    probe = ring_world(probe_distance, seed)
    mismatched, matched, knowledge = {}, {}, {}
    for i in sorted(checkpoints):
        host = clone_specimen(birth.prototype)
        host.adaptive_freeze = AdaptiveFreeze(enabled=True)
        _graft_M(host, checkpoints[i]["M"])
        knowledge[i] = read_bank(host, bank).discrimination
        mismatched[i] = live(host, probe, seed=seed, learning=False).effective_consumes

        paired_host = clone_specimen(birth.prototype)
        paired_host.adaptive_freeze = AdaptiveFreeze(enabled=True)
        _graft_M(paired_host, checkpoints[i]["M"])
        _graft_theta(paired_host, checkpoints[i]["theta"])
        matched[i] = live(paired_host, probe, seed=seed, learning=False).effective_consumes

    return {"birth": birth.pair_id, "informative": informative,
            "steps": sorted(checkpoints), "divergence": divergence,
            "mismatched": mismatched, "matched": matched, "knowledge": knowledge}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--nacimientos", type=int, default=8)
    parser.add_argument("--pasos", type=int, default=300)
    parser.add_argument("--distancia", type=int, default=3)
    args = parser.parse_args()

    print("DESGASTE FRENTE A CO-ADAPTACIÓN · transplante de `M` por checkpoint\n")
    print("  DESGASTE       predice daño CONSTANTE con el momento del checkpoint")
    print("  CO-ADAPTACIÓN  predice daño CRECIENTE con la divergencia de `M`\n")

    runs = []
    for index in range(args.nacimientos):
        result = run_birth(index, acquisition_steps=args.pasos,
                           probe_distance=args.distancia)
        if result is None:
            print(f"  {index}: sin experiencia informativa — descartado")
            continue
        runs.append(result)
        row = " ".join(f"{result['mismatched'][i]:>4}" for i in result["steps"])
        print(f"  {result['birth']}: desemparejado por checkpoint → {row}")

    if not runs:
        print("\n  sin datos")
        return 2

    steps = runs[0]["steps"]
    n = len(runs)
    print(f"\n\n  n = {n} nacimientos · checkpoints en los pasos {steps}\n")
    print(f"  {'paso':<8}{'‖M−M₀‖':>12}{'M sobre θ₀':>14}{'M sobre θ del mismo t':>24}"
          f"{'conocimiento':>16}")
    print("  " + "-" * 76)
    for i in steps:
        print(f"  {i:<8}{statistics.fmean(r['divergence'][i] for r in runs):>12.4f}"
              f"{statistics.fmean(r['mismatched'][i] for r in runs):>14.2f}"
              f"{statistics.fmean(r['matched'][i] for r in runs):>24.2f}"
              f"{statistics.fmean(r['knowledge'][i] for r in runs):>+16.6f}")

    first, last = steps[0], steps[-1]
    mismatch_delta = PairedResult(
        "desemparejado tardío − temprano",
        [float(r["mismatched"][last] - r["mismatched"][first]) for r in runs])
    matched_delta = PairedResult(
        "emparejado tardío − temprano",
        [float(r["matched"][last] - r["matched"][first]) for r in runs])

    print(f"\n  {'contraste':<34}{'media':>9}{'IC95% pareado':>26}{'signo −':>10}")
    print("  " + "-" * 79)
    for result in (mismatch_delta, matched_delta):
        lo, hi = result.bootstrap()
        negative = sum(1 for d in result.deltas if d < 0) / len(result.deltas)
        print(f"  {result.name:<34}{result.mean:>+9.2f}"
              f"{f'[{lo:+.2f}, {hi:+.2f}]':>26}{negative:>10.0%}")

    lo, hi = mismatch_delta.bootstrap()
    print("\n  LECTURA")
    if hi < 0:
        print("    El desemparejado EMPEORA con el momento del checkpoint.")
        print("    Compatible con CO-ADAPTACIÓN; incompatible con desgaste constante.")
    elif lo > 0:
        print("    El desemparejado MEJORA con el momento del checkpoint.")
        print("    Incompatible con las dos lecturas que propuse. Hay que rehacer la hipótesis.")
    else:
        print("    El intervalo cruza el cero: con esta n no se separan las dos lecturas.")
        print(f"    n={n} es un primer tiro, no una respuesta.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
