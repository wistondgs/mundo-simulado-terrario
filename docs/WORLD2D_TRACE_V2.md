# Sandbox trace v2

Schema: `terrario.sandbox.trace/v2`. `trace.v2.jsonl` is append-only and authoritative. Each record contains monotonic sequence, tick, previous hash, and its SHA-256 hash. Persistence and fsync happen before publication.

SQLite stores rebuildable offsets indexed by tick, sequence, event type, and entity ID. Generic seek reads one indexed record rather than scanning the trace; frame seek constrains that lookup to frame-bearing records so a status/event at the same tick cannot replace the logical frame. Checkpoints are complete frames at 256-tick intervals and terminal state. Their source sequence is recorded in the derived index and restored when the index is rebuilt. Index corruption is rebuilt from JSONL; a broken chain raises `TRACE_INTEGRITY_FAILURE`.

The legacy v1 run JSON remains readable through `/api/sandbox`; unavailable v2 identity/index fields are not invented.
