from terrario.core.rng import RNGManager
from terrario.core.types import Action, ActionType, Direction
from terrario.experiment.controller import build_world_state
from terrario.world.physics import Physics
from terrario.world.state import WorldStateManager


def test_private_object_event_never_reaches_agent_consequence():
    world = WorldStateManager(build_world_state({
        "grid_size": [5, 5], "agent_start": {"pos": [2, 2], "energy": 10},
        "objects": [{"pos": [2, 3], "channels": [0.8]}],
    }))
    consequence = Physics().step(world, {0: Action(ActionType.CONSUME, Direction.RIGHT)}, RNGManager(1))[0]
    assert "consume_pending_obj_0" in consequence.observer_events
    assert all("obj_" not in event and "consume_pending" not in event for event in consequence.events)
