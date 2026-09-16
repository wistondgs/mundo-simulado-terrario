from dataclasses import replace
from pathlib import Path

from terrario.lab.api import LabAPI
from terrario.lab.d2_visual_fixture import build_d2_visual_validation_fixture


SCENARIO = "scenarios/d2_properties.yaml"


def fixture():
    return build_d2_visual_validation_fixture(SCENARIO)


def test_fixture_is_deterministic_path_independent_and_non_evidential():
    first, second = fixture(), build_d2_visual_validation_fixture(Path(SCENARIO).resolve())
    assert first.fixture_id == second.fixture_id and first.semantic_hash == second.semantic_hash
    payload = first.payload()
    assert payload["epistemic_scope"] == "INSTRUMENT_SELF_AUDIT_NOT_AGENT_EVIDENCE"
    assert payload["agent_executed"] is False and payload["evidence_graph_writes"] == 0
    assert all(frame["agent_observation"]["availability"] == "NOT_APPLICABLE" for frame in payload["frames"])
    assert all(frame["cognitive_state"]["availability"] == "NOT_APPLICABLE" for frame in payload["frames"])


def test_fixture_has_canonical_lifecycle_identity_property_and_binding_events():
    frames = {frame.phase: frame for frame in fixture().frames}
    assert tuple(frame.tick for frame in fixture().frames) == tuple(range(12))
    assert 0 in frames["INITIAL"].visible_object_ids
    assert 0 not in frames["OCCLUDED"].visible_object_ids
    assert 0 in frames["REAPPEAR"].visible_object_ids
    assert dict(frames["OCCLUDED"].lifecycle)[0] == "occluded"
    assert dict(frames["REAPPEAR"].lifecycle)[0] == "visible_again"
    initial = next(item for item in frames["INITIAL"].world_truth if item["object_id"] == 0)
    changed = next(item for item in frames["PROPERTY_CHANGE"].world_truth if item["object_id"] == 0)
    assert initial["object_id"] == changed["object_id"] and initial["property_signature"] != changed["property_signature"]
    assert "BINDING_ERROR" in frames["BINDING_ERROR"].observer_errors


def test_fixture_frames_have_no_unknown_visible_object_or_tick_skew():
    for frame in fixture().frames:
        ids = {item["object_id"] for item in frame.world_truth}
        assert set(frame.visible_object_ids) <= ids
        payload = frame.payload()
        assert payload["tick"] == payload["projection_tick"] == payload["evaluation_tick"]


def test_visual_fixture_api_is_read_only_and_keeps_data_root_empty(tmp_path):
    service = LabAPI(Path("."), data_root=tmp_path / "visual-fixture-root")
    status, payload = service.dispatch("GET", "/api/studio/d2/visual-fixture")
    assert status == 200 and payload["fixture_id"] == fixture().fixture_id
    assert service.artifacts.count() == 0


def test_d2_studio_consumes_server_fixture_without_reimplementing_classifier_logic():
    view = Path("terrario/lab/static/workspace/views/d2studio.js").read_text(encoding="utf-8")
    assert "d2VisualFixture" in view
    assert "D2 VISUAL VALIDATION FIXTURE" in view
    assert "frame.observer_view?.errors" in view
    assert "BINDING_ERROR" not in view  # the UI renders, it does not classify
