"""Experiment configuration for Terrario."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Mapping

import yaml

from terrario.experiment.hypothesis import HypothesisSpec


@dataclass
class ExperimentConfig:
    """Full configuration for a single experiment run."""

    experiment_id: str
    hypothesis: HypothesisSpec | None
    scenario_path: str
    agent_types: list[str]  # ["A0_RANDOM", "A1_REACTIVE", ...]
    agent_config: dict  # config for A4
    seeds: list[int]
    num_episodes: int
    max_steps_per_episode: int
    observer_mode: str  # "performance", "scientific_standard", "forensic_full"
    checkpoint_every: int
    output_dir: str
    device: str = "cpu"
    # An in-memory, already validated scenario may enter the same controller
    # path as a YAML scenario.  This is deliberately additive: persisted
    # experiments keep using ``scenario_path``; generated diagnostic worlds do
    # not need a lossy temporary YAML file or a second execution loop.
    scenario_payload: Mapping[str, Any] | None = None
    # Scientific origin of an inline scenario.  It is part of the config hash
    # and is passed to the observer, but never interpreted as runtime physics.
    scenario_provenance: Mapping[str, Any] | None = None

    @staticmethod
    def from_yaml(path: str) -> ExperimentConfig:
        """Load an ExperimentConfig from a YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)

        exp = data.get("experiment", data)

        hypothesis = None
        if "hypothesis" in exp and exp["hypothesis"] is not None:
            h = exp["hypothesis"]
            hypothesis = HypothesisSpec(
                hypothesis_id=h["hypothesis_id"],
                claim=h["claim"],
                participants=h.get("participants", []),
                predicted_effect=h.get("predicted_effect", ""),
                world_pressure=h.get("world_pressure", ""),
                controls=h.get("controls", []),
                ablations=h.get("ablations", []),
                evidence_required=h.get("evidence_required", []),
            )

        return ExperimentConfig(
            experiment_id=exp.get("experiment_id", "unnamed"),
            hypothesis=hypothesis,
            scenario_path=exp.get("scenario_path", ""),
            agent_types=exp.get("agent_types", ["A0_RANDOM"]),
            agent_config=exp.get("agent_config", {}),
            seeds=exp.get("seeds", [42]),
            num_episodes=exp.get("num_episodes", 1),
            max_steps_per_episode=exp.get("max_steps_per_episode", 500),
            observer_mode=exp.get("observer_mode", "scientific_standard"),
            checkpoint_every=exp.get("checkpoint_every", 100),
            output_dir=exp.get("output_dir", "runs"),
            device=exp.get("device", "cpu"),
            scenario_payload=exp.get("scenario_payload"),
            scenario_provenance=exp.get("scenario_provenance"),
        )

    def config_hash(self) -> str:
        """SHA256 of the serialized config for reproducibility tracking."""
        data = {
            "experiment_id": self.experiment_id,
            "scenario_path": self.scenario_path,
            "agent_types": sorted(self.agent_types),
            "agent_config": self.agent_config,
            "seeds": sorted(self.seeds),
            "num_episodes": self.num_episodes,
            "max_steps_per_episode": self.max_steps_per_episode,
            "observer_mode": self.observer_mode,
            "checkpoint_every": self.checkpoint_every,
            "device": self.device,
            "scenario_payload": self.scenario_payload,
            "scenario_provenance": self.scenario_provenance,
        }
        if self.hypothesis is not None:
            data["hypothesis"] = {
                "hypothesis_id": self.hypothesis.hypothesis_id,
                "claim": self.hypothesis.claim,
            }
        serialized = json.dumps(data, sort_keys=True, default=str)
        return hashlib.sha256(serialized.encode()).hexdigest()
