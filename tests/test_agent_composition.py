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
    AGENT_CONFIGS, CONCEPTS, CompositionError, catalogue, concepts_for,
    config_for, describe_selection, validate_selection,
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
    # Un catálogo que derive del código ofrecería interruptores que no hacen
    # nada, que es exactamente la confusión que esto viene a terminar. Ahora se
    # comprueba POR AGENTE, porque el linaje tiene más de uno: ofrecer
    # `use_curiosity` --que es de A5-- sobre A4 fue precisamente el fallo.
    for agent in AGENT_CONFIGS:
        config = config_for(agent)
        for concept in concepts_for(agent):
            assert concept.key in config, (agent, concept.key)
            assert concept.purpose and concept.without_it, concept.key


def test_ningun_concepto_pertenece_a_un_agente_que_no_existe():
    """Un concepto que ningún organismo lee no es ofrecible por nadie."""
    ofrecidos = {c.key for agent in AGENT_CONFIGS for c in concepts_for(agent)}
    assert {c.key for c in CONCEPTS} == ofrecidos


def test_un_concepto_de_otro_organismo_se_rechaza_en_vez_de_ignorarse():
    """La fixture negativa del defecto que esto repara.

    `use_curiosity` la lee A5 y no A4. Aceptarla para A4 no cambiaba nada y no
    avisaba -- el peor modo de fallo que puede tener una pantalla de
    composición, y el que su propia cabecera declara.
    """
    with pytest.raises(CompositionError, match="use_curiosity"):
        validate_selection({"use_curiosity": True}, "A4")
    assert validate_selection({"use_curiosity": True}, "A5") == {"use_curiosity": True}


def test_un_agente_sin_conceptos_no_acepta_ninguno():
    """A0 no lee ninguna clave; ofrecerle una es un error, no un no-op."""
    assert concepts_for("A0_RANDOM") == ()
    with pytest.raises(CompositionError, match="use_planner"):
        validate_selection({"use_planner": False}, "A0_RANDOM")


def test_un_agente_desconocido_falla_cerrado():
    with pytest.raises(CompositionError, match="unknown agent"):
        catalogue("A9_INVENTADO")


def test_the_catalogue_carries_what_a_person_needs_to_choose():
    body = catalogue("A4")
    assert body["agent"] == "A4"
    assert len(body["concepts"]) == len(concepts_for("A4"))
    for entry in body["concepts"]:
        # Not just an identifier: a label, what it is for, and what is lost.
        assert entry["label"] and entry["purpose"] and entry["without_it"]
        assert entry["default"] == bool(DEFAULT_CONFIG[entry["key"]])


def test_el_catalogo_de_A5_es_el_de_A4_mas_su_adquisicion():
    """A5 es A4 más una cosa, y su catálogo lo dice igual."""
    a4 = {c["key"] for c in catalogue("A4")["concepts"]}
    a5 = {c["key"] for c in catalogue("A5")["concepts"]}
    assert a5 - a4 == {"use_curiosity"}
    assert a4 - a5 == set()


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


def test_omitting_the_mix_keeps_the_organism_callers_already_had(tmp_path):
    # Additive: a caller that never heard of agent_configuration must get the
    # same agent it got before the field existed.
    api = _api(tmp_path)
    status, run = api.dispatch("POST", "/api/sandbox", {"world_id": "D2", "agent_reference": "A4"})
    assert status == 201 and run["spec"]["agent_configuration"] == {}
