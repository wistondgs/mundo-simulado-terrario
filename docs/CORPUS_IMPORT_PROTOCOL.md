# Corpus import protocol

`terrario.scientific-reference-corpus/v1` defines how an external corpus package is bound into the reference graph. The importer is `CorpusImporter` in `terrario/lab/referencegraph/import_corpus.py`.

## Consumed inputs

The importer consumes, as data (never hardcoded):

- `manifest/CORPUS_MANIFEST.jsonl` / `.csv` — per-document identity: `document_id`, `reference_id`, `sha256`, `local_relative_path`, `mime_type`, `file_size_bytes`, `version_type`, `doi`, `title`, `authors`, `year`, `venue`, `license`, `access_status`, `open_access_status`, `peer_review_status`, `fulltext_status`, `document_validation`, `terrario_levels`, `d2_constructs`, `experimental_paradigm`, `discipline`, `provenance`, urls, `page_count`.
- `metadata/REFERENCE_RECORDS.jsonl` — per-reference: `reference_id`, `reference_type`, `title`, `authors`, `year`, `constructs[]`, `experimental_paradigms[]`, `design_principles[]`, `known_limitations[]`, `paper_document_ids[]`, `terrario_levels[]`, `discipline`, `code_url`, `verification_status`.
- `metadata/D2_PROTOCOL_EXTRACTION.csv` — per-reference protocol fields (subjects/agents, sample size, stimulus, environment, manipulated/independent/dependent variables, controls, outcomes, training/test/occlusion/delay/distractor/generalisation structure, statistics, reported effect, authors' interpretation, limitations, `extraction_basis`).
- `metadata/REFERENCE_LIMITATIONS.csv`, `metadata/DESIGN_PRINCIPLES.csv`, `metadata/VERSION_RELATIONSHIPS.csv`.
- `bibliography/references.csv` / `references.bib` — bibliographic cross-check.
- `provenance/SOURCE_PROVENANCE.jsonl` / `.csv` — acquisition provenance (discovered_via, downloaded_from, redirect_chain, repository, access_date, verification_notes).
- Document bytes at each `local_relative_path`.

## Pipeline

`parse → schema validate → file verify → SHA-256 verify → identity resolution → duplicate analysis → conflict analysis → ImportPlan → (human review on conflict) → stage CAS → transaction → graph snapshot → commit`.

`build_plan` produces an `ImportPlan` listing `CREATE`, `UPDATE_AS_NEW_VERSION`, `EXACT_DUPLICATE`, `CONFLICT`, and `QUARANTINE` actions before anything is written. When conflicts exist, a human reviews the plan; the import does not silently proceed. The whole batch commits in one `BEGIN IMMEDIATE` transaction that ends in a new graph snapshot; a failure leaves the previous snapshot valid.

## Quarantine

Durable quarantine (never silent, never auto-repaired) for: `MISSING_FILE`, `HASH_MISMATCH`, `HTML_DISGUISED_AS_PDF`, `ZERO_BYTE_DOCUMENT`, `CONFLICTING_DOI_IDENTITY`, `MALFORMED_METADATA`, `INCOMPATIBLE_SCHEMA`, `INCOMPATIBLE_DUPLICATE`. Each record carries reason, source, import batch, timestamp, and resolution state.

## Full-text search boundary

Document bytes are stored in the SHA-256 CAS but are **not** full-text indexed. Only authorized content — claim text and normalized summaries — enters the FTS5 index (`ref_claims_fts`). Copyrighted document full text is not duplicated into the search index. The corpus's extracted `.txt` companions are the authorized full text for any future authorized indexing; the PDFs themselves remain CAS-only.

## Atomicity and concurrency

Concurrent imports are serialized by `BEGIN IMMEDIATE`. Dedup is re-verified inside the serialized transaction, so a concurrent import that committed the same document between planning and commit is treated as an exact duplicate, not an error. CAS writes are atomic and process-safe: staging files are named per-process (`blob-<pid>-*.staging`), and crash recovery only reclaims staging whose owning process is dead, so an active concurrent writer is never moved out from under itself. The outcome is a single consistent winner with no half-snapshot and no lost update.
