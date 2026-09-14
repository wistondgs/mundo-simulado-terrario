# SCIENTIFIC_LIVE_OBSERVABILITY_FAILURE_MODEL

Explicit domain errors; expected scientific states never collapse into generic 500.

| Error | HTTP | Meaning |
|---|---|---|
| `ATTEMPT_NOT_FOUND` | 404 | No live attempt / no sealed trace for the attempt. |
| `ATTEMPT_NOT_RUNNING` | 409 | Publish attempted after terminal. |
| `ATTEMPT_TERMINAL` | 409 | Operation only valid on a running attempt. |
| `CURSOR_INVALID` | 400 | Malformed cursor (schema/type/sequence). |
| `CURSOR_WRONG_ATTEMPT` | 400 | Cursor bound to a different execution/trial/attempt. |
| `CURSOR_TOO_OLD` | 409 | Requested sequence evicted from live retention. |
| `RESYNC_REQUIRED` | 409 / SSE event | Authoritative snapshot required; never a silent jump. |
| `CONTRACT_MISMATCH` | 400 | Non-monotonic sequence or frame/attempt identity mismatch. |
| `SUBSCRIBER_LIMIT` | 429 | `MAX_SUBSCRIBERS_PER_ATTEMPT` reached. |
| `TRACE_UNAVAILABLE` | 409 | Terminal artifact missing. |
| `TRACE_CORRUPTED` | 409 | Sealed trace fails integrity/identity check; fails closed. |
| `ARTIFACT_NOT_SEALED` | 409 | Terminal claimed before required artifact sealing. |

## Race ownership

- Publisher state is guarded by a per-attempt `RLock` + `Condition`; no global lock.
- Locks are never held during slow I/O or network writes (SSE writes happen outside the attempt lock).
- Terminal event cannot precede the state/artifact invariants it claims: the dispatcher seals CAS artifacts and updates durable attempt state before `end_attempt`.

## Bounded-resource guarantees

- Slow subscriber cannot block publication (publication is O(1) append + notify; subscriber reads pull-based).
- Subscriber count is capped; disconnect cleanup releases the slot.
- Live ring is bounded by `LIVE_FRAME_RETENTION`; subscriber queues bounded by `SUBSCRIBER_QUEUE_LIMIT`.

## Fail-closed cases (tested)

- execution A cannot read B; trial A cannot read B; attempt A cursor cannot resume B.
- incorrect plan binding fails; malformed cursor fails; stale cursor triggers resync.
- corrupt CAS playback fails closed (`TRACE_CORRUPTED`).
- subscriber limit enforced; slow client cannot exhaust unbounded memory.
