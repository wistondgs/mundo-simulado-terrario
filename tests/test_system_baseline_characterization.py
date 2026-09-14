"""Golden characterization gates for refactors after SYSTEM-BASELINE-01."""
from __future__ import annotations

import json
from pathlib import Path

from terrario.lab.characterization import (
    AGENTS, BASELINE_SEED, BASELINE_STEPS, SCENARIOS,
    characterize_case, characterize_matrix, protected_file_hashes,
)

# Baseline 01 remains immutable historical characterization.  Baseline 02 is
# the active protected-source line after the reviewed causal-state contracts.
FIXTURE_ROOT = Path("tests/fixtures/system_baseline_02")


def load_fixture(name: str):
    return json.loads((FIXTURE_ROOT / name).read_text())


def test_protected_source_and_historical_artifact_hashes_match_baseline():
    expected = load_fixture("protected_manifest.json")
    actual = protected_file_hashes(Path("."))
    assert expected["classification"] == "CHARACTERIZATION_ONLY"
    assert len(expected["baseline_head"]) == 40
    assert expected["protected_file_count"] == len(actual)
    assert expected["files"] == actual


def test_d2_d3_d4_a0_a1_a4_match_checked_in_behavior(tmp_path):
    expected = load_fixture("behavior_fixture.json")
    actual = characterize_matrix(Path("."), tmp_path, BASELINE_SEED, BASELINE_STEPS)
    assert expected == actual
    assert set(actual["cases"]) == {f"{scenario}:{agent}" for scenario in SCENARIOS for agent in AGENTS}
    assert actual["classification"] == "ENGINEERING_CHARACTERIZATION_NOT_EVIDENCE"


def test_same_case_repeats_semantically_byte_for_byte(tmp_path):
    first = characterize_case(Path(".").resolve(), tmp_path / "first", "D2", "A0_RANDOM")
    second = characterize_case(Path(".").resolve(), tmp_path / "second", "D2", "A0_RANDOM")
    assert first == second


def test_characterization_covers_transitions_metrics_checkpoints_and_trace_manifests():
    fixture = load_fixture("behavior_fixture.json")
    for case in fixture["cases"].values():
        assert len(case["actions"]) == BASELINE_STEPS
        assert len(case["observation_t_hashes"]) == BASELINE_STEPS
        assert len(case["observation_t1_hashes"]) == BASELINE_STEPS
        assert len(case["world_state_hashes"]) == BASELINE_STEPS
        assert len(case["consequences"]) == BASELINE_STEPS
        assert case["num_steps"] == BASELINE_STEPS
        assert case["checkpoint_steps"] == [2, 4]
        assert case["trace_manifest_verified"] is True
        assert case["trace_counts"] == {"consequence":4,"provenance":4,"sensation":4,"transition":4,"world":4}
        assert {"final_energy", "mean_energy", "acquisition_rate", "num_steps"} <= set(case["metrics"])


def test_d4_fixture_preserves_scheduled_causal_change_without_running_campaign():
    fixture = load_fixture("behavior_fixture.json")
    d4_cases = [case for key, case in fixture["cases"].items() if key.startswith("D4:")]
    assert all(case["scheduled_changes"] for case in d4_cases)
    assert all(len(set(case["rules_versions"])) == 1 for case in d4_cases)
    assert all(case["scheduled_changes"][0]["at_step"] >= BASELINE_STEPS for case in d4_cases)
