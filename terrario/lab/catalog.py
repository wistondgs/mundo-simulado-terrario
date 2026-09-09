"""Persistent metadata index. Raw evidence remains at its original path."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from terrario.lab.models import thaw


@dataclass(frozen=True)
class LabCatalog:
    version: int
    experiments: tuple
    runs: tuple
    hypotheses: tuple
    evidence: tuple
    forensic_cases: tuple

    def save(self, path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = {name: thaw(getattr(self, name)) for name in (
            "version", "experiments", "runs", "hypotheses", "evidence", "forensic_cases"
        )}
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return target
