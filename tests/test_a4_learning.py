import numpy as np

from terrario.agent.agents import create_agent
from terrario.core.contracts import Transition
from terrario.core.types import Consequence, Observation


def _observation():
    return Observation(np.full((4, 5, 5), 0.2, dtype=np.float32), np.ones((5, 5), dtype=np.float32), 0.5, 0.1)


def _config(online=True):
    return {
        "use_planner": False, "use_uncertainty": False, "use_episodic_memory": False,
        "use_longterm_memory": False, "use_temporal": False, "use_online_learning": online,
        "latent_dim": 16, "hidden_dim": 24, "memory_dim": 8, "memory_slots": 4, "ensemble_size": 2,
    }


def _learn(agent, steps=10):
    observation = _observation()
    losses, gradients = [], []
    for step in range(steps):
        agent.perceive(observation)
        action = agent.decide()
        agent.learn(Transition(observation, None, action, Consequence(1.0, []), observation, False, False, step, 1))
        event = next(item for item in agent.get_trace_events() if item.get("op") == "learn")
        if "loss_total" in event:
            losses.append(event["loss_total"])
            gradients.append(event["grad_norms"]["encoder"])
    return losses, gradients


def test_a4_has_real_parameter_learning_and_trivial_world_model_improvement():
    agent = create_agent("A4_ADVANCED", _config(), seed=1)
    before = {name: value.clone() for name, value in agent.get_parameters().items()}
    losses, gradients = _learn(agent)
    delta_norm = sum((agent.get_parameters()[name] - value).norm().item() for name, value in before.items())
    assert delta_norm > 0.0
    assert max(gradients) > 0.0
    assert losses[-1] < losses[0]
    assert any(not np.array_equal(value.detach().cpu().numpy(), np.zeros_like(value.detach().cpu().numpy())) for value in agent.get_parameters().values())


def test_a4_online_learning_off_keeps_parameters_unchanged():
    agent = create_agent("A4_ADVANCED", _config(online=False), seed=2)
    before = {name: value.clone() for name, value in agent.get_parameters().items()}
    _learn(agent, steps=3)
    assert all(np.array_equal(before[name].numpy(), value.numpy()) for name, value in agent.get_parameters().items())
