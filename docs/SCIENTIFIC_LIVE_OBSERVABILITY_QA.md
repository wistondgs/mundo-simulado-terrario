# SCIENTIFIC_LIVE_OBSERVABILITY_QA

Branch: `experiment/scientific-live-observability-01`. PRE_HEAD `2170748`.

## Acceptance gates

| Gate | Result | Evidence |
|---|---|---|
| A Previous runtime golden path | PASS | `test_scientific_execution_gate.py` |
| B Previous durable playback | PASS | `test_terminal_scientific_playback_survives_dispatcher_memory_loss` |
| C Tick 0 live | PASS | `test_publish_tick_zero_and_later_frames`, E2E SSE |
| D Later frames live | PASS | `test_publish_tick_zero_and_later_frames` |
| E Monotonic frame sequence | PASS | `test_monotonic_frame_sequence` |
| F Reconnect within retention | PASS | `test_reconnect_within_retention_no_duplication` |
| G Stale cursor -> RESYNC_REQUIRED | PASS | `test_stale_cursor_resync_required_via_api`, E2E |
| H Resync | PASS | frontend unit `RESYNCING -> LIVE` |
| I Slow consumer bounded | PASS | `test_slow_subscriber_does_not_block_publication` |
| J Terminal event | PASS | `test_terminal_event_after_sealing`, E2E SSE |
| K Live -> Terminal -> Playback | PASS | `test_live_to_terminal_to_playback_provenance_continuity`, E2E golden |
| L Provenance continuity | PASS | `test_live_to_terminal_to_playback_provenance_continuity` |
| M Durable playback after service reconstruction | PASS | `test_durable_playback_after_service_reconstruction` |
| N Cross-trial isolation | PASS | `test_cross_trial_isolation`, E2E |
| O Sandbox isolation | PASS | `test_live_package_has_no_evidence_or_sandbox_imports`, E2E badge |
| P Scientific viewer read-only | PASS | E2E golden (no control buttons) |
| Q Chromium golden E2E | PASS | `scientific-live.spec.js` (4/4) |
| R Firefox core E2E | PASS | `scientific-live.spec.js` (4/4) |
| S Protected baseline | PASS | full backend suite (see final report) |
| T EvidenceGraph write path | NONE | `test_live_package_has_no_evidence_or_sandbox_imports` |

## Test runs

- Backend targeted: `tests/test_scientific_live_observability.py` — 18 passed.
- Backend integration: `test_scientific_execution_gate.py`, `test_scientific_state_contract.py` — passed.
- Frontend unit: `tests_frontend/unit/scientific-live.test.js` — 10 passed; full unit suite 30 passed.
- Chromium E2E: `tests_frontend/e2e/scientific-live.spec.js` — 4 passed.
- Firefox E2E: same — 4 passed.
