#!/usr/bin/env python3
"""¿Puede siquiera GANAR la partición de profundidad 1? DIAGNÓSTICO · pasivo.

Si conditionar por `a_{t-1}` --que es exactamente lo que el primer split del
learner produce-- no bate al baseline continuo, entonces el mecanismo arranca
desde una posición perdedora y estudiar profundidad 8 no tiene sentido.

Cuatro organizaciones sobre la MISMA evidencia del mismo mundo, todas con la
misma regla de conservación de masa:

    NO-SPLIT          Z = {z_0}                    = C17-ONLY continuo
    DEPTH-1           Z = a_{t-1}                  4 estados
    LEARNER           Z lo que el mecanismo halló
    ORACLE-PARTITION  Z = la situación verdadera   techo

El oráculo se usa **sólo** como instrumento. El learner no lo ve.
"""
from __future__ import annotations

import sys

import numpy as np

sys.path.insert(0, ".")

from terrario.level1.world import DELTA, Direction          # noqa: E402
from terrario.level16.motor import EndogenousMotor          # noqa: E402
from terrario.level16.structure import _signature           # noqa: E402
from terrario.level16.temporal import OBSERVATION_INDEX, TemporalModel  # noqa: E402
from terrario.level16.world import build_world, motor_stream  # noqa: E402
from terrario.level17.contingency import ActionContingencyModel  # noqa: E402
from terrario.level17.efference import ALL_COMMANDS, EfferenceCopy  # noqa: E402
from terrario.level17.wiring import ActuatorWiring          # noqa: E402
from terrario.level18.predictive_state import PredictiveStateModel  # noqa: E402

SEEDS = tuple(range(150000011, 150000019))


def _situations(grid):
    reachable = {grid.position}
    stack = [grid.position]
    while stack:
        here, there = stack.pop()
        for direction in Direction:
            step = (here + DELTA[direction][0], there + DELTA[direction][1])
            if grid.cells[step] == 0 and step not in reachable:
                reachable.add(step)
                stack.append(step)
    ordered = sorted(reachable)
    return ordered, {c: i for i, c in enumerate(ordered)}


def run(seed: int, budget: int, predecessor: int = 4096, contingency: int = 1024,
        post: int = 2048):
    grid = build_world(seed)
    wiring = ActuatorWiring.sampled(seed)
    motor = EndogenousMotor(motor_stream(seed))
    ordered, index = _situations(grid)

    temporal = TemporalModel()
    observation = grid.observe()
    for _ in range(predecessor):
        command = ALL_COMMANDS[int(motor.next())]
        _, following = grid.step(wiring.actuate(command))
        temporal.observe(observation, following)
        observation = following
    temporal.freeze()

    contingent = ActionContingencyModel(temporal)
    for _ in range(contingency):
        command = ALL_COMMANDS[int(motor.next())]
        _, following = grid.step(wiring.actuate(command))
        contingent.observe(observation, EfferenceCopy(command), following)
        observation = following

    table = (np.repeat(contingent._inherited[:, None, :], 4, axis=1) * 0.25
             + contingent.acquired_snapshot())

    baseline = ActionContingencyModel(temporal)
    baseline.load_acquired(contingent.acquired_snapshot())
    depth_one = {a: table / 4.0 for a in range(4)}
    evidence_one = {a: np.zeros_like(table) for a in range(4)}
    oracle_prior = {index[c]: table / len(ordered) for c in ordered}
    evidence_oracle = {index[c]: np.zeros_like(table) for c in ordered}
    learner = PredictiveStateModel(table)
    learner.begin()

    last = 0
    for _ in range(budget):
        command = ALL_COMMANDS[int(motor.next())]
        action = ALL_COMMANDS.index(command)
        standing = grid.position
        _, following = grid.step(wiring.actuate(command))
        before = OBSERVATION_INDEX[observation]
        after = OBSERVATION_INDEX[following]
        baseline.observe(observation, EfferenceCopy(command), following)
        learner.observe(observation, EfferenceCopy(command), following)
        evidence_one[last][before, action, after] += 1
        evidence_oracle[index[standing]][before, action, after] += 1
        last = action
        observation = following

    bank = []
    for _ in range(post):
        command = ALL_COMMANDS[int(motor.next())]
        standing = grid.position
        _, following = grid.step(wiring.actuate(command))
        bank.append((observation, command, following, last, index[standing]))
        last = ALL_COMMANDS.index(command)
        observation = following

    def score(fn):
        return -float(np.mean([np.log(max(fn(*row), 1e-300)) for row in bank]))

    def tabled(prior, evidence, which):
        def fn(obs, command, nxt, previous_action, situation):
            key = previous_action if which == "one" else situation
            weights = (prior[key][OBSERVATION_INDEX[obs], ALL_COMMANDS.index(command)]
                       + evidence[key][OBSERVATION_INDEX[obs],
                                       ALL_COMMANDS.index(command)])
            return weights[OBSERVATION_INDEX[nxt]] / weights.sum()
        return fn

    learner.begin()
    return {
        "no_split": score(lambda o, k, n, p, s: baseline.probability(
            o, EfferenceCopy(k), n)),
        "depth_one": score(tabled(depth_one, evidence_one, "one")),
        "learner": score(lambda o, k, n, p, s: learner.probability(
            o, EfferenceCopy(k), n)),
        "oracle": score(tabled(oracle_prior, evidence_oracle, "oracle")),
        "states": len(learner.states()),
        "splits": learner.refinements,
        "situations": len(ordered),
        "mass_one": float(np.abs(sum(depth_one.values()) - table).max()),
        "mass_oracle": float(np.abs(sum(oracle_prior.values()) - table).max()),
    }


def main() -> None:
    print("=== ¿gana la profundidad 1, que es lo que el primer split produce? ===\n")
    print(f"{'T_18':>6} {'NO-SPLIT':>9} {'DEPTH-1':>9} {'LEARNER':>9} {'ORACLE':>9} | "
          f"{'ΔL d1':>8} {'ΔL lrn':>8} {'ΔL orac':>8} | {'est':>4} {'spl':>4} {'sit':>4}")
    for budget in (1024, 4096):
        rows = [run(s, budget) for s in SEEDS]
        mean = lambda k: float(np.mean([r[k] for r in rows]))
        base = mean("no_split")
        print(f"{budget:>6} {base:>9.4f} {mean('depth_one'):>9.4f} "
              f"{mean('learner'):>9.4f} {mean('oracle'):>9.4f} | "
              f"{base - mean('depth_one'):>+8.4f} {base - mean('learner'):>+8.4f} "
              f"{base - mean('oracle'):>+8.4f} | {mean('states'):>4.1f} "
              f"{mean('splits'):>4.1f} {mean('situations'):>4.1f}")
    print(f"\n  conservación de masa · DEPTH-1 {max(r['mass_one'] for r in rows):.2e}"
          f" · ORACLE {max(r['mass_oracle'] for r in rows):.2e}")


if __name__ == "__main__":
    main()
