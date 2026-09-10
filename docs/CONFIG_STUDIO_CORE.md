# Config Studio Core

Config Studio uses one immutable `LabConfiguration` beneath typed controls and structured display. It exposes validation and semantic diff endpoints but no experiment-run endpoint.

Validation findings distinguish `VALIDATION_ERROR`, `SCIENTIFIC_WARNING`, and compatibility/protocol categories. Structural errors block; warnings such as `SANDBOX_ONLY`, `NOT_PREREGISTERED`, and incomplete proxies remain visible without becoming evidence claims.

Diffs separate scenario, difficulty, observation, action, intervention, metric, seeds, observer, agent, and variant changes from UI preferences. UI layout never affects scientific hashes. The in-memory repository prohibits silent overwrite and creates child records for edits/transitions.

Current endpoints:

- `GET /api/worlds`
- `GET /api/worlds/{D0..D4}`
- `GET /api/studio/d2`
- `POST /api/config/validate`
- `POST /api/config/diff`

POST validation/diff operates on a copy of the D2 draft and does not persist or execute it. Sandbox Runner and Experiment Composer remain outside this phase.
