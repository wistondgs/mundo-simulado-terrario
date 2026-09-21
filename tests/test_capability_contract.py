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
    """Adds the fixture mechanism without removing the productive ones.

    Clearing would have hidden a real failure behind a test-only registry: the
    migrated passport points at `online-gradient-update`, which is registered at
    import time, and a test that wipes it proves nothing about the tree."""
    previo = dict(mechanisms.REGISTRY)
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
    estados = {cid: status_of(p).value for cid, p in REGISTRY.items() if not p.is_v2}
    assert len(estados) == 10
    assert estados["LEARN-A1"] == PassportState.READY_FOR_CERTIFICATION.value
    assert PassportState.SUPPLIED_AND_ACQUIRED_NOT_SEPARATED.value not in estados.values()


#: The canonical v1 shape, written out rather than counted.
#:
#: A count is what let the docstring say "veintidós" while the dataclass had
#: twenty-three on its first day, and twenty-four after `operationalization_id`
#: landed.  Protecting historical identity with a number protects nothing: the
#: literal set is the authority, and a field added, removed or renamed breaks
#: this before it can move an identity.
V1_CANONICAL_SHAPE = (
    "algorithm_id", "algorithm_version", "allowed_information", "capability_id",
    "composition_flag", "concept_id", "corpus_provenance", "demanding_world",
    "expected_behavior", "falsification_controls", "forbidden_information",
    "inputs", "internal_state", "intervention_purity", "known_confounders",
    "known_dependencies", "negative_prediction", "notes",
    "operational_definition", "operationalization_id", "outputs",
    "primary_endpoint", "required_world_property", "secondary_endpoints",
)


def test_the_v1_canonical_shape_is_exactly_these_twenty_four_keys():
    """Pins the shape literally, for every v1 passport, not just one."""
    v1 = [p for p in REGISTRY.values() if not p.is_v2]
    assert len(v1) == 10
    for passport in v1:
        assert tuple(sorted(passport.payload())) == V1_CANONICAL_SHAPE, passport.capability_id


def test_a_v1_payload_emits_its_historical_shape_and_nothing_else():
    """Four new fields serialised as null would move every stored identity."""
    payload = REGISTRY["LEARN-A1"].payload()
    assert len(payload) == len(V1_CANONICAL_SHAPE) == 24
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


# --- control · la semántica de ElementRef sale del dominio, no de esta prueba ------

def test_the_domain_really_has_an_entity_layer_without_versions():
    """Read off the existing types, not asserted.

    `concept_id` is declared with no version beside `algorithm_id` and
    `algorithm_version`.  That pair is the tree saying entity and versioned
    realisation are different layers, which is what licenses `ElementRef.key`
    to drop the revision."""
    campos = CapabilityPassport.__dataclass_fields__
    assert "concept_id" in campos and "concept_version" not in campos
    assert "algorithm_id" in campos and "algorithm_version" in campos


def test_the_realisation_layer_refuses_a_version_substitution():
    """And the same tree refuses it where the revision IS the identity, which
    is why `MechanismRef` keeps it and `ElementRef` does not."""
    from terrario.lab import instrument_registry
    assert hasattr(instrument_registry, "InstrumentRef")
    with pytest.raises(mechanisms.MechanismVersionDrift):
        mechanisms.resolve(mechanisms.MechanismRef("one-step-cue-memory", 2, "x"))


def test_a_mechanism_ref_carries_its_version_in_its_identity():
    """The two layers, side by side: swapping the version of a MechanismRef
    gives a different reference; swapping it on an ElementRef does not change
    which entity is named."""
    a = mechanisms.MechanismRef("m", 1, "h")
    assert a != mechanisms.MechanismRef("m", 2, "h")
    assert (ElementRef(ElementKind.MECHANISM, "m", "1").key
            == ElementRef(ElementKind.MECHANISM, "m", "2").key)


def test_degenerate_of_is_a_relation_the_tree_already_builds():
    """Not an encoding of 1.8.

    Deliberate degenerate forms exist as controls in at least four campaigns --
    ConstantDistance and BlindCore in 1.2, NoMemory, WriteDisabledMemory and
    ImmediateMemory in 1.3, NoMemory in the fusion -- and A4's planner has one
    that was only found by reading.  The field makes that declarable up front;
    it does not invent the relation."""
    spec = mechanisms.MechanismSpec(
        mechanism_id="planner", version=1, semantic_definition="chooses by lookahead",
        operational_form="a* = argmax_a E[V(s') | s, a] under the world model",
        state_variables=(), inputs=("state",), outputs=("action",),
        invariants=("the world model is consulted",),
        degenerate_of=("a constant-output world model, which makes it an "
                       "exploration source rather than a planner",))
    assert spec.degenerate_of
    assert mechanisms.register(spec).spec_hash == spec.spec_hash


# --- el expediente del único pasaporte productivo migrable -------------------------

def test_learn_a1_is_the_only_migratable_candidate():
    """Audited across the ten: only two have an endpoint resolving to a
    MetricSpec with declared scope, and the other -- WM-A1 -- is
    INTERVENTION_IMPURE, so its effect is attributable to nobody."""
    from terrario.lab import instrument_registry

    con_alcance = sorted(
        cid for cid, p in REGISTRY.items()
        if not p.is_v2 and instrument_registry.REGISTRY.get(p.primary_endpoint))
    assert con_alcance == ["LEARN-A1", "WM-A1"]
    assert status_of(REGISTRY["WM-A1"]) is PassportState.INTERVENTION_IMPURE


def test_the_migrated_passport_satisfies_every_condition():
    v1, v2 = REGISTRY["LEARN-A1"], REGISTRY["LEARN-A1-V2"]

    # v1 permanece inmutable
    assert v1.schema_version == SCHEMA_VERSION
    assert tuple(sorted(v1.payload())) == V1_CANONICAL_SHAPE
    assert status_of(v1) is PassportState.READY_FOR_CERTIFICATION
    assert v1.content_identity != v2.content_identity

    # y la migración NO heredó la procedencia: el registro de
    # operacionalización es una decisión humana que nombra a LEARN-A1, así que
    # el v2 nace sin enlace en vez de reclamar uno que no lo nombra
    assert v2.corpus_provenance == () and v2.operationalization_id is None
    assert status_of(v2) is PassportState.NO_CORPUS_PROVENANCE

    # v2 resuelve todas sus referencias, y su plan sale
    assert validate(v2) == ()
    plan = emit_plan("LEARN-A1-V2")

    # supplied y acquisition_target sustentados, y separados
    assert v2.separates_supply_from_acquisition()
    assert any(r.kind is ElementKind.MECHANISM for r in v2.supplied)
    assert all(r.kind is ElementKind.CONTENT for r in v2.acquisition_target)

    # formalization_ref resuelve, y el binding lo realiza sin ser el mecanismo
    spec = mechanisms.resolve(v2.formalization_ref)
    assert spec.mechanism_id == "online-gradient-update"
    assert plan["implementation"]["algorithm_id"] == "OnlineLearner"
    assert plan["implementation"]["algorithm_id"] != spec.mechanism_id

    # non_claims sustentado por el alcance que el instrumento declara
    assert any("stable-rule segment" in c for c in v2.non_claims)
    assert any("NOT_EVALUABLE" in c for c in v2.non_claims)

    # plan_identity determinista
    assert plan["plan_identity"] == emit_plan("LEARN-A1-V2")["plan_identity"]
