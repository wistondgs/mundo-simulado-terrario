# A1b prospective Gate A transition rules v1

These rules are governed by `GATE_A_A1B_PROSPECTIVE_AMENDMENT_v1.md`, which is
sealed in the same commit. The two documents form one normative unit; where
they conflict, the amendment governs.

- **References.** Section numbers written "§N" refer to the amendment, and
  "SPEC §N" refers to SPEC A. The sequence names (`SHOT_START`, `G5_SEAL` and so
  on) and the determination session are defined in amendment §1.
- **Scope.** These rules apply to A1b evidence only:
  - They do not reconstruct A1 or A2 history, or what any investigator knew.
  - They do not change the historical classifications of A1 or A2.
  - They do not reopen or re-adjudicate A2b.

## 1. Outcome states

```text
A1B_RAW_RESULT_STATUS              = NOT_STARTED | IN_PROGRESS | SEALED_VALID | INCOMPLETE | INVALID
A1B_POST_SEAL_ADJUDICATION_STATUS  = NOT_STARTED | NOT_APPLICABLE | PASS | FAIL | INDETERMINATE
A1B_G0                             = NOT_EVALUATED | PASS | FAIL
A1B_G5                             = NOT_EVALUATED | PASS | FAIL
A1B_BLIND_REPLICATION              = NOT_STARTED | IN_PROGRESS | PASS | FAIL | INDETERMINATE | INVALID
A1B_DIAGNOSTIC                     = NONE | a list with one class per divergence: ERROR_REPLICA | ERROR_REFERENCIA | AMBIGUEDAD_SPEC
A1B_DIAGNOSTIC_ADJUDICATION        = NOT_APPLICABLE | PENDING | ADJUDICATED
GATE_A                             = PENDING_PROVENANCE | REPLICADO
GATE_A_CLOSABLE_UNDER_V1           = YES | NO
```

- **No other `GATE_A` values.** Under this version `GATE_A` has no other value.
- **One final seal.** The complete block, with its values, is sealed once as
  `FINAL_STATUS_SEAL` (§12).
- **Status of later changes.** After `FINAL_STATUS_SEAL`, any change is a
  recorded revision, and only amendment §15 permits one.

## 2. Raw result

The determination session sets `A1B_RAW_RESULT_STATUS` from the sealed records,
in `CUSTODY_DETERMINATION_SEAL`.

| `A1B_RAW_RESULT_STATUS` | Condition |
| --- | --- |
| `NOT_STARTED` | Before `SHOT_START`. |
| `IN_PROGRESS` | From `SHOT_START` until `CUSTODY_DETERMINATION_SEAL`. |
| `SEALED_VALID` | `G5_SEAL` is complete, the capture contains every SPEC §0.5 deliverable (`por_sistema.jsonl`, `resumen.json`, the ambiguity register, and the language and version used), and no `INVALID` condition holds. |
| `INCOMPLETE` | C's session ended without every SPEC §0.5 deliverable, including when the same session cannot be resumed after an interruption (§6), and no `INVALID` condition holds. The capture is still frozen and sealed (§12). |
| `INVALID` | At least one of the conditions below holds. |

A raw run is `INVALID` if any of the following holds:

- **The blind protocol was broken after `SHOT_START`.** This covers:
  - a failed startup check;
  - a firewall breach (§13);
  - a non-pre-registered input judged a breach (§11);
  - an isolation probe shown to be false;
  - a second role C session, including a prohibited resume (§6).
- **Premature disclosure.** Result material reached role B or role C before
  `G5_SEAL`.
- **Execution failure.** An execution failure prevented a compared deliverable
  from being produced.
- **Missing custody artifact.** A mandatory custody artifact is missing: a
  record or capture that amendment §10–§12 requires.
- **Indeterminate compared field.** A compared field has no determinate value,
  for example a value left open between readings, so no comparison under SPEC
  §14 is possible. This is the A2b rules' "unresolved value-affecting ambiguity"
  at the level of the raw run.
- **Undeliverable bytes.** The bytes C delivered cannot be established (§12).
- **OEIS contamination.** An OEIS anchor value altered a compared field (§7).
- **Prior work.** There is evidence that scientific work for the attempt, such
  as code or outputs, existed before `SHOT_START` (§6).

## 3. Post-seal adjudication

The post-seal adjudication happens only if the raw result is `SEALED_VALID`. If
the raw result is `INCOMPLETE` or `INVALID`, then
`A1B_POST_SEAL_ADJUDICATION_STATUS = NOT_APPLICABLE`.

Role D compares the frozen A1b result with the frozen reference artifacts (§0):

- using the comparator sealed in `COMPARATOR_SEAL`;
- under the SPEC §14 criteria and the normalizations of
  `SUMMARY_SEMANTIC_SCHEMA.md`, including F1–F3;
- in the order of GATE_A_PROTOCOL points 3–5.

Equal aggregates with unequal per-system records is not `PASS`.

Each compared field is classified as one of:

