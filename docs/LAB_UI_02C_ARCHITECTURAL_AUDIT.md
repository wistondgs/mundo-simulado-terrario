# LAB-UI-02C architectural audit

## Protected baseline

The phase started from `e34bf99b9a2f0a18ec8dc34101876cc73eda0e39` with a clean tree and `276 passed, 1 skipped`. It adds read models and design artifacts only under `terrario/lab`; it does not modify A0–A4, Core, World, the experiment runner, historical EvidenceGraph, Scientific Review, theory snapshots, H-ADAPT, RNFE, or Genesis.

No scientific campaign is executed. No endpoint creates `ScientificRun`, `ExperimentSpec`, approval, preregistration, or evidence. H-ADAPT remains `BLOCKED_CUDA` and was not run.

## Reused source contracts

| Source | 02C use | Safety boundary |
|---|---|---|
| `ScenarioDefinition`, `DifficultyProfile`, `MetricBinding` | immutable inputs and versioned provenance | no mutation of 02A contracts |
| A0–A4 `AgentInterface` and factory | static descriptors and real parameter counts | no agent injection or source edits |
| `scientific_state` in sandbox traces | optional runtime read model | always `ENGINEERING_SANDBOX`, never evidence |
| `ScientificObserver.VALID_MODES` | runtime-mode mapping | profile expansion cannot alter `AgentObservation` |
| Scientific Review/portfolio | upstream review truth | `READY_FOR_HUMAN_REVIEW` cannot become approval |

## Capability audit

`module exists`, `structural support`, `scenario sufficiency`, and `scientific competence` are separate claims. The registry never searches class or module names to infer support. `SUPPORTED` requires at least one `CapabilityEvidence` reference. Explicit source declarations justify `MISSING`; absence of a safe determination is `UNKNOWN`. A recurrent tensor is `temporal_state`, not automatically `working_memory`; an internal tensor is displayed only as `INTERNAL_STATE` with `INTERPRETATION_REQUIRES_ANALYSIS`.

Technical compatibility (observation/action/reset/device interfaces) is independent from cognitive expectations. A deliberately incapable baseline can therefore remain execution-compatible.

## Metric and Observer audit

Metric definitions retain distinct `construct`, `proxy`, implementation state, construct-validation state, signals, direction, limitations, and provenance. Proposed metrics are not callable implementations. Missing signals yield `MISSING_REQUIRED_SIGNAL`, never a synthetic zero or silent NaN.

Observer labels expand to explicit channels. Channels carry source, frequency, schema, estimated size, separation class, cost, purpose, and availability. `FULL_DEBUG` may widen observer recording but `ObserverRegistry.agent_projection` is profile-invariant and restricted to the established agent-visible field set. Storage values are labeled `ESTIMATE`; missing dimensions return `UNKNOWN`.

## Experiment grammar

`ExperimentDraft` is the terminal artifact of Composer in this phase. Its scientific hash includes scenario, difficulty, variants, agents, controls, metrics, observer scientific channels, exact seed lists, repetitions, limits, device, truth/signals, manipulation checks, and transfer design. UI tab/zoom/sorting preferences and artifact bookkeeping do not affect the scientific hash.

Derivation creates `parent -> delta -> child`; it never overwrites the parent. Structural, compatibility, and scientific findings remain separate and carry a rule source. The available states stop at `PREREGISTRATION_READY`; there is deliberately no `APPROVED_FOR_EXECUTION` state.

`TrialMatrix` materializes deterministic `TrialIntent` cells over:

`variants × agent/control conditions × world seeds × agent seeds × repetitions`.

It computes the exact count, records explicit blockers, and may add `COMBINATORIAL_EXPLOSION` without changing any cell. It has no execution method and reports `execution_performed = false`.

