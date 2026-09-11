# LAB-UI-02C API

All endpoints are local Lab design/read endpoints. None is a scientific execution endpoint.

## Read models

- `GET /api/capabilities` — taxonomy plus A0–A4 evidence-backed matrix.
- `GET /api/agents` and `GET /api/agents/{id}` — verified static descriptors and real parameter counts.
- `GET /api/agents/{id}/runtime?run_id=...` — snapshot only for an existing sandbox trace; otherwise `NOT_EXPOSED`.
- `GET /api/metrics` — metric registry with construct/proxy/status/limitations.
- `GET /api/observer/profiles` — explicit profiles and channel registry.
- `GET /api/experiment-drafts/{id}` — the latest durable immutable version of a draft.

## Design operations

- `POST /api/compatibility` — technical and cognitive compatibility report.
- `POST /api/metrics/applicability` — required-signal check.
- `POST /api/observer/estimate` — labeled storage estimate or `UNKNOWN`.
- `POST /api/experiment-drafts/validate` — returns `ExperimentDraft`, hash, and findings; does not persist or execute.
- `POST /api/experiment-drafts` — stores a durable versioned draft; duplicate IDs/hashes return provenance conflict.
- `POST /api/experiment-drafts/diff` — derives an unpersisted child and reports scientific/UI differences.
- `POST /api/trial-matrices/build` — materializes and durably stores deterministic `TrialIntent` records while always returning `execution_performed: false`.

Durability is provided by `LAB-PERSISTENCE-01`. It changes storage, not scientific authority: these routes still cannot approve, preregister, execute, analyze, or publish evidence.

The server resolves upstream review status. Client payloads cannot submit an approval state. Unknown fields are rejected. There is no `/execute` route.
