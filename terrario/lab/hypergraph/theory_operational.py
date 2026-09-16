"""Fail-closed operational representation for source-backed theory hyperedges.

This is deliberately separate from execution-plane hypergraphs.  It never turns
an imported candidate into a causal claim and it never infers a role from a
component list.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import csv
import hashlib
from pathlib import Path
from typing import Iterable, Mapping

from terrario.lab.models import EpistemicStatus
from terrario.lab.persistence.canonical import canonical_json, content_hash
from terrario.lab.theory.ingestion import TheoryImport
from terrario.lab.theory.models import HyperedgeCandidateRecord

ROLE_SCHEMA = "terrario.theory.hyperedge-role/v1"
PAYLOAD_SCHEMA = "terrario.theory.operational-hyperedge/v1"
APPROVED_CANDIDATES = frozenset({"HYPERCAND-02", "HYPERCAND-08"})
SOURCE_BACKED = "SOURCE_BACKED"
DERIVED = "DERIVED"


@dataclass(frozen=True)
class TheoryHyperedgeBinding:
    candidate_id: str
    participant: str
    role: str
    role_schema_version: str
    cardinality: str
    claim_id: str
    claim_artifact: str
    claim_version: str
    source_record_id: str
    source_artifact: str
    source_version: str
    source_locator: str
    binding_basis: str

    def __post_init__(self) -> None:
        required = (self.candidate_id, self.participant, self.role, self.claim_id,
                    self.claim_artifact, self.claim_version, self.source_record_id,
                    self.source_artifact, self.source_version, self.source_locator)
        if not all(required):
            raise ValueError("hyperedge binding requires a complete provenance locator")
        if self.role_schema_version != ROLE_SCHEMA:
            raise ValueError("unsupported role schema")
        if self.cardinality != "ONE":
            raise ValueError("unsupported role cardinality")
        if self.binding_basis != "SOURCE_EXPLICIT" and not self.binding_basis.startswith((
            "EDITORIAL_NORMALIZATION:", "SOURCE_EXPLICIT_NORMALIZATION:",
        )):
            raise ValueError("role binding basis is not source-backed")


@dataclass(frozen=True)
class BindingRequirement:
    """A conjunctive query condition for one role/player pair."""

    participant: str
    role: str

    def __post_init__(self) -> None:
        if not self.participant or not self.role:
            raise ValueError("joint query requirements require participant and role")


@dataclass(frozen=True)
class RoleCompatibility:
    """An explicit semantic bridge, never an inferred ID intersection."""

    left: BindingRequirement
    right: BindingRequirement
    rationale: str

    def __post_init__(self) -> None:
        if not self.rationale:
            raise ValueError("semantic composition requires an explicit rationale")


@dataclass(frozen=True)
class CompositionRule:
    """A versioned, inspectable rule for a derived structural relation."""

    rule_id: str
    version: str
    conclusion: str

    def __post_init__(self) -> None:
        if not all((self.rule_id, self.version, self.conclusion)):
            raise ValueError("composition rule requires id, version, and conclusion")

    @property
    def identity(self) -> str:
        return f"{self.rule_id}@{self.version}"


@dataclass(frozen=True)
class TheoryOperationalHyperedge:
    candidate_id: str
    bindings: tuple[TheoryHyperedgeBinding, ...]
    provenance: str
    epistemic_status: EpistemicStatus
    relation_type: str = "TESTABLE_CONJUNCTION"
    origin: str = SOURCE_BACKED
    parent_semantic_ids: tuple[str, ...] = ()
    composition_rule: str | None = None
    corroboration_status: str = "NOT_CLAIMED"

    def __post_init__(self) -> None:
        if self.origin not in {SOURCE_BACKED, DERIVED}:
            raise ValueError("unknown hyperedge origin")
        if self.origin == SOURCE_BACKED and self.parent_semantic_ids:
            raise ValueError("source-backed hyperedges cannot have derived parents")
        if self.origin == SOURCE_BACKED and self.composition_rule is not None:
            raise ValueError("source-backed hyperedges cannot have a composition rule")
        if self.origin == DERIVED and len(self.parent_semantic_ids) < 2:
            raise ValueError("derived hyperedges require at least two parents")
        if self.origin == DERIVED and self.composition_rule is None:
            raise ValueError("derived hyperedges require a versioned composition rule")
        if len({(item.participant, item.role) for item in self.bindings}) != len(self.bindings):
            raise ValueError("duplicate participant/role binding")

    @property
    def semantic_id(self) -> str:
        return "THEORY-HYPEREDGE-" + content_hash(self._semantic_payload())[:16]

    def _semantic_payload(self) -> dict:
        # Corpus records historically use a repository-relative snapshot path.
        # An absolute mount prefix is deployment detail, not hyperedge semantics.
        provenance = self.provenance
        marker = "theory_snapshots/"
        if marker in provenance:
            provenance = provenance[provenance.index(marker):]
        payload = {
            "candidate_id": self.candidate_id,
            "bindings": sorted((asdict(item) for item in self.bindings), key=canonical_json),
            "epistemic_status": self.epistemic_status.value,
            "origin": self.origin,
            "parent_semantic_ids": sorted(self.parent_semantic_ids),
            "provenance": provenance,
            "relation_type": self.relation_type,
        }
        if self.origin == DERIVED:
            payload["composition_rule"] = self.composition_rule
            payload["corroboration_status"] = self.corroboration_status
        return payload

    def payload(self) -> dict:
        return {"schema": PAYLOAD_SCHEMA, **self._semantic_payload(), "semantic_id": self.semantic_id}

    @classmethod
    def from_payload(cls, payload: Mapping) -> "TheoryOperationalHyperedge":
        if payload.get("schema") != PAYLOAD_SCHEMA:
            raise ValueError("unsupported hyperedge payload schema")
        try:
            edge = cls(
                candidate_id=payload["candidate_id"],
                bindings=tuple(TheoryHyperedgeBinding(**item) for item in payload["bindings"]),
                provenance=payload["provenance"],
                epistemic_status=EpistemicStatus(payload["epistemic_status"]),
                relation_type=payload["relation_type"], origin=payload["origin"],
                parent_semantic_ids=tuple(payload["parent_semantic_ids"]),
                composition_rule=payload.get("composition_rule"),
                corroboration_status=payload.get("corroboration_status", "NOT_CLAIMED"),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError("invalid hyperedge payload") from exc
        if payload.get("semantic_id") != edge.semantic_id:
            raise ValueError("semantic identity mismatch after deserialization")
        return edge

    def has_requirement(self, requirement: BindingRequirement) -> bool:
        return any(binding.participant == requirement.participant and binding.role == requirement.role
                   for binding in self.bindings)


def _indexed(records: Iterable) -> dict[str, object]:
    return {record.id: record for record in records}


def validate_bindings(candidate: HyperedgeCandidateRecord, bindings: Iterable[TheoryHyperedgeBinding], imported: TheoryImport, *, primary_source_root: str | Path | None = None) -> tuple[TheoryHyperedgeBinding, ...]:
    """Resolve every role binding through imported claim and source records."""
    bound = tuple(bindings)
    claims = _indexed(imported.claims)
    for binding in bound:
        if binding.candidate_id != candidate.id:
            raise ValueError("binding candidate does not match materialization target")
        claim = claims.get(binding.claim_id)
        source = next((item for item in imported.sources if item.id == binding.source_record_id
                       and (item.source_artifact, item.source_version) == (binding.source_artifact, binding.source_version)), None)
        if claim is None or source is None:
            raise ValueError("binding provenance cannot be resolved")
        if not source.valid_evidence_source:
            raise ValueError("binding source is not valid evidence")
        if (claim.source_artifact, claim.source_version) != (binding.claim_artifact, binding.claim_version):
            raise ValueError("binding claim revision mismatch")
        if (source.source_artifact, source.source_version) != (binding.source_artifact, binding.source_version):
            raise ValueError("binding source revision mismatch")
        if claim.fields.get("pagina_seccion", claim.fields.get("source_locator")) != binding.source_locator:
            raise ValueError("binding source locator mismatch")
        if claim.source_id != binding.source_record_id and f"[{binding.source_record_id}]" not in claim.source_id:
            raise ValueError("claim does not resolve to declared source record")
        if source.source_version.startswith("sha256:"):
            if primary_source_root is None:
                raise ValueError("primary source root is required for hash-addressed evidence")
            source_path = Path(primary_source_root) / source.fields["corpus_relative_path"]
            if not source_path.is_file() or hashlib.sha256(source_path.read_bytes()).hexdigest() != source.source_version.removeprefix("sha256:"):
                raise ValueError("primary source artifact is unavailable or has a hash mismatch")
    return bound


def materialize(candidate: HyperedgeCandidateRecord, bindings: Iterable[TheoryHyperedgeBinding], imported: TheoryImport, *, primary_source_root: str | Path | None = None) -> TheoryOperationalHyperedge:
    """Create a real n-ary relation only for an explicitly approved candidate."""
    if candidate.id not in APPROVED_CANDIDATES:
        raise ValueError("candidate is NOT_MATERIALIZABLE without approved role bindings")
    if candidate.epistemic_status is not EpistemicStatus.TESTABLE_CONJUNCTION:
        raise ValueError("materialization cannot promote epistemic status")
    bound = validate_bindings(candidate, bindings, imported, primary_source_root=primary_source_root)
    if len(bound) < 3 or len(bound) != len(candidate.components):
        raise ValueError("n-ary materialization requires exactly one binding per component")
    if {item.participant for item in bound} != set(candidate.components):
        raise ValueError("bindings must cover every candidate component exactly")
    if len({item.role for item in bound}) != len(bound):
        raise ValueError("duplicate role binding")
    return TheoryOperationalHyperedge(candidate.id, bound, candidate.provenance, candidate.epistemic_status)


def query(edges: Iterable[TheoryOperationalHyperedge], *, requirements: Iterable[BindingRequirement] = (), status: EpistemicStatus | None = None, provenance: str | None = None) -> tuple[TheoryOperationalHyperedge, ...]:
    """Return edges satisfying every player/role condition and all metadata filters."""
    required = tuple(requirements)
    if len(set(required)) != len(required):
        raise ValueError("duplicate joint query requirement")
    return tuple(edge for edge in edges
                 if (status is None or edge.epistemic_status is status)
                 and (provenance is None or provenance in edge.provenance)
                 and all(edge.has_requirement(item) for item in required))


def compose(left: TheoryOperationalHyperedge, right: TheoryOperationalHyperedge, *, compatibility: Iterable[RoleCompatibility], rule: CompositionRule, provenance: str) -> TheoryOperationalHyperedge:
    """Derive only from two distinct edges with declared role semantics."""
    bridges = tuple(compatibility)
    if left.semantic_id == right.semantic_id:
        raise ValueError("cannot compose an edge with itself")
    if not bridges or not provenance:
        raise ValueError("semantic composition requires explicit role compatibility and provenance")
    if left.epistemic_status is not right.epistemic_status:
        raise ValueError("epistemically incompatible hyperedges cannot compose")
    for bridge in bridges:
        if not left.has_requirement(bridge.left) or not right.has_requirement(bridge.right):
            raise ValueError("NO_COMPOSITION: declared roles are not semantically compatible")
    merged: dict[tuple[str, str], TheoryHyperedgeBinding] = {}
    for binding in (*left.bindings, *right.bindings):
        key = (binding.participant, binding.role)
        current = merged.get(key)
        if current is not None:
            current_payload = asdict(current); current_payload.pop("candidate_id")
            binding_payload = asdict(binding); binding_payload.pop("candidate_id")
            if current_payload != binding_payload:
                raise ValueError("NO_COMPOSITION: compatible roles have conflicting source semantics")
            continue
        merged[key] = binding
    bindings = tuple(sorted(merged.values(), key=canonical_json))
    return TheoryOperationalHyperedge(
        candidate_id="DERIVED:" + "+".join(sorted((left.candidate_id, right.candidate_id))),
        bindings=bindings, provenance=provenance, epistemic_status=left.epistemic_status,
        relation_type="SEMANTIC_ROLE_COMPOSITION", origin=DERIVED,
        parent_semantic_ids=tuple(sorted((left.semantic_id, right.semantic_id))),
        composition_rule=rule.identity,
        corroboration_status="STRUCTURAL_COMPOSITION_NOT_CORROBORATION",
    )


def provenance_forward(edge: TheoryOperationalHyperedge, edges_by_semantic_id: Mapping[str, TheoryOperationalHyperedge]) -> tuple[TheoryHyperedgeBinding, ...]:
    """Resolve an edge to leaf claim/source bindings, including derived parents."""
    if edge.origin == SOURCE_BACKED:
        return edge.bindings
    leaves: list[TheoryHyperedgeBinding] = []
    for parent_id in edge.parent_semantic_ids:
        parent = edges_by_semantic_id.get(parent_id)
        if parent is None:
            raise ValueError("derived hyperedge parent is unavailable")
        leaves.extend(provenance_forward(parent, edges_by_semantic_id))
    return tuple(sorted(set(leaves), key=canonical_json))


def provenance_reverse(claim_id: str, edges: Iterable[TheoryOperationalHyperedge], edges_by_semantic_id: Mapping[str, TheoryOperationalHyperedge]) -> tuple[TheoryOperationalHyperedge, ...]:
    """Find source-backed or derived edges reachable from a source claim."""
    return tuple(edge for edge in edges
                 if any(binding.claim_id == claim_id for binding in provenance_forward(edge, edges_by_semantic_id)))


def load_bindings(path: str | Path, candidate_id: str) -> tuple[TheoryHyperedgeBinding, ...]:
    with Path(path).open(encoding="utf-8", newline="") as stream:
        rows = [row for row in csv.DictReader(stream) if row.get("candidate_id") == candidate_id]
    return tuple(TheoryHyperedgeBinding(**{key: row[key] for key in TheoryHyperedgeBinding.__dataclass_fields__}) for row in rows)
