"""Review-gated conversion of theory hyperedges into experiment previews."""

from __future__ import annotations

from dataclasses import replace
from typing import TYPE_CHECKING, Mapping

from terrario.lab.persistence.canonical import content_hash
from terrario.lab.theory.models import (
    ExperimentPreview, HyperedgeCandidateRecord, HypothesisDraft, HypothesisPremise,
)

if TYPE_CHECKING:
    from terrario.lab.hypergraph.theory_operational import TheoryOperationalHyperedge
    from terrario.lab.world_contracts import ScenarioDefinition


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


class OperationalHypothesisCompiler:
    """Derive review-gated, falsifiable hypotheses from composed operational edges."""

    DERIVATION_RULE = "ROLE_REFINEMENT_ABLATION_PREDICTION@v1"
    REQUIRED_COMPOSITION_RULE = "ACTION_PRODUCING_AGENT_REFINEMENT@v1"

    def compile(
        self,
        hyperedge: "TheoryOperationalHyperedge",
        edges_by_semantic_id: Mapping[str, "TheoryOperationalHyperedge"],
    ) -> HypothesisDraft:
        if hyperedge.origin != "DERIVED" or hyperedge.relation_type != "SEMANTIC_ROLE_COMPOSITION":
            raise ValueError("only a derived semantic composition can produce an operational hypothesis")
        if hyperedge.epistemic_status.value != "TESTABLE_CONJUNCTION":
            raise ValueError("operational hypothesis cannot promote epistemic status")
        if hyperedge.composition_rule != self.REQUIRED_COMPOSITION_RULE:
            raise ValueError("derived hypothesis requires the declared compatible composition rule")
        if hyperedge.corroboration_status != "STRUCTURAL_COMPOSITION_NOT_CORROBORATION":
            raise ValueError("derived hypothesis cannot treat structural composition as corroboration")
        parents = tuple(edges_by_semantic_id.get(item) for item in hyperedge.parent_semantic_ids)
        if len(parents) != 2 or any(item is None for item in parents):
            raise ValueError("derived hypothesis requires two resolvable immediate parents")
        from terrario.lab.hypergraph.theory_operational import provenance_forward
        leaves = provenance_forward(hyperedge, edges_by_semantic_id)
        parent_for_candidate = {item.candidate_id: item.semantic_id for item in parents if item is not None}

        required = (
            ("agent", "agent"), ("actor", "action_sequence_proposer"),
            ("world model", "future_state_predictor"), ("cost", "intrinsic_cost_and_critic_evaluator"),
        )
        selected = []
        for requirement in required:
            binding = next((item for item in leaves if (item.participant, item.role) == requirement), None)
            if binding is None or binding.candidate_id not in parent_for_candidate:
                raise ValueError("derived hypothesis lacks a required source-backed role premise")
            selected.append(HypothesisPremise(
                source_hyperedge_id=parent_for_candidate[binding.candidate_id],
                participant=binding.participant, role=binding.role, claim_id=binding.claim_id,
                source_id=binding.source_record_id, source_locator=binding.source_locator,
            ))
        premise_ids = tuple(item.claim_id for item in selected)
        prediction = (
            "Under the declared autonomous-agent architecture, ablating the actor's action-sequence "
            "proposal role while preserving the world-model and cost roles removes the composed "
            "planned-action evaluation pathway."
        )
        identifier = "DRAFT-DERIVED-" + content_hash({
            "hyperedge": hyperedge.semantic_id, "rule": self.DERIVATION_RULE,
            "premises": premise_ids, "prediction": prediction,
        })[:16]
        return HypothesisDraft(
            id=identifier, source_hyperedge_id=hyperedge.semantic_id,
            components=tuple(sorted({item.participant for item in leaves})),
            predicted_outcome="planned-action evaluation pathway availability",
            source_provenance=hyperedge.provenance,
            confounders=(
                "actor ablation may alter capacity or optimization budget",
                "an alternative action-producing module may substitute for the actor role",
            ),
            discriminating_test="actor-role ablation with world-model and cost roles preserved",
            coverage_status="SOURCE_BACKED_COMPOSITION",
            theory_warning="STRUCTURAL_DERIVATION_NOT_CORROBORATION",
            premises=tuple(selected), composition_path=tuple(hyperedge.parent_semantic_ids),
            derivation_rule=self.DERIVATION_RULE,
            assumptions=(
                "the actor role can be ablated without changing the declared world-model and cost roles",
                "planned-action evaluation is observable under the selected protocol",
            ),
            known_contradictions=("UNRESOLVED: selected premises carry no resolved contradiction audit",),
            novelty_evidence=(
                "Derived by joining TI-0071 formal agent action role with TI-0077 architectural actor role; "
                "not recovered verbatim from either source."
            ),
            testability="REVIEW_REQUIRED_TESTABLE",
            target_domain="autonomous planning/action architecture",
            required_capabilities=("actor-role ablation", "planned-action observable", "matched role-preservation control"),
            prediction=prediction,
        )


