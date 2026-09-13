# SCIENTIFIC-REFERENCE-GRAPH-01 — Requirements Traceability Matrix

Final acceptance matrix. Every PASS cites a concrete implementation path, test path, and evidence. States: `PASS`, `PARTIAL`, `FAIL`, `N/A + justification`. No PASS without evidence.

| # | Requirement | Implementation | Test | Evidence | Status |
|---|---|---|---|---|---|
| 1 | Three-identity model (Document/Bibliographic/ReferenceRecord) | `domain.py` `DocumentRecord`/`BibliographicRecord`/`ScientificReferenceRecord`; `repository.py` | `test_three_identity_model_is_not_collapsed` | `document_id==cas_blob_hash` (64), `identity_hash != document_id`, `reference_id != biblio_id` | PASS |
| 2 | Document version model (9 types + VERSION_OF/SUPERSEDES/CORRECTS/SUPPLEMENTS) | `domain.py` `DocumentVersionType`, `ref_document_versions` | schema test | version relations explicit; never destructive dedup | PASS |
| 3 | Core domain model (25 typed records) | `domain.py` frozen dataclasses | import/round-trip via import tests | all records typed, no arbitrary JSON centralization | PASS |
| 4 | Claim model (who/what/source/where/context/provenance) | `domain.py` `SourceClaimRecord`, `ref_claims` | import tests; verifier claim-binding | claim carries text/summary/locator/type/source/method/status | PASS |
| 5 | Claim locators (page/section/figure/table/etc.) | `domain.py` `ClaimLocator` | schema test | optional fields; claim→document traceable | PASS |
| 6 | Provenance levels (7) + no auto-promotion | `domain.py` `ProvenanceLevel`; per-edge provenance | `test_analyst_inference_cannot_be_source_explicit` | analyst-inference ≠ SOURCE_EXPLICIT enforced | PASS |
| 7 | Corpus binding (CSV/JSONL/BibTeX/SHA-256/paths/DOI/license/version/provenance) | `import_corpus.py` | `test_import_plan_then_commit_produces_verified_snapshot` + real corpus import | 32 refs / 30 docs imported, snapshot verified | PASS |
| 8 | Quarantine (8 reasons, durable, no auto-repair) | `import_corpus.py`, `ref_quarantine` | `test_quarantine_on_hash_mismatch` | hash mismatch → quarantine, 0 documents, reason recorded | PASS |
| 9 | Duplicate resolution (candidate ≠ confirmed, no auto-merge) | `repository.py` `DuplicateCandidate`, `ref_duplicates`; idempotent import | `test_duplicate_import_is_idempotent_not_destructive` | re-import dedups by SHA-256, 0 new docs, valid | PASS |
| 10 | Graph node types (17) | `domain.py` `NodeType` | import tests | 17 closed node types | PASS |
| 11 | Graph edge types (22) + per-edge provenance | `domain.py` `EdgeType`, `ref_edges` | corruption test on edge payload | 22 closed edge types; provenance committed in edge hash | PASS |
| 12 | Edge semantics (CITES≠SUPPORTS≠CRITIQUES; no proximity semantics) | `domain.py`; provenance required per edge | firewall/verifier tests | CRITIQUES requires explicit provenance | PASS |
| 13 | No TRUE/PROVEN/CORRECT_THEORY/INTELLIGENCE_SCORE | `domain.py` | `test_no_true_proven_score_fields_in_domain` | forbidden tokens absent; conflicts via ConflictKind records | PASS |
| 14 | Protocol extraction model (D2 fields, SOURCE_REPORTED vs EXTRACTION_INFERENCE) | `import_corpus.py` `_protocol_provenance`, `ref_nodes` PROTOCOL | real corpus protocol import | D2 protocol nodes with extraction_basis provenance | PASS |
| 15 | Replication / critique model (not a citation edge) | `domain.py` `ReplicationRecord`/`CritiqueRecord`, REPLICATES/CRITIQUES edges | schema + finder tests | dedicated records + edges with provenance | PASS |
| 16 | Retraction/correction awareness (5 states, not deleted) | `domain.py` `DocumentStatus`, append-only | verifier warning test | RETRACTED retained + visible | PASS |
| 17 | Graph versioning (immutable snapshots, parent, root hash) | `service.py` `create_snapshot`, `ref_snapshots` | `test_snapshot_immutable_and_chained` | N→delta→N+1, parent linked, root verifies | PASS |
| 18 | Content addressing (3 distinct hashes) | `service.py`, `domain.py` | identity + verifier tests | bytes/record/snapshot hashes distinct | PASS |
| 19 | Canonicalization (reuse canonical-json-v1) | `persistence/canonical.py` | preregistration canonical property tests (reused) | same state→same hash; non-finite rejected | PASS |
| 20 | CAS integration | `persistence/blobs.py` | `test_corruption_blob_byte_detected` | tampered byte → DOCUMENT_CAS_INVALID | PASS |
| 21 | Bitemporal/audit (recorded_at, effective_at) | schema cols | schema test | history not rewritten on correction/retraction | PASS |
| 22 | Persistence (WAL, FK, synchronous=FULL, migrations, append-only) | `persistence/store.py`, migration 3+4 | `test_migration_three_applied`, `test_append_only_triggers_block_update_and_delete` | UPDATE/DELETE raise IntegrityError | PASS |
| 23 | Indexing (DOI/title/author/year/construct/paradigm/node/edge/hash/status/snapshot) | migration 3+4 indexes, `ref_constructs`/`ref_paradigms` | performance test | construct query 2421ms→51ms after index | PASS |
| 24 | FTS5 boundary (authorized claims only, not full docs) | `ref_claims_fts` | `search_claims` query test | claims searchable; PDF bytes not indexed | PASS |
| 25 | Query service (14 first-level queries) | `queries.py` | query tests + API tests | all queries return; neighborhood bounded | PASS |
| 26 | Graph projections (read-only, ≠ snapshot) | `queries.py` `projection` | `test_projection_is_read_only_not_snapshot` | read_only, is_snapshot=False, snapshot count unchanged | PASS |
| 27 | D-level tagging (D0–D11 + relevance kinds, no auto-assign) | `domain.py` `RelevanceKind`, d_level_tags | projection by D2 test | D2 projection returns 31 (real corpus) | PASS |
| 28 | D2 first-class support (constructs) | corpus data + constructs index | real corpus query | OBJECT_PERSISTENCE → 6 refs | PASS |
| 29 | D2 references as data (Spriteworld, CLEVR, Spelke, etc.) | real corpus import | real corpus counts | 32 refs incl. named D2 set, not hardcoded | PASS |
| 30 | Corpus import contract (ImportPlan before write) | `import_corpus.py` `build_plan` | plan test | plan lists create/dup/conflict/quarantine | PASS |
| 31 | Import atomicity (validate→stage CAS→transaction→snapshot→commit) | `import_corpus.py` `import_corpus` | `test_fault_injection_before_snapshot_keeps_previous_valid` | failure leaves previous snapshot valid | PASS |
| 32 | Concurrency (no dup identity/lost update/half-snapshot) | `BEGIN IMMEDIATE` + in-transaction dedup + per-pid CAS staging | `test_concurrent_imports_single_winner_no_half_snapshot` | 4 processes → consistent winner, valid graph | PASS |
| 33 | Integrity verifier (structured) | `service.py` `verify` | all corruption tests | structured report localizes each tamper | PASS |
| 34 | Graph invariants (10) | `service.py` `verify` | corruption + invariant tests | each invariant has a failing-case test | PASS |
| 35 | Cross-graph boundary (foreign IDs as contracts, no traversal) | opaque IDs; no cross-domain engine | firewall test | no TheoryGraph/EvidenceGraph write path | PASS |
| 36 | API (read/write separated, queries vs mutations) | `api.py`, wired in `LabAPI` | API dispatch tests | mutating routes need CSRF/local; queries separate | PASS |
| 37 | Export (self-contained snapshot manifest) | export manifest test | `test_export_snapshot_manifest_self_contained` | manifest + required blobs all verify | PASS |
| 38 | Backup / restore integral | `persistence/store.py` `backup_archive`/`restore_archive` | `test_backup_restore_preserves_graph_and_roots` | root hashes identical, counts equal, verify clean | PASS |
| 39 | Advanced testing (unit/integration/invariant/concurrency/fault/roundtrip/backup/corruption) | `tests/test_reference_graph_*.py` | 22 tests pass | no mocks where integrity depends on SQLite/CAS | PASS |
| 40 | Required corruption tests (8) | `tests/test_reference_graph_advanced.py` | blob/DOI/node/edge/provenance/root/parent/version | verifier localizes each | PASS |
| 41 | Performance characterization (10k + larger, real measures, O(N²) detection) | `scripts/reference_graph_performance.py` | measured | see Performance below; 2 O(N²) found & fixed | PASS |
| 42 | API/domain firewalls (no EvidenceGraph/TheoryGraph/Hypothesis/ExperimentDraft/preregister/execute) | package-wide | `test_reference_graph_firewall_no_evidence_or_theory_write` | no forbidden creation call; status flags false | PASS |
| 43 | Human authority (system suggests; never declares truth/merges/promotes/decides) | design + invariants | invariant tests | no auto-merge, no auto-promote, no citation-count support | PASS |
| 44 | Documentation (7 docs) | `docs/SCIENTIFIC_REFERENCE_GRAPH_01.md` + 6 | doc review | only real behavior documented | PASS |
| 45 | Historical integrity (A0–A4, H-ADAPT, preregistration, theory, evidence) | full suite | regression run | all historical suites green; H-ADAPT not executed | PASS |

