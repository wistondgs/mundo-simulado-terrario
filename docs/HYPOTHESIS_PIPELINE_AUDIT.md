# Hypothesis Pipeline Audit

Audit performed before `HYPOTHESIS-FACTORY-01` implementation. `Existing`
means a typed field and enforced behavior existed; `Partial` means prose was
carried but not operationally validated.

| Property | Existing | Partial | Missing before factory |
|---|---:|---:|---:|
| explanandum |  | yes | observable operationalization |
| explanans | yes |  |  |
| assumptions |  |  | yes |
| alternatives |  |  | yes |
| predictions |  | yes | typed observable comparisons |
| interventions |  | yes | typed manipulation contract |
| controls |  | yes | matching and adequacy audit |
| confounders | yes |  | registry and mitigation |
| falsification |  | yes | mandatory adverse patterns |
| necessity |  | yes | explicit design questions |
| sufficiency |  | yes | explicit design questions |
| mediation |  |  | yes |
| moderation |  |  | yes |
| expected evidence |  | yes | outcome classification |
| adverse evidence |  | yes | structured weakening/contradiction rules |

`HyperedgeCandidateRecord` preserves the source conjunction, outcome,
necessity/sufficiency prose, confounders and provenance. `HypothesisDraft`
preserves only the conjunction, outcome, provenance, confounders, coverage and
one discriminating-test string. `HypothesisSpec` has participants, effect,
pressure, controls, ablations and evidence requirements. `ExperimentSpec` is a
runnable condition but has no review-state field and can be instantiated
directly. Therefore the factory adds a separate, review-gated design layer and
does not reinterpret or mutate any of these historical contracts.
