# Reference provenance model

Every scientific relation in the reference graph declares provenance. Provenance is never inferred from bibliographic proximity and is never promoted automatically from one level to another.

## Provenance levels

- `SOURCE_EXPLICIT` — stated explicitly in the source document.
- `SOURCE_DERIVED` — derived from the source by an analyst reading it.
- `ANALYST_INFERRED` — an analyst's interpretation, not the source's words.
- `MACHINE_EXTRACTED_UNVERIFIED` — produced by an automated extractor, not yet human-verified.
- `USER_ASSERTED` — asserted by a user without source backing.
- `IMPORTED_METADATA` — carried in from corpus metadata.
- `UNKNOWN` — provenance not established.

## Claim model

A `SourceClaimRecord` expresses *who claims what, in which source, where exactly, under what context, with what extraction provenance*. It carries `claim_text`, `normalized_summary`, `document_version_id`, a `ClaimLocator`, `claim_type`, `epistemic_source`, `extraction_method`, `verification_status`, and `created_at`. Claim types are kept distinct: `SOURCE_TEXT`, `SOURCE_REPORTED_CLAIM`, `ANALYST_INTERPRETATION`, `MACHINE_EXTRACTION_UNVERIFIED`, `USER_NOTE`.

A hard invariant, enforced by the verifier: an `ANALYST_INTERPRETATION` claim can never be marked `SOURCE_EXPLICIT`. Machine extraction is never promoted to a verified claim automatically.

## Claim locators

A `ClaimLocator` can point, when present, to page, section, subsection, figure, table, paragraph, appendix, or supplement. None is required individually, but the locator always allows returning from the claim to the exact document location.

## Edge semantics

An edge such as `paper A CRITIQUES paper B` cannot be derived merely because B is cited by A; it requires explicit provenance for that interpretation. `CITES` is distinct from `SUPPORTS` and from `CRITIQUES`. Every edge stores a `provenance_level` and `provenance_detail`, and the edge hash commits to both, so tampering with provenance is detected by the verifier.

## Conflicts

The graph has no `TRUE`/`PROVEN`. Disagreements between sources are recorded as first-class records/relations with provenance: `CONTRADICTORY_REPORTS`, `METHODOLOGICAL_DISAGREEMENT`, or `UNRESOLVED_CONFLICT`. The system never decides which reference "wins" and never infers causal support from citation counts.

## Bitemporal semantics

Mutable-discovery metadata preserves `recorded_at` and, where applicable, `effective_at`. When a correction, retraction, DOI fix, or new version is later discovered, a new append-only record is written; history is never rewritten.
