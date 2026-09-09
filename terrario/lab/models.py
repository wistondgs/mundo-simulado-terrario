"""Immutable contracts exposed by the laboratory read model."""

from __future__ import annotations

from dataclasses import dataclass, fields
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping

NOT_APPLICABLE = "NOT_APPLICABLE"


class EpistemicStatus(StrEnum):
    RAW = "RAW"
    CANONICAL_CANDIDATE = "CANONICAL_CANDIDATE"
    AUTHOR_CLAIM = "AUTHOR_CLAIM"
    ANALYST_INFERENCE = "ANALYST_INFERENCE"
    TESTABLE_CONJUNCTION = "TESTABLE_CONJUNCTION"
    UNTESTED_HYPOTHESIS = "UNTESTED_HYPOTHESIS"
    EVIDENCE_FOR = "EVIDENCE_FOR"
    EVIDENCE_AGAINST = "EVIDENCE_AGAINST"
    UNRESOLVED = "UNRESOLVED"


def freeze(value: Any) -> Any:
    if isinstance(value, Mapping):
        return MappingProxyType({str(k): freeze(v) for k, v in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(freeze(v) for v in value)
    return value


def thaw(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(k): thaw(v) for k, v in value.items()}
    if isinstance(value, (tuple, list)):
        return [thaw(v) for v in value]
    if isinstance(value, StrEnum):
        return value.value
    if hasattr(value, "__dataclass_fields__"):
        return {field.name: thaw(getattr(value, field.name)) for field in fields(value)}
    return value


@dataclass(frozen=True)
class ExperimentRecord:
    id: str; status: str; protocol: str; source: str
    config_hash: str = NOT_APPLICABLE; code_hash: str = NOT_APPLICABLE
    locked: bool = False; run_count: int = 0


@dataclass(frozen=True)
class RunRecord:
    id: str; experiment_id: str; status: str; variant: str; seed: int | str
    source: str; config_hash: str = NOT_APPLICABLE; code_hash: str = NOT_APPLICABLE
    protocol: str = NOT_APPLICABLE; evidence_path: str = NOT_APPLICABLE
    technical_valid: bool | str = NOT_APPLICABLE
    experimental_valid: bool | str = NOT_APPLICABLE


@dataclass(frozen=True)
class HypothesisRecord:
    id: str; status: str; claim: str; protocol: str; source: str


@dataclass(frozen=True)
class EvidenceRecordSummary:
    id: str; status: str; source: str; experiment_id: str
    code_hash: str = NOT_APPLICABLE; config_hash: str = NOT_APPLICABLE


@dataclass(frozen=True)
class ForensicCaseRecord:
    id: str; status: str; source: str; run_id: str


@dataclass(frozen=True)
class TimelinePoint:
    step: int
    action: int | str = NOT_APPLICABLE
    energy: float | str = NOT_APPLICABLE
    causal_competence: float | str = NOT_APPLICABLE
    prediction_error: float | str = NOT_APPLICABLE
    uncertainty: float | str = NOT_APPLICABLE
    policy_entropy: float | str = NOT_APPLICABLE
    memory_events: tuple[Any, ...] | str = NOT_APPLICABLE
    learning_events: tuple[Any, ...] | str = NOT_APPLICABLE
    causal_change: bool | str = NOT_APPLICABLE
    checkpoint: str = NOT_APPLICABLE
    origin: str = "RECORDED"


@dataclass(frozen=True)
class RunTimeline:
    run_id: str; points: tuple[TimelinePoint, ...]; source: str


@dataclass(frozen=True)
class AgentWorldView:
    run_id: str; step: int; channels: tuple[Any, ...]; mask: tuple[Any, ...]
    agent_energy: float | str; time_fraction: float | str; origin: str = "RECORDED"


@dataclass(frozen=True)
class ObserverWorldView:
    run_id: str; step: int; grid_width: int; grid_height: int
    objects: Mapping[str, Any]; agents: Mapping[str, Any]
    active_rule: int | str; change_event: bool | str
    opportunity_lifecycle: Any = NOT_APPLICABLE; origin: str = "RECORDED"
