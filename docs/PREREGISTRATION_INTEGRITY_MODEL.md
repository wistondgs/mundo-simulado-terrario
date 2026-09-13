# Preregistration integrity model

## Canonicalization and hashing

The architecture is `canonical component -> SHA-256 component hash -> manifest/index -> bundle root`. Ten ordered canonical components are serialized with `terrario-canonical-json-v1` (UTF-8, sorted keys, deterministic compact separators, `allow_nan=False` so non-finite numbers are rejected) and written to the SHA-256 CAS. Their descriptors form a Merkle-style root manifest; this is hash composition over a canonical profile, not a claim of a general Merkle tree or a public cryptographic signature. No custom cryptography is introduced.

The ten ordered component roles are: scientific question, causal design, protocol, metrics and endpoints, Observer, seeds/partitions/randomization/replication, analysis, policies, environment and software, validation policy. Each component receives a content SHA-256 and a CAS SHA-256. The ordered root manifest pins source version/hash pairs, the canonicalization profile, and the explicit `scientific_execution: false` / `evidence_publication: false` boundaries; its canonical SHA-256 is the bundle root.

The required hash properties hold: same scientific state -> same root; a scientific delta -> a different root; a UI-only delta -> the same root; a tampered component -> verification FAIL; a missing component -> verification FAIL.

## Structured verifier

`verify_preregistration` returns a structured report, not a boolean. It checks schema validity, the exact component role set and order, the DB component index against the manifest, component hashes, CAS object existence and integrity, the bundle root, the review-package hash, the exact `ExperimentDraft`/`TrialMatrix` references, parent hashes and cycle detection, the audit hash chain, the review decision / lock / attestation binding, the terminal immutable state, and referenced-artifact availability. It reports per-field booleans (`schema_valid`, `component_hashes_valid`, `root_hash_valid`, `cas_valid`, `review_binding_valid`, `immutable_status_valid`, `audit_chain_valid`, `parent_chain_valid`, `referenced_artifacts_valid`) plus `failures` and `warnings` lists, distinguishing PASS / FAIL / WARNING / UNAVAILABLE / NOT_APPLICABLE where applicable.

## Trust boundaries and immutability

Locks, attestations, review decisions, warning acceptances, components, audit events, exposures, and artifact versions are append-only under SQLite triggers; direct UPDATE/DELETE at the SQL layer raises `IntegrityError`. The local attestation is deliberately labelled `UNSIGNED_LOCAL_ATTESTATION`: its trust boundary is the local database/CAS and the human session, not external identity proof. Immutability is enforced at four layers — domain (frozen dataclasses), repository (state machine + transaction), API (no mutation route for locked records, forbidden client governance fields), and SQL (triggers).

## Portability

Portable export contains all preregistration versions, exact referenced artifacts, the root and component CAS payloads, the review package, the audit lineage, and the external attestation. Import preserves exact immutable version IDs and rejects conflicts; it never rewrites an identity to make a bundle pass. External attestations never become local approval: an imported bundle requires an independent local review before any local lock.
