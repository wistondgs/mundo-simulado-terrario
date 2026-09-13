# Recovery and bundles

Lease loss is detected by expiry and produces `RECOVERY_REQUIRED` or `ABORTED` without silent replay. Recovery is idempotent because events, commands, artifacts and authorization consumption are immutable. Export produces a `terrario.scientific-execution-bundle/v1` ZIP containing the preregistration bundle, authorization, execution ledger and referenced CAS bytes. Validation rejects unsafe paths and hash failures.
