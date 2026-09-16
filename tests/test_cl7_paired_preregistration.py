from dataclasses import replace

import pytest

from terrario.lab.experiment_composer import (
    ControlCondition, DraftProvenance, DraftState, ExperimentDraft,
    HypothesisExperimentCondition, HypothesisExperimentMapping, TreatmentArm,
    build_trial_matrix,
)
from terrario.lab.models import thaw
from terrario.lab.planning_trace_metric import evaluate
from terrario.lab.preregistration.cl7 import paired_matrix_report


def _draft():
    mapping = HypothesisExperimentMapping(
        "terrario.lab.hypothesis-experiment-mapping/v1", "HYPOTHESIS-b1c155f9304067f0", "prediction", "planner", "trace",
        (HypothesisExperimentCondition("actor-role-preserved", "preserve", "trace", "rationale", {"use_planner": True, "use_world_model": True}),
         HypothesisExperimentCondition("actor-role-ablated", "ablate", "no trace", "rationale", {"use_planner": False, "use_world_model": True})),
        "A4", "D2", "planned-action-evaluation-pathway", "trace", "criterion", "rule", ("C1",),
        {key: "rationale" for key in ("independent_variable", "dependent_variable", "control", "scenario", "metric", "failure_criterion")},
    )
    return ExperimentDraft("EXPERIMENT-DRAFT-20b807bf16cf7ff4", "terrario.lab.experiment-draft/v1", DraftState.REVIEW_BLOCKED,
        "D2", "a" * 64, ("legacy-preserved", "legacy-ablated"), "difficulty", ("A4",),
        (ControlCondition("actor-role-preserved", "ROLE_PRESERVATION_CONTROL", "A4", "paired"),),
        ("planned-action-evaluation-pathway",), "STANDARD", ("decision", "planner_proposal_trace"), (11, 12), (21, 22), 1, 100,
        "cpu", (), (), (), "check", None, DraftProvenance("test", "test", "HYPOTHESIS-b1c155f9304067f0", "REVIEW_REQUIRED"),
        hypothesis_mapping=mapping)


def test_cl7_matrix_is_exactly_eight_paired_noncontradictory_cells_and_order_independent():
    matrix = build_trial_matrix(_draft())
    assert matrix.total_trials == 8
    assert {(cell.seed_pair_id, cell.arm_id) for cell in matrix.cells} == {
        (f"P{i}", arm) for i in range(1, 5) for arm in ("PLANNER_PRESERVED", "PLANNER_ABLATED")}
    report = paired_matrix_report(thaw(matrix))
    reordered = replace(matrix, cells=tuple(reversed(matrix.cells)))
    assert report["valid"]
    assert paired_matrix_report(thaw(reordered))["semantic_matrix_hash"] == report["semantic_matrix_hash"]
    for pair in range(1, 5):
        shared = {cell.initial_state_fingerprint.shared_hash for cell in matrix.cells if cell.seed_pair_id == f"P{pair}"}
        assert len(shared) == 1


def test_cl7_negative_domain_rejections_and_matrix_failures():
    with pytest.raises(ValueError, match="contradictory"):
        TreatmentArm("PLANNER_PRESERVED", "preserved", {"use_planner": False, "use_world_model": True})
    with pytest.raises(ValueError, match="contradictory"):
        TreatmentArm("PLANNER_ABLATED", "ablated", {"use_planner": True, "use_world_model": True})
    matrix = thaw(build_trial_matrix(_draft()))
    matrix["cells"].append(matrix["cells"][0])
    report = paired_matrix_report(matrix)
    assert not report["valid"] and report["duplicate_pair_arm_count"] == 1


def test_cl7_metric_firewall_is_treatment_label_independent():
    trace = ({"op": "decide", "step": 0, "action_int": 0},
             {"op": "plan", "horizon": 2, "num_candidates": 1, "best_action": 0, "rollouts": [{"candidate": 0}]})
    # There is intentionally no arm/variant/config argument to evaluate.
    assert evaluate(trace).value == evaluate(trace).value == 1.0
