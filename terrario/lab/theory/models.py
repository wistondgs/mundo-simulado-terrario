"""Canonical, non-destructive records for Theory of Intelligence artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from terrario.lab.models import EpistemicStatus, freeze


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
