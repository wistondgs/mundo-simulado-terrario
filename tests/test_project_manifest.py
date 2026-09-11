import json
from pathlib import Path


ROOT = Path(__file__).parents[1]


def manifest():
    return json.loads((ROOT / "project_manifest.json").read_text(encoding="utf-8"))


def test_project_manifest_tracks_active_snapshot_counts():
    project = manifest()
    summary = json.loads(
        (ROOT / "theory_snapshots" / "theory-f59dbb6d6ee3850c" / "ingestion_summary.json").read_text(encoding="utf-8")
    )
    active = project["active_theory_snapshot"]
    assert active["snapshot_id"] == summary["snapshot_id"]
    for key, value in active["counts"].items():
        assert summary[key] == value


def test_project_manifest_dependencies_and_world_levels_are_resolved():
    project = manifest()
    component_ids = {item["id"] for item in project["components"]}
    phase_ids = {item["id"] for item in project["phases"]}
    assert all(set(item["depends_on"]) <= component_ids for item in project["components"])
    assert all(set(item["depends_on"]) <= phase_ids for item in project["phases"])
    assert [item["id"] for item in project["world_levels"]] == [f"D{index}" for index in range(12)]


def test_project_manifest_preserves_scientific_boundaries_and_deferred_ux():
    project = manifest()
    invariants = set(project["scientific_invariants"])
    assert "hypothesis != evidence" in invariants
    assert "sandbox run != scientific evidence" in invariants
    phases = {item["id"]: item["status"] for item in project["phases"]}
    assert phases["LAB-UX-03"] == "DEFERRED"
    assert phases["SCIENTIFIC-PILOT-01"] == "HUMAN_AUTHORIZATION_REQUIRED"
