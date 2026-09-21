#!/usr/bin/env python3
"""Diagnóstico de adjudicación de 1.8. EXPLORATORIO · NO CONFIRMATORIO.

No implementa ninguna capacidad: nadie aprende nada nuevo aquí. Corre políticas
**suministradas** sobre el estado congelado de 1.7 para contestar dos preguntas
previas al diseño:

    F · ¿K(o,a) es un readout del estado de C17, sin estado nuevo?
    G · ¿cuánto del techo da C17 + readout fijo + política que escribimos nosotros?

    python scripts/diagnostico_seleccion.py
"""
from __future__ import annotations

import sys

import numpy as np

sys.path.insert(0, ".")

from terrario.level16.motor import EndogenousMotor          # noqa: E402
from terrario.level16.temporal import OBSERVATION_INDEX, TemporalModel  # noqa: E402
from terrario.level16.world import build_world, motor_stream  # noqa: E402
from terrario.level17.contingency import ActionContingencyModel  # noqa: E402
from terrario.level17.efference import ALL_COMMANDS, EfferenceCopy  # noqa: E402
from terrario.level17.shadow import AnalyticActionShadow    # noqa: E402
from terrario.level17.wiring import ActuatorWiring          # noqa: E402

SEEDS = tuple(range(150000011, 150000027))
PREDECESSOR = 4096


def ceilings(seed):
    """Techo LIBRE (no realizable) y techo ALCANZABLE por una política.

    La diferencia importa: una política elige `a` dado `o`, **no elige `o`**. El
    techo libre reasigna presupuesto entre observaciones, cosa que ningún
    organismo puede hacer desde dentro.
    """
    shadow = AnalyticActionShadow(build_world(seed), ActuatorWiring.sampled(seed))
    table = shadow.action_conditional()
    reference = shadow.p_reference
    outcomes = np.maximum(np.array(
        [[(table[o, a] > 1e-12).sum() for a in range(4)] for o in range(16)],
        float) - 1, 0)

    def error(allocation):
        mask = (reference > 1e-12) & (outcomes > 0)
        return float(np.sum(reference[mask] * outcomes[mask]
                            / (2 * np.maximum(allocation[mask], 1e-15))))

    uniform = reference / reference.sum()
    free = np.sqrt(reference * outcomes)
    free = free / free.sum() if free.sum() > 0 else uniform
    reachable = np.zeros((16, 4))
    per_observation = reference.sum(axis=1)
    for o in range(16):
        if per_observation[o] <= 1e-12:
            continue
        weight = np.sqrt(outcomes[o])
        reachable[o] = per_observation[o] * (
            weight / weight.sum() if weight.sum() > 1e-12 else np.full(4, 0.25))
    base = error(uniform)
    return (error(free) / base, error(reachable) / base) if base > 0 else (1.0, 1.0)


def run(seed: int, budget: int, policy: str, rng):
    """Una vida de dos fases con la política indicada en la fase de adquisición."""
    grid = build_world(seed)
    wiring = ActuatorWiring.sampled(seed)
    motor = EndogenousMotor(motor_stream(seed))
    inherited = TemporalModel()
    observation = grid.observe()
    for _ in range(PREDECESSOR):
        command = ALL_COMMANDS[int(motor.next())]
        _, following = grid.step(wiring.actuate(command))
        inherited.observe(observation, following)
        observation = following
    inherited.freeze()

    model = ActionContingencyModel(inherited)
    counts = np.zeros((16, 4))
    visits = np.zeros(16)
    shadow = AnalyticActionShadow(build_world(seed), wiring)
    truth = np.array([[(shadow.action_conditional()[o, a] > 1e-12).sum()
                       for a in range(4)] for o in range(16)], float)

    for _ in range(budget):
        index = OBSERVATION_INDEX[observation]
        visits[index] += 1
        if policy == "uniforme":
            action = int(motor.next())
        elif policy == "lowcount":
            row = counts[index]
            action = int(rng.choice(np.flatnonzero(row == row.min())))
        else:
            seen = (truth if policy == "oraculo"
                    else (model.acquired_snapshot() > 0).sum(axis=2).astype(float))
            weight = np.sqrt(np.maximum(seen[index] - 1, 0))
            if weight.sum() <= 1e-12:
                action = int(motor.next())
            else:
                target = weight / weight.sum()
                current = counts[index] / max(counts[index].sum(), 1)
                action = int(np.argmax(target - current))
        command = ALL_COMMANDS[action]
        _, following = grid.step(wiring.actuate(command))
        model.observe(observation, EfferenceCopy(command), following)
        counts[index, action] += 1
        observation = following

    empirical = visits / visits.sum()
    drift = float(np.abs(empirical - shadow.p_reference.sum(axis=1)).sum() / 2)
    return shadow.learner_error(model), drift


def main() -> None:
    free, reach = zip(*(ceilings(s) for s in SEEDS))
    print("=== techo libre (NO realizable) contra techo alcanzable ===")
    print(f"  libre       razón {np.mean(free):.4f}   ganancia {100*(1-np.mean(free)):5.1f}%")
    print(f"  alcanzable  razón {np.mean(reach):.4f}   ganancia {100*(1-np.mean(reach)):5.1f}%")

    print("\n=== G · epsilon_A final (menos es mejor) y deriva respecto de p_ref ===")
    print(f"{'T':>5} {'uniforme':>9} {'lowcount':>9} {'C17+readout':>12} {'oráculo':>9} "
          f"| {'TV unif':>8} {'TV oráculo':>11}")
    for budget in (64, 128, 256, 512):
        out = {}
        for policy in ("uniforme", "lowcount", "suministrada", "oraculo"):
            pairs = [run(s, budget, policy, np.random.default_rng([s, 512]))
                     for s in SEEDS]
            out[policy] = (np.mean([e for e, _ in pairs]),
                           np.mean([d for _, d in pairs]))
        print(f"{budget:>5} {out['uniforme'][0]:>9.4f} {out['lowcount'][0]:>9.4f} "
              f"{out['suministrada'][0]:>12.4f} {out['oraculo'][0]:>9.4f} | "
              f"{out['uniforme'][1]:>8.4f} {out['oraculo'][1]:>11.4f}")


if __name__ == "__main__":
    main()
