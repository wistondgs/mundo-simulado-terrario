"""D2 property/identity/binding protocol with strict observer boundaries.

This is an instrument for evaluating an agent-provided tracking report.  It is
not a claim that any current Terrario agent has the required cognitive state.
World truth and observer scoring are never included in the agent observation.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import numpy as np
import yaml

from terrario.experiment.controller import build_world_state
from terrario.lab.persistence.canonical import content_hash
from terrario.world.state import WorldStateManager


ERROR_PROPERTY = "PROPERTY_ERROR"
ERROR_IDENTITY = "IDENTITY_ERROR"
ERROR_IDENTITY_SWAP = "IDENTITY_SWAP_ERROR"
ERROR_BINDING = "BINDING_ERROR"
ERROR_MISSING_REPORT = "MISSING_TRACK_REPORT"
NOT_EVALUABLE = "NOT_EVALUABLE"
PROTOCOL_SCHEMA = "terrario.lab.d2-binding-protocol/v2"
EVALUATOR_VERSION = "terrario.lab.d2-binding-evaluator/v2"
MISSING_DATA_POLICY = "EXCLUDE_FROM_ERROR_DENOMINATOR_AND_RECORD_NOT_EVALUABLE"
FORBIDDEN_AGENT_OBSERVATION_FIELDS = frozenset({
    "object_id", "object_ids", "property_signature", "expected_tracks",
    "target", "truth", "world_truth", "answer_key",
})


@dataclass(frozen=True)
class D2Condition:
    condition_id: str
    pressure: str
    rationale: str


@dataclass(frozen=True)
class D2TruthObject:
    object_id: int
    position: tuple[int, int]
    property_signature: tuple[float, ...]
    movable: bool


@dataclass(frozen=True)
class D2WorldTruth:
    tick: int
    condition_id: str
    objects: tuple[D2TruthObject, ...]


@dataclass(frozen=True)
class D2AgentObservation:
    """Raw local perceptual input only; ids and properties remain absent."""

    channels: tuple
    mask: tuple
    agent_energy: float
    time_fraction: float


@dataclass(frozen=True)
class D2AgentObjectReport:
    """Adapter output from an agent internal tracker, aligned only by the observer."""

    track_id: str
    position: tuple[int, int]
    property_signature: tuple[float, ...]


@dataclass(frozen=True)
class D2AgentInternalState:
    reports: tuple[D2AgentObjectReport, ...]
    adapter_status: str = "EXTERNAL_TRACKING_ADAPTER"

    def __post_init__(self) -> None:
        tracks = tuple(item.track_id for item in self.reports)
        if not all(isinstance(track, str) and track.strip() for track in tracks):
            raise ValueError("MALFORMED_TRACK_IDENTITY")
        if len(set(tracks)) != len(tracks):
            raise ValueError("DUPLICATE_TRACK_IDENTITY")


@dataclass(frozen=True)
class D2ObserverView:
    expected_tracks: tuple[tuple[str, int], ...]
    errors: tuple[str, ...]
    error_details: tuple[str, ...]
    metrics: tuple["D2ErrorMetric", ...] = ()
    not_evaluable_tracks: tuple[str, ...] = ()
    evaluation_tick: int = -1


@dataclass(frozen=True)
class D2ErrorMetric:
    """One explicit error-rate denominator; diagnostics never become errors."""

    metric_id: str
    numerator: int
    denominator: int
    eligible_cases: int
    non_evaluable_cases: int
    missing_data_policy: str = MISSING_DATA_POLICY

    def __post_init__(self) -> None:
        if min(self.numerator, self.denominator, self.eligible_cases, self.non_evaluable_cases) < 0:
            raise ValueError("D2 metric counts must be non-negative")
        if self.numerator > self.denominator or self.denominator != self.eligible_cases:
            raise ValueError("D2 metric denominator must equal eligible cases")

    @property
    def rate(self) -> float | None:
        return self.numerator / self.denominator if self.denominator else None


@dataclass(frozen=True)
class D2ScientificFrame:
    world_truth: D2WorldTruth
    agent_observation: D2AgentObservation
    agent_internal_state: D2AgentInternalState
    observer_view: D2ObserverView
    projection_tick: int
    evaluation_tick: int


@dataclass(frozen=True)
class D2RenderedObject:
    object_id: int
    position: tuple[int, int]
    property_signature: tuple[float, ...]
    movable: bool


@dataclass(frozen=True)
class D2RenderedFrame:
    """Pure visual projection of one scientific frame; it contains no simulation state."""

    tick: int
    condition_id: str
    objects: tuple[D2RenderedObject, ...]
    visible_binding_errors: tuple[str, ...]
    source_protocol_id: str


def render_scientific_frame(frame: D2ScientificFrame, protocol_id: str) -> D2RenderedFrame:
    """Project exact tick/object facts into renderer data without inventing cognition."""
    return D2RenderedFrame(
        tick=frame.world_truth.tick, condition_id=frame.world_truth.condition_id,
        objects=tuple(D2RenderedObject(item.object_id, item.position, item.property_signature, item.movable)
                      for item in frame.world_truth.objects),
        visible_binding_errors=frame.observer_view.errors, source_protocol_id=protocol_id,
    )


def verify_render_alignment(frame: D2ScientificFrame, rendered: D2RenderedFrame) -> tuple[str, ...]:
    """Fail closed when the rendering ceases to represent the selected scientific tick."""
    errors: list[str] = []
    if frame.projection_tick != frame.world_truth.tick:
        errors.append("PROJECTION_TICK_MISMATCH")
    if frame.evaluation_tick != frame.world_truth.tick or frame.observer_view.evaluation_tick != frame.world_truth.tick:
        errors.append("EVALUATION_TICK_MISMATCH")
    if rendered.tick != frame.world_truth.tick:
        errors.append("RENDER_TICK_MISMATCH")
    if rendered.condition_id != frame.world_truth.condition_id:
        errors.append("RENDER_CONDITION_MISMATCH")
    expected = tuple(D2RenderedObject(item.object_id, item.position, item.property_signature, item.movable)
                     for item in frame.world_truth.objects)
    if rendered.objects != expected:
        errors.append("RENDER_WORLD_TRUTH_MISMATCH")
    if rendered.visible_binding_errors != frame.observer_view.errors:
        errors.append("RENDER_OBSERVER_VIEW_MISMATCH")
    return tuple(errors)


class D2BindingProtocol:
    """Deterministic D2 protocol that scores declared report-to-truth bindings."""

    CONDITIONS = (
        D2Condition("baseline", "none", "establish initial property/identity bindings"),
        D2Condition("movement", "object movement", "test identity under location change"),
        D2Condition("occlusion", "object outside local field", "test temporal persistence without truth disclosure"),
        D2Condition("temporal_property_change", "controlled channel change", "test property update without identity replacement"),
        D2Condition("similar_properties", "nearby channel signatures", "test property discrimination"),
        D2Condition("distractor", "additional similar object", "test resistance to extra candidate objects"),
        D2Condition("spatial_proximity", "tracked objects become adjacent", "test binding under spatial crowding"),
    )

    def __init__(self, scenario_path: str | Path):
        data = yaml.safe_load(Path(scenario_path).read_text(encoding="utf-8"))["scenario"]
        self._scenario = data
        if len(data.get("objects", ())) < 3:
            raise ValueError("D2 binding protocol requires at least three real D2 objects")

    @property
    def semantic_id(self) -> str:
        return "D2-PROTOCOL-" + content_hash({
            "schema": PROTOCOL_SCHEMA, "scenario": self._scenario,
            "conditions": self.CONDITIONS, "evaluator_version": EVALUATOR_VERSION,
            "missing_data_policy": MISSING_DATA_POLICY,
            "binding_rule": "CROSS_ATTRIBUTED_DISTINCT_PROPERTY_SIGNATURES",
        })[:16]

    @property
    def expected_tracks(self) -> tuple[tuple[str, int], ...]:
        return (("track-A", 0), ("track-B", 1))

    def truth_and_observation(self, condition_id: str) -> tuple[D2WorldTruth, D2AgentObservation]:
        condition = next((item for item in self.CONDITIONS if item.condition_id == condition_id), None)
        if condition is None:
            raise ValueError(f"unknown D2 protocol condition: {condition_id}")
        manager = WorldStateManager(build_world_state(self._scenario), max_duration=self._scenario["duration"])
        self._apply_condition(manager, condition_id)
        truth = D2WorldTruth(
            tick=self.CONDITIONS.index(condition), condition_id=condition_id,
            objects=tuple(sorted((D2TruthObject(
                object_id=item.object_id, position=item.pos.to_tuple(),
                property_signature=tuple(float(value) for value in item.channels), movable=item.movable,
            ) for item in manager.state.objects.values()), key=lambda item: item.object_id)),
        )
        observation = manager.get_observation(0, self._scenario["view_radius"], self._scenario["num_channels"])
        return truth, D2AgentObservation(
            channels=tuple(np.asarray(observation.channels).tolist()), mask=tuple(np.asarray(observation.mask).tolist()),
            agent_energy=float(observation.agent_energy), time_fraction=float(observation.time_fraction),
        )

    def correct_reports(self, condition_id: str) -> D2AgentInternalState:
        """Observer-side fixture builder for instrument tests; never agent input."""
        truth, _ = self.truth_and_observation(condition_id)
        by_id = {item.object_id: item for item in truth.objects}
        return D2AgentInternalState(tuple(D2AgentObjectReport(
            track_id=track, position=by_id[object_id].position, property_signature=by_id[object_id].property_signature,
        ) for track, object_id in self.expected_tracks))

    def frame(self, condition_id: str, state: D2AgentInternalState) -> D2ScientificFrame:
        truth, observation = self.truth_and_observation(condition_id)
        assessment = self.assess(truth, state)
        return D2ScientificFrame(truth, observation, state, assessment, truth.tick, assessment.evaluation_tick)

    @staticmethod
    def validate_agent_observation_payload(payload: Mapping[str, object]) -> None:
        """Reject privileged evaluator fields at the agent-facing boundary."""
        forbidden = FORBIDDEN_AGENT_OBSERVATION_FIELDS.intersection(payload)
        if forbidden:
            raise ValueError("TRUTH_LEAKAGE_DETECTED:" + ",".join(sorted(forbidden)))

    def self_audit(self) -> dict:
        """Verify the instrument's declared cases without attributing cognition.

        The reports used here are observer-side fixtures.  This checks the
        protocol, its view boundaries, and its render projection; it is never
        an agent run, an experimental result, or EvidenceGraph input.
        """
        cases = []
        for condition in self.CONDITIONS:
            frame = self.frame(condition.condition_id, self.correct_reports(condition.condition_id))
            rendered = render_scientific_frame(frame, self.semantic_id)
            cases.append({
                "condition_id": condition.condition_id,
                "tick": frame.world_truth.tick,
                "observer_errors": frame.observer_view.errors,
                "render_alignment_errors": verify_render_alignment(frame, rendered),
            })
        return {
            "schema_version": PROTOCOL_SCHEMA,
            "evaluator_version": EVALUATOR_VERSION,
            "protocol_id": self.semantic_id,
            "classification": "INSTRUMENT_SELF_AUDIT_NOT_AGENT_EVIDENCE",
            "agent_execution": False,
            "evidence_graph_write": False,
            "fixture_origin": "OBSERVER_SIDE_CORRECT_REPORTS",
            "all_cases_pass": all(not item["observer_errors"] and not item["render_alignment_errors"] for item in cases),
            "cases": tuple(cases),
        }

    def assess(self, truth: D2WorldTruth, state: D2AgentInternalState) -> D2ObserverView:
        by_id = {item.object_id: item for item in truth.objects}
        reports = {item.track_id: item for item in state.reports}
        errors: set[str] = set(); details: list[str] = []; missing: list[str] = []
        property_errors = identity_errors = 0
        expected = dict(self.expected_tracks)
        for track_id, object_id in expected.items():
            report = reports.get(track_id)
            if report is None:
                errors.add(ERROR_MISSING_REPORT); missing.append(track_id)
                details.append(f"{track_id}: missing report; {NOT_EVALUABLE}")
                continue
            target = by_id[object_id]
            if report.position != target.position:
                errors.add(ERROR_IDENTITY); identity_errors += 1
                details.append(f"{track_id}: position does not preserve target identity {object_id}")
            if report.property_signature != target.property_signature:
                errors.add(ERROR_PROPERTY); property_errors += 1
                details.append(f"{track_id}: property signature differs from target identity {object_id}")
        first, second = self.expected_tracks
        left, right = reports.get(first[0]), reports.get(second[0])
        pair_eligible = left is not None and right is not None
        identity_swap = binding_swap = False
        if left is not None and right is not None:
            a, b = by_id[first[1]], by_id[second[1]]
            # Equal property signatures are intentionally part of D2 pressure.
            # They are insufficient evidence of a swap; require an independently
            # observable inversion of the tracked identities' positions.
            identity_swap = left.position == b.position and right.position == a.position
            # Binding is an attribute-to-identity error, not merely selecting a
            # different location.  Equal signatures cannot identify a swap.
            binding_swap = (
                a.property_signature != b.property_signature
                and left.property_signature == b.property_signature
                and right.property_signature == a.property_signature
            )
            if identity_swap:
                errors.add(ERROR_IDENTITY_SWAP)
                details.append("track-A/track-B positions are cross-attributed: identity swap")
            if binding_swap:
                errors.add(ERROR_BINDING)
                details.append("track-A/track-B properties are cross-attributed: binding error")
        participant_eligible = len(expected) - len(missing)
        pair_non_evaluable = 0 if pair_eligible else 1
        metrics = (
            D2ErrorMetric(ERROR_PROPERTY, property_errors, participant_eligible, participant_eligible, len(missing)),
            D2ErrorMetric(ERROR_IDENTITY, identity_errors, participant_eligible, participant_eligible, len(missing)),
            D2ErrorMetric(ERROR_IDENTITY_SWAP, int(identity_swap), int(pair_eligible), int(pair_eligible), pair_non_evaluable),
            D2ErrorMetric(ERROR_BINDING, int(binding_swap), int(pair_eligible), int(pair_eligible), pair_non_evaluable),
        )
        return D2ObserverView(
            self.expected_tracks, tuple(sorted(errors)), tuple(details), metrics, tuple(missing), truth.tick)

    def _apply_condition(self, manager: WorldStateManager, condition_id: str) -> None:
        if condition_id == "baseline":
            return
        if condition_id == "movement":
            manager.move_object(0, type(manager.state.objects[0].pos)(3, 3))
        elif condition_id == "occlusion":
            manager.move_object(0, type(manager.state.objects[0].pos)(9, 9))
        elif condition_id == "temporal_property_change":
            original = manager.state.objects[0].channels.copy(); original[0] = min(1.0, float(original[0]) + 0.1)
            manager.set_object_channels(0, original)
        elif condition_id == "similar_properties":
            manager.set_object_channels(1, manager.state.objects[0].channels.copy())
        elif condition_id == "distractor":
            manager.add_object(type(manager.state.objects[2])(
                object_id=99, pos=type(manager.state.objects[2].pos)(4, 4),
                channels=manager.state.objects[0].channels.copy(), movable=True, energy_value=0.0,
                properties={"protocol_role": "distractor"},
            ))
        elif condition_id == "spatial_proximity":
            manager.move_object(1, type(manager.state.objects[1].pos)(2, 4))
        manager.advance_time()
