# WorldStream protocol v1

Schema: `terrario.worldstream/v1`. Identity fields are session, world instance, scenario, world/agent seeds, agent identity, tick, sequence, simulation time, origin, trace, and schema version.

Commands are POSTed with a unique `command_id` and `expected_session_revision`. A first valid command increments the revision; a repeated ID returns the original ACK without effects; stale revisions return 409. SSE is opened with authenticated `fetch`, enabling the CSRF header. Messages are `SESSION_OPEN`, `SNAPSHOT`, `DELTA`, `EVENT`, `STATUS`, `COMMAND_ACK`, `HEARTBEAT`, `GAP`, `RESYNC`, and `SESSION_END`.

Heartbeat is five seconds. The client reconnects with exponential delay from 250 ms to 5 s. A delta is applied only when `base_sequence` equals the current frame sequence; overflow or mismatch requests resync.
