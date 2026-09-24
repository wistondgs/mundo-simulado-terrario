# Gate A prospective amendment v1 — A1b

- Amendment: `GATE_A_A1B_PROSPECTIVE_AMENDMENT_v1`
- Version: 1
- Parent commit: `d2824ba18f3c83003635fdb10304f08d002a76ec`
- Branch: `protocol/gate-a-a1b-amendment-v1`
- Decision: the investigator approved option 2, a prospective Gate A
  amendment, on 2026-09-23. That date, like every date in this document, is in
  local time (UTC−6). The investigator also fixed the decisions recorded in §2.
- Companion rules: `A1B_GATE_A_TRANSITION_RULES_v1.md`, sealed in the same
  commit. The two documents are one normative unit. If they conflict, this
  amendment governs.
- Prospective boundary: the commit that introduces this file (§18).

## 0. Frozen artifacts

- **Governance documents** are identified by path at a commit, together with
  their blob id and SHA-256.
- **Records and archives that hold result material** (§1) are identified by
  path at a commit only.
- **Commit identifiers** of whole repositories are provenance anchors, not
  result material.

| Artifact | Identity |
| --- | --- |
| Gate A protocol | `experiments/primitivo_n2/control/control/GATE_A_PROTOCOL.txt` at `d2824ba`, blob `9201c285a539a12e421c5ff7b63c17a2030346f1`, SHA-256 `caa6d63ca004bd10ea947d9e8e26427f475530c1b000f34d834d178a87896210`. Byte-identical to its entry `control/GATE_A_PROTOCOL.txt` in the frozen control archive `experiments/primitivo_n2/control/PRIMITIVO_N2_EXPERIMENT_CONTROL.zip` at `d2824ba`. The archive itself is identified by path only. |
| Historical custody checklist | `experiments/primitivo_n2/control/control/WORKSPACE_CUSTODY.txt` at `d2824ba`, blob `1a43c43f5565ce92a4c01da26bfb8da118888b8b`, SHA-256 `6edccd599f4e441429b92d618ccf93334bf38552729981e285f4f5c4d5430ce9`. Byte-identical to its entry in the control archive. |
| SPEC A | `experiments/primitivo_n2/control/control/SPEC_PRIMITIVO_N2_A_REPLICA_CERRADA_v0_1.md` at `d2824ba`, blob `e322e4572261c7e9fc2294f860943255cda49e71`, SHA-256 `f19324cd5039cc6f83176a77afe8ff23b07e817e1a1471e5e56d05823515a430`. Byte-identical to its entry in the control archive, and to the sealed A2b input. |
| A2b transition rules, superseded in part (§4) | `experiments/primitivo_n2/a2b/protocol/A2B_GATE_A_TRANSITION_RULES.md` at `c3d11a983e1e3c2746975277fdf09724ab8bea6f`, blob `aea92b948f93c270386f27b050c82021adf339a0`, SHA-256 `423d850faa91e39041b2c44fccc076b3547d1c9f90ab1b8c839c23355150c7fe`. The same blob appears at `cde971a5c76a9481ae3a2f50b02914b5d4fd1690`. |
| A2b OEIS resolution, applied to A1b (§7) | `experiments/primitivo_n2/a2b/protocol/A2B_OEIS_RESOLUTION.md` at `c3d11a983e1e3c2746975277fdf09724ab8bea6f`, blob `b97fdc5c003c0166f326226f43e5c5fb4c96d3f3`, SHA-256 `20d473baf49a1269c44358b7cb660a3b8e6220510805f0607025f9c2e7032432`. |
| Semantic comparison schema | `experiments/primitivo_n2/gate_a_verifier/SUMMARY_SEMANTIC_SCHEMA.md` at `d2824ba`, blob `b1a2c5f00f22af5753767510a8c6748441df0627`, SHA-256 `3ee763d6da46f47f88db5ded5bc9c6f32ac36dfa460c8615cb8cd7bd1b3f1a8d`. |
| SPEC §14 reference artifacts | `experiments/primitivo_n2/gate_a_verifier/reference_generated/` at `d2824ba`, path only. The A2b §14 adjudication used the same artifacts. |
| A2b evidence | Independent package `/home/wis/primitivo_blind/A2b_build_package`, evidence commit `60626c7aa9391ba2ae7d5cbff8cb11f95e91bfc8`, seal-record commit `9ebc0cc7e78a3854aaa0b13e935b3e2b77430adb`. |
| Historical A1 custody records | Path only, at `d2824ba`: `experiments/primitivo_n2/gate_a_verifier/CUSTODY_REQUIREMENTS_AUDIT.json`, `experiments/primitivo_n2/gate_a_verifier/BLINDNESS_GATE.json`, and the sealed session custody under `experiments/primitivo_n2/gate_a_verifier/session_custody/`. |
| Historical A1 attestation form | `experiments/primitivo_n2/gate_a_verifier/ATTESTATION_FINAL_TO_CONFIRM.md` at `d2824ba`, path only. Unsigned. |
| Gate A result record | `experiments/primitivo_n2/gate_a_verifier/GATE_A_RESULT.json` at `d2824ba`, path only. This amendment does not modify it. |

This amendment contains no result material as defined in §1. It contains no
scientific value, no output, and no content hash of any file, archive or
directory that holds result material.

## 1. Definitions

