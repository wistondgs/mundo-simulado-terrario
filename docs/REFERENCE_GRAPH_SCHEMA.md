# Reference graph schema

`terrario.lab.reference-graph/v1` is a durable, append-only, versioned schema for scientific references. Domain types live in `terrario/lab/referencegraph/domain.py`; SQL access lives in `terrario/lab/referencegraph/repository.py`; persistence is migration 3 (`scientific_reference_graph`) in `terrario/lab/persistence/migrations.py`.

## Tables

- `ref_documents` — `document_id` (= SHA-256 of bytes = CAS blob hash, PK), `cas_blob_hash` FK→`blob_manifests`, media type, size, `version_type`, `status`, `effective_at`, `recorded_at`.
- `ref_authors`, `ref_venues` — normalized-name unique.
- `ref_bibliographic` — `biblio_id` PK, title, `normalized_title`, `authors_json`, year, `venue_id` FK, edition, `doi`, `identity_hash` UNIQUE.
- `ref_references` — `reference_id` PK, `biblio_id` FK, `primary_document_id` FK (nullable), `reference_type`, `status`, `d_level_tags_json`, `constructs_json`, `experimental_paradigms_json`, `discipline`, `code_url`, `verification_status`, `recorded_at`.
- `ref_document_versions` — explicit `VERSION_OF` / `SUPERSEDES_DOCUMENT_VERSION` / `CORRECTS` / `SUPPLEMENTS` relations.
- `ref_claims` — claim text, normalized summary, `claim_type`, `epistemic_source`, `extraction_method`, `verification_status`, `locator_json`, context.
- `ref_nodes`, `ref_edges` — typed graph with `node_hash` / `edge_hash` UNIQUE and per-edge provenance.
- `ref_snapshots` — `snapshot_id` PK, `parent_snapshot_id` FK, schema version, `node_set_hash`, `edge_set_hash`, `root_hash` UNIQUE, counts, provenance, `created_at`.
- `ref_import_batches`, `ref_import_records` — ImportPlan + per-record action.
- `ref_quarantine` — reason, source, batch, payload, resolution state.
- `ref_duplicates` — candidate pair, detection method, status.
- `ref_verifications` — structured verifier reports.
- `ref_claims_fts` — FTS5 over authorized claim text/summary only.

## Closed enums

`DocumentVersionType` (9 values), `DocumentStatus` (5), `ClaimType` (5), `ProvenanceLevel` (7), `VerificationStatus` (5), `NodeType` (17), `EdgeType` (22), `DuplicateStatus` (5), `RelevanceKind` (4), `ConflictKind` (3), `QuarantineReason` (8), `ResolutionState` (4), `ImportAction` (5). Unknown enum values are rejected at the domain boundary.

## Immutability

All scientific tables are append-only via SQLite triggers (`BEFORE UPDATE` / `BEFORE DELETE` abort). Snapshots, nodes, edges, claims, documents, bibliographic records, references, quarantine, and import records cannot be mutated or deleted. Corrections and retractions are recorded as new append-only records with bitemporal timestamps (`recorded_at`, and `effective_at` where applicable); history is never rewritten.

## Indexes

Real indexes exist for DOI, normalized title, author, year, node type, edge type, edge source/target, reference status, claim status, snapshot parent, quarantine state, and bibliographic identity hash. Normal lookups do not perform full scans.
