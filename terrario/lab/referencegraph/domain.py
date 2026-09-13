"""Typed scientific reference-graph contracts.

These contracts describe documents, bibliographic works, source claims and
their provenance only. Nothing in this module can write the TheoryGraph, write
the EvidenceGraph, create a hypothesis, create an ExperimentDraft, preregister,
or execute a trial. A reference is never evidence; a citation is never support;
a source claim is never one of our claims.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping

from terrario.lab.persistence.canonical import content_hash, plain

SCHEMA_VERSION = "terrario.lab.reference-graph/v1"
CANONICALIZATION_PROFILE = "terrario-canonical-json-v1"
SNAPSHOT_SCHEMA_VERSION = "terrario.lab.reference-graph-snapshot/v1"


class DocumentVersionType(StrEnum):
    PUBLISHED_VERSION = "PUBLISHED_VERSION"
    AUTHOR_ACCEPTED_MANUSCRIPT = "AUTHOR_ACCEPTED_MANUSCRIPT"
    PREPRINT = "PREPRINT"
    TECHNICAL_REPORT = "TECHNICAL_REPORT"
    THESIS_VERSION = "THESIS_VERSION"
    SUPPLEMENT = "SUPPLEMENT"
    CORRECTION = "CORRECTION"
    RETRACTION_NOTICE = "RETRACTION_NOTICE"
    UNKNOWN_VERSION = "UNKNOWN_VERSION"


class DocumentStatus(StrEnum):
    ACTIVE = "ACTIVE"
    CORRECTED = "CORRECTED"
    RETRACTED = "RETRACTED"
    EXPRESSION_OF_CONCERN = "EXPRESSION_OF_CONCERN"
    UNKNOWN = "UNKNOWN"


class ClaimType(StrEnum):
    SOURCE_TEXT = "SOURCE_TEXT"
    SOURCE_REPORTED_CLAIM = "SOURCE_REPORTED_CLAIM"
    ANALYST_INTERPRETATION = "ANALYST_INTERPRETATION"
    MACHINE_EXTRACTION_UNVERIFIED = "MACHINE_EXTRACTION_UNVERIFIED"
    USER_NOTE = "USER_NOTE"


class ProvenanceLevel(StrEnum):
    SOURCE_EXPLICIT = "SOURCE_EXPLICIT"
    SOURCE_DERIVED = "SOURCE_DERIVED"
    ANALYST_INFERRED = "ANALYST_INFERRED"
    MACHINE_EXTRACTED_UNVERIFIED = "MACHINE_EXTRACTED_UNVERIFIED"
    USER_ASSERTED = "USER_ASSERTED"
    IMPORTED_METADATA = "IMPORTED_METADATA"
    UNKNOWN = "UNKNOWN"


class VerificationStatus(StrEnum):
    UNVERIFIED = "UNVERIFIED"
    VERIFIED = "VERIFIED"
    ACQUIRED = "ACQUIRED"
    NEEDS_REVIEW = "NEEDS_REVIEW"
    UNKNOWN = "UNKNOWN"


class NodeType(StrEnum):
    DOCUMENT = "DOCUMENT"
    REFERENCE = "REFERENCE"
    AUTHOR = "AUTHOR"
    VENUE = "VENUE"
    SOURCE_CLAIM = "SOURCE_CLAIM"
    CONSTRUCT = "CONSTRUCT"
    PARADIGM = "PARADIGM"
    PROTOCOL = "PROTOCOL"
    METHOD = "METHOD"
    METRIC = "METRIC"
    DATASET = "DATASET"
    BENCHMARK = "BENCHMARK"
    ENVIRONMENT = "ENVIRONMENT"
    LIMITATION = "LIMITATION"
    REPLICATION = "REPLICATION"
    CRITIQUE = "CRITIQUE"
    DESIGN_PRINCIPLE = "DESIGN_PRINCIPLE"


class EdgeType(StrEnum):
    AUTHORED_BY = "AUTHORED_BY"
    PUBLISHED_IN = "PUBLISHED_IN"
    VERSION_OF = "VERSION_OF"
    CITES = "CITES"
    REPORTS_CLAIM = "REPORTS_CLAIM"
    STUDIES_CONSTRUCT = "STUDIES_CONSTRUCT"
    USES_PARADIGM = "USES_PARADIGM"
    IMPLEMENTS_PROTOCOL = "IMPLEMENTS_PROTOCOL"
    USES_METHOD = "USES_METHOD"
    USES_METRIC = "USES_METRIC"
    USES_DATASET = "USES_DATASET"
    EVALUATES_ENVIRONMENT = "EVALUATES_ENVIRONMENT"
    REPORTS_LIMITATION = "REPORTS_LIMITATION"
    REPLICATES = "REPLICATES"
    CRITIQUES = "CRITIQUES"
    EXTENDS = "EXTENDS"
    SUPPLEMENTS = "SUPPLEMENTS"
    CORRECTS = "CORRECTS"
    METHODOLOGICAL_INSPIRATION = "METHODOLOGICAL_INSPIRATION"
    TECHNICAL_REFERENCE = "TECHNICAL_REFERENCE"
    DIRECT_PARADIGM_ADAPTATION = "DIRECT_PARADIGM_ADAPTATION"
    FUTURE_REFERENCE = "FUTURE_REFERENCE"


class DuplicateStatus(StrEnum):
    MERGE_CANDIDATE = "MERGE_CANDIDATE"
    CONFIRMED_DUPLICATE = "CONFIRMED_DUPLICATE"
    DISTINCT_VERSION = "DISTINCT_VERSION"
    DISTINCT_WORK = "DISTINCT_WORK"
    UNRESOLVED = "UNRESOLVED"


class RelevanceKind(StrEnum):
    PRIMARY_RELEVANCE = "PRIMARY_RELEVANCE"
    SECONDARY_RELEVANCE = "SECONDARY_RELEVANCE"
    TRANSITION_REFERENCE = "TRANSITION_REFERENCE"
    CONTROL_REFERENCE = "CONTROL_REFERENCE"


class ConflictKind(StrEnum):
    CONTRADICTORY_REPORTS = "CONTRADICTORY_REPORTS"
    METHODOLOGICAL_DISAGREEMENT = "METHODOLOGICAL_DISAGREEMENT"
    UNRESOLVED_CONFLICT = "UNRESOLVED_CONFLICT"


class QuarantineReason(StrEnum):
    MISSING_FILE = "MISSING_FILE"
    HASH_MISMATCH = "HASH_MISMATCH"
    HTML_DISGUISED_AS_PDF = "HTML_DISGUISED_AS_PDF"
    ZERO_BYTE_DOCUMENT = "ZERO_BYTE_DOCUMENT"
    CONFLICTING_DOI_IDENTITY = "CONFLICTING_DOI_IDENTITY"
    MALFORMED_METADATA = "MALFORMED_METADATA"
    INCOMPATIBLE_SCHEMA = "INCOMPATIBLE_SCHEMA"
    INCOMPATIBLE_DUPLICATE = "INCOMPATIBLE_DUPLICATE"


class ResolutionState(StrEnum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"
    DEFERRED = "DEFERRED"


class ImportAction(StrEnum):
    CREATE = "CREATE"
    UPDATE_AS_NEW_VERSION = "UPDATE_AS_NEW_VERSION"
    EXACT_DUPLICATE = "EXACT_DUPLICATE"
    CONFLICT = "CONFLICT"
    QUARANTINE = "QUARANTINE"


class ReferenceGraphError(RuntimeError):
    code = "REFERENCE_GRAPH_ERROR"


class ReferenceNotFound(ReferenceGraphError):
    code = "REFERENCE_NOT_FOUND"


class ReferenceConflict(ReferenceGraphError):
    code = "REFERENCE_CONFLICT"


class ReferenceIntegrityError(ReferenceGraphError):
    code = "REFERENCE_INTEGRITY_ERROR"


def frozen_mapping(value: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return MappingProxyType(dict(value or {}))


@dataclass(frozen=True)
class ClaimLocator:
    page: str | None = None
    section: str | None = None
    subsection: str | None = None
    figure: str | None = None
    table: str | None = None
    paragraph: str | None = None
    appendix: str | None = None
    supplement: str | None = None


@dataclass(frozen=True)
class DocumentRecord:
    """Identity of a concrete file: SHA-256 of its bytes (the CAS blob hash)."""
    document_id: str
    cas_blob_hash: str
    media_type: str
    size_bytes: int
    version_type: DocumentVersionType
    status: DocumentStatus
    recorded_at: str
    effective_at: str | None = None

    @property
    def content_hash(self) -> str:
        return content_hash(plain(self))


@dataclass(frozen=True)
class AuthorRecord:
    author_id: str
    display_name: str
    normalized_name: str
    recorded_at: str


@dataclass(frozen=True)
class VenueRecord:
    venue_id: str
    name: str
    normalized_name: str
    venue_type: str
    recorded_at: str


@dataclass(frozen=True)
class BibliographicRecord:
    """Identity of the work/publication, independent of any single file."""
    biblio_id: str
    title: str
    normalized_title: str
    authors: tuple[str, ...]
    year: str
    venue_id: str | None
    edition: str | None
    doi: str | None
    identity_hash: str
    recorded_at: str

    @staticmethod
    def compute_identity(doi: str | None, normalized_title: str,
                         authors: tuple[str, ...], year: str) -> str:
        if doi and doi != "UNKNOWN":
            return content_hash({"doi": doi.casefold()})
        return content_hash({"normalized_title": normalized_title,
                             "authors": list(authors), "year": year})


@dataclass(frozen=True)
class DocumentVersion:
    version_id: str
    document_id: str
    biblio_id: str
    version_type: DocumentVersionType
    relation: EdgeType | None
    relation_target_document_id: str | None
    recorded_at: str


@dataclass(frozen=True)
class ScientificReferenceRecord:
    """Terrario-internal record binding a work to its documents and tags."""
    reference_id: str
    biblio_id: str
    primary_document_id: str | None
    reference_type: str
    status: DocumentStatus
    d_level_tags: tuple[Mapping[str, Any], ...]
    constructs: tuple[str, ...]
    experimental_paradigms: tuple[str, ...]
    discipline: str
    code_url: str | None
    verification_status: VerificationStatus
    recorded_at: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "d_level_tags",
                           tuple(frozen_mapping(x) for x in self.d_level_tags))

    @property
    def content_hash(self) -> str:
        return content_hash(plain(self))


@dataclass(frozen=True)
class SourceClaimRecord:
    claim_id: str
    reference_id: str
    document_id: str | None
    claim_text: str
    normalized_summary: str
    claim_type: ClaimType
    epistemic_source: ProvenanceLevel
    extraction_method: str
    verification_status: VerificationStatus
    locator: ClaimLocator
    context: str
    recorded_at: str

    @property
    def content_hash(self) -> str:
        return content_hash(plain(self))


@dataclass(frozen=True)
class ProtocolRecord:
    protocol_id: str
    reference_id: str
    extraction_status: str
    subjects_or_agents: str
    sample_size: str
    stimulus: str
    environment: str
    manipulated_variables: str
    independent_variables: str
    dependent_variables: str
    controls: str
    measured_outcomes: str
    training_structure: str
    test_structure: str
    occlusion_structure: str
    delay_structure: str
    distractor_structure: str
    generalisation_structure: str
    statistical_method: str
    reported_effect: str
    authors_interpretation: str
    reported_limitations: str
    extraction_basis: str
    recorded_at: str


@dataclass(frozen=True)
class LimitationRecord:
    limitation_id: str
    reference_id: str
    limitation_type: str
    limitation: str
    source_basis: str
    notes: str
    recorded_at: str


@dataclass(frozen=True)
class DesignPrincipleRecord:
    principle_id: str
    reference_id: str
    source_basis: str
    principle: str
    terrario_possible_use: str
    adaptation_type: EdgeType
    limitations: str
    recorded_at: str


@dataclass(frozen=True)
class ReplicationRecord:
    replication_id: str
    original_reference_id: str
    replication_reference_id: str
    replication_kind: str
    methodological_deltas: str
    reported_result: str
    interpretation: str
    provenance: ProvenanceLevel
    recorded_at: str


@dataclass(frozen=True)
class CritiqueRecord:
    critique_id: str
    source_reference_id: str
    target_reference_id: str
    critique_kind: str
    substance: str
    provenance: ProvenanceLevel
    recorded_at: str


@dataclass(frozen=True)
class GraphNode:
    node_id: str
    node_type: NodeType
    reference_id: str | None
    payload: Mapping[str, Any]
    node_hash: str
    recorded_at: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", frozen_mapping(self.payload))


@dataclass(frozen=True)
class GraphEdge:
    edge_id: str
    edge_type: EdgeType
    source_node_id: str
    target_node_id: str
    provenance_level: ProvenanceLevel
    provenance_detail: str
    edge_hash: str
    recorded_at: str


@dataclass(frozen=True)
class ReferenceGraphSnapshot:
    snapshot_id: str
    parent_snapshot_id: str | None
    schema_version: str
    node_set_hash: str
    edge_set_hash: str
    root_hash: str
    node_count: int
    edge_count: int
    provenance: str
    created_at: str


@dataclass(frozen=True)
class ReferenceImportRecord:
    import_record_id: str
    batch_id: str
    external_id: str
    action: ImportAction
    detail: str
    recorded_at: str


@dataclass(frozen=True)
class ExtractionRecord:
    extraction_id: str
    document_id: str
    extraction_method: str
    extractor_version: str
    provenance: ProvenanceLevel
    payload: Mapping[str, Any]
    recorded_at: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "payload", frozen_mapping(self.payload))


@dataclass(frozen=True)
class VerificationRecord:
    verification_id: str
    subject_id: str
    report: Mapping[str, Any]
    recorded_at: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "report", frozen_mapping(self.report))
