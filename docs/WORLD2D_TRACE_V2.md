# Sandbox trace v2

Schema: `terrario.sandbox.trace/v2`. `trace.v2.jsonl` is append-only and authoritative. Each record contains monotonic sequence, tick, previous hash, and its SHA-256 hash. Persistence and fsync happen before publication.

SQLite stores rebuildable offsets indexed by tick, sequence, event type, and entity ID. Seek reads one indexed record rather than scanning the trace. Checkpoints are complete frames at 256-tick intervals and terminal state. Index corruption is rebuilt from JSONL; a broken chain raises `TRACE_INTEGRITY_FAILURE`.

The legacy v1 run JSON remains readable through `/api/sandbox`; unavailable v2 identity/index fields are not invented.
