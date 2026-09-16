from dataclasses import replace
from pathlib import Path

from terrario.lab.api import LabAPI
from terrario.lab.d2_operational import (
    D2AgentInternalState, ERROR_BINDING, ERROR_IDENTITY, ERROR_IDENTITY_SWAP,
    ERROR_MISSING_REPORT, ERROR_PROPERTY, D2BindingProtocol, render_scientific_frame,
    verify_render_alignment,
)


def protocol():
    return D2BindingProtocol("scenarios/d2_properties.yaml")


def test_d2_protocol_has_explicit_conditions_and_keeps_truth_out_of_agent_observation():
    instrument = protocol()
    assert {item.condition_id for item in instrument.CONDITIONS} == {
        "baseline", "movement", "occlusion", "temporal_property_change",
        "similar_properties", "distractor", "spatial_proximity",
    }
    frame = instrument.frame("baseline", instrument.correct_reports("baseline"))
    assert frame.observer_view.errors == ()
    assert frame.agent_observation.__dict__.keys() == {"channels", "mask", "agent_energy", "time_fraction"}
    assert frame.world_truth.objects and frame.agent_internal_state.adapter_status == "EXTERNAL_TRACKING_ADAPTER"
    assert frame.world_truth.tick == frame.projection_tick == frame.evaluation_tick == frame.observer_view.evaluation_tick


def test_d2_protocol_detects_property_identity_and_binding_swaps_under_real_d2_pressures():
    instrument = protocol()
    for condition in ("movement", "occlusion", "temporal_property_change", "similar_properties", "distractor", "spatial_proximity"):
        assert instrument.frame(condition, instrument.correct_reports(condition)).observer_view.errors == ()

    baseline = instrument.correct_reports("baseline")
    left, right = baseline.reports
    swapped = D2AgentInternalState((
        replace(left, position=right.position, property_signature=right.property_signature),
        replace(right, position=left.position, property_signature=left.property_signature),
    ))
    errors = set(instrument.frame("baseline", swapped).observer_view.errors)
    assert {ERROR_PROPERTY, ERROR_IDENTITY, ERROR_IDENTITY_SWAP, ERROR_BINDING} <= errors


def test_d2_protocol_fails_closed_when_a_required_internal_tracking_report_is_absent():
    instrument = protocol()
    correct = instrument.correct_reports("movement")
    frame = instrument.frame("movement", D2AgentInternalState(correct.reports[:1]))
    assert ERROR_MISSING_REPORT in frame.observer_view.errors
    assert frame.observer_view.not_evaluable_tracks == ("track-B",)
    metrics = {item.metric_id: item for item in frame.observer_view.metrics}
    assert metrics[ERROR_PROPERTY].denominator == 1 and metrics[ERROR_PROPERTY].non_evaluable_cases == 1
    assert metrics[ERROR_IDENTITY_SWAP].denominator == 0 and metrics[ERROR_IDENTITY_SWAP].rate is None


def test_d2_protocol_identity_is_deterministic_for_same_source_scenario():
    assert protocol().semantic_id == protocol().semantic_id


def test_rendered_d2_frame_is_tick_aligned_and_rejects_stale_or_mismatched_render_data():
    instrument = protocol()
    scientific = instrument.frame("spatial_proximity", instrument.correct_reports("spatial_proximity"))
    rendered = render_scientific_frame(scientific, instrument.semantic_id)
    assert verify_render_alignment(scientific, rendered) == ()
    assert "RENDER_TICK_MISMATCH" in verify_render_alignment(scientific, replace(rendered, tick=rendered.tick + 1))
    assert "RENDER_OBSERVER_VIEW_MISMATCH" in verify_render_alignment(scientific, replace(rendered, visible_binding_errors=("fake",)))
    assert "EVALUATION_TICK_MISMATCH" in verify_render_alignment(
        replace(scientific, evaluation_tick=scientific.evaluation_tick + 1), rendered)


def test_error_decision_matrix_distinguishes_property_identity_swap_and_binding():
    instrument = protocol()
    correct = instrument.correct_reports("baseline")
    left, right = correct.reports
    property_only = D2AgentInternalState((
        replace(left, property_signature=right.property_signature), right,
    ))
    identity_only = D2AgentInternalState((
        replace(left, position=right.position), right,
    ))
    full_swap = D2AgentInternalState((
        replace(left, position=right.position, property_signature=right.property_signature),
        replace(right, position=left.position, property_signature=left.property_signature),
    ))
    assert set(instrument.frame("baseline", correct).observer_view.errors) == set()
    assert set(instrument.frame("baseline", property_only).observer_view.errors) == {ERROR_PROPERTY}
    assert set(instrument.frame("baseline", identity_only).observer_view.errors) == {ERROR_IDENTITY}
    assert set(instrument.frame("baseline", full_swap).observer_view.errors) == {
        ERROR_PROPERTY, ERROR_IDENTITY, ERROR_IDENTITY_SWAP, ERROR_BINDING,
    }


