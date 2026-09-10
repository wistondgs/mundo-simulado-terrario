"""Metric and observer registries with signal and leakage safety."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Iterable

from terrario.lab.world_contracts import AGENT_FIELDS, ScenarioDefinition

METRIC_SCHEMA_VERSION = "terrario.lab.metric/v2"
OBSERVER_SCHEMA_VERSION = "terrario.lab.observer/v1"


class MetricImplementationStatus(StrEnum):
    IMPLEMENTED = "IMPLEMENTED"
    PARTIAL = "PARTIAL"
    PROPOSED = "PROPOSED"
    UNAVAILABLE = "UNAVAILABLE"
    DEPRECATED = "DEPRECATED"


class ConstructValidationStatus(StrEnum):
    VALIDATED_FOR_CONSTRUCT = "VALIDATED_FOR_CONSTRUCT"
    NOT_VALIDATED_FOR_CONSTRUCT = "NOT_VALIDATED_FOR_CONSTRUCT"
    UNKNOWN = "UNKNOWN"


class Direction(StrEnum):
    HIGHER_IS_BETTER = "HIGHER_IS_BETTER"
    LOWER_IS_BETTER = "LOWER_IS_BETTER"
    TARGET_VALUE = "TARGET_VALUE"
    DESCRIPTIVE_ONLY = "DESCRIPTIVE_ONLY"
    NO_ORDERING = "NO_ORDERING"


class SeparationClass(StrEnum):
    AGENT_VISIBLE = "AGENT_VISIBLE"
    OBSERVER_ONLY = "OBSERVER_ONLY"
    SCIENTIFIC_STATE = "SCIENTIFIC_STATE"
    DEBUG_ONLY = "DEBUG_ONLY"


@dataclass(frozen=True)
class MetricDefinition:
    metric_id: str
    schema_version: str
    construct: str
    proxy: str
    implementation_ref: str | None
    mathematical_definition: str | None
    unit: str
    direction: Direction
    domain: str
    required_signals: tuple[str, ...]
    aggregation: str
    applicability: tuple[str, ...]
    limitations: tuple[str, ...]
    implementation_status: MetricImplementationStatus
    construct_validation_status: ConstructValidationStatus
    provenance: str


@dataclass(frozen=True)
class MetricApplicability:
    metric_id: str
    status: str
    missing_signals: tuple[str, ...]
    available_signals: tuple[str, ...]


@dataclass(frozen=True)
class ObserverChannel:
    channel_id: str
    source: str
    frequency: int
    payload_schema: str
    expected_bytes_per_record: int | None
    separation_class: SeparationClass
    runtime_cost: str
    storage_cost: str
    scientific_purpose: str
    availability: str


@dataclass(frozen=True)
class ObserverProfile:
    profile_id: str
    runtime_mode: str
    channels: tuple[str, ...]
    schema_version: str = OBSERVER_SCHEMA_VERSION


@dataclass(frozen=True)
class StorageEstimate:
    status: str
    estimated_bytes: int | None
    classification: str
    assumptions: tuple[str, ...]
    warning: str | None = None


class MetricRegistry:
    def __init__(self):
        self._metrics: dict[str, MetricDefinition] = {}
        for did in ("D0", "D1", "D2", "D3", "D4"):
            self.register(MetricDefinition(
                f"{did}-energy-trajectory", METRIC_SCHEMA_VERSION,
                "bounded behavioral performance", "energy trajectory",
                "terrario.experiment.metrics:MetricsCalculator", "E_t over episode",
                "energy", Direction.HIGHER_IS_BETTER, "scenario bounded",
                ("agent_energy",), "trajectory and final value", (did,),
                ("energy is not a direct cognitive construct",),
                MetricImplementationStatus.IMPLEMENTED,
                ConstructValidationStatus.NOT_VALIDATED_FOR_CONSTRUCT,
                f"terrario.lab.world_registry:{did}"))
        self.register(MetricDefinition(
            "prediction-error", METRIC_SCHEMA_VERSION, "prediction", "absolute energy prediction error",
            "terrario.agent.scientific:scientific_state", "|predicted_energy - observed_delta|",
            "energy", Direction.LOWER_IS_BETTER, "nonnegative", ("prediction_error",),
            "mean by episode", ("D2", "D3", "D4"),
            ("only available for agents that expose an operational prediction",),
            MetricImplementationStatus.PARTIAL, ConstructValidationStatus.NOT_VALIDATED_FOR_CONSTRUCT,
            "OBSERVE-02 source audit"))
        self.register(MetricDefinition(
            "adaptation-recovery-steps", METRIC_SCHEMA_VERSION, "adaptation", "recovery steps",
            None, None, "steps", Direction.LOWER_IS_BETTER, "nonnegative integer",
            ("causal_intervention", "recovery_event"), "per intervention", ("D4",),
            ("recovery detector is not implemented",), MetricImplementationStatus.PROPOSED,
            ConstructValidationStatus.NOT_VALIDATED_FOR_CONSTRUCT, "theory proposal; not runtime implementation"))

    def register(self, metric: MetricDefinition) -> None:
        self._metrics[metric.metric_id] = metric

    def definitions(self) -> tuple[MetricDefinition, ...]:
        return tuple(self._metrics[k] for k in sorted(self._metrics))

    def get(self, metric_id: str) -> MetricDefinition:
        return self._metrics[metric_id]

    def applicability(self, metric_id: str, scenario: ScenarioDefinition,
                      observer_signals: Iterable[str]) -> MetricApplicability:
        metric = self.get(metric_id)
        available = set(observer_signals) | set(scenario.observation_contract.primitive_features) | set(scenario.required_ground_truth)
        missing = tuple(sorted(set(metric.required_signals) - available))
        if scenario.scenario_id not in metric.applicability:
            return MetricApplicability(metric_id, "NOT_APPLICABLE", missing, tuple(sorted(available)))
        if metric.implementation_status in {MetricImplementationStatus.PROPOSED, MetricImplementationStatus.UNAVAILABLE}:
            return MetricApplicability(metric_id, "IMPLEMENTATION_UNAVAILABLE", missing, tuple(sorted(available)))
        return MetricApplicability(metric_id, "MISSING_REQUIRED_SIGNAL" if missing else "APPLICABLE", missing, tuple(sorted(available)))


class ObserverRegistry:
    def __init__(self):
        rows = (
            ObserverChannel("world", "WorldState", 1, "WorldTrace", 900, SeparationClass.OBSERVER_ONLY, "LOW", "MEDIUM", "world trajectory", "AVAILABLE"),
            ObserverChannel("consequence", "Transition", 1, "ConsequenceTrace", 300, SeparationClass.OBSERVER_ONLY, "LOW", "LOW", "outcome", "AVAILABLE"),
            ObserverChannel("agent_energy", "AgentObservation", 1, "float", 16, SeparationClass.AGENT_VISIBLE, "LOW", "LOW", "behavioral proxy", "AVAILABLE"),
            ObserverChannel("sensation", "AgentObservation", 1, "SensationTrace", 400, SeparationClass.AGENT_VISIBLE, "LOW", "MEDIUM", "input audit", "AVAILABLE"),
            ObserverChannel("decision", "AgentInterface", 1, "DecisionTrace", 240, SeparationClass.SCIENTIFIC_STATE, "LOW", "LOW", "decision audit", "AVAILABLE"),
            ObserverChannel("prediction_error", "get_scientific_state", 1, "PredictionTrace", 320, SeparationClass.SCIENTIFIC_STATE, "MEDIUM", "LOW", "operational prediction diagnostic", "CONDITIONAL"),
            ObserverChannel("internal_tensors", "get_scientific_state", 1, "tensor summary/raw", 4096, SeparationClass.DEBUG_ONLY, "HIGH", "HIGH", "debug inspection only", "CONDITIONAL"),
            ObserverChannel("causal_intervention", "ChangeScheduler", 1, "structured event", 160, SeparationClass.OBSERVER_ONLY, "LOW", "LOW", "manipulation timing", "AVAILABLE"),
        )
        self._channels = {x.channel_id: x for x in rows}
        self._profiles = {
            "SUMMARY": ObserverProfile("SUMMARY", "performance", ("world", "consequence", "agent_energy")),
            "STANDARD": ObserverProfile("STANDARD", "scientific_standard", ("world", "consequence", "agent_energy", "sensation", "decision", "prediction_error", "causal_intervention")),
            "FORENSIC_WINDOW": ObserverProfile("FORENSIC_WINDOW", "forensic_full", ("world", "consequence", "agent_energy", "sensation", "decision", "prediction_error", "causal_intervention", "internal_tensors")),
            "FULL_DEBUG": ObserverProfile("FULL_DEBUG", "forensic_full", tuple(x.channel_id for x in rows)),
        }

    def channels(self) -> tuple[ObserverChannel, ...]:
        return tuple(self._channels[k] for k in sorted(self._channels))

    def profiles(self) -> tuple[ObserverProfile, ...]:
        return tuple(self._profiles[k] for k in ("SUMMARY", "STANDARD", "FORENSIC_WINDOW", "FULL_DEBUG"))

    def profile(self, profile_id: str) -> ObserverProfile:
        return self._profiles[profile_id]

    def expand(self, profile_id: str) -> tuple[ObserverChannel, ...]:
        return tuple(self._channels[x] for x in self.profile(profile_id).channels)

    def agent_projection(self, observation: dict[str, Any], profile_id: str) -> dict[str, Any]:
        # profile_id is deliberately unused: observer verbosity cannot widen this projection.
        return {k: observation[k] for k in sorted(AGENT_FIELDS) if k in observation}

    def estimate(self, profile_id: str, steps: int | None, trials: int | None,
                 checkpoints: int = 0, forensic_window_steps: int = 0) -> StorageEstimate:
        if steps is None or trials is None:
            return StorageEstimate("UNKNOWN", None, "ESTIMATE", ("steps and trials required",))
        if steps < 0 or trials < 0 or checkpoints < 0 or forensic_window_steps < 0:
            raise ValueError("storage dimensions must be nonnegative")
        channels = self.expand(profile_id)
        if any(c.expected_bytes_per_record is None for c in channels):
            return StorageEstimate("UNKNOWN", None, "ESTIMATE", ("channel size unavailable",))
        per_step = sum(c.expected_bytes_per_record // c.frequency for c in channels)
        total = per_step * steps * trials + checkpoints * trials * 1_000_000
        if profile_id == "FORENSIC_WINDOW":
            debug = self._channels["internal_tensors"].expected_bytes_per_record or 0
            total = (per_step - debug) * steps * trials + debug * forensic_window_steps * trials + checkpoints * trials * 1_000_000
        warning = "STORAGE_WARNING" if total > 1_000_000_000 else None
        return StorageEstimate("ESTIMATED", total, "ESTIMATE",
            ("registry byte sizes are engineering estimates", "compression excluded"), warning)
