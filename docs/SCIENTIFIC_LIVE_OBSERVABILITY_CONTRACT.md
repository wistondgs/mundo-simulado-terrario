# SCIENTIFIC_LIVE_OBSERVABILITY_CONTRACT

Schema: `terrario.scientific-live/v1`. Transport-only, read-only observation plane.

## Separation of planes

- **Control plane** (unchanged): authorization, sealed plan, dispatcher, leases, CAS, verification.
- **Observation plane** (this contract): live frames, subscribers, cursor, SSE, snapshot, resume, playback, viewer.

Observation never mutates a trial. World2D scientific mode has no start/step/pause/resume/reset/seed/intervention controls.

## Components

- `terrario/lab/execution/live.py` — `ScientificLivePublisher`: attempt-scoped bounded ring, `Condition` for subscribers, monotonic sequence enforcement, terminal signaling.
- `terrario/lab/execution/dispatcher.py` — publishes each runtime `ScientificFrame` via the publisher; emits terminal only after CAS artifacts are sealed and attempt state is durable.
- `terrario/lab/execution/observation.py` — `live_snapshot()`: live publisher state while running, CAS snapshot once terminal.
- `terrario/lab/api.py` — scientific SSE route mirroring the WorldStream transport pattern.
- Frontend `world2d/scientific-protocol.js` — canonical observation state machine + reducer + SSE client.
- Frontend `views/scientific-world2d.js` — read-only live/playback viewer.

## Frame identity invariant

Every live frame stays bound to `execution_id`, `trial_intent_id`, `attempt_id`, `plan_hash`, plus `preregistration_root_hash`, `software_identity`, `contract_version`, `tick`, `frame_sequence`. No frontend-generated provenance; no identity inferred from URL alone. Backend object identity and payload identity must agree. Mismatch fails closed (`CONTRACT_MISMATCH` / `PROVENANCE_MISMATCH`).

## Atomic frame invariant

World Truth, Agent Observation, and Observer View belong to the same `ScientificFrame`. The atomic frame is the publication unit; the viewer can never render mixed ticks across views.

## Live retention model (bounded)

Configuration constants in `live.py` (no scattered magic values):

- `LIVE_FRAME_RETENTION = 512`
- `SUBSCRIBER_QUEUE_LIMIT = 256`
- `MAX_SUBSCRIBERS_PER_ATTEMPT = 6`
- `HEARTBEAT_INTERVAL_SECONDS = 5.0`
- `MAX_LIVE_PAGE_SIZE = 256`

When retention is exceeded, only the oldest LIVE frames are discarded; the sealed CAS trace is never affected. Live memory is `O(retention_window + subscriber_count)`, not `O(total_frames)`.

## Cursor

Attempt-bound, versioned (`terrario.scientific-live/v1`): `execution_id`, `trial_intent_id`, `attempt_id`, `frame_sequence`. Cross-attempt reuse fails (`CURSOR_WRONG_ATTEMPT`); malformed fails (`CURSOR_INVALID`); older than retention fails (`CURSOR_TOO_OLD`).

## Lifecycle

```
RUNNING ATTEMPT  -> bounded live publication -> SSE / snapshot   (LIVE_UNSEALED)
TERMINAL ATTEMPT -> sealed CAS trace -> ScientificObservationService -> durable playback (SEALED_PLAYBACK)
```

A live frame becoming visible is not yet durable scientific evidence. Terminal is signaled only after required artifacts are sealed. Provenance identity is identical across live frame, terminal state, and playback frame.

## SSE route

`GET /api/v1/scientific-executions/{eid}/trials/{tid}/live/stream?attempt_id={aid}&after_sequence={n}`

Events: `FRAME` (id = frame_sequence), `TERMINAL`, `HEARTBEAT`, `RESYNC_REQUIRED`. Transport only; never mutates runtime.

## Reconnect / gap / resync

- Reconnect within retention: deliver `N+1..current` without duplication or silent omission.
- Cursor no longer retained: explicit `RESYNC_REQUIRED` (HTTP 409 `CURSOR_TOO_OLD` on the JSON route; `RESYNC_REQUIRED` event on SSE), never a silent jump.
- Backend and frontend both enforce `frame_sequence == previous + 1` except on initial snapshot, explicit resync, or transition to playback. A discontinuity puts the frontend in `RESYNCING` and triggers an authoritative snapshot.

## Frontend state machine

Canonical states: `IDLE, CONNECTING, LIVE, RESYNCING, TERMINAL, PLAYBACK, LOST, ERROR`. Deterministic transitions; no parallel booleans. Visible modes: `SCIENTIFIC · LIVE / RESYNCING / TERMINAL / PLAYBACK`. Engineering sandbox remains separately labeled `ENGINEERING_SANDBOX · NOT EVIDENCE`.

## Crash semantics

- Network disconnect: reconnect with cursor.
- Observation service loss / process restart: completed attempts remain available via durable CAS playback; running attempts expose explicit status (no pretend live recovery).
- Trial runtime failure: terminal event with `TRACE_UNAVAILABLE`.

## EvidenceGraph write path

NONE.
