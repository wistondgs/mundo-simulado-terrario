"""Observer-only viability-recovery metric for the D4 causal-change construct.

Ashby's frame (*An Introduction to Cybernetics*, ch. 10; `TI-0049` in the
project corpus, sha256 verified): ``E`` is the set of essential variables,
``eta`` the subset of E's states in which the organism is viable, ``D`` the
source of disturbance, and ``F`` the regulator interposed between them.  His
criterion for a good regulator is not that E returns but that F *blocks the
transmission of variety* from D to E.

So this reports four numbers rather than one.  "Steps to recovery" alone
rewards a system that swings wildly and snaps back exactly as much as one that
barely moved, and those are different organisms.

Nothing here is emitted by the runtime.  `world_truth.agents[*].energy`,
`world_truth.max_energy` and `world_revision` are already sealed in every
SCIENTIFIC_TRACE frame, and a rule reversal is visible as a change of
`world_revision`.  The detector is a projection over sealed observer data:
the agent is not touched, behaviour stays byte-identical, and no new channel
is added.  `agent_observation` is never read -- the essential variable is the
organism's true state, not its belief about it.

Two numbers are NOT defaulted silently, because they are the scientific
content of the measurement and belong in a preregistration, not in a library:

    viable_floor  the eta boundary, as a fraction of max_energy
    dwell_k       consecutive in-eta ticks required to call it recovered

`validate_construct()` proves the detector on synthetic trajectories whose
answers are known by construction; it makes no claim about any agent.
"""
from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any, Iterable, Mapping

from terrario.lab.persistence.canonical import content_hash

METRIC_ID = "viability-recovery-profile"
METRIC_VERSION = "terrario.lab.viability-recovery/v1"
EVALUATOR_VERSION = "terrario.lab.viability-recovery-evaluator/v1"
VALIDATION_SCOPE = "METRIC_CONSTRUCT_VALIDATION_NOT_AGENT_EVIDENCE"
MISSINGNESS_POLICY = "RECORD_NOT_EVALUABLE_DO_NOT_COERCE_TO_ZERO"

#: Reading any of these would make the measurement about the agent's belief,
#: or about the future, rather than about the essential variable.
FORBIDDEN_FRAME_FIELDS = frozenset({"agent_observation", "cognitive_state"})


class ViabilityRecoveryError(ValueError):
    """The trace cannot support this measurement; it is never coerced to a score."""


@dataclass(frozen=True)
class ViabilityRecovery:
    """Ashby's four quantities over one perturbed episode."""

    evaluable: bool
    perturbation_tick: int | None
    #: max depth below the eta boundary after D, in units of the essential
    #: variable.  0.0 means E never left eta.
    excursion_depth: float
    #: ticks spent outside eta after D.
    dwell_outside: int
    #: ticks from D until E re-enters eta and stays for `dwell_k`.  None means
    #: it never did within the episode -- which is a finding, not a zero.
    recovery_steps: int | None
    #: distinct quantised states of E after D / before D.  Ashby's own
    #: criterion: a good regulator keeps this at or below 1.0.
    variety_ratio: float | None
    #: whether E was inside eta on the final observed tick.  `recovery_steps`
    #: reports the FIRST sustained re-entry and must never be read without
    #: this: the first real D4S run returned recovery_steps=0 for an organism
    #: that was inside eta when the disturbance landed and then decayed out of
    #: it permanently.  Alone, the 0 read as "recovered instantly"; the truth
    #: was "was fine at the blow, then died slowly".
    viable_at_end: bool | None = None
    #: recovered and then left eta again before the episode ended.  Without
    #: this a relapse is indistinguishable from a clean recovery.
    relapse: bool | None = None
    #: the episode ended with E outside eta, so `recovery_steps` is None
    #: because OBSERVATION STOPPED, not because recovery failed.  Conflating
    #: right-censoring with failure biases any aggregate over None.
    censored: bool | None = None
    #: only set by `evaluate_segments`: this segment ended because the NEXT
    #: disturbance arrived while E was still outside eta.  A third cause of
    #: `recovery_steps is None`, and not the same as either of the other two:
    #: observation did not stop, and recovery was not refused -- it was cut
    #: short.  Aggregating it as failure would make a dense schedule look like
    #: a worse organism.
    interrupted: bool | None = None
    reason: str | None = None


