"""A metric does not exist scientifically until it can discriminate its known cases.

Terrario already had a theory of experimental validity — preregistration, sealed
evidence, a firewall between sandbox and evidence. It had no theory of
INSTRUMENT validity, and four measuring instruments were wrong before anyone
noticed. Three of those were caught by luck: they collided with something loud
enough to contradict. The fourth was caught by a control.

So every scientific metric is registered here with its full definition, not just
its name. Two functions can share a name and measure different conditioned
quantities — `addressing rate` over all steps and over opportunities differ by a
factor of three in these worlds — and the registry forces the conditioning into
the open as P(A | B, C) rather than leaving it implicit in code.

The state machine decides what may appear in a scientific report:

    UNREGISTERED -> DEFINED -> CONTROLLED -> CALIBRATED -> REPORTABLE

with blocking states FAILED_CONTROL, UNIDENTIFIABLE, INSUFFICIENT_SUPPORT and
CONTRACT_MISMATCH. Only REPORTABLE enters evidence. A metric under development
is not forbidden — it is marked EXPLORATORY_UNCALIBRATED, which keeps it usable
for steering and unusable as a finding. That is the same boundary the laboratory
already draws between engineering sandbox and scientific evidence, applied one
level down, to the ruler instead of the experiment.
"""

from __future__ import annotations

import enum
from dataclasses import dataclass, field
from typing import Any

from terrario.lab import instrument_calibration as cal


class InstrumentState(enum.StrEnum):
    UNREGISTERED = "UNREGISTERED"
    DEFINED = "DEFINED"
    CONTROLLED = "CONTROLLED"
    CALIBRATED = "CALIBRATED"
    REPORTABLE = "REPORTABLE"
    # Blocking
    FAILED_CONTROL = "FAILED_CONTROL"
    UNIDENTIFIABLE = "UNIDENTIFIABLE"
    INSUFFICIENT_SUPPORT = "INSUFFICIENT_SUPPORT"
    CONTRACT_MISMATCH = "CONTRACT_MISMATCH"
    EXPLORATORY_UNCALIBRATED = "EXPLORATORY_UNCALIBRATED"


REPORTABLE_STATES = frozenset({InstrumentState.REPORTABLE})


@dataclass(frozen=True)
class MetricSpec:
    metric_id: str
    semantic_definition: str
    conditional_form: str          # P(A | B, C) — written out, not implied
    numerator: str
    denominator: str
    conditioning_set: tuple[str, ...]
    valid_domain: str
    undefined_conditions: tuple[str, ...]
    expected_range: tuple[float, float]
    instrument_controls: tuple[str, ...]
    version: int = 1
    exploratory: bool = False
    notes: str = ""


REGISTRY: dict[str, MetricSpec] = {}


def register(spec: MetricSpec) -> MetricSpec:
    REGISTRY[spec.metric_id] = spec
    return spec


register(MetricSpec(
    metric_id="tasa_oportunidad",
    semantic_definition="Fraction of decisions taken with an object in contact.",
    conditional_form="P(O_t)",
    numerator="steps whose preceding world had an object at Manhattan distance 1",
    denominator="decisions (trace rows minus one, since a step is judged against "
                "the world its action was chosen in)",
    conditioning_set=(),
    valid_domain="any trace whose observer world records agent and object positions",
    undefined_conditions=("decision_count == 0",
                          "positions absent from the observer world"),
    expected_range=(0.0, 1.0),
    instrument_controls=("empty_world", "adjacent_every_step"),
    notes="A low value accuses the world or the organism's foraging, never the "
          "action channel. Read it before anything downstream.",
))

register(MetricSpec(
    metric_id="tasa_interaccion",
    semantic_definition="Fraction of decisions in which the organism chose to "
                        "interact at all, whether or not anything was there.",
    conditional_form="P(C_t)",
    numerator="steps whose action operation was CONSUME",
    denominator="decisions",
    conditioning_set=(),
    valid_domain="any trace recording the chosen operation",
    undefined_conditions=("decision_count == 0",),
    expected_range=(0.0, 1.0),
    instrument_controls=("never_target_agent", "perfect_targeting_agent"),
    notes="High interaction with low addressing is an organism that wants and "
          "cannot — the signature of an actuator bottleneck rather than apathy.",
))

register(MetricSpec(
    metric_id="tasa_direccionamiento",
    semantic_definition="Of the genuine opportunities, the fraction the emitted "
                        "action actually pointed at.",
    conditional_form="P(T_t | C_t, O_t)",
    numerator="opportunities where the action both was CONSUME and referred to an "
              "adjacent object",
    denominator="opportunities",
    conditioning_set=("an object is in contact", "the operation is CONSUME"),
    valid_domain="traces under a declared addressing mode",
    undefined_conditions=("opportunity_count == 0",),
    expected_range=(0.0, 1.0),
    instrument_controls=("perfect_targeting_agent", "never_target_agent",
                         "t1_perfect_targeting_agent", "t1_never_resolving_agent",
                         "uniform_random_agent"),
    notes="Controlled under BOTH addressing contracts, because they answer the "
          "question differently: T0 geometrically, T1 through the resolver. "
          "Under T0 the analytic chance value is 1/25: CONSUME is one of five "
          "operations and the neighbour one of five directions. A reading near "
          "0.04 is therefore not a weak policy, it is no addressing at all.",
))