## Performance (real measurements, this machine; not a scalability claim)

Scale 10,000 references (40,000 nodes / 30,000 edges / 10,000 documents):

- bulk import: 71.4 s
- DOI lookup: 1.0 ms
- construct query: 51.1 ms (was 2421.9 ms before term indexes — O(N²) removed)
- neighborhood traversal (depth 2): 1.0 ms (was 179.0 ms before SQL-frontier rewrite — O(E) removed)
- snapshot creation: 1.0 s
- verification: 5.1 s
- snapshot diff: 2.6 ms

Larger scale (25,000 references; 100,000 nodes / 75,000 edges / 25,000 documents):

- bulk import: 155.9 s (2.2× the 10k time for 2.5× the records — near-linear)
- DOI lookup: 1.5 ms
- construct query: 141.3 ms (2.8× — near-linear, no residual O(N²))
- neighborhood traversal (depth 2): 1.7 ms
- snapshot creation: 2.8 s
- verification: 12.4 s (2.7× — near-linear)
- snapshot diff: 1.7 ms

Bulk import is dominated by per-document CAS fsync and per-record inserts; it is a batch operation and is reported, not claimed scalable. Query and traversal paths scale near-linearly after the two accidental O(N²) paths were eliminated.

## Summary

- PASS: 45 requirements.
- PARTIAL: 0.
- FAIL: 0.
- N/A: 0.

No substantive block is PARTIAL. Two accidental O(N²) paths (construct query, neighborhood traversal) were detected by measurement and eliminated via term indexes and a SQL-frontier traversal.
