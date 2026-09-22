"""N1.0 · el cierre científico. Reconstrucción, integridad y coherencia.

Nothing here re-runs the experiment. These tests read preserved files and
check that the reported numbers can be rebuilt from them, that the sealed
artefacts have not moved, and that the claim and the non-claims do not
contradict each other.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "scripts"))

BUNDLE = json.loads((RAIZ / "docs" / "N10_EVIDENCE_BUNDLE_V1.json").read_text())


def test_the_reanalysis_reads_the_raw_and_never_the_published_summary():
    """Blindness has to be visible in the code, not promised in prose."""
    import ast
    fuente = (RAIZ / "scripts" / "n10_reanalysis.py").read_text()
    arbol = ast.parse(fuente)
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Expr) and isinstance(nodo.value, ast.Constant) \
                and isinstance(nodo.value.value, str):
            nodo.value.value = ""
    codigo = ast.unparse(arbol)
    # Los nombres prohibidos sólo pueden aparecer en la lista que los prohíbe.
    assert codigo.count("N10_SEED_SUMMARY") == 1
    assert codigo.count("N10_CONFIRMATORY_REPORT") == 1
    assert "PROHIBIDO" in codigo


def test_the_reanalysis_reproduces_the_published_numbers():
    from n10_reanalysis import reconstruir
    r = reconstruir()
    publicado = json.loads((RAIZ / "docs" / "N10_SEED_SUMMARY.json").read_text())
    for nombre in ("acquisition_gain", "lesion_loss", "shuffle_loss"):
        a = r["bootstrap"][nombre]
        b = publicado["contrasts_primary"][nombre]
        assert a["estimate"] == pytest.approx(b["estimate"], abs=1e-12), nombre
        assert a["lcb95"] == pytest.approx(b["lcb95"], abs=1e-12), nombre
        assert a["ci95"] == pytest.approx(b["ci95"], abs=1e-12), nombre
    assert r["verdict"] == "NEW_DF_DETECTED"
    assert r["campaign_valid"] is True


def test_every_validity_gate_is_recomputed_and_passes():
    from n10_reanalysis import reconstruir
    g = reconstruir()["validity_gates"]
    assert len(g) == 10
    assert all(g.values()), [k for k, v in g.items() if not v]


def test_the_sealed_preregistrations_have_not_moved():
    esperado = {
        "docs/N10_CAMPAIGN_MANIFEST_V1.json":
            "4d18ffcc29322f916901fe7c7b4738e5f016b7cc7d81bdd978aec5d7e143703f",
        "docs/N10_CAMPAIGN_MANIFEST_V2.json":
            "762d5e6a7c7a1eaa680a2852569e2861078dd1dc86ea0a041c246bb3c645297f",
        "docs/N10_CAMPAIGN_MANIFEST_V3.json":
            "de93859afe4486440752fc3a335d45e6aca496e12bec84d4160bce1f4dfc861c",
    }
    for ruta, h in esperado.items():
        vivo = hashlib.sha256((RAIZ / ruta).read_bytes()).hexdigest()
        assert vivo == h, f"{ruta} cambió"


def test_the_bundle_hashes_match_the_files_on_disk():
    for nombre, a in BUNDLE["artifacts"].items():
        vivo = hashlib.sha256((RAIZ / a["path"]).read_bytes()).hexdigest()
        assert vivo == a["sha256"], nombre


def test_the_bundle_answers_every_question_a_consumer_would_ask():
    for clave in ("claim", "non_claims", "verdict", "artifacts",
                  "sealed_code_root_hash", "seed_manifest_hash",
                  "campaign_head", "independent_reconstruction",
                  "limitations", "version_genealogy"):
        assert clave in BUNDLE and BUNDLE[clave], clave
    assert BUNDLE["independent_reconstruction"]["reproduces"] is True


def test_the_bundle_declares_itself_incomplete_and_says_why():
    """The primitive observations were produced and not written, so the
    question «what data did it produce» is answered with aggregates."""
    assert BUNDLE["evidence_bundle_complete"] is False
    assert "LIMIT-N10-02" in BUNDLE["evidence_bundle_incomplete_because"]


def test_the_three_limitations_are_recorded_with_what_would_have_closed_them():
    lim = BUNDLE["limitations"]
    assert set(lim) == {"LIMIT-N10-01", "LIMIT-N10-02", "LIMIT-N10-03"}
    for k, v in lim.items():
        assert v["title"] and v["statement"]
        assert "not_fixed_here" in v, k


def test_the_contrasts_are_counted_as_two_and_not_three():
    """B equals N structurally, so lesion_loss is the same vector as
    acquisition_gain. Calling them three independent causal contrasts would
    say more than was measured."""
    from n10_reanalysis import reconstruir
    r = reconstruir()
    assert r["independent_contrast_count"] == 2
    assert r["b_equals_n_from_raw"]["replicas_identical_BA"] == 32
    assert r["bootstrap"]["lesion_loss"]["estimate"] == \
        r["bootstrap"]["acquisition_gain"]["estimate"]
    assert BUNDLE["independent_contrast_count"] == 2


def test_the_per_class_bounds_are_degenerate_and_that_is_recorded():
    """Accuracy per class in arm A is exactly 1.0 in all 32 replicas at
    epsilon 0, so every bootstrap resample has mean 1.0. The bound is
    trivially satisfied rather than precisely estimated, and the informative
    readout for that question is the secondary one."""
    from n10_reanalysis import reconstruir
    assert reconstruir()["per_class_bounds_degenerate"] is True
    assert BUNDLE["independent_reconstruction"]["per_class_bounds_degenerate"] is True


def test_the_claim_and_the_non_claims_do_not_overlap():
    claim = BUNDLE["claim"].lower()
    for nc in ("general intelligence", "consciousness", "causal understanding",
               "episodic memory", "planning"):
        assert nc not in claim, nc
    assert "acquired by experience" in claim
    assert any("SUPPLIED" in n for n in BUNDLE["non_claims"])


def test_nothing_was_admitted_to_the_evidence_graph():
    assert "not_admitted_to_evidence_graph" in BUNDLE
    assert "separate decision" in BUNDLE["not_admitted_to_evidence_graph"]


def test_the_composition_map_was_not_touched():
    """N1.0 is an acquisition study, not a composition between two
    proto-organs, so no COMPOSES_TO edge was invented for it."""
    from terrario.lab.hypergraph.primitive_composition import edges_v01
    aristas = edges_v01()
    assert len(aristas) == 6
    assert all(e.provenance == "HISTORICAL" for e in aristas)
    assert not any("N1" in e.id or "U1" in e.id for e in aristas)
