"""Canonical, non-evidential visual timeline derived from the D2 instrument.

This fixture exists only to validate the D2 Scientific Studio rendering path.
It is not an agent run, scientific result, or EvidenceGraph input.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Mapping

from terrario.lab.d2_operational import D2AgentInternalState, D2BindingProtocol
from terrario.lab.persistence.canonical import content_hash


FIXTURE_SCHEMA = "terrario.lab.d2-visual-validation-fixture/v1"
EPISTEMIC_SCOPE = "INSTRUMENT_SELF_AUDIT_NOT_AGENT_EVIDENCE"


@dataclass(frozen=True)
class D2VisualFixtureFrame:
    frame_id: str
    sequence: int
    tick: int
    phase: str
    source_condition: str
    visible_object_ids: tuple[int, ...]
    lifecycle: tuple[tuple[int, str], ...]
    world_truth: tuple[dict, ...]
    observer_errors: tuple[str, ...]
    observer_details: tuple[str, ...]
    expected_tracks: tuple[tuple[str, int], ...]

    def payload(self) -> dict:
        return {
            "frame_id": self.frame_id, "frame_sequence": self.sequence, "tick": self.tick,
            "projection_tick": self.tick, "evaluation_tick": self.tick,
            "phase": self.phase, "source_condition": self.source_condition,
            "visible_object_ids": list(self.visible_object_ids),
            "lifecycle": {str(key): value for key, value in self.lifecycle},
            "world_truth": {"objects": list(self.world_truth), "tick": self.tick},
            "agent_observation": {"availability": "NOT_APPLICABLE", "reason": "NO_AGENT_EXECUTED"},
            "cognitive_state": {"availability": "NOT_APPLICABLE", "reason": "NO_AGENT_EXECUTED"},
            "observer_view": {
                "expected_tracks": [list(item) for item in self.expected_tracks],
                "errors": list(self.observer_errors), "details": list(self.observer_details),
                "scope": EPISTEMIC_SCOPE,
            },
        }


@dataclass(frozen=True)
class D2VisualValidationFixture:
    fixture_id: str
    protocol_version: str
    protocol_id: str
    semantic_hash: str
    frames: tuple[D2VisualFixtureFrame, ...]

    def payload(self) -> dict:
        return {
            "schema_version": FIXTURE_SCHEMA, "fixture_id": self.fixture_id,
            "fixture_version": "v1", "protocol_version": self.protocol_version,
            "protocol_id": self.protocol_id, "semantic_hash": self.semantic_hash,
            "epistemic_scope": EPISTEMIC_SCOPE, "agent_executed": False,
            "evidence_graph_writes": 0, "scientific_result_writes": 0,
            "frames": [item.payload() for item in self.frames],
        }


def _records(frame, tick: int) -> tuple[dict, ...]:
    return tuple({"object_id": item.object_id, "position": list(item.position),
                  "property_signature": list(item.property_signature), "movable": item.movable}
                 for item in frame.world_truth.objects)


def build_d2_visual_validation_fixture(scenario_path: str | Path) -> D2VisualValidationFixture:
    """Build the fixed validation sequence from authoritative D2 transformations."""
    protocol = D2BindingProtocol(scenario_path)
    specifications = (
        ("INITIAL", "baseline", {0: "created", 1: "created", 2: "created"}, None),
        ("MOVEMENT", "movement", {0: "moving"}, None),
        ("PROXIMITY", "spatial_proximity", {0: "visible", 1: "moving"}, None),
        ("OCCLUSION_BEGIN", "occlusion", {0: "occluded"}, (0,)),
        ("OCCLUDED", "occlusion", {0: "occluded"}, (0,)),
        ("REAPPEAR", "movement", {0: "visible_again"}, None),
        ("PROPERTY_CHANGE", "temporal_property_change", {0: "changed"}, None),
        ("SIMILAR_PROPERTIES", "similar_properties", {0: "visible", 1: "visible"}, None),
        ("DISTRACTOR_PRESENT", "distractor", {99: "created"}, None),
        ("BINDING_PRESSURE", "spatial_proximity", {0: "visible", 1: "visible"}, None),
        ("BINDING_ERROR", "baseline", {0: "visible", 1: "visible"}, "swap"),
        ("TERMINAL", "baseline", {0: "terminal", 1: "terminal", 2: "terminal"}, None),
    )
    frames: list[D2VisualFixtureFrame] = []
    for sequence, (phase, condition, lifecycle_changes, occluded) in enumerate(specifications):
        reports = protocol.correct_reports(condition)
        if occluded == "swap":
            left, right = reports.reports
            reports = D2AgentInternalState((
                replace(left, position=right.position, property_signature=right.property_signature),
                replace(right, position=left.position, property_signature=left.property_signature),
            ))
        frame = protocol.frame(condition, reports)
        objects = _records(frame, sequence)
        object_ids = tuple(item["object_id"] for item in objects)
        hidden = (0,) if occluded == (0,) else ()
        lifecycle = tuple((object_id, lifecycle_changes.get(object_id, "visible")) for object_id in object_ids)
        semantic = {"sequence": sequence, "phase": phase, "condition": condition,
                    "objects": objects, "hidden": hidden, "lifecycle": lifecycle,
                    "errors": frame.observer_view.errors, "tracks": frame.observer_view.expected_tracks}
        frames.append(D2VisualFixtureFrame(
            frame_id="D2VF-" + content_hash(semantic)[:16], sequence=sequence, tick=sequence,
            phase=phase, source_condition=condition,
            visible_object_ids=tuple(item for item in object_ids if item not in hidden), lifecycle=lifecycle,
            world_truth=objects, observer_errors=frame.observer_view.errors,
            observer_details=frame.observer_view.error_details,
            expected_tracks=frame.observer_view.expected_tracks,
        ))
    semantic_payload = {"schema": FIXTURE_SCHEMA, "protocol": protocol.semantic_id,
                        "frames": [item.payload() for item in frames]}
    semantic_hash = content_hash(semantic_payload)
    return D2VisualValidationFixture(
        fixture_id="D2-VISUAL-FIXTURE-" + semantic_hash[:16], protocol_version="terrario.lab.d2-binding-protocol/v2",
        protocol_id=protocol.semantic_id, semantic_hash=semantic_hash, frames=tuple(frames))


def validate_visual_fixture_payload(payload: Mapping[str, object]) -> None:
    """Fail closed before a canonical fixture can be served to the renderer."""
    if payload.get("schema_version") != FIXTURE_SCHEMA:
        raise ValueError("D2_VISUAL_FIXTURE_SCHEMA_MISMATCH")
    if payload.get("epistemic_scope") != EPISTEMIC_SCOPE or payload.get("agent_executed") is not False:
        raise ValueError("D2_VISUAL_FIXTURE_SCOPE_VIOLATION")
    frames = payload.get("frames")
    if not isinstance(frames, list) or not frames:
        raise ValueError("D2_VISUAL_FIXTURE_FRAMES_MISSING")
    for expected_sequence, frame in enumerate(frames):
        if not isinstance(frame, Mapping) or frame.get("frame_sequence") != expected_sequence:
            raise ValueError("D2_VISUAL_FIXTURE_SEQUENCE_INVALID")
        if frame.get("tick") != frame.get("projection_tick") or frame.get("tick") != frame.get("evaluation_tick"):
            raise ValueError("D2_VISUAL_FIXTURE_TICK_MISMATCH")
        truth = frame.get("world_truth")
        if not isinstance(truth, Mapping) or not isinstance(truth.get("objects"), list):
            raise ValueError("D2_VISUAL_FIXTURE_TRUTH_MISSING")
        ids = {item.get("object_id") for item in truth["objects"] if isinstance(item, Mapping)}
        visible = set(frame.get("visible_object_ids", ()))
        if not visible <= ids:
            raise ValueError("D2_VISUAL_FIXTURE_UNKNOWN_VISIBLE_OBJECT")
        if frame.get("agent_observation", {}).get("availability") != "NOT_APPLICABLE":
            raise ValueError("D2_VISUAL_FIXTURE_AGENT_VIEW_VIOLATION")
        if frame.get("cognitive_state", {}).get("availability") != "NOT_APPLICABLE":
            raise ValueError("D2_VISUAL_FIXTURE_COGNITIVE_VIEW_VIOLATION")
