from dataclasses import replace
from pathlib import Path

from terrario.lab.experiment_composer import (
    SCHEMA_VERSION, ControlCondition, DraftProvenance, DraftState, ExperimentDraft,
    build_trial_matrix, draft_diff, state_for, validate_draft,
)
from terrario.lab.metrics_observer import MetricRegistry, ObserverRegistry
from terrario.lab.world_registry import WorldScenarioRegistry, configuration_for


def scenario(identifier="D2"):
    return WorldScenarioRegistry(Path(".")).get(identifier).scenario


def draft(identifier="D2"):
    s = scenario(identifier); observer = ObserverRegistry().profile("STANDARD")
    return ExperimentDraft("ED-1", SCHEMA_VERSION, DraftState.DRAFT, s.scenario_id, s.content_hash,
        (f"{identifier}-base",), "difficulty-hash", ("A4",),
        (ControlCondition("A0-baseline", "BASELINE_AGENT", "A0", "A4 versus random baseline"),),
        (f"{identifier}-energy-trajectory",), "STANDARD", observer.channels, (11, 12), (21, 22),
        2, 100, "cpu", s.required_ground_truth, s.required_ground_truth,
        ("agent_energy",), "rules_version changes at scheduled event" if s.interventions else None,
        None, DraftProvenance("lab-user", "compose", "HYPERCAND-01", "READY_FOR_HUMAN_REVIEW"), {})


def findings(d):
    return validate_draft(d, scenario(d.scenario_id), MetricRegistry(), ObserverRegistry())


def test_composer_output_is_draft_never_scientific_run_or_approval():
    d = draft()
    assert type(d).__name__ == "ExperimentDraft"
    assert "APPROVED_FOR_EXECUTION" not in {x.value for x in DraftState}
    assert state_for(findings(d)) == DraftState.REVIEW_BLOCKED


def test_unreviewed_design_and_ground_truth_are_not_laundered():
    d = replace(draft(), available_ground_truth=())
    codes = {x.code for x in findings(d)}
    assert {"REVIEW_REQUIRED", "DESIGN_NOT_APPROVED", "GROUND_TRUTH_MISSING"} <= codes


def test_invalid_scenario_hash_and_missing_metric_signal_fail():
    summary = ObserverRegistry().profile("SUMMARY")
    d = replace(draft(), scenario_hash="wrong", metric_ids=("prediction-error",),
        observer_profile="SUMMARY", observer_channels=summary.channels, available_signals=())
    codes = {x.code for x in findings(d)}
    assert "MISSING_REFERENCE" in codes and "MISSING_REQUIRED_SIGNAL" in codes


def test_unknown_agent_is_an_invalid_technical_interface():
    d = replace(draft(), agent_ids=("A9",))
    assert any(x.code == "INVALID_INTERFACE" and x.category == "COMPATIBILITY" for x in findings(d))


def test_parent_and_reviewed_upstream_are_not_modified_by_derivation():
    parent = draft(); before = parent.content_hash
    child = parent.derive("new seeds", world_seeds=(99,))
    assert parent.content_hash == before and parent.world_seeds == (11, 12)
    assert child.provenance.parent_id == parent.draft_id
    assert child.provenance.source_review_state == "READY_FOR_HUMAN_REVIEW"


def test_scientific_change_changes_hash_but_ui_change_does_not():
    parent = draft()
    changed = parent.derive("metric", metric_ids=("prediction-error",), available_signals=("prediction_error",))
    ui = parent.derive("layout", ui_preferences={"tab": "matrix", "zoom": 2})
    assert changed.content_hash != parent.content_hash
    assert ui.content_hash == parent.content_hash
    assert draft_diff(parent, ui)["hash_changed"] is False


def test_control_contrast_is_explicit_and_empty_contrast_is_blocked():
    d = replace(draft(), controls=(ControlCondition("bad", "ABLATION", "A3", ""),))
    assert any(x.code == "NO_CONTROL" for x in findings(d))


def test_locked_upstream_configuration_is_read_only():
    config = configuration_for(WorldScenarioRegistry(Path(".")).get("D2"))
    before = config.content_hash
    _ = draft()
    assert config.content_hash == before


def test_trial_count_seed_reproducibility_and_no_execution():
    d = draft(); first = build_trial_matrix(d); second = build_trial_matrix(d)
    assert first.total_trials == 1 * 2 * 2 * 2 * 2 == 16
    assert first.cells == second.cells
    assert first.execution_performed is False


def test_blocked_cells_have_reason_and_warning_does_not_change_matrix():
    d = draft()
    blocked = build_trial_matrix(d, {"A0-baseline": ("CAPABILITY_UNVERIFIED",)}, warning_threshold=1)
    normal = build_trial_matrix(d, {"A0-baseline": ("CAPABILITY_UNVERIFIED",)}, warning_threshold=1000)
    assert all(x.blockers for x in blocked.cells if x.condition_id == "A0-baseline")
    assert "COMBINATORIAL_EXPLOSION" in blocked.warnings
    assert blocked.cells == normal.cells


def test_d2_d3_d4_use_same_trial_matrix_infrastructure():
    for identifier in ("D2", "D3", "D4"):
        matrix = build_trial_matrix(draft(identifier))
        assert matrix.total_trials == 16 and matrix.execution_performed is False
