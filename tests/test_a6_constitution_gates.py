"""K01--K06 engineering gates for the integrated A6 adapter.

These are contract tests, not a confirmation campaign.  They protect the
meaning of a later A6 comparison from interface leakage or non-resumable state.
"""
from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

import numpy as np

from terrario.agent.agents import create_agent
from terrario.agent.agents.a6_integrated import A6Integrated
from terrario.core.types import Observation
from terrario.experiment.config import ExperimentConfig
from terrario.experiment.controller import ExperimentController
from terrario.experiment.metrics import MetricsCalculator
from terrario.observer.checkpoints import CheckpointManager


def _observation(*, energy: float = 0.1, time: float = 0.0, shifted: bool = False) -> Observation:
    channels = np.zeros((4, 3, 3), dtype=np.float32)
    channels[0, 1 if shifted else 0, 1] = 1.0
    return Observation(channels, np.ones((3, 3), dtype=np.float32), energy, time)


class A6ConstitutionGatesTest(unittest.TestCase):
 def test_k01_visual_codec_is_invariant_to_time_energy_and_declares_aliasing(self):
    first = _observation(energy=0.1, time=0.0)
    same_visual = _observation(energy=0.9, time=0.9)
    spatial_alias = _observation(energy=0.1, time=0.0, shifted=True)
    self.assertEqual(A6Integrated._bit(first), A6Integrated._bit(same_visual))
    self.assertEqual(A6Integrated._observation4(first), A6Integrated._observation4(same_visual))
    # The four presence bits intentionally cannot identify spatial layouts.
    self.assertEqual(A6Integrated._observation4(first), A6Integrated._observation4(spatial_alias))


 def test_k03_models_causally_select_action_after_their_training_boundary(self):
    agent = A6Integrated()
    obs = (1, 0, 0, 0)
    for _ in range(8):
        agent.temporal.observe(obs, obs)
    agent.temporal.freeze()
    from terrario.level17.contingency import ActionContingencyModel

    agent.contingency = ActionContingencyModel(agent.temporal)
    for _ in range(2):
        agent.contingency.observe(obs, agent._efference("B"), obs)
        agent.predictive_state.observe(obs, agent._efference("B"), obs)
    agent.perceive(_observation())
    self.assertEqual(agent.decide().direction.name, "RIGHT")
    # Change both action-conditioned learned tables, then decide again from
    # the same observation. The action must reverse without an outcome first.
    for _ in range(6):
        agent.contingency.observe(obs, agent._efference("A"), obs)
        agent.predictive_state.observe(obs, agent._efference("A"), obs)
    agent.perceive(_observation())
    self.assertEqual(agent.decide().direction.name, "LEFT")


 def test_k05_checkpoint_restores_a6_learned_state_exactly(self):
    base = ExperimentConfig.from_yaml("experiments/unidad_minima_01/ser_integrado_terrario_smoke.yaml")
    with tempfile.TemporaryDirectory() as temporary:
        config = replace(base, output_dir=temporary, max_steps_per_episode=8, checkpoint_every=8)
        result = ExperimentController(config).run()
        run_dir = result["episodes"][0]["observer_run_dir"]
        saved_state = json.loads((Path(run_dir) / "events" / "transition.jsonl").read_text().splitlines()[-1])["internal_state"]
        restored = create_agent("A6_INTEGRATED", config.agent_config, seed=config.seeds[0])
        CheckpointManager(f"{run_dir}/checkpoints").restore(restored, 8)
        self.assertEqual(json.loads(json.dumps(restored.get_internal_state())), saved_state)


 def test_k06_episode_reset_preserves_learning_but_clears_pending_perception(self):
    agent = A6Integrated()
    agent.core.trans[(0, "A")] = (0, 1)
    agent.perceive(_observation())
    agent.reset()
    self.assertEqual(agent.core.trans, {(0, "A"): (0, 1)})
    self.assertIsNone(agent._last_bit)
    self.assertIsNone(agent._last_observation4)

 def test_k02_absent_prediction_is_not_silently_zero_and_energy_is_not_learning(self):
    metrics = MetricsCalculator.compute_all({
        "energy_history": [10.0, 12.0], "actions": [], "traces": [{}],
        "final_energy": 12.0, "compute_cost": 1.0, "num_steps": 2,
    })
    self.assertIsNone(metrics["prediction_errors"])
    self.assertEqual(metrics["prediction_measurement"], "NOT_MEASURED")
    self.assertEqual(metrics["learning_acquisition_rate"]["status"], "NOT_MEASURED")


if __name__ == "__main__":
    unittest.main()
