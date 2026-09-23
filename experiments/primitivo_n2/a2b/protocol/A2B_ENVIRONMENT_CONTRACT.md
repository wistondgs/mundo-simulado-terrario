# A2b environment contract

The blind builder and executor use `/usr/bin/python3.12` (CPython 3.12.3) on
Linux x86_64 with glibc 2.39 or newer. Only the Python standard library is
allowed. Run in isolated mode with `LC_ALL=C.UTF-8`, `TZ=UTC`, and
`PYTHONHASHSEED=0`.

Network access, third-party packages, native extensions, parent/sibling
filesystem reads, Git history access, and all historical Gate A/Gate B paths
are prohibited. IEEE-754 binary64 is the real-number model. Canonical JSON is
UTF-8 with sorted Unicode-code-point keys, compact separators, and a final LF.

The executor may read only `input/`, `protocol/`, `schemas/`, and
`blind_build/`; it may write only its source/tests and `raw_results/`.
