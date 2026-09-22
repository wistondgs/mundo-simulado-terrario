#!/usr/bin/env python3
"""N1.0 · preregistro v2. V1 queda intacto y se marca SUPERSEDED.

V1 is not edited and not regenerated: its script and its artefact stay
exactly as they were sealed. What changed is statistical and procedural, and
all of it was changed while no confirmatory seed had been spent.

Six corrections:

1. The lesion and shuffle threshold keeps its value and loses its
   justification.  «A fifth of the expected loss» derives a bar from what we
   expect to happen, which is the wrong direction.  It is now a declared
   minimum relevant causal effect -- 10 points of balanced accuracy, a fifth
   of the functional range between chance and solution -- and it applies to
   the one-sided lower bound, not to the point estimate.
2. Per-class evidence is computed per seed and bootstrapped between seeds.
   Two point estimates above chance would let a class squeak past on noise.
3. `signed_branch` is reported and is NOT a fourth confirmatory contrast: in
   a binary task it re-expresses the same separation balanced accuracy
   already carries.
4. Whether a seed contains both histories is decided from world truth BEFORE
   any agent runs.  A tied row or a learner that failed, with both histories
   available, is a scientific result and is not replaced.
5. The shuffle must be strong, not merely marginal-preserving.
6. The bootstrap has its own sealed seed and a named interval method.

And the pilot diagnostic is narrowed: what was established is a fact about
the pilot's snapshots, not a general property of U1.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))

import n10_preregistration as v1  # noqa: E402

DESTINO = RAIZ / "docs" / "N10_CAMPAIGN_MANIFEST_V2.json"
SCHEMA = "terrario.n10-preregistration/v2"

ANALISIS = {
    "unit": "TRAINING SEED / TRAINED SNAPSHOT",
    "resamples": 10000,
    "bootstrap_seed": 20260921,
    "interval_method": (
        "paired bootstrap over seed-level deltas; the DECISION rule uses the "
        "one-sided 95% lower confidence bound (the 5th percentile of the "
        "resampled distribution). A two-sided 95% interval (2.5th, 97.5th) is "
        "reported alongside and is descriptive only"),
    "conjunction": (
        "intersection-union: acquisition, lesion and shuffle must ALL clear "
        "their bound. No retrospective selection of the favourable contrast"),
    "per_class": (
        "accuracy_H0 and accuracy_H1 are computed PER SEED and bootstrapped "
        "between seeds; BOTH lower bounds must exceed 0.5. Two point "
        "estimates above chance would let a class pass on noise"),
    "signed_branch": (
        "reported for direction, NOT a fourth confirmatory contrast: in a "
        "binary task it re-expresses the separation balanced accuracy carries"),
}

UMBRALES_V2 = {
    "structural": dict(v1.UMBRALES["structural"], **{
        "seed_evaluability": (
            "decided from GeneratedWorld.stations BEFORE any agent runs: both "
            "history classes must be present in the acquisition world and in "
            "the evaluation world"),
        "shuffle_strength": (
            "P(policy_token == actual_history) <= 0.75, reported against the "
            "chance floor (n0^2 + n1^2)/n^2. Preserving the marginals is not "
            "enough: a permutation leaving most tokens in place would make "
            "arm C nearly arm A with noise"),
    }),
    "statistical": {
        "BA_A": {"rule": "LCB95(BA_A) >= 0.75",
                 "derivation": "halfway between the chance floor 0.5 and the "
                               "ceiling 1.0: the mapping has to be more "
                               "present than absent"},
        "acquisition_gain": {"rule": "LCB95(delta_acquisition) > 0",
                             "derivation": "strictly positive"},
        "lesion_loss": {
            "rule": "LCB95(delta_lesion) >= 0.10",
            "derivation": "PREREGISTERED MINIMUM RELEVANT CAUSAL EFFECT: ten "
                          "points of balanced accuracy, a fifth of the "
                          "functional range between chance (0.5) and solution "
                          "(1.0). Declared as a bar we are willing to call "
                          "causal, NOT derived from the size we expect"},
        "shuffle_loss": {"rule": "LCB95(delta_shuffle) >= 0.10",
                         "derivation": "the same declared minimum effect"},
        "per_history": {"rule": "LCB95(accuracy_H0) > 0.5 AND "
                                "LCB95(accuracy_H1) > 0.5",
                        "derivation": "chance in the binary task, bounded per "
                                      "class rather than point-estimated"},
    },
}


def construir() -> dict:
    base = v1.construir()
    archivos = {p: v1.digest(RAIZ / p) for p in
                v1.CODIGO_SELLADO + ("scripts/n10_preregistration_v2.py",)}
    m = dict(base)
    m.update({
        "schema": SCHEMA,
        "revision": 2,
        "supersedes": {"revision": 1,
                       "artifact": "docs/N10_CAMPAIGN_MANIFEST_V1.json",
                       "status": "SUPERSEDED, preserved unedited",
                       "reason": "statistical and procedural corrections made "
                                 "while no confirmatory seed had been spent"},
        "sealed_code": archivos,
        "sealed_code_root_hash": hashlib.sha256(
            json.dumps(archivos, sort_keys=True).encode()).hexdigest(),
        "analysis": ANALISIS,
        "thresholds": UMBRALES_V2,
        "arms_unchanged_from_v1": True,
        "pilot_diagnostics": {
            "EXPLORATION_EXPLAINS_RESIDUAL_WITHIN_PILOT": "ESTABLISHED",
            "scope": "a fact about the pilot's snapshots, not a general "
                     "property of U1",
            "evidence": base["pilot_diagnostics"]["evidence"],
        },
    })
    return m


if __name__ == "__main__":
    m = construir()
    if "--write" in sys.argv:
        DESTINO.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n")
        propio = hashlib.sha256(DESTINO.read_bytes()).hexdigest()
        v1_hash = hashlib.sha256(
            (RAIZ / "docs" / "N10_CAMPAIGN_MANIFEST_V1.json").read_bytes()).hexdigest()
        print(f"V2 escrito: {DESTINO.relative_to(RAIZ)}")
        print(f"  commit             {m['repo_commit']}")
        print(f"  código sellado     {len(m['sealed_code'])} ficheros")
        print(f"  raíz del código    {m['sealed_code_root_hash']}")
        print(f"  manifiesto semillas {m['seed_manifest_hash']}")
        print(f"  bootstrap seed     {m['analysis']['bootstrap_seed']}")
        print(f"  V2 sha256          {propio}")
        print(f"  V1 sha256          {v1_hash}  (intacto)")
    else:
        print(json.dumps(m, indent=2, ensure_ascii=False))
