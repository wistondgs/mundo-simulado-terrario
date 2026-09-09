from copy import deepcopy
from pathlib import Path

from terrario.experiment.adaptation import AdaptationProtocolRunner
from terrario.experiment.campaign import verify_evidence_manifest


def test_transfer_uses_checkpointed_parameters_without_learning(tmp_path):
    runner = AdaptationProtocolRunner(
        "scenarios/d4_adaptation_scientific.yaml",
        "scenarios/d4_adaptation_transfer.yaml",
        str(tmp_path),
        observer_mode="performance",
        agent_overrides={"latent_dim": 8},
    )
    primary = deepcopy(runner.scientific_scenario)
    primary.update({"duration": 8, "max_energy": 100.0, "step_energy_cost": 0.0})
    primary["changes"][0]["at_step"] = 3
    transfer = deepcopy(runner.transfer_scenario)
    transfer.update({"duration": 5, "max_energy": 100.0, "step_energy_cost": 0.0})
    runner.scientific_scenario = primary
    runner.transfer_scenario = transfer

    result = runner.run_variant("A1_REACTIVE", 7)

    assert result["transfer_parameters_unchanged"] is True
    assert result["primary"]["num_steps"] == 8
    assert result["transfer"]["num_steps"] == 5
    assert Path(result["checkpoint_ref"]).is_dir()
    assert Path(result["completion_certificate_path"]).is_file()
    assert verify_evidence_manifest(result["evidence_manifest_path"], Path(result["evidence_manifest_path"]).parent)
