#!/usr/bin/env python3
"""Run the sealed L19 campaign and write a provenance-bearing JSON artifact."""

from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path
import platform
import subprocess
import sys

import numpy as np

# A source checkout is a supported scientific execution surface; invoking this
# script by path must not silently import a different installed Terrario.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from terrario.level19.experiment import HELD_OUT_SEEDS, campaign


def _git(*args: str) -> str:
    return subprocess.check_output(["git", *args], text=True).strip()


def _file_hash(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=Path("artifacts/level19_predictive_state_v1.json"))
    parser.add_argument("--checkpoints", type=Path,
                        default=Path("artifacts/level19_checkpoints"))
    parser.add_argument("--train-episodes", type=int, default=256)
    parser.add_argument("--evaluation-episodes", type=int, default=256)
    args = parser.parse_args()
    if args.train_episodes <= 0 or args.evaluation_episodes <= 0:
        raise SystemExit("los presupuestos deben ser positivos")
    source = Path("terrario/level19")
    source_hashes = {str(path): _file_hash(path) for path in sorted(source.glob("*.py"))}
    test_hashes = {str(path): _file_hash(path) for path in sorted(Path("tests").glob("test_level19_*.py"))}
    result = campaign(seeds=HELD_OUT_SEEDS, train_episodes=args.train_episodes,
                      evaluation_episodes=args.evaluation_episodes,
                      checkpoint_dir=args.checkpoints)
    payload = {
        "schema_version": "terrario.level19.provenance/v1",
        "git_head": _git("rev-parse", "HEAD"),
        "git_dirty": bool(_git("status", "--porcelain")),
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "pythonpath": __import__("os").environ.get("PYTHONPATH", ""),
        "source_hashes": source_hashes,
        "runner_hash": _file_hash(Path(__file__)),
        "test_hashes": test_hashes,
        "protocol": "docs/LEVEL19_PREDICTIVE_STATE_V1_PREREGISTRATION.md",
        "result": result,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"verdict": result["verdict"],
                      "lcb95_predictive_gain": result["lcb95_predictive_gain"],
                      "lcb95_decision_gain": result["lcb95_decision_gain"]}, sort_keys=True))


if __name__ == "__main__":
    main()
