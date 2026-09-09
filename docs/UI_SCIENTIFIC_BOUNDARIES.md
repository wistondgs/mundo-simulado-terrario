# UI Scientific Boundaries

The Lab UI is a read-only client of `/api`. Campaigns are always `READ_ONLY`, and
locked campaigns display `LOCKED` with their config and code hashes. Interactive
controls operate only on `SandboxSession`; the type rejects every control and
configuration edit when `locked_campaign` is true.

`AgentWorldView` includes only recorded channels, visibility mask, normalized
energy and exposed time fraction. `ObserverWorldView` is a different type and may
contain IDs, causal classes, rules, global positions and hidden annotations. The
agent endpoint never serializes observer fields.

Offline replay reads completed traces and does not execute an agent. Its cursor
supports forward, backward, reset and scientific jumps. Data origin remains
visible, and unavailable fields remain `NOT_APPLICABLE`.
