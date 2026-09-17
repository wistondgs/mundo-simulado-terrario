"""Choosing the concepts an organism is made of must reach the organism.

Until this pipe existed the lab contract carried an agent *id* and nothing
else, so every screen could name an architecture and none could compose one.
These tests pin that a chosen mix arrives at the running agent, that it is
part of the run's identity, and that a misspelled concept fails loudly instead
of silently changing nothing -- which is the worst failure a composition
screen can have.
"""
from pathlib import Path

import pytest

from terrario.agent.agents.a4_advanced import DEFAULT_CONFIG
from terrario.lab.agent_composition import (
    CONCEPTS, CompositionError, catalogue, describe_selection, validate_selection,
)
from terrario.lab.api import LabAPI


def _api(tmp_path):
    return LabAPI(Path("."), data_root=tmp_path / ".terrario")


def _run(api, mix, steps=2, world="D2"):
    status, run = api.dispatch("POST", "/api/sandbox", {
        "world_id": world, "agent_reference": "A4", "step_limit": steps + 1,
        "agent_configuration": mix})
    assert status == 201, run
    api.dispatch("POST", f"/api/sandbox/{run['sandbox_run_id']}/run", {"steps": steps})
    _, timeline = api.dispatch("GET", f"/api/sandbox/{run['sandbox_run_id']}/trace")
    return run, timeline


def test_every_offered_concept_is_a_key_the_agent_actually_reads():
    # A catalogue that drifts from the code would offer switches that do
    # nothing, which is exactly the confusion this is meant to end.
    for concept in CONCEPTS:
        assert concept.key in DEFAULT_CONFIG
        assert concept.purpose and concept.without_it, concept.key


def test_the_catalogue_carries_what_a_person_needs_to_choose():
    body = catalogue()
    assert len(body["concepts"]) == len(CONCEPTS)
    for entry in body["concepts"]:
        # Not just an identifier: a label, what it is for, and what is lost.
        assert entry["label"] and entry["purpose"] and entry["without_it"]
        assert entry["default"] == bool(DEFAULT_CONFIG[entry["key"]])


def test_a_chosen_mix_reaches_the_running_organism(tmp_path):
    api = _api(tmp_path)
    _, default_timeline = _run(api, {})
    assert default_timeline[0]["scientific_state"]["active_ablations"] == []

    mix = {"use_planner": False, "use_world_model": False, "use_homeostasis": False}
    _, mixed_timeline = _run(api, mix)
    assert sorted(mixed_timeline[0]["scientific_state"]["active_ablations"]) == [
        "use_homeostasis", "use_planner", "use_world_model"]


def test_the_mix_is_part_of_the_run_identity(tmp_path):
    # A different mix is a different organism, so it belongs in the spec and
    # therefore in its hash -- not in a UI preference beside it.
    api = _api(tmp_path)
    run, _ = _run(api, {"use_planner": False})
    assert run["spec"]["agent_configuration"] == {"use_planner": False}
    plain, _ = _run(api, {})
    assert plain["spec"]["agent_configuration"] == {}


def test_a_misspelled_concept_is_refused_not_ignored(tmp_path):
    api = _api(tmp_path)
    status, body = api.dispatch("POST", "/api/sandbox", {
        "world_id": "D2", "agent_reference": "A4", "agent_configuration": {"use_planer": True}})
    assert status == 400 and "use_planer" in body["error"]


def test_a_tuning_outside_its_range_is_refused():
    with pytest.raises(CompositionError):
        validate_selection({"homeostasis_threshold": 1.4})
    assert validate_selection({"homeostasis_threshold": 0.23}) == {"homeostasis_threshold": 0.23}


def test_a_switch_must_be_a_switch():
    with pytest.raises(CompositionError):
        validate_selection({"use_planner": "no"})


def test_the_mix_reads_as_a_sentence_not_as_flags():
    lines = describe_selection({"use_planner": False, "use_world_model": False})
    assert lines[0].startswith("Con: ") and lines[1].startswith("Sin: ")
    assert "Planificación" in lines[1] and "Modelo del mundo" in lines[1]


def test_omitting_the_mix_keeps_the_organism_callers_already_had(tmp_path):
    # Additive: a caller that never heard of agent_configuration must get the
    # same agent it got before the field existed.
    api = _api(tmp_path)
    status, run = api.dispatch("POST", "/api/sandbox", {"world_id": "D2", "agent_reference": "A4"})
    assert status == 201 and run["spec"]["agent_configuration"] == {}
