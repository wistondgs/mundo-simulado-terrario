# Execution state machine

`REQUESTED → VALIDATING → AUTHORIZED → PLANNED → READY → RUNNING` is the normal path. `PAUSING` and `STOPPING` settle only at a certified safe boundary. Terminal states are `COMPLETED`, `FAILED`, `CANCELLED` and `ABORTED`; expired leases enter `RECOVERY_REQUIRED` rather than replaying work. Commands carry `command_id` and `expected_revision`.
