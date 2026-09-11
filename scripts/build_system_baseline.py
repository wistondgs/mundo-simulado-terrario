#!/usr/bin/env python
"""Build SYSTEM-BASELINE-01 artifacts without publishing scientific evidence."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from terrario.lab.characterization import characterize_matrix, protected_manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(args.root).resolve(); output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=False)
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    with tempfile.TemporaryDirectory(prefix="terrario-characterization-") as temporary:
        behavior = characterize_matrix(root, temporary)
    (output / "protected_manifest.json").write_text(json.dumps(protected_manifest(root, head), indent=2, sort_keys=True) + "\n")
    (output / "behavior_fixture.json").write_text(json.dumps(behavior, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"classification":"CHARACTERIZATION_ONLY","baseline_head":head,"behavior_digest":behavior["semantic_digest"]}, sort_keys=True))


if __name__ == "__main__": main()