class OperationalExperimentCompiler:
    """CL-4 mapping from a review-gated operational hypothesis to a non-executing draft."""

    DERIVATION_RULE = "HYPOTHESIS_TO_EXPERIMENT_FIELD_MAPPING@v1"
    METRIC_ID = "planned-action-evaluation-pathway"

    def compile(
        self,
        hypothesis: HypothesisDraft,
        *,
        scenario: "ScenarioDefinition",
        difficulty_fingerprint: str,
        agent_id: str = "A4",
        world_seeds: tuple[int, ...] = (11, 12),
        agent_seeds: tuple[int, ...] = (21, 22),
    ):
        """Return an inspectable draft; capability/metric gaps remain explicit blockers."""
        from terrario.lab.experiment_composer import (
            ControlCondition, DraftProvenance, DraftState, ExperimentDraft,
            HypothesisExperimentCondition, HypothesisExperimentMapping,
        )
        from terrario.lab.metrics_observer import ObserverRegistry

        required = (hypothesis.prediction, hypothesis.derivation_rule, hypothesis.discriminating_test,
                    hypothesis.target_domain, hypothesis.premises)
        if not all(required) or hypothesis.epistemic_status != "REVIEW_REQUIRED":
            raise ValueError("only a complete review-required operational hypothesis can produce an experiment draft")
        if scenario.scenario_id != "D2":
            raise ValueError("this operational derivation is currently defined only for D2")
        if "actor-role ablation" not in hypothesis.required_capabilities:
            raise ValueError("hypothesis lacks the required actor-role ablation capability")

        source_claim_ids = tuple(sorted(item.claim_id for item in hypothesis.premises))
        mapping = HypothesisExperimentMapping(
            schema_version="terrario.lab.hypothesis-experiment-mapping/v1",
            hypothesis_semantic_id=hypothesis.semantic_id,
            prediction=hypothesis.prediction,
            independent_variable="availability of the actor action-sequence proposal role (A4 use_planner true versus false)",
            dependent_variable="planned-action evaluation pathway availability",
            conditions=(
                HypothesisExperimentCondition(
                    "actor-role-preserved", "A4 use_planner=true with world model and cost pathway preserved",
                    "planner proposal trace is available", "baseline required to establish the declared pathway",
                    {"use_planner": True, "use_world_model": True}),
                HypothesisExperimentCondition(
                    "actor-role-ablated", "A4 use_planner=false while use_world_model remains true",
                    "planner proposal trace is absent while world-model prediction remains observable",
                    "isolates the source-backed actor role without disabling the world model",
                    {"use_planner": False, "use_world_model": True}),
            ),
            agent_capability="A4 configuration exposes use_planner and use_world_model as separately declared switches",
            scenario_rationale="D2 supplies a seeded, partially observable property environment; it is an explicit target, not evidence that the cognitive construct is already validated",
            metric_id=self.METRIC_ID,
            metric_rationale="planner proposal traces are the closest declared observable for the derived planned-action pathway; energy is explicitly not substituted",
            failure_criterion=(
                "The actor-role-ablated condition retains the planner-proposal trace, or the matched control no longer preserves the declared world-model role."
            ),
            derivation_rule=self.DERIVATION_RULE,
            source_claim_ids=source_claim_ids,
            field_rationales={
                "independent_variable": "derived prediction specifically targets the actor action-sequence proposal role",
                "dependent_variable": "the prediction concerns pathway availability, not aggregate reward",
                "control": "world-model preservation separates actor-role ablation from wholesale architecture removal",
                "scenario": "D2 has deterministic seeds and an explicit observation contract for a future controlled protocol",
                "metric": "no energy proxy is scientifically equivalent to a planner proposal trace",
                "failure_criterion": "a retained pathway under ablation or broken preservation control falsifies the operational contrast",
            },
        )
        profile = ObserverRegistry().profile("STANDARD")
        identifier = "EXPERIMENT-DRAFT-" + content_hash({
            "hypothesis": hypothesis.semantic_id, "scenario": scenario.content_hash,
            "mapping": mapping, "agent": agent_id, "world_seeds": world_seeds, "agent_seeds": agent_seeds,
        })[:16]
        return ExperimentDraft(
            draft_id=identifier, schema_version="terrario.lab.experiment-draft/v1", state=DraftState.REVIEW_BLOCKED,
            scenario_id=scenario.scenario_id, scenario_hash=scenario.content_hash,
            variant_ids=("D2-actor-role-preserved", "D2-actor-role-ablated"),
            difficulty_fingerprint=difficulty_fingerprint, agent_ids=(agent_id,),
            controls=(ControlCondition(
                "actor-role-preserved", "ROLE_PRESERVATION_CONTROL", agent_id,
                "A4 use_planner=true versus A4 use_planner=false, with use_world_model=true in both conditions",
            ),),
            metric_ids=(self.METRIC_ID,), observer_profile="STANDARD", observer_channels=profile.channels,
            world_seeds=world_seeds, agent_seeds=agent_seeds, repetitions=1, step_limit=100,
            device_requirement="cpu", required_ground_truth=scenario.required_ground_truth,
            available_ground_truth=scenario.required_ground_truth, available_signals=profile.channels,
            manipulation_check="verify use_planner is false only in actor-role-ablated and use_world_model remains true in both conditions",
            transfer_phase=None,
            provenance=DraftProvenance(
                "OperationalExperimentCompiler", "CL-4 derivation from operational hypothesis",
                hypothesis.semantic_id, hypothesis.epistemic_status,
            ),
            hypothesis_mapping=mapping,
        )