def specification(*, viable_floor: float, dwell_k: int, variety_bin: float) -> Mapping[str, Any]:
    """The frozen instrument, hashed with its parameters inside.

    The parameters are part of the identity: a different eta boundary is a
    different measurement, and its hash must differ.
    """
    _check_parameters(viable_floor, dwell_k, variety_bin)
    body = {
        "schema_version": "terrario.lab.metric-instrument/v1",
        "metric_id": METRIC_ID, "metric_version": METRIC_VERSION,
        "evaluator_version": EVALUATOR_VERSION, "scope": VALIDATION_SCOPE,
        "construct": "maintenance of essential variables within the viable set under disturbance",
        "theoretical_source": "Ashby, An Introduction to Cybernetics, ch. 10 (corpus TI-0049)",
        "operational_definition": (
            "over a trace whose world_revision changes at D: depth and duration of the "
            "excursion of the essential variable below eta, ticks until it re-enters eta "
            "for dwell_k consecutive ticks, and the ratio of its quantised variety after "
            "D to before D"),
        "essential_variable": "world_truth.agents[*].energy (minimum across agents)",
        "eta": f"energy >= {viable_floor} * world_truth.max_energy",
        "disturbance_marker": "change of world_revision",
        "parameters": {"viable_floor": viable_floor, "dwell_k": dwell_k, "variety_bin": variety_bin},
        "not_evaluable_policy": MISSINGNESS_POLICY,
        # A consumer must not have to discover this coupling by being burned
        # by it, so it travels inside the hashed instrument.
        "reading_rule": ("recovery_steps is the FIRST sustained re-entry and is "
                         "meaningless alone: read it with viable_at_end, or an "
                         "organism that was inside eta at the disturbance and "
                         "decayed out of it afterwards reports 0. A None recovery_steps "
                         "means 'never recovered' only when censored is False"),
        "does_not_measure": (
            "reward, task success or goal attainment",
            "whether the organism reorganised its own parameters (Ashby's ultrastability "
            "proper) -- only that the essential variable returned",
            "planning quality or any internal representation",
            "adaptation in any sense beyond the declared eta boundary",
        ),
        "forbidden_frame_fields": tuple(sorted(FORBIDDEN_FRAME_FIELDS)),
    }
    return dict(body) | {"metric_spec_hash": content_hash(body)}


SEGMENT_METRIC_ID = "viability-recovery-profile-per-disturbance"
SEGMENT_METRIC_VERSION = "terrario.lab.viability-recovery-segments/v1"
SEGMENT_EVALUATOR_VERSION = "terrario.lab.viability-recovery-segment-evaluator/v1"


def segment_specification(*, viable_floor: float, dwell_k: int,
                          variety_bin: float) -> Mapping[str, Any]:
    """The per-disturbance instrument, which is a DIFFERENT measurement.

    `specification()` is left untouched on purpose: a single-disturbance
    reading and a per-disturbance reading are not the same instrument, and
    giving them one hash would let a design cite one and run the other.
    """
    _check_parameters(viable_floor, dwell_k, variety_bin)
    body = {
        "schema_version": "terrario.lab.metric-instrument/v1",
        "metric_id": SEGMENT_METRIC_ID, "metric_version": SEGMENT_METRIC_VERSION,
        "evaluator_version": SEGMENT_EVALUATOR_VERSION, "scope": VALIDATION_SCOPE,
        "construct": ("maintenance of essential variables within the viable set under a "
                      "SEQUENCE of disturbances, reported once per disturbance"),
        "theoretical_source": "Ashby, An Introduction to Cybernetics, ch. 10 (corpus TI-0049)",
        "operational_definition": (
            "the trace is split at every change of world_revision; each segment runs from "
            "one disturbance to the next (the last runs to the end of the episode) and is "
            "evaluated by the single-disturbance projection over that window"),
        "base_instrument": METRIC_VERSION,
        "parameters": {"viable_floor": viable_floor, "dwell_k": dwell_k, "variety_bin": variety_bin},
        "not_evaluable_policy": MISSINGNESS_POLICY,
        "reading_rule": (
            "recovery_steps is None for THREE distinct reasons, and they must not be "
            "pooled: never recovered (censored False, interrupted False); observation "
            "stopped with E outside eta (censored True); the next disturbance arrived "
            "first (interrupted True). Only the last segment of an episode can be "
            "censored, and only a non-last segment can be interrupted"),
        "does_not_measure": (
            "whether recovery got faster BECAUSE of the earlier disturbances -- the "
            "instrument reports each segment, the comparison between them is a design",
            "reorganisation of the organism's own parameters",
            "reward, task success or goal attainment",
        ),
        "forbidden_frame_fields": tuple(sorted(FORBIDDEN_FRAME_FIELDS)),
    }
    return dict(body) | {"metric_spec_hash": content_hash(body)}


