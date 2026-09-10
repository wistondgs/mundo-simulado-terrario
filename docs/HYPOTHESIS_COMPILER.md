# Hypothesis Compiler

The compiler produces a `HypothesisDraft` from a hyperedge candidate. Every
draft starts at `REVIEW_REQUIRED`. Explicit approval is required to reach
`UNTESTED_HYPOTHESIS`; activation never runs an experiment.

Weak or absent concept coverage adds `THEORY_BASE_WEAK` without silently
blocking experimentation. The experiment preview lists the full condition,
component ablations, controls, expected observation, falsification condition
and source confounders. Creating `ExperimentSpec` remains a later human gate.
