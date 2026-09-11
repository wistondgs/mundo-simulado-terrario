"""Ports that keep domain services independent from SQLite implementation details."""

from __future__ import annotations

from typing import Any, ContextManager, Protocol, runtime_checkable

from terrario.lab.persistence.blobs import BlobManifest
from terrario.lab.persistence.store import ArtifactVersionRecord


@runtime_checkable
class ArtifactRepositoryPort(Protocol):
    def create_artifact(self, kind: str, payload: Any, schema_version: str, **options: Any) -> ArtifactVersionRecord: ...
    def create_version(self, artifact_id: str, payload: Any, schema_version: str, **options: Any) -> ArtifactVersionRecord: ...
    def current(self, artifact_id: str, kind: str | None = None) -> ArtifactVersionRecord: ...
    def versions(self, artifact_id: str) -> tuple[ArtifactVersionRecord, ...]: ...


@runtime_checkable
class BlobStorePort(Protocol):
    def put_bytes(self, payload: bytes, media_type: str = "application/octet-stream") -> BlobManifest: ...
    def verify(self, digest: str) -> bool: ...
    def read(self, digest: str) -> bytes: ...


@runtime_checkable
class UnitOfWorkPort(Protocol):
    def transaction(self) -> ContextManager[Any]: ...


@runtime_checkable
class JobRepositoryPort(Protocol):
    """Reserved boundary for EXECUTION-ORCHESTRATOR-01; no execution is exposed now."""

    def enqueue(self, trial_intent_id: str, idempotency_key: str, required_device: str) -> Any: ...
    def lease_next(self, worker_id: str, device_kind: str) -> Any: ...
