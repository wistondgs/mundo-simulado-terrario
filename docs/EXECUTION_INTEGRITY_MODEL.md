# Execution integrity model

Verification checks the event hash chain, every referenced CAS blob, the exact preregistration root and sealed plan/root identities. It returns `PASS`, `FAIL`, `WARNING`, `INCOMPLETE`, `DEVIATED`, `ABORTED` or `UNVERIFIABLE`. `COMPLETED` alone has no scientific validity meaning.