register(MetricSpec(
    metric_id="conversion_aprendizaje",
    semantic_definition="Best discrimination achieved inside a stable-rule segment.",
    conditional_form="P(B_t | T_t, C_t, O_t)",
    numerator="effective consumes that gained energy against the step baseline",
    denominator="effective consumes within the segment",
    conditioning_set=("the consume reached something", "rules did not change mid-segment"),
    valid_domain="traces with an energy series and a declared or inferable step cost",
    undefined_conditions=("no segment holds at least 3 effective consumes",
                          "no idle steps and no declared step cost, so the "
                          "baseline cannot be established",
                          "N_informative == 0"),
    expected_range=(0.0, 1.0),
    instrument_controls=("non_learning_agent", "oracle_learner"),
    notes="Zero here means exposures existed and none were converted. With no "
          "exposures the reading is NOT_EVALUABLE and the two must never merge.",
))

register(MetricSpec(
    metric_id="tasa_realizacion",
    semantic_definition="Of the intentions that named a resolvable referent, the "
                        "fraction the world actually executed against that referent.",
    conditional_form="P(executed == intended | intention is valid)",
    numerator="steps where executed_target == intended_target",
    denominator="steps with a VALID resolution",
    conditioning_set=("the intention resolved to a real, in-range entity",),
    valid_domain="traces carrying Action Contract v2 provenance",
    undefined_conditions=("no step produced a VALID resolution",),
    expected_range=(0.0, 1.0),
    instrument_controls=("realization_faithful", "realization_substituted",
                         "realization_no_contract"),
    notes="Separates deciding correctly from executing correctly. The "
          "substitution control is the one that matters: an instrument that "
          "cannot tell a substituted referent from a faithful one cannot police "
          "AC2-5, which is the invariant keeping addressing measurable at all.",
))

register(MetricSpec(
    metric_id="contabilidad_energetica",
    semantic_definition="Fraction of non-consuming steps whose energy change equals "
                        "exactly the declared step cost.",
    conditional_form="P(dV_observed == dV_declared | no interaction this step)",
    numerator="non-consuming steps reconciling to within 1e-6",
    denominator="non-consuming steps",
    conditioning_set=("no consume event on the step",),
    valid_domain="traces with an energy series and a declared step cost",
    undefined_conditions=("no declared step cost", "no energy series",
                          "every step consumed something"),
    expected_range=(0.0, 1.0),
    instrument_controls=("ledger_balanced", "ledger_undeclared_flow"),
    notes="Below 1.0 there is a flow the scenario does not declare, and any "
          "baseline reconstructed after the fact is silently measuring it. The "
          "ledger of metabolic transitions is meant to be the source of truth; "
          "this is the check that it still is.",
))


def state_of(metric_id: str) -> InstrumentState:
    spec = REGISTRY.get(metric_id)
    if spec is None:
        return InstrumentState.UNREGISTERED
    if spec.exploratory:
        return InstrumentState.EXPLORATORY_UNCALIBRATED
    if not spec.instrument_controls:
        return InstrumentState.DEFINED
    declared = set(spec.instrument_controls)
    if metric_id not in cal.CONTROLS:
        return InstrumentState.CONTRACT_MISMATCH
    implemented = {c.case for c in cal.CONTROLS[metric_id][1]}
    if declared != implemented:
        return InstrumentState.CONTRACT_MISMATCH
    outcomes = cal.calibrate(metric_id)
    if any(not o.passed for o in outcomes):
        return InstrumentState.FAILED_CONTROL
    return InstrumentState.REPORTABLE


def reportable(metric_id: str) -> bool:
    return state_of(metric_id) in REPORTABLE_STATES


def assert_reportable(metric_id: str) -> None:
    state = state_of(metric_id)
    if state not in REPORTABLE_STATES:
        raise RuntimeError(
            f"{metric_id} is {state.value} and may not enter a scientific report. "
            f"Register it, give it falsification controls, and make them pass.")


def report() -> str:
    lines = ["INSTRUMENT REGISTRY", ""]
    for metric_id in sorted(REGISTRY):
        spec = REGISTRY[metric_id]
        state = state_of(metric_id)
        lines.append(f"  {state.value:<26} {metric_id:<24} {spec.conditional_form}")
    return "\n".join(lines)


if __name__ == "__main__":
    print(report())
