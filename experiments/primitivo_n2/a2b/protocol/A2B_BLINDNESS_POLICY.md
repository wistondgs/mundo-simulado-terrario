# A2b blindness and firewall policy

## Allowed to a fresh blind builder/executor

- sealed SPEC and TASK under `input/`;
- this environment and execution contract;
- output manifest and run-manifest template;
- scientific-freedom freeze and synthetic-test policy;
- blind-build task and clean handoff;
- generic language/runtime documentation needed for CPython 3.12.

## Sealed until raw results are committed

- any comparison program, comparison output, or adjudication report;
- all expected-result and reference artifacts;
- this protocol's Gate A transition rule.

## Forbidden

- all A1/A2 outcomes, source, comparison tables, and historical session logs;
- all Gate A historical result and investigator-attestation content, other than
  the abstract fact that adjudication is external to the blind run;
- Gate B in every form;
- historical reference hashes that encode outcomes;
- parent/sibling directories, repository metadata/history, external paths,
  network access, and prior experimental interpretation.

## Delivery firewall

The prep repository itself is not handed to the blind session. After the prep
protocol commit, a custodian creates a sanitized external blind package from
the explicit allowlist below, verifies that its file inventory equals that
allowlist, initializes a new local Git repository containing only those files,
and records the source prep commit in `BLIND_PACKAGE_SOURCE.json`. The fresh
session receives only that new repository. It may not have filesystem mounts
to the parent repository, `/home/wis/mundo simulado terrario`, or the source
workspace.

`BLIND_INPUT_ALLOWLIST`:

```text
input/SPEC_PRIMITIVO_N2_A_REPLICA_CERRADA_v0_1.md
input/TASK_A2B.txt
protocol/A2B_SCIENTIFIC_FREEDOM_FREEZE.json
protocol/A2B_SCIENTIFIC_FREEDOM_FREEZE.md
protocol/A2B_ENVIRONMENT.json
protocol/A2B_ENVIRONMENT_CONTRACT.md
protocol/A2B_EXECUTION_CONTRACT.json
protocol/A2B_EXECUTION_CONTRACT.md
protocol/A2B_RAW_RESULT_QUARANTINE.md
protocol/A2B_SYNTHETIC_TEST_POLICY.md
schemas/A2B_OUTPUT_MANIFEST.json
schemas/A2B_RUN_MANIFEST_TEMPLATE.json
blind_build/A2B_BLIND_BUILD_TASK.md
blind_build/A2B_FRESH_SESSION_HANDOFF.md
custody/BLIND_PACKAGE_SOURCE.json
```

`BLIND_INPUT_DENYLIST`: every path not explicitly allowlisted, especially
`.git/`, `custody/A2B_INPUT_PROVENANCE.*`,
`protocol/A2B_GATE_A_TRANSITION_RULES.md`, all historical verifier paths, and
all Gate B paths.

The custodian, not the blind executor, creates `BLIND_PACKAGE_SOURCE.json`
with only source commit, input hashes, allowlist hash, and creation timestamp.
