# Cross-graph failure and recovery model

## Crash consistency

Link persistence, snapshot commit, CAS write, index rebuild, and candidate activation all run inside `BEGIN IMMEDIATE` transactions. A fault injected before a snapshot commit leaves the previous snapshot as the latest valid one; after restart there is never a half-snapshot. CAS writes are atomic and process-safe (per-pid staging, dead-owner-only recovery).

## Concurrency

Multiprocess link creation, candidate activation, snapshot creation, import, and composition save are serialized by SQLite. Concurrent writers produce no lost update and no double activation; losers receive a typed conflict, and the store re-verifies clean afterward.

## Endpoint failure model

Endpoints that become inaccessible are not deleted. They are classified `DANGLING`, `STALE_VERSION`, `STORE_UNAVAILABLE`, or `HASH_MISMATCH` and kept with provenance, so the failure is visible and history is preserved. Link activation requires both endpoints to resolve; a candidate cannot activate against a dangling or hash-mismatched endpoint.

## Trace breaks

Where a trace cannot continue — a missing concept, an absent claim, an unresolvable scenario — a `TraceBreak` is recorded with `from`, expected next domain, reason, missing identity/relation, discovered_at, and resolution state. Gaps are never filled automatically to complete a demo.

## Backup / restore

Integral backup/restore preserves links, provenance, snapshots, federation manifests, candidates, compositions, and reconstructible indexes. Restore validates the archive manifest and SQLite integrity in staging and installs atomically; root hashes remain identical and the graph re-verifies clean.

## Export / import

A `CrossGraphBundle` export contains the schema, federation manifest, links, provenance, hashes, snapshot root, and referenced identity manifests. Import runs `validate -> verify -> resolve domains -> conflict detection -> transaction -> snapshot`; it never silently overwrites an existing identity.
