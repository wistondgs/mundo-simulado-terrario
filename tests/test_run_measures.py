"""Several meshes over one trace, because one measure only finds what it was built to see.

The screening design depends on these: a mesh that stops being defined when a
concept is ablated cannot screen that concept, so every measure here must stay
defined across every mix, and one that cannot be computed must say so instead
of reporting zero.
"""
from pathlib import Path

from terrario.lab.api import LabAPI
from terrario.lab.run_measures import MEASURES_SCHEMA, measure_run


def _step(step, energy=50.0, action="MOVE", revision=1, entropy=1.0, updates=0, alive=True):
    return {
        "step": step,
        "agent_action": {"action_type": action},
        "observer_world": {"agents": {"0": {"energy": energy, "alive": alive}},
                           "max_energy": 100.0, "rules_version": revision},
        "scientific_state": {"policy_entropy": entropy,
                             "parameter_delta_norm": "NOT_APPLICABLE",
                             "learning_summary": {"update_count": updates}},
    }


def _valor(medido, clave):
    return next(m for m in medido["measures"] if m["key"] == clave)


def test_an_empty_trace_is_not_evaluable_rather_than_zero():
    medido = measure_run([])
    assert medido["evaluable"] is False and medido["schema_version"] == MEASURES_SCHEMA


def test_a_channel_the_runtime_marks_not_applicable_is_not_read_as_a_number():
    # The runtime writes the string NOT_APPLICABLE when a channel does not
    # apply. Coercing it to 0.0 would make a frozen organism look like one that
    # changed by exactly nothing, which are different claims.
    medido = measure_run([_step(0), _step(1)])
    cambio = _valor(medido, "cambio_propio")
    assert cambio["evaluable"] is False and cambio["value"] is None
    assert "NO LO EXPONE AL SANDBOX" in cambio["reason"]


def test_behavioural_spread_separates_a_repeater_from_a_mixer():
    repite = measure_run([_step(i, action="MOVE") for i in range(6)])
    mezcla = measure_run([_step(i, action=a) for i, a in
                          enumerate(["MOVE", "PUSH", "CONSUME", "INSPECT", "NOOP", "MOVE"])])
    assert _valor(repite, "variedad_conductual")["value"] == 0.0
    assert _valor(repite, "acciones_distintas")["value"] == 1
    assert _valor(mezcla, "variedad_conductual")["value"] > 2.0
    assert _valor(mezcla, "acciones_distintas")["value"] == 5


def test_indecision_is_averaged_so_a_longer_run_is_not_automatically_less_decided():
    corto = measure_run([_step(i, entropy=1.5) for i in range(3)])
    largo = measure_run([_step(i, entropy=1.5) for i in range(30)])
    assert _valor(corto, "indecision_media")["value"] == _valor(largo, "indecision_media")["value"]


def test_self_updates_are_summed_because_the_total_is_the_quantity_of_interest():
    # update_count is cumulative in the runtime, so the last step carries it.
    medido = measure_run([_step(i, updates=i + 1) for i in range(7)])
    assert _valor(medido, "actualizaciones")["value"] == 7
    congelado = measure_run([_step(i, updates=0) for i in range(7)])
    assert _valor(congelado, "actualizaciones")["value"] == 0


def test_disturbances_are_counted_from_the_rule_version_the_observer_sealed():
    sin = measure_run([_step(i, revision=1) for i in range(8)])
    con = measure_run([_step(i, revision=1 + (i >= 3) + (i >= 6)) for i in range(9)])
    assert _valor(sin, "perturbaciones_vistas")["value"] == 0
    assert _valor(con, "perturbaciones_vistas")["value"] == 2


def test_energy_balance_reports_the_direction_not_only_the_level():
    bajando = measure_run([_step(0, energy=60.0), _step(1, energy=42.5)])
    assert _valor(bajando, "energia_final")["value"] == 42.5
    assert _valor(bajando, "balance_energia")["value"] == -17.5


def test_every_mesh_survives_the_emptiest_mix(tmp_path):
    # The point of these meshes is screening, and a mesh that disappears when a
    # concept is switched off cannot measure that concept.
    api = LabAPI(Path("."), data_root=tmp_path / ".terrario")
    apagado = {"use_temporal": False, "use_episodic_memory": False, "use_longterm_memory": False,
               "use_world_model": False, "use_uncertainty": False, "use_planner": False,
               "use_online_learning": False, "use_homeostasis": False}
    status, run = api.dispatch("POST", "/api/sandbox", {
        "world_id": "D2", "agent_reference": "A4", "step_limit": 5, "agent_configuration": apagado})
    assert status == 201
    api.dispatch("POST", f"/api/sandbox/{run['sandbox_run_id']}/run", {"steps": 4})
    status, medido = api.dispatch("GET", f"/api/sandbox/{run['sandbox_run_id']}/measures")
    assert status == 200
    definidas = [m["key"] for m in medido["measures"] if m["evaluable"]]
    # Only the mesh the agent never exposes is missing; the rest hold up with
    # every concept switched off.
    assert set(m["key"] for m in medido["measures"]) - set(definidas) == {"cambio_propio"}
