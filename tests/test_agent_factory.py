import pytest

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


def test_factory_fails_loudly_for_unknown_or_unavailable_device():
    with pytest.raises(AgentFactoryError):
        create_agent("not-an-agent", seed=1)
    with pytest.raises(AgentFactoryError):
        create_agent("A4_ADVANCED", {"use_planner": False}, seed=1, device="cuda")
