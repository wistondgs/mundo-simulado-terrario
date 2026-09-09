from terrario.experiment.controller import build_world_state, load_scenario, materialize_scenario
from terrario.world.opportunities import OpportunityLifecycle
from terrario.world.state import WorldStateManager


def test_d4_initial_signal_and_lifecycle_are_reproducible_per_seed():
    scenario = load_scenario("scenarios/d4_adaptation_scientific.yaml")
    signatures = []
    for _ in range(2):
        resolved = materialize_scenario(scenario, 11)
        world = WorldStateManager(build_world_state(resolved), resolved["duration"])
        lifecycle = OpportunityLifecycle(resolved["opportunity_lifecycle"], 11)
        target = next(iter(world._mutable_state().objects.values()))
        world.remove_object(target.object_id); lifecycle.consume(world, target, 0)
        for step in range(9): lifecycle.advance(world, step)
        signatures.append((world._mutable_state().state_hash(), [event.__dict__ for event in lifecycle.events]))
    assert signatures[0] == signatures[1]
