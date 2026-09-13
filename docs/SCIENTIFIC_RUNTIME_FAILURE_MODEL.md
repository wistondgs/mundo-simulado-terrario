# Scientific runtime failure model

Only an atomically claimed `READY` job can materialize. Materialization errors record `TRIAL_MATERIALIZATION_FAILED`, retain any prior raw data, and do not mark an execution complete. Existing execution leases and recovery remain authoritative. The dispatcher has no fallback scenario, seed, device or agent configuration.
