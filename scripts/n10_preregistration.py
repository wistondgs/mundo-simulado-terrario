#!/usr/bin/env python3
"""N1.0 · el preregistro, con los hashes LEÍDOS y no tecleados.

The project's catalogued failure is a campaign that seals by transcribing
values into constants with nothing checking the transcription against the
document.  Every digest below is computed from the file on disk at the moment
this runs, and the commit comes from git.

Nothing here runs the campaign.  It writes down what the campaign will be, so
that afterwards nobody can decide what it was.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
PREREG = RAIZ / "docs" / "N10_CAMPAIGN_MANIFEST_V1.json"

SCHEMA = "terrario.n10-preregistration/v1"

#: Todo lo que, si cambia, invalida el preregistro.
CODIGO_SELLADO = (
    "terrario/lab/n10_u1.py",
    "terrario/lab/n10_u1_spec.py",
    "terrario/lab/n10_instrument.py",
    "terrario/lab/world_generator.py",
    "terrario/lab/world_oracles.py",
    "terrario/world/state.py",
    "terrario/world/transition.py",
    "terrario/core/types.py",
    "terrario/core/contracts.py",
    "scripts/n10_preregistration.py",
)

#: Semillas frescas. Disjuntas del piloto (train 100-107, eval 0-3), de las
#: fixtures (0, 7, 8) y de todo lo mirado durante el desarrollo.
N_REPLICAS = 32
TRAIN_BASE, EVAL_BASE, SHUFFLE_BASE, RESERVE_BASE = 2600000, 2700000, 2800000, 2900000
N_RESERVE = 8


def semillas() -> dict:
    return {
        "n_replicas": N_REPLICAS,
        "train": [TRAIN_BASE + i for i in range(N_REPLICAS)],
        "eval": [EVAL_BASE + i for i in range(N_REPLICAS)],
        "shuffle": [SHUFFLE_BASE + i for i in range(N_REPLICAS)],
        "reserve": [RESERVE_BASE + i for i in range(N_RESERVE)],
        "namespaces": "N10/TRAIN/i, N10/EVAL/i, N10/SHUFFLE/i — streams disjuntos",
        "disjoint_from": {"pilot_train": list(range(100, 108)),
                          "pilot_eval": [0, 1, 2, 3],
                          "fixtures": [0, 7, 8]},
    }


CONFIG = {
    "economy": {"initial_energy": 250.0, "max_energy": 400.0,
                "step_energy_cost": 0.15, "gain": 4.0, "loss": 4.0,
                "safe": 0.0, "low_energy": 0.0},
    "apparatus_normalization": {"enabled": True, "baseline_energy": 250.0,
                                "applied": "after learn, before the next observation",
                                "kind": "APPARATUS_INTERVENTION"},
    "scenario": {"capability": "EPMEM-A1", "expose_time_fraction": False,
                 "num_channels": 4, "view_radius": 2},
    "budget": {"acquisition_decisions_per_train_seed": 512,
               "acquisition_stations": 512,
               "evaluation_decisions_per_eval_seed": 128,
               "evaluation_stations": 128,
               "derivation": "the pilot's own totals, read from its run: 8x64 "
                             "acquisition decisions and 4x32 evaluation ones"},
    "learner": {"alpha_train": 0.3, "epsilon_train": 0.2,
                "epsilon_primary_eval": 0.0, "epsilon_secondary_eval": 0.2,
                "rule": "Q(tau,a) <- Q(tau,a) + alpha * [c - Q(tau,a)]",
                "feedback": "transition.consequence_t1.energy_delta",
                "initialization": "memory EMPTY, Q empty, ties by a dedicated draw",
                "frozen_from_pilot": True,
                "not_optimised": "no grid search, no selection on confirmatory data"},
}

ARMS = {
    "N": {"name": "NAIVE", "intervention": "none; the pre-acquisition snapshot",
          "purpose": "shows behaviourally that no mapping is present before "
                     "experience; CF8 already showed it structurally"},
    "A": {"name": "COMPLETE", "intervention": "none",
          "memory_read": True, "shuffle": False, "learning": False},
    "B": {"name": "MEMORY_READ_LESION",
          "intervention": "the token keeps being written; the policy cannot "
                          "consume its retained value",
          "memory_read": False, "shuffle": False, "learning": False,
          "not_called": "ablation — the write path continues"},
    "C": {"name": "HISTORY_SHUFFLED",
          "intervention": "a sealed deterministic permutation replaces the token "
                          "the policy reads; world, Q, observations and "
                          "consequences untouched",
          "memory_read": True, "shuffle": True, "learning": False},
}

METRICAS = {
    "primary": {
        "balanced_functional_accuracy":
            "BA = [P(correct|H0) + P(correct|H1)] / 2, because the H0/H1 split "
            "is not exactly even; chance is 0.5",
        "signed_branch":
            "B_s = P(UP|H_up) - P(UP|H_down); +1 perfect, 0 no governance, "
            "-1 fully inverted. The absolute value is reported too but is not "
            "the diagnostic of direction",
    },
    "contrasts_per_seed": {
        "acquisition_gain": "BA(A) - BA(N)",
        "lesion_loss": "BA(A) - BA(B)",
        "shuffle_loss": "BA(A) - BA(C)",
    },
    "inference": {
        "unit": "TRAINING SEED / TRAINED SNAPSHOT — decisions from one learner "
                "are not independent replicates",
        "procedure": "paired bootstrap over seed-level deltas, 10000 resamples, "
                     "95% interval and lower bound",
        "conjunction": "intersection-union: all three contrasts must clear "
                       "their bound; no retrospective selection of the "
                       "favourable one",
    },
}

UMBRALES = {
    "structural": {
        "snapshot_parity": "hash(theta_A) == hash(theta_B) == hash(theta_C), exact",
        "decision_parity": "set(decision_ids) identical across A, B and C — not "
                           "merely equal counts",
        "evaluation_freeze": "theta digest identical before and after every "
                             "evaluation, exact",
        "same_present": "every comparable decision group collapses to ONE "
                        "obs_hash holding both histories",
        "world_truth_nonleakage": "PASS on the sealed commit",
        "exposure": "both history classes present in acquisition and in "
                    "evaluation for every seed",
    },
    "statistical": {
        "BA_A_lower_bound": {
            "value": 0.75,
            "derivation": "halfway between the chance floor 0.5 and the ceiling "
                          "1.0: the mapping has to be more present than absent",
        },
        "acquisition_gain_lower_bound": {"value": 0.0, "derivation": "strictly positive"},
        "lesion_loss_lower_bound": {
            "value": 0.10,
            "derivation": "a learner with no usable history sits at 0.5 and the "
                          "pilot's frozen BA at epsilon 0 was 1.0, so the "
                          "expected loss is about 0.5; 0.10 is a fifth of that, "
                          "set so a hair's-breadth difference is not called causal",
        },
        "shuffle_loss_lower_bound": {"value": 0.10, "derivation": "same as the lesion"},
        "per_history_lower_bound": {
            "value": 0.5,
            "derivation": "chance in the binary task; BOTH histories must clear "
                          "it in arm A, so a high mean from solving one class is "
                          "not enough",
        },
    },
}

INVALIDATION = (
    "observation leakage at a comparable decision",
    "any instrument gate failing on the sealed commit",
    "code differing from the sealed hashes",
    "snapshot inequality across A, B and C",
    "decision-id parity failure",
    "any parameter update during evaluation",
    "history_id reaching the organism by any route",
    "feedback taken from anything but consequence_t1.energy_delta",
    "a missing history class in a seed's evaluation",
    "a corrupted or incomplete trace",
    "any protocol deviation not registered before the run",
)

RESERVE_RULE = (
    "A seed is replaced ONLY when the GENERATED WORLD makes it unevaluable — "
    "its evaluation contains a single history class, so balanced accuracy has "
    "no second term. Marked SEED_NOT_EVALUABLE and replaced by the next sealed "
    "reserve seed, in order. Never replaced because the agent did badly, and "
    "every replacement is recorded."
)

VERDICTS = ("INVALID", "INDETERMINATE", "MEASURED_ZERO", "NEW_DF_DETECTED")


def digest(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def commit() -> str:
    r = subprocess.run(["git", "-C", str(RAIZ), "rev-parse", "HEAD"],
                       capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else "UNKNOWN"


def construir() -> dict:
    archivos = {p: digest(RAIZ / p) for p in CODIGO_SELLADO}
    s = semillas()
    manifiesto = {
        "schema": SCHEMA,
        "claim": (
            "Under the preregistered scope of N1.0, U1 acquired by experience "
            "an association between a retained historical trace and a later "
            "action. With an equivalent present observation and learning "
            "frozen, that history functionally modulated the decision; "
            "interrupting its read or decoupling it from the real history "
            "reduced the appropriate behaviour."),
        "claim_does_not_assert": (
            "acquired memory", "understanding of its past", "learned causality",
            "general experience", "emergent intelligence",
            "a general cognitive degree of freedom"),
        "three_claims_kept_apart": {
            "A_ACQUISITION": "U1 learns tau->action from experience",
            "B_EXPRESSION": "frozen U1 uses tau to choose under identical O",
            "C_CAUSAL_DEPENDENCE": "lesion and shuffle degrade that relation",
            "rule": "NEW_DF_DETECTED requires all three",
        },
        "repo_commit": commit(),
        "sealed_code": archivos,
        "sealed_code_root_hash": hashlib.sha256(
            json.dumps(archivos, sort_keys=True).encode()).hexdigest(),
        "config": CONFIG,
        "arms": ARMS,
        "seeds": s,
        "seed_manifest_hash": hashlib.sha256(
            json.dumps(s, sort_keys=True).encode()).hexdigest(),
        "reserve_seed_rule": RESERVE_RULE,
        "metrics": METRICAS,
        "thresholds": UMBRALES,
        "invalidation_rules": list(INVALIDATION),
        "possible_verdicts": list(VERDICTS),
        "pilot_diagnostics": {
            "EXPLORATION_EXPLAINS_RESIDUAL": "ESTABLISHED",
            "evidence": "the same reproduced snapshot 785eef13841936be gives "
                        "acc 0.9297 / BA 0.9274 / signed_branch +0.8548 at "
                        "epsilon 0.2 and acc 1.0000 / BA 1.0000 / "
                        "signed_branch +1.0000 at epsilon 0; the prediction "
                        "under the exploration hypothesis is 0.90",
        },
    }
    return manifiesto


if __name__ == "__main__":
    import sys
    m = construir()
    if "--write" in sys.argv:
        PREREG.write_text(json.dumps(m, indent=2, ensure_ascii=False) + "\n")
        propio = hashlib.sha256(PREREG.read_bytes()).hexdigest()
        print(f"manifiesto escrito: {PREREG.relative_to(RAIZ)}")
        print(f"  commit            {m['repo_commit'][:12]}")
        print(f"  código sellado    {len(m['sealed_code'])} ficheros · "
              f"raíz {m['sealed_code_root_hash'][:16]}")
        print(f"  semillas          {m['seeds']['n_replicas']} réplicas · "
              f"manifiesto {m['seed_manifest_hash'][:16]}")
        print(f"  manifiesto        {propio[:16]}")
    else:
        print(json.dumps(m, indent=2, ensure_ascii=False))
