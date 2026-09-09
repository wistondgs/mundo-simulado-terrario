from terrario.experiment.controller import build_world_state, load_scenario, materialize_scenario
from terrario.world.opportunities import OpportunityLifecycle
from terrario.world.state import WorldStateManager


def test_d4_respawn_is_not_adjacent_to_agent():
    scenario = materialize_scenario(load_scenario("scenarios/d4_adaptation_scientific.yaml"), 11)
    world = WorldStateManager(build_world_state(scenario), scenario["duration"])
    lifecycle = OpportunityLifecycle(scenario["opportunity_lifecycle"], 11)
    target = next(iter(world._mutable_state().objects.values()))
    world.remove_object(target.object_id)
    lifecycle.consume(world, target, 0)
    for step in range(9):
        lifecycle.advance(world, step)
    agent = world._mutable_state().agents[0]
    spawned = [obj for obj in world._mutable_state().objects.values() if obj.object_id >= 10_000]
    assert spawned
    assert all(abs(obj.pos.x-agent.pos.x) + abs(obj.pos.y-agent.pos.y) >= 2 for obj in spawned)
