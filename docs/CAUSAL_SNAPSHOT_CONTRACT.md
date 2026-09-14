# Causal Snapshot Contract

Schema: `terrario.causal-fork-snapshot/v1`. Payload is canonical JSON in CAS
and includes materialized scenario, world, rules, scheduler, A0 generator and
counter, tick, terminal state, and causal trace prefix. Payload and envelope
hashes are independently verified before restore. Snapshots are insert-only.

Observer data, wall-clock fields and viewer cursors are excluded. A snapshot is
rejected on schema, payload, software, execution, attempt, trial, plan, or
preregistration binding mismatch.
