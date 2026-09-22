#!/usr/bin/env python3
"""N1.0 · el paquete de evidencia. Referencia por hash, no duplica."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "docs" / "N10_EVIDENCE_BUNDLE_V1.json"

ARTEFACTOS = {
    "preregistration_v1_superseded": "docs/N10_CAMPAIGN_MANIFEST_V1.json",
    "preregistration_v2_superseded": "docs/N10_CAMPAIGN_MANIFEST_V2.json",
    "preregistration_v3_authoritative": "docs/N10_CAMPAIGN_MANIFEST_V3.json",
    "preregistration_doc_v1": "docs/N10_PREREGISTRATION_V1.md",
    "preregistration_doc_v2": "docs/N10_PREREGISTRATION_V2.md",
    "raw_results": "docs/N10_RAW_RESULTS.json",
    "seed_summary": "docs/N10_SEED_SUMMARY.json",
    "confirmatory_report": "docs/N10_CONFIRMATORY_REPORT.md",
    "campaign_runner": "scripts/n10_confirmatory.py",
    "independent_reanalysis": "scripts/n10_reanalysis.py",
    "learner": "terrario/lab/n10_u1.py",
    "causal_form_spec": "terrario/lab/n10_u1_spec.py",
    "instrument": "terrario/lab/n10_instrument.py",
    "arms": "terrario/lab/n10_arms.py",
}

CLAIM = (
    "Under the preregistered scope of N1.0, U1 acquired by experience a "
    "correspondence between a retained historical trace and an action. With "
    "learning frozen and the present observation equivalent, the correct "
    "history allowed the appropriate action to be selected differentially. "
    "Decoupling the trace from the real history removed the solution; "
    "blocking its read collapsed the expression to the naive regime.")

NON_CLAIMS = (
    "acquisition of the memory mechanism", "autonomous representation formation",
    "episodic memory", "spatial memory", "semantic memory",
    "causal understanding", "planning",
    "generalisation to arbitrary histories", "general intelligence",
    "consciousness",
    "SUPPLIED and therefore not acquired: the tokenisation, the memory slot, "
    "the update rule and the action repertoire. What was acquired is the "
    "token-to-action correspondence and nothing else",
)

LIMITACIONES = {
    "LIMIT-N10-01": {
        "title": "MEMORY_READ_LESION collapses to the naive regime",
        "statement": (
            "Arm B sends the policy to the EMPTY token, whose context was "
            "never trained, so both table entries stay at the 0.0 default and "
            "the tie-break branch is always taken. The naive organism has an "
            "entirely empty table and reaches the same branch. Verified in "
            "code: both consume exactly two RNG draws per decision and return "
            "ACTIONS[second draw], so they are the same function of the same "
            "stream -- the equivalence is STRUCTURAL, not coincidental. "
            "Therefore lesion_loss is NOT statistically independent evidence "
            "from acquisition_gain: they are the same vector, and the "
            "intersection-union test has three named components and two "
            "distinct ones."),
        "evidence": "BA(B) == BA(N) in 32/32 replicas in both readouts; the "
                    "raw carries no per-decision actions, so from the raw "
                    "alone the classification is BEHAVIORAL and the stronger "
                    "STRUCTURAL reading comes from the code audit",
        "conditional_on": (
            "novelty = 0.0 in the sealed demand, and the cue-before-door "
            "geometry. Neither is enforced by an assertion. Under a demand "
            "with novelty > 0 a novel station's cue would go undetected and "
            "Q[EMPTY, a] WOULD be written, and arm B would stop tying"),
        "not_fixed_here": "a more discriminating lesion would have to preserve "
                          "a context inside the learned support and remove the "
                          "historical information specifically. That is "
                          "another study",
    },
    "LIMIT-N10-02": {
        "title": "The per-decision rows were produced and not preserved",
        "statement": (
            "DecisionRow carries the twelve primitive fields the closure asks "
            "for. The campaign runner reduced them to eight aggregates per arm "
            "and dropped the tuples: 32 replicas x 2 readouts x 4 arms x 128 "
            "decisions = 32,768 rows destroyed. The most primitive object "
            "recoverable is a per-arm 2x2 contingency table, and only by "
            "inference from per-class rates times class counts."),
        "consequence": "the bundle reproduces its numbers from its own "
                       "numbers. No third party can audit a balanced accuracy "
                       "against anything more primitive than its own two "
                       "components",
        "minimal_artefact_that_would_have_closed_it":
            "one JSONL of DecisionRow.as_record() per arm per readout — the "
            "object already existed in memory and needed one write",
        "not_fixed_here": "re-running the campaign would not repair a "
                          "preservation gap, and is forbidden",
    },
    "LIMIT-N10-03": {
        "title": "The decision-parity gate cannot fail as constructed",
        "statement": (
            "decision_id is assigned as len(filas) at append time, so it is "
            "always 0..n-1 and the parity check across A, B and C compares "
            "three copies of the same range. The gate declares itself as "
            "'identical sequences, not merely equal counts' and, under this "
            "construction, it tests exactly the counts. The stored id arrays "
            "are about a third of the raw file and carry one bit each."),
        "consequence": "a criterion that cannot fail is not a criterion, which "
                       "is the defect class this project hunts. The parity it "
                       "was meant to guarantee is real -- the arms share a "
                       "world and a seed -- but this gate is not what "
                       "establishes it",
        "not_fixed_here": "it would need ids derived from the world (station "
                          "index and step) rather than from the append order",
    },
}


def digest(p: str) -> str:
    return hashlib.sha256((RAIZ / p).read_bytes()).hexdigest()


def construir() -> dict:
    m = json.loads((RAIZ / ARTEFACTOS["preregistration_v3_authoritative"]).read_text())
    reana = subprocess.run(
        [str(RAIZ / ".venv/bin/python"), str(RAIZ / "scripts/n10_reanalysis.py"), "--json"],
        capture_output=True, text=True, cwd=str(RAIZ),
        env={"PYTHONPATH": str(RAIZ), "PATH": "/usr/bin:/bin"})
    recon = json.loads(reana.stdout) if reana.returncode == 0 else {"error": reana.stderr[-400:]}
    return {
        "schema": "terrario.n10-evidence-bundle/v1",
        "claim": CLAIM,
        "non_claims": list(NON_CLAIMS),
        "verdict": "NEW_DF_DETECTED",
        "independent_contrast_count": recon.get("independent_contrast_count"),
        "artifacts": {k: {"path": v, "sha256": digest(v)}
                      for k, v in ARTEFACTOS.items()},
        "sealed_code_root_hash": m["sealed_code_root_hash"],
        "seed_manifest_hash": m["seed_manifest_hash"],
        "campaign_head": json.loads(
            (RAIZ / ARTEFACTOS["raw_results"]).read_text())["seal"]["head"],
        "independent_reconstruction": {
            "reproduces": recon.get("verdict") == "NEW_DF_DETECTED"
                          and recon.get("campaign_valid") is True,
            "verdict": recon.get("verdict"),
            "bootstrap": {k: recon["bootstrap"][k]
                          for k in ("acquisition_gain", "lesion_loss",
                                    "shuffle_loss", "BA_A")}
            if "bootstrap" in recon else recon,
            "per_class_bounds_degenerate": recon.get("per_class_bounds_degenerate"),
        },
        "limitations": LIMITACIONES,
        "version_genealogy": {
            "V1": "initial preregistration · SUPERSEDED, preserved",
            "V2": "statistical and protocol corrections · SUPERSEDED, preserved",
            "V3": "added the executable B/C interventions and the confirmatory "
                  "runner to the sealed set · AUTHORITATIVE",
        },
        "evidence_bundle_complete": False,
        "evidence_bundle_incomplete_because":
            "LIMIT-N10-02: the question 'what data did it produce' is answered "
            "with aggregates. The primitive observations were produced and not "
            "written",
        "not_admitted_to_evidence_graph":
            "evidence existing is not evidence admitted; admission is a "
            "separate decision and has not been taken",
    }


if __name__ == "__main__":
    b = construir()
    if "--write" in sys.argv:
        DESTINO.write_text(json.dumps(b, indent=2, ensure_ascii=False) + "\n")
        print(f"bundle: {DESTINO.relative_to(RAIZ)}")
        print(f"  sha256          {hashlib.sha256(DESTINO.read_bytes()).hexdigest()}")
        print(f"  artefactos      {len(b['artifacts'])}")
        print(f"  reproduce       {b['independent_reconstruction']['reproduces']}")
        print(f"  limitaciones    {list(b['limitations'])}")
        print(f"  bundle completo {b['evidence_bundle_complete']}")
    else:
        print(json.dumps(b, indent=2, ensure_ascii=False))
