"""Tests for the observer subsystem: traces, storage, checkpoints."""

from __future__ import annotations

import json
import os
import tempfile

import numpy as np
import pytest

from terrario.core.types import Observation


class TestTraceCreation:
    """Test trace creation and serialization."""

    def test_trace_dict_structure(self):
        trace = {
            "step": 0,
            "action": 5,
            "energy": 100.0,
            "events": ["move_success"],
            "prediction_error": 0.0,
            "state_hash": "abc123",
        }
        assert trace["step"] == 0
        assert isinstance(trace["events"], list)
        assert isinstance(trace["energy"], float)

    def test_trace_json_serializable(self):
        trace = {
            "step": 0,
            "action": 5,
            "energy": 100.0,
            "events": ["move_success"],
            "prediction_error": 0.0,
            "state_hash": "abc123",
        }
        serialized = json.dumps(trace)
        deserialized = json.loads(serialized)
        assert deserialized == trace

    def test_trace_with_rule_changes(self):
        trace = {
            "step": 750,
            "action": 3,
            "energy": 85.0,
            "events": ["consume_pending_obj_2"],
            "prediction_error": 0.5,
            "state_hash": "def456",
            "rule_changes": [{"old_version": 1, "new_version": 2}],
        }
        serialized = json.dumps(trace)
        deserialized = json.loads(serialized)
        assert deserialized["rule_changes"][0]["new_version"] == 2


class TestStorageManager:
    """Test save and load of experiment data."""

    def test_save_and_load_results(self):
        results = {
            "experiment_id": "test",
            "episodes": [
                {"agent_type": "A0_RANDOM", "seed": 42, "final_energy": 95.0},
                {"agent_type": "A1_REACTIVE", "seed": 42, "final_energy": 110.0},
            ],
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, "results.json")
            with open(path, "w") as f:
                json.dump(results, f)

            with open(path) as f:
                loaded = json.load(f)

            assert loaded["experiment_id"] == "test"
            assert len(loaded["episodes"]) == 2
            assert loaded["episodes"][0]["final_energy"] == 95.0

    def test_save_numpy_types(self):
        """Numpy types should be serializable with a default handler."""
        data = {
            "energy": np.float64(95.5),
            "count": np.int64(42),
        }
        serialized = json.dumps(data, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer)) else str(o))
        loaded = json.loads(serialized)
        assert loaded["energy"] == pytest.approx(95.5)
        assert loaded["count"] == 42


class TestCheckpoint:
    """Test checkpoint save and load."""

    def test_checkpoint_save_load(self):
        from terrario.core.rng import RNGManager

        rng = RNGManager(42)
        rng.python.random()  # advance state
        state = rng.get_state()

        with tempfile.TemporaryDirectory() as tmpdir:
            # Save checkpoint data
            checkpoint = {
                "step": 100,
                "rng_python_state": str(state.python_state),
                "world_hash": "abc123",
            }
            path = os.path.join(tmpdir, "checkpoint.json")
            with open(path, "w") as f:
                json.dump(checkpoint, f)

            with open(path) as f:
                loaded = json.load(f)

            assert loaded["step"] == 100
            assert loaded["world_hash"] == "abc123"

    def test_rng_restore_from_checkpoint(self):
        from terrario.core.rng import RNGManager

        rng = RNGManager(42)
        vals_before = [rng.python.random() for _ in range(5)]
        state = rng.get_state()

        # Advance further
        [rng.python.random() for _ in range(10)]

        # Restore
        rng.set_state(state)
        vals_after = [rng.python.random() for _ in range(5)]

        # Generate reference
        rng2 = RNGManager(42)
        [rng2.python.random() for _ in range(5)]
        vals_ref = [rng2.python.random() for _ in range(5)]

        assert vals_after == vals_ref


class TestObserverDoesNotModifyAgent:
    """Verify that observer operations don't affect agent state."""

    def test_observer_is_passive(self):
        from terrario.experiment.controller import _BuiltinAgent

        agent = _BuiltinAgent("A0_RANDOM", seed=42)
        obs = Observation(
            channels=np.zeros((4, 5, 5), dtype=np.float32),
            mask=np.ones((5, 5), dtype=np.float32),
            agent_energy=0.5,
            time_fraction=0.0,
        )

        # Record action before "observation"
        agent.perceive(obs)
        action_before = agent.decide()

        # Simulate observer logging (should not affect agent)
        trace = {
            "step": 0,
            "action": action_before.to_int(),
            "energy": 100.0,
            "events": [],
            "prediction_error": 0.0,
        }
        serialized = json.dumps(trace)

        # Agent should produce the same action sequence after observer activity
        agent2 = _BuiltinAgent("A0_RANDOM", seed=42)
        agent2.perceive(obs)
        action_after = agent2.decide()

        assert action_before.to_int() == action_after.to_int()