- **equal**: equal under those criteria;
- **discordant**: unequal under those criteria;
- **undecidable**: the frozen criteria do not determine whether it is equal,
  because of a documented SPEC-level ambiguity in SPEC §14 or F1–F3.

The status is assigned by the first rule that applies:

1. **`INDETERMINATE`.** Control 12.4 fails (§7; SPEC §12: "hay un error antes
   de interpretar cualquier resultado"). Any discordances are still listed.
2. **`FAIL`.** At least one field is discordant. Every discordance is listed,
   together with the first discordant `F` and field.
3. **`INDETERMINATE`.** Nothing is discordant, but at least one field is
   undecidable.
4. **`PASS`.** Every compared field is equal.

The first output sealed in `ADJUDICATION_SEAL` governs (§12).

A comparator defect adjudicated by the investigator never changes these
statuses. It is recorded as a separate finding in `FINAL_STATUS_SEAL`, and it
sets `GATE_A_CLOSABLE_UNDER_V1 = NO` (§12).

`A1B_BLIND_REPLICATION` is set as follows:

| Raw result | Post-seal status | `A1B_BLIND_REPLICATION` |
| --- | --- | --- |
| `NOT_STARTED` | `NOT_STARTED` | `NOT_STARTED` |
| `IN_PROGRESS` | `NOT_STARTED` | `IN_PROGRESS` |
| `SEALED_VALID` | `NOT_STARTED` | `IN_PROGRESS` |
| `SEALED_VALID` | `PASS` | `PASS` |
| `SEALED_VALID` | `FAIL` | `FAIL` |
| `SEALED_VALID` | `INDETERMINATE` | `INDETERMINATE` |
| `INCOMPLETE` or `INVALID` | `NOT_APPLICABLE` | `INVALID` |

- **`INVALID`** has no scientific adjudication.
- **`FAIL` and `INDETERMINATE`** are scientific evidence, and they stay in the
  record.
- **SPEC §14 result labels.** `PASS` is `REPLICADO`. Under this version, `FAIL`
  is `NO_REPLICADO` (§5).

## 4. Diagnostic

When `A1B_BLIND_REPLICATION = FAIL`:

- **Classification.** Role D classifies each divergence under SPEC §14 and
  GATE_A_PROTOCOL point 6 as `ERROR_REPLICA`, `ERROR_REFERENCIA` or
  `AMBIGUEDAD_SPEC`. This sets `A1B_DIAGNOSTIC`, and sets
  `A1B_DIAGNOSTIC_ADJUDICATION = PENDING`.
- **Adjudication.** The investigator adjudicates the classification. The status
  then becomes `A1B_DIAGNOSTIC_ADJUDICATION = ADJUDICATED`.
- **No correction.** The diagnostic applies no correction. Every correction
  that SPEC §14 describes needs a repair, a rerun, a new SPEC version or a
  reference change. This version authorizes none of them.

In every other case, `A1B_DIAGNOSTIC = NONE` and
`A1B_DIAGNOSTIC_ADJUDICATION = NOT_APPLICABLE`.

## 5. Unresolved value-affecting ambiguity

**Basis.** GATE_A_PROTOCOL point 8 lets Gate A close only "with no unresolved
ambiguity". `NO_UNRESOLVED_VALUE_AFFECTING_AMBIGUITY` holds only if no
ambiguity remains for which an admissible alternative reading of the frozen
SPEC would change a value compared under SPEC §14. An admissible reading is one
that the frozen SPEC's text does not exclude.

**Before the comparison.** The determination session classifies each entry of
A1b's SPEC §13 ambiguity register as value-affecting or not, giving its
reasoning. The classification is sealed in `CUSTODY_DETERMINATION_SEAL`.

**After the comparison.** Role D may add only readings that the comparison
reveals and the register does not record. Each addition states:

- the alternative reading;
- the compared field it affects.

**Adjudication.** The investigator adjudicates both lists, and the outcome is
sealed in `FINAL_STATUS_SEAL`.

**Cases:**

- **Fixed or covered readings.** A reading already fixed by the frozen SPEC, or
  a variant already covered by F1–F3, is not unresolved.
- **Silent resolution.** A value-affecting reading that C resolved silently,
  without recording it, is recorded as a replica protocol defect. It counts as
  unresolved.
- **Agreement with the reference.** A1b agreeing with the reference does not
  resolve a value-affecting ambiguity. The SPEC's own remedy is a new
  specification and a rerun (SPEC §14, AMBIGUEDAD_SPEC), and this version
  authorizes neither.

## 6. Custody statuses

`A1B_G0` and `A1B_G5` follow the evidence standard of amendment §15.

- **Who and when.** The determination session determines them from the sealed
  records alone. The investigator certifies them. Both are sealed in
  `CUSTODY_DETERMINATION_SEAL`, before role D accesses any reference artifact,
  comparator output or OEIS.
- **Before that seal.** Both are `NOT_EVALUATED`. If the shot never starts, they
  stay `NOT_EVALUATED`.
- **Failed startup check.** It is determined as `A1B_G0 = FAIL` in
  `CUSTODY_DETERMINATION_SEAL`.
- **What is not `PASS`:**
  - a requirement without contemporaneous sealed evidence;
  - a requirement whose evidence was sealed out of order
    (`LATE_PROVENANCE_EVIDENCE_CANNOT_RETROACTIVELY_REPAIR_CUSTODY_ORDER`).
- **Breach evidence found after `ADJUDICATION_SEAL`.**
  - It sets the affected status to `FAIL` and `GATE_A_CLOSABLE_UNDER_V1 = NO`.
  - It never alters `A1B_POST_SEAL_ADJUDICATION_STATUS` or
    `A1B_BLIND_REPLICATION`.
  - The revision is recorded with its source, and the earlier determination is
    kept.

## 7. Gate A effect

These rules and the amendment supersede only part of the A2b transition rules
(§4):

- the dependency on "the separate A1 investigator attestation";
- the implication block that states it.

```text
IF   A2B_BLIND_REPLICATION = PASS
AND  A1B_BLIND_REPLICATION = PASS
AND  A1B_G0 = PASS
AND  A1B_G5 = PASS
AND  NO_UNRESOLVED_VALUE_AFFECTING_AMBIGUITY
AND  the GATE_A_PROTOCOL requirements not superseded by the amendment are met, including points 2 and 8
THEN GATE_A may be recorded as REPLICADO
ELSE GATE_A = PENDING_PROVENANCE
```

`GATE_A_CLOSABLE_UNDER_V1` records whether that condition can still become true
under this version:

| A1b state | `GATE_A` | `GATE_A_CLOSABLE_UNDER_V1` |
| --- | --- | --- |
| `A1B_BLIND_REPLICATION` is `NOT_STARTED` or `IN_PROGRESS` | `PENDING_PROVENANCE` | `YES` |
| `PASS`, with `A1B_G0` and `A1B_G5` `PASS`, and the ambiguity condition or a protocol requirement not yet determined | `PENDING_PROVENANCE` | `YES` |
| `PASS`, and every condition holds | `REPLICADO`, once recorded by the investigator | `YES` |
| `PASS`, but any of these holds: `A1B_G0` or `A1B_G5` is not `PASS`; the ambiguity condition fails; a protocol requirement is not met; a comparator defect is adjudicated | `PENDING_PROVENANCE`. The A1b result is kept as evidence. | `NO` |
| `FAIL`, before or during the diagnostic (`A1B_DIAGNOSTIC_ADJUDICATION = PENDING`) | `PENDING_PROVENANCE`. Gate A does not close until the diagnostic is adjudicated. | `NO` |
| `FAIL`, diagnostic `ADJUDICATED` | `PENDING_PROVENANCE` | `NO` |
| `INDETERMINATE` | `PENDING_PROVENANCE` | `NO` |
| `INVALID` | `PENDING_PROVENANCE`, with no scientific adjudication | `NO` |

- **No automatic failure.** No A1b outcome converts into a Gate A failure. This
  version has no `GATE_A = FAIL` state.
- **No corrections under this version.** `REPLICADO_CON_CORRECCIONES` is not
  reachable on A1b evidence under this version.
- **One shot.** The shot is consumed at `SHOT_START`. There is no retry under
  this version.
- **New version required.** Any consequence of an A1b outcome that needs a
  repair, a rerun, a new SPEC version, a reference change or a new A1b attempt
  needs a new prospective amendment version, sealed before it. The prior
  attempts are declared as §6 requires.
- **Permanent record.** Every A1b attempt and every pre-shot record stays in the
  permanent record, with its sealed statuses (§6).
- **No reopening.** No A1b outcome reopens A2b or changes the historical
  classifications of A1 or A2.
- **Recording.** The investigator records any change of `GATE_A` in a separate,
  dated record. These rules do not modify `GATE_A_RESULT.json`.

## 8. Gate B

`GATE_A = REPLICADO` satisfies the Gate A precondition of GATE_A_PROTOCOL
point 9. It does not open, prepare or execute Gate B, which requires a separate
explicit authorization. Until then, `GATE_B = BLOCKED`, and these rules do not
authorize it.

## 9. State at the seal of these rules

Identical to amendment §2:

```text
A1 (historical)                   = CORROBORATIVE · SCIENTIFIC_BLINDNESS_SUPPORTED · CUSTODY_NOT_FULLY_CERTIFIABLE
A2 (historical)                   = DEPENDENT_CORROBORATION · LINEAGE_NOT_AUDITABLE
A2B_BLIND_REPLICATION             = PASS
A1B_RAW_RESULT_STATUS             = NOT_STARTED
A1B_POST_SEAL_ADJUDICATION_STATUS = NOT_STARTED
A1B_G0                            = NOT_EVALUATED
A1B_G5                            = NOT_EVALUATED
A1B_BLIND_REPLICATION             = NOT_STARTED
A1B_DIAGNOSTIC                    = NONE
A1B_DIAGNOSTIC_ADJUDICATION       = NOT_APPLICABLE
GATE_A                            = PENDING_PROVENANCE
GATE_A_CLOSABLE_UNDER_V1          = YES
GATE_B                            = BLOCKED
```