- **Roles.**
  - **A**: governance and amendment author.
  - **B**: A1b preparation and custody operator.
  - **C**: the A1b blind scientific session.
  - **D**: the post-seal adjudicator.

  Other functions:

  - **Determination session.** A session that is not A, B or C and carries no
    project-result context. It determines the custody statuses (§15). D may
    perform this function only if D meets those same conditions at that point.
  - **TASK screener.** Defined in §11.
  - **B's environment setter.** Defined in §9.

  §9 states the separation and how it is proven.
- **Result material.** Any of the following:
  - a scientific value, output file or output hash;
  - a reference hash, or a content hash of any file, archive or directory that
    holds result material;
  - reference code or reference outputs;
  - any comparison or diagnostic detail: the first discordant `F` or field, a
    divergence classification, or an ambiguity audit;
  - the OEIS anchor value.
- **Governance status.** The evidentiary classifications and outcome labels of
  A1, A2, A2b and A1b, as they appear in §2, §3, §4 and §5 and in the
  transition rules' §7 and §9. They are not result material.
  - Role C never receives them.
  - Role B and the determination session receive only the operative extract,
    which contains none of them.
- **Operative extract.** The byte-for-byte concatenation, in this order, of:
  - this amendment's sections §1 and §6–§15;
  - the transition rules' sections §1, §2, §5 and §6.

  Each section runs from its `## N.` heading line up to, but not including, the
  next `## ` heading. The extract's SHA-256 is recorded in the custody manifest
  (§18). Anyone can regenerate it and check it.
- **Project-result context.** Any memory, instruction, conversation, file or
  tool access that carries any of the following:
  - result material;
  - historical session transcripts or records of A1, A2 or A2b;
  - A1b outputs seen before `CUSTODY_DETERMINATION_SEAL` by anyone other than
    role B or the determination session;
  - governance statuses;
  - Gate B material.
- **Result-bearing tree.** Any of the following:
  - a repository, worktree, package or directory listed in §10;
  - any directory that holds result material;
  - any directory containing either of the above.
- **Seal.** A record is sealed when both conditions hold:
  - **Fixed.** It is committed, or otherwise cryptographically fixed, outside
    the reach of roles B and C.
  - **Anchored.** Its SHA-256 is delivered to a party or system outside the
    control of the role that produced the record, and outside the control of
    roles B and C. That party records the time of receipt, and the receipt is
    kept.

  Examples of such a party: the investigator, through an external timestamped
  channel; a remote with server-side time; a timestamping service.
- **Ordered sequence.** These names are used everywhere. Each step follows the
  one before it, unless stated otherwise.
  1. `A2B_POINT2_CERTIFICATION`: the investigator's GATE_A_PROTOCOL point 2
     certification for A2b is recorded and anchored (§4).
  2. `ENVIRONMENT_SEAL`: the following are sealed (§9, §10):
     - role B's environment;
     - its restrictions and probe results;
     - role B's launch record.
  3. `PREPARATION`: role B prepares the workspace and the TASK, and runs the
     environment probes (§10, §11).
  4. `PRE_RUN_SEAL`: the pre-run custody record is sealed (§11).
  5. `COMPARATOR_SEAL`: role D's comparison program is identified and sealed
     (§12). This step may occur at any point before `SHOT_START`.
  6. `SHOT_START`: the role C session is opened (§6).
  7. `STARTUP_SEAL`: C's startup checks are recorded and sealed, before any
     input to C (§11).
  8. `DIRECTIVE`: the first input to C, which starts the scientific task.
  9. `DELIVERY`: C's session has ended and its write access has been revoked.
  10. `G5_SEAL`: the G5 capture and its verification are sealed (§12).
  11. `CUSTODY_DETERMINATION_SEAL`: the determination session's findings and
      the investigator's certification are sealed (§15).
  12. `ADJUDICATION_SEAL`: the comparator's first output is sealed (§12).
  13. `FINAL_STATUS_SEAL`: the complete A1b state block of the transition rules
      is sealed (§12).
- **Shot and attempt.** An attempt is a shot that has started. Records made
  before the shot are not attempts.

## 2. Fixed classifications and decisions

The investigator's decisions of 2026-09-23, recorded exactly:

1. Option 2: prospective amendment.
2. `OEIS = POST_SEAL_ONLY`, as for A2b.
3. No different model or family is required. A different session and a
   different construction and execution context are required, completely
   isolated. The family and version are recorded, but they are not an
   eligibility criterion.
4. If the substitute fails, Gate A is not converted automatically into a
   failure:
   - SPEC §14 applies (`ERROR_REPLICA`, `ERROR_REFERENCIA`, `AMBIGUEDAD_SPEC`);
   - Gate A does not close;
   - another attempt requires another prospective version of the amendment;
   - the earlier failure is kept permanently.
5. Seal in a dedicated branch and worktree from `d2824ba`, following the A2b
   precedent.

The investigator also decided the following.

- **Roles.** The governance session may know the project. It must never take
  part in:
  - the material preparation of the A1b workspace;
  - execution;
  - custody;
  - scientific construction.

  The post-seal adjudicator may know the project, but it must be a different
  session from the scientific operator.
- **Isolation.** Independence must be technical, not declarative.

State at the seal:

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

- **Where the values come from.**
  - The historical values are the investigator's fixed classifications.
  - The A1b values and `GATE_A_CLOSABLE_UNDER_V1` are defined by the transition
    rules.
  - `GATE_B = BLOCKED` means that Gate B, the B experiment, may not be opened,
    prepared or executed.
- **Historical A1.** It is a separate historical artifact. This amendment
  neither changes it nor renames it.
