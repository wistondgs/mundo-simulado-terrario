#!/usr/bin/env python3
"""Pruebas de contrato de Ser Integrado; no son una campaña científica."""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from ser_integrado_01 import _demo, main


class SerIntegradoContractTest(unittest.TestCase):
    def test_shared_core_and_chain(self) -> None:
        organism, result = _demo()
        organism.assert_shared_core()
        self.assertTrue(organism.verify_trace())
        self.assertGreater(len(organism.life_trace), 1)
        self.assertEqual(result["probe"], {"action": "B", "source": "exploration_08"})
        self.assertGreater(result["teacher"]["action_sources"].get("teacher_10", 0), 0)
        self.assertEqual(result["goal"]["authority"], "external_goal_04")
        self.assertTrue(result["goal"]["goal_met"])
        self.assertTrue(result["w1_metrics"]["identifies"])
        sources = {entry["action_source"] for entry in organism.life_trace}
        self.assertTrue({"lesion_03", "regeneration_03", "external_goal_04",
                         "inheritance_repair_09", "exploration_08", "teacher_10"} <= sources)
        contract = organism.laboratory_trace_contract()
        self.assertEqual(contract["status"], "adapter_required")
        self.assertEqual(contract["trace_mapping"]["state_hash"], "state_after_hash")

    def test_explicit_output_is_reconstructible(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "trace.json"
            self.assertEqual(main(["--self-test", "--out", str(output)]), 0)
            self.assertTrue(output.exists())
            self.assertIn('"trace_valid": true', output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
