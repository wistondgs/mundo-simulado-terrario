"""G0: human-approved, reversible provenance for LEARN-A1 only."""
from dataclasses import replace

import pytest

from terrario.lab.capability_operationalization import (
    CLAIM_0127, LEARN_A1_OPERATIONALIZATION, REGISTRY, OperationalizationRecord,
    operationalization_for_passport, reverse_lookup, validate_registry,
)
from terrario.lab.capability_passport import REGISTRY as PASSPORTS


def test_capability_claim_source_round_trip_preserves_locator_and_snapshot():
    record = operationalization_for_passport(PASSPORTS["LEARN-A1"])
    assert record is LEARN_A1_OPERATIONALIZATION
    assert record.primary_claim.claim_id == "CLM-0127"
    assert record.primary_claim.source_id == "TI-0097"
    assert record.primary_claim.locator == "ch. 1.1, PDF p. 23"
    record.validate()


def test_reverse_lookup_finds_only_explicit_human_operationalization():
    assert reverse_lookup("CLM-0127") == (LEARN_A1_OPERATIONALIZATION,)
    assert reverse_lookup("CLM-0132") == (LEARN_A1_OPERATIONALIZATION,)
    with pytest.raises(KeyError, match="unknown or unbound claim"):
        reverse_lookup("CLM-0137")


def test_human_operationalization_is_not_a_source_claim():
    record = LEARN_A1_OPERATIONALIZATION
    assert record.human_operationalization.status == "HUMAN_OPERATIONALIZATION"
    assert record.primary_claim.claim_id != record.human_operationalization.decision_id
    assert record.algorithm.algorithm_id == "OnlineLearner"
    assert record.implementation.implementation_id.endswith("A4Advanced.learn")
    assert record.endpoint.endpoint_id == "conversion_aprendizaje"


def test_unknown_claim_fails_closed_against_the_immutable_snapshot():
    with pytest.raises(ValueError, match="unknown claim id"):
        replace(CLAIM_0127, claim_id="CLM-UNKNOWN").validate()


def test_provenance_and_operationalization_never_appear_one_without_the_other():
    """The invariant, which is not a head count.

    This used to assert that LEARN-A1 was the only capability with provenance.
    That was true when written and is no longer: Ashby, Ha & Schmidhuber and
    Pathak were sitting in the audited layer of the corpus, with locators, while
    three passports shipped `corpus_provenance=()`. What must hold is not how
    many are linked but that a passport can never claim a corpus link it cannot
    resolve, nor carry a record that does not round-trip back to it.
    """
    for passport in PASSPORTS.values():
        linked = bool(passport.corpus_provenance)
        assert linked == bool(passport.operationalization_id), passport.capability_id
        if not linked:
            continue
        record = REGISTRY[passport.operationalization_id]
        assert record.capability_id == passport.capability_id
        assert passport.corpus_provenance == record.claim_ids


def test_serialization_and_hash_round_trip_are_stable():
    payload = LEARN_A1_OPERATIONALIZATION.payload()
    restored = OperationalizationRecord.from_payload(payload)
    assert restored == LEARN_A1_OPERATIONALIZATION
    assert restored.semantic_id == LEARN_A1_OPERATIONALIZATION.semantic_id


def test_registry_is_complete_and_fail_closed():
    validate_registry()
    # Every claim every record cites resolves against the sealed snapshot: hash,
    # identity, claim id, declared source and exact locator.
    for record in REGISTRY.values():
        for claim in (record.primary_claim, *record.supporting_claims):
            claim.validate()
    assert {record.capability_id for record in REGISTRY.values()} == {
        passport.capability_id for passport in PASSPORTS.values() if passport.corpus_provenance}


# --- concept provenance: the half of L-1 that had no field -------------------

from terrario.lab.capability_operationalization import (  # noqa: E402
    CorpusConceptReference, snapshot_root,
)