- **A1b.** `A1b = prospective blind substitute for the A1 component of Gate A`.
  A1b is a new replication, not a version of A1.
- **Nothing earlier counts as A1b.** No session, record or artifact that
  predates the prospective boundary can be designated A1b. A1's code, outputs
  and ambiguity register are not inputs to B, C or the TASK.
- **A2b is immutable under this amendment.** It is not rerun and not
  re-adjudicated, and its evidence is not altered. No A1b outcome reopens A2b
  under this version.

## 3. Purpose and motivation

This amendment exists because the historical custody of A1 cannot be fully
certified. The investigator's provisional record of 2026-09-23 has:

- `A1_G0_CUSTODY = NOT_FULLY_CERTIFIABLE`;
- `A1_G5_CUSTODY = NOT_FULLY_CERTIFIABLE`.

The basis comes from the historical A1 custody records (§0) and from the
attestation adjudication of 2026-09-23, which is not itself a committed record:

- A1's session had the project root as its working directory. Its sealed
  session record shows the sandbox policy `danger-full-access`, while
  reference, control and B material were in that tree.
- No external initial directory listing was preserved.
- No freeze or hashes independent of the replicating session were made, and
  kept outside its reach, before the reference comparison.

**This amendment is not motivated by A1's scientific result.** It would have
been adopted in the same form whether historical A1 matched the reference or
failed to match it.

A1's isolation was instructed rather than technically enforced. That is why
§10 requires technical isolation, and why §7 follows the A2b OEIS discipline
rather than historical A1.

The amendment is prospective only. It creates no new historical fact about
A1. Beyond recording the classification in §2, it neither certifies nor
decertifies A1's historical custody.

## 4. What A1b replaces

This amendment supersedes, as norms, two parts of the "Gate A effect" section
of the A2b transition rules (§0).

The sentence:

> The prospective Gate condition requires both a successful new A2b blind
> replication and the separate A1 investigator attestation.

And the implication block that follows it:

```text
IF A2B_BLIND_REPLICATION = PASS
AND A1_ATTESTATION is unresolved
THEN G0 = PENDING_PROVENANCE
     G5 = PENDING_PROVENANCE
     GATE_A = PENDING_PROVENANCE.
```

Both are replaced by the condition in §5. The dependency on **the separate A1
investigator attestation** becomes:

```text
a prospective A1b blind replication that:
  - receives PASS under the frozen SPEC §14 comparison;
  - satisfies prospective G0 (§11);
  - satisfies prospective G5 (§12);
  - has no unresolved value-affecting ambiguity.
```

- **The bytes of the A2b rules are not modified.** All their other content
  stays in force, including:
  - A2b's outcome-state definitions;
  - the statement that A2b never automatically changes G0 or G5;
  - the statement that an A2b failure is evidence about the A2b requirement
    only;
  - the statement that those rules do not authorize Gate B.
- **GATE_A_PROTOCOL point 2, A1 component.** The G0 and G5 certified under
  point 2 are `A1B_G0` and `A1B_G5`.
- **GATE_A_PROTOCOL point 2, A2b.** This amendment does not change it. The
  investigator still certifies A2b's G0 and G5, as for every blind replica.
  - The certification is made from A2b's sealed evidence only.
  - It is recorded and anchored as `A2B_POINT2_CERTIFICATION` before
    `ENVIRONMENT_SEAL`, so that it cannot depend on A1b's outcome.
  - A1b preparation does not start until it exists.
  - It certifies custody. It does not re-adjudicate A2b's result.
- **The historical attestation form** stays part of the historical record.
  Signing it or not documents A1's history. It no longer affects the Gate A
  condition.
- **Nothing historical is rewritten:** neither historical A1 nor A2b's
  scientific evidence.

## 5. Gate A condition after this amendment

`GATE_A = REPLICADO` only if all of the following hold:

```text
A2B_BLIND_REPLICATION = PASS
AND A1B_BLIND_REPLICATION = PASS
AND A1B_G0 = PASS
AND A1B_G5 = PASS
AND NO_UNRESOLVED_VALUE_AFFECTING_AMBIGUITY
AND the GATE_A_PROTOCOL requirements not superseded here are met, including points 2 and 8
```

The last line adds nothing new. It records that GATE_A_PROTOCOL remains in
force wherever this amendment does not supersede it.

**Gate A values.** Under this version, `GATE_A` takes only the values
`PENDING_PROVENANCE` and `REPLICADO`.

- There is no `GATE_A = FAIL`, and no A1b mismatch converts automatically into
  one.
- `GATE_A_CLOSABLE_UNDER_V1` records whether closure is still possible under
  this version.

**A1b does not reproduce the reference** (`A1B_BLIND_REPLICATION = FAIL`).

- **Diagnostic.** Each divergence is classified under SPEC §14 and
  GATE_A_PROTOCOL point 6 as `ERROR_REPLICA`, `ERROR_REFERENCIA` or
  `AMBIGUEDAD_SPEC`. The investigator adjudicates the classification.
