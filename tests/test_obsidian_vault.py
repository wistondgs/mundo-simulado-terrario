import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).parents[1]


def test_generated_obsidian_dashboard_matches_project_manifest():
    result = subprocess.run(
        [sys.executable, "scripts/sync_obsidian_vault.py", "--check"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, result.stderr

    manifest = ROOT / "project_manifest.json"
    dashboard = (ROOT / "knowledge" / "_generated" / "Estado tecnico.md").read_text(encoding="utf-8")
    project = json.loads(manifest.read_text(encoding="utf-8"))
    assert hashlib.sha256(manifest.read_bytes()).hexdigest() in dashboard
    assert project["active_theory_snapshot"]["snapshot_id"] in dashboard
    assert all(blocker in dashboard for blocker in project["active_blockers"])
