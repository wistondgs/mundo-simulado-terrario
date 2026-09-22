#!/usr/bin/env python3
"""N1.0 · reanálisis independiente, desde los crudos y el preregistro.

Reads only the raw results and the authoritative preregistration. It does not
open the published summary or the confirmatory report: those are what its
output is compared against, and reading them would make the reconstruction
worthless.

It runs no experiment. No world is generated, nothing is trained, no agent is
evaluated and no seed is consumed. If a number cannot be rebuilt from what was
preserved, that is a debt of preservation and it is reported as one; running
the campaign again would not repair it.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
CRUDO = RAIZ / "docs" / "N10_RAW_RESULTS.json"
MANIFIESTO = RAIZ / "docs" / "N10_CAMPAIGN_MANIFEST_V3.json"

#: Lo que este script NO puede abrir. Está escrito para que se vea.
PROHIBIDO = ("docs/N10_SEED_SUMMARY.json", "docs/N10_CONFIRMATORY_REPORT.md")


def bootstrap_pareado(vectores: dict[str, list[float]], *, seed: int,
                      resamples: int) -> dict:
    """Un solo sorteo de índices, reutilizado para todas las cantidades.

    Eso es lo que hace el bootstrap PAREADO y lo que mantiene los tres
    contrastes mutuamente consistentes: si cada uno remuestreara por su
    cuenta, sus intervalos vendrían de reparticiones distintas de las mismas
    semillas.
    """
    n = len(next(iter(vectores.values())))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(resamples, n))
    salida = {}
    for nombre, v in vectores.items():
        d = np.asarray(v, dtype=float)
        medias = d[idx].mean(axis=1)
        salida[nombre] = {"estimate": float(d.mean()),
                          "lcb95": float(np.percentile(medias, 5)),
                          "ci95": [float(np.percentile(medias, 2.5)),
                                   float(np.percentile(medias, 97.5))],
                          "n_seeds": n}
    return salida


def gates_desde_crudo(R: list) -> dict:
    """Recalculados, no heredados del campo `CAMPAIGN_VALID`."""
    def todos(f):
        return all(f(r) for r in R)
    g = {}
    g["snapshot_parity_ABC"] = todos(lambda r: all(
        r["readouts"][l]["snapshot_parity"] for l in ("primary", "secondary")))
    g["evaluation_freeze"] = todos(lambda r: all(
        r["readouts"][l]["freeze_held"] for l in ("primary", "secondary")))
    g["decision_id_parity"] = todos(lambda r: all(
        r["readouts"][l]["decision_parity"] for l in ("primary", "secondary")))
    g["same_present_all_arms"] = todos(lambda r: all(
        v == "PASS" for l in ("primary", "secondary")
        for v in r["readouts"][l]["same_present"].values()))
    g["one_obs_hash_per_arm"] = todos(lambda r: all(
        v == 1 for l in ("primary", "secondary")
        for v in r["readouts"][l]["n_obs_hash"].values()))
    g["both_histories_in_acquisition"] = todos(
        lambda r: len(r["acquisition"]["exposure"]) == 2)
    g["both_histories_in_evaluation"] = todos(
        lambda r: len(r["evaluable_eval"]["history_classes"]) == 2)
    g["shuffle_marginals"] = todos(lambda r: all(
        r["readouts"][l]["shuffle"]["marginals_preserved"]
        for l in ("primary", "secondary")))
    g["shuffle_strength"] = todos(lambda r: all(
        r["readouts"][l]["shuffle"]["strong_enough"]
        for l in ("primary", "secondary")))
    g["no_seed_replacement"] = todos(
        lambda r: r["evaluable_train"]["evaluable"] and r["evaluable_eval"]["evaluable"])
    return g


def reconstruir() -> dict:
    crudo = json.loads(CRUDO.read_text())
    m = json.loads(MANIFIESTO.read_text())
    R = crudo["replicas"]
    an = m["analysis"]
    lect = "primary"
    ba = {k: [r["readouts"][lect]["BA"][k] for r in R] for k in ("N", "A", "B", "C")}
    vect = {"acquisition_gain": [a - x for a, x in zip(ba["A"], ba["N"])],
            "lesion_loss": [a - x for a, x in zip(ba["A"], ba["B"])],
            "shuffle_loss": [a - x for a, x in zip(ba["A"], ba["C"])],
            "BA_A": ba["A"]}
    clases = sorted({h for r in R for h in r["readouts"][lect]["per_class"]["A"]})
    for h in clases:
        vect[f"acc_H_{h}"] = [r["readouts"][lect]["per_class"]["A"][h] for r in R]
    boot = bootstrap_pareado(vect, seed=an["bootstrap_seed"],
                             resamples=an["resamples"])

    u = m["thresholds"]["statistical"]
    reglas = {
        "BA_A >= 0.75": boot["BA_A"]["lcb95"] >= 0.75,
        "acquisition_gain > 0": boot["acquisition_gain"]["lcb95"] > 0.0,
        "lesion_loss >= 0.10": boot["lesion_loss"]["lcb95"] >= 0.10,
        "shuffle_loss >= 0.10": boot["shuffle_loss"]["lcb95"] >= 0.10,
    }
    for h in clases:
        reglas[f"acc_H_{h} > 0.5"] = boot[f"acc_H_{h}"]["lcb95"] > 0.5

    gates = gates_desde_crudo(R)
    valida = all(gates.values())
    veredicto = ("NEW_DF_DETECTED" if valida and all(reglas.values())
                 else ("INVALID" if not valida else "INDETERMINATE"))

    #: Lo que la equivalencia B/N puede sostenerse DESDE EL CRUDO. La prueba
    #: estructural vive en el código y se registra aparte: el crudo no guarda
    #: acciones por decisión, así que desde aquí no se puede afirmar EXACT.
    iguales = sum(1 for r in R
                  if r["readouts"][lect]["BA"]["N"] == r["readouts"][lect]["BA"]["B"])
    degenerado = all(v == 1.0 for h in clases for v in vect[f"acc_H_{h}"])

    return {"source": {"raw": CRUDO.name, "manifest": MANIFIESTO.name,
                       "never_read": list(PROHIBIDO)},
            "n_replicas": len(R), "validity_gates": gates,
            "campaign_valid": valida,
            "ba_means": {k: float(np.mean(v)) for k, v in ba.items()},
            "bootstrap": boot, "threshold_rules": reglas,
            "verdict": veredicto,
            "b_equals_n_from_raw": {"replicas_identical_BA": iguales, "of": len(R),
                                    "classification_from_raw": "BEHAVIORAL"},
            "per_class_bounds_degenerate": degenerado,
            "independent_contrast_count": 2 if iguales == len(R) else 3}


if __name__ == "__main__":
    r = reconstruir()
    if "--json" in sys.argv:
        print(json.dumps(r, indent=2))
    else:
        print(f"réplicas {r['n_replicas']} · CAMPAIGN_VALID {r['campaign_valid']}")
        for k, v in r["validity_gates"].items():
            print(f"  {k:32} {'PASS' if v else 'FAIL'}")
        print(f"\nBA  " + "  ".join(f"{k} {v:.4f}" for k, v in r["ba_means"].items()))
        for k in ("acquisition_gain", "lesion_loss", "shuffle_loss", "BA_A"):
            b = r["bootstrap"][k]
            print(f"  {k:18} est {b['estimate']:+.10f}  LCB95 {b['lcb95']:+.10f}")
        print(f"\nveredicto reconstruido: {r['verdict']}")
        print(f"contrastes independientes: {r['independent_contrast_count']}")
        print(f"cotas por clase degeneradas: {r['per_class_bounds_degenerate']}")
