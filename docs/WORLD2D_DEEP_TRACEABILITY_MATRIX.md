# WORLD2D-DEEP-INTEGRATION traceability matrix

Statuses require implementation, test, and executed evidence.

| Requirement | Implementation | Test/evidence | Status |
|---|---|---|---|
| Tick 0 and atomic `t+1` frame | `worldstream/service.py` | `test_tick_zero_and_atomic_three_views`, `test_transition_records_observation_t_and_t1_then_frame_t1` | PASS |
| Exact Agent observation/firewall | service agent payload + Observer sidecar | profile invariance test; existing no-leakage suite | PASS |
| Observer configured projection | `ObserverRegistry` reuse | frame contract/profile test | PASS |
| State/revision/idempotency | live service locks and command ACK cache | conflict/idempotency backend + E2E | PASS |
| Trace v2/hash-chain/index/seek | `worldstream/trace.py` | corruption/rebuild/seek tests | PASS |
| SSE/reconnect/gap/resync | handler + `protocol.js` | Chromium live E2E + reducer tests | PASS |
| Legacy `/api/sandbox` | same live service authority | legacy suite + versioned API test | PASS |
| Three labelled synchronized views | WorldFrame validator + UI | Chromium live E2E | PASS |
| Canvas/WebGL2/fallback/picking | `renderers.js` | existing canvas interaction; WebGL fault benchmark pending | PARTIAL |
| Timeline/diff/identity | `timeline.js`, World2D panel | virtualization, adjacent diff and stable truth identity tested; arbitrary range/bookmarks/entity history incomplete | PARTIAL |
| Firefox real E2E | Playwright official build/project | 23 Firefox tests passed; visual baselines remain Chromium-specific | PASS |
| 10k/50k render and 100k/1M trace gates | benchmark model | full matrix not yet executed | PARTIAL |
| Restart/SESSION_LOST and subscriber cap | documented failure model | not implemented end-to-end | PARTIAL |
| Protected scientific artifacts | firewall boundary + no scientific route | 70/70 protected hashes unchanged; full backend regression green | PASS |

No PARTIAL/PENDING row is represented as PASS.

Final executed suites: backend **442 passed, 1 skipped**; frontend unit **17 passed**; Playwright **49 passed** (26 Chromium including 3 visual baselines, 23 Firefox; Firefox visual baselines intentionally not claimed). Protected baseline: **70/70 hashes unchanged**.
