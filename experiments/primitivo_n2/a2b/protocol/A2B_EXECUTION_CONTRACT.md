# A2b fixed execution interface

From the root of the sanitized blind package, the sole scientific command is:

```text
/usr/bin/python3.12 -I blind_build/src/run_a2b.py --spec input/SPEC_PRIMITIVO_N2_A_REPLICA_CERRADA_v0_1.md --task input/TASK_A2B.txt --output raw_results
```

It is non-interactive, has no scientific flags or hidden defaults, may not use
the network, and may not read outside the blind-package allowlist. It is run
exactly once per sealed run identifier. Any failure or incomplete output is
`INVALID`, not a reason to tune or rerun.

The SPEC section 12.4 OEIS anchor is `POST_SEAL_ONLY` under
`A2B_OEIS_RESOLUTION.md`: it is checked by the independent adjudicator after
the raw-result commit and before interpretation.  The command neither accesses
nor embeds an OEIS reference.
