"""Small, hashable intervention contracts for approved capabilities.

An intervention contract is an execution-plane declaration.  It records what
may diverge directly; it does not alter a corpus claim or claim that a
capability produces any behavioral result.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Mapping

from terrario.lab.persistence.canonical import content_hash


SCHEMA_VERSION = "terrario.lab.capability-intervention/v1"


class InterventionMode(StrEnum):
    SUPPRESS_COMMIT = "SUPPRESS_COMMIT"


@dataclass(frozen=True)
class InterventionManifest:
    capability_id: str
    operationalization_id: str
    implementation_version: str
    intervention_target: str
    intervention_mode: InterventionMode
    allowed_direct_write_set: tuple[str, ...]
    forbidden_direct_write_set: tuple[str, ...]
    preconditions: tuple[str, ...]
    expected_first_divergence: str

    def __post_init__(self) -> None:
        required = (self.capability_id, self.operationalization_id,
                    self.implementation_version, self.intervention_target,
                    self.allowed_direct_write_set, self.forbidden_direct_write_set,
                    self.preconditions, self.expected_first_divergence)
        if not all(required):
            raise ValueError("intervention manifest is incomplete")

    @property
    def semantic_id(self) -> str:
        return "INTERVENTION-" + content_hash(self._payload())[:16]

    def _payload(self) -> dict:
        payload = asdict(self)
        payload["intervention_mode"] = self.intervention_mode.value
        return payload

    def payload(self) -> dict:
        return {"schema": SCHEMA_VERSION, **self._payload(), "semantic_id": self.semantic_id}

    @classmethod
    def from_payload(cls, payload: Mapping) -> "InterventionManifest":
        if payload.get("schema") != SCHEMA_VERSION:
            raise ValueError("unsupported intervention manifest schema")
        try:
            manifest = cls(
                capability_id=payload["capability_id"],
                operationalization_id=payload["operationalization_id"],
                implementation_version=payload["implementation_version"],
                intervention_target=payload["intervention_target"],
                intervention_mode=InterventionMode(payload["intervention_mode"]),
                allowed_direct_write_set=tuple(payload["allowed_direct_write_set"]),
                forbidden_direct_write_set=tuple(payload["forbidden_direct_write_set"]),
                preconditions=tuple(payload["preconditions"]),
                expected_first_divergence=payload["expected_first_divergence"],
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("invalid intervention manifest payload") from exc
        if payload.get("semantic_id") != manifest.semantic_id:
            raise ValueError("intervention manifest identity mismatch")
        return manifest


LEARN_A1_COMMIT_MANIFEST = InterventionManifest(
    capability_id="LEARN-A1",
    operationalization_id="OPR-LEARN-A1-RL-01",
    implementation_version="OnlineLearner@v1",
    intervention_target="OnlineLearner.step.optimizer_commit",
    intervention_mode=InterventionMode.SUPPRESS_COMMIT,
    allowed_direct_write_set=(
        "learner._modules.*.parameters",
        "learner._optimizer.state.{step,exp_avg,exp_avg_sq}",
        "learner._trace.commit_applied",
    ),
    forbidden_direct_write_set=(
        "agent.capability_composition", "agent.architecture", "agent._generator",
        "planner.enablement", "world_model.enablement", "episodic_memory.enablement",
        "longterm_memory.enablement", "uncertainty.enablement", "homeostasis.enablement",
        "observation_contract", "action_contract", "world_definition", "world_instance",
        "world_rng", "world_physics",
    ),
    preconditions=(
        "same A4 configuration except learning_commit_enabled",
        "use_online_learning remains true in both arms",
        "same initial parameters, optimizer definition, and agent RNG state",
        "same ordered replay experiences before comparing direct writes",
    ),
    expected_first_divergence="POST_COMMIT: learner parameters or Adam optimizer state",
)
