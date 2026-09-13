# Cross-graph identity model

CrossGraph connects sovereign domains without fusing them. Its identity model is built so a reference can always be pinned exactly, and so a "latest" pointer never enters saved scientific state.

## CrossDomainEntityRef

The single strong type for referencing any entity in any domain:

- `domain` — one of the 12 registered domains.
- `entity_type` — the type within that domain (e.g. `ScientificReferenceRecord`, `WorldDefinition`, `HypothesisRecord`).
- `entity_id` — the domain-local identifier (required).
- `version_id` — exact version, when the domain versions entities.
- `snapshot_id` — exact snapshot, when the domain snapshots state.
- `content_hash` — exact content hash, when the domain content-addresses.
- `schema_version` — the entity's schema version.

Not every field is mandatory for every domain, but a reproducible scientific reference can pin the exact version/snapshot/hash. `ref_hash` commits to the whole reference; `key()` gives the canonical `DOMAIN:entity_type:entity_id` form used by indexes.

## No "latest" in scientific state

An interactive view may query `latest` for exploration (`EXPLORATORY_LATEST` mode). But any saved composition, exported traversal, scientific path, preregistration binding, or provenance report must resolve to an exact version/snapshot/hash (`PINNED_REPRODUCIBLE` mode). The two modes are never conflated, and the future UI must show which is in use.

## Federation identity

A `FederationManifest` pins the exact snapshot combination of every federated domain (ReferenceGraph snapshot, Theory snapshot, Hypergraph version, Hypothesis registry version, World registry version, Preregistration state, EvidenceGraph snapshot). Its `manifest_hash` is the identity of that reproducible distributed view. A `CrossGraphSnapshot` then commits the manifest hash plus the cross-link-set hash, parent, and root hash.

## Identity relations are not semantic relations

`same thing`, `maps to`, `related to`, `supports`, `tests`, and `derived from` are kept distinct. `MAPS_TO` is an analyst-asserted mapping between distinct entities, never an identity claim; there is no `SAME_AS` wildcard. Identity is established only by the sovereign domain's own content hash / version / snapshot, verified through its adapter.

## Dangling and stale identity

A cross-link whose endpoint becomes inaccessible is never deleted. It is classified `DANGLING`, `STALE_VERSION`, `STORE_UNAVAILABLE`, or `HASH_MISMATCH` and kept with its provenance, so history is preserved and the failure is visible to the verifier.
