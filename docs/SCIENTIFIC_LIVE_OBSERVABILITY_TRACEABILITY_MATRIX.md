# SCIENTIFIC_LIVE_OBSERVABILITY_TRACEABILITY_MATRIX

| REQ | IMPLEMENTATION | TEST | STATUS |
|---|---|---|---|
| Live frame publisher (bounded, attempt-scoped) | `execution/live.py` `ScientificLivePublisher` | `test_publish_tick_zero_and_later_frames`, `test_bounded_retention_discards_oldest_live_only` | PASS |
| Tick 0 + later frames | `dispatcher.py` sink -> `live.publish` | `test_publish_tick_zero_and_later_frames` | PASS |
| Monotonic sequence | `live.publish` sequence check | `test_monotonic_frame_sequence` | PASS |
| Bounded retention | `live.py` ring `maxlen` | `test_bounded_retention_discards_oldest_live_only` | PASS |
| Bounded subscriber queue / limit | `live.py` `acquire_subscriber` | `test_bounded_subscriber_limit_enforced` | PASS |
| Snapshot running attempt | `live.snapshot` / `observation.live_snapshot` | `test_snapshot_running_attempt` | PASS |
| Connect SSE | `lab/api.py` scientific SSE route | E2E `live SSE stream...` | PASS |
| Reconnect within retention | `live.frames_after` | `test_reconnect_within_retention_no_duplication` | PASS |
| Stale cursor -> RESYNC_REQUIRED | `CursorTooOld` / SSE `RESYNC_REQUIRED` | `test_stale_cursor_resync_required_via_api`, E2E | PASS |
| Wrong-attempt cursor rejected | `CursorWrongAttempt` | `test_wrong_attempt_cursor_rejected`, E2E | PASS |
| Terminal event | `live.end_attempt` after CAS seal | `test_terminal_event_after_sealing`, E2E | PASS |
| Live -> terminal transition | dispatcher terminal signaling | `test_terminal_event_after_sealing` | PASS |
| Terminal CAS playback | `observation.playback` | `test_durable_playback_after_service_reconstruction` | PASS |
| Provenance equality live/playback | identity binding in publisher + CAS | `test_live_to_terminal_to_playback_provenance_continuity` | PASS |
| Corrupt trace fails closed | `TraceCorrupted` | `test_corrupt_trace_fails_closed` | PASS |
| Cross-trial isolation | attempt-scoped keying | `test_cross_trial_isolation`, E2E | PASS |
| Subscriber cleanup | `release_subscriber` | `test_subscriber_cleanup_on_release` | PASS |
| Slow subscriber handling | pull-based, O(1) publish | `test_slow_subscriber_does_not_block_publication` | PASS |
| Publish after terminal rejected | `AttemptNotRunning` | `test_publish_after_terminal_rejected` | PASS |
| Frontend state machine | `scientific-protocol.js` transitions | `scientific-live.test.js` | PASS |
| Gap detection frontend | `reduceScientificEvent` | unit `frame gap forces RESYNCING` | PASS |
| Provenance display | `scientific-world2d.js` `_renderProvenance` | E2E golden | PASS |
| Read-only viewer | no control buttons | E2E golden | PASS |
| Terminal -> playback seek | `openPlayback`/`seek` | E2E golden | PASS |
| EvidenceGraph write path NONE | no evidence imports | `test_live_package_has_no_evidence_or_sandbox_imports` | NONE |
