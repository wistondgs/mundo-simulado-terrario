#!/usr/bin/env python3
"""N1.0 · la campaña confirmatoria. Verifica el sello y después no decide nada.

Nothing in here looks at a scientific number to choose what to do next.  It
checks the seal, runs every replica, writes the raw rows, and only then
applies the analysis that was sealed before any of it ran.

If the seal does not match, it aborts without spending a seed.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))

from terrario.lab import world_generator as gen                       # noqa: E402
from terrario.lab.n10_arms import Arm, build_arm                      # noqa: E402
from terrario.lab.n10_instrument import (                             # noqa: E402
    ApparatusNormalization, n1_run, same_present, seed_is_evaluable,
    shuffle_report, shuffled_tokens)
from terrario.lab.n10_u1 import U1, U1Agent, U1Config                 # noqa: E402

MANIFIESTO = RAIZ / "docs" / "N10_CAMPAIGN_MANIFEST_V3.json"
CRUDO = RAIZ / "docs" / "N10_RAW_RESULTS.json"


def verificar_sello(m: dict) -> dict:
    """Abortar antes de gastar una semilla si algo no coincide."""
    vivos = {p: hashlib.sha256((RAIZ / p).read_bytes()).hexdigest()
             for p in m["sealed_code"]}
    raiz = hashlib.sha256(json.dumps(vivos, sort_keys=True).encode()).hexdigest()
    estado = subprocess.run(["git", "-C", str(RAIZ), "status", "--porcelain"],
                            capture_output=True, text=True).stdout.strip()
    head = subprocess.run(["git", "-C", str(RAIZ), "rev-parse", "HEAD"],
                          capture_output=True, text=True).stdout.strip()
    difieren = [p for p, h in vivos.items() if h != m["sealed_code"][p]]
    return {"head": head, "tree_clean": estado == "", "code_root_live": raiz,
            "code_root_sealed": m["sealed_code_root_hash"],
            "code_matches": raiz == m["sealed_code_root_hash"],
            "differing_files": difieren,
            "seed_manifest_hash": m["seed_manifest_hash"],
            "manifest_sha256": hashlib.sha256(MANIFIESTO.read_bytes()).hexdigest()}


def _mundo(seed: int, stations: int, eco: gen.Economy):
    w = gen.world_for(['EPMEM-A1'], seed=seed, stations=stations, economy=eco)
    w.scenario['expose_time_fraction'] = False
    return w


def _ba(filas) -> float | None:
    por = {}
    for r in filas:
        por.setdefault(r.history_id, []).append(r.correct)
    if len(por) < 2:
        return None
    return sum(sum(v) / len(v) for v in por.values()) / len(por)


def _por_clase(filas) -> dict:
    por = {}
    for r in filas:
        por.setdefault(r.history_id, []).append(r.correct)
    return {h: sum(v) / len(v) for h, v in sorted(por.items())}


def _signed_branch(filas) -> float | None:
    arriba, por = {}, {}
    for r in filas:
        por.setdefault(r.history_id, []).append(r)
    if len(por) < 2:
        return None
    for h, v in por.items():
        correcta = v[0].correct_action
        arriba[h] = (sum(1 for x in v if x.chosen_action == "up") / len(v), correcta)
    h_up = [h for h, (_, c) in arriba.items() if c == "up"]
    h_dn = [h for h, (_, c) in arriba.items() if c == "down"]
    if not h_up or not h_dn:
        return None
    return arriba[h_up[0]][0] - arriba[h_dn[0]][0]


def replica(i: int, m: dict) -> dict:
    cfg_e = m["config"]["economy"]
    eco = gen.Economy(**cfg_e)
    norm = ApparatusNormalization(
        enabled=True,
        baseline_energy=m["config"]["apparatus_normalization"]["baseline_energy"])
    b = m["config"]["budget"]
    lp = m["config"]["learner"]
    train_seed = m["seeds"]["train"][i]
    eval_seed = m["seeds"]["eval"][i]
    shuffle_seed = m["seeds"]["shuffle"][i]

    cfg_train = U1Config(alpha=lp["alpha_train"], exploration=lp["epsilon_train"],
                         seed=train_seed)
    w_train = _mundo(train_seed, b["acquisition_stations"], eco)
    w_eval = _mundo(eval_seed, b["evaluation_stations"], eco)
    ev_train = seed_is_evaluable(w_train)
    ev_eval = seed_is_evaluable(w_eval)

    naive = U1(cfg_train)
    q_inicial = dict(naive.theta)
    ag = U1Agent(w_train, cfg_train)
    ag.core = naive
    filas_train = n1_run(w_train, ag, arm="acq", seed=train_seed,
                         learning_enabled=True, normalization=norm)
    snapshot = ag.core
    snapshot.freeze()

    naive_frozen = U1(cfg_train)
    naive_frozen.freeze()

    salida = {"replica": i, "train_seed": train_seed, "eval_seed": eval_seed,
              "shuffle_seed": shuffle_seed,
              "evaluable_train": ev_train, "evaluable_eval": ev_eval,
              "acquisition": {"decisions": len(filas_train),
                              "exposure": {h: sum(1 for f in filas_train
                                                  if f.history_id == h)
                                           for h in {f.history_id for f in filas_train}},
                              "feedback_positive": sum(1 for f in filas_train
                                                       if f.consequence > 0),
                              "feedback_negative": sum(1 for f in filas_train
                                                       if f.consequence < 0),
                              "q_initial": {f"{k[0]}|{k[1]}": v
                                            for k, v in q_inicial.items()},
                              "q_final": {f"{k[0]}|{k[1]}": round(v, 9)
                                          for k, v in sorted(snapshot.theta.items())},
                              "snapshot_digest": snapshot.theta_digest()},
              "readouts": {}}

    for etiqueta, eps in (("primary", lp["epsilon_primary_eval"]),
                          ("secondary", lp["epsilon_secondary_eval"])):
        cfg_eval = U1Config(alpha=lp["alpha_train"], exploration=eps, seed=eval_seed)
        brazos, hashes_pre, hashes_post, filas_por_brazo = {}, {}, {}, {}

        ag_n = U1Agent(_mundo(eval_seed, b["evaluation_stations"], eco), cfg_eval)
        ag_n.core = naive_frozen.clone(cfg_eval)
        ag_n.core.freeze()
        hashes_pre["N"] = ag_n.core.theta_digest()
        filas_por_brazo["N"] = list(n1_run(
            _mundo(eval_seed, b["evaluation_stations"], eco), ag_n, arm="N",
            seed=eval_seed, learning_enabled=False, normalization=norm))
        hashes_post["N"] = ag_n.core.theta_digest()

        for arm in (Arm.COMPLETE, Arm.MEMORY_READ_LESION):
            w = _mundo(eval_seed, b["evaluation_stations"], eco)
            a = build_arm(arm, w, snapshot, cfg_eval)
            hashes_pre[arm.value] = a.core.theta_digest()
            filas_por_brazo[arm.value] = list(n1_run(
                w, a, arm=arm.value, seed=eval_seed, learning_enabled=False,
                normalization=norm))
            hashes_post[arm.value] = a.core.theta_digest()

        # C necesita la secuencia de A para permutarla: mismo mundo, mismos ids.
        base = filas_por_brazo["A"]
        mapa = shuffled_tokens(base, seed=shuffle_seed)
        historia_a_token = {f.history_id: None for f in base}
        from terrario.lab.n10_u1_spec import opaque_token
        for h in historia_a_token:
            historia_a_token[h] = opaque_token(float(h.split("|")[0]))
        w = _mundo(eval_seed, b["evaluation_stations"], eco)
        c = build_arm(Arm.HISTORY_SHUFFLED, w, snapshot, cfg_eval)
        hashes_pre["C"] = c.core.theta_digest()
        filas_por_brazo["C"] = list(n1_run(
            w, c, arm="C", seed=eval_seed, learning_enabled=False,
            normalization=norm,
            token_source=lambda idx, h: historia_a_token[mapa[idx]]
            if idx in mapa else historia_a_token[h]))
        hashes_post["C"] = c.core.theta_digest()

        salida["readouts"][etiqueta] = {
            "epsilon": eps,
            "theta_before": hashes_pre, "theta_after": hashes_post,
            "snapshot_parity": len({hashes_pre[k] for k in ("A", "B", "C")}) == 1,
            "freeze_held": all(hashes_pre[k] == hashes_post[k] for k in hashes_pre),
            "decision_ids": {k: [f.decision_id for f in v]
                             for k, v in filas_por_brazo.items()},
            "decision_parity": len({tuple(f.decision_id for f in v)
                                    for k, v in filas_por_brazo.items()
                                    if k in ("A", "B", "C")}) == 1,
            "same_present": {k: same_present(v)["result"]
                             for k, v in filas_por_brazo.items()},
            "n_obs_hash": {k: same_present(v)["n_obs_hash"]
                           for k, v in filas_por_brazo.items()},
            "shuffle": shuffle_report(base, seed=shuffle_seed),
            "BA": {k: _ba(v) for k, v in filas_por_brazo.items()},
            "per_class": {k: _por_clase(v) for k, v in filas_por_brazo.items()},
            "signed_branch": {k: _signed_branch(v) for k, v in filas_por_brazo.items()},
            "n_decisions": {k: len(v) for k, v in filas_por_brazo.items()},
        }
    return salida


def bootstrap(deltas: list[float], *, seed: int, resamples: int) -> dict:
    rng = np.random.default_rng(seed)
    d = np.asarray(deltas, dtype=float)
    idx = rng.integers(0, len(d), size=(resamples, len(d)))
    medias = d[idx].mean(axis=1)
    return {"estimate": float(d.mean()),
            "lcb95": float(np.percentile(medias, 5)),
            "ci95": [float(np.percentile(medias, 2.5)),
                     float(np.percentile(medias, 97.5))],
            "n_seeds": len(d)}


if __name__ == "__main__":
    m = json.loads(MANIFIESTO.read_text())
    sello = verificar_sello(m)
    print("=== SELLO ===")
    for k, v in sello.items():
        print(f"  {k}: {v if not isinstance(v, str) or len(v) < 50 else v[:32] + '…'}")
    if not (sello["code_matches"] and sello["tree_clean"]):
        raise SystemExit("ABORTADO: el sello no coincide. No se gastó ninguna semilla.")
    if "--run" not in sys.argv:
        print("\n(sin --run no se consume ninguna semilla)")
        raise SystemExit(0)

    filas = []
    for i in range(m["seeds"]["n_replicas"]):
        filas.append(replica(i, m))
        print(f"  réplica {i + 1}/{m['seeds']['n_replicas']} hecha", flush=True)
    CRUDO.write_text(json.dumps({"seal": sello, "manifest_version": m["schema"],
                                 "replicas": filas}, indent=2) + "\n")
    print(f"\ncrudo escrito: {CRUDO.relative_to(RAIZ)}")
