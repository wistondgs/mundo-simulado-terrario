# SCIENTIFIC-EXECUTION-GATE-01 traceability matrix

| Prereg commitment | Current runtime input | Enforcement | Required control | Status |
| --- | --- | --- | --- | --- |
| Bundle root | TrialMatrix/protocol | exact locked-root lookup + verify at request/plan/start | no latest lookup | PASS |
| Trial identities/seeds | `trial_intents` | sealed canonical plan | identity/seed retention | PASS |
| Authorization | execution start | quota transaction + append-only event | no automatic execution | PASS |
| Environment/software | plan | snapshots and dirty/device validation | no implicit fallback | PASS |
| Raw output policy | CAS | typed raw descriptors + hash chain | no EvidenceGraph route/import | PASS |
| Failure/stopping | execution states | revisioned state machine and safe boundaries | preserve partials | PASS |
| Sandbox separation | workspace | distinct scientific panel/badge and import firewall | no promotion path | PASS |

Known boundary: worker-specific runtime checkpoint certification and streamed multipart bundle import remain integration work; neither is represented as a completed scientific run by this gate.
