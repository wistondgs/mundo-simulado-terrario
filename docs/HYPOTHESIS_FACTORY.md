# Hypothesis Factory

The factory converts each versioned `HyperedgeCandidateRecord` into a typed, immutable `HypothesisFamily`. It enumerates every non-empty component subset and one null hypothesis. Generated rivals carry `SYSTEM_GENERATED_RIVAL`; this is system synthesis, never an author claim or evidence.

Each family preserves the hyperedge, source claims, theory snapshot, source artifact, generator version, review state, and human modification log. Questions cover necessity, sufficiency, facilitation, interaction, mediation, and moderation. Explicit alternative explanations may be added as `AlternativeExplanation`; the generator does not invent them when the corpus supplies none.

Workflow: `GENERATED → UNDER_REVIEW → APPROVED_FOR_EXPERIMENT_DESIGN → APPROVED_FOR_EXECUTION`. `REVISE` returns to review and `REJECTED` is terminal. Transitions cannot be skipped. Saved versions are immutable; revisions create a new version and retain their delta.

Epistemic invariant: generated hypotheses are proposals. No design, dry run, or outcome classifier can emit `PROVEN_TRUE`.
