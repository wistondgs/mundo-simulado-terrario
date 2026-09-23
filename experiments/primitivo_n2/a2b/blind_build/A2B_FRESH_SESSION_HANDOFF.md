# Fresh blind-session handoff

You must start in the sanitized blind-package repository supplied by a
custodian. It contains only the files enumerated by the blind-input allowlist
and must have no parent-repository, external-workspace, network, or historical
experiment access.

Verify the SPEC SHA-256 is
`f19324cd5039cc6f83176a77afe8ff23b07e817e1a1471e5e56d05823515a430` and the
TASK SHA-256 is
`245f922101df5cdfaaf5415efa9b4d87a2532c471c4e023ca9c2cfbf0133830a`.

Read the environment, execution, output, OEIS-resolution, and synthetic-test contracts. Build
`blind_build/src/run_a2b.py` and synthetic-only tests, using CPython 3.12
standard library only. The future scientific command is fixed as:

```text
/usr/bin/python3.12 -I blind_build/src/run_a2b.py --spec input/SPEC_PRIMITIVO_N2_A_REPLICA_CERRADA_v0_1.md --task input/TASK_A2B.txt --output raw_results
```

Do **not** run that command. Commit the source and synthetic tests, report the
commit and hashes, and STOP. Do not inspect or request any data outside this
package.

The OEIS A001372 anchor is explicitly `POST_SEAL_ONLY`; no OEIS value or
reference is available to this session. Validate the package first with
`/usr/bin/python3.12 -I validate_blind_package.py`.
