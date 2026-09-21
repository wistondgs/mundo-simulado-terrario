"""Contracts for the v2 capability passport, its mechanism and its plan.

Every guarantee here is paired with the mutant that breaks it.  A protection
that has only ever been green has not shown it can detect the defect, and this
schema exists because of two defects that were green for months: the fusion's
`F-9`, true under the wrong name, and level 1.8, whose implementation was the
degenerate case of what its oracle sealed.
"""

from __future__ import annotations

import pytest

from terrario.lab import mechanism_spec as mechanisms
from terrario.lab.capability_passport import (
    REGISTRY, SCHEMA_VERSION, SCHEMA_VERSION_V2, CapabilityPassport, ElementKind,
    ElementRef, NonClaimViolation, PassportState, Purity, assert_claimable,
    migrate_to_v2, status_of,
)
from terrario.lab.capability_plan import PlanRefused, emit_plan, validate

# --- a mechanism, and the same mechanism at another version -----------------------

MEMORIA = mechanisms.MechanismSpec(
    mechanism_id="one-step-cue-memory", version=1,
    semantic_definition="a slot that carries one cue across exactly one tick",
    operational_form="M_{t+1} = write(c_t); peek(M_t) = c_{t-1}; expire after two ticks",
    state_variables=("slot", "age"), inputs=("cue",), outputs=("peek",),
    invariants=("reading does not consume", "two ticks expire the slot"),
    degenerate_of=("a slot readable in the same tick, which needs no interval",))

MEMORIA_V2 = mechanisms.MechanismSpec(
    mechanism_id="one-step-cue-memory", version=2,
    semantic_definition="a slot that carries one cue across exactly two ticks",
    operational_form="M_{t+1} = write(c_t); expire after three ticks",
    state_variables=("slot", "age"), inputs=("cue",), outputs=("peek",),
    invariants=("reading does not consume",))


@pytest.fixture(autouse=True)
def _registro_limpio():
    previo = dict(mechanisms.REGISTRY)
    mechanisms.REGISTRY.clear()
    mechanisms.register(MEMORIA)
    yield
    mechanisms.REGISTRY.clear()
    mechanisms.REGISTRY.update(previo)


def _pasaporte(**cambios) -> CapabilityPassport:
    """A v2 fixture, not a productive record.

    No passport of the 1.x lineage exists -- the ten registered are A4/A5
    modules -- so inventing one to demonstrate the schema would be fabricating
    provenance for a campaign that never wrote it."""
    base = dict(
        concept_id="MEMORIA_DE_UN_PASO", corpus_provenance=("CLAIM-001",),
        operational_definition="retains one reference across one interval",
        algorithm_id="OneStepCueMemory", algorithm_version="1",
        capability_id="FIXTURE-MEM", inputs=("cue",), outputs=("peek",),
        internal_state=("slot",), allowed_information=("cue",),
        forbidden_information=("true_distance",),
        expected_behavior="recovers the cue after one tick",
        negative_prediction="without the tick it falls to the ignorant floor",
        required_world_property="the cue is absent at query time",
        primary_endpoint="conversion_aprendizaje", secondary_endpoints=(),
        falsification_controls=("tick omitted",), intervention_purity=Purity.PURE,
        known_dependencies=(), known_confounders=(), composition_flag=None,
        demanding_world="W-MEM", schema_version=SCHEMA_VERSION_V2,
        supplied=(ElementRef(ElementKind.MECHANISM, "one-step-cue-memory", "1"),),
        acquisition_target=(ElementRef(ElementKind.CONTENT, "which cue to keep"),),
        non_claims=("the organism represents time",),
        formalization_ref=mechanisms.MechanismRef.to(MEMORIA))
    return CapabilityPassport(**{**base, **cambios})


# --- v1 stays exactly as it was ---------------------------------------------------

def test_the_ten_registered_passports_are_untouched_by_v2_existing():
    """Measured before the field was added: evaluating the separation on v1
    would have reclassified 10 of 10 and taken the only READY_FOR_CERTIFICATION
    with it.  That is a migration, not an improvement."""
    assert {p.schema_version for p in REGISTRY.values()} == {SCHEMA_VERSION}
    estados = {cid: status_of(p).value for cid, p in REGISTRY.items()}
    assert estados["LEARN-A1"] == PassportState.READY_FOR_CERTIFICATION.value
    assert PassportState.SUPPLIED_AND_ACQUIRED_NOT_SEPARATED.value not in estados.values()


