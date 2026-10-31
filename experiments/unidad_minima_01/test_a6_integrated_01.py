#!/usr/bin/env python3
"""Contrato de interfaz A6: humo de ingeniería, no campaña confirmatoria."""
from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from terrario.experiment.config import ExperimentConfig
from terrario.experiment.controller import ExperimentController


class A6IntegratedContractTest(unittest.TestCase):
    def test_one_life_updates_shared_and_transferred_state(self) -> None:
        base = ExperimentConfig.from_yaml("experiments/unidad_minima_01/ser_integrado_terrario_smoke.yaml")
        with tempfile.TemporaryDirectory() as temporary:
            config = replace(base, output_dir=temporary)
            result = ExperimentController(config).run()
            episode = result["episodes"][0]
            trace = Path(episode["observer_run_dir"]) / "events" / "transition.jsonl"
            rows = [json.loads(line) for line in trace.read_text(encoding="utf-8").splitlines()]

        self.assertEqual(len(rows), 32)
        state = rows[-1]["internal_state"]
        self.assertTrue(state["trace_valid"])
        self.assertEqual(state["temporal"]["updates"], 8)
        self.assertTrue(state["temporal"]["frozen"])
        self.assertEqual(state["contingency"]["updates"], 24)
        self.assertEqual(state["predictive_state"]["updates"], 32)
        self.assertGreater(rows[-1]["agent_trace_events"][-1]["step"], 0)


if __name__ == "__main__":
    unittest.main()
