"""The missing link: a sealed trace becomes a sealed measurement.

The ledger holds 238 `SCIENTIFIC_TRACE` artifacts and zero `METRIC_RESULT`.
`EmpiricalResultPublicationService` cannot publish without one, the API that
writes them (`record_raw_artifact`) has existed all along, and until now the
only caller was a test.  So the chain from preregistration to evidence was
complete except for the step that reads a trace with an instrument.

This module is that step, and it is deliberately the narrowest thing that can
close it.  **It decides nothing scientific.**  Every field that carries meaning
-- which metric, at which version, under which analysis rule, for which
hypothesis revision -- is copied out of the sealed preregistration and the
execution row.  Anything this module invented would be a finding produced by
the tool rather than by the experiment.

Two arguments are the caller's and cannot be defaulted:

    evaluator        the instrument, already validated for its construct
    classification   the application of the PREREGISTERED decision rule to the
                     number that came out

`classification` is not derived here.  `decision_rule` is free text, so any
mechanical reading of it would be this module quietly inventing the analysis.
The rule travels beside the verdict in `analysis_rule`, copied verbatim from
the endpoint, so a reviewer can check the two against each other -- and
`evidence_publication` refuses the result if they do not match.
"""
from __future__ import annotations

import json
from typing import Any, Callable, Mapping

from terrario.lab.evidence_publication import RESULT_SCHEMA, _RELATIONS
from terrario.lab.persistence.canonical import canonical_json

#: The scope that marks a measurement as a scientific result.  The publication
#: service rejects INSTRUMENT_SELF_AUDIT_NOT_AGENT_EVIDENCE outright, which is
#: how a calibration report is kept from being published as a finding.
RESULT_SCOPE = "AUTHORIZED_SCIENTIFIC_RESULT"

Evaluator = Callable[[Mapping[str, Any]], Mapping[str, Any]]


class MetricResultSealingError(RuntimeError):
    """The measurement cannot be sealed; it is never completed with a guess."""

    code = "METRIC_RESULT_SEALING_REFUSED"

    def __init__(self, reason: str):
        super().__init__(f"{self.code}: {reason}")
        self.reason = reason


def seal_metric_result(api, *, execution_id: str, attempt_id: str, metric_id: str,
                       evaluator: Evaluator, classification: str, actor_id: str,
                       excluded_count: int = 0, missing_count: int = 0) -> Mapping[str, Any]:
    """Evaluate one sealed trace and seal the measurement as a METRIC_RESULT.

    Returns the raw-artifact descriptor, including the `descriptor_hash` that
    `EmpiricalResultPublicationService.eligibility` and `.ingest` take.

    Raises `MetricResultSealingError` rather than sealing something that could
    not be published: a sealed artifact is permanent, and one that fails
    eligibility later is noise in an append-only ledger.
    """
    if classification not in _RELATIONS:
        raise MetricResultSealingError(f"CLASSIFICATION_NOT_ONE_OF_{sorted(_RELATIONS)}")

    with api.artifacts._connect() as con:
        execution = con.execute(
            "SELECT * FROM scientific_executions WHERE execution_id=?", (execution_id,)).fetchone()
        if execution is None:
            raise MetricResultSealingError("EXECUTION_NOT_FOUND")
        attempt = con.execute(
            "SELECT * FROM run_attempts WHERE attempt_id=?", (attempt_id,)).fetchone()
        if attempt is None:
            raise MetricResultSealingError("ATTEMPT_NOT_FOUND")
        trace = con.execute(
            """SELECT * FROM scientific_execution_artifacts WHERE execution_id=? AND attempt_id=?
               AND artifact_type='SCIENTIFIC_TRACE'""", (execution_id, attempt_id)).fetchone()
        if trace is None:
            raise MetricResultSealingError("TRACE_ARTIFACT_MISSING")

    # The preregistration is the source of every scientific field below.  If it
    # does not declare this metric as an endpoint, the measurement is not the
    # one that was promised, and sealing it would be preregistering after the
    # fact.
    try:
        prereg = api.artifacts.current(str(execution["preregistration_id"]), "Preregistration")
        draft = prereg.payload["draft"]
        question = draft["scientific_question"]
        metric = next(x for x in draft["metrics"] if x["metric_id"] == metric_id)
        endpoint = next(x for x in draft["endpoints"] if x["metric_id"] == metric_id)
    except StopIteration:
        raise MetricResultSealingError("METRIC_NOT_A_PREREGISTERED_ENDPOINT") from None
    except Exception as exc:  # noqa: BLE001 - the payload shape is the contract
        raise MetricResultSealingError("PREREGISTRATION_PAYLOAD_UNREADABLE") from exc

    measurement = evaluator(json.loads(api.artifacts.blobs.read(trace["blob_hash"])))
    for key in ("value", "numerator", "denominator"):
        if key not in measurement:
            raise MetricResultSealingError(f"EVALUATOR_DID_NOT_REPORT_{key.upper()}")

    # Lineage is copied, never reconstructed: these five fields are what ties a
    # number to the exact run and the exact sealed design that authorised it.
    measured = {
        "schema_version": RESULT_SCHEMA,
        "execution_id": execution["execution_id"],
        "trial_intent_id": attempt["trial_intent_id"],
        "attempt_id": attempt["attempt_id"],
        "execution_plan_hash": execution["plan_hash"],
        "preregistration_root_hash": execution["preregistration_root_hash"],
        "hypothesis_id": question["hypothesis_id"],
        "hypothesis_revision": question["hypothesis_hash"],
        "metric_id": metric["metric_id"],
        "metric_version": metric["definition_version"],
        "value": measurement["value"],
        "numerator": measurement["numerator"],
        "denominator": measurement["denominator"],
        "excluded_count": int(measurement.get("excluded_count", excluded_count)),
        "missing_count": int(measurement.get("missing_count", missing_count)),
        "epistemic_classification": classification,
        "analysis_rule": endpoint["decision_rule"],
        "trace_blob_hash": trace["blob_hash"],
        "scope": RESULT_SCOPE,
    }

    sealed = api.scientific_executions.record_raw_artifact(
        execution_id, "METRIC_RESULT", canonical_json(measured).encode(), actor_id,
        attempt["trial_intent_id"], attempt_id)
    with api.artifacts._connect() as con:
        row = con.execute(
            """SELECT descriptor_hash FROM scientific_execution_artifacts
               WHERE execution_id=? AND attempt_id=? AND artifact_type='METRIC_RESULT'
               AND blob_hash=?""", (execution_id, attempt_id, sealed["blob_hash"])).fetchone()
    return {**sealed, "descriptor_hash": row["descriptor_hash"], "measured": measured}
