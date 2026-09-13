# Cross-graph integrity model

## Structured verifier

`verify_cross_graph` returns a structured report, not a boolean. It checks: schema, snapshot root, federation manifest, domain snapshot identities, node refs, endpoint resolution, link hashes, relation semantics, provenance, link lineage, hyperlink members, dangling references, stale versions, and the snapshot ancestry chain. Indexes are optionally checked.

## Consistency classes

Issues are not all treated alike. The report distinguishes `INTEGRITY_FAILURE`, `STALE_REFERENCE`, `DOMAIN_UNAVAILABLE`, `SCIENTIFIC_WARNING`, `UNREVIEWED_CANDIDATE`, `HISTORICAL_REFERENCE`, and `NOT_APPLICABLE`. A dangling endpoint on an active link is an integrity failure; a stale version is a stale-reference warning; an unavailable domain is reported separately from a hard failure.

## Invariants enforced

- every active link has provenance;
- link hash commits to source ref, target ref, relation, assertion class, state, provenance, lineage, and timestamps;
- denormalized index keys (`source_key`/`target_key`) match the committed refs;
- relation source/target domains satisfy the registry constraints;
- a `MACHINE_CANDIDATE` is never `ACTIVE`;
- hyperlink members number at least two and the hyperlink hash verifies;
- snapshot ancestry has no missing parent and no cycle;
- federation manifests are well-formed domain→snapshot maps.

## Corruption detection

Targeted mutation tests confirm the verifier localizes: entity hash tampering, endpoint ID tampering (`TARGET_KEY_MISMATCH`), relation-type tampering, provenance tampering, federation-manifest tampering, snapshot-root tampering, hyperlink-member tampering, and parent-snapshot tampering.

## Append-only enforcement

Cross-links, hyperlinks, federation manifests, snapshots, and trace breaks are append-only via SQLite triggers; direct UPDATE/DELETE raises `IntegrityError`. Combined with the frozen-dataclass domain and an API that exposes no mutation route for committed records, immutability holds at the domain, repository, API, and SQL layers. Correction is `supersede/retract`, never `UPDATE old meaning`.

## Firewalls

The verifier report always carries `theory_graph_modified: false`, `evidence_graph_modified: false`, `reference_graph_modified: false`, `preregistration_modified: false`, `scientific_execution: false`, `evidence_publication: false`. CrossGraph reads sovereign domains through read-only adapters and writes only to its own append-only tables.
