"""G8 — one authority decides whether a number may become evidence.

Terrario had two registries answering that question and neither was the
authority.  `instrument_registry` knew what an instrument means scientifically
and had zero production callers; `metrics_observer` knew what the runtime can
observe and had no notion of certification.  Underneath both,
`EvidenceRecord(metrics: dict[str, float])` could bypass either.

These tests pin the decision: `instrument_registry` is canonical, the observer
registry is subordinate, and every lateral route into evidence is closed.  They
are written as attacks wherever possible, because a gate is only worth what it
refuses.
"""
from __future__ import annotations

import pytest

from terrario.lab import evidence_admission as gate
from terrario.lab import instrument_registry as authority
from terrario.lab import metrics_observer as observer
from terrario.lab.measurement_status import NotEvaluableError, Reading, Status

REPORTABLE_ID = "tasa_oportunidad"
LEARN_ENDPOINT = "conversion_aprendizaje"


def _ref(metric_id=REPORTABLE_ID):
    return authority.ref_for(metric_id)


def _admit(**kw):
    base = dict(endpoint_role="PRIMARY", instrument_ref=_ref(),
                reading=Reading.ok(0.5, support=2).as_record(),
                preregistered_instrument_ref=_ref())
    base.update(kw)
    return gate.admit_evidence(**base)


# --- authority ---------------------------------------------------------------

def test_instrument_registry_is_scientific_authority():
    """It is the only module that answers the reportability question."""
    assert authority.assert_admissible(_ref()).metric_id == REPORTABLE_ID
    assert not hasattr(observer, "assert_reportable")
    assert not hasattr(observer, "reportable")
    assert not hasattr(observer.MetricRegistry, "assert_reportable")


def test_observer_metric_without_instrument_is_not_scientific():
    """Being known to the runtime registry is not a scientific authorization."""
    registry = observer.MetricRegistry()
    known = registry._metrics["D2-energy-trajectory"]
    assert known.scientific_instrument is None
    verdict = _admit(instrument_ref={"instrument_id": known.metric_id, "version": 1, "spec_hash": "x"})
    assert not verdict.admitted and "UNKNOWN_INSTRUMENT" in verdict.blockers


def test_a_binding_declares_an_instrument_it_does_not_certify_one():
    """The claim is a string; only the authority turns it into a resolution."""
    field = {f.name for f in __import__("dataclasses").fields(observer.MetricDefinition)}
    assert "scientific_instrument" in field
    claimed = observer.MetricDefinition.__dataclass_fields__["scientific_instrument"]
    assert claimed.type in ("str | None", str | None)


def test_unknown_instrument_fails_closed():
    with pytest.raises(authority.InstrumentResolutionError) as exc:
        authority.resolve(authority.InstrumentRef("no-such-instrument", 1, "0" * 64))
    assert exc.value.code == "UNKNOWN_INSTRUMENT"


def test_protocol_freezes_instrument_identity():
    """A frozen reference pins the whole specification, not just the name."""
    ref = _ref()
    assert ref.spec_hash == authority.spec_hash(REPORTABLE_ID)
    assert authority.resolve(ref).metric_id == REPORTABLE_ID


def test_version_drift_is_not_silent():
    ref = _ref()
    drifted = authority.InstrumentRef(ref.instrument_id, ref.version + 1, ref.spec_hash)
    with pytest.raises(authority.InstrumentResolutionError) as exc:
        authority.resolve(drifted)
    assert exc.value.code == "INSTRUMENT_VERSION_DRIFT"


def test_specification_drift_is_distinct_from_version_drift():
    """A revised instrument needs an amendment; an edited one is a defect."""
    ref = _ref()
    edited = authority.InstrumentRef(ref.instrument_id, ref.version, "0" * 64)
    with pytest.raises(authority.InstrumentResolutionError) as exc:
        authority.resolve(edited)
    assert exc.value.code == "INSTRUMENT_SPEC_DRIFT"


def test_conversion_aprendizaje_resolves_canonical_instrument():
    """LEARN-A1's declared endpoint resolves and is reportable."""
    from terrario.lab.capability_passport import REGISTRY as passports
    assert passports["LEARN-A1"].primary_endpoint == LEARN_ENDPOINT
    assert authority.assert_admissible(_ref(LEARN_ENDPOINT)).metric_id == LEARN_ENDPOINT


# --- admission ----------------------------------------------------------------

def test_evidence_admission_requires_reportable_instrument():
    verdict = _admit(instrument_ref=authority.InstrumentRef("no-such", 1, "0" * 64),
                     preregistered_instrument_ref=authority.InstrumentRef("no-such", 1, "0" * 64))
    assert not verdict.admitted and "UNKNOWN_INSTRUMENT" in verdict.blockers


def test_evidence_admission_requires_protocol_binding():
    verdict = _admit(preregistered_instrument_ref=None)
    assert not verdict.admitted
    assert "PROTOCOL_INSTRUMENT_BINDING_ABSENT" in verdict.blockers


def test_runtime_metric_must_match_the_preregistered_instrument():
    verdict = _admit(preregistered_instrument_ref=_ref(LEARN_ENDPOINT))
    assert not verdict.admitted and "INSTRUMENT_MISMATCH" in verdict.blockers


