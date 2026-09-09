"""Provider-neutral contract for analysis outside the experimental core."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from terrario.lab.models import freeze


@dataclass(frozen=True)
class ExternalAnalyzerInput:
    hypothesis_spec: Any; protocol: str; version: str; evidence_manifest: Any
    metrics: Any; selected_traces: tuple[Any, ...]; forensic_cases: tuple[Any, ...]; provenance: Any

    def __post_init__(self):
        for name in ("hypothesis_spec", "evidence_manifest", "metrics", "provenance"):
            object.__setattr__(self, name, freeze(getattr(self, name)))
        object.__setattr__(self, "selected_traces", freeze(self.selected_traces))
        object.__setattr__(self, "forensic_cases", freeze(self.forensic_cases))


@dataclass(frozen=True)
class ExternalAnalyzerResult:
    analyzer_id: str; findings: tuple[str, ...]; anomalies: tuple[str, ...]
    alternative_explanations: tuple[str, ...]; methodological_concerns: tuple[str, ...]
    confidence: float; requested_follow_up_experiments: tuple[str, ...]
    artifact_type: str = "DERIVED_ANALYSIS"


class ExternalAnalyzerPlugin(ABC):
    @property
    @abstractmethod
    def analyzer_id(self) -> str: ...

    @abstractmethod
    def analyze(self, request: ExternalAnalyzerInput) -> ExternalAnalyzerResult: ...


class AnalyzerRegistry:
    def __init__(self): self._plugins: dict[str, ExternalAnalyzerPlugin] = {}
    def register(self, plugin: ExternalAnalyzerPlugin): self._plugins[plugin.analyzer_id] = plugin
    def analyze(self, analyzer_id: str, request: ExternalAnalyzerInput):
        result = self._plugins[analyzer_id].analyze(request)
        if result.artifact_type != "DERIVED_ANALYSIS": raise ValueError("analyzers may only emit DERIVED_ANALYSIS")
        return result
