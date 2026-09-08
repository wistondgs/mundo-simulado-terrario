"""Serializable contracts from hypothesis through experimental evidence."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from typing import Any

from terrario.experiment.hypothesis import HypothesisSpec


@dataclass(frozen=True)
class ExperimentSpec:
    experiment_id: str
    hypothesis_id: str
    condition_id: str
    agent_id: str
    agent_overrides: dict[str, Any]
    scenario_path: str
    seeds: list[int]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def config_hash(self) -> str:
        return hashlib.sha256(json.dumps(self.to_dict(), sort_keys=True).encode()).hexdigest()


@dataclass(frozen=True)
class EvidenceSpec:
    concept_id: str
    hypothesis_id: str
    relation_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_spec: EvidenceSpec
    experiment_id: str
    run_id: str
    config_hash: str
    code_hash: str
    metrics: dict[str, float] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["evidence_spec"] = self.evidence_spec.to_dict()
        return data


def synthetic_h_adapt_001() -> HypothesisSpec:
    """A test object, not a truth claim about the architecture."""
    return HypothesisSpec(
        hypothesis_id="H-ADAPT-001",
        claim="{memory, prediction, error_detection} -> adaptation",
        participants=["memory", "prediction", "error_detection"],
        predicted_effect="adaptation", world_pressure="causal_rule_reversal",
        controls=["A1_REACTIVE", "A0_RANDOM"],
        ablations=["use_episodic_memory", "use_world_model", "use_online_learning"],
        evidence_required=["multiple_seeds", "matched_compute"],
    )


def experiments_from_hypothesis(
    hypothesis: HypothesisSpec, scenario_path: str, seeds: list[int], agent_id: str = "A4_ADVANCED",
) -> list[ExperimentSpec]:
    conditions = [
        ("full", agent_id, {}),
        ("no-memory", agent_id, {"use_episodic_memory": False, "use_longterm_memory": False}),
        ("no-prediction", agent_id, {"use_world_model": False}),
        ("no-online-learning", agent_id, {"use_online_learning": False}),
        ("reactive", "A1_REACTIVE", {}),
        ("random", "A0_RANDOM", {}),
    ]
    return [ExperimentSpec(
        experiment_id=f"{hypothesis.hypothesis_id}:{condition}", hypothesis_id=hypothesis.hypothesis_id,
        condition_id=condition, agent_id=requested_agent, agent_overrides=overrides,
        scenario_path=scenario_path, seeds=list(seeds),
    ) for condition, requested_agent, overrides in conditions]