def test_a_diagnostic_endpoint_is_not_promoted_by_existing():
    """It may run; it does not thereby become a finding."""
    verdict = _admit(endpoint_role="DIAGNOSTIC", preregistered_instrument_ref=None)
    assert verdict.admitted and verdict.endpoint_role == "DIAGNOSTIC"
    assert verdict.numeric_claim is True


# --- the four readings ----------------------------------------------------------

@pytest.mark.parametrize("reading,expected", [
    (Reading.ok(0.0, support=12), Status.OK),
    (Reading.not_evaluable("no support", support=0), Status.NOT_EVALUABLE),
    (Reading.missing("field absent"), Status.MISSING),
    (Reading.invalid("contract violated"), Status.INVALID),
])
def test_every_reading_status_survives_admission(reading, expected):
    verdict = _admit(reading=reading.as_record())
    assert verdict.admitted, verdict.blockers
    assert verdict.reading_status is expected


def test_reading_ok_zero_is_a_numeric_claim_and_keeps_its_zero():
    """0.0 with support is a finding: it converted nothing, having had the chance."""
    verdict = _admit(reading=Reading.ok(0.0, support=12).as_record())
    assert verdict.admitted and verdict.numeric_claim is True
    assert verdict.reading_status is Status.OK


@pytest.mark.parametrize("reading", [
    Reading.not_evaluable("no support", support=0),
    Reading.missing("field absent"),
    Reading.invalid("contract violated"),
])
def test_non_ok_readings_are_recorded_but_make_no_numeric_claim(reading):
    verdict = _admit(reading=reading.as_record())
    assert verdict.admitted and verdict.numeric_claim is False


def test_non_ok_readings_never_coerce_to_float():
    for reading in (Reading.not_evaluable("x"), Reading.missing("x"), Reading.invalid("x")):
        with pytest.raises(NotEvaluableError):
            float(reading)


def test_a_non_ok_reading_carrying_a_number_is_refused():
    """The coercion this gate exists to prevent, arriving pre-packaged."""
    smuggled = {"status": Status.NOT_EVALUABLE.value, "value": 0.0, "support": 0, "reason": "none"}
    verdict = _admit(reading=smuggled)
    assert not verdict.admitted and "READING_NON_OK_CARRIES_VALUE" in verdict.blockers


# --- attacks --------------------------------------------------------------------

def test_attack_bare_numeric_cannot_bypass_admission():
    verdict = _admit(reading=0.99)
    assert not verdict.admitted and "READING_IS_BARE_NUMERIC" in verdict.blockers


def test_attack_absent_reading_is_refused():
    verdict = _admit(reading=None)
    assert not verdict.admitted and "READING_ABSENT" in verdict.blockers


def test_attack_ok_without_a_value_is_refused():
    verdict = _admit(reading={"status": "OK", "value": None, "support": 3, "reason": None})
    assert not verdict.admitted and "READING_OK_WITHOUT_VALUE" in verdict.blockers


def test_legacy_evidence_record_is_structurally_outside_the_canonical_path():
    """Preserved, never a side door.

    The legacy record carries `dict[str, float]` and lives in
    `terrario.experiment`, which cannot reach the sealing step: the only writer
    of a METRIC_RESULT is `seal_metric_result`, and it now refuses anything
    without a canonical instrument and a Reading.  This is asserted structurally
    rather than by editing the historical type, because rewriting it would break
    the runs it was written to keep readable.
    """
    import inspect

    from terrario.experiment.specs import EvidenceRecord
    from terrario.lab import metric_result_sealing as sealing

    assert EvidenceRecord.__dataclass_fields__["metrics"].type == "dict[str, float]"
    source = inspect.getsource(sealing)
    assert "METRIC_NOT_BOUND_TO_CANONICAL_INSTRUMENT" in source
    assert "EvidenceRecord" not in source
    legacy = EvidenceRecord(evidence_spec=None, experiment_id="e", run_id="r",
                            config_hash="c", code_hash="h", metrics={"x": 0.7})
    verdict = gate.admit_evidence(endpoint_role="PRIMARY", instrument_ref=None,
                                  reading=legacy.metrics["x"], preregistered_instrument_ref=None)
    assert not verdict.admitted
    assert {"INSTRUMENT_REF_ABSENT", "READING_IS_BARE_NUMERIC",
            "PROTOCOL_INSTRUMENT_BINDING_ABSENT"} <= set(verdict.blockers)


def test_legacy_result_schema_is_not_retroactively_certified():
    from terrario.lab.evidence_publication import LEGACY_RESULT_SCHEMAS, RESULT_SCHEMA

    assert RESULT_SCHEMA.endswith("/v2")
    assert "terrario.scientific-metric-result/v1" in LEGACY_RESULT_SCHEMAS
    assert RESULT_SCHEMA not in LEGACY_RESULT_SCHEMAS


def test_instrument_identity_survives_a_record_round_trip():
    ref = _ref()
    assert authority.InstrumentRef.from_record(ref.as_record()) == ref
    assert authority.resolve(authority.InstrumentRef.from_record(ref.as_record())) is authority.REGISTRY[REPORTABLE_ID]
