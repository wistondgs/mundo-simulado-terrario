# Federation snapshot model

## FederationManifest

A `FederationManifest` pins the exact snapshot combination of every federated domain, forming a scientifically reproducible view of the distributed system:

```text
ReferenceGraph snapshot
Theory snapshot
Hypergraph snapshot/version
Hypothesis registry version
World registry version
Preregistration state
EvidenceGraph snapshot
```

Each domain adapter reports its current snapshot identity (or none, for domains without a snapshot mechanism). The manifest's `manifest_hash` commits to the full domain→snapshot map and the schema version. Manifests are append-only.

## CrossGraphSnapshot

A `CrossGraphSnapshot` is an immutable, append-only record with:

- `snapshot_id`, `parent_snapshot_id`;
- `federation_manifest_hash` — the exact domain-snapshot combination;
- `cross_link_set_hash` — `content_hash` over the sorted active link hashes and active hyperlink hashes;
- `root_hash` — `content_hash` over schema version + manifest hash + link-set hash + parent id + parent root hash;
- `link_count`, `hyperlink_count`;
- `created_at`, `actor`, `provenance`.

Snapshots form a chain (`snapshot N -> delta -> snapshot N+1`) and are never mutated. Snapshot creation is idempotent over identical state.

## Query reproducibility

A saved query records its query spec, the federation manifest, the cross-graph snapshot, and the schema versions. Re-executing over the same snapshot returns the same logical result. A derived query cache may be used for pinned queries; its key always includes the query, the cross-graph snapshot, and the federation manifest, so a result is never served from the wrong snapshot.

## Version-aware traversal

Because links and snapshots are append-only with lineage, the system can answer "what relation existed in snapshot X?" and "what changed between X and Y?" via `snapshot_diff`, `link_history`, and `entity_reference_history`. Bitemporal metadata (`recorded_at`, and `effective_at` where applicable) is preserved — for example, a retraction published today about a 2018 paper does not rewrite the past.

## Backup / restore

Integral backup/restore reuses the shared `backup_archive` / `restore_archive` (DB + CAS with a SHA-256 manifest, staged verification, atomic install). Links, provenance, snapshots, federation manifests, candidates, compositions, and reconstructible indexes are preserved; root hashes remain identical and the graph re-verifies clean.
