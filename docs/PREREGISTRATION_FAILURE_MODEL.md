# Preregistration failure and recovery model

## Failure and exclusion policies

Preregistered failure classes include process crash, timeout, numerical error, corrupted artifact, invalid world, incomplete episode, hardware failure, and invalid trace. Allowlisted dispositions are `RETRY_SAME_SEED`, `EXCLUDE`, `REPLACE_WITH_PRECOMMITTED_SEED`, `COUNT_AS_FAILURE`, and `HUMAN_REVIEW_REQUIRED`. Stopping rules are `FIXED_TRIAL_COUNT`, `FIXED_SEED_SET`, `SEQUENTIAL_PREDEFINED`, `RESOURCE_BOUND`, and `EXTERNAL_TERMINATION_ONLY`. A different post-lock choice is recorded as a typed `DeviationRecord` and cannot mutate the original root.

## Crash consistency and fault model

CAS writes use staging, file fsync, SHA-256 verification, atomic rename, and directory fsync. A candidate CAS object may safely precede the SQLite transaction: a failure after CAS but before the DB commit leaves no candidate and no lock, only a benign GC-safe CAS orphan. A false-complete preregistration (`LOCKED` with an incomplete bundle) is never permitted. Lock uses `BEGIN IMMEDIATE`; the decision, warning acceptances, attestation, state transition, and audit event all roll back together on an injected failure anywhere before commit. Fault injection is exercised before CAS, after CAS, before the DB transaction, inside the transaction, and before commit; after restart the store never shows a partial governance state.

## Concurrency

Concurrent lock attempts are serialized by SQLite. Evidence uses six independent writer processes attempting to lock the same preregistration: exactly one wins, the others receive a typed `LOCKED_ARTIFACT` conflict, there is no double lock, no lost update, and no silent overwrite, and exactly one lock row persists. The race is repeated to increase sensitivity.

## Backup and restore

Full backup archives the checkpointed SQLite database plus every CAS object under an outer file manifest with per-file SHA-256 and size. Restore accepts only a new empty destination, rejects unsafe members (absolute paths, `..`, missing entries) and hash/size mismatches, validates SQLite integrity in a staging directory, and atomically installs the restored tree. A restored store preserves identities, roots, lineage, the audit chain, and CAS integrity, and re-verifies clean. No CPU/GPU execution is part of this model.
