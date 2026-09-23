# Task for a fresh blind A2b builder

You receive only the allowlisted blind package. Implement the sealed SPEC
independently in CPython 3.12 standard library code at
`blind_build/src/run_a2b.py`, with the exact interface in
`protocol/A2B_EXECUTION_CONTRACT.md`.

Create synthetic-only unit tests under `blind_build/tests/` according to
`protocol/A2B_SYNTHETIC_TEST_POLICY.md`. Do not enumerate the real 256-dynamic
scientific instance, invoke the scientific command, generate any A2b raw
output, inspect outside the package, access the network, or request expected
results.

Freeze the source and synthetic tests in a commit, report its commit hash and
file hashes, then STOP. If the SPEC has a value-affecting ambiguity, report it
and STOP without inventing a resolution.
