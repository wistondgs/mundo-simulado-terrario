"""Numbered SQLite migrations for the local Terrario data store."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    sql: str


MIGRATIONS = (
    Migration(
        1,
        "initial_durable_lab_store",
        r"""
CREATE TABLE IF NOT EXISTS schema_migrations (
    version INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    checksum TEXT NOT NULL,
    applied_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS artifacts (
    artifact_id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS artifact_versions (
    version_id TEXT PRIMARY KEY,
    artifact_id TEXT NOT NULL REFERENCES artifacts(artifact_id),
    version_number INTEGER NOT NULL CHECK (version_number > 0),
    kind TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    scientific_hash TEXT NOT NULL CHECK (length(scientific_hash) = 64),
    scientific_payload_json TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    classification TEXT NOT NULL,
    parent_version_id TEXT REFERENCES artifact_versions(version_id),
    parent_hash TEXT,
    delta_json TEXT NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    sealed INTEGER NOT NULL DEFAULT 0 CHECK (sealed IN (0, 1)),
    UNIQUE (artifact_id, version_number),
    UNIQUE (kind, scientific_hash)
);

CREATE INDEX IF NOT EXISTS artifact_versions_artifact_idx
    ON artifact_versions(artifact_id, version_number DESC);
CREATE INDEX IF NOT EXISTS artifact_versions_parent_idx ON artifact_versions(parent_version_id);

CREATE TABLE IF NOT EXISTS artifact_state_events (
    event_id TEXT PRIMARY KEY,
    version_id TEXT NOT NULL REFERENCES artifact_versions(version_id),
    sequence INTEGER NOT NULL CHECK (sequence > 0),
    from_state TEXT,
    to_state TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    decision_id TEXT,
    created_at TEXT NOT NULL,
    UNIQUE (version_id, sequence)
);

CREATE TABLE IF NOT EXISTS artifact_links (
    link_id TEXT PRIMARY KEY,
    source_version_id TEXT NOT NULL REFERENCES artifact_versions(version_id),
    target_version_id TEXT NOT NULL REFERENCES artifact_versions(version_id),
    relation TEXT NOT NULL,
    epistemic_status TEXT NOT NULL,
    provenance_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS review_requests (
    review_id TEXT PRIMARY KEY,
    artifact_version_id TEXT NOT NULL REFERENCES artifact_versions(version_id),
    review_kind TEXT NOT NULL,
    requested_by TEXT NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS review_decisions (
    decision_id TEXT PRIMARY KEY,
    review_id TEXT NOT NULL REFERENCES review_requests(review_id),
    artifact_version_id TEXT NOT NULL REFERENCES artifact_versions(version_id),
    artifact_hash TEXT NOT NULL,
    decision TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    supersedes_decision_id TEXT REFERENCES review_decisions(decision_id),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS trial_intents (
    trial_intent_id TEXT PRIMARY KEY,
    execution_plan_version_id TEXT NOT NULL,
    identity_json TEXT NOT NULL,
    required_device TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS execution_batches (
    batch_id TEXT PRIMARY KEY,
    execution_plan_version_id TEXT NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS execution_jobs (
    job_id TEXT PRIMARY KEY,
    batch_id TEXT REFERENCES execution_batches(batch_id),
    trial_intent_id TEXT NOT NULL REFERENCES trial_intents(trial_intent_id),
    idempotency_key TEXT NOT NULL UNIQUE,
    required_device TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 0,
    projected_state TEXT NOT NULL,
    lease_owner TEXT,
    lease_expires_at TEXT,
    not_before TEXT,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS job_events (
    event_id TEXT PRIMARY KEY,
    job_id TEXT NOT NULL REFERENCES execution_jobs(job_id),
    sequence INTEGER NOT NULL,
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (job_id, sequence)
);

CREATE TABLE IF NOT EXISTS worker_leases (
    worker_id TEXT PRIMARY KEY,
    device_kind TEXT NOT NULL,
    capabilities_json TEXT NOT NULL,
    heartbeat_at TEXT NOT NULL,
    lease_expires_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS run_attempts (
    attempt_id TEXT PRIMARY KEY,
    trial_intent_id TEXT NOT NULL REFERENCES trial_intents(trial_intent_id),
    ordinal INTEGER NOT NULL CHECK (ordinal > 0),
    projected_state TEXT NOT NULL,
    staging_path TEXT,
    manifest_hash TEXT,
    worker_id TEXT,
    device_manifest_id TEXT,
    started_at TEXT,
    finished_at TEXT,
    UNIQUE (trial_intent_id, ordinal)
);

CREATE TABLE IF NOT EXISTS blob_manifests (
    blob_hash TEXT PRIMARY KEY CHECK (length(blob_hash) = 64),
    relative_path TEXT NOT NULL UNIQUE,
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    media_type TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS audit_events (
    audit_id TEXT PRIMARY KEY,
    correlation_id TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    action TEXT NOT NULL,
    target_type TEXT NOT NULL,
    target_id TEXT NOT NULL,
    details_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TRIGGER IF NOT EXISTS artifact_versions_no_update
BEFORE UPDATE ON artifact_versions BEGIN
    SELECT RAISE(ABORT, 'artifact versions are append-only');
END;

CREATE TRIGGER IF NOT EXISTS artifact_versions_no_delete
BEFORE DELETE ON artifact_versions BEGIN
    SELECT RAISE(ABORT, 'artifact versions are append-only');
END;

CREATE TRIGGER IF NOT EXISTS artifact_state_events_no_update
BEFORE UPDATE ON artifact_state_events BEGIN
    SELECT RAISE(ABORT, 'artifact state events are append-only');
END;

CREATE TRIGGER IF NOT EXISTS artifact_state_events_no_delete
BEFORE DELETE ON artifact_state_events BEGIN
    SELECT RAISE(ABORT, 'artifact state events are append-only');
END;

CREATE TRIGGER IF NOT EXISTS review_decisions_no_update
BEFORE UPDATE ON review_decisions BEGIN
    SELECT RAISE(ABORT, 'review decisions are append-only');
END;

CREATE TRIGGER IF NOT EXISTS review_decisions_no_delete
BEFORE DELETE ON review_decisions BEGIN
    SELECT RAISE(ABORT, 'review decisions are append-only');
END;

CREATE TRIGGER IF NOT EXISTS job_events_no_update
BEFORE UPDATE ON job_events BEGIN
    SELECT RAISE(ABORT, 'job events are append-only');
END;

CREATE TRIGGER IF NOT EXISTS job_events_no_delete
BEFORE DELETE ON job_events BEGIN
    SELECT RAISE(ABORT, 'job events are append-only');
END;

CREATE TRIGGER IF NOT EXISTS audit_events_no_update
BEFORE UPDATE ON audit_events BEGIN
    SELECT RAISE(ABORT, 'audit events are append-only');
END;

CREATE TRIGGER IF NOT EXISTS audit_events_no_delete
BEFORE DELETE ON audit_events BEGIN
    SELECT RAISE(ABORT, 'audit events are append-only');
END;
""",
    ),
    Migration(
        2,
        "scientific_preregistration_core",
        r"""
CREATE TABLE IF NOT EXISTS preregistration_components (
    component_id TEXT PRIMARY KEY,
    bundle_version_id TEXT NOT NULL REFERENCES artifact_versions(version_id),
    role TEXT NOT NULL,
    ordinal INTEGER NOT NULL CHECK (ordinal >= 0),
    schema_version TEXT NOT NULL,
    content_hash TEXT NOT NULL CHECK (length(content_hash) = 64),
    cas_hash TEXT NOT NULL REFERENCES blob_manifests(blob_hash),
    source_artifact_version_id TEXT REFERENCES artifact_versions(version_id),
    source_scientific_hash TEXT,
    created_at TEXT NOT NULL,
    UNIQUE(bundle_version_id, role, ordinal)
);

CREATE TABLE IF NOT EXISTS preregistration_review_packages (
    review_package_id TEXT PRIMARY KEY,
    bundle_version_id TEXT NOT NULL UNIQUE REFERENCES artifact_versions(version_id),
    package_hash TEXT NOT NULL UNIQUE CHECK (length(package_hash) = 64),
    blob_hash TEXT NOT NULL REFERENCES blob_manifests(blob_hash),
    policy_snapshot_hash TEXT NOT NULL CHECK (length(policy_snapshot_hash) = 64),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS review_warning_acceptances (
    acceptance_id TEXT PRIMARY KEY,
    decision_id TEXT NOT NULL REFERENCES review_decisions(decision_id),
    finding_hash TEXT NOT NULL CHECK (length(finding_hash) = 64),
    rule_id TEXT NOT NULL,
    rule_version TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(decision_id, finding_hash)
);

CREATE TABLE IF NOT EXISTS preregistration_attestations (
    attestation_id TEXT PRIMARY KEY,
    preregistration_id TEXT NOT NULL REFERENCES artifacts(artifact_id),
    bundle_version_id TEXT NOT NULL UNIQUE REFERENCES artifact_versions(version_id),
    bundle_root_hash TEXT NOT NULL UNIQUE CHECK (length(bundle_root_hash) = 64),
    review_decision_id TEXT NOT NULL REFERENCES review_decisions(decision_id),
    review_package_hash TEXT NOT NULL CHECK (length(review_package_hash) = 64),
    actor_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    accepted_warning_hashes_json TEXT NOT NULL,
    audit_event_hash TEXT NOT NULL CHECK (length(audit_event_hash) = 64),
    signature_status TEXT NOT NULL,
    attestation_hash TEXT NOT NULL UNIQUE CHECK (length(attestation_hash) = 64),
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS preregistration_locks (
    preregistration_id TEXT PRIMARY KEY REFERENCES artifacts(artifact_id),
    bundle_version_id TEXT NOT NULL UNIQUE REFERENCES artifact_versions(version_id),
    bundle_root_hash TEXT NOT NULL UNIQUE CHECK (length(bundle_root_hash) = 64),
    review_decision_id TEXT NOT NULL REFERENCES review_decisions(decision_id),
    attestation_id TEXT NOT NULL UNIQUE REFERENCES preregistration_attestations(attestation_id),
    actor_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    idempotency_key TEXT UNIQUE,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS exposure_records (
    exposure_id TEXT PRIMARY KEY,
    scenario_id TEXT NOT NULL,
    scenario_hash TEXT NOT NULL,
    world_seed INTEGER NOT NULL,
    exposure_kind TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    context_type TEXT NOT NULL,
    context_id TEXT NOT NULL,
    preregistration_root_hash TEXT,
    previous_event_hash TEXT,
    event_hash TEXT NOT NULL UNIQUE CHECK (length(event_hash) = 64),
    occurred_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS exposure_subject_idx
    ON exposure_records(scenario_id, scenario_hash, world_seed, occurred_at);

CREATE TABLE IF NOT EXISTS preregistration_audit_chain (
    chain_event_id TEXT PRIMARY KEY,
    preregistration_id TEXT NOT NULL REFERENCES artifacts(artifact_id),
    sequence INTEGER NOT NULL CHECK (sequence > 0),
    event_type TEXT NOT NULL,
    event_payload_json TEXT NOT NULL,
    previous_event_hash TEXT,
    event_hash TEXT NOT NULL UNIQUE CHECK (length(event_hash) = 64),
    actor_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(preregistration_id, sequence)
);

CREATE TABLE IF NOT EXISTS preregistration_command_keys (
    idempotency_key TEXT PRIMARY KEY,
    command_type TEXT NOT NULL,
    request_hash TEXT NOT NULL CHECK (length(request_hash) = 64),
    response_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TRIGGER IF NOT EXISTS preregistration_components_no_update
BEFORE UPDATE ON preregistration_components BEGIN
    SELECT RAISE(ABORT, 'preregistration components are append-only');
END;
CREATE TRIGGER IF NOT EXISTS preregistration_components_no_delete
BEFORE DELETE ON preregistration_components BEGIN
    SELECT RAISE(ABORT, 'preregistration components are append-only');
END;
CREATE TRIGGER IF NOT EXISTS preregistration_review_packages_no_update
BEFORE UPDATE ON preregistration_review_packages BEGIN
    SELECT RAISE(ABORT, 'review packages are append-only');
END;
CREATE TRIGGER IF NOT EXISTS preregistration_review_packages_no_delete
BEFORE DELETE ON preregistration_review_packages BEGIN
    SELECT RAISE(ABORT, 'review packages are append-only');
END;
CREATE TRIGGER IF NOT EXISTS review_warning_acceptances_no_update
BEFORE UPDATE ON review_warning_acceptances BEGIN
    SELECT RAISE(ABORT, 'warning acceptances are append-only');
END;
CREATE TRIGGER IF NOT EXISTS review_warning_acceptances_no_delete
BEFORE DELETE ON review_warning_acceptances BEGIN
    SELECT RAISE(ABORT, 'warning acceptances are append-only');
END;
CREATE TRIGGER IF NOT EXISTS preregistration_attestations_no_update
BEFORE UPDATE ON preregistration_attestations BEGIN
    SELECT RAISE(ABORT, 'preregistration attestations are append-only');
END;
CREATE TRIGGER IF NOT EXISTS preregistration_attestations_no_delete
BEFORE DELETE ON preregistration_attestations BEGIN
    SELECT RAISE(ABORT, 'preregistration attestations are append-only');
END;
CREATE TRIGGER IF NOT EXISTS preregistration_locks_no_update
BEFORE UPDATE ON preregistration_locks BEGIN
    SELECT RAISE(ABORT, 'preregistration locks are immutable');
END;
CREATE TRIGGER IF NOT EXISTS preregistration_locks_no_delete
BEFORE DELETE ON preregistration_locks BEGIN
    SELECT RAISE(ABORT, 'preregistration locks are immutable');
END;
CREATE TRIGGER IF NOT EXISTS exposure_records_no_update
BEFORE UPDATE ON exposure_records BEGIN
    SELECT RAISE(ABORT, 'exposure records are append-only');
END;
CREATE TRIGGER IF NOT EXISTS exposure_records_no_delete
BEFORE DELETE ON exposure_records BEGIN
    SELECT RAISE(ABORT, 'exposure records are append-only');
END;
CREATE TRIGGER IF NOT EXISTS preregistration_audit_chain_no_update
BEFORE UPDATE ON preregistration_audit_chain BEGIN
    SELECT RAISE(ABORT, 'preregistration audit chain is append-only');
END;
CREATE TRIGGER IF NOT EXISTS preregistration_audit_chain_no_delete
BEFORE DELETE ON preregistration_audit_chain BEGIN
    SELECT RAISE(ABORT, 'preregistration audit chain is append-only');
END;
CREATE TRIGGER IF NOT EXISTS preregistration_command_keys_no_update
BEFORE UPDATE ON preregistration_command_keys BEGIN
    SELECT RAISE(ABORT, 'idempotency records are append-only');
END;
CREATE TRIGGER IF NOT EXISTS preregistration_command_keys_no_delete
BEFORE DELETE ON preregistration_command_keys BEGIN
    SELECT RAISE(ABORT, 'idempotency records are append-only');
END;
CREATE TRIGGER IF NOT EXISTS preregistration_no_version_after_lock
BEFORE INSERT ON artifact_versions
WHEN EXISTS (
    SELECT 1 FROM preregistration_locks locks
    WHERE locks.preregistration_id = NEW.artifact_id
)
BEGIN
    SELECT RAISE(ABORT, 'locked preregistration cannot acquire new versions');
END;
""",
    ),
)
