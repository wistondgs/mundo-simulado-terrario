# Execution security model

Mutating HTTP calls use the same local-host and CSRF controls as preregistration. The server derives the actor; clients cannot submit an actor field. Exact SHA-256 roots are mandatory. Export validation rejects path traversal and the durable ledger has append-only SQL protection.
