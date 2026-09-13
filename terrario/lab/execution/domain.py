"""Versioned, dependency-free contracts for SCIENTIFIC-EXECUTION-GATE-01."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, Mapping

from terrario.lab.persistence.canonical import content_hash

SCHEMA_VERSION = "terrario.lab.scientific-execution/v1"


class ExecutionState(StrEnum):
    REQUESTED = "REQUESTED"
    VALIDATING = "VALIDATING"
    AUTHORIZED = "AUTHORIZED"
    PLANNED = "PLANNED"
    READY = "READY"
    RUNNING = "RUNNING"
    PAUSING = "PAUSING"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    ABORTED = "ABORTED"
    RECOVERY_REQUIRED = "RECOVERY_REQUIRED"


class AuthorizationScope(StrEnum):
    ONE_EXECUTION = "ONE_EXECUTION"
    N_EXECUTIONS = "N_EXECUTIONS"
    REPLICATION_SERIES = "REPLICATION_SERIES"
    UNTIL_EXPIRY = "UNTIL_EXPIRY"


class VerificationClass(StrEnum):
    PASS = "PASS"
    FAIL = "FAIL"
    WARNING = "WARNING"
    INCOMPLETE = "INCOMPLETE"
    DEVIATED = "DEVIATED"
    ABORTED = "ABORTED"
    UNVERIFIABLE = "UNVERIFIABLE"


class ExecutionError(RuntimeError):
    code = "SCIENTIFIC_EXECUTION_ERROR"


class ExecutionNotReady(ExecutionError):
    code = "EXECUTION_NOT_READY"


class ExecutionConflict(ExecutionError):
    code = "EXECUTION_CONFLICT"


class ExecutionUnauthorized(ExecutionError):
    code = "EXECUTION_UNAUTHORIZED"


class InvalidExecutionTransition(ExecutionError):
    code = "INVALID_EXECUTION_TRANSITION"


@dataclass(frozen=True)
class ResourceCeiling:
    cpu_cores: int
    gpu_devices: tuple[str, ...]
    memory_bytes: int
    disk_bytes: int
    max_processes: int
    wall_clock_seconds: int

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any]) -> "ResourceCeiling":
        required = {"cpu_cores", "gpu_devices", "memory_bytes", "disk_bytes", "max_processes", "wall_clock_seconds"}
        if set(payload) != required:
            raise ValueError("resource_ceiling requires exactly cpu_cores, gpu_devices, memory_bytes, disk_bytes, max_processes, wall_clock_seconds")
        value = cls(int(payload["cpu_cores"]), tuple(str(x) for x in payload["gpu_devices"]),
                    int(payload["memory_bytes"]), int(payload["disk_bytes"]),
                    int(payload["max_processes"]), int(payload["wall_clock_seconds"]))
        if any(x <= 0 for x in (value.cpu_cores, value.memory_bytes, value.disk_bytes, value.max_processes, value.wall_clock_seconds)):
            raise ValueError("resource ceiling values must be positive")
        return value


@dataclass(frozen=True)
class ScientificExecutionRequest:
    execution_id: str
    preregistration_root_hash: str
    created_by: str
    created_at: str
    schema_version: str = f"{SCHEMA_VERSION}/request"


@dataclass(frozen=True)
class ExecutionAuthorization:
    authorization_id: str
    preregistration_root_hash: str
    actor_id: str
    scope_type: AuthorizationScope
    max_execution_count: int
    resource_ceiling: ResourceCeiling
    created_at: str
    reason: str
    expires_at: str | None = None
    replication_group_id: str | None = None
    schema_version: str = f"{SCHEMA_VERSION}/authorization"

    @property
    def authorization_hash(self) -> str:
        return content_hash(self)


@dataclass(frozen=True)
class ExecutionEnvironmentSnapshot:
    values: Mapping[str, Any]
    schema_version: str = f"{SCHEMA_VERSION}/environment"

    @property
    def content_hash(self) -> str:
        return content_hash(self)


@dataclass(frozen=True)
class ExecutionSoftwareSnapshot:
    values: Mapping[str, Any]
    schema_version: str = f"{SCHEMA_VERSION}/software"

    @property
    def content_hash(self) -> str:
        return content_hash(self)


@dataclass(frozen=True)
class ScientificExecutionPlan:
    preregistration_root_hash: str
    trial_matrix_hash: str
    trial_count: int
    trial_identities: tuple[Mapping[str, Any], ...]
    protocol: Mapping[str, Any]
    environment_hash: str
    software_hash: str
    schema_version: str = f"{SCHEMA_VERSION}/plan"

    @property
    def plan_hash(self) -> str:
        return content_hash(self)


@dataclass(frozen=True)
class ExecutionSession:
    execution_id: str
    state: ExecutionState
    revision: int
    execution_root_hash: str | None = None
    schema_version: str = f"{SCHEMA_VERSION}/session"


@dataclass(frozen=True)
class TrialExecution:
    trial_intent_id: str
    execution_id: str
    identity: Mapping[str, Any]
    schema_version: str = f"{SCHEMA_VERSION}/trial"


@dataclass(frozen=True)
class TrialAttempt:
    attempt_id: str
    trial_intent_id: str
    ordinal: int
    state: str
    schema_version: str = f"{SCHEMA_VERSION}/attempt"


@dataclass(frozen=True)
class ExecutionArtifactManifest:
    execution_id: str
    descriptors: tuple[Mapping[str, Any], ...]
    schema_version: str = f"{SCHEMA_VERSION}/artifact-manifest"

    @property
    def artifact_root_hash(self) -> str:
        return content_hash(self)


@dataclass(frozen=True)
class RawRunArtifact:
    artifact_type: str
    blob_hash: str
    size_bytes: int
    trial_intent_id: str | None = None
    attempt_id: str | None = None
    schema_version: str = f"{SCHEMA_VERSION}/raw-artifact"

    @property
    def descriptor_hash(self) -> str:
        return content_hash(self)


@dataclass(frozen=True)
class ExecutionDeviation:
    deviation_id: str
    execution_id: str
    deviation_type: str
    payload: Mapping[str, Any]
    schema_version: str = f"{SCHEMA_VERSION}/deviation"


@dataclass(frozen=True)
class ExecutionFailure:
    execution_id: str
    failure_code: str
    payload: Mapping[str, Any]
    schema_version: str = f"{SCHEMA_VERSION}/failure"


@dataclass(frozen=True)
class ExecutionCheckpoint:
    checkpoint_id: str
    execution_id: str
    checkpoint_class: str
    blob_hash: str
    schema_version: str = f"{SCHEMA_VERSION}/checkpoint"


@dataclass(frozen=True)
class ExecutionAttestation:
    execution_id: str
    actor_id: str
    statement: str
    schema_version: str = f"{SCHEMA_VERSION}/attestation"


@dataclass(frozen=True)
class ExecutionSummary:
    execution_id: str
    state: ExecutionState
    trial_count: int
    attempt_count: int
    failure_count: int
    deviation_count: int
    schema_version: str = f"{SCHEMA_VERSION}/summary"


@dataclass(frozen=True)
class ExecutionVerificationReport:
    execution_id: str
    classification: VerificationClass
    checks: Mapping[str, bool]
    failures: tuple[str, ...] = ()
    warnings: tuple[str, ...] = ()
    schema_version: str = f"{SCHEMA_VERSION}/verification"

    @property
    def report_hash(self) -> str:
        return content_hash(self)


LEGAL_TRANSITIONS: dict[ExecutionState, frozenset[ExecutionState]] = {
    ExecutionState.REQUESTED: frozenset({ExecutionState.VALIDATING, ExecutionState.CANCELLED}),
    ExecutionState.VALIDATING: frozenset({ExecutionState.AUTHORIZED, ExecutionState.FAILED, ExecutionState.CANCELLED}),
    ExecutionState.AUTHORIZED: frozenset({ExecutionState.PLANNED, ExecutionState.CANCELLED}),
    ExecutionState.PLANNED: frozenset({ExecutionState.READY, ExecutionState.FAILED, ExecutionState.CANCELLED}),
    ExecutionState.READY: frozenset({ExecutionState.RUNNING, ExecutionState.CANCELLED}),
    ExecutionState.RUNNING: frozenset({ExecutionState.PAUSING, ExecutionState.STOPPING, ExecutionState.COMPLETED, ExecutionState.FAILED, ExecutionState.RECOVERY_REQUIRED}),
    ExecutionState.PAUSING: frozenset({ExecutionState.PAUSED, ExecutionState.FAILED, ExecutionState.RECOVERY_REQUIRED}),
    ExecutionState.PAUSED: frozenset({ExecutionState.RUNNING, ExecutionState.STOPPING, ExecutionState.CANCELLED, ExecutionState.RECOVERY_REQUIRED}),
    ExecutionState.STOPPING: frozenset({ExecutionState.CANCELLED, ExecutionState.ABORTED, ExecutionState.FAILED}),
    ExecutionState.RECOVERY_REQUIRED: frozenset({ExecutionState.PAUSED, ExecutionState.ABORTED, ExecutionState.FAILED}),
    ExecutionState.COMPLETED: frozenset(), ExecutionState.FAILED: frozenset(),
    ExecutionState.CANCELLED: frozenset(), ExecutionState.ABORTED: frozenset(),
}


def assert_transition(current: str, target: ExecutionState) -> None:
    if target not in LEGAL_TRANSITIONS[ExecutionState(current)]:
        raise InvalidExecutionTransition(f"{current} -> {target.value} is prohibited")