def test_a_v1_payload_emits_its_historical_shape_and_nothing_else():
    """Four new fields serialised as null would move every stored identity."""
    payload = REGISTRY["LEARN-A1"].payload()
    assert len(payload) == 24
    assert not ({"supplied", "acquisition_target", "non_claims",
                 "formalization_ref", "schema_version"} & set(payload))


def test_a_v1_passport_cannot_carry_v2_fields():
    with pytest.raises(ValueError, match="migra el pasaporte"):
        _pasaporte(schema_version=SCHEMA_VERSION)


def test_migrating_to_v2_mints_a_new_identity_and_refuses_to_overwrite():
    v1 = REGISTRY["LEARN-A1"]
    with pytest.raises(ValueError, match="capability_id propio"):
        migrate_to_v2(v1, capability_id=v1.capability_id, supplied=(),
                      acquisition_target=(), non_claims=(), formalization_ref=None)
    migrado = migrate_to_v2(
        v1, capability_id="LEARN-A1-V2",
        supplied=(ElementRef(ElementKind.MECHANISM, "one-step-cue-memory", "1"),),
        acquisition_target=(ElementRef(ElementKind.CONTENT, "what to retain"),),
        non_claims=("the organism understands",),
        formalization_ref=mechanisms.MechanismRef.to(MEMORIA))
    assert migrado.content_identity != v1.content_identity
    assert v1.schema_version == SCHEMA_VERSION  # el original no se tocó


# --- MUTANTE · supplied == acquisition_target --------------------------------------

def test_supplied_and_acquired_cannot_be_the_same_thing():
    ref = ElementRef(ElementKind.MECHANISM, "one-step-cue-memory", "1")
    with pytest.raises(ValueError, match="suministrado y como objetivo"):
        _pasaporte(supplied=(ref,), acquisition_target=(ref,))


def test_the_same_identity_at_another_revision_still_collapses():
    """Giving version 1 and asking that version 2 be acquired is still giving
    and asking for the same thing."""
    with pytest.raises(ValueError, match="suministrado y como objetivo"):
        _pasaporte(supplied=(ElementRef(ElementKind.MECHANISM, "m", "1"),),
                   acquisition_target=(ElementRef(ElementKind.MECHANISM, "m", "2"),))


def test_separation_is_by_identity_not_by_spelling():
    """`memory` and `episodic_memory` are different strings; the point is that
    kind and identity decide, not prose."""
    p = _pasaporte(supplied=(ElementRef(ElementKind.MECHANISM, "memory"),),
                   acquisition_target=(ElementRef(ElementKind.CONTENT, "memory"),))
    assert p.separates_supply_from_acquisition()


# --- MUTANTE · forbidden information supplied anyway --------------------------------

def test_a_forbidden_input_cannot_appear_in_supplied():
    with pytest.raises(ValueError, match="forbidden_information"):
        _pasaporte(supplied=(ElementRef(ElementKind.CONTENT, "true_distance"),))


# --- MUTANTE · mechanism vs implementation ------------------------------------------

def test_the_same_mechanism_with_another_implementation_stays_the_same_mechanism():
    """The whole reason MechanismSpec is not AlgorithmBinding."""
    a = _pasaporte(algorithm_id="OneStepCueMemory", algorithm_version="1")
    b = _pasaporte(algorithm_id="RingBufferCueMemory", algorithm_version="7")
    assert a.formalization_ref == b.formalization_ref
    assert validate(a) == validate(b) == ()
    assert a.content_identity != b.content_identity  # distinta implementación, sí


def test_the_same_implementation_under_a_changed_mechanism_is_refused():
    """Semantic drift: the code did not move, the promise did."""
    mechanisms.register(MEMORIA_V2)
    p = _pasaporte(formalization_ref=mechanisms.MechanismRef(
        "one-step-cue-memory", 1, MEMORIA_V2.spec_hash))
    assert any(c.startswith("MECHANISM_SPEC_DRIFT") for c in validate(p))


