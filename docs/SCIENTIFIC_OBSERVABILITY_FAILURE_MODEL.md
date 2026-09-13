# Scientific observability failures

Unknown attempts fail as `ATTEMPT_NOT_FOUND`; unavailable trace as `TRACE_NOT_AVAILABLE`; malformed bytes or identity mismatch as `TRACE_CORRUPTED`. Playback never falls back across execution, trial or attempt. SSE-specific `CLIENT_LAGGED` and `RESYNC_REQUIRED` are deferred with the SSE bridge.
