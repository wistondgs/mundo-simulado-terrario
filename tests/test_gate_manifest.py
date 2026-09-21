"""Contracts for the sealed gate inventory.

The central case is a replay: the fusion campaign really did seal `F-9` for
passivity and really did evaluate it as the tick, and no instrument in the tree
could see it.  If this module cannot see it either, it is decoration.
"""

from __future__ import annotations

import pytest

from terrario.lab.preregistration.gate_manifest import (
    GateManifest, GateManifestError, GateOutcome, SealedGate, manifest_from_payload,
    reconcile,
)


def _gate(gate_id: str, certifies: str, **kwargs) -> SealedGate:
    base = {
        "statement": f"what {gate_id} certifies, in words",
        "criterion": "fingerprints identical before and after measuring",
        "negative_fixture": f"{gate_id}-negative",
    }
    return SealedGate(gate_id=gate_id, certifies=certifies,
                      certifies_revision=kwargs.pop("revision", "v1"), **{**base, **kwargs})


def _ran(gate: SealedGate, *, passed: bool = True, fell: bool | None = True) -> GateOutcome:
    return GateOutcome(gate_id=gate.gate_id, certifies=gate.certifies,
                       certifies_revision=gate.certifies_revision, passed=passed,
                       evidence="fingerprints equal", negative_fixture_fell=fell)


# --- the fusion, as it actually happened -----------------------------------------

#: `F-0`..`F-9` exactly as `ORGANISM_FUSION_HM_01_PREREGISTRADO.md` seals them.
FUSION = GateManifest(gates=(
    _gate("F-0", "SINGLE_CORE"), _gate("F-1", "LINEAGE_INTACT"),
    _gate("F-2", "MEMORY_WITHOUT_DRIFT"), _gate("F-3", "MEMORY_SEMANTICS"),
    _gate("F-4", "COEXISTENCE"), _gate("F-5", "JOINT_USE"),
    _gate("F-6", "INTERACTION"), _gate("F-7", "NO_LEAKAGE"),
    _gate("F-8", "POLICY_INTACT"), _gate("F-9", "PASSIVITY"),
))


def test_the_sealed_run_reconciles():
    outcome = reconcile(FUSION, [_ran(g) for g in FUSION.gates])
    assert outcome.consistent and outcome.failures == ()
    assert outcome.evaluated == outcome.sealed == 10


def test_the_fusion_substitution_is_refused_and_names_both_meanings():
    """The historical defect: nine rows, `F-9` evaluating the tick.

    Before this module the run reported `PASS` for a true statement under a
    number that belonged to something else, and nothing disagreed."""
    como_ocurrio = [_ran(g) for g in FUSION.gates if g.gate_id not in {"F-2", "F-9"}]
    como_ocurrio.append(GateOutcome(
        gate_id="F-9", certifies="TICK_REQUIRED", certifies_revision="v1",
        passed=True, evidence="skip_tick > joint[ON,ON]", negative_fixture_fell=True))

    outcome = reconcile(FUSION, como_ocurrio)

    assert not outcome.consistent
    assert "GATE_CERTIFIES_MISMATCH:F-9:sealed=PASSIVITY@v1:run=TICK_REQUIRED@v1" \
        in outcome.failures
    # And the omission that the substitution was hiding is reported separately,
    # which is what makes "nine of ten" legible as two distinct defects.
    assert "SEALED_GATE_NOT_EVALUATED:F-2" in outcome.failures
    assert "SEALED_GATE_NOT_EVALUATED:F-9" not in outcome.failures


def test_a_number_that_passes_under_the_wrong_meaning_is_not_a_pass():
    """`passed=True` never rescues a mismatch: admission is about identity."""
    outcome = reconcile(FUSION, [
        *[_ran(g) for g in FUSION.gates if g.gate_id != "F-9"],
        GateOutcome("F-9", "TICK_REQUIRED", "v1", True, "evidence", True)])
    assert not outcome.consistent


# --- what the manifest refuses to seal --------------------------------------------

def test_two_gates_cannot_certify_the_same_property():
    """How an inventory keeps its count while a property drops out."""
    with pytest.raises(GateManifestError, match="both certify"):
        GateManifest(gates=(_gate("F-8", "PASSIVITY"), _gate("F-9", "PASSIVITY")))


