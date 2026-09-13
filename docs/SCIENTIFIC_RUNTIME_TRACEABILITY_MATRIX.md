# Scientific runtime traceability

| Requirement | Implementation | Test | Status |
| --- | --- | --- | --- |
| sealed plan to trial | dispatcher claims reserved job | dispatcher integration | PASS |
| real engine | `run_materialized_trial` calls `ExperimentController.run_episode` | dispatcher integration | PASS |
| strong identity | `ScientificTrialIdentity` in observer/frames/artifacts | dispatcher integration | PASS |
| tick 0 and later frames | scientific frame sink | dispatcher integration | PASS |
| raw CAS artifacts | trace/result sealing through service | dispatcher integration | PASS |
| sandbox isolation | separate runtime package; no sandbox import | execution firewall | PASS |

No EvidenceGraph write path exists.
