import numpy as np
import pytest

from terrario.experiment.controller import build_world_state
from terrario.world.state import WorldStateManager


def test_external_state_view_cannot_mutate_worldtruth():
    manager = WorldStateManager(build_world_state({
        "grid_size": [4, 4], "agent_start": {"pos": [1, 1], "energy": 10}, "objects": [],
    }))
    external = manager.state
    external.agents[0].energy = -999
    assert manager.state.agents[0].energy == 10


def test_agent_observation_has_no_private_world_fields():
    manager = WorldStateManager(build_world_state({
        "grid_size": [4, 4], "agent_start": {"pos": [1, 1], "energy": 10},
        "objects": [{"pos": [1, 2], "channels": [1.0], "energy_value": 99, "properties": {"secret": 1}}],
    }))
    observation = manager.get_observation(0, 1, 2)
    with pytest.raises(AttributeError):
        _ = observation.objects
    with pytest.raises(ValueError):
        observation.channels[0, 0, 0] = 1.0
    assert np.isfinite(observation.channels).all()