def test_the_same_property_at_another_revision_is_another_property():
    manifest = GateManifest(gates=(_gate("F-8", "PASSIVITY"),
                                   _gate("F-9", "PASSIVITY", revision="v2")))
    assert len(manifest.gates) == 2


def test_a_gate_without_a_negative_fixture_cannot_be_sealed():
    """The rule every oracle in both lineages already states."""
    with pytest.raises(GateManifestError, match="negative_fixture"):
        SealedGate(gate_id="F-9", certifies="PASSIVITY", certifies_revision="v1",
                   statement="s", criterion="c", negative_fixture="  ")


def test_a_gate_without_a_stated_meaning_cannot_be_sealed():
    with pytest.raises(GateManifestError, match="certifies"):
        SealedGate(gate_id="F-9", certifies="", certifies_revision="v1",
                   statement="s", criterion="c", negative_fixture="f")


def test_an_empty_manifest_is_refused():
    with pytest.raises(GateManifestError, match="certifies nothing"):
        GateManifest(gates=())


def test_duplicate_gate_ids_are_refused():
    with pytest.raises(GateManifestError, match="duplicate gate id"):
        GateManifest(gates=(_gate("F-9", "PASSIVITY"), _gate("F-9", "TICK_REQUIRED")))


# --- what a run cannot get away with ----------------------------------------------

def test_a_gate_nobody_sealed_is_refused():
    outcome = reconcile(FUSION, [*[_ran(g) for g in FUSION.gates],
                                 _ran(_gate("F-10", "INVENTED_AFTERWARDS"))])
    assert "GATE_NOT_SEALED:F-10" in outcome.failures


def test_a_negative_fixture_that_did_not_fall_is_a_failure():
    outcome = reconcile(FUSION, [_ran(g, fell=(g.gate_id != "F-3")) for g in FUSION.gates])
    assert "GATE_NEGATIVE_FIXTURE_DID_NOT_FALL:F-3" in outcome.failures


def test_a_fixture_nobody_ran_is_reported_apart_from_a_failure():
    """Not proven is not refuted, and collapsing them would hide the difference."""
    outcome = reconcile(FUSION, [_ran(g, fell=(None if g.gate_id == "F-3" else True))
                                 for g in FUSION.gates])
    assert outcome.unproven_fixtures == ("F-3",)
    assert not any("F-3" in f for f in outcome.failures)


def test_a_gate_reported_twice_is_refused():
    outcome = reconcile(FUSION, [*[_ran(g) for g in FUSION.gates], _ran(FUSION.gates[0])])
    assert "GATE_REPORTED_TWICE:F-0" in outcome.failures


def test_evidence_is_required_even_when_the_gate_passes():
    outcome = reconcile(FUSION, [
        *[_ran(g) for g in FUSION.gates if g.gate_id != "F-1"],
        GateOutcome("F-1", "LINEAGE_INTACT", "v1", True, "   ", True)])
    assert "GATE_EVIDENCE_ABSENT:F-1" in outcome.failures


def test_a_consistent_campaign_can_be_entirely_negative():
    """Consistency asks whether the promised gates were evaluated under the
    promised meanings -- not whether they passed.  A negative that reconciles is
    a publishable result, and refusing it here would push campaigns to report
    green."""
    outcome = reconcile(FUSION, [_ran(g, passed=False) for g in FUSION.gates])
    assert outcome.consistent


# --- identity survives the round trip ---------------------------------------------

def test_a_manifest_rebuilt_from_its_payload_keeps_its_hash():
    rebuilt = manifest_from_payload({**FUSION.payload(),
                                     "manifest_hash": FUSION.manifest_hash})
    assert rebuilt.manifest_hash == FUSION.manifest_hash


def test_a_tampered_payload_is_refused_instead_of_trusted():
    tampered = FUSION.payload()
    tampered["gates"][9]["certifies"] = "TICK_REQUIRED"
    with pytest.raises(GateManifestError, match="does not match its content"):
        manifest_from_payload({**tampered, "manifest_hash": FUSION.manifest_hash})


def test_rewording_the_statement_changes_the_gate_identity_but_not_the_property():
    """The statement is a rendering; the property is the identity.  Both must be
    sealed, and only one governs the comparison."""
    reworded = _gate("F-9", "PASSIVITY", statement="measuring moves no fingerprint")
    assert reworded.semantic_id != FUSION.by_id()["F-9"].semantic_id
    assert reconcile(GateManifest(gates=(reworded,)), [_ran(reworded)]).consistent
