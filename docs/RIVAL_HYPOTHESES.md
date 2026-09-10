# Rival hypotheses

For components `{A, B, C}`, the generator creates `{A}`, `{B}`, `{C}`, `{A,B}`, `{A,C}`, `{B,C}`, `{A,B,C}`, and the null. Every rival declares mechanism, outcome, components, assumptions, provenance, predictions, falsification rules, and known confounders.

Predictions state observable, direction, comparison, temporal window, minimum meaningful effect (or a preregistration requirement), and expected, contradictory, and ambiguous patterns. Discriminating predictions compare a structural rival against the null under a named intervention and record diagnosticity assumptions.

Supported intervention vocabulary includes ablation, substitution, freeze, noise, delay, capacity limitation, information removal, environmental change, transfer, placebo, and sham. The initial compiler emits conservative ablation candidates and marks feasibility for capability review; it does not pretend every intervention is currently executable.
