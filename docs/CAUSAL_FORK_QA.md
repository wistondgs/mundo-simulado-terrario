# Causal Fork QA

- Exact restore: original continuation equals restored continuation.
- Double restore: two restored branches equal each other.
- Isolation: snapshot serialization eliminates live-reference aliasing.
- C01: registered sham yields equal canonical traces.
- Active fixture: declared agent-energy delta produces first divergence at the fork boundary.

Tested forkability matrix:

| Agent | World | Classification | Reason |
| --- | --- | --- | --- |
| A0_RANDOM | d0_differences | EXACT_FORKABLE | world, scheduler, rules and A0 generator explicitly restored |
| A1–A4 | any | NOT_FORKABLE | per-agent causal-state contracts not yet qualified |
| any | D1–D4 | NOT_FORKABLE | world/lifecycle contracts not yet qualified |
