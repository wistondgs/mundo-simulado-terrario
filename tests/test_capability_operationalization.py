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


def test_only_learn_a1_has_explicit_provenance_or_operationalization():
    linked = [passport for passport in PASSPORTS.values()
              if passport.corpus_provenance or passport.operationalization_id]
    assert [passport.capability_id for passport in linked] == ["LEARN-A1"]
    assert PASSPORTS["LEARN-A1"].corpus_provenance == ("CLM-0127", "CLM-0132")


def test_serialization_and_hash_round_trip_are_stable():
    payload = LEARN_A1_OPERATIONALIZATION.payload()
    restored = OperationalizationRecord.from_payload(payload)
    assert restored == LEARN_A1_OPERATIONALIZATION
    assert restored.semantic_id == LEARN_A1_OPERATIONALIZATION.semantic_id


def test_registry_is_complete_and_fail_closed():
    assert tuple(REGISTRY) == ("OPR-LEARN-A1-RL-01",)
    validate_registry()
