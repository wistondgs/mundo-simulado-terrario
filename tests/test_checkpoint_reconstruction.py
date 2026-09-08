from terrario.agent.agents import create_agent
from terrario.core.rng import RNGManager
from terrario.core.types import Action, ActionType, Direction
from terrario.experiment.controller import build_world_state
from terrario.observer.checkpoints import CheckpointManager
from terrario.world.physics import Physics
from terrario.world.state import WorldStateManager


def test_checkpoint_restores_agent_rng_trajectory(tmp_path):
    agent = create_agent("A0_RANDOM", seed=23)
    first = [agent.decide().to_int() for _ in range(3)]
    manager = CheckpointManager(str(tmp_path), save_every_n=1)
    manager.save(agent, 3)
    forward = [agent.decide().to_int() for _ in range(5)]
    manager.restore(agent, 3)
    replay = [agent.decide().to_int() for _ in range(5)]
    assert first
    assert replay == forward


def test_checkpoint_restores_worldtruth_for_identical_replay(tmp_path):
    world = WorldStateManager(build_world_state({
        "grid_size": [5, 5], "agent_start": {"pos": [2, 2], "energy": 10}, "objects": [],
    }))
    agent = create_agent("A0_RANDOM", seed=7)
    manager = CheckpointManager(str(tmp_path))
    physics = Physics()
    for step in range(2):
        physics.step(world, {0: Action(ActionType.MOVE, Direction.RIGHT)}, RNGManager(step))
    manager.save(agent, 2, {"world_snapshot": world.serialize()})
    for step in range(2, 4):
        physics.step(world, {0: Action(ActionType.MOVE, Direction.LEFT)}, RNGManager(step))
    forward_hash = world.state.state_hash()
    manager.restore(agent, 2, world)
    for step in range(2, 4):
        physics.step(world, {0: Action(ActionType.MOVE, Direction.LEFT)}, RNGManager(step))
    assert world.state.state_hash() == forward_hash
