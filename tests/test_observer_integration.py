from pathlib import Path

from terrario.experiment.config import ExperimentConfig
from terrario.experiment.controller import ExperimentController


def test_scientific_observer_persists_complete_transition(tmp_path):
    config = ExperimentConfig("observer", None, "scenarios/d0_differences.yaml", ["A0_RANDOM"], {}, [9], 1, 2, "scientific_standard", 1, str(tmp_path))
    result = ExperimentController(config).run()
    run_dir = Path(result["episodes"][0]["observer_run_dir"])
    assert (run_dir / "manifest.yaml").exists()
    assert any(path.name.startswith("transition.") for path in (run_dir / "events").iterdir())
    assert any((run_dir / "checkpoints").iterdir())
    assert any(path.name == "runtime_state.pt" for path in (run_dir / "checkpoints").rglob("runtime_state.pt"))


def test_forensic_full_captures_real_activation_gradient_and_delta(tmp_path):
    config = ExperimentConfig("forensic", None, "scenarios/d0_differences.yaml", ["A4_ADVANCED"], {
        "use_planner": False, "use_uncertainty": False, "use_episodic_memory": False,
        "use_longterm_memory": False, "use_temporal": False, "latent_dim": 16,
        "hidden_dim": 24, "memory_dim": 8, "memory_slots": 4, "ensemble_size": 2,
    }, [1], 1, 1, "forensic_full", 0, str(tmp_path))
    result = ExperimentController(config).run()
    tensor_names = [path.name for path in (Path(result["episodes"][0]["observer_run_dir"]) / "tensors").iterdir()]
    assert any(name.startswith("activation_") for name in tensor_names)
    assert any(name.startswith("gradient_") for name in tensor_names)
    assert any(name.startswith("parameter_delta_norms") for name in tensor_names)