def _check_parameters(viable_floor: float, dwell_k: int, variety_bin: float) -> None:
    if not 0.0 < float(viable_floor) < 1.0:
        raise ViabilityRecoveryError("VIABLE_FLOOR_MUST_BE_A_FRACTION_STRICTLY_BETWEEN_0_AND_1")
    if int(dwell_k) < 1:
        raise ViabilityRecoveryError("DWELL_K_MUST_BE_AT_LEAST_1")
    if float(variety_bin) <= 0.0:
        raise ViabilityRecoveryError("VARIETY_BIN_MUST_BE_POSITIVE")


def evaluate(samples: Iterable[Mapping[str, Any]], *,
             viable_floor: float, dwell_k: int, variety_bin: float) -> ViabilityRecovery:
    """Evaluate ``[{tick, energy, max_energy, revision}, ...]`` in tick order."""
    _check_parameters(viable_floor, dwell_k, variety_bin)
    rows = sorted(({"tick": int(s["tick"]), "energy": float(s["energy"]),
                    "max_energy": float(s["max_energy"]), "revision": int(s["revision"])}
                   for s in samples), key=lambda s: s["tick"])
    if not rows:
        return ViabilityRecovery(False, None, 0.0, 0, None, None, reason="NO_SAMPLES")

    first_revision = rows[0]["revision"]
    perturbed = next((r for r in rows if r["revision"] != first_revision), None)
    if perturbed is None:
        # An unperturbed episode cannot speak about recovery.  Reporting 0 here
        # would read as "recovered instantly", which is the opposite of true.
        return ViabilityRecovery(False, None, 0.0, 0, None, None, reason="NO_DISTURBANCE_OBSERVED")
    d_tick = perturbed["tick"]

    before = [r for r in rows if r["tick"] < d_tick]
    after = [r for r in rows if r["tick"] >= d_tick]
    if not after:
        return ViabilityRecovery(False, d_tick, 0.0, 0, None, None, reason="NO_POST_DISTURBANCE_SAMPLES")

    floor_of = lambda r: viable_floor * r["max_energy"]
    deficits = [max(0.0, floor_of(r) - r["energy"]) for r in after]
    excursion = max(deficits)
    dwell = sum(1 for d in deficits if d > 0.0)

    recovery = None
    if dwell == 0:
        recovery = 0  # never left eta: the regulator absorbed the disturbance
    else:
        run = 0
        for r in after:
            inside = r["energy"] >= floor_of(r)
            run = run + 1 if inside else 0
            if run >= int(dwell_k):
                recovery = (r["tick"] - int(dwell_k) + 1) - d_tick
                break

    variety = None
    if before:
        quantise = lambda r: round(r["energy"] / float(variety_bin))
        pre = len({quantise(r) for r in before})
        post = len({quantise(r) for r in after})
        variety = post / pre if pre else None

    viable_at_end = after[-1]["energy"] >= floor_of(after[-1])
    # Right-censoring: observation stopped with E outside eta.  recovery_steps
    # is None because we stopped looking, not because recovery failed.
    censored = recovery is None and not viable_at_end
    relapse = recovery is not None and not viable_at_end
    return ViabilityRecovery(True, d_tick, excursion, dwell, recovery, variety,
                             viable_at_end=viable_at_end, relapse=relapse, censored=censored)


def evaluate_scientific_trace(trace: Mapping[str, Any], *, viable_floor: float,
                              dwell_k: int, variety_bin: float) -> ViabilityRecovery:
    """Project a sealed SCIENTIFIC_TRACE, reading observer truth only."""
    return evaluate(_trace_samples(trace), viable_floor=viable_floor,
                    dwell_k=dwell_k, variety_bin=variety_bin)


