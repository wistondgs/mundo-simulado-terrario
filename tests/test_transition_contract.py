from tempfile import TemporaryDirectory

from terrario.agent.agents import create_agent
from terrario.experiment.config import ExperimentConfig
from terrario.experiment.controller import ExperimentController


def test_a3_receives_complete_transition(monkeypatch):
    agent = create_agent("A3_WORLD_MODEL", seed=4)
    received = []
    original_learn = agent.learn
    def capture(transition):
        received.append(transition)
        original_learn(transition)
    monkeypatch.setattr(agent, "learn", capture)
    with TemporaryDirectory() as path:
        config = ExperimentConfig("transition", None, "scenarios/d0_differences.yaml", ["A3_WORLD_MODEL"], {}, [4], 1, 1, "performance", 0, path)
        controller = ExperimentController(config)
        monkeypatch.setattr(controller, "_create_agent", lambda *_: agent)
        controller.run()
    assert len(received) == 1
    transition = received[0]
    assert transition.observation_t1 is transition.consequence_t1.new_observation
    assert transition.action_t is not None
    assert transition.step == 0 and transition.truncated
