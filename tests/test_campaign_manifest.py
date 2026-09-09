from terrario.experiment.campaign import build_evidence_manifest, verify_evidence_manifest, write_manifest


def test_evidence_manifest_hashes_completed_artifacts(tmp_path):
    artifact = tmp_path / "events" / "transition.jsonl"
    artifact.parent.mkdir()
    artifact.write_text('{"step": 1}\n')
    manifest = build_evidence_manifest(tmp_path, "run-1", {"schema": "test"})
    path = tmp_path / "EVIDENCE_MANIFEST.json"
    write_manifest(path, manifest)

    assert verify_evidence_manifest(path, tmp_path)
    artifact.write_text('{"step": 2}\n')
    assert not verify_evidence_manifest(path, tmp_path)
