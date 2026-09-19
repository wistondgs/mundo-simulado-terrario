"""Choosing the concepts an organism is made of must reach the organism.

Until this pipe existed the lab contract carried an agent *id* and nothing
else, so every screen could name an architecture and none could compose one.
These tests pin that a chosen mix arrives at the running agent, that it is
part of the run's identity, and that a misspelled concept fails loudly instead
of silently changing nothing -- which is the worst failure a composition
screen can have.

"Reaches the organism" is a claim about a NAMED organism.  The catalogue
covers the A4 lineage and A5 reads one key A4 does not, so a concept is only
offerable, and only composable, on the agents that read it.  A catalogue that
answered the question once for everybody would hand an A4 a switch that
changes nothing -- the same failure as a misspelling, one level up.
"""
from pathlib import Path

import pytest

from terrario.agent.agents import ARCHITECTURES
from terrario.agent.agents.a4_advanced import DEFAULT_CONFIG as A4_DEFAULT_CONFIG
from terrario.agent.agents.a5_cybernetic import DEFAULT_CONFIG as A5_DEFAULT_CONFIG
from terrario.lab.agent_composition import (
    CONCEPTS, DEFAULTS_OF, READS, CompositionError, catalogue, default_of,
    describe_selection, keys_read_by, validate_selection,
)
from terrario.lab.api import LabAPI


def _api(tmp_path):
    return LabAPI(Path("."), data_root=tmp_path / ".terrario")


def _run(api, mix, steps=2, world="D2", agent="A4"):
    status, run = api.dispatch("POST", "/api/sandbox", {
        "world_id": world, "agent_reference": agent, "step_limit": steps + 1,
        "agent_configuration": mix})
    assert status == 201, run
    api.dispatch("POST", f"/api/sandbox/{run['sandbox_run_id']}/run", {"steps": steps})
    _, timeline = api.dispatch("GET", f"/api/sandbox/{run['sandbox_run_id']}/trace")
    return run, timeline


def test_every_offered_concept_is_a_key_the_agent_actually_reads():
    # A catalogue that drifts from the code would offer switches that do
    # nothing, which is exactly the confusion this is meant to end. "The agent"
    # is the one that INTRODUCES the concept: the check used to be against A4
    # for everything, which is why a concept only A5 reads could sit in the
    # catalogue with no agent behind it at all.
    for concept in CONCEPTS:
        assert concept.introduced_by in DEFAULTS_OF, concept.key
        assert concept.key in DEFAULTS_OF[concept.introduced_by], concept.key
        assert concept.purpose and concept.without_it, concept.key
    # And the reverse direction, per agent: nothing offered to an organism is
    # a key that organism cannot read.
    for agent in ("A4", "A5"):
        for entry in catalogue(agent)["concepts"]:
            assert entry["key"] in keys_read_by(agent)


def test_every_architecture_the_factory_builds_declares_what_it_reads():
    # A new agent must say what it reads before it can be composed. Silence
    # would make `validate_selection` refuse everything or accept everything,
    # and both are a wrong answer dressed as an answer.
    assert set(READS) == ARCHITECTURES


def test_the_catalogue_carries_what_a_person_needs_to_choose():
    body = catalogue()
    assert len(body["concepts"]) == len(CONCEPTS)
    for entry in body["concepts"]:
        # Not just an identifier: a label, what it is for, and what is lost.
        assert entry["label"] and entry["purpose"] and entry["without_it"]
        assert entry["default"] == bool(DEFAULTS_OF[entry["introduced_by"]][entry["key"]])


def test_the_catalogue_offers_an_organism_only_what_it_can_be_made_of():
    # The one concept A4 does not read is the one that makes A5 an organism of
    # its own. Offering it on an A4 screen would be a dead switch; dropping it
    # from the catalogue would delete the ablation that is CURIO-A1's own
    # falsification control. So it is offered, to A5.
    de_a4 = {c["key"] for c in catalogue("A4")["concepts"]}
    de_a5 = {c["key"] for c in catalogue("A5")["concepts"]}
    assert "use_curiosity" not in de_a4
    assert "use_curiosity" in de_a5
    assert de_a5 - de_a4 == {"use_curiosity"}
    assert de_a4 < de_a5, "un descendiente lee todo lo que lee su ancestro"
    assert catalogue("A5")["architecture"] == "A5_CYBERNETIC"
    # A0 reads its addressing mode and no module switch at all, so it has
    # nothing to compose and the screen must not pretend otherwise.
    assert catalogue("A0")["concepts"] == ()


