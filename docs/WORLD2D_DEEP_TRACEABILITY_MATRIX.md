# WORLD2D-DEEP-INTEGRATION traceability matrix

A `PASS` requires an implementation path, executable test or measured artifact, and observed result. `OPEN` and `DEFERRED` never count as a pass.

| Gate | Implementation | Exact evidence | Status |
|---|---|---|---|
| Tick 0 / atomic `t+1` | `worldstream/service.py` | `test_tick_zero_and_atomic_three_views`, transition test | PASS |
| Exact Agent observation boundary | service capture contract | `test_observer_profile_does_not_change_agent_observation` | PASS |
| Revision / idempotency | service lock and ACK cache | backend conflict test + authenticated E2E | PASS |
| Concurrent commands | service context lock | `test_concurrent_commands_apply_at_most_one_transition` | PASS |
| Trace v2 integrity / rebuild | `worldstream/trace.py` | corruption, frame seek, checkpoint and index rebuild tests | PASS |
| Indexed seek 100k | `TraceArchive.frame_at` | `scripts/worldstream_performance.py --records 100000 --samples 128`: cold p95 32.92 ms, valid chain | PASS |
| Trace 1M | same | completed 100k predicts 3.99 h, 1.205 GB JSONL + 146 MB index | DEFERRED_WITH_JUSTIFICATION |
| Bounded presentation history | `BoundedFrameHistory` | unit bound/old-frame tests; indexed trace recovery | PASS for invariant; live memory soak OPEN |
| Fault reducer | `protocol.js` | malformed, wrong-world, wrong-base, duplicate/out-of-order, gap tests | PASS |
| Same-tick UI proof | `views/world2d.js` | real SSE live E2E has equal frame/view ticks; delayed-view presentation test | PASS |
| Worker failure | `LiveSandboxService` | explicit `WORLDSTREAM_WORKER_FAILURE` test | PASS |
| Resource limits | service limits | subscriber and active-session exact-limit/recovery tests | PASS |
| Service restart / session lost | restart discovery | `test_restart_marks_non_restorable_session_lost_and_keeps_trace` | PASS at service boundary; browser restart E2E OPEN |
| Canvas/WebGL characterization | production renderers | 32 browser matrix cases, `world2d-performance.spec.js`, report | PASS as characterization |
| 10k three-view target | production renderers | Canvas 37.0 FPS both browsers; WebGL 59.9/58.8 | PASS |
| 50k three-view target | production renderers | Canvas 6.8/6.6; WebGL 17.3/25.0 FPS | FAIL_TARGET, documented |
| WebGL context loss / picking | `ResilientRenderer` | real Chromium/Firefox renderer-resilience E2E; local Canvas recovery, 10k DPR2 pick | PASS after local-canvas replacement fix |
| Live latency | client, API, service, SSE, rAF | ten-cycle real E2E in both browsers, performance report | DATA_PASS; Firefox STEP/START P95 target miss |
| Live/playback separation | World2D panel modes | live E2E and playback click behavior | PASS |
| Timeline / diff / local bookmarks | `timeline.js`, panel | unit and live E2E; non-causal label | PASS |
| Accessibility keyboard flow | semantic panel DOM | `accessibility.spec.js` keyboard-only World2D E2E | PASS |
| Chromium visual regression | snapshots | `visual-qa.spec.js` 3 deterministic baselines | PASS |
| Firefox semantic E2E | Playwright Firefox project | final 43 Firefox tests passed (89 total Playwright) | PASS |
| Firefox visual baseline | none | no stable Firefox screenshot baseline configured | OPEN |
| D2 occlusion / binding UI | no new fixture invented | no valid executable D2 occlusion scenario supplied | OPEN |
| Browser reconnect / multi-viewer / soak | no false proxy | backend coverage exists only where named above | OPEN |
| Scientific execution firewall | sandbox classification / `EvidenceFirewall` | final backend 449 passed, 1 skipped; no scientific run | PASS |
| Reference/Theory/Evidence/CrossGraph/prereg/A0–A4/H-ADAPT integrity | unchanged protected artifacts | protected-hash regression in final backend; H-ADAPT not executed | PASS |

Raw browser and trace measurements are in `WORLD2D_PERFORMANCE_REPORT.md`; browser provisioning, visual, accessibility and fault findings are in `WORLD2D_QA_REPORT.md`.