- **Gate A does not close until that diagnostic is adjudicated,** and under
  this version it does not close afterwards either. By decision 4, a failed
  substitute does not close Gate A.
  - Every correction path needs a repair, a rerun, a new SPEC version or a
    reference change. That is true of SPEC §14 ("se corrige la especificación y
    ambas implementaciones vuelven a correr") and of GATE_A_PROTOCOL point 7.
  - This version authorizes none of these.
  - Therefore `REPLICADO_CON_CORRECCIONES` (GATE_A_PROTOCOL point 8, SPEC §14)
    is not reachable on A1b evidence under this version.
  - In SPEC §14 terms, a `FAIL` is recorded as `NO_REPLICADO` under this
    version.
- **Bearing on A2b.** An `ERROR_REFERENCIA` finding, or a normative
  `AMBIGUEDAD_SPEC` finding, may also bear on A2b, which was compared against
  the same reference under the same SPEC. That question is reserved to a later
  version. A2b is not reopened under this one.

**Other outcomes.**

- **`INDETERMINATE`.** Gate A stays pending (`PENDING_PROVENANCE`), and it is
  not closable under this version.
- **`INVALID`.** There is no scientific adjudication. Gate A stays
  `PENDING_PROVENANCE`, and it is not closable under this version.
- **A1b passes but a condition fails.** Suppose `A1B_G0`, `A1B_G5`, the
  ambiguity condition, or a remaining protocol requirement fails. Gate A is
  then not closable under this version, and the A1b result stays in the record
  as evidence.
- **A2b not `PASS`.** If `A2B_BLIND_REPLICATION` were not `PASS`, Gate A would
  not close under this version.

**Outside this version.** Any consequence of an A1b outcome that needs one of
the following lies outside this version:

- a repair, a rerun, a new SPEC version or a reference change;
- a new A1b attempt.

Such a consequence requires a new prospective amendment version, sealed before
it (§6).

**Gate B.** `GATE_A = REPLICADO` satisfies the Gate A precondition of
GATE_A_PROTOCOL point 9. It does not by itself open, prepare or execute Gate
B. That requires a separate explicit authorization.

**Recording.** The investigator records any change of `GATE_A` in a separate
dated record.

## 6. Sequence and one-shot policy

A1b has exactly **one** scientific shot under this amendment version. There is
no retry, no silent repair, and no rerun after results are seen.

- **The shot starts at `SHOT_START`,** the opening of the role C session: the
  first session or process, other than role B acting under §10–§12, that can
  read the A1b workspace. The shot is consumed from that moment.
- **Before the shot.**
  - **Probe environment.** Role B verifies the environment with probes run in a
    probe environment. That environment has the same sandbox, harness and tool
    configuration as role C. Its workspace holds neither SPEC A nor the TASK.
  - **Probes are programs.** A probe may open a model session in the probe
    environment only with a fixed, non-scientific prompt recorded verbatim.
  - **No rehearsal.** No model session other than C receives SPEC A or the
    TASK with an instruction to solve it or any part of it. Role B reads SPEC A
    only to write the TASK, and implements no part of it.
  - **Pre-shot failures.** A failure found before the shot consumes no shot. It
    is kept in the custody record, and the preparation may be corrected and
    probed again. Every probe output and transcript goes into `PRE_RUN_SEAL`.
- **After the shot starts, any defect ends the attempt.** This covers:
  - a failed startup check;
  - a preparation defect;
  - an unsealed or wrong TASK;
  - a firewall breach;
  - evidence that scientific work for the attempt, such as code or outputs,
    existed before `SHOT_START`.

  The attempt is classified under the transition rules, and the shot stays
  consumed. If a startup check fails, `DIRECTIVE` is never sent.
- **Every attempt passes through the custody steps.** However it ends, including
  before `DIRECTIVE`, an attempt passes through `DELIVERY`, `G5_SEAL` and
  `CUSTODY_DETERMINATION_SEAL`.
- **Exactly one role C session per version.** No second role C session may be
  opened under this version. A sub-agent spawned by C is part of C: it runs in
  C's sandbox under C's tool allowlist, and it is logged.
- **Interruption.** If infrastructure interrupts C (for example a power or
  network outage), the *same* C session may be resumed, under these conditions:
  - only from its last recorded turn;
  - only after role B has sealed the SHA-256 of the transcript so far;
  - only with the pre-registered continuation message (§11).

  Rewinding, restoring a checkpoint, editing the transcript and forking are
  prohibited. Any of them counts as a second role C session. Automatic context
  compaction by the harness is recorded, not prohibited. If the same session
  cannot be resumed, the attempt ends `INCOMPLETE`.
- **A later attempt** requires a new prospective amendment version, sealed
  before that later run.
- **Every attempt stays in the permanent record,** whether failed, invalid or
  indeterminate, and so does every pre-shot record. A new version may never
  erase or supersede evidence merely because a result was inconvenient. In
  particular:
  - **Sealed statuses are final.** No later version may change the sealed
    statuses of an attempt whose shot started under an earlier version.
  - **Standards are fixed before the shot.** No later version may count such an
    attempt toward Gate A under standards other than those sealed before its
    shot.
  - **Prior attempts are declared first.** Every later version states on the
    record, before its own run:
    - the cause for the new attempt;
    - each prior attempt, with its sealed statuses and any adjudicated
      diagnostic;
    - how Gate A treats each of them.

    It may not treat a prior sealed `FAIL` or `INDETERMINATE` as if it had not
    occurred.

## 7. OEIS

```text
OEIS = POST_SEAL_ONLY
```

- **Construction and execution.** A1b may not consult OEIS during construction
  or scientific execution. It produces and seals its scientific result first.
- **Who may consult it, and when.** Only role D may consult the authorized OEIS
  reference (A001372, SPEC §12.4), and only after `CUSTODY_DETERMINATION_SEAL`.
  This follows the A2b discipline.
- **Binding resolution.** SPEC §12.4 is resolved for A1b exactly as the A2b
  OEIS resolution (§0) resolves it:
  - role C computes and reports `tipos_S4` as SPEC §11 requires;
  - role C records control 12.4 only as the status `POST_SEAL_ONLY`, and
    states, embeds or compares no anchor value;
  - role D performs control 12.4 before interpretation.

  This is not an execution failure, a missing artifact or a SPEC ambiguity.
- **If control 12.4 fails,** SPEC §12 applies: "hay un error antes de
  interpretar cualquier resultado". The transition rules classify the outcome.
- **Enforcement.** Consultation is technically blocked. C's tools have no
  network access, and C has no web or search tool, including provider-side
  tools (§10). The recorded residual is the same as A2b's: prior model
  knowledge of a public OEIS term named by the frozen SPEC cannot be excluded.
- **If an anchor value appears in C's outputs or transcript,** it is recorded
  as a deviation. By itself it does not invalidate the run, because control
  12.4 is performed by role D and no field compared under SPEC §14 depends on
  it. If it altered a compared field, the run is `INVALID`.

## 8. Model and session independence

A1b is **not** required to use a different model family. Changing model family
here would introduce an unnecessary new variable. That may be of scientific
interest later, but it is not a Gate A criterion.

Role C requires instead:

- the intended model name, family and version, recorded in the `PRE_RUN_SEAL`
  record;
- the model actually used, recorded from C's session record at `STARTUP_SEAL`
  and again at `G5_SEAL`. A recorded model change does not by itself invalidate
  the run;
- a new session;
- no inherited project memory or context;
- no participation in A1;
- no participation in A2b construction or execution;
- no knowledge of reference outputs;
- no knowledge of A1, A2 or A2b scientific values;
- no material from any earlier A1b attempt.

## 9. Role separation

```text
A != B
A != C
B != C
C != D
```

These are the only required inequalities among roles A–D. The functional
exclusions of §1 and §9–§15 also apply:

- who sets up B's environment;
- who screens the TASK;
- who verifies a custody-only normalization;
- that role B never determines `A1B_G0` or `A1B_G5`.

**Role A** may know project history, because it defines the protocol. A session
carrying project-result context must not perform B or C, and must not act as
the determination session.

**The role A session that drafted and sealed this amendment** carries
project-result context. Its identifier, and the A2b functions it performed, are
recorded in the custody manifest. It must never take part in any of the
following:

- the material preparation of the A1b workspace, including the TASK;
- A1b custody;
- A1b execution;
- A1b scientific construction.

**Role D** may carry project context, including role A's. D accesses reference
artifacts, comparator output and OEIS only after
`CUSTODY_DETERMINATION_SEAL`, when the A1b result is already immutable. C and D
are distinct so that the scientific operator never judges its own execution.

**Separation is proven, not declared.**

- **Fresh top-level sessions.** B, C and the determination session are each a
  top-level session started fresh: no resume, no continue, no fork, and not
  spawned by another agent. The only exception is the resume of the same C
  session under §6.
- **Launch records.** Before each session acts, the following are recorded and
  sealed:
  - its launch command;
  - its parent process;
  - its harness configuration directory;
  - its initial context.

  For B, they are sealed in `ENVIRONMENT_SEAL`.
- **Startup conditions.** The startup conditions of §11 apply to B and to the
  determination session as well as to C.
- **D and C.** D's record shows that D is not a continuation of C's transcript.

**B's environment setter.** Role B's environment and inputs are set up by the
investigator, or by a session that is neither A nor B. B's inputs are
SHA-256-verified copies, held outside the main repository, of:

- SPEC A;
- the operative extract (§1);
- the identity fields of the custody manifest and seal record (§18): the
  boundary commit, and the SHA-256 of this amendment, of its transition rules
  and of the operative extract.

**Separation is by session and causal context,** not necessarily by model.

## 10. Technical isolation principle

```text
INDEPENDENCE MUST BE TECHNICALLY ENFORCED, NOT MERELY INSTRUCTED.
```

A prompt saying "do not read X" is not isolation if X remains technically
accessible.

- **Filesystem allowlist.** Role C's readable filesystem is the A1b workspace
  plus a declared runtime allowlist. This is enforced by an
  operating-system-level mechanism, such as a separate OS user, a container or
  a virtual machine.
- **Clean runtime.** The runtime is a clean image or environment identified by
  digest. It contains no project package, code or data.
- **Minimum denylist.** Before `SHOT_START`, probes must establish that C's
  execution environment cannot read any of the following:
  - the main repository;
  - A1/A2 historical outputs;
  - the A2b package;
  - PREP repositories;
  - control and reference outputs;
  - Gate B;
  - `~/.codex`;
  - `~/.claude`;
  - project memories or instructions;
  - sibling worktrees and repositories;
  - any directory containing scientific result hashes;
  - agent temporary and scratch directories, including other sessions'
    scratchpads under `/tmp`;
  - the branch and worktree of this amendment;
  - the custody locations of roles B and D.
- **Probes prove both directions:**
  - every item of the minimum denylist is unreadable;
  - nothing readable outside the workspace falls outside the declared
    allowlist.
- **Readable surface.** Everything else C can read is screened against the
  TASK criteria (§11):
  - the runtime allowlist;
  - environment variables;
  - the user name;
  - the hostname;
  - path names;
  - any account-level or harness-level instructions.
- **Tool inventory.** The `PRE_RUN_SEAL` record contains C's complete tool
  inventory, matched against a declared allowlist:
  - built-in tools;
  - MCP servers and connectors;
  - skills and plugins;
  - sub-agent types;
  - provider-side tools.

  There is no web or search tool of any kind.

  The same record also contains:
  - the harness configuration directory;
  - the environment variables;
  - `PATH`;
  - the runtime digest;
  - evidence that account-level memory is disabled.
- **Network.** C's tools cannot reach the network. B's network is restricted so
  that B cannot reach OEIS or any result-bearing remote.
- **Role B.** The firewall of §13 binds role B. B's restrictions are
  established and probed before B prepares anything, and they are sealed in
  `ENVIRONMENT_SEAL`.
- **No observation of C before `G5_SEAL`.** Before `G5_SEAL`, only role B may
  read C's workspace, outputs or transcript.
  - For every other agent session this is enforced technically, and recorded:
    their environments cannot read the A1b workspace or B's custody locations.
  - The investigator's own abstention is declared and recorded. It is a
    residual, because the machine owner cannot be excluded technically.
- **No probe passes, no shot.** The results of every probe are part of the
  `PRE_RUN_SEAL` record. `SHOT_START` does not happen unless every probe
  passes.

## 11. Prospective G0

**Preparation (role B), before `PRE_RUN_SEAL`.**

- **Workspace location.** The A1b workspace is not inside any result-bearing
  tree (§1). None of its entries is a symlink, a hardlink (link count greater
  than 1), or a mount into one. Location is necessary but not sufficient; §10
  proves isolation.
- **Workspace contents.** The initial workspace contains **exactly** these two
  files, and nothing else, hidden entries included:
  - `SPEC_PRIMITIVO_N2_A_REPLICA_CERRADA_v0_1.md`, SHA-256
    `f19324cd5039cc6f83176a77afe8ff23b07e817e1a1471e5e56d05823515a430`;
  - `TASK.txt`.
- **The TASK.**
  - **Author.** Role B writes the TASK. Role A does not write it, edit it, or
    supply text for it.
  - **Contents.** It contains the complete execution instructions, and it is
    procedural only:
    - the SPEC §0.5 deliverables;
    - file locations;
    - the SPEC §13 ambiguity register;
    - no network access;
    - control 12.4 recorded as `POST_SEAL_ONLY` (§7);
    - the delivery signal.
  - **Exclusions.** It contains no interpretation, clarification, example,
    emphasis or resolution of any SPEC reading. It contains no output schema
    beyond SPEC §9 and §11–§13.
  - **Screen.** Before `PRE_RUN_SEAL`, the TASK screener screens the TASK
    against fixed criteria. The screener is any session or person other than
    the TASK's author and other than the role A session that drafted this
    amendment. The screen checks for:
    - any reference or result material;
    - any output hash;
    - any OEIS value;
    - any A1, A2 or A2b material;
    - any governance status (§1);
    - any Gate B material;
    - any project conversation;
    - any material from an earlier A1b attempt.

    The label `POST_SEAL_ONLY` required by §7 is the one permitted exception.
  - **Screener limits.** The screener never edits the TASK. Its verdict is
    limited to three things, recorded verbatim in `PRE_RUN_SEAL`:
    - pass or fail;
    - the criterion triggered;
    - the passage of the TASK affected.
  - **Why the screen exists.** The screen is an extra check. It does not
    replace the separation of authorship.
- **Procedural messages.** The chat inputs to role C that may be used are
  pre-registered verbatim and declared non-scientific:
  - the start directive, which only directs C to execute the TASK;
  - one fixed continuation or resume message.

**The pre-run custody record** is sealed as `PRE_RUN_SEAL` before
`SHOT_START`. It contains:

- the absolute workspace identity;
- the exact directory inventory, hidden entries included, with each entry's
  file type, mode and link count;
- byte sizes;
- the SHA-256 of every authorized input, including the TASK;
- the model, family and version intended for role C;
- a timestamp;
- the protocol and amendment identity: the boundary commit, and the SHA-256
  of this amendment, of its transition rules and of the operative extract;
- the pre-registered procedural messages;
- the TASK screen result;
- the results and transcripts of every probe, the tool inventory and the
  environment inventory (§10);
- role B's session records (§9).

**Startup checks (role B), after `SHOT_START` and before any input to C.**
Using C's session record and environment, B verifies and records the
following:

- there is no `AGENTS.md` injection;
- there is no `CLAUDE.md` injection;
- there is no project memory;
- there is no inherited conversation;
- there is no parent-agent scientific context, and C is a top-level session
  (§9);
- there is no unexpected file;
- the model actually running matches the recorded one, or the difference is
  recorded (§8);
- C has no access outside the authorized workspace:
  - B runs the probe set as a separate process inside C's actual sandbox, with
    the same user, mounts and network policy, and not through C's chat;
  - C's recorded sandbox, user, mounts and tool configuration are the ones the
    §10 probes passed in.

The record is sealed as `STARTUP_SEAL` before `DIRECTIVE`. If any check fails,
`DIRECTIVE` is never sent, and the attempt ends as §6 describes.

**Chat inputs during the run.**

- **Recording.** Every input to C is recorded verbatim, with its time, and
  sealed in `G5_SEAL`.
- **No scientific instruction.** No supplementary scientific instruction is
  pasted into C's chat.
- **Tool approvals.** C's environment is configured so that no tool-approval
  prompt arises. Any approval that is given counts as an input.
- **Inputs that were not pre-registered.** The determination session judges
  each one, from the verbatim record, against a fixed criterion:
  - it is a breach if it contains any scientific instruction, interpretation or
    SPEC reading, or any project or result information;
  - otherwise it is a procedural deviation, with no consequence by itself.

These requirements, together with §10, §12, §13 and §15, incorporate every
item of the historical `WORKSPACE_CUSTODY.txt` checklist (§0), and they make
each one technical and contemporaneous.

## 12. Prospective G5 and adjudication order

**`DELIVERY`** means that C's session has ended and its write access has been
revoked. At `DELIVERY`, and before **any** reference comparison, custody (role
B) does the following:

1. **Capture**, outside A1b's reach:
   - the entire workspace tree, hidden entries included;
   - every location C could write to;
   - C's complete session transcript and tool log;
   - the verbatim input record (§11).
2. **Hash independently.** B hashes the workspace directly at `DELIVERY`,
   read-only and before copying, and also hashes the capture.
3. **Record the freeze time.**
4. **Create an immutable, sealed custody record.** It lists by hash everything
   captured, plus the raw probe outputs and role B's session records.
5. **Commit or anchor.** B commits that evidence, or otherwise
   cryptographically anchors it, as §1 requires.
6. **Verify.** B reads the sealed evidence back and verifies that it matches
   the hashes taken directly at `DELIVERY`. The result goes into an anchored
   addendum. `G5_SEAL` is complete only with that addendum.

**Which bytes count.** The frozen bytes that match the direct `DELIVERY`
hashes are authoritative.

- **Unexplained mismatch.** If the capture and the direct `DELIVERY` hashes
  differ without explanation, `A1B_G5 = FAIL`.
- **Delivery cannot be established.** If the bytes C delivered cannot be
  established, the run is `INVALID`.
- **C's own hashes.** C's self-declared hashes are not custody. A difference
  from them is recorded only.

**Order after `G5_SEAL`.**

1. **Custody determination.** The determination session determines the custody
   statuses from the sealed records (§15), and the investigator certifies
   them. Both are sealed in `CUSTODY_DETERMINATION_SEAL`.
2. **Reference access.** Only then may reference code, reference outputs or
   OEIS become accessible to role D.
3. **The comparison.** Role D performs the SPEC §14 comparison; the A1b
   scientific session does not. D uses the following:
   - the comparison program sealed in `COMPARATOR_SEAL`;
   - the frozen reference artifacts (§0);
   - the SPEC §14 criteria;
   - the normalizations of `SUMMARY_SEMANTIC_SCHEMA.md`: key order, whitespace,
     and F1–F3.

   The comparison follows GATE_A_PROTOCOL points 3–5, in order:
   1. the `por_sistema.jsonl` SHA-256;
   2. if the files differ, localization of the first discordant `F` and field;
   3. the `resumen.json` aggregates.

**The comparator.**

- **Before the shot.** D's comparison program is written from SPEC §14 and
  `SUMMARY_SEMANTIC_SCHEMA.md`, without access to reference outputs. Its
  SHA-256 is sealed in `COMPARATOR_SEAL` before `SHOT_START`.
- **Input check.** It verifies its inputs against the anchored `G5_SEAL`
  hashes.
- **One run.** It runs once.
- **Mutant check.** In the same run, it must report a discordance on a copy of
  the A1b output in which one compared field has been deliberately altered.
- **First output sealed.** Its first output, including the mutant check, is
  sealed in `ADJUDICATION_SEAL` before interpretation.

**The first sealed output governs.**

- **Comparator defect.** The investigator may adjudicate a comparator defect.
  - It never changes `A1B_POST_SEAL_ADJUDICATION_STATUS` or
    `A1B_BLIND_REPLICATION`.
  - It is recorded as a separate finding in `FINAL_STATUS_SEAL`, and it sets
    `GATE_A_CLOSABLE_UNDER_V1 = NO`.
  - The corrected comparator and its output are kept as evidence for a later
    version.
- **No replacement.** Nothing replaces the first output under this version.

**After `ADJUDICATION_SEAL`.**

- Role D performs control 12.4 (§7).
- Role D proposes the diagnostic, if there is one.
- Role D audits readings not recorded in the register (transition rules §5).
- The investigator adjudicates.
- The complete A1b state block is sealed as `FINAL_STATUS_SEAL`.

## 13. Reference and result firewall

Before `G5_SEAL`, A1b PREP (role B) and A1b scientific execution (role C) must
not have access to any of the following:

- the reference implementation;
- reference outputs;
- historical result hashes;
- the A1 result;
- the A2 result;
- A2b scientific values;
- the OEIS value used as external anchor;
- Gate B.

The same firewall binds the determination session until
`CUSTODY_DETERMINATION_SEAL`. This firewall is technically enforced (§10).

This amendment and its transition rules contain historical and project
information not required to perform the scientific task.

- They stay outside the A1b workspace, and role C never receives them.
- Role B and the determination session receive only the operative extract
  (§1). It contains no governance status and no result material.

A1b receives only the frozen SPEC and the TASK.

## 14. Frozen scientific rules

This amendment does not alter any of the following:

- SPEC A;
- the SPEC §14 comparison semantics;
- the calibration vectors (SPEC §9);
- the deterministic population (the 256 dynamics of SPEC §1);
- the result schema defined by SPEC §9 and §11–§13;
- the existing semantic equivalence rules (`SUMMARY_SEMANTIC_SCHEMA.md`).

**Machine schema for custody validation.** A machine schema used to validate
custody must be derived from the result schema and add no constraint on values.
It is listed by SHA-256 in the `PRE_RUN_SEAL` record.

**Custody-only normalization.**

- **What it may do:**
  - set file names and locations;
  - add custody metadata outside the compared fields;
  - record control 12.4 as `POST_SEAL_ONLY` (§7).
- **What it may not do:** change the value, representation, presence or order
  of any field compared under SPEC §14 and F1–F3.
- **Who handles it.** Role B writes it and lists it by SHA-256 in the
  `PRE_RUN_SEAL` record. Before the comparison, a session other than role B
  verifies it.
- **Anything else** requires a new amendment version.

A1b answers the same scientific question. This amendment changes provenance and
custody, not the target phenomenon.

## 15. Evidence standard, and who decides

**When G0 and G5 pass.**

- **`A1B_G0 = PASS`** only if every requirement of §10 and §11 is evidenced by
  records sealed in `ENVIRONMENT_SEAL`, `PRE_RUN_SEAL` and `STARTUP_SEAL`. For
  inputs during the run, the evidence is the verbatim input record sealed in
  `G5_SEAL`.
- **`A1B_G5 = PASS`** only if steps 1–6 of §12 are evidenced by records sealed
  in `G5_SEAL`, before any reference comparison.

**Who determines them, and when.** The determination session (§1) works from
the sealed records alone. It determines:

- `A1B_RAW_RESULT_STATUS`;
- `A1B_G0` and `A1B_G5`;
- the judgment on inputs that were not pre-registered (§11);
- the classification of each entry of A1b's ambiguity register (transition
  rules §5).