def test_a_concept_the_named_organism_cannot_read_is_refused():
    # Same grounds as a misspelling: a choice the organism will never see.
    with pytest.raises(CompositionError, match="does not read"):
        validate_selection({"use_curiosity": False}, "A4")
    assert validate_selection({"use_curiosity": False}, "A5") == {"use_curiosity": False}
    # A1 reads nothing from the mix -- its constructor takes explicit arguments
    # and the factory forwards no composition key -- so composing one is refused
    # rather than accepted and dropped on the floor.
    with pytest.raises(CompositionError, match="does not read"):
        validate_selection({"use_planner": False}, "A1")
    with pytest.raises(CompositionError, match="no agent answers"):
        validate_selection({"use_planner": False}, "A9")
    # An empty mix names no choice, so it cannot contradict any agent.
    assert validate_selection({}, "A1") == {}


def test_curiosity_is_ablatable_on_the_organism_that_has_it(tmp_path):
    # The point of the whole arrangement: `use_curiosity` off returns A4 bit by
    # bit, and the trace says so. It could not be composed at all before.
    api = _api(tmp_path)
    _, con = _run(api, {}, agent="A5")
    assert "use_curiosity" not in con[0]["scientific_state"]["active_ablations"]
    _, sin = _run(api, {"use_curiosity": False}, agent="A5")
    assert "use_curiosity" in sin[0]["scientific_state"]["active_ablations"]
    # And the same mix on the ancestor is refused instead of silently ignored.
    status, body = api.dispatch("POST", "/api/sandbox", {
        "world_id": "D2", "agent_reference": "A4",
        "agent_configuration": {"use_curiosity": False}})
    assert status == 400 and "use_curiosity" in body["error"]


def test_the_curiosity_numbers_are_configuration_not_a_constructor_signature():
    # They were literals inside `config.get(...)`, so no preregistration could
    # set them without reading the constructor. A tuning needs a calibrated
    # range and they have none, so they are reachable without being offered.
    assert A5_DEFAULT_CONFIG["curiosity_scale"] == 1.0
    assert A5_DEFAULT_CONFIG["curiosity_floor_decay"] == 0.01
    assert set(A4_DEFAULT_CONFIG) < set(A5_DEFAULT_CONFIG)
    assert "use_curiosity" not in A4_DEFAULT_CONFIG, "A4 permanece intacto"


def test_a_chosen_mix_reaches_the_running_organism(tmp_path):
    api = _api(tmp_path)
    _, default_timeline = _run(api, {})
    # `active_ablations` is derived generically as "every use_* key that is
    # false", so a concept that SHIPS off appears there on a default organism.
    # That reads oddly and it is accurate: the module really is absent, and the
    # observer's job is to say what the organism is made of, not to flatter it.
    # A concept switched off from a default-on state and one never switched on
    # are the same fact for anyone reading the trace.
    assert default_timeline[0]["scientific_state"]["active_ablations"] == [
        "use_factored_action", "use_entropy_regularization"]

    mix = {"use_planner": False, "use_world_model": False, "use_homeostasis": False}
    _, mixed_timeline = _run(api, mix)
    assert sorted(mixed_timeline[0]["scientific_state"]["active_ablations"]) == [
        "use_entropy_regularization", "use_factored_action", "use_homeostasis",
        "use_planner", "use_world_model"]

    # And switching ON a default-off concept removes it from the list, which is
    # the same rule read in the other direction. The OTHER default-off concept
    # stays listed, which is the point: the observer reports what the organism is
    # made of, one concept at a time, not a global verdict.
    _, con_entropia = _run(api, {"use_entropy_regularization": True})
    assert con_entropia[0]["scientific_state"]["active_ablations"] == ["use_factored_action"]

    _, con_ambos = _run(api, {"use_entropy_regularization": True,
                              "use_factored_action": True})
    assert con_ambos[0]["scientific_state"]["active_ablations"] == []


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
    # Named an organism, the sentence describes THAT organism: A4 has no
    # curiosity to be with or without, and saying it lacked one would be
    # reporting an absence that is not a fact about A4.
    de_a4 = " · ".join(describe_selection({}, "A4"))
    assert "Curiosidad" not in de_a4
    assert "Curiosidad" in " · ".join(describe_selection({}, "A5"))


def test_omitting_the_mix_keeps_the_organism_callers_already_had(tmp_path):
    # Additive: a caller that never heard of agent_configuration must get the
    # same agent it got before the field existed.
    api = _api(tmp_path)
    status, run = api.dispatch("POST", "/api/sandbox", {"world_id": "D2", "agent_reference": "A4"})
    assert status == 201 and run["spec"]["agent_configuration"] == {}
