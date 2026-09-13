# Reference graph integrity model

## Canonicalization and hashing

The reference graph reuses the shared `terrario-canonical-json-v1` profile (UTF-8, sorted keys, deterministic compact separators, `allow_nan=False`). Three hashes are kept distinct and never conflated:

- **document bytes hash** — SHA-256 of the file, the CAS blob hash;
- **record canonical hash** — `content_hash` of a record's scientific payload (node/edge hashes);
- **snapshot root** — `content_hash` over schema version + node-set hash + edge-set hash + parent snapshot id + parent root hash.

Scientifically significant metadata affects identity; UI preferences never enter scientific payloads.

## Graph versioning

Snapshots are immutable. A change is `snapshot N → delta → snapshot N+1`; each snapshot records parent, schema version, node-set hash, edge-set hash, root hash, counts, and provenance. Snapshots are append-only and are never mutated. A projection is a read-only derived view (`is_snapshot: false`), never a new snapshot.

## Structured verifier

`verify_reference_graph` returns a structured report, not a boolean. It checks: schema, graph root, node hashes, edge hashes, CAS document integrity, bibliographic identities, version lineages, edge endpoint existence, provenance existence, duplicate conflicts, dangling references, snapshot ancestry, and retraction/correction consistency. It reports per-area failures and warnings plus counts.

## Graph invariants

Enforced by the verifier and by targeted corruption tests:

- edge endpoints exist;
- every scientific edge has provenance;
- document hash matches bytes (`document_id == cas_blob_hash` and CAS verifies);
- version lineage is valid;
- snapshot root verifies;
- a retracted reference is not deleted;
- claims have source binding;
- an analyst inference is never `SOURCE_EXPLICIT`;
- a duplicate candidate is not a destructive merge;
- a projection does not mutate a snapshot.

## Corruption detection

The verifier localizes deliberate tampering of: a document blob byte (`DOCUMENT_CAS_INVALID`), a node payload (`NODE_HASH_MISMATCH`), an edge payload / provenance (`EDGE_HASH_MISMATCH`), the snapshot root (`NODE_SET_HASH_MISMATCH` / `ROOT_HASH_MISMATCH`), a parent snapshot (`SNAPSHOT_PARENT_MISSING`), a dangling edge endpoint (`EDGE_TARGET_MISSING`), and an analyst-inference marked source-explicit (`ANALYST_INFERENCE_MARKED_SOURCE_EXPLICIT`).

## Append-only enforcement

All scientific tables are append-only via SQLite triggers; direct UPDATE/DELETE at the SQL layer raises `IntegrityError`. Combined with the frozen-dataclass domain and the API's refusal to expose mutation routes for committed records, immutability holds at the domain, repository, API, and SQL layers.

## Backup and restore

Integral backup/restore reuses the existing `backup_archive` / `restore_archive` (DB + CAS with a SHA-256 file manifest, staged verification, atomic install). A restored store preserves records, graph, snapshots, lineage, quarantine, CAS, and provenance; root hashes remain identical and the graph re-verifies clean. Indexes are reconstructible from the restored tables.
