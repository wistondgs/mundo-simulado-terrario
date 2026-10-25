"""Portable L19 checkpoints with a content hash over the acquired state."""

from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
from typing import Any

from .predictive_state import PredictiveStateLearner


def save_checkpoint(path: str | Path, learner: PredictiveStateLearner,
                    metadata: dict[str, Any]) -> str:
    target = Path(path)
    payload = {
        "schema_version": "terrario.level19.checkpoint/v1",
        "state": learner.state_dict(),
        "state_fingerprint": learner.fingerprint(),
        "metadata": metadata,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(encoded + "\n")
    return sha256(encoded.encode()).hexdigest()


def load_checkpoint(path: str | Path) -> tuple[PredictiveStateLearner, dict[str, Any], str]:
    payload = json.loads(Path(path).read_text())
    if payload.get("schema_version") != "terrario.level19.checkpoint/v1":
        raise ValueError("checkpoint L19 desconocido")
    learner = PredictiveStateLearner.from_state_dict(payload["state"])
    if learner.fingerprint() != payload["state_fingerprint"]:
        raise ValueError("checkpoint L19 corrupto")
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return learner, dict(payload["metadata"]), sha256(encoded.encode()).hexdigest()