**Certification.** The investigator certifies `A1B_G0` and `A1B_G5`, as
`WORKSPACE_CUSTODY.txt` requires ("G0 and G5 are certified by the
investigator, not by the replicator").

- The certification rests on the determination session's sealed findings, not
  on memory. Any disagreement with those findings is recorded with its reason.
- All of this is sealed in `CUSTODY_DETERMINATION_SEAL`, before role D accesses
  any reference artifact, comparator output or OEIS.
- Recorded residual: the investigator's certification cannot be blinded to the
  A1b output hashes.

**Evidence rules.**

- **No sealed evidence, no `PASS`.** A requirement without contemporaneous
  sealed evidence is not `PASS`.
- **Breach evidence.** Evidence of a breach of §7, §10, §11 or §13 is recorded
  whenever it is discovered.
  - **Before `ADJUDICATION_SEAL`,** it enters the determination, and the
    transition rules may classify the run `INVALID`.
  - **After `ADJUDICATION_SEAL`,** it sets the affected custody status to
    `FAIL` and `GATE_A_CLOSABLE_UNDER_V1 = NO`. It never erases or alters the
    post-seal status or `A1B_BLIND_REPLICATION`.
  - **Revisions are traceable.** Every revision is recorded with its source,
    and the earlier determination is kept.
- **Diagnostic.** The investigator adjudicates the diagnostic, as SPEC §14
  states ("la hace el investigador"). Role D performs the SPEC §14 comparison
  and proposes its classification on the investigator's behalf.

```text
LATE_PROVENANCE_EVIDENCE_CANNOT_RETROACTIVELY_REPAIR_CUSTODY_ORDER
```

Evidence produced later may document what happened. It cannot turn a missing
or out-of-order custody step into a satisfied one.

## 16. Existing records

**This amendment does not modify:**

- any historical Gate A record, including `GATE_A_RESULT.json`;
- the A1 or A2 artifacts;
- the A2b package;
- the bytes of any A2b PREP document (the A2b transition rules are superseded
  only in part and only as norms, §4);
- the control package.

**`GATE_A_RESULT.json`** at `d2824ba` shows a state earlier than the A2b
execution. This sealing step does not update it. Any later update is a
separate, dated record.

**GATE_A_PROTOCOL remains in force,** except where §4 and §5 state otherwise.

- This amendment adds no closure path beyond the protocol.
- Under this version, it makes `REPLICADO_CON_CORRECCIONES` unreachable on A1b
  evidence (§5).

## 17. What sealing this amendment does not authorize

Sealing this amendment does not authorize any of the following:

- creating the A1b workspace;
- writing the A1b TASK;
- choosing the A1b model or any role's session;
- starting an A1b session;
- building a solver;
- running A1b;
- accessing Gate B;
- changing Gate A's result.

After sealing, work stops until A1b preparation is separately authorized.

## 18. Sealed artifacts

**The sealing commit** is the commit that introduces these three files. It is
the prospective boundary.

- `GATE_A_A1B_PROSPECTIVE_AMENDMENT_v1.md`: this file.
- `A1B_GATE_A_TRANSITION_RULES_v1.md`.
- `GATE_A_A1B_AMENDMENT_v1_CUSTODY_MANIFEST.json`. It records:
  - the parent commit;
  - the amendment version;
  - the SHA-256 of the amendment, of the transition rules, and of the operative
    extract;
  - the sealing timestamp;
  - the branch;
  - the commit produced;
  - `A1B_NOT_PREPARED = TRUE`, `A1B_NOT_EXECUTED = TRUE` and
    `GATE_B_ACCESSED = FALSE`.

**The seal record.** A commit cannot contain its own hash. So the following
commit adds only `GATE_A_A1B_AMENDMENT_v1_SEAL_RECORD.txt`, which records the
sealing commit, and it modifies none of the three sealed files.
