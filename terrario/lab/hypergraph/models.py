"""Provenance-preserving hypergraph interchange contracts."""

from __future__ import annotations

from dataclasses import dataclass

from terrario.lab.models import EpistemicStatus


@dataclass(frozen=True)
class SourceRecord:
    id: str; label: str; provenance: str; status: EpistemicStatus = EpistemicStatus.RAW

@dataclass(frozen=True)
class ClaimRecord:
    id: str; text: str; source_id: str; provenance: str; status: EpistemicStatus = EpistemicStatus.AUTHOR_CLAIM

@dataclass(frozen=True)
class ConceptRecord:
    id: str; label: str; source_ids: tuple[str, ...]; provenance: str; status: EpistemicStatus = EpistemicStatus.CANONICAL_CANDIDATE

@dataclass(frozen=True)
class RelationRecord:
    id: str; members: tuple[str, ...]; relation: str; provenance: str; status: EpistemicStatus = EpistemicStatus.UNRESOLVED

@dataclass(frozen=True)
class HyperedgeCandidateRecord:
    id: str; members: tuple[str, ...]; provenance: str; status: EpistemicStatus = EpistemicStatus.TESTABLE_CONJUNCTION

@dataclass(frozen=True)
class HypothesisRecord:
    id: str; hyperedge_ids: tuple[str, ...]; provenance: str; status: EpistemicStatus = EpistemicStatus.UNTESTED_HYPOTHESIS

@dataclass(frozen=True)
class ExperimentLink:
    id: str; hypothesis_id: str; experiment_id: str; provenance: str; status: EpistemicStatus = EpistemicStatus.UNTESTED_HYPOTHESIS

@dataclass(frozen=True)
class EvidenceLink:
    id: str; experiment_id: str; evidence_id: str; provenance: str; status: EpistemicStatus = EpistemicStatus.UNRESOLVED

@dataclass(frozen=True)
class HypergraphEdge:
    source: str; target: str; provenance: str; status: EpistemicStatus
