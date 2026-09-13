"""Domain adapter contract and concrete adapters for the federated cross-graph.

Every sovereign domain exposes a common read interface. CrossGraph resolves
identity, version, snapshot, hash, neighbors, and provenance through these
adapters; it never writes through them. Adapters for historical domains
(TheoryGraph, Hypergraph, Hypothesis, EvidenceGraph) are strictly read-only.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Protocol

from terrario.lab.crossgraph.domain import CrossDomainEntityRef, Domain
from terrario.lab.persistence import ArtifactRepository


class DomainAdapter(Protocol):
    domain: Domain
    read_only: bool

    def exists(self, ref: CrossDomainEntityRef) -> bool: ...
    def resolve_entity(self, ref: CrossDomainEntityRef) -> Mapping[str, Any] | None: ...
    def verify_identity(self, ref: CrossDomainEntityRef) -> bool: ...
    def get_content_hash(self, ref: CrossDomainEntityRef) -> str | None: ...
    def get_snapshot(self) -> str | None: ...
    def get_provenance(self, ref: CrossDomainEntityRef) -> Mapping[str, Any]: ...
    def get_neighbors(self, ref: CrossDomainEntityRef) -> tuple[Mapping[str, Any], ...]: ...


class _ArtifactAdapter:
    """Shared base for domains stored as durable artifact versions."""

    read_only = True

    def __init__(self, artifacts: ArtifactRepository):
        self.artifacts = artifacts

    def _version(self, ref: CrossDomainEntityRef):
        from terrario.lab.persistence import ArtifactNotFound
        try:
            if ref.version_id:
                return self.artifacts.get_version(ref.version_id)
            return self.artifacts.current(ref.entity_id)
        except (ArtifactNotFound, Exception):
            return None

    def exists(self, ref: CrossDomainEntityRef) -> bool:
        return self._version(ref) is not None

    def resolve_entity(self, ref: CrossDomainEntityRef) -> Mapping[str, Any] | None:
        version = self._version(ref)
        if version is None:
            return None
        return {"version_id": version.version_id, "artifact_id": version.artifact_id,
                "kind": version.kind, "scientific_hash": version.scientific_hash,
                "payload": version.payload}

    def verify_identity(self, ref: CrossDomainEntityRef) -> bool:
        version = self._version(ref)
        if version is None:
            return False
        if ref.content_hash and version.scientific_hash != ref.content_hash:
            return False
        if ref.version_id and version.version_id != ref.version_id:
            return False
        return True

    def get_content_hash(self, ref: CrossDomainEntityRef) -> str | None:
        version = self._version(ref)
        return version.scientific_hash if version else None

    def get_snapshot(self) -> str | None:
        return None

    def get_provenance(self, ref: CrossDomainEntityRef) -> Mapping[str, Any]:
        version = self._version(ref)
        if version is None:
            return {}
        return {"artifact_id": version.artifact_id, "version_id": version.version_id,
                "created_by": version.created_by, "created_at": version.created_at,
                "classification": version.classification}

    def get_neighbors(self, ref: CrossDomainEntityRef) -> tuple[Mapping[str, Any], ...]:
        return ()


class ExperimentAdapter(_ArtifactAdapter):
    domain = Domain.EXPERIMENT


class PreregistrationAdapter(_ArtifactAdapter):
    domain = Domain.PREREGISTRATION


class ReferenceGraphAdapter:
    """Read access to the ScientificReferenceGraph domain."""

    domain = Domain.REFERENCE
    read_only = True

    def __init__(self, artifacts: ArtifactRepository):
        self.artifacts = artifacts

    def _service(self):
        from terrario.lab.referencegraph.service import ReferenceGraphService
        return ReferenceGraphService(self.artifacts)

    def exists(self, ref: CrossDomainEntityRef) -> bool:
        return self.resolve_entity(ref) is not None

    def resolve_entity(self, ref: CrossDomainEntityRef) -> Mapping[str, Any] | None:
        service = self._service()
        try:
            if ref.entity_type in {"ScientificReferenceRecord", "REFERENCE"}:
                return dict(service.get_reference(ref.entity_id))
            if ref.entity_type in {"DocumentRecord", "DOCUMENT"}:
                return service.repository.get_document(ref.entity_id)
            with self.artifacts._connect() as connection:
                row = connection.execute(
                    "SELECT * FROM ref_nodes WHERE node_id=?", (ref.entity_id,)).fetchone()
                return dict(row) if row else None
        except Exception:
            return None

    def verify_identity(self, ref: CrossDomainEntityRef) -> bool:
        entity = self.resolve_entity(ref)
        if entity is None:
            return False
        if ref.content_hash:
            return self.get_content_hash(ref) == ref.content_hash
        return True

    def get_content_hash(self, ref: CrossDomainEntityRef) -> str | None:
        entity = self.resolve_entity(ref)
        if entity is None:
            return None
        return entity.get("node_hash") or entity.get("cas_blob_hash") or entity.get("identity_hash")

    def get_snapshot(self) -> str | None:
        latest = self._service().repository.latest_snapshot()
        return str(latest["root_hash"]) if latest else None

    def get_provenance(self, ref: CrossDomainEntityRef) -> Mapping[str, Any]:
        try:
            from terrario.lab.referencegraph.queries import ReferenceGraphQueries
            return ReferenceGraphQueries(self.artifacts).get_provenance(ref.entity_id)
        except Exception:
            return {}

    def get_neighbors(self, ref: CrossDomainEntityRef) -> tuple[Mapping[str, Any], ...]:
        try:
            from terrario.lab.referencegraph.queries import ReferenceGraphQueries
            neighborhood = ReferenceGraphQueries(self.artifacts).get_neighborhood(ref.entity_id, depth=1)
            return tuple(neighborhood["nodes"])
        except Exception:
            return ()


class TheoryGraphAdapter:
    """Read-only access to the historical TheoryGraph (in-memory/JSON snapshot)."""

    domain = Domain.THEORY
    read_only = True

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self._store = None

    def _load(self):
        if self._store is None:
            from terrario.lab.theory.store import TheoryGraphStore
            graphs = sorted(self.root.glob("theory_snapshots/*/theory_graph.json"))
            self._store = TheoryGraphStore.load(graphs[-1]) if graphs else None
        return self._store

    def exists(self, ref: CrossDomainEntityRef) -> bool:
        return self.resolve_entity(ref) is not None

    def resolve_entity(self, ref: CrossDomainEntityRef) -> Mapping[str, Any] | None:
        store = self._load()
        if store is None:
            return None
        candidates = (ref.entity_id, f"{ref.entity_type}:{ref.entity_id}")
        for node_id in candidates:
            node = store.theory_nodes.get(node_id) or store.evidence_nodes.get(node_id)
            if node:
                return dict(node)
        return None

    def verify_identity(self, ref: CrossDomainEntityRef) -> bool:
        return self.resolve_entity(ref) is not None

    def get_content_hash(self, ref: CrossDomainEntityRef) -> str | None:
        return None

    def get_snapshot(self) -> str | None:
        store = self._load()
        return str(store.snapshot_id) if store else None

    def get_provenance(self, ref: CrossDomainEntityRef) -> Mapping[str, Any]:
        entity = self.resolve_entity(ref) or {}
        return {"provenance": entity.get("provenance"),
                "epistemic_status": entity.get("epistemic_status"),
                "source_artifact": entity.get("source_artifact")}

    def get_neighbors(self, ref: CrossDomainEntityRef) -> tuple[Mapping[str, Any], ...]:
        store = self._load()
        if store is None:
            return ()
        neighbors = []
        for edge in (*store.theory_edges, *store.evidence_edges):
            if edge["source"] == ref.entity_id:
                neighbors.append({"id": edge["target"], "relation": edge["relation"]})
            elif edge["target"] == ref.entity_id:
                neighbors.append({"id": edge["source"], "relation": edge["relation"]})
        return tuple(neighbors)


class EvidenceGraphAdapter(TheoryGraphAdapter):
    """Read-only access to the evidence layer of the historical graph."""

    domain = Domain.EVIDENCE

    def resolve_entity(self, ref: CrossDomainEntityRef) -> Mapping[str, Any] | None:
        store = self._load()
        if store is None:
            return None
        node = store.evidence_nodes.get(ref.entity_id)
        return dict(node) if node else None


class HypergraphAdapter:
    """Read-only access to the Hypergraph domain."""

    domain = Domain.HYPERGRAPH
    read_only = True

    def __init__(self, root: str | Path):
        self.root = Path(root)
        self._records: dict[str, Mapping[str, Any]] | None = None

    def _load(self) -> dict[str, Mapping[str, Any]]:
        if self._records is None:
            from terrario.lab.theory.ingestion import TheoryIngestor
            records: dict[str, Mapping[str, Any]] = {}
            graphs = sorted(self.root.glob("theory_snapshots/*/theory_graph.json"))
            if graphs:
                ingestor = TheoryIngestor(graphs[-1].parent).ingest()
                for hyperedge in getattr(ingestor, "hyperedges", ()):
                    data = hyperedge if isinstance(hyperedge, Mapping) else vars(hyperedge)
                    records[str(data.get("id"))] = dict(data)
            self._records = records
        return self._records

    def exists(self, ref: CrossDomainEntityRef) -> bool:
        return ref.entity_id in self._load()

    def resolve_entity(self, ref: CrossDomainEntityRef) -> Mapping[str, Any] | None:
        return self._load().get(ref.entity_id)

    def verify_identity(self, ref: CrossDomainEntityRef) -> bool:
        return self.exists(ref)

    def get_content_hash(self, ref: CrossDomainEntityRef) -> str | None:
        return None

    def get_snapshot(self) -> str | None:
        return None

    def get_provenance(self, ref: CrossDomainEntityRef) -> Mapping[str, Any]:
        entity = self.resolve_entity(ref) or {}
        return {"provenance": entity.get("provenance"), "status": entity.get("status")}

    def get_neighbors(self, ref: CrossDomainEntityRef) -> tuple[Mapping[str, Any], ...]:
        entity = self.resolve_entity(ref)
        if entity is None:
            return ()
        members = entity.get("members", ())
        return tuple({"id": member, "relation": "MEMBER_OF"} for member in members)


class HypothesisAdapter(TheoryGraphAdapter):
    """Read-only access to hypotheses recorded in the historical graph."""

    domain = Domain.HYPOTHESIS

    def resolve_entity(self, ref: CrossDomainEntityRef) -> Mapping[str, Any] | None:
        store = self._load()
        if store is None:
            return None
        node = store.evidence_nodes.get(ref.entity_id) or store.theory_nodes.get(ref.entity_id)
        return dict(node) if node else None


class WorldAdapter:
    """Read-only access to World/Scenario definitions."""

    domain = Domain.WORLD
    read_only = True

    def __init__(self, root: str | Path):
        self.root = Path(root)

    def _compiled(self, world_id: str):
        from terrario.lab.world_authoring import compile_registry_world
        from terrario.lab.world_registry import WorldScenarioRegistry
        try:
            entry = WorldScenarioRegistry(self.root).get(world_id)
            return compile_registry_world(world_id, entry.source) if entry else None
        except Exception:
            return None

    def exists(self, ref: CrossDomainEntityRef) -> bool:
        return self._compiled(ref.entity_id) is not None

    def resolve_entity(self, ref: CrossDomainEntityRef) -> Mapping[str, Any] | None:
        compiled = self._compiled(ref.entity_id)
        if compiled is None:
            return None
        return {"world_id": compiled.definition.world_id,
                "content_hash": compiled.definition.content_hash}

    def verify_identity(self, ref: CrossDomainEntityRef) -> bool:
        entity = self.resolve_entity(ref)
        if entity is None:
            return False
        if ref.content_hash:
            return entity["content_hash"] == ref.content_hash
        return True

    def get_content_hash(self, ref: CrossDomainEntityRef) -> str | None:
        entity = self.resolve_entity(ref)
        return entity["content_hash"] if entity else None

    def get_snapshot(self) -> str | None:
        return None

    def get_provenance(self, ref: CrossDomainEntityRef) -> Mapping[str, Any]:
        return {"world_id": ref.entity_id, "source": "world_registry"}

    def get_neighbors(self, ref: CrossDomainEntityRef) -> tuple[Mapping[str, Any], ...]:
        return ()


class ScenarioAdapter(WorldAdapter):
    domain = Domain.SCENARIO


def build_adapter_registry(root: str | Path,
                           artifacts: ArtifactRepository) -> dict[Domain, DomainAdapter]:
    """Central registry of domain adapters; no scattered domain-specific logic."""
    root = Path(root)
    reference = ReferenceGraphAdapter(artifacts)
    theory = TheoryGraphAdapter(root)
    return {
        Domain.REFERENCE: reference,
        Domain.CORPUS: reference,
        Domain.CLAIM: reference,
        Domain.ONTOLOGY: theory,
        Domain.THEORY: theory,
        Domain.HYPERGRAPH: HypergraphAdapter(root),
        Domain.HYPOTHESIS: HypothesisAdapter(root),
        Domain.WORLD: WorldAdapter(root),
        Domain.SCENARIO: ScenarioAdapter(root),
        Domain.EXPERIMENT: ExperimentAdapter(artifacts),
        Domain.PREREGISTRATION: PreregistrationAdapter(artifacts),
        Domain.EVIDENCE: EvidenceGraphAdapter(root),
    }
