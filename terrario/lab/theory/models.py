"""Canonical, non-destructive records for Theory of Intelligence artifacts."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import StrEnum
from typing import Any

from terrario.lab.models import EpistemicStatus, freeze
from terrario.lab.persistence.canonical import content_hash


class MappingRelation(StrEnum):
    EXACT_SYNONYM = "EXACT_SYNONYM"
    CONTEXTUAL_SYNONYM = "CONTEXTUAL_SYNONYM"
    PARTIAL_OVERLAP = "PARTIAL_OVERLAP"
    SUBTYPE_OF = "SUBTYPE_OF"
    PART_OF = "PART_OF"
    RELATED_BUT_DISTINCT = "RELATED_BUT_DISTINCT"
    HOMONYM_DIFFERENT_MEANING = "HOMONYM_DIFFERENT_MEANING"
    TRANSLATION_EQUIVALENT = "TRANSLATION_EQUIVALENT"
    UNRESOLVED = "UNRESOLVED"


class RelationStrength(StrEnum):
    CONTEXTUAL_COOCCURRENCE = "CONTEXTUAL_COOCCURRENCE"
    ASSOCIATION = "ASSOCIATION"
    FACILITATION_MODULATION = "FACILITATION_MODULATION"
    REQUIREMENT_DEPENDENCY = "REQUIREMENT_DEPENDENCY"
    EXPLICIT_CAUSAL_CLAIM = "EXPLICIT_CAUSAL_CLAIM"


@dataclass(frozen=True, kw_only=True)
class TheoryRecord:
    id: str
    original_id: str
    original_text: str
    source_artifact: str
    source_version: str
    provenance: str
    epistemic_status: EpistemicStatus
    fields: Any = field(default_factory=dict)

    def __post_init__(self): object.__setattr__(self, "fields", freeze(self.fields))


@dataclass(frozen=True, kw_only=True)
class SourceRecord(TheoryRecord):
    integrity_status: str = "UNRESOLVED"
    valid_evidence_source: bool = True


@dataclass(frozen=True, kw_only=True)
class ClaimRecord(TheoryRecord):
    source_id: str = "UNRESOLVED"
    attribution: str = "UNRESOLVED"


@dataclass(frozen=True, kw_only=True)
class RawConceptRecord(TheoryRecord): pass


@dataclass(frozen=True, kw_only=True)
class CanonicalConceptCandidate(TheoryRecord):
    raw_concept_id: str
    mapping_relation: str


@dataclass(frozen=True, kw_only=True)
class RelationRecord(TheoryRecord):
    source_concept: str
    target_concept: str
    relation_type: str
    strength: RelationStrength
    attribution: str


@dataclass(frozen=True, kw_only=True)
class AmbiguityRecord(TheoryRecord): pass


@dataclass(frozen=True, kw_only=True)
class ConflictRecord(TheoryRecord):
    conflict_type: str = "UNRESOLVED_CONFLICT_TYPE"
    participants: tuple[str, ...] = ()


@dataclass(frozen=True, kw_only=True)
class HyperedgeCandidateRecord(TheoryRecord):
    components: tuple[str, ...]
    predicted_outcome: str
    attribution: str
    conjunction_explicitness: str
    necessity: str
    sufficiency: str
    level: str
    discriminating_test: str
    confounders: tuple[str, ...]
    decision: str


@dataclass(frozen=True, kw_only=True)
class CoverageRecord(TheoryRecord):
    concept_family: str
    coverage_status: str


@dataclass(frozen=True, kw_only=True)
class IntegrityRecord(TheoryRecord):
    integrity_status: str


@dataclass(frozen=True)
class HypothesisPremise:
    source_hyperedge_id: str
    participant: str
    role: str
    claim_id: str
    source_id: str
    source_locator: str


@dataclass(frozen=True)
class HypothesisDraft:
    id: str
    source_hyperedge_id: str
    components: tuple[str, ...]
    predicted_outcome: str
    source_provenance: str
    confounders: tuple[str, ...]
    discriminating_test: str
    coverage_status: str
    epistemic_status: str = "REVIEW_REQUIRED"
    theory_warning: str | None = None
    premises: tuple[HypothesisPremise, ...] = ()
    composition_path: tuple[str, ...] = ()
    derivation_rule: str | None = None
    assumptions: tuple[str, ...] = ()
    known_contradictions: tuple[str, ...] = ()
    novelty_evidence: str | None = None
    testability: str = "UNASSESSED"
    target_domain: str | None = None
    required_capabilities: tuple[str, ...] = ()
    prediction: str | None = None

    @property
    def semantic_id(self) -> str:
        return "HYPOTHESIS-" + content_hash({
            "source_hyperedge_id": self.source_hyperedge_id,
            "components": sorted(self.components),
            "predicted_outcome": self.predicted_outcome,
            "source_provenance": self.source_provenance,
            "confounders": sorted(self.confounders),
            "discriminating_test": self.discriminating_test,
            "coverage_status": self.coverage_status,
            "theory_warning": self.theory_warning,
            "premises": sorted((asdict(item) for item in self.premises), key=lambda item: (item["source_hyperedge_id"], item["claim_id"], item["participant"], item["role"])),
            "composition_path": sorted(self.composition_path),
            "derivation_rule": self.derivation_rule,
            "assumptions": sorted(self.assumptions),
            "known_contradictions": sorted(self.known_contradictions),
            "novelty_evidence": self.novelty_evidence,
            "testability": self.testability,
            "target_domain": self.target_domain,
            "required_capabilities": sorted(self.required_capabilities),
            "prediction": self.prediction,
            "epistemic_status": self.epistemic_status,
        })[:16]

    def payload(self) -> dict:
        return {"schema": "terrario.theory.hypothesis-draft/v2", **asdict(self), "semantic_id": self.semantic_id}

    @classmethod
    def from_payload(cls, payload: dict) -> "HypothesisDraft":
        if payload.get("schema") != "terrario.theory.hypothesis-draft/v2":
            raise ValueError("unsupported hypothesis payload schema")
        try:
            draft = cls(
                id=payload["id"], source_hyperedge_id=payload["source_hyperedge_id"],
                components=tuple(payload["components"]), predicted_outcome=payload["predicted_outcome"],
                source_provenance=payload["source_provenance"], confounders=tuple(payload["confounders"]),
                discriminating_test=payload["discriminating_test"], coverage_status=payload["coverage_status"],
                epistemic_status=payload["epistemic_status"], theory_warning=payload.get("theory_warning"),
                premises=tuple(HypothesisPremise(**item) for item in payload.get("premises", ())),
                composition_path=tuple(payload.get("composition_path", ())),
                derivation_rule=payload.get("derivation_rule"), assumptions=tuple(payload.get("assumptions", ())),
                known_contradictions=tuple(payload.get("known_contradictions", ())),
                novelty_evidence=payload.get("novelty_evidence"), testability=payload.get("testability", "UNASSESSED"),
                target_domain=payload.get("target_domain"), required_capabilities=tuple(payload.get("required_capabilities", ())),
                prediction=payload.get("prediction"),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("invalid hypothesis payload") from exc
        if payload.get("semantic_id") != draft.semantic_id:
            raise ValueError("hypothesis semantic identity mismatch after deserialization")
        return draft


@dataclass(frozen=True)
class ExperimentPreview:
    hypothesis_draft_id: str
    full_condition: tuple[str, ...]
    ablations: tuple[str, ...]
    controls: tuple[str, ...]
    expected_observations: tuple[str, ...]
    falsification_conditions: tuple[str, ...]
    likely_confounders: tuple[str, ...]
    status: str = "REVIEW_REQUIRED"
