#!/usr/bin/env python3
"""Interruptible campaign envelope for the canonical ExperimentController.

Completed units are immutable and never replayed.  An interrupted unit is
preserved under its own attempt directory and is retried as a new attempt; this
avoids appending a resumed trace to partial evidence.  It deliberately does not
claim step-level scientific resumption: that needs a frozen protocol for
restoring both world and agent checkpoint at an exact transition boundary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import socket
import subprocess
import time
from dataclasses import replace
from pathlib import Path
from typing import Any

from terrario.experiment.config import ExperimentConfig
from terrario.experiment.controller import ExperimentController


class Interrupted(RuntimeError):
    pass


_INTERRUPTED = False


def _on_signal(signum: int, _frame: Any) -> None:
    global _INTERRUPTED
    _INTERRUPTED = True


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _atomic_json(path: Path, payload: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with temporary.open("rb") as handle:
        os.fsync(handle.fileno())
    temporary.replace(path)


def _head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def _unit_id(agent: str, seed: int, episode: int) -> str:
    return f"{agent}__seed_{seed:08d}__episode_{episode:04d}"


def _completed(record: Path, parent_hash: str, code_sha: str) -> bool:
    if not record.exists():
        return False
    saved = json.loads(record.read_text(encoding="utf-8"))
    result = Path(saved.get("result_path", ""))
    return (saved.get("state") == "COMPLETED" and saved.get("parent_config_hash") == parent_hash
            and saved.get("code_sha") == code_sha and result.is_file()
            and saved.get("result_sha256") == _sha256(result))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--status-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    config_path, status_dir = args.config.resolve(), args.status_dir.resolve()
    config = ExperimentConfig.from_yaml(str(config_path))
    parent_hash, code_sha = config.config_hash(), _head()
    status_dir.mkdir(parents=True, exist_ok=True)
    units_dir = status_dir / "units"
    units_dir.mkdir(exist_ok=True)
    manifest = status_dir / "manifest.json"
    fixed = {"schema": "ser-cibernetico-resumable/v1", "config_path": str(config_path),
             "config_sha256": _sha256(config_path), "parent_config_hash": parent_hash,
             "code_sha": code_sha, "hostname": socket.gethostname()}
    if manifest.exists():
        old = json.loads(manifest.read_text(encoding="utf-8"))
        if any(old.get(key) != value for key, value in fixed.items() if key != "hostname"):
            raise RuntimeError("status-dir pertenece a otra configuración o código")
    else:
        _atomic_json(manifest, {**fixed, "created_at_unix": time.time()})
    signal.signal(signal.SIGTERM, _on_signal)
    signal.signal(signal.SIGINT, _on_signal)
    pending = 0
    for seed in config.seeds:
        for episode in range(config.num_episodes):
            for agent in config.agent_types:
                if _INTERRUPTED:
                    raise Interrupted("signal before next unit")
                unit = _unit_id(agent, seed, episode)
                record = units_dir / f"{unit}.json"
                if _completed(record, parent_hash, code_sha):
                    continue
                previous = json.loads(record.read_text(encoding="utf-8")) if record.exists() else {}
                attempt = int(previous.get("attempt", 0)) + 1
                attempt_dir = Path(config.output_dir) / "units" / unit / f"attempt_{attempt:04d}"
                unit_config = replace(config, agent_types=[agent], seeds=[seed], num_episodes=1,
                                      output_dir=str(attempt_dir))
                running = {**fixed, "state": "RUNNING", "unit": unit, "attempt": attempt,
                           "pid": os.getpid(), "started_at_unix": time.time(),
                           "unit_config_hash": unit_config.config_hash(), "attempt_dir": str(attempt_dir)}
                _atomic_json(record, running)
                try:
                    controller = ExperimentController(unit_config)
                    episode_result = controller._run_single_episode(agent, seed, episode)
                    controller.results["episodes"] = [episode_result]
                    controller._save_results()
                    result_path = attempt_dir / f"{unit_config.experiment_id}_results.json"
                    _atomic_json(record, {**running, "state": "COMPLETED", "finished_at_unix": time.time(),
                                          "result_path": str(result_path), "result_sha256": _sha256(result_path)})
                except BaseException as exc:
                    _atomic_json(record, {**running, "state": "INTERRUPTED" if _INTERRUPTED else "FAILED",
                                          "finished_at_unix": time.time(), "error_type": type(exc).__name__,
                                          "error": str(exc)})
                    raise
                if _INTERRUPTED:
                    raise Interrupted("signal after atomic unit completion")
                pending += 1
    _atomic_json(status_dir / "status.json", {**fixed, "state": "COMPLETED", "finished_at_unix": time.time(),
                                                "units_completed_this_invocation": pending})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
