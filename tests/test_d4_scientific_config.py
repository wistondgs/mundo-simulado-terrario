from terrario.experiment.controller import build_world_state, load_scenario, materialize_scenario
from terrario.world.state import WorldStateManager


def test_scientific_d4_is_paired_procedural_and_renewable():
    scenario = load_scenario("scenarios/d4_adaptation_scientific.yaml")
    first = materialize_scenario(scenario, 17)
    repeat = materialize_scenario(scenario, 17)
    different = materialize_scenario(scenario, 18)

    assert first["objects"] == repeat["objects"]
    assert first["objects"] != different["objects"]
    assert len(first["objects"]) == 32
    assert all(obj["movable"] is False for obj in first["objects"])
    assert all(rule["effect"]["destroy_object"] is False for rule in first["rules"]["rules"])
    assert 425 <= first["changes"][0]["at_step"] <= 475


def test_scientific_d4_hides_time_from_observation_and_charges_steps():
    scenario = materialize_scenario(load_scenario("scenarios/d4_adaptation_scientific.yaml"), 17)
    manager = WorldStateManager(
        build_world_state(scenario), scenario["duration"], scenario["max_energy"],
        scenario["step_energy_cost"], scenario["expose_time_fraction"],
    )
    before = manager._mutable_state().agents[0].energy
    observation = manager.get_observation(0, scenario["view_radius"], scenario["num_channels"])

    assert observation.time_fraction == 0.0
    assert manager.apply_step_energy_cost(0) == -0.06
    assert manager._mutable_state().agents[0].energy == before - 0.06
