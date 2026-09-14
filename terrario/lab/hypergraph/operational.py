"""Typed operational hypergraph for Terrario's execution and observation plane.

This is deliberately distinct from the Theory Hypergraph: its members describe
runtime provenance and control boundaries, not scientific mechanisms or
evidence.  It is a stable schema from which views and cross-domain bindings can
be derived without promoting an execution result to an EvidenceGraph claim.
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum


SCHEMA_VERSION = "terrario.operational-hypergraph/v1"


class OperationalNodeType(StrEnum):
    HYPOTHESIS = "HYPOTHESIS"
    EXPERIMENT_DRAFT = "EXPERIMENT_DRAFT"
    PREREGISTRATION = "PREREGISTRATION"
    EXECUTION_PLAN = "EXECUTION_PLAN"
    TRIAL_INTENT = "TRIAL_INTENT"
    TRIAL_ATTEMPT = "TRIAL_ATTEMPT"
    SCENARIO = "SCENARIO"
    WORLD = "WORLD"
    AGENT_CONFIGURATION = "AGENT_CONFIGURATION"
    SEED_PARTITION = "SEED_PARTITION"
    OBSERVER_PROFILE = "OBSERVER_PROFILE"
    SCIENTIFIC_OBSERVER = "SCIENTIFIC_OBSERVER"
    WORLD_TRUTH = "WORLD_TRUTH"
    AGENT_OBSERVATION = "AGENT_OBSERVATION"
    SCIENTIFIC_FRAME = "SCIENTIFIC_FRAME"
    RAW_TRACE = "RAW_TRACE"
    RAW_RESULT = "RAW_RESULT"
    CAS_BLOB = "CAS_BLOB"
    PLAYBACK = "PLAYBACK"
    CAUSAL_SNAPSHOT = "CAUSAL_SNAPSHOT"
    CAUSAL_FORK = "CAUSAL_FORK"
    FORK_BRANCH = "FORK_BRANCH"
    INTERVENTION_SPEC = "INTERVENTION_SPEC"
    CAUSAL_DIFF = "CAUSAL_DIFF"


@dataclass(frozen=True)
class OperationalHyperedgeMember:
    role: str
    node_type: OperationalNodeType
    cardinality: str = "ONE"
    causal: bool = True


@dataclass(frozen=True)
class OperationalHyperedge:
    """An n-ary contract; never flatten this to independent binary claims."""
    edge_id: str
    label: str
    members: tuple[OperationalHyperedgeMember, ...]
    output: OperationalNodeType
    semantics: str
    output_classification: str
    forbidden_outputs: tuple[str, ...] = ("EVIDENCE_GRAPH",)
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        object.__setattr__(self, "members", tuple(self.members))
        if len(self.members) < 2:
            raise ValueError("operational hyperedge requires at least two members")
        roles = tuple(item.role for item in self.members)
        if len(set(roles)) != len(roles) or not all(roles):
            raise ValueError("operational hyperedge member roles must be unique and non-empty")
        if self.output.value in self.forbidden_outputs:
            raise ValueError("operational hypergraph cannot emit EvidenceGraph")

    @property
    def causal_members(self) -> tuple[OperationalHyperedgeMember, ...]:
        return tuple(member for member in self.members if member.causal)


def _member(role: str, node: OperationalNodeType, *, cardinality: str = "ONE", causal: bool = True) -> OperationalHyperedgeMember:
    return OperationalHyperedgeMember(role, node, cardinality, causal)


OPERATIONAL_HYPEREDGES: tuple[OperationalHyperedge, ...] = (
    OperationalHyperedge(
        "OHG-01", "Diseño preregistrable", (
            _member("hypothesis", OperationalNodeType.HYPOTHESIS),
            _member("experiment_draft", OperationalNodeType.EXPERIMENT_DRAFT),
            _member("scenario", OperationalNodeType.SCENARIO),
            _member("world", OperationalNodeType.WORLD),
            _member("observer_profile", OperationalNodeType.OBSERVER_PROFILE),
            _member("seed_partition", OperationalNodeType.SEED_PARTITION),
        ), OperationalNodeType.PREREGISTRATION,
        "Locks one executable design and its observational contract; it does not execute it.",
        "SCIENTIFIC_DESIGN",
    ),
    OperationalHyperedge(
        "OHG-02", "Materialización de intento científico", (
            _member("preregistration", OperationalNodeType.PREREGISTRATION),
            _member("execution_plan", OperationalNodeType.EXECUTION_PLAN),
            _member("trial_intent", OperationalNodeType.TRIAL_INTENT),
            _member("scenario", OperationalNodeType.SCENARIO),
            _member("agent_configuration", OperationalNodeType.AGENT_CONFIGURATION),
            _member("seed_partition", OperationalNodeType.SEED_PARTITION),
            _member("observer_profile", OperationalNodeType.OBSERVER_PROFILE),
        ), OperationalNodeType.TRIAL_ATTEMPT,
        "Materializes one strongly identified attempt through the real runtime.",
        "SCIENTIFIC_EXECUTION",
    ),
    OperationalHyperedge(
        "OHG-03", "Frame científico atómico", (
            _member("trial_attempt", OperationalNodeType.TRIAL_ATTEMPT),
            _member("world_truth", OperationalNodeType.WORLD_TRUTH),
            _member("agent_observation", OperationalNodeType.AGENT_OBSERVATION),
            _member("scientific_observer", OperationalNodeType.SCIENTIFIC_OBSERVER),
            _member("tick", OperationalNodeType.TRIAL_ATTEMPT, causal=False),
        ), OperationalNodeType.SCIENTIFIC_FRAME,
        "Binds World Truth, Agent Observation and Observer View from one tick; observer view is observational, not an agent input.",
        "OBSERVATIONAL",
    ),
    OperationalHyperedge(
        "OHG-04", "Sellado de artefacto crudo", (
            _member("trial_attempt", OperationalNodeType.TRIAL_ATTEMPT),
            _member("scientific_frames", OperationalNodeType.SCIENTIFIC_FRAME, cardinality="ONE_OR_MORE", causal=False),
            _member("raw_trace", OperationalNodeType.RAW_TRACE, causal=False),
            _member("raw_result", OperationalNodeType.RAW_RESULT, causal=False),
        ), OperationalNodeType.CAS_BLOB,
        "Seals raw trace/result bytes with their attempt identity. A sealed raw artifact is not EvidenceGraph evidence.",
        "RAW_ARTIFACT",
    ),
    OperationalHyperedge(
        "OHG-05", "Playback verificable", (
            _member("trial_attempt", OperationalNodeType.TRIAL_ATTEMPT),
            _member("sealed_trace", OperationalNodeType.CAS_BLOB, causal=False),
            _member("observer_profile", OperationalNodeType.OBSERVER_PROFILE, causal=False),
        ), OperationalNodeType.PLAYBACK,
        "Reconstructs a read-only playback from a sealed trace; it never re-executes the world.",
        "DERIVED_READ_MODEL",
    ),
    OperationalHyperedge(
        "OHG-06", "Fork causal pareado", (
            _member("parent_attempt", OperationalNodeType.TRIAL_ATTEMPT),
            _member("causal_snapshot", OperationalNodeType.CAUSAL_SNAPSHOT),
            _member("control_branch", OperationalNodeType.FORK_BRANCH),
            _member("intervention_branch", OperationalNodeType.FORK_BRANCH),
            _member("intervention_spec", OperationalNodeType.INTERVENTION_SPEC),
        ), OperationalNodeType.CAUSAL_FORK,
        "Requires one exact snapshot and shared history before the intervention boundary; same seed alone is insufficient.",
        "CAUSAL_EXECUTION",
    ),
    OperationalHyperedge(
        "OHG-07", "Comparación causal descriptiva", (
            _member("causal_fork", OperationalNodeType.CAUSAL_FORK),
            _member("control_trace", OperationalNodeType.CAS_BLOB, causal=False),
            _member("intervention_trace", OperationalNodeType.CAS_BLOB, causal=False),
        ), OperationalNodeType.CAUSAL_DIFF,
        "Computes paired deltas and first divergence. It is descriptive and does not generate a causal conclusion.",
        "DERIVED_ANALYSIS",
    ),
)


def operational_hypergraph() -> tuple[OperationalHyperedge, ...]:
    """Return the immutable, complete operational relation catalogue."""
    return OPERATIONAL_HYPEREDGES


def hyperedges_for(node_type: OperationalNodeType) -> tuple[OperationalHyperedge, ...]:
    return tuple(edge for edge in OPERATIONAL_HYPEREDGES
                 if edge.output is node_type or any(member.node_type is node_type for member in edge.members))
