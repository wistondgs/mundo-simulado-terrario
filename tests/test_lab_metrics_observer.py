from dataclasses import replace
from pathlib import Path

from terrario.lab.metrics_observer import (
    ConstructValidationStatus, Direction, MetricImplementationStatus,
    MetricRegistry, ObserverRegistry, SeparationClass,
)
from terrario.lab.world_registry import WorldScenarioRegistry
from terrario.lab.world_registry import configuration_for
from terrario.lab.world_authoring import compile_registry_world
from terrario.lab.sandbox_runtime import SandboxService, derive_sandbox, make_spec


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


def test_same_execution_inputs_have_identical_agent_observation_across_observer_profiles(tmp_path):
    entry = WorldScenarioRegistry(Path(".")).get("D2")
    base = derive_sandbox(configuration_for(entry))
    summary_config = replace(base, config_id="summary", observer_configuration={"mode":"performance", "profile":"SUMMARY"})
    debug_config = replace(base, config_id="debug", observer_configuration={"mode":"forensic_full", "profile":"FULL_DEBUG"})
    compiled = compile_registry_world("D2", entry.source)
    service = SandboxService(tmp_path)
    summary_run = service.create(make_spec(summary_config, compiled, 77, 88, 2), summary_config, compiled)
    debug_run = service.create(make_spec(debug_config, compiled, 77, 88, 2), debug_config, compiled)
    service.step(summary_run.run_id); service.step(debug_run.run_id)
    left = summary_run.timeline[0].agent_observation
    right = debug_run.timeline[0].agent_observation
    assert left == right
    assert set(left) == {"channels", "mask", "agent_energy", "time_fraction"}


def test_storage_estimate_changes_with_channels_and_frequency():
    registry = ObserverRegistry()
    summary = registry.estimate("SUMMARY", 100, 4)
    full = registry.estimate("FULL_DEBUG", 100, 4)
    assert summary.classification == "ESTIMATE"
    assert full.estimated_bytes > summary.estimated_bytes
    assert registry.estimate("SUMMARY", None, 4).status == "UNKNOWN"
