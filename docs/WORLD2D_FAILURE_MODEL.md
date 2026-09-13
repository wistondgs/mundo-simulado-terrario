# World2D failure model

Malformed schema, wrong-session input, duplicate/out-of-order input, missing delta base, and client overflow are explicit reducer outcomes. Gaps stop delta application and cause resync. Each panel exposes `SYNCHRONIZED`, `STALE`, `MISSING`, `RESYNCING`, or local error; an old tick is never relabelled synchronized.

Server limits are four active sessions, six intended subscribers per session, 16 MiB frames, 2 GiB traces, 10k query rows, and a 2048-envelope ring. The client ring is 512 frames or 64 MiB. A missing runtime after process restart is not restored from guesses; a valid trace remains playback material.

Known residual: subscriber-count enforcement and durable `SESSION_LOST` discovery after a fresh process are documented but not yet implemented, so their acceptance rows remain PARTIAL.
