#!/usr/bin/env python3
"""¿Qué distingue a una vida donde C18 gana de una donde pierde?

`LEARNER-18-v1` produce media(m) > 0 y sólo 10 de 16 vidas positivas. Si a la
v1 le falta una subcapacidad concreta, debe haber algún instrumento que separe
los dos grupos. Esto NO propone mecanismos: mide cuáles de los candidatos del
hipergrafo tienen evidencia y cuáles son, por ahora, sólo una idea.

Con dieciséis vidas y quince instrumentos, algo parecerá discriminar por azar.
La nula se deriva permutando la etiqueta ganar/perder, que es exactamente la
estructura que sesga.
"""
from __future__ import annotations

import sys

import numpy as np

sys.path.insert(0, ".")

from diagnostico.calibracion_ronda_c import seeds             # noqa: E402
from terrario.level18.life import live                        # noqa: E402

BUDGET = 16384
REPLICAS = 2000

#: Instrumento → el nodo candidato del hipergrafo que pondría a prueba.
CANDIDATES = {
    "states": "control de sobrefragmentación",
    "max_states": "control de sobrefragmentación",
    "occupied": "control de sobrefragmentación",
    "splits": "estabilidad de hipótesis",
    "merges": "estabilidad de hipótesis",
    "reverted": "estabilidad de hipótesis",
    "survival_mean": "persistencia estructural",
    "first_split": "persistencia estructural",
    "extensions": "criterio de identidad de contexto",
    "signatures": "criterio de identidad de contexto",
    "cells_supported": "asignación de evidencia",
    "starved": "asignación de evidencia",
    "starved_mass": "asignación de evidencia",
    "hungry_full": "asignación de evidencia",
    "situations": "(propiedad del mundo · control)",
    "mi_corrected": "recuperación de situación (diagnóstico)",
}


def collect():
    rows = []
    for seed in seeds():
        row = live(seed, BUDGET)
        margin = row["l_depth1"] - row["l_full"]
        readout = row["readout"]
        from terrario.level18.life import _conditional_entropy
        h_c_o = _conditional_entropy([(o, c) for o, _z, c in readout])
        h_c_zo = _conditional_entropy([((o, z), c) for o, z, c in readout])
        rows.append({
            **{k: row[k] for k in
               ("states", "max_states", "occupied", "splits", "merges",
                "reverted", "signatures", "cells_supported", "starved",
                "starved_mass", "hungry_full", "situations")},
            "survival_mean": float(np.mean(row["survival"])) if row["survival"] else 0.0,
            "first_split": row["first_split"] if row["first_split"] is not None else -1,
            "extensions": row["splits"] - len(row["survival"]),
            "mi_corrected": h_c_o - h_c_zo,
            "margin": margin, "wins": margin > 0, "seed": seed,
        })
    return rows


def main() -> None:
    rows = collect()
    wins = np.array([r["wins"] for r in rows])
    print(f"=== ingeniería inversa de LEARNER-18-v1 · T={BUDGET} · {len(rows)} vidas ===")
    print(f"    ganan {int(wins.sum())}/{len(rows)} · nula por permutación de la "
          f"etiqueta, {REPLICAS} réplicas\n")
    print(f"{'instrumento':>17} {'ganan':>9} {'pierden':>9} {'dif':>9} "
          f"{'|z| nula':>9}  nodo candidato")
    generator = np.random.default_rng(11)
    results = []
    for name, node in CANDIDATES.items():
        values = np.array([float(r[name]) for r in rows])
        a, b = values[wins].mean(), values[~wins].mean()
        observed = a - b
        null = []
        for _ in range(REPLICAS):
            shuffled = generator.permutation(wins)
            null.append(values[shuffled].mean() - values[~shuffled].mean())
        null = np.array(null)
        z = abs(observed - null.mean()) / (null.std(ddof=1) or 1.0)
        results.append((z, name, a, b, observed, node))
    for z, name, a, b, observed, node in sorted(results, reverse=True):
        mark = "  ←" if z >= 2.0 else ""
        print(f"{name:>17} {a:>9.3f} {b:>9.3f} {observed:>+9.3f} {z:>9.2f}  {node}{mark}")
    print("\n  '←' marca los instrumentos que separan los grupos por encima de su "
          "propia nula.\n  Lo que no lo marca NO está refutado: está sin evidencia "
          "con dieciséis vidas.")


if __name__ == "__main__":
    main()
