#!/usr/bin/env python3
"""¿Se parecen sus estados a las situaciones del mundo? DIAGNÓSTICO · pasivo.

`ΔL` dice si predice mejor. No dice si lo que construyó ES el estado latente.
Aquí se mide `I(C;Z|O)` --cuánta información sobre la situación verdadera lleva
su estado, más allá de lo que la observación ya da-- con una advertencia que la
haría inservible si se ignorase: el estimador empírico de información **sesga
hacia arriba con el número de estados**. Comparar 61 estados contra 7 mediría en
parte el estimador.

La nula se deriva del propio dato: permutar Z DENTRO de cada observación destruye
la relación C-Z y conserva exactamente el número de estados, que es lo que sesga.
Lo que se reporta es `I - nula`.

El oráculo C es instrumento de medida. El learner no lo ve nunca.
"""
from __future__ import annotations

import sys
from collections import defaultdict

import numpy as np

sys.path.insert(0, ".")

import diagnostico.profundidad_uno as microscopio          # noqa: E402
from terrario.level18.predictive_state import PredictiveStateModel  # noqa: E402

REPLICAS = 32


def informacion(readout) -> float:
    fuera = microscopio._entropia_condicional([(o, c) for o, _z, c in readout])
    dentro = microscopio._entropia_condicional([((o, z), c) for o, z, c in readout])
    return fuera - dentro


def nula(readout, replicas: int, seed: int):
    generator = np.random.default_rng(seed)
    by_observation = defaultdict(list)
    for i, (o, _z, _c) in enumerate(readout):
        by_observation[o].append(i)
    values = []
    for _ in range(replicas):
        shuffled = list(readout)
        for indices in by_observation.values():
            states = [readout[i][1] for i in indices]
            generator.shuffle(states)
            for i, z in zip(indices, states):
                shuffled[i] = (readout[i][0], z, readout[i][2])
        values.append(informacion(shuffled))
    return float(np.mean(values)), float(np.std(values, ddof=1))


def main() -> None:
    print("=== I(C;Z|O) contra su propia nula por permutación ===")
    print(f"    {REPLICAS} réplicas · Z permutado dentro de cada observación\n")
    print(f"{'T_18':>6} {'brazo':>18} {'|Z|':>6} | {'I medida':>9} {'I nula':>8} "
          f"{'sd nula':>8} | {'I - nula':>9} {'z':>7} {'% H(C|O)':>9}")
    intact = PredictiveStateModel._judge_open_split
    for budget in (1024, 4096):
        for name, patch in (("CON merge", intact),
                            ("SIN merge (lesión)", lambda self, *a, **k: None)):
            PredictiveStateModel._judge_open_split = patch
            measured, nulls, sds, sizes, ceilings = [], [], [], [], []
            for k, seed in enumerate(microscopio.SEEDS):
                row = microscopio.run(seed, budget)
                readout = row["readout"]
                measured.append(informacion(readout))
                mean, sd = nula(readout, REPLICAS, 180000000 + k)
                nulls.append(mean)
                sds.append(sd)
                sizes.append(len({z for _o, z, _c in readout}))
                ceilings.append(row["h_c_o"])
            m, n, s = np.mean(measured), np.mean(nulls), np.mean(sds)
            print(f"{budget:>6} {name:>18} {np.mean(sizes):>6.1f} | {m:>9.4f} "
                  f"{n:>8.4f} {s:>8.4f} | {m - n:>+9.4f} {(m - n) / s:>7.2f} "
                  f"{100 * (m - n) / np.mean(ceilings):>8.2f}%")
    PredictiveStateModel._judge_open_split = intact


if __name__ == "__main__":
    main()
