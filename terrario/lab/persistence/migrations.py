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
    Migration(
        3,
        "scientific_reference_graph",
        r"""
CREATE TABLE IF NOT EXISTS ref_documents (
    document_id TEXT PRIMARY KEY CHECK (length(document_id) = 64),
    cas_blob_hash TEXT NOT NULL REFERENCES blob_manifests(blob_hash),
    media_type TEXT NOT NULL,
    size_bytes INTEGER NOT NULL CHECK (size_bytes >= 0),
    version_type TEXT NOT NULL,
    status TEXT NOT NULL,
    effective_at TEXT,
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ref_authors (
    author_id TEXT PRIMARY KEY,
    display_name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    UNIQUE (normalized_name)
);
CREATE INDEX IF NOT EXISTS ref_authors_name_idx ON ref_authors(normalized_name);

CREATE TABLE IF NOT EXISTS ref_venues (
    venue_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    normalized_name TEXT NOT NULL,
    venue_type TEXT NOT NULL,
    recorded_at TEXT NOT NULL,
    UNIQUE (normalized_name)
);

CREATE TABLE IF NOT EXISTS ref_bibliographic (
    biblio_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    normalized_title TEXT NOT NULL,
    authors_json TEXT NOT NULL,
    year TEXT NOT NULL,
    venue_id TEXT REFERENCES ref_venues(venue_id),
    edition TEXT,
    doi TEXT,
    identity_hash TEXT NOT NULL UNIQUE CHECK (length(identity_hash) = 64),
    recorded_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ref_bibliographic_doi_idx ON ref_bibliographic(doi);
CREATE INDEX IF NOT EXISTS ref_bibliographic_title_idx ON ref_bibliographic(normalized_title);
CREATE INDEX IF NOT EXISTS ref_bibliographic_year_idx ON ref_bibliographic(year);

CREATE TABLE IF NOT EXISTS ref_references (
    reference_id TEXT PRIMARY KEY,
    biblio_id TEXT NOT NULL REFERENCES ref_bibliographic(biblio_id),
    primary_document_id TEXT REFERENCES ref_documents(document_id),
    reference_type TEXT NOT NULL,
    status TEXT NOT NULL,
    d_level_tags_json TEXT NOT NULL,
    constructs_json TEXT NOT NULL,
    experimental_paradigms_json TEXT NOT NULL,
    discipline TEXT NOT NULL,
    code_url TEXT,
    verification_status TEXT NOT NULL,
    recorded_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ref_references_biblio_idx ON ref_references(biblio_id);
CREATE INDEX IF NOT EXISTS ref_references_status_idx ON ref_references(verification_status);

CREATE TABLE IF NOT EXISTS ref_document_versions (
    version_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES ref_documents(document_id),
    biblio_id TEXT NOT NULL REFERENCES ref_bibliographic(biblio_id),
    version_type TEXT NOT NULL,
    relation TEXT,
    relation_target_document_id TEXT REFERENCES ref_documents(document_id),
    recorded_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ref_document_versions_doc_idx ON ref_document_versions(document_id);
CREATE INDEX IF NOT EXISTS ref_document_versions_biblio_idx ON ref_document_versions(biblio_id);

CREATE TABLE IF NOT EXISTS ref_claims (
    claim_id TEXT PRIMARY KEY,
    reference_id TEXT NOT NULL REFERENCES ref_references(reference_id),
    document_id TEXT REFERENCES ref_documents(document_id),
    claim_text TEXT NOT NULL,
    normalized_summary TEXT NOT NULL,
    claim_type TEXT NOT NULL,
    epistemic_source TEXT NOT NULL,
    extraction_method TEXT NOT NULL,
    verification_status TEXT NOT NULL,
    locator_json TEXT NOT NULL,
    context TEXT NOT NULL,
    recorded_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ref_claims_reference_idx ON ref_claims(reference_id);
CREATE INDEX IF NOT EXISTS ref_claims_status_idx ON ref_claims(verification_status);

CREATE TABLE IF NOT EXISTS ref_nodes (
    node_id TEXT PRIMARY KEY,
    node_type TEXT NOT NULL,
    reference_id TEXT REFERENCES ref_references(reference_id),
    payload_json TEXT NOT NULL,
    node_hash TEXT NOT NULL UNIQUE CHECK (length(node_hash) = 64),
    recorded_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ref_nodes_type_idx ON ref_nodes(node_type);
CREATE INDEX IF NOT EXISTS ref_nodes_reference_idx ON ref_nodes(reference_id);

CREATE TABLE IF NOT EXISTS ref_edges (
    edge_id TEXT PRIMARY KEY,
    edge_type TEXT NOT NULL,
    source_node_id TEXT NOT NULL REFERENCES ref_nodes(node_id),
    target_node_id TEXT NOT NULL REFERENCES ref_nodes(node_id),
    provenance_level TEXT NOT NULL,
    provenance_detail TEXT NOT NULL,
    edge_hash TEXT NOT NULL UNIQUE CHECK (length(edge_hash) = 64),
    recorded_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ref_edges_type_idx ON ref_edges(edge_type);
CREATE INDEX IF NOT EXISTS ref_edges_source_idx ON ref_edges(source_node_id);
CREATE INDEX IF NOT EXISTS ref_edges_target_idx ON ref_edges(target_node_id);

CREATE TABLE IF NOT EXISTS ref_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    parent_snapshot_id TEXT REFERENCES ref_snapshots(snapshot_id),
    schema_version TEXT NOT NULL,
    node_set_hash TEXT NOT NULL CHECK (length(node_set_hash) = 64),
    edge_set_hash TEXT NOT NULL CHECK (length(edge_set_hash) = 64),
    root_hash TEXT NOT NULL UNIQUE CHECK (length(root_hash) = 64),
    node_count INTEGER NOT NULL CHECK (node_count >= 0),
    edge_count INTEGER NOT NULL CHECK (edge_count >= 0),
    provenance TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ref_snapshots_parent_idx ON ref_snapshots(parent_snapshot_id);

CREATE TABLE IF NOT EXISTS ref_import_batches (
    batch_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    plan_json TEXT NOT NULL,
    plan_hash TEXT NOT NULL CHECK (length(plan_hash) = 64),
    snapshot_id TEXT REFERENCES ref_snapshots(snapshot_id),
    state TEXT NOT NULL,
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ref_import_records (
    import_record_id TEXT PRIMARY KEY,
    batch_id TEXT NOT NULL REFERENCES ref_import_batches(batch_id),
    external_id TEXT NOT NULL,
    action TEXT NOT NULL,
    detail TEXT NOT NULL,
    recorded_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ref_import_records_batch_idx ON ref_import_records(batch_id);

CREATE TABLE IF NOT EXISTS ref_quarantine (
    quarantine_id TEXT PRIMARY KEY,
    reason TEXT NOT NULL,
    source TEXT NOT NULL,
    batch_id TEXT REFERENCES ref_import_batches(batch_id),
    payload_json TEXT NOT NULL,
    resolution_state TEXT NOT NULL,
    recorded_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ref_quarantine_state_idx ON ref_quarantine(resolution_state);

CREATE TABLE IF NOT EXISTS ref_duplicates (
    duplicate_id TEXT PRIMARY KEY,
    left_reference_id TEXT NOT NULL,
    right_reference_id TEXT NOT NULL,
    detection_method TEXT NOT NULL,
    status TEXT NOT NULL,
    recorded_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS ref_verifications (
    verification_id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL,
    report_json TEXT NOT NULL,
    recorded_at TEXT NOT NULL
);

CREATE VIRTUAL TABLE IF NOT EXISTS ref_claims_fts USING fts5(
    claim_id UNINDEXED,
    claim_text,
    normalized_summary
);

CREATE TRIGGER IF NOT EXISTS ref_documents_no_update
BEFORE UPDATE ON ref_documents BEGIN
    SELECT RAISE(ABORT, 'reference documents are append-only');
END;
CREATE TRIGGER IF NOT EXISTS ref_documents_no_delete
BEFORE DELETE ON ref_documents BEGIN
    SELECT RAISE(ABORT, 'reference documents are append-only');
END;
CREATE TRIGGER IF NOT EXISTS ref_bibliographic_no_update
BEFORE UPDATE ON ref_bibliographic BEGIN
    SELECT RAISE(ABORT, 'bibliographic records are append-only');
END;
CREATE TRIGGER IF NOT EXISTS ref_bibliographic_no_delete
BEFORE DELETE ON ref_bibliographic BEGIN
    SELECT RAISE(ABORT, 'bibliographic records are append-only');
END;
CREATE TRIGGER IF NOT EXISTS ref_references_no_update
BEFORE UPDATE ON ref_references BEGIN
    SELECT RAISE(ABORT, 'reference records are append-only');
END;
CREATE TRIGGER IF NOT EXISTS ref_references_no_delete
BEFORE DELETE ON ref_references BEGIN
    SELECT RAISE(ABORT, 'reference records are append-only');
END;
CREATE TRIGGER IF NOT EXISTS ref_claims_no_update
BEFORE UPDATE ON ref_claims BEGIN
    SELECT RAISE(ABORT, 'source claims are append-only');
END;
CREATE TRIGGER IF NOT EXISTS ref_claims_no_delete
BEFORE DELETE ON ref_claims BEGIN
    SELECT RAISE(ABORT, 'source claims are append-only');
END;
CREATE TRIGGER IF NOT EXISTS ref_nodes_no_update
BEFORE UPDATE ON ref_nodes BEGIN
    SELECT RAISE(ABORT, 'reference graph nodes are append-only');
END;
CREATE TRIGGER IF NOT EXISTS ref_nodes_no_delete
BEFORE DELETE ON ref_nodes BEGIN
    SELECT RAISE(ABORT, 'reference graph nodes are append-only');
END;
CREATE TRIGGER IF NOT EXISTS ref_edges_no_update
BEFORE UPDATE ON ref_edges BEGIN
    SELECT RAISE(ABORT, 'reference graph edges are append-only');
END;
CREATE TRIGGER IF NOT EXISTS ref_edges_no_delete
BEFORE DELETE ON ref_edges BEGIN
    SELECT RAISE(ABORT, 'reference graph edges are append-only');
END;
CREATE TRIGGER IF NOT EXISTS ref_snapshots_no_update
BEFORE UPDATE ON ref_snapshots BEGIN
    SELECT RAISE(ABORT, 'reference graph snapshots are append-only');
END;
CREATE TRIGGER IF NOT EXISTS ref_snapshots_no_delete
BEFORE DELETE ON ref_snapshots BEGIN
    SELECT RAISE(ABORT, 'reference graph snapshots are append-only');
END;
CREATE TRIGGER IF NOT EXISTS ref_quarantine_no_update
BEFORE UPDATE ON ref_quarantine BEGIN
    SELECT RAISE(ABORT, 'quarantine records are append-only');
END;
CREATE TRIGGER IF NOT EXISTS ref_quarantine_no_delete
BEFORE DELETE ON ref_quarantine BEGIN
    SELECT RAISE(ABORT, 'quarantine records are append-only');
END;
""",
    ),
    Migration(
        4,
        "reference_graph_term_indexes",
        r"""
CREATE TABLE IF NOT EXISTS ref_constructs (
    reference_id TEXT NOT NULL REFERENCES ref_references(reference_id),
    construct TEXT NOT NULL,
    UNIQUE (reference_id, construct)
);
CREATE INDEX IF NOT EXISTS ref_constructs_term_idx ON ref_constructs(construct);
CREATE INDEX IF NOT EXISTS ref_constructs_ref_idx ON ref_constructs(reference_id);

CREATE TABLE IF NOT EXISTS ref_paradigms (
    reference_id TEXT NOT NULL REFERENCES ref_references(reference_id),
    paradigm TEXT NOT NULL,
    UNIQUE (reference_id, paradigm)
);
CREATE INDEX IF NOT EXISTS ref_paradigms_term_idx ON ref_paradigms(paradigm);
CREATE INDEX IF NOT EXISTS ref_paradigms_ref_idx ON ref_paradigms(reference_id);

CREATE TRIGGER IF NOT EXISTS ref_constructs_no_update
BEFORE UPDATE ON ref_constructs BEGIN
    SELECT RAISE(ABORT, 'construct index is append-only');
END;
CREATE TRIGGER IF NOT EXISTS ref_constructs_no_delete
BEFORE DELETE ON ref_constructs BEGIN
    SELECT RAISE(ABORT, 'construct index is append-only');
END;
CREATE TRIGGER IF NOT EXISTS ref_paradigms_no_update
BEFORE UPDATE ON ref_paradigms BEGIN
    SELECT RAISE(ABORT, 'paradigm index is append-only');
END;
CREATE TRIGGER IF NOT EXISTS ref_paradigms_no_delete
BEFORE DELETE ON ref_paradigms BEGIN
    SELECT RAISE(ABORT, 'paradigm index is append-only');
END;
""",
    ),
    Migration(
        5,
        "scientific_cross_graph",
        r"""
CREATE TABLE IF NOT EXISTS cross_links (
    link_id TEXT PRIMARY KEY,
    source_ref_json TEXT NOT NULL,
    target_ref_json TEXT NOT NULL,
    source_key TEXT NOT NULL,
    target_key TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    assertion_class TEXT NOT NULL,
    state TEXT NOT NULL,
    provenance TEXT NOT NULL,
    rule_id TEXT,
    rule_version TEXT,
    supersedes_link_id TEXT REFERENCES cross_links(link_id),
    link_hash TEXT NOT NULL UNIQUE CHECK (length(link_hash) = 64),
    effective_at TEXT,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS cross_links_source_idx ON cross_links(source_key);
CREATE INDEX IF NOT EXISTS cross_links_target_idx ON cross_links(target_key);
CREATE INDEX IF NOT EXISTS cross_links_relation_idx ON cross_links(relation_type);
CREATE INDEX IF NOT EXISTS cross_links_state_idx ON cross_links(state);

CREATE TABLE IF NOT EXISTS cross_hyperlinks (
    hyperlink_id TEXT PRIMARY KEY,
    members_json TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    assertion_class TEXT NOT NULL,
    state TEXT NOT NULL,
    provenance TEXT NOT NULL,
    link_hash TEXT NOT NULL UNIQUE CHECK (length(link_hash) = 64),
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS cross_hyperlinks_state_idx ON cross_hyperlinks(state);

CREATE TABLE IF NOT EXISTS cross_federation_manifests (
    manifest_id TEXT PRIMARY KEY,
    domain_snapshots_json TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    manifest_hash TEXT NOT NULL UNIQUE CHECK (length(manifest_hash) = 64),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cross_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    parent_snapshot_id TEXT REFERENCES cross_snapshots(snapshot_id),
    federation_manifest_hash TEXT NOT NULL CHECK (length(federation_manifest_hash) = 64),
    cross_link_set_hash TEXT NOT NULL CHECK (length(cross_link_set_hash) = 64),
    root_hash TEXT NOT NULL UNIQUE CHECK (length(root_hash) = 64),
    link_count INTEGER NOT NULL CHECK (link_count >= 0),
    hyperlink_count INTEGER NOT NULL CHECK (hyperlink_count >= 0),
    actor TEXT NOT NULL,
    provenance TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS cross_snapshots_parent_idx ON cross_snapshots(parent_snapshot_id);

CREATE TABLE IF NOT EXISTS cross_trace_breaks (
    trace_break_id TEXT PRIMARY KEY,
    from_ref_json TEXT NOT NULL,
    expected_next_domain TEXT NOT NULL,
    reason TEXT NOT NULL,
    missing_identity_or_relation TEXT NOT NULL,
    resolution_state TEXT NOT NULL,
    discovered_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cross_compositions (
    rowid INTEGER PRIMARY KEY AUTOINCREMENT,
    composition_id TEXT NOT NULL,
    title TEXT NOT NULL,
    refs_json TEXT NOT NULL,
    local_links_json TEXT NOT NULL,
    notes TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    parent_composition_id TEXT,
    created_at TEXT NOT NULL,
    created_by TEXT NOT NULL,
    UNIQUE (composition_id, version)
);

CREATE TABLE IF NOT EXISTS cross_verifications (
    verification_id TEXT PRIMARY KEY,
    subject_id TEXT NOT NULL,
    report_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TRIGGER IF NOT EXISTS cross_links_no_update
BEFORE UPDATE ON cross_links BEGIN
    SELECT RAISE(ABORT, 'cross links are append-only');
END;
CREATE TRIGGER IF NOT EXISTS cross_links_no_delete
BEFORE DELETE ON cross_links BEGIN
    SELECT RAISE(ABORT, 'cross links are append-only');
END;
CREATE TRIGGER IF NOT EXISTS cross_hyperlinks_no_update
BEFORE UPDATE ON cross_hyperlinks BEGIN
    SELECT RAISE(ABORT, 'cross hyperlinks are append-only');
END;
CREATE TRIGGER IF NOT EXISTS cross_hyperlinks_no_delete
BEFORE DELETE ON cross_hyperlinks BEGIN
    SELECT RAISE(ABORT, 'cross hyperlinks are append-only');
END;
CREATE TRIGGER IF NOT EXISTS cross_snapshots_no_update
BEFORE UPDATE ON cross_snapshots BEGIN
    SELECT RAISE(ABORT, 'cross graph snapshots are append-only');
END;
CREATE TRIGGER IF NOT EXISTS cross_snapshots_no_delete
BEFORE DELETE ON cross_snapshots BEGIN
    SELECT RAISE(ABORT, 'cross graph snapshots are append-only');
END;
CREATE TRIGGER IF NOT EXISTS cross_federation_manifests_no_update
BEFORE UPDATE ON cross_federation_manifests BEGIN
    SELECT RAISE(ABORT, 'federation manifests are append-only');
END;
CREATE TRIGGER IF NOT EXISTS cross_federation_manifests_no_delete
BEFORE DELETE ON cross_federation_manifests BEGIN
    SELECT RAISE(ABORT, 'federation manifests are append-only');
END;
CREATE TRIGGER IF NOT EXISTS cross_trace_breaks_no_update
BEFORE UPDATE ON cross_trace_breaks BEGIN
    SELECT RAISE(ABORT, 'trace breaks are append-only');
END;
CREATE TRIGGER IF NOT EXISTS cross_trace_breaks_no_delete
BEFORE DELETE ON cross_trace_breaks BEGIN
    SELECT RAISE(ABORT, 'trace breaks are append-only');
END;
""",
    ),
    Migration(
        6,
        "cross_graph_materialized_adjacency",
        r"""
-- Derived, non-authoritative adjacency index for interactive traversal.
-- This table is a rebuildable cache: it is never a source of truth, may be
-- discarded and rebuilt from cross_links, and is invalidated whenever the
-- canonical link set changes. It intentionally has no append-only triggers.
CREATE TABLE IF NOT EXISTS cross_adjacency_index (
    link_id TEXT PRIMARY KEY,
    source_key TEXT NOT NULL,
    target_key TEXT NOT NULL,
    relation_type TEXT NOT NULL,
    source_domain TEXT NOT NULL,
    target_domain TEXT NOT NULL,
    source_entity_type TEXT NOT NULL,
    target_entity_type TEXT NOT NULL,
    link_hash TEXT NOT NULL CHECK (length(link_hash) = 64)
);
CREATE INDEX IF NOT EXISTS cross_adj_outbound_idx ON cross_adjacency_index(source_key);
CREATE INDEX IF NOT EXISTS cross_adj_inbound_idx ON cross_adjacency_index(target_key);
CREATE INDEX IF NOT EXISTS cross_adj_relation_idx ON cross_adjacency_index(relation_type);
CREATE INDEX IF NOT EXISTS cross_adj_source_domain_idx ON cross_adjacency_index(source_domain);
CREATE INDEX IF NOT EXISTS cross_adj_target_domain_idx ON cross_adjacency_index(target_domain);

-- Tracks which canonical link-set the derived index was built from, so a stale
-- or corrupt index can be detected and discarded.
CREATE TABLE IF NOT EXISTS cross_adjacency_meta (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    built_from_link_set_hash TEXT NOT NULL CHECK (length(built_from_link_set_hash) = 64),
    link_count INTEGER NOT NULL,
    built_at TEXT NOT NULL
);
""",
    ),
    Migration(
        7,
        "scientific_execution_gate_01",
        r"""
-- Scientific execution is deliberately separate from preregistration, sandbox,
-- evidence, and theory tables.  These rows are the authoritative execution
-- ledger; derived status can always be rebuilt from execution_events.
CREATE TABLE IF NOT EXISTS scientific_execution_authorizations (
    authorization_id TEXT PRIMARY KEY,
    preregistration_root_hash TEXT NOT NULL CHECK(length(preregistration_root_hash)=64),
    authorization_hash TEXT NOT NULL UNIQUE CHECK(length(authorization_hash)=64),
    actor_id TEXT NOT NULL,
    scope_type TEXT NOT NULL CHECK(scope_type IN ('ONE_EXECUTION','N_EXECUTIONS','REPLICATION_SERIES','UNTIL_EXPIRY')),
    max_execution_count INTEGER NOT NULL CHECK(max_execution_count > 0),
    consumed_execution_count INTEGER NOT NULL DEFAULT 0 CHECK(consumed_execution_count >= 0),
    replication_group_id TEXT,
    expires_at TEXT,
    resource_ceiling_json TEXT NOT NULL,
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL,
    CHECK(consumed_execution_count <= max_execution_count),
    CHECK((scope_type != 'REPLICATION_SERIES') OR replication_group_id IS NOT NULL),
    CHECK((scope_type != 'UNTIL_EXPIRY') OR expires_at IS NOT NULL)
);

CREATE TABLE IF NOT EXISTS scientific_execution_authorization_events (
    event_id TEXT PRIMARY KEY,
    authorization_id TEXT NOT NULL REFERENCES scientific_execution_authorizations(authorization_id),
    event_type TEXT NOT NULL CHECK(event_type IN ('CREATED','CONSUMED','REVOKED')),
    payload_json TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scientific_executions (
    execution_id TEXT PRIMARY KEY,
    preregistration_id TEXT NOT NULL REFERENCES artifacts(artifact_id),
    preregistration_root_hash TEXT NOT NULL CHECK(length(preregistration_root_hash)=64),
    authorization_id TEXT REFERENCES scientific_execution_authorizations(authorization_id),
    plan_hash TEXT UNIQUE CHECK(plan_hash IS NULL OR length(plan_hash)=64),
    execution_root_hash TEXT UNIQUE CHECK(execution_root_hash IS NULL OR length(execution_root_hash)=64),
    artifact_root_hash TEXT CHECK(artifact_root_hash IS NULL OR length(artifact_root_hash)=64),
    state TEXT NOT NULL,
    revision INTEGER NOT NULL DEFAULT 0 CHECK(revision >= 0),
    environment_snapshot_json TEXT,
    software_snapshot_json TEXT,
    readiness_json TEXT,
    plan_json TEXT,
    authorization_consumed INTEGER NOT NULL DEFAULT 0 CHECK(authorization_consumed IN (0,1)),
    lease_owner TEXT,
    lease_expires_at TEXT,
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL,
    completed_at TEXT
);
CREATE INDEX IF NOT EXISTS scientific_executions_root_idx ON scientific_executions(preregistration_root_hash, created_at);

CREATE TABLE IF NOT EXISTS scientific_execution_events (
    event_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL REFERENCES scientific_executions(execution_id),
    sequence INTEGER NOT NULL CHECK(sequence > 0),
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    previous_event_hash TEXT,
    event_hash TEXT NOT NULL UNIQUE CHECK(length(event_hash)=64),
    actor_id TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(execution_id, sequence)
);

CREATE TABLE IF NOT EXISTS scientific_execution_commands (
    command_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL REFERENCES scientific_executions(execution_id),
    command_type TEXT NOT NULL,
    expected_revision INTEGER NOT NULL,
    response_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scientific_execution_deviations (
    deviation_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL REFERENCES scientific_executions(execution_id),
    deviation_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    actor_id TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scientific_execution_artifacts (
    artifact_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL REFERENCES scientific_executions(execution_id),
    trial_intent_id TEXT REFERENCES trial_intents(trial_intent_id),
    attempt_id TEXT REFERENCES run_attempts(attempt_id),
    artifact_type TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    blob_hash TEXT NOT NULL REFERENCES blob_manifests(blob_hash),
    size_bytes INTEGER NOT NULL CHECK(size_bytes >= 0),
    descriptor_hash TEXT NOT NULL UNIQUE CHECK(length(descriptor_hash)=64),
    created_at TEXT NOT NULL,
    UNIQUE(execution_id, attempt_id, artifact_type, blob_hash)
);

CREATE TABLE IF NOT EXISTS scientific_execution_checkpoints (
    checkpoint_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL REFERENCES scientific_executions(execution_id),
    attempt_id TEXT REFERENCES run_attempts(attempt_id),
    checkpoint_class TEXT NOT NULL CHECK(checkpoint_class IN ('RESTORABLE_EXACT','OBSERVABILITY_ONLY','TRIAL_BOUNDARY')),
    blob_hash TEXT NOT NULL REFERENCES blob_manifests(blob_hash),
    manifest_hash TEXT NOT NULL CHECK(length(manifest_hash)=64),
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS scientific_execution_verifications (
    verification_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL REFERENCES scientific_executions(execution_id),
    report_hash TEXT NOT NULL UNIQUE CHECK(length(report_hash)=64),
    report_json TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TRIGGER IF NOT EXISTS scientific_execution_authorizations_no_delete
BEFORE DELETE ON scientific_execution_authorizations BEGIN SELECT RAISE(ABORT, 'execution authorization is immutable'); END;
CREATE TRIGGER IF NOT EXISTS scientific_execution_authorization_events_no_update
BEFORE UPDATE ON scientific_execution_authorization_events BEGIN SELECT RAISE(ABORT, 'authorization event is append-only'); END;
CREATE TRIGGER IF NOT EXISTS scientific_execution_authorization_events_no_delete
BEFORE DELETE ON scientific_execution_authorization_events BEGIN SELECT RAISE(ABORT, 'authorization event is append-only'); END;
CREATE TRIGGER IF NOT EXISTS scientific_execution_events_no_update
BEFORE UPDATE ON scientific_execution_events BEGIN SELECT RAISE(ABORT, 'execution event is append-only'); END;
CREATE TRIGGER IF NOT EXISTS scientific_execution_events_no_delete
BEFORE DELETE ON scientific_execution_events BEGIN SELECT RAISE(ABORT, 'execution event is append-only'); END;
CREATE TRIGGER IF NOT EXISTS scientific_execution_commands_no_update
BEFORE UPDATE ON scientific_execution_commands BEGIN SELECT RAISE(ABORT, 'execution command is immutable'); END;
CREATE TRIGGER IF NOT EXISTS scientific_execution_commands_no_delete
BEFORE DELETE ON scientific_execution_commands BEGIN SELECT RAISE(ABORT, 'execution command is immutable'); END;
CREATE TRIGGER IF NOT EXISTS scientific_execution_deviations_no_update
BEFORE UPDATE ON scientific_execution_deviations BEGIN SELECT RAISE(ABORT, 'execution deviation is append-only'); END;
CREATE TRIGGER IF NOT EXISTS scientific_execution_deviations_no_delete
BEFORE DELETE ON scientific_execution_deviations BEGIN SELECT RAISE(ABORT, 'execution deviation is append-only'); END;
CREATE TRIGGER IF NOT EXISTS scientific_execution_artifacts_no_update
BEFORE UPDATE ON scientific_execution_artifacts BEGIN SELECT RAISE(ABORT, 'execution artifact is immutable'); END;
CREATE TRIGGER IF NOT EXISTS scientific_execution_artifacts_no_delete
BEFORE DELETE ON scientific_execution_artifacts BEGIN SELECT RAISE(ABORT, 'execution artifact is immutable'); END;
CREATE TRIGGER IF NOT EXISTS scientific_execution_checkpoints_no_update
BEFORE UPDATE ON scientific_execution_checkpoints BEGIN SELECT RAISE(ABORT, 'execution checkpoint is immutable'); END;
CREATE TRIGGER IF NOT EXISTS scientific_execution_checkpoints_no_delete
BEFORE DELETE ON scientific_execution_checkpoints BEGIN SELECT RAISE(ABORT, 'execution checkpoint is immutable'); END;
CREATE TRIGGER IF NOT EXISTS scientific_execution_verifications_no_update
BEFORE UPDATE ON scientific_execution_verifications BEGIN SELECT RAISE(ABORT, 'execution verification is immutable'); END;
CREATE TRIGGER IF NOT EXISTS scientific_execution_verifications_no_delete
BEFORE DELETE ON scientific_execution_verifications BEGIN SELECT RAISE(ABORT, 'execution verification is immutable'); END;
""",
    ),
    Migration(
        8,
        "causal_intervention_fork_core",
        r"""
CREATE TABLE IF NOT EXISTS causal_snapshots (
    snapshot_id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL,
    trial_intent_id TEXT NOT NULL,
    attempt_id TEXT NOT NULL,
    snapshot_hash TEXT NOT NULL UNIQUE CHECK(length(snapshot_hash)=64),
    blob_hash TEXT NOT NULL REFERENCES blob_manifests(blob_hash),
    schema_version TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS causal_forks (
    fork_id TEXT PRIMARY KEY,
    parent_snapshot_id TEXT NOT NULL REFERENCES causal_snapshots(snapshot_id),
    parent_execution_id TEXT NOT NULL,
    parent_trial_intent_id TEXT NOT NULL,
    parent_attempt_id TEXT NOT NULL,
    identity_hash TEXT NOT NULL UNIQUE CHECK(length(identity_hash)=64),
    shared_history_hash TEXT NOT NULL CHECK(length(shared_history_hash)=64),
    intervention_spec_hash TEXT NOT NULL CHECK(length(intervention_spec_hash)=64),
    state TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS causal_fork_events (
    event_id TEXT PRIMARY KEY,
    fork_id TEXT NOT NULL REFERENCES causal_forks(fork_id),
    sequence INTEGER NOT NULL CHECK(sequence > 0),
    event_type TEXT NOT NULL,
    payload_json TEXT NOT NULL,
    event_hash TEXT NOT NULL UNIQUE CHECK(length(event_hash)=64),
    created_at TEXT NOT NULL,
    UNIQUE(fork_id, sequence)
);
CREATE TABLE IF NOT EXISTS causal_branch_bindings (
    branch_id TEXT PRIMARY KEY,
    fork_id TEXT NOT NULL REFERENCES causal_forks(fork_id),
    role TEXT NOT NULL CHECK(role IN ('CONTROL','INTERVENTION')),
    artifact_blob_hash TEXT REFERENCES blob_manifests(blob_hash),
    trace_hash TEXT,
    UNIQUE(fork_id, role)
);
CREATE TRIGGER IF NOT EXISTS causal_snapshots_no_update BEFORE UPDATE ON causal_snapshots BEGIN SELECT RAISE(ABORT, 'causal snapshots are immutable'); END;
CREATE TRIGGER IF NOT EXISTS causal_snapshots_no_delete BEFORE DELETE ON causal_snapshots BEGIN SELECT RAISE(ABORT, 'causal snapshots are immutable'); END;
CREATE TRIGGER IF NOT EXISTS causal_fork_events_no_update BEFORE UPDATE ON causal_fork_events BEGIN SELECT RAISE(ABORT, 'causal fork events are append-only'); END;
CREATE TRIGGER IF NOT EXISTS causal_fork_events_no_delete BEFORE DELETE ON causal_fork_events BEGIN SELECT RAISE(ABORT, 'causal fork events are append-only'); END;
CREATE TRIGGER IF NOT EXISTS causal_branch_bindings_no_update BEFORE UPDATE ON causal_branch_bindings BEGIN SELECT RAISE(ABORT, 'causal branch bindings are immutable'); END;
CREATE TRIGGER IF NOT EXISTS causal_branch_bindings_no_delete BEFORE DELETE ON causal_branch_bindings BEGIN SELECT RAISE(ABORT, 'causal branch bindings are immutable'); END;
""",
    ),
    Migration(
        9,
        "empirical_result_publication_core",
        r"""
-- CL-7 owns an append-only empirical ledger.  It does not write to the
-- historical TheoryGraph/EvidenceGraph projection: those are read models.
CREATE TABLE IF NOT EXISTS scientific_results (
    result_id TEXT PRIMARY KEY,
    result_hash TEXT NOT NULL UNIQUE CHECK(length(result_hash)=64),
    execution_id TEXT NOT NULL REFERENCES scientific_executions(execution_id),
    trial_intent_id TEXT NOT NULL REFERENCES trial_intents(trial_intent_id),
    attempt_id TEXT NOT NULL REFERENCES run_attempts(attempt_id),
    preregistration_id TEXT NOT NULL REFERENCES artifacts(artifact_id),
    preregistration_root_hash TEXT NOT NULL CHECK(length(preregistration_root_hash)=64),
    execution_plan_hash TEXT NOT NULL CHECK(length(execution_plan_hash)=64),
    hypothesis_id TEXT NOT NULL,
    hypothesis_revision TEXT NOT NULL,
    metric_id TEXT NOT NULL,
    metric_version TEXT NOT NULL,
    metric_artifact_descriptor_hash TEXT NOT NULL REFERENCES scientific_execution_artifacts(descriptor_hash),
    trace_artifact_descriptor_hash TEXT NOT NULL REFERENCES scientific_execution_artifacts(descriptor_hash),
    envelope_json TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(attempt_id, metric_id, metric_version)
);

CREATE TABLE IF NOT EXISTS empirical_evidence (
    evidence_id TEXT PRIMARY KEY,
    evidence_hash TEXT NOT NULL UNIQUE CHECK(length(evidence_hash)=64),
    result_id TEXT NOT NULL UNIQUE REFERENCES scientific_results(result_id),
    hypothesis_id TEXT NOT NULL,
    hypothesis_revision TEXT NOT NULL,
    relation TEXT NOT NULL CHECK(relation IN ('EVIDENCE_FOR','EVIDENCE_AGAINST','UNRESOLVED')),
    qualification TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS empirical_evidence_links (
    link_id TEXT PRIMARY KEY,
    evidence_id TEXT NOT NULL REFERENCES empirical_evidence(evidence_id),
    source_kind TEXT NOT NULL,
    source_id TEXT NOT NULL,
    target_kind TEXT NOT NULL,
    target_id TEXT NOT NULL,
    relation TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE(evidence_id, source_kind, source_id, target_kind, target_id, relation)
);
CREATE INDEX IF NOT EXISTS empirical_evidence_hypothesis_idx ON empirical_evidence(hypothesis_id,hypothesis_revision);
CREATE INDEX IF NOT EXISTS empirical_evidence_links_target_idx ON empirical_evidence_links(target_kind,target_id);

CREATE TRIGGER IF NOT EXISTS scientific_results_no_update
BEFORE UPDATE ON scientific_results BEGIN SELECT RAISE(ABORT, 'scientific result is immutable'); END;
CREATE TRIGGER IF NOT EXISTS scientific_results_no_delete
BEFORE DELETE ON scientific_results BEGIN SELECT RAISE(ABORT, 'scientific result is immutable'); END;
CREATE TRIGGER IF NOT EXISTS empirical_evidence_no_update
BEFORE UPDATE ON empirical_evidence BEGIN SELECT RAISE(ABORT, 'empirical evidence is immutable'); END;
CREATE TRIGGER IF NOT EXISTS empirical_evidence_no_delete
BEFORE DELETE ON empirical_evidence BEGIN SELECT RAISE(ABORT, 'empirical evidence is immutable'); END;
CREATE TRIGGER IF NOT EXISTS empirical_evidence_links_no_update
BEFORE UPDATE ON empirical_evidence_links BEGIN SELECT RAISE(ABORT, 'empirical evidence link is immutable'); END;
CREATE TRIGGER IF NOT EXISTS empirical_evidence_links_no_delete
BEFORE DELETE ON empirical_evidence_links BEGIN SELECT RAISE(ABORT, 'empirical evidence link is immutable'); END;
""",
    ),
)
