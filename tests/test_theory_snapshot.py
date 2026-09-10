import hashlib, json
from tests.theory_helpers import snapshot_dir

def test_theory_snapshot_is_content_addressed_and_complete():
    root=snapshot_dir(); manifest=json.loads((root/"snapshot_manifest.json").read_text())
    assert manifest["missing_artifacts"] == [] and manifest["immutable"] is True
    for item in manifest["artifacts"]:
        assert hashlib.sha256((root/item["filename"]).read_bytes()).hexdigest() == item["sha256"]
