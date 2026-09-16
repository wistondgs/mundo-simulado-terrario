"""Non-destructive reconciliation for pre-normalization hypothesis artifacts."""
from __future__ import annotations

from typing import Any, Mapping

from terrario.lab.persistence.canonical import canonical_json, content_hash


class HypothesisReconciliationError(RuntimeError):
    code = "HYPOTHESIS_RECONCILIATION_ERROR"


class HypothesisReconciler:
    """Marks a semantically equivalent historical hypothesis as superseded.

    It deliberately operates only on review-required draft artifacts and refuses
    to touch an artifact that has already contributed empirical evidence.
    """

    def __init__(self, artifacts):
        self.artifacts = artifacts

    def reconcile(self, old_artifact_id: str, canonical_artifact_id: str, actor_id: str,
                  reason: str) -> Mapping[str, Any]:
        if old_artifact_id == canonical_artifact_id:
            raise HypothesisReconciliationError("SELF_SUPERSESSION_FORBIDDEN")
        old = self.artifacts.current(old_artifact_id, "OperationalHypothesisDraft")
        canonical = self.artifacts.current(canonical_artifact_id, "OperationalHypothesisDraft")
        self._same_scientific_question(old.payload, canonical.payload)
        with self.artifacts.transaction() as con:
            used = con.execute("SELECT 1 FROM scientific_results WHERE hypothesis_id=? LIMIT 1", (old_artifact_id,)).fetchone()
            if used:
                raise HypothesisReconciliationError("HISTORICAL_HYPOTHESIS_ALREADY_HAS_EMPIRICAL_EVIDENCE")
            old_state = self._state(con, old.version_id)
            canonical_state = self._state(con, canonical.version_id)
            if canonical_state != "REVIEW_REQUIRED":
                raise HypothesisReconciliationError("CANONICAL_HYPOTHESIS_NOT_REVIEW_REQUIRED")
            existing = con.execute("""SELECT link_id FROM artifact_links WHERE source_version_id=? AND target_version_id=?
                AND relation='SUPERSEDED_BY'""", (old.version_id, canonical.version_id)).fetchone()
            if existing:
                return {"old_artifact_id": old_artifact_id, "canonical_artifact_id": canonical_artifact_id,
                        "link_id": existing["link_id"], "deduplicated": True, "old_state": old_state}
            if old_state not in {"REVIEW_REQUIRED", "SUPERSEDED"}:
                raise HypothesisReconciliationError("HISTORICAL_HYPOTHESIS_STATE_NOT_RECONCILABLE")
            now = self.artifacts.now()
            if old_state != "SUPERSEDED":
                sequence = con.execute("SELECT COALESCE(MAX(sequence),0)+1 FROM artifact_state_events WHERE version_id=?", (old.version_id,)).fetchone()[0]
                self.artifacts._insert_state_event(con, old.version_id, int(sequence), old_state, "SUPERSEDED", actor_id, reason, now)
            link_id = f"hypothesis-supersession-{content_hash((old.version_id, canonical.version_id))[:24]}"
            provenance = {"schema_version": "terrario.hypothesis-reconciliation/v1", "reason": reason,
                          "old_scientific_hash": old.scientific_hash, "canonical_scientific_hash": canonical.scientific_hash,
                          "semantic_equivalence": "CLAIM_ROLE_PREDICTION"}
            con.execute("""INSERT INTO artifact_links(link_id,source_version_id,target_version_id,relation,epistemic_status,provenance_json,created_at)
                VALUES(?,?,?,?,?,?,?)""", (link_id, old.version_id, canonical.version_id, "SUPERSEDED_BY", "REVIEW_REQUIRED", canonical_json(provenance), now))
            self.artifacts._insert_audit(con, self.artifacts._identifier("correlation"), actor_id, "HYPOTHESIS_RECONCILED",
                "OperationalHypothesisDraft", old_artifact_id, {"canonical_artifact_id": canonical_artifact_id, "link_id": link_id}, now)
        return {"old_artifact_id": old_artifact_id, "canonical_artifact_id": canonical_artifact_id,
                "link_id": link_id, "deduplicated": False, "old_state": "SUPERSEDED"}

    @staticmethod
    def _state(connection, version_id: str) -> str | None:
        row = connection.execute("SELECT to_state FROM artifact_state_events WHERE version_id=? ORDER BY sequence DESC LIMIT 1", (version_id,)).fetchone()
        return str(row["to_state"]) if row else None

    @staticmethod
    def _same_scientific_question(old: Mapping[str, Any], canonical: Mapping[str, Any]) -> None:
        def question(payload):
            premises = tuple(sorted((item["claim_id"], item["participant"], item["role"]) for item in payload.get("premises", ())))
            return (payload.get("derivation_rule"), payload.get("prediction"), payload.get("epistemic_status"), premises)
        if question(old) != question(canonical):
            raise HypothesisReconciliationError("HYPOTHESES_NOT_SEMANTICALLY_EQUIVALENT")
