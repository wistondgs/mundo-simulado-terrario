"""Fail-closed publication of authorized scientific results as empirical evidence.

Execution deliberately seals only raw artifacts.  This module is the separate
CL-7 boundary that may publish a *verified*, preregistered metric result.  It
never modifies the historical TheoryGraph/EvidenceGraph projection and it
never changes a hypothesis into truth.  The empirical ledger is append-only;
the aggregate epistemic view is reconstructed from its evidence rows.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping

from terrario.lab.execution.domain import ExecutionState, VerificationClass
from terrario.lab.persistence.canonical import canonical_json, content_hash


RESULT_SCHEMA = "terrario.scientific-metric-result/v1"
ENVELOPE_SCHEMA = "terrario.scientific-result-envelope/v1"
EVIDENCE_SCHEMA = "terrario.empirical-evidence/v1"
_RELATIONS = frozenset({"EVIDENCE_FOR", "EVIDENCE_AGAINST", "UNRESOLVED"})


class ResultPublicationError(RuntimeError):
    code = "RESULT_PUBLICATION_ERROR"


class ResultIneligible(ResultPublicationError):
    code = "REJECT_NOT_SCIENTIFIC_RESULT"


class ResultIntegrityError(ResultPublicationError):
    code = "RESULT_INTEGRITY_INVALID"


@dataclass(frozen=True)
class EligibilityReport:
    eligible: bool
    blockers: tuple[str, ...]
    warnings: tuple[str, ...]
    envelope: Mapping[str, Any] | None = None
    schema_version: str = "terrario.result-eligibility/v1"


class EmpiricalResultPublicationService:
    """The only writer for the durable CL-7 empirical result ledger.

    ``metric_artifact_descriptor_hash`` must name a CAS-sealed
    ``METRIC_RESULT`` artifact.  Requiring the descriptor instead of a path
    prevents a temporary filesystem location from becoming scientific identity.
    """

    def __init__(self, artifacts, preregistrations):
        self.artifacts = artifacts
        self.preregistrations = preregistrations

    def eligibility(self, execution_id: str, attempt_id: str,
                    metric_artifact_descriptor_hash: str) -> EligibilityReport:
        blockers: list[str] = []
        warnings: list[str] = []
        with self.artifacts._connect() as con:
            execution = con.execute("SELECT * FROM scientific_executions WHERE execution_id=?", (execution_id,)).fetchone()
            if execution is None:
                return EligibilityReport(False, ("EXECUTION_NOT_FOUND",), ())
            if execution["state"] != ExecutionState.COMPLETED.value:
                blockers.append("EXECUTION_NOT_COMPLETED")
            if not execution["authorization_id"] or not execution["authorization_consumed"]:
                blockers.append("EXECUTION_NOT_AUTHORIZED")
            if not execution["plan_hash"] or not execution["artifact_root_hash"]:
                blockers.append("EXECUTION_NOT_SEALED")

            verification = con.execute("""SELECT report_json FROM scientific_execution_verifications
                WHERE execution_id=? ORDER BY created_at DESC LIMIT 1""", (execution_id,)).fetchone()
            if verification is None:
                blockers.append("EXECUTION_UNVERIFIED")
            else:
                report = json.loads(verification["report_json"])
                if report.get("classification") not in {VerificationClass.PASS.value, VerificationClass.DEVIATED.value}:
                    blockers.append("EXECUTION_VERIFICATION_NOT_PASS")
                elif report.get("classification") == VerificationClass.DEVIATED.value:
                    warnings.append("EXECUTION_DEVIATED_QUALIFIED")

            attempt = con.execute("""SELECT attempts.*, intents.identity_json, batches.idempotency_key
                FROM run_attempts attempts JOIN trial_intents intents ON intents.trial_intent_id=attempts.trial_intent_id
                JOIN execution_jobs jobs ON jobs.trial_intent_id=intents.trial_intent_id
                JOIN execution_batches batches ON batches.batch_id=jobs.batch_id
                WHERE attempts.attempt_id=?""", (attempt_id,)).fetchone()
            if attempt is None:
                blockers.append("ATTEMPT_NOT_FOUND")
            elif attempt["idempotency_key"] != execution_id:
                blockers.append("CROSS_LINEAGE_ATTEMPT")
            elif attempt["projected_state"] != "COMPLETED":
                blockers.append("ATTEMPT_NOT_COMPLETED")

            metric_artifact = con.execute("""SELECT * FROM scientific_execution_artifacts
                WHERE descriptor_hash=? AND execution_id=? AND attempt_id=? AND artifact_type='METRIC_RESULT'""",
                (metric_artifact_descriptor_hash, execution_id, attempt_id)).fetchone()
            if metric_artifact is None:
                blockers.append("METRIC_RESULT_ARTIFACT_NOT_SEALED")
                return EligibilityReport(False, tuple(sorted(set(blockers))), tuple(sorted(set(warnings))))
            if not self.artifacts.blobs.verify(str(metric_artifact["blob_hash"])):
                blockers.append("METRIC_RESULT_CAS_INVALID")

            trace_artifact = con.execute("""SELECT * FROM scientific_execution_artifacts
                WHERE execution_id=? AND attempt_id=? AND artifact_type='SCIENTIFIC_TRACE'
                ORDER BY created_at DESC LIMIT 1""", (execution_id, attempt_id)).fetchone()
            if trace_artifact is None:
                blockers.append("TRACE_ARTIFACT_MISSING")
            elif not self.artifacts.blobs.verify(str(trace_artifact["blob_hash"])):
                blockers.append("TRACE_CAS_INVALID")

            try:
                measured = json.loads(self.artifacts.blobs.read(str(metric_artifact["blob_hash"])))
            except Exception:
                blockers.append("METRIC_RESULT_PAYLOAD_INVALID")
                return EligibilityReport(False, tuple(sorted(set(blockers))), tuple(sorted(set(warnings))))
            envelope = self._envelope(con, execution, attempt, metric_artifact, trace_artifact, measured, blockers, warnings)
        return EligibilityReport(not blockers, tuple(sorted(set(blockers))), tuple(sorted(set(warnings))), envelope)

    def ingest(self, execution_id: str, attempt_id: str, metric_artifact_descriptor_hash: str) -> Mapping[str, Any]:
        report = self.eligibility(execution_id, attempt_id, metric_artifact_descriptor_hash)
        if not report.eligible or report.envelope is None:
            raise ResultIneligible("; ".join(report.blockers))
        envelope = dict(report.envelope)
        result_hash = content_hash(envelope)
        result_id = f"RESULT-{result_hash[:20]}"
        relation = str(envelope["epistemic_classification"])
        evidence_payload = {"schema_version": EVIDENCE_SCHEMA, "result_hash": result_hash,
                            "hypothesis_id": envelope["hypothesis_id"], "hypothesis_revision": envelope["hypothesis_revision"],
                            "relation": relation, "qualification": envelope["qualification"]}
        evidence_hash = content_hash(evidence_payload)
        evidence_id = f"EVIDENCE-{evidence_hash[:20]}"
        now = self.artifacts.now()
        with self.artifacts.transaction() as con:
            existing = con.execute("SELECT result_id FROM scientific_results WHERE result_hash=?", (result_hash,)).fetchone()
            if existing:
                return self.get_result(str(existing["result_id"])) | {"deduplicated": True}
            con.execute("""INSERT INTO scientific_results(
                result_id,result_hash,execution_id,trial_intent_id,attempt_id,preregistration_id,preregistration_root_hash,
                execution_plan_hash,hypothesis_id,hypothesis_revision,metric_id,metric_version,
                metric_artifact_descriptor_hash,trace_artifact_descriptor_hash,envelope_json,created_at)
                VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (result_id, result_hash, envelope["execution_id"], envelope["trial_intent_id"], envelope["attempt_id"],
                 envelope["preregistration_id"], envelope["preregistration_root_hash"], envelope["execution_plan_hash"],
                 envelope["hypothesis_id"], envelope["hypothesis_revision"], envelope["metric_id"], envelope["metric_version"],
                 envelope["metric_artifact_descriptor_hash"], envelope["trace_artifact_descriptor_hash"], canonical_json(envelope), now))
            self._after_result_insert(con, envelope)
            con.execute("""INSERT INTO empirical_evidence(evidence_id,evidence_hash,result_id,hypothesis_id,hypothesis_revision,relation,qualification,created_at)
                VALUES(?,?,?,?,?,?,?,?)""", (evidence_id, evidence_hash, result_id, envelope["hypothesis_id"],
                envelope["hypothesis_revision"], relation, envelope["qualification"], now))
            for source_kind, source_id, target_kind, target_id, edge_relation in (
                ("EmpiricalEvidence", evidence_id, "ScientificResult", result_id, "OBSERVES"),
                ("ScientificResult", result_id, "TrialAttempt", envelope["attempt_id"], "PRODUCED_BY"),
                ("ScientificResult", result_id, "ScientificExecution", envelope["execution_id"], "PART_OF_EXECUTION"),
                ("ScientificResult", result_id, "Preregistration", envelope["preregistration_id"], "UNDER_PROTOCOL"),
                ("ScientificResult", result_id, "OperationalHypothesis", envelope["hypothesis_id"], "TESTS"),
                ("ScientificResult", result_id, "Metric", envelope["metric_id"], "MEASURES"),
            ):
                link_id = f"empirical-link-{content_hash((evidence_id, source_kind, source_id, target_kind, target_id, edge_relation))[:24]}"
                con.execute("""INSERT INTO empirical_evidence_links(link_id,evidence_id,source_kind,source_id,target_kind,target_id,relation,created_at)
                    VALUES(?,?,?,?,?,?,?,?)""", (link_id, evidence_id, source_kind, source_id, target_kind, target_id, edge_relation, now))
        return self.get_result(result_id) | {"deduplicated": False}

    def get_result(self, result_id: str) -> Mapping[str, Any]:
        with self.artifacts._connect() as con:
            row = con.execute("SELECT * FROM scientific_results WHERE result_id=?", (result_id,)).fetchone()
            if row is None:
                raise ResultPublicationError("RESULT_NOT_FOUND")
            evidence = con.execute("SELECT * FROM empirical_evidence WHERE result_id=?", (result_id,)).fetchone()
            return {"result_id": result_id, "result_hash": row["result_hash"], "envelope": json.loads(row["envelope_json"]),
                    "evidence_id": evidence["evidence_id"], "evidence_hash": evidence["evidence_hash"],
                    "epistemic_classification": evidence["relation"], "qualification": evidence["qualification"],
                    "scientific_result": True, "evidence_publication": True}

    def evidence_for_hypothesis(self, hypothesis_id: str, hypothesis_revision: str | None = None) -> Mapping[str, Any]:
        query = "SELECT * FROM empirical_evidence WHERE hypothesis_id=?"
        values: list[str] = [hypothesis_id]
        if hypothesis_revision is not None:
            query += " AND hypothesis_revision=?"; values.append(hypothesis_revision)
        query += " ORDER BY created_at,evidence_id"
        with self.artifacts._connect() as con:
            rows = con.execute(query, values).fetchall()
        relations = {str(row["relation"]) for row in rows}
        aggregate = "UNRESOLVED" if len(relations) != 1 else (next(iter(relations)) if relations else "UNRESOLVED")
        return {"hypothesis_id": hypothesis_id, "hypothesis_revision": hypothesis_revision,
                "evidence_ids": tuple(str(row["evidence_id"]) for row in rows), "relations": tuple(str(row["relation"]) for row in rows),
                "aggregate_epistemic_status": aggregate, "automatic_truth_promotion": False}

    def provenance_for_result(self, result_id: str) -> Mapping[str, Any]:
        result = self.get_result(result_id)
        with self.artifacts._connect() as con:
            rows = con.execute("SELECT source_kind,source_id,target_kind,target_id,relation FROM empirical_evidence_links WHERE evidence_id=? ORDER BY relation,target_kind,target_id", (result["evidence_id"],)).fetchall()
        return {"result_id": result_id, "evidence_id": result["evidence_id"], "forward": tuple(dict(row) for row in rows)}

    def provenance_for_hypothesis(self, hypothesis_id: str) -> tuple[Mapping[str, Any], ...]:
        with self.artifacts._connect() as con:
            rows = con.execute("""SELECT results.result_id FROM scientific_results results
                JOIN empirical_evidence evidence ON evidence.result_id=results.result_id
                WHERE evidence.hypothesis_id=? ORDER BY results.created_at,results.result_id""", (hypothesis_id,)).fetchall()
        return tuple(self.provenance_for_result(str(row["result_id"])) for row in rows)

    def verify_integrity(self, result_id: str) -> Mapping[str, Any]:
        result = self.get_result(result_id)
        envelope = result["envelope"]
        ok = content_hash(envelope) == result["result_hash"]
        with self.artifacts._connect() as con:
            rows = con.execute("SELECT blob_hash FROM scientific_execution_artifacts WHERE descriptor_hash IN (?,?)",
                (envelope["metric_artifact_descriptor_hash"], envelope["trace_artifact_descriptor_hash"])).fetchall()
        cas_ok = len(rows) == 2 and all(self.artifacts.blobs.verify(str(row["blob_hash"])) for row in rows)
        return {"result_id": result_id, "valid": ok and cas_ok, "result_hash": ok, "cas": cas_ok}

    def status(self) -> Mapping[str, Any]:
        """Read-only publication readiness; never turns a pending run into evidence."""
        with self.artifacts._connect() as con:
            results = int(con.execute("SELECT COUNT(*) FROM scientific_results").fetchone()[0])
            evidence = int(con.execute("SELECT COUNT(*) FROM empirical_evidence").fetchone()[0])
            completed = int(con.execute("SELECT COUNT(*) FROM scientific_executions WHERE state='COMPLETED'").fetchone()[0])
            verified = int(con.execute("""SELECT COUNT(DISTINCT execution_id) FROM scientific_execution_verifications
                WHERE json_extract(report_json, '$.classification') IN ('PASS','DEVIATED')""").fetchone()[0])
        return {"schema_version": "terrario.empirical-result-publication-status/v1", "scientific_results": results,
                "empirical_evidence": evidence, "completed_executions": completed, "verified_executions": verified,
                "automatic_execution": False, "automatic_truth_promotion": False}

    def _after_result_insert(self, _connection, _envelope):
        """A narrow test seam for proving transaction rollback; production is a no-op."""

    def _envelope(self, con, execution, attempt, metric_artifact, trace_artifact, measured, blockers, warnings):
        required = {"schema_version", "execution_id", "trial_intent_id", "attempt_id", "execution_plan_hash",
                    "preregistration_root_hash", "hypothesis_id", "hypothesis_revision", "metric_id", "metric_version",
                    "value", "numerator", "denominator", "excluded_count", "missing_count", "epistemic_classification",
                    "analysis_rule", "trace_blob_hash", "scope"}
        if not isinstance(measured, Mapping) or set(measured) != required:
            blockers.append("METRIC_RESULT_SCHEMA_INVALID"); return None
        if measured["schema_version"] != RESULT_SCHEMA:
            blockers.append("METRIC_RESULT_SCHEMA_VERSION_INVALID")
        if measured["scope"] == "INSTRUMENT_SELF_AUDIT_NOT_AGENT_EVIDENCE":
            blockers.append("REJECT_NOT_SCIENTIFIC_RESULT")
        identity = json.loads(attempt["identity_json"])
        exact = {
            "execution_id": execution["execution_id"], "trial_intent_id": attempt["trial_intent_id"], "attempt_id": attempt["attempt_id"],
            "execution_plan_hash": execution["plan_hash"], "preregistration_root_hash": execution["preregistration_root_hash"],
        }
        for key, expected in exact.items():
            if measured.get(key) != expected:
                blockers.append(f"CROSS_LINEAGE_{key.upper()}")
        if trace_artifact is not None and measured.get("trace_blob_hash") != trace_artifact["blob_hash"]:
            blockers.append("TRACE_IDENTITY_MISMATCH")

        try:
            prereg = self.artifacts.current(str(execution["preregistration_id"]), "Preregistration")
            draft = prereg.payload["draft"]
            question, metrics, endpoints = draft["scientific_question"], draft["metrics"], draft["endpoints"]
        except Exception:
            blockers.append("PREREGISTRATION_PAYLOAD_INVALID"); return None
        if prereg.scientific_hash != execution["preregistration_root_hash"] or not prereg.sealed:
            blockers.append("PREREGISTRATION_NOT_EXACT_LOCKED")
        if measured["hypothesis_id"] != question["hypothesis_id"] or measured["hypothesis_revision"] != question["hypothesis_hash"]:
            blockers.append("HYPOTHESIS_REVISION_MISMATCH")
        metric = next((item for item in metrics if item["metric_id"] == measured["metric_id"]), None)
        declared_endpoints = [item for item in endpoints if item["metric_id"] == measured["metric_id"]]
        if metric is None or not declared_endpoints:
            blockers.append("METRIC_NOT_PREREGISTERED_ENDPOINT")
        else:
            if measured["metric_version"] != metric["definition_version"]:
                blockers.append("METRIC_VERSION_MISMATCH")
            if metric["implementation_status"] != "IMPLEMENTED":
                blockers.append("METRIC_IMPLEMENTATION_UNAVAILABLE")
            if metric["validation_status"] != "VALIDATED_FOR_CONSTRUCT":
                blockers.append("METRIC_NOT_VALIDATED_FOR_CONSTRUCT")
            endpoint = declared_endpoints[0]
            if measured["analysis_rule"] != endpoint["decision_rule"]:
                blockers.append("ANALYSIS_RULE_NOT_PREREGISTERED")
        if measured["epistemic_classification"] not in _RELATIONS:
            blockers.append("EPISTEMIC_CLASSIFICATION_INVALID")
        if not all(isinstance(measured[key], (int, float)) and not isinstance(measured[key], bool) for key in ("value", "numerator", "denominator", "excluded_count", "missing_count")):
            blockers.append("METRIC_VALUE_TYPE_INVALID")
        elif measured["denominator"] <= 0 or measured["numerator"] < 0 or measured["excluded_count"] < 0 or measured["missing_count"] < 0:
            blockers.append("METRIC_DENOMINATOR_INVALID")

        deviations = con.execute("SELECT payload_json FROM scientific_execution_deviations WHERE execution_id=?", (execution["execution_id"],)).fetchall()
        critical = any(bool(json.loads(row["payload_json"]).get("critical", True)) for row in deviations)
        relation = measured["epistemic_classification"]
        qualification = "NO_DEVIATION"
        if critical:
            relation, qualification = "UNRESOLVED", "CRITICAL_DEVIATION_NO_UNQUALIFIED_UPDATE"
            warnings.append("CRITICAL_DEVIATION_QUALIFIED")
        return {
            "schema_version": ENVELOPE_SCHEMA, "result_schema_version": RESULT_SCHEMA,
            "execution_id": execution["execution_id"], "attempt_id": attempt["attempt_id"], "trial_intent_id": attempt["trial_intent_id"],
            "preregistration_id": execution["preregistration_id"], "preregistration_root_hash": execution["preregistration_root_hash"],
            "protocol_hash": execution["preregistration_root_hash"], "execution_plan_hash": execution["plan_hash"],
            "hypothesis_id": measured["hypothesis_id"], "hypothesis_revision": measured["hypothesis_revision"],
            "agent_id": identity["agent_id"], "scenario_id": json.loads(execution["plan_json"])["protocol"]["scenario_id"],
            "world_seed": identity["world_seed"], "agent_seed": identity["agent_seed"], "metric_id": measured["metric_id"],
            "metric_version": measured["metric_version"], "value": measured["value"], "numerator": measured["numerator"],
            "denominator": measured["denominator"], "excluded_count": measured["excluded_count"], "missing_count": measured["missing_count"],
            "missingness_policy": metric["missing_data_behavior"] if metric else "UNKNOWN", "analysis_rule": measured["analysis_rule"],
            "epistemic_classification": relation, "qualification": qualification,
            "metric_artifact_descriptor_hash": metric_artifact["descriptor_hash"], "trace_artifact_descriptor_hash": trace_artifact["descriptor_hash"] if trace_artifact else "MISSING",
            "trace_blob_hash": measured["trace_blob_hash"], "deviation_count": len(deviations),
            "scope": measured["scope"], "scientific_result": True,
        }
