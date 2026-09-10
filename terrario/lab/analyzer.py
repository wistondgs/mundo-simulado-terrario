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


class DeterministicScientificAnalyzer(ExternalAnalyzerPlugin):
    """Mechanical evidence checks only; it does not interpret intelligence."""

    @property
    def analyzer_id(self) -> str: return "deterministic-scientific-v1"

    def analyze(self, request: ExternalAnalyzerInput) -> ExternalAnalyzerResult:
        manifest = request.evidence_manifest; metrics = request.metrics
        findings, anomalies, concerns, followups = [], [], [], []
        required = ("code_hash", "config_hash", "protocol")
        missing = tuple(key for key in required if not manifest.get(key))
        findings.append("evidence package complete" if not missing else f"missing manifest fields: {', '.join(missing)}")
        invalid = metrics.get("invalid_runs", ()) if hasattr(metrics, "get") else ()
        if invalid: anomalies.append(f"invalid runs: {len(invalid)}")
        deviations = metrics.get("protocol_deviations", ()) if hasattr(metrics, "get") else ()
        if deviations: concerns.append(f"protocol deviations: {len(deviations)}")
        sensitivity = metrics.get("threshold_sensitivity", None) if hasattr(metrics, "get") else None
        if sensitivity: concerns.append("threshold sensitivity requires review")
        if missing or invalid: followups.append("complete or reconcile the evidence package")
        return ExternalAnalyzerResult(self.analyzer_id, tuple(findings), tuple(anomalies),
            ("measurement or sampling confounders require explicit review",), tuple(concerns),
            1.0 if not missing and not anomalies else 0.5, tuple(followups))


@dataclass(frozen=True)
class AnalyzerResultSet:
    results: tuple[ExternalAnalyzerResult, ...]

    def compare(self):
        buckets: dict[str, set[str]] = {}
        for result in self.results:
            for finding in (*result.findings, *result.anomalies, *result.methodological_concerns):
                buckets.setdefault(finding, set()).add(result.analyzer_id)
        all_ids = {result.analyzer_id for result in self.results}
        return freeze({
            "agreements": sorted(text for text, ids in buckets.items() if ids == all_ids and len(all_ids) > 1),
            "disagreements": sorted(text for text, ids in buckets.items() if ids != all_ids),
            "unresolved_findings": sorted(buckets),
            "truth_by_vote": False,
        })
