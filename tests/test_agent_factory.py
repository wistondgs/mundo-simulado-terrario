import pytest
import torch

from terrario.agent.agents import AgentFactoryError, create_agent


@pytest.mark.parametrize("requested, klass", [
    ("A1_REACTIVE", "A1Reactive"), ("A2_GRU", "A2GRUBaseline"),
    ("A3_WORLD_MODEL", "A3WorldModel"), ("A4_ADVANCED", "A4Advanced"),
])
def test_factory_never_substitutes_requested_agent(requested, klass):
    agent = create_agent(requested, {"use_planner": False}, seed=7, device="cpu")
    assert type(agent).__name__ == klass
    assert agent.agent_identity["requested_agent_id"] == requested
    assert agent.agent_identity["initial_parameters_hash"]


def test_factory_fails_loudly_for_unknown_or_unavailable_device(monkeypatch):
    with pytest.raises(AgentFactoryError):
        create_agent("not-an-agent", seed=1)
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)
    with pytest.raises(AgentFactoryError):
        create_agent("A4_ADVANCED", {"use_planner": False}, seed=1, device="cuda")


def test_factory_auto_device_resolves_to_cpu_when_cuda_is_unavailable(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)

    agent = create_agent("A2_GRU", seed=1, device="auto")

    assert agent.agent_identity["device"] == "cpu"
    assert agent._hidden.device.type == "cpu"


@pytest.mark.skipif(not torch.cuda.is_available(), reason="CUDA host required")
def test_a4_cuda_pipeline_keeps_runtime_tensors_on_gpu():
    import numpy as np

    from terrario.core.types import Observation

    agent = create_agent("A4_ADVANCED", {"use_planner": False}, seed=1, device="cuda")
    observation = Observation(
        channels=np.zeros((4, 5, 5), dtype=np.float32), mask=np.ones((5, 5), dtype=np.float32),
        agent_energy=0.5, time_fraction=0.0,
    )
    agent.perceive(observation)
    agent.decide()

    assert agent._hidden.device.type == "cuda"
    assert agent._last_state.device.type == "cuda"
    assert all(parameter.device.type == "cuda" for parameter in agent.get_parameters().values())