def test_d2_rejects_malformed_track_identity_and_privileged_agent_payload():
    instrument = protocol()
    correct = instrument.correct_reports("baseline").reports
    try:
        D2AgentInternalState((replace(correct[0], track_id=""),))
    except ValueError as exc:
        assert str(exc) == "MALFORMED_TRACK_IDENTITY"
    else:  # pragma: no cover - makes the intended failure unmistakable
        raise AssertionError("malformed track identity was accepted")
    try:
        instrument.validate_agent_observation_payload({"channels": (), "world_truth": {}})
    except ValueError as exc:
        assert str(exc) == "TRUTH_LEAKAGE_DETECTED:world_truth"
    else:  # pragma: no cover
        raise AssertionError("privileged payload was accepted")


def test_d2_semantics_ignore_report_storage_order_and_global_position_translation():
    instrument = protocol()
    reports = instrument.correct_reports("movement").reports
    assert instrument.frame("movement", D2AgentInternalState(tuple(reversed(reports)))).observer_view.errors == ()
    truth, _ = instrument.truth_and_observation("baseline")
    shifted_truth = replace(truth, objects=tuple(
        replace(item, position=(item.position[0] + 5, item.position[1] + 7)) for item in truth.objects))
    shifted_reports = D2AgentInternalState(tuple(
        replace(item, position=(item.position[0] + 5, item.position[1] + 7)) for item in instrument.correct_reports("baseline").reports))
    assert instrument.assess(shifted_truth, shifted_reports).errors == ()


def test_d2_instrument_ablations_do_not_launder_missing_or_indistinguishable_information():
    instrument = protocol()
    # ABL-D2-01: a missing participant is data-quality/not-evaluable, never correct.
    partial = D2AgentInternalState(instrument.correct_reports("baseline").reports[:1])
    assert instrument.frame("baseline", partial).observer_view.not_evaluable_tracks == ("track-B",)
    # ABL-D2-02: equal property signatures remove the ability to diagnose a
    # property-binding swap, while the position-based identity swap remains visible.
    baseline = instrument.correct_reports("baseline").reports
    indistinguishable = D2AgentInternalState((
        replace(baseline[0], position=baseline[1].position, property_signature=baseline[0].property_signature),
        replace(baseline[1], position=baseline[0].position, property_signature=baseline[0].property_signature),
    ))
    truth, _ = instrument.truth_and_observation("baseline")
    equal_properties_truth = replace(truth, objects=tuple(
        replace(item, property_signature=truth.objects[0].property_signature) if item.object_id == 1 else item
        for item in truth.objects))
    errors = set(instrument.assess(equal_properties_truth, indistinguishable).errors)
    assert ERROR_IDENTITY_SWAP in errors and ERROR_BINDING not in errors
    # ABL-D2-03 / 04: baseline disables pressure; shuffled mappings cannot pass silently.
    assert instrument.frame("baseline", instrument.correct_reports("baseline")).observer_view.errors == ()
    assert ERROR_BINDING in instrument.frame("baseline", D2AgentInternalState((
        replace(baseline[0], position=baseline[1].position, property_signature=baseline[1].property_signature),
        replace(baseline[1], position=baseline[0].position, property_signature=baseline[0].property_signature),
    ))).observer_view.errors


def test_d2_self_audit_is_explicitly_an_instrument_check_not_agent_evidence(tmp_path):
    service = LabAPI(Path("."), data_root=tmp_path / ".terrario")
    status, audit = service.dispatch(
        "GET", "/api/studio/d2/protocol-audit")
    assert status == 200
    assert audit["all_cases_pass"] is True
    assert audit["classification"] == "INSTRUMENT_SELF_AUDIT_NOT_AGENT_EVIDENCE"
    assert audit["agent_execution"] is False and audit["evidence_graph_write"] is False
    assert {item["condition_id"] for item in audit["cases"]} == {
        "baseline", "movement", "occlusion", "temporal_property_change",
        "similar_properties", "distractor", "spatial_proximity",
    }
    assert all(not item["observer_errors"] and not item["render_alignment_errors"] for item in audit["cases"])
    assert service.artifacts.count() == 0


def test_d2_studio_labels_the_protocol_audit_as_non_evidence():
    view = Path("terrario/lab/static/workspace/views/d2studio.js").read_text(encoding="utf-8")
    client = Path("terrario/lab/static/workspace/core/api.js").read_text(encoding="utf-8")
    assert "D2 INSTRUMENT SELF-AUDIT" in view
    assert "no agent execution · no EvidenceGraph write" in view
    assert "d2ProtocolAudit" in client and "/api/studio/d2/protocol-audit" in client
