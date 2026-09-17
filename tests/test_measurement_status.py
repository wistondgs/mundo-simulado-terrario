"""Absence must not be able to become zero by accident."""

import pytest

from terrario.lab import instrument_registry as reg
from terrario.lab.measurement_status import (
    NotEvaluableError, Reading, Status, ratio, summarise,
)


def test_an_empty_denominator_is_not_evaluable_rather_than_zero():
    r = ratio(0, 0, what="addressing")
    assert r.status is Status.NOT_EVALUABLE and r.value is None and r.support == 0


def test_a_real_zero_stays_a_real_zero():
    r = ratio(0, 40, what="addressing")
    assert r.status is Status.OK and r.value == 0.0 and r.support == 40


def test_a_non_ok_reading_refuses_to_become_a_number():
    for reading in (Reading.not_evaluable("no support"), Reading.missing("no field"),
                    Reading.invalid("contract violated")):
        with pytest.raises(NotEvaluableError):
            float(reading)


def test_a_numerator_larger_than_its_denominator_is_invalid_not_clipped():
    # Two counters disagreeing about what they count is a defect, and silently
    # returning 1.2 or clamping to 1.0 hides it.
    assert ratio(7, 5).status is Status.INVALID


def test_a_missing_field_is_distinguishable_from_no_support():
    assert ratio(None, 10).status is Status.MISSING
    assert ratio(3, 0).status is Status.NOT_EVALUABLE


def test_serialisation_keeps_the_four_statuses_apart():
    record = summarise({"a": ratio(1, 4), "b": ratio(0, 0)})
    assert record["a"]["value"] == 0.25 and record["a"]["status"] == "OK"
    assert record["b"]["value"] is None and record["b"]["status"] == "NOT_EVALUABLE"


# ── The reportability gate ─────────────────────────────────────────────

def test_only_reportable_metrics_may_enter_a_report():
    for metric_id in reg.REGISTRY:
        state = reg.state_of(metric_id)
        if state is reg.InstrumentState.REPORTABLE:
            reg.assert_reportable(metric_id)
        else:
            with pytest.raises(RuntimeError):
                reg.assert_reportable(metric_id)


def test_an_unregistered_metric_is_not_reportable():
    assert reg.state_of("una_metrica_inventada") is reg.InstrumentState.UNREGISTERED
    with pytest.raises(RuntimeError):
        reg.assert_reportable("una_metrica_inventada")


def test_a_spec_whose_declared_controls_do_not_match_the_implemented_ones_is_blocked():
    # A metric whose registry entry claims controls it does not have would pass
    # a naive "has controls?" check while measuring nothing of the sort.
    original = reg.REGISTRY["tasa_oportunidad"]
    try:
        reg.REGISTRY["tasa_oportunidad"] = reg.MetricSpec(
            **{**original.__dict__, "instrument_controls": ("un_control_que_no_existe",)})
        assert reg.state_of("tasa_oportunidad") is reg.InstrumentState.CONTRACT_MISMATCH
    finally:
        reg.REGISTRY["tasa_oportunidad"] = original


def test_every_registered_metric_writes_down_what_it_conditions_on():
    # Two functions can share a name and measure different conditioned
    # quantities. The conditioning belongs in the record, not in the code.
    for metric_id, spec in reg.REGISTRY.items():
        assert spec.conditional_form.startswith("P("), metric_id
        assert spec.numerator and spec.denominator, metric_id
        assert spec.undefined_conditions, f"{metric_id} never says when it is undefined"
