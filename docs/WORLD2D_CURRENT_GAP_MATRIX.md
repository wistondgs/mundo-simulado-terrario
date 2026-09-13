# World2D current gap matrix

This matrix is a closure-control document. `DEFERRED_WITH_JUSTIFICATION` is not an acceptance PASS.

| Gate / concern | Status | Verifiable evidence | Remaining boundary or exact next test |
|---|---|---|---|
| Browser infrastructure | CLOSED | Official Playwright Chromium 153 / Firefox 155 run locally; provenance in `WORLD2D_QA_REPORT.md`. | Temporary extracted shared libraries are a local test prerequisite, not an application dependency. |
| Real live sandbox, SSE, trace playback | CLOSED | `worldstream-live.spec.js` drives the live backend through create, tick 0, commands, stop and playback; final Playwright 89/89. | No remaining known failure in this covered flow. |
| Same-tick three views | CLOSED | Live E2E asserts all three view and frame ticks equal at tick 1; delayed injected Agent view is visibly `STALE`. | A network-delay per-view transport injector remains a future stronger version of the presentation fault injection. |
| Agent/World Truth firewall | CLOSED | `test_observer_profile_does_not_change_agent_observation`; live UI labels no direct identity mapping. | D2 occlusion UI scenario remains OPEN below. |
| Command revision and idempotency | CLOSED | `test_revision_conflict_and_idempotent_command`, concurrent-command test, authenticated E2E conflict. | Two-viewer concurrent browser-control test is OPEN. |
| Reducer fault matrix | CLOSED for malformed/wrong-session/wrong-world/duplicate/out-of-order/wrong-base/gap | `worldstream.test.js` plus resync backend test. | Full live reconnect-duration matrix is OPEN. |
| Worker failure / resource limits | CLOSED | explicit `WORLDSTREAM_WORKER_FAILURE`, active-session and subscriber-limit tests. | Browser UI display of a deliberately killed worker is OPEN. |
| Server restart / SESSION_LOST | CLOSED at service boundary | `test_restart_marks_non_restorable_session_lost_and_keeps_trace`. | Browser-process restart and playback offer E2E is OPEN; backend proof is not relabelled browser proof. |
| WebGL context loss and picking | CLOSED | `world2d-renderer-resilience.spec.js`: WebGL loss → local Canvas fallback, 10k DPR2 pick in Chromium and Firefox. | Panel-specific independent rendering-fault matrix is OPEN. |
| Accessibility keyboard / semantic DOM | CLOSED | keyboard-only live and playback E2E; tick/session/view status and forensic regions named. | Screen-reader manual audit is outside this automated evidence. |
| Chromium visual baselines | CLOSED | Three deterministic baselines regenerated and pass. | Firefox pixel baselines are OPEN. |
| Render characterization | CLOSED as characterization | Actual 1/3-view Canvas2D/WebGL2 matrix, 100–50k, both browsers, 36 samples/case. | 50k/three views fails 30 FPS; it is a documented limit, not a target pass. |
| Renderer selection | CLOSED | Canvas2D primary based on complete Agent rendering and 10k/three-view 37 FPS; WebGL2 measured accelerated path. | WebGL Agent channel/mask visual+picking parity is OPEN before promotion. |
| Live latency | OPEN_BROWSER_TARGET_MISS | Chromium meets the orientation target; Firefox STEP p50 191.2 ms / p95 231.3 ms and START p95 205.0 ms. | Profile Firefox command/presentation path, then repeat with a larger sample. |
| Browser memory / backpressure soak | OPEN | Bounded ring/history unit invariants and trace authority are verified. | Run thousands-of-live-ticks browser soak recording queue/coalescing/drop/memory. |
| Trace 10k and 100k | CLOSED | Production trace archive: 10k and 100k writes, index/checkpoints, 64/128 seek samples, valid hash chains. | Sequential-playback and RSS profiling are not included in this harness. |
| Trace 1M | DEFERRED_WITH_JUSTIFICATION | Measured 100k predicts ~3.99 h, 1.205 GB JSONL + 146 MB index. | Execute only with a dedicated long-run budget; not a PASS. |
| D2 occlusion / lifecycle / binding UI | OPEN | No fabricated scenario claim. | Build/use an existing valid D2 occlusion fixture, then drive UI identity/visibility timeline E2E. |
| Security hostile strings | OPEN | Existing general workspace security boundary remains unchanged. | Add World2D object/scenario/event/bookmark hostile-string E2E in both browsers. |
| Historical scientific firewall | CLOSED | Final backend **449 passed, 1 skipped** includes the protected-hash baseline; no scientific run invoked. | H-ADAPT remains integrity-only and unexecuted. |

The phase cannot be declared fully closed while any row marked `OPEN`, `OPEN_BROWSER_TARGET_MISS`, or `DEFERRED_WITH_JUSTIFICATION` remains.
