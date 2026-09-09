import json

from terrario.experiment.adaptation import AdaptationProtocolRunner, lock_protocol


def test_protocol_lock_persists_frozen_hypothesis_and_hashes(tmp_path):
    runner = AdaptationProtocolRunner(
        "scenarios/d4_adaptation_scientific.yaml",
        "scenarios/d4_adaptation_transfer.yaml",
        str(tmp_path),
    )
    path = tmp_path / "nested" / "H_ADAPT_001_PROTOCOL_LOCK.json"
    lock = lock_protocol(str(path), runner)

    assert path.exists()
    assert json.loads(path.read_text()) == lock
    assert lock["status"] == "LOCKED"
    assert len(lock["variants"]) == 8
