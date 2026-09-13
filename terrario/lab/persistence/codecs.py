"""Lossless codecs between immutable Lab contracts and stored JSON payloads."""

from __future__ import annotations

from typing import Any, Mapping

from terrario.lab.experiment_composer import (
    ControlCondition,
    DraftProvenance,
    DraftState,
    ExperimentDraft,
)
from terrario.lab.world_authoring import WorldDraft
from terrario.lab.world_contracts import WorldProvenance
from terrario.lab.preregistration.domain import (
    AnalysisPlan, CausalDesignCommitment, CausalMode, ControlCommitment,
    EndpointCommitment, EndpointRole, EnvironmentRequirement, ExclusionPolicy,
    ExclusionRule, FailurePolicy, FailureRule, MetricCommitment,
    ObservedEnvironment, ObserverChannelCommitment, ObserverCommitment,
    Partition, PreregistrationDraft, ProtocolSnapshot, RandomizationPlan,
    ReplicationPlan, SeedCommitment, SeedPartition, ScientificQuestionSnapshot,
    SoftwareManifest, StoppingRule, StorageTracePolicy, StudyIntent,
)


def world_draft_from_payload(payload: Mapping[str, Any]) -> WorldDraft:
    provenance = payload["provenance"]
    return WorldDraft(
        draft_id=str(payload["draft_id"]),
        schema_version=str(payload["schema_version"]),
        purpose=str(payload["purpose"]),
        topology=str(payload["topology"]),
        dimensions=tuple(int(value) for value in payload["dimensions"]),
        entities=tuple(dict(value) for value in payload["entities"]),
        object_distributions=tuple(dict(value) for value in payload["object_distributions"]),
        initial_conditions=dict(payload["initial_conditions"]),
        deterministic_rules=tuple(dict(value) for value in payload["deterministic_rules"]),
        stochastic_rules=tuple(dict(value) for value in payload["stochastic_rules"]),
        observation_sources=tuple(str(value) for value in payload["observation_sources"]),
        action_availability=tuple(str(value) for value in payload["action_availability"]),
        termination_conditions=tuple(str(value) for value in payload["termination_conditions"]),
        intervention_targets=tuple(str(value) for value in payload["intervention_targets"]),
        scheduled_events=tuple(dict(value) for value in payload["scheduled_events"]),
        resource_structure=dict(payload["resource_structure"]),
        seed_semantics=str(payload["seed_semantics"]),
        provenance=WorldProvenance(
            creator=str(provenance["creator"]),
            reason=str(provenance["reason"]),
            created_at=str(provenance["created_at"]),
            source=provenance.get("source"),
            parent_id=provenance.get("parent_id"),
            parent_hash=provenance.get("parent_hash"),
            delta=dict(provenance.get("delta") or {}),
        ),
    )


def experiment_draft_from_payload(payload: Mapping[str, Any]) -> ExperimentDraft:
    provenance = payload["provenance"]
    controls = tuple(
        ControlCondition(
            control_id=str(value["control_id"]),
            control_type=str(value["control_type"]),
            agent_id=str(value["agent_id"]),
            contrast=str(value["contrast"]),
            availability=str(value.get("availability", "AVAILABLE")),
        )
        for value in payload["controls"]
    )
    return ExperimentDraft(
        draft_id=str(payload["draft_id"]), schema_version=str(payload["schema_version"]),
        state=DraftState(payload["state"]), scenario_id=str(payload["scenario_id"]),
        scenario_hash=str(payload["scenario_hash"]), variant_ids=tuple(str(value) for value in payload["variant_ids"]),
        difficulty_fingerprint=str(payload["difficulty_fingerprint"]), agent_ids=tuple(str(value) for value in payload["agent_ids"]),
        controls=controls, metric_ids=tuple(str(value) for value in payload["metric_ids"]),
        observer_profile=str(payload["observer_profile"]), observer_channels=tuple(str(value) for value in payload["observer_channels"]),
        world_seeds=tuple(int(value) for value in payload["world_seeds"]), agent_seeds=tuple(int(value) for value in payload["agent_seeds"]),
        repetitions=int(payload["repetitions"]), step_limit=int(payload["step_limit"]), device_requirement=str(payload["device_requirement"]),
        required_ground_truth=tuple(str(value) for value in payload["required_ground_truth"]),
        available_ground_truth=tuple(str(value) for value in payload["available_ground_truth"]),
        available_signals=tuple(str(value) for value in payload["available_signals"]), manipulation_check=payload.get("manipulation_check"),
        transfer_phase=dict(payload["transfer_phase"]) if payload.get("transfer_phase") is not None else None,
        provenance=DraftProvenance(creator=str(provenance["creator"]), reason=str(provenance["reason"]),
            source_artifact=str(provenance["source_artifact"]), source_review_state=str(provenance["source_review_state"]),
            parent_id=provenance.get("parent_id"), parent_hash=provenance.get("parent_hash"),
            changed_fields=tuple(str(value) for value in provenance.get("changed_fields", ())),
            created_at=str(provenance.get("created_at", "RUNTIME"))),
        ui_preferences=dict(payload.get("ui_preferences") or {}),
    )


