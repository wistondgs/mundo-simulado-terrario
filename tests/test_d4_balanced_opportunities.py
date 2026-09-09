from terrario.experiment.controller import build_world_state, load_scenario, materialize_scenario
from terrario.world.opportunities import OpportunityLifecycle
from terrario.world.state import WorldStateManager


def test_d4_respawn_preserves_causal_class():
    scenario = materialize_scenario(load_scenario("scenarios/d4_adaptation_scientific.yaml"), 23)
    world = WorldStateManager(build_world_state(scenario), scenario["duration"])
    lifecycle = OpportunityLifecycle(scenario["opportunity_lifecycle"], 23)
    target = next(obj for obj in world._mutable_state().objects.values() if obj.properties["causal_class"] == "A")
    world.remove_object(target.object_id)
    lifecycle.consume(world, target, 0)
    for step in range(9): lifecycle.advance(world, step)
    assert any(event.kind == "respawn" and event.causal_class == "A" for event in lifecycle.events)
