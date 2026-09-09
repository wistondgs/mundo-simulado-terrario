from terrario.experiment.controller import build_world_state, load_scenario, materialize_scenario
from terrario.world.opportunities import OpportunityLifecycle
from terrario.world.state import WorldStateManager


def _world(seed=11):
    scenario = materialize_scenario(load_scenario("scenarios/d4_adaptation_scientific.yaml"), seed)
    return scenario, WorldStateManager(build_world_state(scenario), scenario["duration"])


def test_d4_signal_density_starts_with_balanced_pool():
    scenario, world = _world()
    geometry = OpportunityLifecycle(scenario["opportunity_lifecycle"], 11).geometry(world)
    assert geometry["opportunities_class_A"] == 16
    assert geometry["opportunities_class_B"] == 16
