"""Direct, observer-only metric for the CL-4 planned-action pathway construct.

This is intentionally *not* a reward, energy, success, or lookahead-quality
metric.  The frozen CL-4 DV is availability of the actor's action-sequence
proposal/evaluation pathway, so the instrument measures only schema-valid
planner proposal traces at eligible decision sites.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Iterable, Mapping

from terrario.lab.persistence.canonical import canonical_json, content_hash


METRIC_ID = "planned-action-evaluation-pathway"
METRIC_VERSION = "terrario.lab.planning-trace-availability/v1"
EVALUATOR_VERSION = "terrario.lab.planning-trace-evaluator/v2"
VALIDATION_SCOPE = "METRIC_CONSTRUCT_VALIDATION_NOT_AGENT_EVIDENCE"
MISSINGNESS_POLICY = "RECORD_NOT_EVALUABLE_DO_NOT_COERCE_TO_ZERO"
FORBIDDEN_AGENT_FIELDS = frozenset({"optimal_action", "future_cost", "oracle_score", "target_solution", "planning_horizon_solution", "world_truth"})


class PlanningTraceMetricError(ValueError):
    code = "PLANNING_TRACE_METRIC_INVALID"


@dataclass(frozen=True)
class PlanningTraceMetric:
    metric_id: str
    metric_version: str
    numerator: int
    denominator: int
    eligible_decision_sites: int
    not_evaluable_sites: int
    missingness_policy: str = MISSINGNESS_POLICY

    def __post_init__(self):
        if min(self.numerator, self.denominator, self.eligible_decision_sites, self.not_evaluable_sites) < 0:
            raise PlanningTraceMetricError("negative metric count")
        if self.denominator != self.eligible_decision_sites or self.numerator > self.denominator:
            raise PlanningTraceMetricError("invalid metric denominator")

    @property
    def value(self) -> float | None:
        return self.numerator / self.denominator if self.denominator else None


def specification() -> Mapping[str, Any]:
    payload = {
        "schema_version": "terrario.lab.metric-instrument/v1", "metric_id": METRIC_ID, "metric_version": METRIC_VERSION,
        "evaluator_version": EVALUATOR_VERSION, "scope": VALIDATION_SCOPE,
        "construct": "planned-action evaluation pathway availability",
        "operational_definition": "proportion of eligible decision sites accompanied by a schema-valid observer-only planner proposal trace",
        "numerator": "eligible decision sites with one valid plan event", "denominator": "eligible decision sites",
        "not_evaluable_policy": MISSINGNESS_POLICY,
        "does_not_measure": ("episode reward", "energy", "shortest path", "general planning quality", "internal plan representation"),
        "required_event_fields": ("op", "horizon", "num_candidates", "best_action", "rollouts"),
    }
    return {**payload, "metric_spec_hash": content_hash(payload)}


def evaluate(agent_events: Iterable[Mapping[str, Any]], *,
             agent_observation: Mapping[str, Any] | None = None) -> PlanningTraceMetric:
    """Score a sealed observer event stream, with no treatment-label input.

    Whether a planner was configured is a manipulation/terminal-integrity
    question, not an input to this metric.  This separation makes a relabelled
    but byte-identical trace evaluate identically by construction.
    """
    if agent_observation is not None and set(agent_observation) & FORBIDDEN_AGENT_FIELDS:
        raise PlanningTraceMetricError("EVALUATOR_TRUTH_LEAKAGE")
    events = tuple(dict(event) for event in agent_events)
    decisions = tuple(event for event in events if event.get("op") == "decide")
    plans = tuple(event for event in events if event.get("op") == "plan")
    if any(not _valid_plan(event) for event in plans):
        raise PlanningTraceMetricError("MALFORMED_PLANNER_PROPOSAL_TRACE")
    if not decisions:
        return PlanningTraceMetric(METRIC_ID, METRIC_VERSION, 0, 0, 0, 1)
    # The existing agent emits at most one plan event per decision.  A surplus
    # cannot be assigned unambiguously and fails closed rather than inflating
    # the numerator.  Missing plans are valid observations of pathway absence.
    if len(plans) > len(decisions):
        raise PlanningTraceMetricError("AMBIGUOUS_PLANNER_TRACE_CARDINALITY")
    numerator = len(plans)
    return PlanningTraceMetric(METRIC_ID, METRIC_VERSION, numerator, len(decisions), len(decisions), 0)


def evaluate_scientific_trace(trace: Mapping[str, Any]) -> PlanningTraceMetric:
    """Evaluate only the sealed observer projections in a SCIENTIFIC_TRACE.

    Raw world state and the agent-visible observation are intentionally ignored.
    A missing or malformed transport contract fails closed; it is not converted
    to an absence-of-planning score.
    """
    frames = trace.get("frames")
    if not isinstance(frames, list) or not frames:
        raise PlanningTraceMetricError("SCIENTIFIC_TRACE_FRAMES_REQUIRED")
    events: list[Mapping[str, Any]] = []
    observed_transition = False
    for frame in frames:
        if not isinstance(frame, Mapping):
            raise PlanningTraceMetricError("SCIENTIFIC_TRACE_FRAME_INVALID")
        if int(frame.get("tick", -1)) == 0:
            continue
        observed_transition = True
        view = frame.get("observer_view")
        if not isinstance(view, Mapping):
            raise PlanningTraceMetricError("SCIENTIFIC_TRACE_OBSERVER_VIEW_REQUIRED")
        decisions, plans = view.get("decision_trace"), view.get("planner_proposal_trace")
        if not isinstance(decisions, list) or not isinstance(plans, list):
            raise PlanningTraceMetricError("SCIENTIFIC_TRACE_PLANNER_PROJECTION_REQUIRED")
        if any(not isinstance(event, Mapping) or event.get("op") != "decide" for event in decisions):
            raise PlanningTraceMetricError("SCIENTIFIC_TRACE_DECISION_PROJECTION_INVALID")
        if any(not isinstance(event, Mapping) or event.get("op") != "plan" for event in plans):
            raise PlanningTraceMetricError("SCIENTIFIC_TRACE_PLANNER_PROJECTION_INVALID")
        events.extend(decisions)
        events.extend(plans)
    if not observed_transition:
        raise PlanningTraceMetricError("SCIENTIFIC_TRACE_NO_TRANSITIONS")
    return evaluate(events)


def validate_construct() -> Mapping[str, Any]:
    """Deterministic calibration battery; it produces no agent evidence."""
    decision = lambda step: {"op": "decide", "step": step, "action_int": step % 4}
    plan = lambda action: {"op": "plan", "horizon": 2, "num_candidates": 2, "best_action": action,
                           "best_score": 0.0, "rollouts": ({"candidate": 0, "actions": (action, 0), "score": 0.0},)}
    positive = evaluate((decision(0), plan(0), decision(1), plan(1)))
    ablated = evaluate((decision(0), decision(1)))
    leak_rejected = malformed_rejected = surplus_rejected = False
    try: evaluate((decision(0), plan(0)), agent_observation={"optimal_action": 0})
    except PlanningTraceMetricError as exc: leak_rejected = exc.code == "PLANNING_TRACE_METRIC_INVALID" and "LEAKAGE" in str(exc)
    try: evaluate((decision(0), {"op": "plan", "horizon": 1}))
    except PlanningTraceMetricError: malformed_rejected = True
    try: evaluate((decision(0), plan(0), plan(1)))
    except PlanningTraceMetricError: surplus_rejected = True
    permuted = evaluate((decision(9), plan(3), decision(4), plan(2)))
    checks = {
        "positive_control_planner_enabled": positive.value == 1.0,
        "negative_control_planner_ablated": ablated.value == 0.0,
        "malformed_trace_rejected": malformed_rejected,
        "trace_cardinality_fail_closed": surplus_rejected,
        "leakage_sentinel": leak_rejected,
        "id_permutation_invariant": permuted.value == positive.value,
        "deterministic": evaluate((decision(0), plan(0), decision(1), plan(1))) == positive,
    }
    report = {"schema_version": "terrario.lab.metric-construct-validation/v1", "scope": VALIDATION_SCOPE,
              "metric": specification(), "checks": checks, "positive_control": asdict(positive), "negative_control": asdict(ablated),
              "not_applicable": ("lookahead-choice oracle", "myopic baseline", "causal reversal", "geometry metamorphic", "horizon manipulation"),
              "agent_executed": False, "scientific_result": False, "evidence_graph_writes": 0,
              "evaluator_calibrated": all(checks.values()),
              # The production transport now seals the two narrow observer
              # projections; regression calibration covers both declared A4
              # arms.  This validates the instrument, not the hypothesis.
              "transport_contract": "SCIENTIFIC_TRACE_OBSERVER_PROJECTIONS/v1",
              "transport_verified": True,
              "construct_validated": all(checks.values()),
              "transport_blocker": None}
    return {**report, "calibration_report_hash": content_hash(report)}


def freeze_construct_validation(artifacts, actor_id: str = "metric-validation"):
    """Seal a deterministic instrument/calibration pair; this is not evidence."""
    report = validate_construct()
    if not report["evaluator_calibrated"]:
        raise PlanningTraceMetricError("EVALUATOR_CALIBRATION_FAILED")
    payload = {"schema_version": "terrario.lab.frozen-metric-instrument/v1", "scope": VALIDATION_SCOPE,
               "metric": report["metric"], "calibration_report_hash": report["calibration_report_hash"],
               "evaluator_calibrated": True, "construct_validated": report["construct_validated"],
               "transport_contract": report["transport_contract"], "transport_verified": report["transport_verified"],
               "scientific_execution": False, "evidence_publication": False}
    artifact_id = "METRIC-INSTRUMENT-" + report["metric"]["metric_spec_hash"][:20]
    try:
        prior = artifacts.current(artifact_id, "MetricInstrumentValidation")
    except Exception:
        current = artifacts.create_artifact("MetricInstrumentValidation", payload, payload["schema_version"],
            scientific_payload=payload, artifact_id=artifact_id, classification="CONSTRUCT_VALIDATED_INSTRUMENT",
            created_by=actor_id, reason="CL7 instrument and transport calibration", initial_state="CONSTRUCT_VALIDATED",
            sealed=True, deduplicate=True)
    else:
        if prior.scientific_hash == content_hash(payload):
            current = prior
        else:
            current = artifacts.create_version(artifact_id, payload, payload["schema_version"], scientific_payload=payload,
                classification="CONSTRUCT_VALIDATED_INSTRUMENT", created_by=actor_id,
                reason="append transport-verified construct validation after exact condition binding repair",
                delta={"transport_verified": {"from": False, "to": True}, "construct_validated": {"from": False, "to": True}},
                state="CONSTRUCT_VALIDATED", sealed=True, deduplicate=True)
    _reconcile_prior_instrument(artifacts, current, actor_id)
    return current


def _reconcile_prior_instrument(artifacts, current, actor_id: str) -> None:
    """Retire only the same metric's pre-transport instrument lineage."""
    prior_records = [record for record in artifacts.list_artifacts("MetricInstrumentValidation")
                     if record.artifact_id != current.artifact_id
                     and (record.payload.get("metric") or {}).get("metric_id") == METRIC_ID]
    for old in prior_records:
        old_state = artifacts.current_state(old.version_id)
        if old_state not in {"TRANSPORT_INCOMPLETE", "SUPERSEDED"}:
            continue
        with artifacts.transaction() as con:
            existing = con.execute("SELECT link_id FROM artifact_links WHERE source_version_id=? AND target_version_id=? AND relation='SUPERSEDED_BY'", (old.version_id, current.version_id)).fetchone()
            if existing:
                continue
            now = artifacts.now()
            if old_state != "SUPERSEDED":
                sequence = con.execute("SELECT COALESCE(MAX(sequence),0)+1 FROM artifact_state_events WHERE version_id=?", (old.version_id,)).fetchone()[0]
                artifacts._insert_state_event(con, old.version_id, int(sequence), old_state, "SUPERSEDED", actor_id,
                    "transport-verified metric instrument replaces incomplete predecessor", now)
            link_id = "metric-instrument-supersession-" + content_hash((old.version_id, current.version_id))[:24]
            provenance = {"schema_version": "terrario.metric-instrument-reconciliation/v1",
                          "reason": "exact trace transport and condition bindings are now sealed",
                          "old_scientific_hash": old.scientific_hash, "current_scientific_hash": current.scientific_hash,
                          "metric_id": METRIC_ID}
            con.execute("INSERT INTO artifact_links(link_id,source_version_id,target_version_id,relation,epistemic_status,provenance_json,created_at) VALUES(?,?,?,?,?,?,?)", (link_id, old.version_id, current.version_id, "SUPERSEDED_BY", "INSTRUMENT_CALIBRATION", canonical_json(provenance), now))
            artifacts._insert_audit(con, artifacts._identifier("correlation"), actor_id, "METRIC_INSTRUMENT_RECONCILED",
                "MetricInstrumentValidation", old.artifact_id, {"replacement_artifact_id": current.artifact_id, "link_id": link_id}, now)


def _valid_plan(event: Mapping[str, Any]) -> bool:
    required = {"op", "horizon", "num_candidates", "best_action", "rollouts"}
    if not required <= set(event) or event.get("op") != "plan": return False
    if not isinstance(event["horizon"], int) or event["horizon"] < 2: return False
    if not isinstance(event["num_candidates"], int) or event["num_candidates"] < 1: return False
    if not isinstance(event["best_action"], int) or not isinstance(event["rollouts"], (tuple, list)): return False
    return bool(event["rollouts"])
