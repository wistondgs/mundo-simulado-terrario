# PREREGISTRATION-CORE-01 — Requirements Traceability Matrix

Final acceptance matrix. Every PASS cites a concrete implementation path, test path, and evidence. States: `PASS`, `PARTIAL`, `FAIL`, `N/A + justification`. No PASS without evidence.

| # | Requirement | Implementation | Test | Evidence | Status |
|---|---|---|---|---|---|
| 1 | Typed domain model (20 first-class contracts) | `terrario/lab/preregistration/domain.py` | `test_every_scientific_mutation_changes_root_and_ui_does_not`, codec round-trip | All 20 contracts are frozen dataclasses; round-trip preserves `scientific_hash` | PASS |
| 2 | AnalysisPlan closure (incl. `DESCRIPTIVE_ONLY`, endpoint roles) | `domain.py:278` `AnalysisPlan`; `domain.py:33` `EndpointRole` | mutation + round-trip tests | transformations/grouping/aggregation pinned; `DESCRIPTIVE_ONLY` supported; no p-value required | PASS |
| 3 | ProtocolSnapshot exact identities | `domain.py:387` `ProtocolSnapshot` | scientific mutation tests | world/observation/action/intervention/agent hashes pinned; `latest/current/active` prohibited | PASS |
| 4 | Hash model (canonical→SHA-256→manifest→root) | `preregistration/commitments.py`, `persistence/canonical.py` | `test_every_scientific_mutation_changes_root_and_ui_does_not`, `test_canonical_hash_properties_without_external_dependency` | same state→same root; scientific delta→diff root; UI delta→same root; 250 canonical cases | PASS |
| 5 | CAS content addressing | `persistence/store.py` blobs | tampered/missing component probes | tampered→`CAS_OBJECT_MISSING` FAIL; missing→FAIL | PASS |
| 6 | Structured verifier | `service.py:173` `verify` | direct probe on locked record | structured dict, 9 per-field booleans, failures/warnings lists | PASS |
| 7 | State machine | `domain.py` `assert_transition`, `ALLOWED_TRANSITIONS` | `test_invalid_state_transitions_are_rejected` | 4 invalid transitions raise `InvalidTransition` | PASS |
| 8 | Human review authority | `service.py` review/lock ceremony, `repository.py` | `test_complete_human_review_lock_and_verification`, `test_unapproved_upstream_is_a_blocker` | exact-root decision required; upstream approval bound to version+hash | PASS |
| 9 | Four-layer immutability (domain/repo/API/SQL) | frozen dataclasses, state machine, API field guards, SQL triggers | `test_sql_layer_rejects_lock_update_and_delete`, `test_sql_rejects_review_audit_and_deviation_deletion` | UPDATE/DELETE on locks/attestations/decisions/audit/deviations raise `IntegrityError` | PASS |
| 10 | Multiprocess concurrency (6 writers → 1 winner) | `repository.py:294` `lock` (`BEGIN IMMEDIATE`) | `test_real_multiprocess_lock_has_exactly_one_winner` (run 3×) | exactly 1 `LOCKED`, others `LOCKED_ARTIFACT`, 1 lock row | PASS |
| 11 | Crash consistency / fault injection | `store.py` CAS staging + transactions | `test_lock_fault_inside_transaction_rolls_back_after_restart`, `test_candidate_failures_never_publish_partial_governance_state` | no `LOCKED`+incomplete; rollback before commit; CAS orphan benign | PASS |
| 12 | Exposure Ledger (Preview/Seed Browser/Sandbox) | `service.py` `record_exposure`, `_exposure_status` | `test_exposure_is_written_before_legacy_preview`, `test_exposure_states_are_derived_without_mutating_locked_root`, `test_postlock_preview_is_bound_to_root_and_becomes_postlock_exposed` | UNEXPOSED/PREEXPOSED/POSTLOCK_EXPOSED/CONTAMINATION_REVIEW_REQUIRED; append-only; root unchanged | PASS |
| 13 | Holdout / partition integrity | `domain.py:40` `Partition`, `validation.py` overlap rules | readiness/validation tests | 6 partitions; overlap detection; holdout exposure→contamination review, not auto-invalidation | PASS |
| 14 | Randomization commitment | `domain.py:258` `RandomizationPlan` | round-trip tests | algorithm/version/seed/constraints frozen; no global mutable RNG | PASS |
| 15 | TrialMatrix exactness | `service.py` `_assemble`, matrix cardinality checks | `validation.py` cardinality/parity rules | exact trials pinned by version+hash; cardinality computed exactly | PASS |
| 16 | Failure / exclusion / stopping policies | `domain.py` `FailurePolicy`/`ExclusionPolicy`/`StoppingRule`, `validation.py:165` | policy/readiness tests | 5 dispositions + 5 stopping rules versioned; post-lock change→DeviationRecord | PASS |
| 17 | Amendment cycle (A→amend→B→review→lock→supersede) | `service.py:311` `add_postlock_record`, `:358` `supersede` | `test_scientific_amendment_creates_new_reviewed_lineage_before_supersede` | A remains verifiable/immutable/exportable; supersede requires locked reviewed descendant | PASS |
| 18 | Deviation ledger (typed, append-only) | `domain.py:592` `DeviationRecord`, `service.py` | `test_postlock_deviation_is_separate_and_root_stays_fixed`, SQL deletion test | 8 deviation categories; append-only; original bundle never mutated | PASS |
| 19 | Audit hash chain | `repository.py` `verify_audit_chain`/`verify_audit_rows` | `test_corrupted_copy_of_audit_chain_is_detected` | tampered copy detected; chained canonical events | PASS |
| 20 | Export / import (exact identity) | `service.py:376/396/424`, `store.py:566` `import_bundle_exact` | `test_portable_bundle_roundtrip_and_tamper_detection`, `test_portable_import_preserves_lineage_references_and_requires_local_review`, `test_missing_portable_cas_component_is_rejected` | round-trip exact; duplicate dedup; conflict/tamper/missing-CAS rejected; identity never rewritten | PASS |
| 21 | Backup / restore integral | `store.py` `backup_archive`/`restore_archive` | `test_full_backup_restore_preserves_lock_cas_exposure_and_verification` | same identities/roots/lineage/audit chain; CAS integrity; `integrity_check()=="ok"` | PASS |
| 22 | Evidence firewall | `preregistration/api.py` route table, `service.py` | `test_no_execution_or_evidence_endpoint_exists`, `test_openapi_exposes_governance_but_no_execution` | no ScientificRun/EvidenceRecord/EvidenceGraph-edge/Conclusion path; `scientific_execution:false`, `evidence_publication:false` | PASS |
| 23 | Historical regression (snapshot/review/evidence/A0–A4/H-ADAPT/persistence/sandbox/composer) | existing suites | 57 + 25 historical tests pass | theory snapshot hash-addressed; H-ADAPT unproven, not executed; integrity only | PASS |
| 24 | Full test suite | whole repo | `pytest` | `367 passed, 1 skipped`, 0 unexplained failures/regressions | PASS |
| 25 | Documentation | `docs/PREREGISTRATION_*.md` | this matrix + doc review | domain/trust/canonicalization/hashing/CAS/state/authority/lock/concurrency/recovery/fault/exposure/holdout/amendments/deviations/export-import/backup-restore/firewall documented as implemented | PASS |
| 26 | Property-based testing (Hypothesis) | deterministic generated cases | `test_canonical_hash_properties_without_external_dependency` | Hypothesis unavailable; 250 seeded randomized canonical cases used instead | N/A — Hypothesis not installed; deterministic property coverage provided |
| 27 | Browser E2E / accessibility | modular UX + live HTTP | live HTTP checks | `agent-browser`/Node unavailable; no dependency silently installed | PARTIAL — HTTP/module verified; browser runner absent |

## Summary

- PASS: 25 requirements.
- PARTIAL: 1 (browser E2E — environmental limitation, not a scientific-integrity gap).
- N/A: 1 (Hypothesis property testing — substituted with deterministic generated cases).
- FAIL: 0.

No substantive scientific-integrity property is FAIL or unverified. The two non-PASS items are environmental/tooling limitations explicitly disclosed, not reductions of scope.
