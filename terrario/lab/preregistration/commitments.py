"""Content-addressed component and root commitments."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from terrario.lab.persistence import ArtifactRepository
from terrario.lab.persistence.canonical import canonical_json, content_hash, plain
from terrario.lab.preregistration.domain import (
    CANONICALIZATION_PROFILE,
    ComponentDescriptor,
    PreregistrationDraft,
)
from terrario.lab.preregistration.validation import policy_snapshot

ROOT_SCHEMA = "terrario.lab.preregistration-bundle/v1"
#: Adds the sealed gate inventory.  A new schema rather than an eleventh entry in
#: `ROLE_ORDER`, because `verify` compares the role tuple exactly and 141 bundles
#: are already sealed with ten: growing the constant would invalidate all of them
#: at once.  Same precedent as `RESULT_SCHEMA v2`, where a v1 payload is refused
#: for new publication and never rewritten.
ROOT_SCHEMA_V2 = "terrario.lab.preregistration-bundle/v2"


@dataclass(frozen=True)
class PreparedCommitment:
    root_manifest: Mapping[str, Any]
    bundle_root_hash: str
    root_cas_hash: str
    components: tuple[ComponentDescriptor, ...]
    component_payloads: Mapping[str, Any]


class CommitmentBuilder:
    """Build a deterministic manifest; CAS writes are safe before DB commit."""

    ROLE_ORDER = (
        "scientific_question",
        "causal_design",
        "protocol",
        "metrics_and_endpoints",
        "observer",
        "seeds_partitions_randomization_replication",
        "analysis",
        "policies",
        "environment_and_software",
        "validation_policy",
    )
    #: v2 appends the sealed gate inventory.  The tuple is compared exactly by
    #: `verify`, so each schema keeps its own and a bundle is checked against the
    #: order it was sealed under -- never against the newest one.
    ROLE_ORDERS = {ROOT_SCHEMA: ROLE_ORDER, ROOT_SCHEMA_V2: ROLE_ORDER + ("gates",)}

    def __init__(self, artifacts: ArtifactRepository):
        self.artifacts = artifacts

    @classmethod
    def role_order(cls, schema_version: str) -> tuple[str, ...]:
        return cls.ROLE_ORDERS.get(schema_version, cls.ROLE_ORDER)

    def build(self, draft: PreregistrationDraft) -> PreparedCommitment:
        payloads: dict[str, Any] = {
            "scientific_question": plain(draft.scientific_question),
            "causal_design": plain(draft.causal_design),
            "protocol": plain(draft.protocol),
            "metrics_and_endpoints": {
                "metrics": plain(draft.metrics), "endpoints": plain(draft.endpoints),
            },
            "observer": plain(draft.observer),
            "seeds_partitions_randomization_replication": {
                "seeds": plain(draft.seeds), "partitions": plain(draft.partitions),
                "randomization": plain(draft.randomization), "replication": plain(draft.replication),
            },
            "analysis": plain(draft.analysis),
            "policies": {
                "stopping": plain(draft.stopping), "exclusions": plain(draft.exclusions),
                "failures": plain(draft.failures), "storage": plain(draft.storage),
            },
            "environment_and_software": {
                "requirement": plain(draft.environment_requirement),
                "observed": plain(draft.observed_environment), "software": plain(draft.software),
            },
            "validation_policy": plain(policy_snapshot()),
        }
        # A draft that seals what its gates certify is a v2 bundle; one that does
        # not is byte-identical to what it would have produced before this role
        # existed, which is what keeps the 141 sealed bundles verifiable.
        schema = ROOT_SCHEMA_V2 if draft.gates is not None else ROOT_SCHEMA
        if draft.gates is not None:
            payloads["gates"] = draft.gates.payload()
        descriptors = []
        for ordinal, role in enumerate(self.role_order(schema)):
            value = payloads[role]
            encoded = canonical_json(value).encode("utf-8")
            manifest = self.artifacts.register_blob(encoded, "application/vnd.terrario.preregistration-component+json")
            source_version = draft.protocol.experiment_draft_version_id if role == "protocol" else None
            source_hash = draft.protocol.experiment_draft_hash if role == "protocol" else None
            descriptors.append(ComponentDescriptor(
                role, ordinal, f"{schema}/{role}", content_hash(value), manifest.blob_hash,
                source_version, source_hash,
            ))
        root_manifest = {
            "schema_version": schema,
            "canonicalization_profile": CANONICALIZATION_PROFILE,
            "study_intent": draft.study_intent.value,
            "components": plain(tuple(descriptors)),
            "experiment_draft": {
                "version_id": draft.protocol.experiment_draft_version_id,
                "scientific_hash": draft.protocol.experiment_draft_hash,
            },
            "trial_matrix": {
                "version_id": draft.protocol.trial_matrix_version_id,
                "scientific_hash": draft.protocol.trial_matrix_hash,
            },
            "scientific_execution": False,
            "evidence_publication": False,
        }
        root_bytes = canonical_json(root_manifest).encode("utf-8")
        root_hash = content_hash(root_manifest)
        root_blob = self.artifacts.register_blob(root_bytes, "application/vnd.terrario.preregistration-root+json")
        if root_blob.blob_hash != root_hash:
            raise AssertionError("canonical root and CAS digest diverged")
        return PreparedCommitment(root_manifest, root_hash, root_blob.blob_hash,
                                  tuple(descriptors), payloads)

    def verify(self, root_manifest: Mapping[str, Any]) -> tuple[bool, tuple[str, ...]]:
        failures: list[str] = []
        schema = str(root_manifest.get("schema_version"))
        if schema not in self.ROLE_ORDERS:
            failures.append("UNSUPPORTED_ROOT_SCHEMA")
        if root_manifest.get("canonicalization_profile") != CANONICALIZATION_PROFILE:
            failures.append("UNSUPPORTED_CANONICALIZATION_PROFILE")
        for descriptor in root_manifest.get("components", ()):
            digest = str(descriptor.get("cas_sha256", ""))
            if not self.artifacts.blobs.verify(digest):
                failures.append(f"CAS_OBJECT_MISSING:{descriptor.get('role')}")
                continue
            payload = self.artifacts.blobs.read(digest)
            if content_hash(__import__("json").loads(payload)) != descriptor.get("content_sha256"):
                failures.append(f"COMPONENT_HASH_MISMATCH:{descriptor.get('role')}")
        root_hash = content_hash(root_manifest)
        if not self.artifacts.blobs.verify(root_hash):
            failures.append("ROOT_CAS_OBJECT_MISSING")
        return not failures, tuple(failures)
