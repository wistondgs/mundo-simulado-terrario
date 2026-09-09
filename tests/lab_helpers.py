import json
from pathlib import Path


def lab_root(tmp_path: Path) -> Path:
    (tmp_path / "configs").mkdir(); (tmp_path / "runs" / "pilot").mkdir(parents=True)
    (tmp_path / "configs" / "h.yaml").write_text("hypothesis:\n  hypothesis_id: H-X\n  status: UNTESTED\n  claim: memory helps\n  version: '1'\n")
    trace = {"step": 0, "action": 2, "energy": .7, "prediction_error": .2, "uncertainty": .1,
             "causal_competence": .8, "rule_changes": ["change"],
             "observation_t": {"channels": [[[1.0]]], "mask": [[1.0]], "agent_energy": .7, "time_fraction": .1},
             "observer_world": {"grid_width": 4, "grid_height": 4, "rules_version": 2,
                                "objects": {"9": {"object_id": 9, "properties": {"causal_class": "SECRET"}}},
                                "agents": {"0": {"pos": [1, 1]}}}}
    data = {"experiment_id": "H-X", "stage": "pilot", "protocol_hash": "cfg", "code_hash": "code",
            "records": [{"variant_id": "A4", "seed": 7, "primary": {"traces": [trace], "energy_history": [.7]}}]}
    (tmp_path / "runs" / "pilot" / "x_results.json").write_text(json.dumps(data))
    return tmp_path
