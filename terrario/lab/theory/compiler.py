"""Review-gated conversion of theory hyperedges into experiment previews."""

from __future__ import annotations

from dataclasses import replace

from terrario.lab.theory.models import ExperimentPreview, HyperedgeCandidateRecord, HypothesisDraft


class HypothesisCompiler:
    def compile(self, hyperedge: HyperedgeCandidateRecord, coverage: str = "UNRESOLVED") -> HypothesisDraft:
        warning = "THEORY_BASE_WEAK" if coverage.upper() in {"WEAK", "ABSENT"} else None
        return HypothesisDraft(
            id=f"DRAFT-{hyperedge.id}", source_hyperedge_id=hyperedge.id,
            components=hyperedge.components, predicted_outcome=hyperedge.predicted_outcome,
            source_provenance=hyperedge.provenance, confounders=hyperedge.confounders,
            discriminating_test=hyperedge.discriminating_test, coverage_status=coverage,
            theory_warning=warning,
        )

    def activate(self, draft: HypothesisDraft, approved: bool = False):
        if not approved or draft.epistemic_status != "REVIEW_REQUIRED":
            raise PermissionError("human review is required before HypothesisSpec activation")
        return replace(draft, epistemic_status="UNTESTED_HYPOTHESIS")

    def preview(self, draft: HypothesisDraft) -> ExperimentPreview:
        return ExperimentPreview(
            hypothesis_draft_id=draft.id, full_condition=draft.components,
            ablations=tuple(f"without {component}" for component in draft.components),
            controls=("matched baseline",), expected_observations=(draft.predicted_outcome,),
            falsification_conditions=(f"no discriminating effect: {draft.discriminating_test}",),
            likely_confounders=draft.confounders,
        )
