"""The viability-recovery detector must fail closed and must not invent scores."""
from __future__ import annotations

import pytest

from terrario.lab.metrics_observer import (ConstructValidationStatus, MetricImplementationStatus,
                                           MetricRegistry)
from terrario.lab.viability_recovery_metric import (METRIC_ID, ViabilityRecoveryError, evaluate,
                                                    evaluate_scientific_trace, specification,
                                                    validate_construct)

PARAMS = {"viable_floor": 0.5, "dwell_k": 3, "variety_bin": 1.0}


def _samples(energies, revision_at, max_energy=100.0):
    return [{"tick": i, "energy": float(e), "max_energy": max_energy,
             "revision": 1 if revision_at is None or i < revision_at else 2}
            for i, e in enumerate(energies)]


def _trace(energies, revision_at, max_energy=100.0):
    return {"frames": [{"tick": i, "world_revision": 1 if revision_at is None or i < revision_at else 2,
                        "world_truth": {"max_energy": max_energy, "rules_version": 1,
                                        "agents": {"0": {"agent_id": 0, "alive": True, "energy": float(e)}}}}
                       for i, e in enumerate(energies)]}


def test_construct_validation_passes_every_declared_case():
    report = validate_construct()
    failed = [c["case"] for c in report["cases"] if not c["passed"]]
    assert not failed, failed
    assert report["all_passed"] and report["calibration_report_hash"]


def test_an_undisturbed_episode_is_not_evaluable_rather_than_zero():
    # Reporting 0 would read as "recovered instantly", the opposite of the truth.
    result = evaluate(_samples([90] * 10, None), **PARAMS)
    assert not result.evaluable and result.recovery_steps is None
    assert result.reason == "NO_DISTURBANCE_OBSERVED"


def test_never_returning_is_none_not_a_large_number():
    result = evaluate(_samples([90] * 5 + [10] * 8, 5), **PARAMS)
    assert result.evaluable and result.recovery_steps is None and result.dwell_outside == 8


def test_parameters_are_required_and_bounded():
    for bad in ({"viable_floor": 0.0}, {"viable_floor": 1.0}, {"dwell_k": 0}, {"variety_bin": 0.0}):
        with pytest.raises(ViabilityRecoveryError):
            evaluate(_samples([90] * 6, 3), **(PARAMS | bad))


def test_the_eta_boundary_is_part_of_the_instrument_identity():
    # A different viable set is a different measurement and must hash differently.
    a = specification(**PARAMS)["metric_spec_hash"]
    b = specification(**(PARAMS | {"viable_floor": 0.9}))["metric_spec_hash"]
    assert a != b


def test_a_sealed_trace_is_projected_from_observer_truth_only():
    result = evaluate_scientific_trace(_trace([90] * 5 + [40, 40, 40] + [80] * 5, 5), **PARAMS)
    assert result.evaluable and result.perturbation_tick == 5
    assert result.dwell_outside == 3 and result.recovery_steps == 3


def test_a_malformed_trace_raises_rather_than_scoring():
    for broken in ({"frames": []}, {"frames": [{"tick": 0}]},
                   {"frames": [{"tick": 0, "world_revision": 1, "world_truth": {"agents": {}}}]}):
        with pytest.raises(ViabilityRecoveryError):
            evaluate_scientific_trace(broken, **PARAMS)


def test_registry_declares_it_implemented_but_not_yet_construct_validated():
    metric = MetricRegistry().get(METRIC_ID)
    assert metric.implementation_status is MetricImplementationStatus.IMPLEMENTED
    # Promotion to VALIDATED is what makes a result publishable; it is a human
    # decision taken against the calibration report, not a library default.
    assert metric.construct_validation_status is ConstructValidationStatus.NOT_VALIDATED_FOR_CONSTRUCT
    assert "D4S" in metric.applicability


def test_d4s_is_additive_and_d4_still_resolves_to_its_original_file():
    from pathlib import Path
    from terrario.lab.world_registry import WorldScenarioRegistry
    registry = WorldScenarioRegistry(Path("."))
    assert Path(registry.get("D4").source).name == "d4_change.yaml"
    assert Path(registry.get("D4S").source).name == "d4_adaptation_scientific.yaml"


def test_recovery_zero_is_not_survival_when_the_organism_decays_out_afterwards():
    """The case real data found on the first D4S run.

    E was inside eta when the disturbance landed and stayed for dwell_k, so
    the first sustained re-entry is 0 -- and then it decayed out of eta and
    never came back.  Reported alone, that 0 reads as "recovered instantly".
    """
    # inside at D, still inside for dwell_k, then a slow decay below eta.
    result = evaluate(_samples([90] * 5 + [60, 58, 56, 54, 40, 30, 20], 5), **PARAMS)
    assert result.recovery_steps == 0          # first sustained re-entry
    assert result.viable_at_end is False       # ...and it did not survive
    assert result.dwell_outside > 0


def test_viable_at_end_is_true_for_a_genuine_recovery():
    result = evaluate(_samples([90] * 5 + [40, 40, 40] + [80] * 5, 5), **PARAMS)
    assert result.recovery_steps == 3 and result.viable_at_end is True


def test_the_reading_rule_is_declared_in_the_specification():
    # A consumer must not have to discover the coupling by being burned by it.
    assert "viable_at_end" in specification(**PARAMS)["reading_rule"]


def test_censoring_is_distinguished_from_failure_to_recover():
    """None recovery_steps has two causes and they must not be conflated.

    An aggregate that reads None as "never recovered" is biased by every
    episode that simply ended while the organism was still outside eta.
    """
    still_out = evaluate(_samples([90] * 5 + [10] * 8, 5), **PARAMS)
    assert still_out.recovery_steps is None and still_out.censored is True
    assert still_out.relapse is False

    recovered = evaluate(_samples([90] * 5 + [40, 40, 40] + [80] * 5, 5), **PARAMS)
    assert recovered.censored is False and recovered.relapse is False


def test_a_relapse_is_named_rather_than_hidden_inside_recovery_steps():
    # Re-enters eta for dwell_k, then leaves again and ends outside.
    result = evaluate(_samples([90] * 5 + [40, 80, 80, 80, 40, 20, 10], 5), **PARAMS)
    assert result.recovery_steps is not None
    assert result.relapse is True and result.viable_at_end is False
    assert result.censored is False
