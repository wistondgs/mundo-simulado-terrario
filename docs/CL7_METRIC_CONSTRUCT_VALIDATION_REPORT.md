# CL7 Metric Construct Validation

Status: `CONSTRUCT_VALIDATED_INSTRUMENT`; not an empirical result.

## Recovered target

| Field | Value |
| --- | --- |
| Hypothesis | `HYPOTHESIS-b1c155f9304067f0` |
| Primary DV | planned-action evaluation pathway availability |
| Primary metric | `planned-action-evaluation-pathway` |
| Construct | availability of an actor action-sequence proposal/evaluation pathway |
| Scenario / agent | D2 / A4 |
| Preserved arm | `use_planner=true`, `use_world_model=true` |
| Ablated arm | `use_planner=false`, `use_world_model=true` |

The DV is a pathway-availability construct, not planning quality or generic
future-sensitive choice. `LOOKAHEAD_CHOICE_ACCURACY` is therefore not a
substitutable primary metric; it can only be proposed later as a separately
reviewed secondary outcome.

## Instrument

`terrario.lab.planning_trace_metric:evaluate_scientific_trace` reads only the
sealed `decision_trace` and `planner_proposal_trace` observer projections in
`SCIENTIFIC_TRACE`. It rejects missing projections, malformed proposals,
surplus proposals and target/oracle leakage. It never reads world truth,
agent-visible observation, arm id, variant, or `use_planner` to score the
result. A proposal found in an ablated cell is a separate terminal-protocol
integrity failure, not a label-dependent metric calculation.

The immutable `TrialIntent.agent_config` is part of the trial identity and
contains the two explicit `use_*` bindings. The runtime passes it into the
agent factory; no execution reconstructs an intervention from prose.

## Calibration evidence (not scientific evidence)

The regression calibration runs the real A4 runtime for two deterministic,
two-step D2 episodes:

| Arm | Expected sealed metric |
| --- | --- |
| preserved | `2 / 2 = 1.0` |
| actor-role ablated | `0 / 2 = 0.0` |

Both runs must have no observation fault. The same test verifies that the
sealed frame payload is canonical-JSON serializable. This calibration creates
no `ScientificResult`, no empirical evidence, and no graph update.

## Durable lineage

The previous prose-only operational draft is superseded, append-only, by the
draft whose condition bindings are explicit. The pre-transport metric
instrument is likewise superseded by the current construct-validated
instrument. Supersession is permitted only from review-blocked/incomplete
records; it refuses a preregistered or executed protocol.

## Remaining CL-7 gate

`CL-7` remains `BLOCKED_PENDING_AUTHORIZED_EXPERIMENT` until a human-reviewed,
authorized, preregistered execution produces and verifies a terminal raw trace
and a `METRIC_RESULT`. Only then can the existing eligibility firewall publish
a result and make a qualified graph/epistemic update.
