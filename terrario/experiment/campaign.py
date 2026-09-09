"""Immutable campaign contracts: validity, identity, certificates and manifests."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any


class ReasonCode(StrEnum):
    TECHNICAL_FAILURE = "TECHNICAL_FAILURE"
    NUMERICAL_FAILURE = "NUMERICAL_FAILURE"
    WORLD_SIGNAL_FAILURE = "WORLD_SIGNAL_FAILURE"
    WORLD_PAIRING_FAILURE = "WORLD_PAIRING_FAILURE"
    INSUFFICIENT_AGENT_INTERACTION = "INSUFFICIENT_AGENT_INTERACTION"
    NOT_LEARNED_PRE_CHANGE = "NOT_LEARNED_PRE_CHANGE"
    NO_DISRUPTION_OBSERVED = "NO_DISRUPTION_OBSERVED"
    FAILED_TO_RECOVER = "FAILED_TO_RECOVER"
    PARTIAL_RECOVERY = "PARTIAL_RECOVERY"
    RECOVERED = "RECOVERED"
    RECOVERED_AND_TRANSFERRED = "RECOVERED_AND_TRANSFERRED"
    TRANSFER_CONTAMINATED = "TRANSFER_CONTAMINATED"
    OBSERVER_INTEGRITY_FAILURE = "OBSERVER_INTEGRITY_FAILURE"
    VALID_UNCLASSIFIED = "VALID_UNCLASSIFIED"


@dataclass(frozen=True)
class ValidityField:
    passed: bool
    reason: ReasonCode
    metrics: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ExperimentalValidity:
    technical_valid: ValidityField
    world_signal_sufficient: ValidityField
    agent_interaction_sufficient: ValidityField
    pre_change_learning_sufficient: ValidityField
    change_exposure_valid: ValidityField
    transfer_integrity_valid: ValidityField
    experimentally_interpretable: ValidityField
    adaptation_status: ReasonCode


@dataclass(frozen=True)
class RunIdentity:
    hypothesis_id: str
    protocol_version: str
    variant_id: str
    world_seed: int
    agent_seed: int
    config_hash: str
    code_hash: str

    @property
    def run_id(self) -> str:
        payload = json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(payload.encode()).hexdigest()[:24]


def file_hash(path: str | Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class RunCompletionCertificate:
    run_id: str
    start_state_hash: str
    final_state_hash: str
    evidence_manifest_hash: str
    metrics_hash: str
    checkpoint_hash: str
    completion_status: ReasonCode
    code_hash: str
    config_hash: str

    def verify(self) -> bool:
        return all(bool(value) for value in asdict(self).values())


@dataclass(frozen=True)
class EvidenceManifest:
    schema_version: str
    run_id: str
    files: dict[str, str]
    metadata: dict[str, Any] = field(default_factory=dict)

    def digest(self) -> str:
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True, default=str).encode()).hexdigest()

    def verify(self, root: str | Path) -> bool:
        root = Path(root)
        return all((root / name).is_file() and file_hash(root / name) == digest for name, digest in self.files.items())


@dataclass(frozen=True)
class TraceManifest(EvidenceManifest):
    observer_mode: str = "scientific_standard"
    forensic_windows: list[dict[str, int]] = field(default_factory=list)
    compression: str = "backend_default"


def write_manifest(path: str | Path, manifest: EvidenceManifest) -> None:
    Path(path).write_text(json.dumps(asdict(manifest), indent=2, sort_keys=True, default=str))


def verify_evidence_manifest(path: str | Path, root: str | Path) -> bool:
    data = json.loads(Path(path).read_text())
    return EvidenceManifest(**{key: data[key] for key in ("schema_version", "run_id", "files", "metadata")}).verify(root)
