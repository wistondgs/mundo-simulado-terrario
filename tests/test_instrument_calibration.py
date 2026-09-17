"""Calibration is an acceptance gate, not a report.

A metric in CALIBRATION_REQUIRED may not be reported until it answers correctly
on cases whose value is fixed by construction. These tests fail the build if a
required metric loses its controls, or if a control stops passing.
"""

import pytest

from terrario.lab import instrument_calibration as cal
from terrario.lab.run_measures import _eating


def test_every_required_metric_declares_controls():
    for metric in cal.CALIBRATION_REQUIRED:
        assert metric in cal.CONTROLS, f"{metric} is required to calibrate and has no controls"
        assert cal.CONTROLS[metric][1], f"{metric} declares an empty control set"


@pytest.mark.parametrize("outcome", cal.calibrate_all(), ids=lambda o: f"{o.metric}:{o.case}")
def test_control_holds(outcome):
    assert outcome.passed, (
        f"{outcome.metric} on {outcome.case}: expected {outcome.expected}, "
        f"observed {outcome.observed}. {outcome.why}")


def test_controls_include_a_ceiling_a_floor_and_where_it_exists_a_chance_value():
    # An instrument checked only at zero passes while reading everything as zero,
    # which is the failure that actually occurred. Every rate needs both ends.
    for metric in ("tasa_direccionamiento", "tasa_oportunidad", "tasa_interaccion"):
        expected = {c.expected for c in cal.CONTROLS[metric][1]}
        assert 0.0 in expected and 1.0 in expected, f"{metric} is not pinned at both ends"


def test_a_collapsed_policy_does_not_manufacture_a_hit_rate_from_the_step_cost():
    # The organism consumes at every step and never reaches anything, in a world
    # that declares no cost. There are no idle steps to read a baseline from, so
    # there is no way to tell a failed consume from the metabolism. The honest
    # answer is a refusal; the previous default of 0.0 invented several hundred
    # failed consumes out of the drain.
    rows = cal.trace([((), cal._act("CONSUME", "RIGHT")) for _ in range(50)],
                     energies=[100.0 - i for i in range(51)])
    reading = _eating(rows)
    assert reading["hit_rate"] is None
    assert reading["baseline_source"] == "NO_IDLE_STEPS_AND_NO_DECLARED_COST"


def test_a_declared_cost_is_preferred_over_the_median():
    rows = cal.trace([((), cal._act("CONSUME", "RIGHT")) for _ in range(50)],
                     energies=[100.0 - i for i in range(51)])
    for row in rows:
        row["observer_world"]["step_energy_cost"] = 1.0
    reading = _eating(rows)
    assert reading["baseline_source"] == "DECLARED" and reading["baseline"] == -1.0
    # With the cost accounted for, none of those consumes is a miss: they reached
    # nothing, which is a third outcome and not a discrimination failure.
    assert reading["effective"] == 0 and reading["hit_rate"] is None
