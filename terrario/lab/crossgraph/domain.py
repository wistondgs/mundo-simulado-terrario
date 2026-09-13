"""Federated scientific cross-graph contracts.

CrossGraph connects independent scientific domains without fusing them. It owns
only cross-domain identities, mappings, links, link provenance, federation
snapshots, traversal indexes, derived projections, and audit history. It never
copies an authoritative entity out of its sovereign store, never modifies a
historical graph, never decides which theory is correct, and never executes a
trial. A cross-link references an exact version/snapshot/hash; it is never a
"latest" pointer in saved scientific state.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from types import MappingProxyType
from typing import Any, Mapping

from terrario.lab.persistence.canonical import content_hash, plain

SCHEMA_VERSION = "terrario.lab.cross-graph/v1"
SNAPSHOT_SCHEMA_VERSION = "terrario.lab.cross-graph-snapshot/v1"
CANONICALIZATION_PROFILE = "terrario-canonical-json-v1"


class Domain(StrEnum):
    REFERENCE = "REFERENCE"
    CORPUS = "CORPUS"
    CLAIM = "CLAIM"
    ONTOLOGY = "ONTOLOGY"
    THEORY = "THEORY"
    HYPERGRAPH = "HYPERGRAPH"
    HYPOTHESIS = "HYPOTHESIS"
    WORLD = "WORLD"
    SCENARIO = "SCENARIO"
    EXPERIMENT = "EXPERIMENT"
    PREREGISTRATION = "PREREGISTRATION"
    EVIDENCE = "EVIDENCE"


class AssertionClass(StrEnum):
    SOURCE_EXPLICIT = "SOURCE_EXPLICIT"
    USER_ASSERTED = "USER_ASSERTED"
    ANALYST_ASSERTED = "ANALYST_ASSERTED"
    SYSTEM_DERIVED = "SYSTEM_DERIVED"
    MACHINE_CANDIDATE = "MACHINE_CANDIDATE"
    IMPORTED = "IMPORTED"
    LEGACY_MAPPING = "LEGACY_MAPPING"


class LinkState(StrEnum):
    CANDIDATE = "CANDIDATE"
    ACTIVE = "ACTIVE"
    REJECTED = "REJECTED"
    SUPERSEDED = "SUPERSEDED"
    RETRACTED = "RETRACTED"
    STALE_ENDPOINT = "STALE_ENDPOINT"
    UNRESOLVED = "UNRESOLVED"


class EndpointStatus(StrEnum):
    RESOLVED = "RESOLVED"
    DANGLING = "DANGLING"
    STALE_VERSION = "STALE_VERSION"
    STORE_UNAVAILABLE = "STORE_UNAVAILABLE"
    HASH_MISMATCH = "HASH_MISMATCH"


class ConsistencyClass(StrEnum):
    INTEGRITY_FAILURE = "INTEGRITY_FAILURE"
    STALE_REFERENCE = "STALE_REFERENCE"
    DOMAIN_UNAVAILABLE = "DOMAIN_UNAVAILABLE"
    SCIENTIFIC_WARNING = "SCIENTIFIC_WARNING"
    UNREVIEWED_CANDIDATE = "UNREVIEWED_CANDIDATE"
    HISTORICAL_REFERENCE = "HISTORICAL_REFERENCE"
    NOT_APPLICABLE = "NOT_APPLICABLE"


class QueryMode(StrEnum):
    EXPLORATORY_LATEST = "EXPLORATORY_LATEST"
    PINNED_REPRODUCIBLE = "PINNED_REPRODUCIBLE"


class PathKind(StrEnum):
    GRAPH_PATH = "GRAPH_PATH"
    PROVENANCE_PATH = "PROVENANCE_PATH"
    SCIENTIFIC_TRACE = "SCIENTIFIC_TRACE"
    DEPENDENCY_PATH = "DEPENDENCY_PATH"


class CrossGraphError(RuntimeError):
    code = "CROSS_GRAPH_ERROR"


class CrossGraphNotFound(CrossGraphError):
    code = "CROSS_GRAPH_NOT_FOUND"


class CrossGraphConflict(CrossGraphError):
    code = "CROSS_GRAPH_CONFLICT"


class CrossGraphIntegrityError(CrossGraphError):
    code = "CROSS_GRAPH_INTEGRITY_ERROR"


class UnresolvableEndpoint(CrossGraphError):
    code = "UNRESOLVABLE_ENDPOINT"


def frozen_mapping(value: Mapping[str, Any] | None) -> Mapping[str, Any]:
    return MappingProxyType(dict(value or {}))


@dataclass(frozen=True)
class CrossDomainEntityRef:
    """A strong, pinnable reference to an entity in a sovereign domain.

    Not every field is mandatory for every domain, but a reproducible
    scientific reference can pin the exact version/snapshot/hash.
    """
    domain: Domain
    entity_type: str
    entity_id: str
    version_id: str | None = None
    snapshot_id: str | None = None
    content_hash: str | None = None
    schema_version: str | None = None

    def __post_init__(self) -> None:
        if not self.entity_id:
            raise ValueError("entity_id is required")

    @property
    def ref_hash(self) -> str:
        return content_hash(plain(self))

    def key(self) -> str:
        return f"{self.domain.value}:{self.entity_type}:{self.entity_id}"


@dataclass(frozen=True)
class RelationSemantics:
    """Versioned semantics for a relation type; never a loose string."""
    relation_type: str
    source_domain_constraint: tuple[str, ...]
    target_domain_constraint: tuple[str, ...]
    directionality: str
    inverse_relation: str | None
    transitive: bool
    symmetric: bool
    scientific_meaning: str
    allowed_provenance_classes: tuple[str, ...]
    acyclic: bool
    registry_version: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_domain_constraint", tuple(self.source_domain_constraint))
        object.__setattr__(self, "target_domain_constraint", tuple(self.target_domain_constraint))
        object.__setattr__(self, "allowed_provenance_classes", tuple(self.allowed_provenance_classes))


@dataclass(frozen=True)
class CrossDomainLink:
    link_id: str
    source_ref: CrossDomainEntityRef
    target_ref: CrossDomainEntityRef
    relation_type: str
    assertion_class: AssertionClass
    state: LinkState
    provenance: str
    created_at: str
    created_by: str
    rule_id: str | None = None
    rule_version: str | None = None
    supersedes_link_id: str | None = None
    effective_at: str | None = None

    def __post_init__(self) -> None:
        if self.assertion_class is AssertionClass.MACHINE_CANDIDATE and self.state is LinkState.ACTIVE:
            raise ValueError("MACHINE_CANDIDATE can never be ACTIVE without human review")

    @property
    def link_hash(self) -> str:
        return content_hash(plain(self))


@dataclass(frozen=True)
class HyperlinkMember:
    ref: CrossDomainEntityRef
    role: str


@dataclass(frozen=True)
class CrossDomainHyperlink:
    hyperlink_id: str
    members: tuple[HyperlinkMember, ...]
    relation_type: str
    assertion_class: AssertionClass
    state: LinkState
    provenance: str
    created_at: str
    created_by: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "members", tuple(self.members))
        if len(self.members) < 2:
            raise ValueError("a hyperlink requires at least two members")

    @property
    def link_hash(self) -> str:
        return content_hash(plain(self))


@dataclass(frozen=True)
class FederationManifest:
    """Pins the exact snapshot combination of every federated domain."""
    manifest_id: str
    domain_snapshots: Mapping[str, str]
    schema_version: str
    created_at: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "domain_snapshots", frozen_mapping(self.domain_snapshots))

    @property
    def manifest_hash(self) -> str:
        return content_hash(plain(self))


@dataclass(frozen=True)
class CrossGraphSnapshot:
    snapshot_id: str
    parent_snapshot_id: str | None
    federation_manifest_hash: str
    cross_link_set_hash: str
    root_hash: str
    link_count: int
    hyperlink_count: int
    created_at: str
    actor: str
    provenance: str


@dataclass(frozen=True)
class TraceBreak:
    trace_break_id: str
    from_ref: CrossDomainEntityRef
    expected_next_domain: str
    reason: str
    missing_identity_or_relation: str
    discovered_at: str
    resolution_state: str = "UNRESOLVED"


@dataclass(frozen=True)
class ResearchComposition:
    composition_id: str
    title: str
    refs: tuple[CrossDomainEntityRef, ...]
    local_links: tuple[Mapping[str, Any], ...]
    notes: str
    version: int
    parent_composition_id: str | None
    created_at: str
    created_by: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "refs", tuple(self.refs))
        object.__setattr__(self, "local_links",
                         tuple(frozen_mapping(x) for x in self.local_links))
