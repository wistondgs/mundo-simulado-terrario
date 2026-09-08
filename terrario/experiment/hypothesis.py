"""Hypothesis specification for Terrario experiments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import yaml


@dataclass
class HypothesisSpec:
    """A testable hypothesis about cognitive development."""

    hypothesis_id: str
    claim: str
    participants: list[str]  # e.g. ["memory", "prediction", "error_detection"]
    predicted_effect: str
    world_pressure: str  # e.g. "causal_rule_reversal"
    controls: list[str]  # agent types to compare against
    ablations: list[str]  # modules to ablate
    evidence_required: list[str]  # e.g. ["generalization", "matched_compute", "multiple_seeds"]

    @staticmethod
    def from_yaml(path: str) -> HypothesisSpec:
        """Load a HypothesisSpec from a YAML file."""
        with open(path) as f:
            data = yaml.safe_load(f)
        h = data.get("hypothesis", data)
        return HypothesisSpec(
            hypothesis_id=h["hypothesis_id"],
            claim=h["claim"],
            participants=h.get("participants", []),
            predicted_effect=h.get("predicted_effect", ""),
            world_pressure=h.get("world_pressure", ""),
            controls=h.get("controls", []),
            ablations=h.get("ablations", []),
            evidence_required=h.get("evidence_required", []),
        )

    def to_yaml(self, path: str) -> None:
        """Serialize this HypothesisSpec to a YAML file."""
        data = {
            "hypothesis": {
                "hypothesis_id": self.hypothesis_id,
                "claim": self.claim,
                "participants": self.participants,
                "predicted_effect": self.predicted_effect,
                "world_pressure": self.world_pressure,
                "controls": self.controls,
                "ablations": self.ablations,
                "evidence_required": self.evidence_required,
            }
        }
        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False)
