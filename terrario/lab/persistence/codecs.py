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
        draft_id=str(payload["draft_id"]),
        schema_version=str(payload["schema_version"]),
        state=DraftState(payload["state"]),
        scenario_id=str(payload["scenario_id"]),
        scenario_hash=str(payload["scenario_hash"]),
        variant_ids=tuple(str(value) for value in payload["variant_ids"]),
        difficulty_fingerprint=str(payload["difficulty_fingerprint"]),
        agent_ids=tuple(str(value) for value in payload["agent_ids"]),
        controls=controls,
        metric_ids=tuple(str(value) for value in payload["metric_ids"]),
        observer_profile=str(payload["observer_profile"]),
        observer_channels=tuple(str(value) for value in payload["observer_channels"]),
        world_seeds=tuple(int(value) for value in payload["world_seeds"]),
        agent_seeds=tuple(int(value) for value in payload["agent_seeds"]),
        repetitions=int(payload["repetitions"]),
        step_limit=int(payload["step_limit"]),
        device_requirement=str(payload["device_requirement"]),
        required_ground_truth=tuple(str(value) for value in payload["required_ground_truth"]),
        available_ground_truth=tuple(str(value) for value in payload["available_ground_truth"]),
        available_signals=tuple(str(value) for value in payload["available_signals"]),
        manipulation_check=payload.get("manipulation_check"),
        transfer_phase=dict(payload["transfer_phase"]) if payload.get("transfer_phase") is not None else None,
        provenance=DraftProvenance(
            creator=str(provenance["creator"]),
            reason=str(provenance["reason"]),
            source_artifact=str(provenance["source_artifact"]),
            source_review_state=str(provenance["source_review_state"]),
            parent_id=provenance.get("parent_id"),
            parent_hash=provenance.get("parent_hash"),
            changed_fields=tuple(str(value) for value in provenance.get("changed_fields", ())),
            created_at=str(provenance.get("created_at", "RUNTIME")),
        ),
        ui_preferences=dict(payload.get("ui_preferences") or {}),
    )
