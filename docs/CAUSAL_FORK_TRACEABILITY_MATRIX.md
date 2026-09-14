# Causal Fork Traceability

| Requirement | Implementation | Test | Status |
| --- | --- | --- | --- |
| Exact snapshot/CAS | `lab/causal.py`, migration 8 | `test_exact_restore...` | PASS A0/D0 |
| Restore + double restore | `CausalRuntime.restore` | `test_exact_restore...` | PASS A0/D0 |
| C00/C01 and registry | `InterventionRegistry` | `test_fork_c00_c01...` | PASS |
| Active declared mutation/diff | `TEST_ENERGY_DELTA`, `first_divergence` | `test_fork_c00_c01...` | PASS |
| Fail closed | `ForkabilityCapability` | `test_snapshot_tamper...` | PASS |
| I01–I12 / A1–A4 / D1–D4 | deferred | n/a | NOT IMPLEMENTED |