def evaluate_scientific_trace_segments(trace: Mapping[str, Any], *, viable_floor: float,
                                       dwell_k: int,
                                       variety_bin: float) -> tuple[ViabilityRecovery, ...]:
    """Per-disturbance projection of a sealed SCIENTIFIC_TRACE."""
    return evaluate_segments(_trace_samples(trace), viable_floor=viable_floor,
                             dwell_k=dwell_k, variety_bin=variety_bin)


def _trace_samples(trace: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    """Read observer truth out of sealed frames.  `agent_observation` is never read."""
    frames = trace.get("frames")
    if not isinstance(frames, list) or not frames:
        raise ViabilityRecoveryError("SCIENTIFIC_TRACE_FRAMES_REQUIRED")
    samples = []
    for frame in frames:
        if not isinstance(frame, Mapping):
            raise ViabilityRecoveryError("SCIENTIFIC_TRACE_FRAME_INVALID")
        truth = frame.get("world_truth")
        if not isinstance(truth, Mapping):
            raise ViabilityRecoveryError("SCIENTIFIC_TRACE_WORLD_TRUTH_REQUIRED")
        agents = truth.get("agents")
        entries = list(agents.values()) if isinstance(agents, Mapping) else agents
        if not isinstance(entries, list) or not entries:
            raise ViabilityRecoveryError("SCIENTIFIC_TRACE_AGENT_STATE_REQUIRED")
        energies = [float(a["energy"]) for a in entries if isinstance(a, Mapping) and "energy" in a]
        if not energies:
            raise ViabilityRecoveryError("SCIENTIFIC_TRACE_ENERGY_REQUIRED")
        max_energy = truth.get("max_energy")
        if not isinstance(max_energy, (int, float)) or float(max_energy) <= 0:
            raise ViabilityRecoveryError("SCIENTIFIC_TRACE_MAX_ENERGY_REQUIRED")
        revision = frame.get("world_revision", truth.get("rules_version"))
        if revision is None:
            raise ViabilityRecoveryError("SCIENTIFIC_TRACE_WORLD_REVISION_REQUIRED")
        # Minimum across agents: the organism is out of eta as soon as ANY
        # essential variable is, not once the average is.
        samples.append({"tick": int(frame.get("tick", 0)), "energy": min(energies),
                        "max_energy": float(max_energy), "revision": int(revision)})
    return samples


def evaluate_segments(samples: Iterable[Mapping[str, Any]], *, viable_floor: float,
                      dwell_k: int, variety_bin: float) -> tuple[ViabilityRecovery, ...]:
    """One `ViabilityRecovery` per disturbance, in order.

    D4S declares one change event, so the single-disturbance reading is the
    whole story there.  A scenario that declares several -- D4T -- breaks it:
    `evaluate` takes the FIRST change of `world_revision` and treats everything
    after as one excursion, so it reports the first recovery and silently pools
    every later one into `dwell_outside`.  That is not a smaller answer, it is
    a wrong one.

    Each segment runs from its disturbance to the next, the last to the end of
    the episode, and carries the preceding window so `variety_ratio` still has
    a before.  Returns `()` when the trace holds no disturbance at all --
    `evaluate` already reports that case as NO_DISTURBANCE_OBSERVED and this
    function must not invent a segment for it.
    """
    _check_parameters(viable_floor, dwell_k, variety_bin)
    rows = sorted(({"tick": int(s["tick"]), "energy": float(s["energy"]),
                    "max_energy": float(s["max_energy"]), "revision": int(s["revision"])}
                   for s in samples), key=lambda s: s["tick"])
    boundaries = [i for i in range(1, len(rows)) if rows[i]["revision"] != rows[i - 1]["revision"]]
    if not boundaries:
        return ()

    starts = [0] + boundaries
    results: list[ViabilityRecovery] = []
    for n, boundary in enumerate(boundaries):
        last = n + 1 == len(boundaries)
        end = len(rows) if last else boundaries[n + 1]
        window = rows[starts[n]:end]
        result = evaluate(window, viable_floor=viable_floor, dwell_k=dwell_k,
                          variety_bin=variety_bin)
        if result.evaluable:
            # Only the final segment can be right-censored: for every other one
            # observation continued, it was the next disturbance that cut the
            # window.  Recording that as censoring would blame the episode's end
            # for something the schedule did.
            interrupted = bool(not last and result.recovery_steps is None)
            result = replace(result, interrupted=interrupted,
                             censored=result.censored if last else False)
        results.append(result)
    return tuple(results)


def _trajectory(energies, *, revision_at: int | None, max_energy: float = 100.0):
    """Synthetic samples; revision flips at `revision_at` (None = undisturbed)."""
    return [{"tick": i, "energy": float(e), "max_energy": max_energy,
             "revision": 1 if revision_at is None or i < revision_at else 2}
            for i, e in enumerate(energies)]


def validate_construct() -> Mapping[str, Any]:
    """Prove the detector on trajectories whose answer is known by construction.

    This validates the INSTRUMENT, not any agent.  Each case is a claim the
    detector must satisfy for the construct to be measurable at all; the
    calibration set contains no agent output.
    """
    floor, k, bin_ = 0.5, 3, 1.0
    cases: list[Mapping[str, Any]] = []

    def case(name: str, energies, revision_at, check) -> None:
        result = evaluate(_trajectory(energies, revision_at=revision_at),
                          viable_floor=floor, dwell_k=k, variety_bin=bin_)
        cases.append({"case": name, "passed": bool(check(result)),
                      "observed": {"evaluable": result.evaluable, "D": result.perturbation_tick,
                                   "excursion": result.excursion_depth, "dwell": result.dwell_outside,
                                   "recovery": result.recovery_steps, "reason": result.reason}})

    # An undisturbed episode says nothing about recovery, and must not say zero.
    case("undisturbed_is_not_evaluable", [90] * 10, None,
         lambda r: not r.evaluable and r.reason == "NO_DISTURBANCE_OBSERVED" and r.recovery_steps is None)
    # The regulator absorbed the disturbance: E never left eta.
    case("absorbed_disturbance_recovers_in_zero", [90] * 5 + [88] * 5, 5,
         lambda r: r.evaluable and r.excursion_depth == 0.0 and r.dwell_outside == 0 and r.recovery_steps == 0)
    # Leaves eta at D, returns at tick 8 and stays: recovery = 8 - 5 = 3.
    case("dips_then_returns", [90] * 5 + [40, 40, 40] + [80] * 5, 5,
         lambda r: r.evaluable and r.dwell_outside == 3 and r.recovery_steps == 3
                   and abs(r.excursion_depth - 10.0) < 1e-9)
    # Never returns: that is a finding, not a zero and not a small number.
    case("never_returns_is_none_not_zero", [90] * 5 + [10] * 8, 5,
         lambda r: r.evaluable and r.recovery_steps is None and r.dwell_outside == 8)
    # A re-entry shorter than dwell_k does not count as recovery.
    case("brief_reentry_does_not_count", [90] * 5 + [40, 80, 80, 40, 40, 80, 80, 80], 5,
         lambda r: r.evaluable and r.recovery_steps == 5)
    # Ashby's own criterion: variety reaching E rises when the regulator fails.
    wild = evaluate(_trajectory([90] * 5 + [70, 40, 85, 30, 95, 55], revision_at=5),
                    viable_floor=floor, dwell_k=k, variety_bin=bin_)
    calm = evaluate(_trajectory([90] * 5 + [90] * 6, revision_at=5),
                    viable_floor=floor, dwell_k=k, variety_bin=bin_)
    cases.append({"case": "variety_ratio_separates_regulated_from_unregulated",
                  "passed": bool(wild.variety_ratio and calm.variety_ratio
                                 and wild.variety_ratio > calm.variety_ratio),
                  "observed": {"unregulated": wild.variety_ratio, "regulated": calm.variety_ratio}})

    report = {"schema_version": "terrario.lab.metric-construct-validation/v1",
              "metric_id": METRIC_ID, "metric_version": METRIC_VERSION,
              "evaluator_version": EVALUATOR_VERSION, "scope": VALIDATION_SCOPE,
              "parameters": {"viable_floor": floor, "dwell_k": k, "variety_bin": bin_},
              "cases": tuple(cases),
              "all_passed": all(c["passed"] for c in cases)}
    return dict(report) | {"calibration_report_hash": content_hash(report)}


def validate_segment_construct() -> Mapping[str, Any]:
    """Prove the per-disturbance detector on schedules whose answer is known.

    Separate from `validate_construct` so the base instrument's calibration
    report hash does not move.  Validates the INSTRUMENT; no agent output is
    involved.
    """
    floor, k, bin_ = 0.5, 3, 1.0
    cases: list[Mapping[str, Any]] = []

    def rows(energies, revisions):
        return [{"tick": i, "energy": float(e), "max_energy": 100.0, "revision": int(r)}
                for i, (e, r) in enumerate(zip(energies, revisions))]

    def case(name: str, samples, check) -> None:
        got = evaluate_segments(samples, viable_floor=floor, dwell_k=k, variety_bin=bin_)
        cases.append({"case": name, "passed": bool(check(got)),
                      "observed": [{"D": x.perturbation_tick, "dwell": x.dwell_outside,
                                    "recovery": x.recovery_steps, "interrupted": x.interrupted,
                                    "censored": x.censored} for x in got]})

    # An undisturbed trace has no segments.  Returning one would invent a
    # disturbance that never happened.
    case("undisturbed_yields_no_segments", rows([90] * 10, [1] * 10), lambda r: r == ())

    # One disturbance must agree with the base instrument exactly, or the two
    # readings would disagree about the same episode.
    single = rows([90] * 5 + [40, 40, 40] + [80] * 5, [1] * 5 + [2] * 8)
    base = evaluate(single, viable_floor=floor, dwell_k=k, variety_bin=bin_)
    got = evaluate_segments(single, viable_floor=floor, dwell_k=k, variety_bin=bin_)
    cases.append({"case": "single_disturbance_agrees_with_base_instrument",
                  "passed": bool(len(got) == 1
                                 and got[0].perturbation_tick == base.perturbation_tick
                                 and got[0].recovery_steps == base.recovery_steps
                                 and got[0].dwell_outside == base.dwell_outside),
                  "observed": {"base": base.recovery_steps, "segment": got[0].recovery_steps}})

    # Three disturbances, three recoveries.  The base instrument reports the
    # first and pools the rest; this must report each.
    three = rows([90] * 5 + [40, 40, 40] + [90] * 7 + [40, 40, 40] + [90] * 7 + [40, 40, 40] + [90] * 7,
                 [1] * 5 + [2] * 10 + [3] * 10 + [4] * 10)
    case("three_disturbances_yield_three_segments",
         three, lambda r: len(r) == 3 and [x.recovery_steps for x in r] == [3, 3, 3])

    # The design question: a shortening sequence must come out as different
    # numbers, not as one pooled figure.
    faster = rows([90] * 5 + [40] * 5 + [90] * 5 + [40] * 3 + [90] * 7 + [40] + [90] * 9,
                  [1] * 5 + [2] * 10 + [3] * 10 + [4] * 10)
    case("shortening_recoveries_are_separable",
         faster, lambda r: len(r) == 3 and r[0].recovery_steps > r[1].recovery_steps > r[2].recovery_steps)

    # Cut short by the next disturbance: not censoring, not failure.
    cut = rows([90] * 5 + [40] * 10 + [90] * 10, [1] * 5 + [2] * 10 + [3] * 10)
    case("segment_cut_by_next_disturbance_is_interrupted",
         cut, lambda r: len(r) == 2 and r[0].recovery_steps is None
              and r[0].interrupted is True and r[0].censored is False)

    # Only the last segment can be right-censored.
    censored = rows([90] * 5 + [40] * 5 + [90] * 5 + [40] * 5, [1] * 5 + [2] * 10 + [3] * 5)
    case("only_the_last_segment_can_be_censored",
         censored, lambda r: len(r) == 2 and r[0].censored is False
              and r[1].censored is True and r[1].interrupted is False)

    report = {"schema_version": "terrario.lab.metric-construct-validation/v1",
              "metric_id": SEGMENT_METRIC_ID, "metric_version": SEGMENT_METRIC_VERSION,
              "evaluator_version": SEGMENT_EVALUATOR_VERSION, "scope": VALIDATION_SCOPE,
              "parameters": {"viable_floor": floor, "dwell_k": k, "variety_bin": bin_},
              "cases": tuple(cases),
              "all_passed": all(c["passed"] for c in cases)}
    return dict(report) | {"calibration_report_hash": content_hash(report)}
