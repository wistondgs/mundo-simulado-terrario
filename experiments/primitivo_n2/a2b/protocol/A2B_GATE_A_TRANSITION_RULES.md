# A2b prospective Gate A transition rules

These rules govern new A2b evidence only. They do not reconstruct A1/A2
history, what an investigator knew, or the historical G0/G5 conditions.

## Outcome states

- `RAW_RESULT_STATUS = SEALED_VALID | INCOMPLETE | INVALID`.
- `POST_SEAL_ADJUDICATION_STATUS = PASS | FAIL | INDETERMINATE | NOT_STARTED`.
- `A2B_BLIND_REPLICATION = PASS | FAIL | INDETERMINATE | INVALID` maps to the
  post-seal status only after raw results have been sealed: `PASS` and `FAIL`
  map directly, `INDETERMINATE` remains unresolved, and any invalid raw run
  maps to `INVALID`.

`PASS` requires a sealed-valid raw result and a post-seal comparison satisfying
the sealed SPEC §14 equality criteria. `FAIL` requires a sealed-valid raw
result and a comparison failure under those criteria. `INDETERMINATE` requires
a sealed-valid raw result but an adjudication blocked by a documented
SPEC-level ambiguity. `INVALID` includes a broken blind protocol, missing
mandatory artifact, execution failure, premature disclosure, or an unresolved
value-affecting ambiguity.

## Gate A effect

The prospective Gate condition requires both a successful new A2b blind
replication and the separate A1 investigator attestation. Therefore:

```text
IF A2B_BLIND_REPLICATION = PASS
AND A1_ATTESTATION is unresolved
THEN G0 = PENDING_PROVENANCE
     G5 = PENDING_PROVENANCE
     GATE_A = PENDING_PROVENANCE.
```

A2b never automatically changes G0 or G5. An A2b failure is new evidence
about the A2b replication requirement only, never proof about A1/A2 history.
`INVALID` has no scientific adjudication; `INDETERMINATE` leaves the new
replication requirement unresolved. Gate B remains prohibited; these rules do
not authorize it.
