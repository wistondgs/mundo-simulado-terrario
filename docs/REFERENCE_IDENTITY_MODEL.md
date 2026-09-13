# Reference identity model

The reference graph never collapses three distinct identities. Conflating them is the most common way scientific provenance is destroyed, so they are modeled as separate, independently keyed records.

## DocumentIdentity

The identity of a concrete file: `SHA-256(file bytes)`, which is also the CAS blob hash. Two different PDFs (a preprint and a published version) have different DocumentIdentities even when they represent the same work. Document bytes are stored in the SHA-256 CAS with atomic, fsynced, recoverable writes; `document_id == cas_blob_hash` is enforced by the verifier.

## BibliographicIdentity

The identity of the work/publication, independent of any single file. Computed as:

- if a real DOI exists: `content_hash({doi: normalized_doi})`;
- otherwise: `content_hash({normalized_title, authors, year})`.

Normalization lowercases, strips accents and punctuation, and collapses whitespace. DOIs are normalized by stripping the `https://doi.org/` / `doi:` prefix and lowercasing. The `identity_hash` is UNIQUE, so the same work resolves to one bibliographic record; multiple document versions attach to it through `ref_document_versions`.

## ReferenceRecordIdentity

The Terrario-internal record (`reference_id`) that binds a work to its documents, D-level tags, constructs, paradigms, discipline, and verification status. This is the node other subsystems reference. It is never derived from, nor equal to, the DocumentIdentity or the BibliographicIdentity.

## Version relations

Legitimate versions are never deduplicated destructively. `DocumentVersion` records carry explicit `VERSION_OF`, `SUPERSEDES_DOCUMENT_VERSION`, `CORRECTS`, and `SUPPLEMENTS` relations with provenance. A correction or retraction does not delete the prior version; it adds a new append-only record and updates status (`ACTIVE`, `CORRECTED`, `RETRACTED`, `EXPRESSION_OF_CONCERN`, `UNKNOWN`) while keeping the retracted reference visible.

## Duplicate resolution

Duplicate candidates are detected by exact SHA-256, DOI, exact normalized bibliographic identity, and title+authors+year similarity. A candidate is recorded with a status of `MERGE_CANDIDATE`, `CONFIRMED_DUPLICATE`, `DISTINCT_VERSION`, `DISTINCT_WORK`, or `UNRESOLVED`. A candidate is never an automatic or destructive merge; only a human confirms a merge, and merges never delete provenance.
