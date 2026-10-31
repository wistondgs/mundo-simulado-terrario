"""K04: rejected remote consume requests may not activate hidden rules."""
from __future__ import annotations

import tempfile
import unittest
from dataclasses import dataclass
from pathlib import Path

import yaml

from terrario.agent.base import AgentInterface
from terrario.core.contracts import Transition
from terrario.core.types import Action, ActionType, Direction, Observation
from terrario.experiment.config import ExperimentConfig
from terrario.experiment.controller import ExperimentController


@dataclass
class _RemoteConsumer(AgentInterface):
    agent_identity: dict = None  # type: ignore[assignment]

    def __post_init__(self):
        self.agent_identity = {"architecture_id": "TEST_REMOTE"}

    def perceive(self, observation: Observation) -> None:
        pass

    def decide(self) -> Action:
        return Action(ActionType.CONSUME, Direction.RIGHT, target_id=0)

    def learn(self, transition: Transition) -> None:
        self.events = transition.events

    def get_internal_state(self):
        return {}

    def get_trace_events(self):
        return []

    def reset(self):
        pass

    def get_parameters(self):
        return {}

    def set_parameters(self, params):
        pass

    def parameter_count(self):
        return 0


class _Controller(ExperimentController):
    def _create_agent(self, agent_type, seed):
        return _RemoteConsumer()


class RemoteTargetGateTest(unittest.TestCase):
 def test_remote_target_cannot_receive_rule_effect(self):
    scenario = {
        "scenario": {
            "grid_size": [4, 4], "duration": 1, "view_radius": 1, "num_channels": 4,
            "agent_start": {"pos": [0, 0], "energy": 10.0},
            "objects": [{"pos": [3, 3], "channels": [1, 0, 0, 0]}],
            "rules": {"rules": [{"id": "remote-must-not-fire", "condition": {"action": "CONSUME"},
                                   "effect": {"energy_delta": 50.0}}]},
        }
    }
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        scenario_path = root / "remote.yaml"
        scenario_path.write_text(yaml.safe_dump(scenario), encoding="utf-8")
        config = ExperimentConfig("k04", None, str(scenario_path), ["TEST_REMOTE"], {}, [7], 1, 1,
                                  "scientific_standard", 0, str(root / "out"))
        result = _Controller(config).run()
        self.assertEqual(result["episodes"][0]["final_energy"], 10.0)


if __name__ == "__main__":
    unittest.main()