def preregistration_draft_from_payload(payload: Mapping[str, Any]) -> PreregistrationDraft:
    """Reconstruct a preregistration without silently filling scientific fields."""
    required = {field.name for field in PreregistrationDraft.__dataclass_fields__.values()}
    unknown = set(payload) - required
    missing = (required - {"ui_preferences", "schema_version"}) - set(payload)
    if unknown or missing:
        raise ValueError(f"invalid preregistration fields; unknown={sorted(unknown)}, missing={sorted(missing)}")
    q, causal, protocol = payload["scientific_question"], payload["causal_design"], payload["protocol"]
    observer, seeds = payload["observer"], payload["seeds"]
    return PreregistrationDraft(
        preregistration_id=str(payload["preregistration_id"]),
        study_intent=StudyIntent(payload["study_intent"]),
        scientific_question=ScientificQuestionSnapshot(
            **{**q, "rival_hypotheses": tuple(q["rival_hypotheses"]),
               "falsification_criteria": tuple(q["falsification_criteria"]),
               "interpretation_boundaries": tuple(q.get("interpretation_boundaries", ()))},
        ),
        causal_design=CausalDesignCommitment(
            **{**causal, "mode": CausalMode(causal["mode"]),
               "identification_assumptions": tuple(causal.get("identification_assumptions", ())),
               "known_confounders": tuple(causal.get("known_confounders", ())),
               "rival_predictions": tuple(causal.get("rival_predictions", ()))},
        ),
        protocol=ProtocolSnapshot(
            **{**protocol, "variant_ids": tuple(protocol["variant_ids"]),
               "agent_ids": tuple(protocol["agent_ids"]),
               "agent_identity_hashes": dict(protocol["agent_identity_hashes"]),
               "controls": tuple(ControlCommitment(**x) for x in protocol["controls"])},
        ),
        metrics=tuple(MetricCommitment(
            **{**x, "required_signals": tuple(x["required_signals"]),
               "applicable_population": tuple(x["applicable_population"]),
               "limitations": tuple(x["limitations"])}
        ) for x in payload["metrics"]),
        endpoints=tuple(EndpointCommitment(**{**x, "role": EndpointRole(x["role"])}) for x in payload["endpoints"]),
        observer=ObserverCommitment(
            **{**observer,
               "channels": tuple(ObserverChannelCommitment(**x) for x in observer["channels"]),
               "forensic_windows": tuple(observer.get("forensic_windows", ()))},
        ),
        seeds=SeedCommitment(
            **{**seeds, "world_seeds": tuple(seeds["world_seeds"]),
               "agent_seeds": tuple(seeds["agent_seeds"]),
               "randomization_seeds": tuple(seeds["randomization_seeds"]),
               "replacement_seeds": tuple(seeds["replacement_seeds"])},
        ),
        partitions=tuple(SeedPartition(**{**x, "partition": Partition(x["partition"]), "seeds": tuple(x["seeds"])}) for x in payload["partitions"]),
        randomization=RandomizationPlan(**{**payload["randomization"],
            "blocks": tuple(payload["randomization"]["blocks"]), "strata": tuple(payload["randomization"]["strata"]),
            "constraints": tuple(payload["randomization"]["constraints"]),
            "materialized_order": tuple(payload["randomization"]["materialized_order"])}),
        replication=ReplicationPlan(**{**payload["replication"],
            "independent_seeds": tuple(payload["replication"]["independent_seeds"]),
            "replication_groups": tuple(payload["replication"]["replication_groups"]),
            "conditions": tuple(payload["replication"]["conditions"]),
            "expected_invariances": tuple(payload["replication"]["expected_invariances"])}),
        analysis=AnalysisPlan(**{**payload["analysis"], "comparisons": tuple(payload["analysis"]["comparisons"]),
            "transformations": tuple(payload["analysis"]["transformations"]),
            "grouping_variables": tuple(payload["analysis"]["grouping_variables"]),
            "sensitivity_analyses": tuple(payload["analysis"]["sensitivity_analyses"])}),
        stopping=StoppingRule(**payload["stopping"]),
        exclusions=ExclusionPolicy(tuple(ExclusionRule(**x) for x in payload["exclusions"]["rules"]), payload["exclusions"]["post_hoc_disposition"]),
        failures=FailurePolicy(tuple(FailureRule(**x) for x in payload["failures"]["rules"])),
        storage=StorageTracePolicy(**{**payload["storage"],
            **{k: tuple(payload["storage"][k]) for k in ("required_artifacts", "required_traces", "checkpoints", "forensic_windows", "summary_outputs")}}),
        environment_requirement=EnvironmentRequirement(**payload["environment_requirement"]),
        observed_environment=ObservedEnvironment(**payload["observed_environment"]),
        software=SoftwareManifest(**payload["software"]),
        ui_preferences=dict(payload.get("ui_preferences") or {}),
        schema_version=str(payload.get("schema_version", "terrario.lab.preregistration/v1")),
    )
