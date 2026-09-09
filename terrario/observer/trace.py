"""Trace event definitions for the Terrario observer subsystem.

Each trace type captures a specific aspect of the agent-world interaction
for scientific analysis. All traces are immutable records with serialization
support.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import Any


def _serialize_value(v: Any) -> Any:
    """Convert a value to a JSON-safe representation."""
    if isinstance(v, tuple):
        return list(v)
    if isinstance(v, dict):
        return {str(k): _serialize_value(val) for k, val in v.items()}
    if isinstance(v, (list, tuple)):
        return [_serialize_value(item) for item in v]
    return v


@dataclass
class WorldTrace:
    step: int
    world_state_hash: str
    rules_version: int
    time: int
    num_objects: int
    num_agents: int
    object_positions: dict[int, tuple[int, int]]
    agent_positions: dict[int, tuple[int, int]]
    agent_energies: dict[int, float]
    occupancy_sum: int

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "world_state_hash": self.world_state_hash,
            "rules_version": self.rules_version,
            "time": self.time,
            "num_objects": self.num_objects,
            "num_agents": self.num_agents,
            "object_positions": {str(k): list(v) for k, v in self.object_positions.items()},
            "agent_positions": {str(k): list(v) for k, v in self.agent_positions.items()},
            "agent_energies": {str(k): v for k, v in self.agent_energies.items()},
            "occupancy_sum": self.occupancy_sum,
        }

    @classmethod
    def from_dict(cls, d: dict) -> WorldTrace:
        return cls(
            step=d["step"],
            world_state_hash=d["world_state_hash"],
            rules_version=d["rules_version"],
            time=d["time"],
            num_objects=d["num_objects"],
            num_agents=d["num_agents"],
            object_positions={int(k): tuple(v) for k, v in d["object_positions"].items()},
            agent_positions={int(k): tuple(v) for k, v in d["agent_positions"].items()},
            agent_energies={int(k): v for k, v in d["agent_energies"].items()},
            occupancy_sum=d["occupancy_sum"],
        )


@dataclass
class SensationTrace:
    step: int
    obs_hash: str
    obs_shape: tuple
    mask_coverage: float
    agent_energy: float
    time_fraction: float
    channel_stats: dict[str, float]

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "obs_hash": self.obs_hash,
            "obs_shape": list(self.obs_shape),
            "mask_coverage": self.mask_coverage,
            "agent_energy": self.agent_energy,
            "time_fraction": self.time_fraction,
            "channel_stats": dict(self.channel_stats),
        }

    @classmethod
    def from_dict(cls, d: dict) -> SensationTrace:
        return cls(
            step=d["step"],
            obs_hash=d["obs_hash"],
            obs_shape=tuple(d["obs_shape"]),
            mask_coverage=d["mask_coverage"],
            agent_energy=d["agent_energy"],
            time_fraction=d["time_fraction"],
            channel_stats=dict(d["channel_stats"]),
        )


@dataclass
class PerceptionTrace:
    step: int
    latent_norm: float
    latent_mean: float
    latent_std: float
    latent_dim: int
    latent_vector: list[float] | None = None

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "latent_norm": self.latent_norm,
            "latent_mean": self.latent_mean,
            "latent_std": self.latent_std,
            "latent_dim": self.latent_dim,
            "latent_vector": self.latent_vector,
        }

    @classmethod
    def from_dict(cls, d: dict) -> PerceptionTrace:
        return cls(
            step=d["step"],
            latent_norm=d["latent_norm"],
            latent_mean=d["latent_mean"],
            latent_std=d["latent_std"],
            latent_dim=d["latent_dim"],
            latent_vector=d.get("latent_vector"),
        )


@dataclass
class TemporalTrace:
    step: int
    h_norm: float
    h_mean: float
    h_std: float
    core_type: str
    h_vector: list[float] | None = None

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "h_norm": self.h_norm,
            "h_mean": self.h_mean,
            "h_std": self.h_std,
            "core_type": self.core_type,
            "h_vector": self.h_vector,
        }

    @classmethod
    def from_dict(cls, d: dict) -> TemporalTrace:
        return cls(
            step=d["step"],
            h_norm=d["h_norm"],
            h_mean=d["h_mean"],
            h_std=d["h_std"],
            core_type=d["core_type"],
            h_vector=d.get("h_vector"),
        )


@dataclass
class MemoryTrace:
    step: int
    operation: str
    memory_type: str
    memory_size: int
    query_norm: float
    result_norm: float
    similarity_scores: list[float] | None = None

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "operation": self.operation,
            "memory_type": self.memory_type,
            "memory_size": self.memory_size,
            "query_norm": self.query_norm,
            "result_norm": self.result_norm,
            "similarity_scores": self.similarity_scores,
        }

    @classmethod
    def from_dict(cls, d: dict) -> MemoryTrace:
        return cls(
            step=d["step"],
            operation=d["operation"],
            memory_type=d["memory_type"],
            memory_size=d["memory_size"],
            query_norm=d["query_norm"],
            result_norm=d["result_norm"],
            similarity_scores=d.get("similarity_scores"),
        )


@dataclass
class PredictionTrace:
    step: int
    predicted_energy: float
    actual_energy: float | None
    prediction_error: float | None
    uncertainty: float
    ensemble_predictions: list[float] | None = None

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "predicted_energy": self.predicted_energy,
            "actual_energy": self.actual_energy,
            "prediction_error": self.prediction_error,
            "uncertainty": self.uncertainty,
            "ensemble_predictions": self.ensemble_predictions,
        }

    @classmethod
    def from_dict(cls, d: dict) -> PredictionTrace:
        return cls(
            step=d["step"],
            predicted_energy=d["predicted_energy"],
            actual_energy=d.get("actual_energy"),
            prediction_error=d.get("prediction_error"),
            uncertainty=d["uncertainty"],
            ensemble_predictions=d.get("ensemble_predictions"),
        )


@dataclass
class DecisionTrace:
    step: int
    action_int: int
    action_type: str
    direction: str
    logits_top5: list[float]
    probs_top5: list[float]
    selected_prob: float
    planner_used: bool
    planner_rollouts: int | None = None

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "action_int": self.action_int,
            "action_type": self.action_type,
            "direction": self.direction,
            "logits_top5": list(self.logits_top5),
            "probs_top5": list(self.probs_top5),
            "selected_prob": self.selected_prob,
            "planner_used": self.planner_used,
            "planner_rollouts": self.planner_rollouts,
        }

    @classmethod
    def from_dict(cls, d: dict) -> DecisionTrace:
        return cls(
            step=d["step"],
            action_int=d["action_int"],
            action_type=d["action_type"],
            direction=d["direction"],
            logits_top5=list(d["logits_top5"]),
            probs_top5=list(d["probs_top5"]),
            selected_prob=d["selected_prob"],
            planner_used=d["planner_used"],
            planner_rollouts=d.get("planner_rollouts"),
        )


@dataclass
class ConsequenceTrace:
    step: int
    executed_action: int
    energy_delta: float
    done: bool
    events: list[str]

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "executed_action": self.executed_action,
            "energy_delta": self.energy_delta,
            "done": self.done,
            "events": list(self.events),
        }

    @classmethod
    def from_dict(cls, d: dict) -> ConsequenceTrace:
        return cls(
            step=d["step"],
            executed_action=d["executed_action"],
            energy_delta=d["energy_delta"],
            done=d["done"],
            events=list(d["events"]),
        )


@dataclass
class LearningTrace:
    step: int
    loss_total: float
    loss_components: dict[str, float]
    grad_norms: dict[str, float]
    param_norms: dict[str, float]
    learning_rate: float

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "loss_total": self.loss_total,
            "loss_components": dict(self.loss_components),
            "grad_norms": dict(self.grad_norms),
            "param_norms": dict(self.param_norms),
            "learning_rate": self.learning_rate,
        }

    @classmethod
    def from_dict(cls, d: dict) -> LearningTrace:
        return cls(
            step=d["step"],
            loss_total=d["loss_total"],
            loss_components=dict(d["loss_components"]),
            grad_norms=dict(d["grad_norms"]),
            param_norms=dict(d["param_norms"]),
            learning_rate=d["learning_rate"],
        )


@dataclass
class ProvenanceTrace:
    step: int
    run_id: str
    episode: int
    seed: int
    config_hash: str
    timestamp: float

    def to_dict(self) -> dict:
        return {
            "step": self.step,
            "run_id": self.run_id,
            "episode": self.episode,
            "seed": self.seed,
            "config_hash": self.config_hash,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, d: dict) -> ProvenanceTrace:
        return cls(
            step=d["step"],
            run_id=d["run_id"],
            episode=d["episode"],
            seed=d["seed"],
            config_hash=d["config_hash"],
            timestamp=d["timestamp"],
        )


@dataclass
class TransitionTrace:
    """One reconstructable agent/world transition and its provenance."""

    step: int
    observation_t_hash: str
    observation_t1_hash: str
    observation_t: dict[str, Any]
    observation_t1: dict[str, Any]
    action_t: int
    terminated: bool
    truncated: bool
    consequence: dict[str, Any]
    agent_identity: dict[str, Any]
    internal_state: dict[str, Any]
    observer_world: dict[str, Any]
    agent_trace_events: list[dict[str, Any]]
    parameter_deltas: dict[str, float] | None = None
    observer_annotations: dict[str, Any] | None = None
    scientific_state: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "step": self.step, "observation_t_hash": self.observation_t_hash,
            "observation_t1_hash": self.observation_t1_hash,
            "observation_t": _serialize_value(self.observation_t),
            "observation_t1": _serialize_value(self.observation_t1), "action_t": self.action_t,
            "terminated": self.terminated, "truncated": self.truncated,
            "consequence": _serialize_value(self.consequence),
            "agent_identity": _serialize_value(self.agent_identity),
            "internal_state": _serialize_value(self.internal_state),
            "observer_world": _serialize_value(self.observer_world),
            "agent_trace_events": _serialize_value(self.agent_trace_events),
            "parameter_deltas": _serialize_value(self.parameter_deltas),
            "observer_annotations": _serialize_value(self.observer_annotations),
            "scientific_state": _serialize_value(self.scientific_state),
        }


# Registry mapping trace type names to classes
TRACE_REGISTRY: dict[str, type] = {
    "world": WorldTrace,
    "sensation": SensationTrace,
    "perception": PerceptionTrace,
    "temporal": TemporalTrace,
    "memory": MemoryTrace,
    "prediction": PredictionTrace,
    "decision": DecisionTrace,
    "consequence": ConsequenceTrace,
    "learning": LearningTrace,
    "provenance": ProvenanceTrace,
    "transition": TransitionTrace,
}