def test_a_registered_mechanism_cannot_be_edited_under_its_version():
    alterado = mechanisms.MechanismSpec(
        mechanism_id="one-step-cue-memory", version=1,
        semantic_definition="something else entirely",
        operational_form="M = 0", state_variables=(), inputs=(),
        outputs=("peek",), invariants=())
    with pytest.raises(mechanisms.MechanismImmutable, match="publish a new version"):
        mechanisms.register(alterado)


def test_an_unknown_mechanism_and_a_missing_version_are_different_failures():
    with pytest.raises(mechanisms.UnknownMechanism):
        mechanisms.resolve(mechanisms.MechanismRef("no-such", 1, "x"))
    with pytest.raises(mechanisms.MechanismVersionDrift):
        mechanisms.resolve(mechanisms.MechanismRef("one-step-cue-memory", 9, "x"))


def test_a_mechanism_spec_cannot_name_its_implementation():
    """Checked by shape: if the spec could hold a class name, the split it
    exists to draw would collapse on first use."""
    campos = set(mechanisms.MechanismSpec.__dataclass_fields__)
    assert not (campos & {"algorithm_id", "implementation_id", "class_name", "module"})


# --- MUTANTE · references that do not resolve ----------------------------------------

def test_a_formalization_ref_to_nothing_refuses_the_plan():
    p = _pasaporte(formalization_ref=mechanisms.MechanismRef("ghost", 1, "x"))
    with pytest.raises(PlanRefused) as refused:
        _emitir(p)
    assert any(c.startswith("UNKNOWN_MECHANISM") for c in refused.value.codes)


def test_an_unknown_prerequisite_refuses_the_plan():
    p = _pasaporte(known_dependencies=("NO-EXISTE",))
    with pytest.raises(PlanRefused) as refused:
        _emitir(p)
    assert "UNKNOWN_PREREQUISITE:NO-EXISTE" in refused.value.codes


def test_a_v1_passport_cannot_produce_a_construction_plan():
    with pytest.raises(PlanRefused) as refused:
        emit_plan("LEARN-A1")
    assert any(c.startswith("NOT_V2") for c in refused.value.codes)


# --- MUTANTE · non_claim promoted to claim ---------------------------------------------

def test_a_non_claim_cannot_be_promoted_to_a_claim():
    p = _pasaporte()
    assert assert_claimable(p, "retains one reference across one interval")
    with pytest.raises(NonClaimViolation, match="fuera de alcance"):
        assert_claimable(p, "the organism represents time")


def test_the_exclusion_survives_rewrapping_and_case():
    p = _pasaporte()
    with pytest.raises(NonClaimViolation):
        assert_claimable(p, "  The Organism   Represents Time  ")


# --- the plan answers the nine questions ------------------------------------------------

def _emitir(passport):
    """Register the fixture so `emit_plan` can load it by identity."""
    REGISTRY[passport.capability_id] = passport
    try:
        return emit_plan(passport.capability_id)
    finally:
        REGISTRY.pop(passport.capability_id, None)


def test_the_plan_answers_what_we_give_and_what_must_be_acquired():
    plan = _emitir(_pasaporte())
    assert plan["supplied"] and plan["acquisition_target"]
    assert plan["formalization"]["mechanism_id"] == "one-step-cue-memory"
    assert plan["formalization"]["must_not_degenerate_to"]
    assert plan["implementation"]["algorithm_id"] == "OneStepCueMemory"
    assert plan["non_claims"] == ["the organism represents time"]
    assert plan["forbidden_information"] == ["true_distance"]


def test_the_plan_is_deterministic():
    primero, segundo = _emitir(_pasaporte()), _emitir(_pasaporte())
    assert primero["plan_identity"] == segundo["plan_identity"]


def test_a_v2_passport_that_separates_reaches_a_real_state():
    """And the new state is what a v2 passport gets when it does not."""
    assert status_of(_pasaporte()) is not PassportState.SUPPLIED_AND_ACQUIRED_NOT_SEPARATED
