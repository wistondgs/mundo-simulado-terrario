from pathlib import Path

import pytest

from terrario.lab.api import LabAPI, serve
from tests.theory_helpers import primary_corpus_root


PRIMARY_CORPUS = primary_corpus_root()


def test_audited_hypothesis_api_is_source_gated_and_persists_review_only_artifact(tmp_path, monkeypatch):
    monkeypatch.setenv("TERRARIO_PRIMARY_SOURCE_ROOT", str(PRIMARY_CORPUS))
    primary_root, isolated_root = tmp_path / "primary", tmp_path / "isolated"
    service = LabAPI(Path("."), data_root=primary_root)
    status, availability = service.dispatch("GET", "/api/operational-hypotheses/status")
    assert status == 200 and availability["available"] is True
    status, result = service.dispatch("POST", "/api/operational-hypotheses", {})
    assert status == 201 and result["durable"] is True and result["scientific_execution"] is False
    assert result["hypothesis"]["epistemic_status"] == "REVIEW_REQUIRED"
    assert result["experiment_draft_preview"]["state"] == "REVIEW_BLOCKED"
    assert result["experiment_draft"]["state"] == "REVIEW_BLOCKED"
    assert result["experiment_draft"]["payload"]["hypothesis_mapping"]["hypothesis_semantic_id"] == result["artifact_id"]
    assert service.artifacts.current(result["experiment_draft"]["artifact_id"], "ExperimentDraft").scientific_hash == result["experiment_draft"]["scientific_hash"]
    status, repeated = service.dispatch("POST", "/api/operational-hypotheses", {})
    assert status == 201 and repeated["deduplicated"] is True
    reopened = LabAPI(Path("."), data_root=primary_root)
    assert result["artifact_id"] == result["hypothesis"]["semantic_id"]
    restored = reopened.artifacts.current(result["artifact_id"], "OperationalHypothesisDraft")
    assert restored.scientific_hash == result["scientific_hash"]
    assert LabAPI(Path("."), data_root=isolated_root).artifacts.count() == 0


def test_workspace_exposes_audited_hypothesis_action_without_execution_surface():
    view = Path("terrario/lab/static/workspace/views/operational-hypergraph.js").read_text()
    assert "Create audited hypothesis" in view
    assert "H02 × H08 only" in view
    assert "scientific_execution" in view


def test_server_refuses_relative_data_root_to_prevent_implicit_cross_contamination():
    with pytest.raises(ValueError, match="--data-root must be absolute"):
        serve(Path("."), port=0, data_root="relative-test-root")
