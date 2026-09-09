from terrario.experiment.controller import build_world_state, load_scenario, materialize_scenario
from terrario.world.opportunities import OpportunityLifecycle
from terrario.world.state import WorldStateManager


def test_d4_respawn_is_deterministic_for_seed_and_event_index():
    positions = []
    for _ in range(2):
        scenario = materialize_scenario(load_scenario("scenarios/d4_adaptation_scientific.yaml"), 37)
        world = WorldStateManager(build_world_state(scenario), scenario["duration"])
        lifecycle = OpportunityLifecycle(scenario["opportunity_lifecycle"], 37)
        target = next(iter(world._mutable_state().objects.values()))
        world.remove_object(target.object_id); lifecycle.consume(world, target, 0)
        for step in range(9): lifecycle.advance(world, step)
        positions.append([event.position for event in lifecycle.events if event.kind == "respawn"])
    assert positions[0] == positions[1]
