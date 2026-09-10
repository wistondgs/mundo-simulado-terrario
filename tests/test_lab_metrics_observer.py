from pathlib import Path

from terrario.lab.metrics_observer import (
    ConstructValidationStatus, Direction, MetricImplementationStatus,
    MetricRegistry, ObserverRegistry, SeparationClass,
)
from terrario.lab.world_registry import WorldScenarioRegistry


def scenario(identifier="D2"):
    return WorldScenarioRegistry(Path(".")).get(identifier).scenario


def test_proposed_is_not_implemented_and_implemented_is_not_validated():
    registry = MetricRegistry()
    proposed = registry.get("adaptation-recovery-steps")
    implemented = registry.get("D2-energy-trajectory")
    assert proposed.implementation_status == MetricImplementationStatus.PROPOSED
    assert implemented.implementation_status == MetricImplementationStatus.IMPLEMENTED
    assert implemented.construct_validation_status == ConstructValidationStatus.NOT_VALIDATED_FOR_CONSTRUCT


def test_missing_signal_is_explicit_not_zero_or_nan():
    result = MetricRegistry().applicability("prediction-error", scenario(), ())
    assert result.status == "MISSING_REQUIRED_SIGNAL"
    assert result.missing_signals == ("prediction_error",)


def test_direction_construct_and_proxy_round_trip_separately():
    metric = MetricRegistry().get("prediction-error")
    assert metric.direction == Direction.LOWER_IS_BETTER
    assert metric.construct == "prediction"
    assert metric.proxy == "absolute energy prediction error"
    assert metric.construct != metric.proxy


def test_metric_applicability_respects_scenario_and_observer_signals():
    registry = MetricRegistry()
    assert registry.applicability("prediction-error", scenario(), ("prediction_error",)).status == "APPLICABLE"
    assert registry.applicability("prediction-error", scenario("D1"), ("prediction_error",)).status == "NOT_APPLICABLE"


def test_profiles_expand_to_explicit_channels_and_debug_is_not_scientific():
    registry = ObserverRegistry()
    standard = registry.profile("STANDARD")
    assert standard.channels == tuple(x.channel_id for x in registry.expand("STANDARD"))
    debug = next(x for x in registry.channels() if x.channel_id == "internal_tensors")
    assert debug.separation_class == SeparationClass.DEBUG_ONLY
    assert "debug" in debug.scientific_purpose


def test_observer_verbosity_never_changes_agent_observation_or_leaks_truth():
    registry = ObserverRegistry()
    observation = {"channels": [1], "mask": [1], "agent_energy": .8, "time_fraction": .2,
                   "world_truth": {"secret": True}, "objects": [1]}
    summary = registry.agent_projection(observation, "SUMMARY")
    debug = registry.agent_projection(observation, "FULL_DEBUG")
    assert summary == debug
    assert "world_truth" not in summary and "objects" not in summary


def test_storage_estimate_changes_with_channels_and_frequency():
    registry = ObserverRegistry()
    summary = registry.estimate("SUMMARY", 100, 4)
    full = registry.estimate("FULL_DEBUG", 100, 4)
    assert summary.classification == "ESTIMATE"
    assert full.estimated_bytes > summary.estimated_bytes
    assert registry.estimate("SUMMARY", None, 4).status == "UNKNOWN"