def _artifact_hashes():
    import json
    manifest = json.loads((snapshot_root() / "snapshot_manifest.json").read_text(encoding="utf-8"))
    return {item["filename"]: item["sha256"] for item in manifest["artifacts"]}


def _row(artifact, key, value):
    import csv
    with (snapshot_root() / artifact).open(encoding="utf-8-sig", newline="") as stream:
        return next(row for row in csv.DictReader(stream) if row.get(key) == value)


def _curiosity_reference():
    """Darwin's `curiosity`, CON-0024, reached through the claim that cites it."""
    hashes = _artifact_hashes()
    concept = _row("CONCEPTS_RAW_v0.1.csv", "concept_id", "CON-0024")
    claim = _row("CLAIMS_RELATIONS_v0.1.csv", "claim_id", "CLM-0020")
    via = replace(CLAIM_0127, claim_id="CLM-0020",
                  source_id=claim["fuente"].split("[")[-1].rstrip("]"),
                  locator=claim["pagina_seccion"])
    return CorpusConceptReference(
        concept_id="CON-0024",
        normalized_name=concept["nombre_normalizado_provisional"],
        concept_locator=concept["pagina_seccion"],
        concept_artifact="CONCEPTS_RAW_v0.1.csv",
        concept_artifact_sha256=hashes["CONCEPTS_RAW_v0.1.csv"],
        via_claim=via,
    )


def test_a_concept_is_citable_only_through_a_claim_that_names_it():
    """The chain L-1 asks for: concept -> located claim -> source.

    A concept row has no place in a document a third party can open; the claim
    does. So the middle link is not decoration -- it is what makes the citation
    checkable.
    """
    _curiosity_reference().validate()


def test_a_concept_absent_from_its_declared_claim_is_refused():
    hashes = _artifact_hashes()
    other = _row("CONCEPTS_RAW_v0.1.csv", "concept_id", "CON-0001")
    impostor = replace(_curiosity_reference(), concept_id="CON-0001",
                       normalized_name=other["nombre_normalizado_provisional"],
                       concept_locator=other["pagina_seccion"],
                       concept_artifact_sha256=hashes["CONCEPTS_RAW_v0.1.csv"])
    with pytest.raises(ValueError, match="concept does not appear in the declared claim"):
        impostor.validate()


def test_a_concept_with_no_author_definition_is_refused():
    """The guard that would have rejected the v0.3 patch layer wholesale.

    All 59 of its concepts carry an empty `definicion_del_autor` -- nothing of
    the author's to cite -- against 224 of 224 populated in v0.1. Citing one
    would be declaring a reading, which is exactly how twelve acquired documents
    came to be uncitable.
    """
    hashes = _artifact_hashes()
    patched = _row("CONCEPTS_RAW_PATCH_v0.3.csv", "concept_id", "P3C-0014")
    assert not patched["definicion_del_autor"].strip(), "fixture assumes the empty column"
    reference = replace(_curiosity_reference(), concept_id="P3C-0014",
                        normalized_name=patched["nombre_normalizado_provisional"],
                        concept_locator=patched["pagina_seccion"],
                        concept_artifact="CONCEPTS_RAW_PATCH_v0.3.csv",
                        concept_artifact_sha256=hashes["CONCEPTS_RAW_PATCH_v0.3.csv"])
    with pytest.raises(ValueError, match="concept has no author definition"):
        reference.validate()


def test_a_second_snapshot_resolves_to_its_own_directory():
    """Regression: the root came from the module constant, not from the reference.

    A reference declaring a newer snapshot looked inside the older one, found
    its manifest and failed with `manifest hash mismatch` -- a message accusing
    the corpus of corruption when nobody had gone to the right directory. A
    laboratory has more than one corpus over time; this is what makes that
    expressible.
    """
    assert snapshot_root("theory-v2-example").name == "theory-v2-example"
    assert snapshot_root().name == CLAIM_0127.snapshot_id
    with pytest.raises(ValueError, match="corpus snapshot is unavailable"):
        replace(CLAIM_0127, snapshot_id="theory-v2-example").validate()
