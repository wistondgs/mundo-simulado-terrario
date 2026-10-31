#!/usr/bin/env python3
"""Durable wrapper around the existing Terrario ExperimentController.

It adds provenance and an atomically updated lifecycle record, but does not
implement a second scientific runner.  Invoke it from a detached OS process
only after a preregistration and its configuration are frozen.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import socket
import subprocess
import time
from pathlib import Path
from typing import Any

from terrario.experiment.config import ExperimentConfig
from terrario.experiment.controller import ExperimentController


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temporary.replace(path)


def _head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--status-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    config_path = args.config.resolve()
    status_dir = args.status_dir.resolve()
    status_dir.mkdir(parents=True, exist_ok=False)
    config = ExperimentConfig.from_yaml(str(config_path))
    status_path = status_dir / "status.json"
    common = {
        "schema": "ser-cibernetico-preflight/v1",
        "pid": os.getpid(), "hostname": socket.gethostname(),
        "started_at_unix": time.time(), "code_sha": _head(),
        "config_path": str(config_path), "config_sha256": _sha256(config_path),
        "config_hash": config.config_hash(), "experiment_id": config.experiment_id,
        "output_dir": config.output_dir,
    }
    _atomic_json(status_path, {**common, "state": "RUNNING"})
    try:
        result = ExperimentController(config).run()
    except BaseException as exc:
        _atomic_json(status_path, {**common, "state": "FAILED", "finished_at_unix": time.time(),
                                   "error_type": type(exc).__name__, "error": str(exc)})
        raise
    result_path = Path(config.output_dir) / f"{config.experiment_id}_results.json"
    _atomic_json(status_path, {**common, "state": "COMPLETED", "finished_at_unix": time.time(),
                               "result_path": str(result_path), "result_sha256": _sha256(result_path),
                               "episodes": len(result["episodes"])})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
