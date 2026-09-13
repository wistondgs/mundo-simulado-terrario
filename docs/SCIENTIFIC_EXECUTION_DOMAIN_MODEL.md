# Scientific execution domain model

Versioned contracts define requests, authorizations, plans, environment/software snapshots, raw artifacts and verification reports. SQLite projections are durable while append-only hash-chained events provide reconstruction. Existing trial intents, jobs and attempts are reused rather than introducing a parallel queue.
