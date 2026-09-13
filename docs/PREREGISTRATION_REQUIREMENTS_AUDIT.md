# PREREGISTRATION-CORE-01 requirements audit

| Requirement | Status | Implementation | Verification |
|---|---|---|---|
| Preflight/baseline | IMPLEMENTED_VERIFIED | Git + pytest | 349 baseline tests before audit |
| Typed domain | IMPLEMENTED_VERIFIED | `domain.py`, codecs | round-trip and mutation tests |
| State machine | IMPLEMENTED_VERIFIED | `ALLOWED_TRANSITIONS`, repository states | invalid-transition tests |
| Canonical commitment | IMPLEMENTED_VERIFIED | `commitments.py` | ten roles, exact root verification |
| Protocol completeness | IMPLEMENTED_VERIFIED | expanded `ProtocolSnapshot` | scientific mutation tests |
| Analysis completeness | IMPLEMENTED_VERIFIED | expanded `AnalysisPlan` | round-trip/mutation tests |
| Hash/CAS/UI exclusion | IMPLEMENTED_VERIFIED | canonical v1 + CAS | mutation/property/tamper tests |
| SQL immutability | IMPLEMENTED_VERIFIED | migration triggers | direct SQL update/delete tests |
| Concurrent lock | IMPLEMENTED_VERIFIED | `BEGIN IMMEDIATE` | six-process race |
| Exposure/Holdout | IMPLEMENTED_VERIFIED | durable ledger | all derived-state tests |
| Failure/exclusion/stopping | IMPLEMENTED_VERIFIED | typed policies + validation | policy tests/readiness |
| Amendments/supersede | IMPLEMENTED_VERIFIED | typed child lineage | full child review/lock test |
| Deviations | IMPLEMENTED_VERIFIED | typed sealed artifacts | schema + SQL deletion test |
| Audit chain | IMPLEMENTED_VERIFIED | chained canonical events | corrupted-copy test |
| Export/import | IMPLEMENTED_VERIFIED | portable DB/CAS bundles | transfer, duplicate, tamper/missing tests |
| Crash consistency | IMPLEMENTED_VERIFIED | atomic CAS/transactions | injected pre-commit and restart tests |
| Backup/restore | IMPLEMENTED_VERIFIED | full archive manifest | restore and verify test |
| Evidence firewall | IMPLEMENTED_VERIFIED | no execution/evidence route/service | endpoint/firewall tests |
| Structured verifier | IMPLEMENTED_VERIFIED | `service.verify` | locked/import/restore verification |
| Property testing | NOT_APPLICABLE_WITH_JUSTIFICATION | Hypothesis unavailable; deterministic generated cases used | 250 randomized canonical cases |
| Performance boundary | IMPLEMENTED_VERIFIED | measured, not claimed scalable | 10k cells: 1,118,976 B; canonical 107 ms; hash 112 ms |
| Browser automation | IMPLEMENTED_UNVERIFIED | modular UX + live HTTP | runner/Node/browser unavailable |

The browser limitation prevents claiming browser accessibility/E2E completion, but it is not used to infer failure or success of scientific integrity gates. No dependency was installed silently.

## Close-out

This audit is superseded by the final `PREREGISTRATION_TRACEABILITY_MATRIX.md`, which records the per-requirement PASS/PARTIAL/N-A state with concrete implementation/test/evidence paths. At close the full suite is `367 passed, 1 skipped` (baseline before corrections `349 passed, 1 skipped`), with 0 unexplained failures or regressions, and the acceptance-gate invariant audit is 8/8 PASS.
