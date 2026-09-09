"""Typed, detached queries over completed Terrario artifacts."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml

from terrario.lab.catalog import LabCatalog
from terrario.lab.models import (
    NOT_APPLICABLE, AgentWorldView, EvidenceRecordSummary, ExperimentRecord,
    ForensicCaseRecord, HypothesisRecord, ObserverWorldView, RunRecord,
    RunTimeline, TimelinePoint, freeze,
)


def _json_cell(value: Any) -> Any:
    if value is None:
        return {}
    if isinstance(value, str):
        try: return json.loads(value)
        except json.JSONDecodeError: return value
    return value


class LabReadModel:
    """Read-only adapter; every returned value is frozen and detached."""

    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.runs_root = self.root / "runs"
        self._experiments: list[ExperimentRecord] = []
        self._runs: list[RunRecord] = []
        self._hypotheses: list[HypothesisRecord] = []
        self._evidence: list[EvidenceRecordSummary] = []
        self._forensic: list[ForensicCaseRecord] = []
        self._run_sources: dict[str, tuple[Path, int | None, str]] = {}
        self.refresh()

    def refresh(self) -> None:
        self._experiments.clear(); self._runs.clear(); self._evidence.clear(); self._forensic.clear()
        self._run_sources.clear(); self._load_hypotheses()
        for path in sorted(self.runs_root.glob("**/*_results.json")):
            self._index_result(path)
        for path in sorted(self.runs_root.glob("**/EVIDENCE_MANIFEST.json")):
            eid = "evidence-" + hashlib.sha256(str(path).encode()).hexdigest()[:12]
            self._evidence.append(EvidenceRecordSummary(eid, "RECORDED", str(path), self._experiment_id(path)))
        for path in sorted(self.runs_root.glob("**/forensic*")):
            if path.is_file():
                rid = self._nearest_run(path)
                self._forensic.append(ForensicCaseRecord("forensic-" + hashlib.sha256(str(path).encode()).hexdigest()[:12], "RECORDED", str(path), rid))

    def _load_hypotheses(self) -> None:
        self._hypotheses.clear()
        for path in sorted((self.root / "configs").glob("*.yaml")):
            data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
            h = data.get("hypothesis")
            if h:
                self._hypotheses.append(HypothesisRecord(str(h.get("hypothesis_id")), str(h.get("status", "UNTESTED")), str(h.get("claim", "")), str(h.get("version", NOT_APPLICABLE)), str(path)))

    def _experiment_id(self, path: Path) -> str:
        rel = path.relative_to(self.runs_root)
        parent = rel.parent.as_posix()
        stem = rel.stem.replace("_results", "")
        return stem if parent in {"", "."} else f"{parent.replace('/', '::')}::{stem}"

    def _index_result(self, path: Path) -> None:
        try: data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError): return
        exp_id = self._experiment_id(path)
        records = data.get("records") or data.get("episodes") or []
        locked = (path.parent / "H_ADAPT_001_PROTOCOL_LOCK.json").exists()
        status = data.get("pilot_diagnostic", {}).get("status", data.get("stage", "RECORDED"))
        self._experiments.append(ExperimentRecord(exp_id, str(status), str(data.get("experiment_id", path.stem)), str(path), str(data.get("config_hash", data.get("protocol_hash", NOT_APPLICABLE))), str(data.get("code_hash", NOT_APPLICABLE)), locked, len(records)))
        for i, row in enumerate(records):
            variant = str(row.get("variant_id", row.get("agent_type", "UNKNOWN")))
            seed = row.get("seed", NOT_APPLICABLE)
            run_id = f"{exp_id}:{variant}:seed-{seed}:run-{i}"
            classification = row.get("classification", {})
            if isinstance(classification, str): classification = {"status": classification}
            run_status = str(classification.get("status", row.get("status", "RECORDED")))
            storage = row.get("storage", {}) or {}
            source = storage.get("observer_run_dir", str(path))
            self._runs.append(RunRecord(run_id, exp_id, run_status, variant, seed, str(path), str(row.get("config_hash", data.get("protocol_hash", NOT_APPLICABLE))), str(row.get("code_hash", data.get("code_hash", NOT_APPLICABLE))), str(data.get("experiment_id", "H-ADAPT-001")), str(source), row.get("technical_valid", classification.get("technical_valid", NOT_APPLICABLE)), row.get("experimental_valid", classification.get("experimental_valid", NOT_APPLICABLE))))
            self._run_sources[run_id] = (path, i, str(source))

    def _nearest_run(self, path: Path) -> str:
        for run in self._runs:
            if str(path).startswith(str(Path(run.evidence_path))): return run.id
        return NOT_APPLICABLE

    def catalog(self) -> LabCatalog:
        return LabCatalog(1, tuple(self._experiments), tuple(self._runs), tuple(self._hypotheses), tuple(self._evidence), tuple(self._forensic))

    def experiments(self): return tuple(self._experiments)
    def experiment(self, record_id: str): return next((x for x in self._experiments if x.id == record_id), None)
    def runs(self, experiment_id: str | None = None): return tuple(x for x in self._runs if experiment_id is None or x.experiment_id == experiment_id)
    def run(self, record_id: str): return next((x for x in self._runs if x.id == record_id), None)
    def hypotheses(self): return tuple(self._hypotheses)
    def evidence_manifests(self): return tuple(self._evidence)
    def evidence(self, record_id: str): return next((x for x in self._evidence if x.id == record_id), None)
    def checkpoints(self): return tuple(str(p) for p in sorted(self.runs_root.glob("**/checkpoints/*")) if p.is_file())
    def forensic_cases(self): return tuple(self._forensic)
    def forensic_case(self, record_id: str): return next((x for x in self._forensic if x.id == record_id), None)

    def _rows(self, run_id: str) -> list[dict]:
        ref = self._run_sources.get(run_id)
        if not ref: raise KeyError(run_id)
        result_path, index, storage = ref
        transition = Path(storage) / "events" / "transition.parquet"
        if transition.exists():
            import pyarrow.parquet as pq
            return pq.read_table(transition).to_pylist()
        data = json.loads(result_path.read_text(encoding="utf-8"))
        records = data.get("records") or data.get("episodes") or []
        row = records[index] if index is not None else {}
        primary = row.get("primary", row)
        traces = primary.get("traces", [])
        energies = primary.get("energy_history", [])
        return [{**t, "energy": energies[n] if n < len(energies) else NOT_APPLICABLE} for n, t in enumerate(traces)]

    def timeline(self, run_id: str) -> RunTimeline:
        points = []
        for row in self._rows(run_id):
            internal = _json_cell(row.get("internal_state")); consequence = _json_cell(row.get("consequence"))
            annotations = _json_cell(row.get("observer_annotations")); scientific = _json_cell(row.get("scientific_state"))
            pred = internal.get("prediction", {}) if isinstance(internal, dict) else {}
            learning = internal.get("learning", {}) if isinstance(internal, dict) else {}
            memory = tuple(e for e in (row.get("events") or consequence.get("agent_events", [])) if "memory" in str(e).lower())
            change = bool(row.get("rule_changes") or annotations.get("rule_change") or scientific.get("causal_change"))
            points.append(TimelinePoint(
                int(row.get("step", len(points))), row.get("action_t", row.get("action", NOT_APPLICABLE)),
                row.get("energy", internal.get("homeostasis", {}).get("energy", NOT_APPLICABLE)),
                scientific.get("causal_competence", row.get("causal_competence", NOT_APPLICABLE)),
                row.get("prediction_error", pred.get("prediction_error", NOT_APPLICABLE)),
                internal.get("uncertainty", row.get("uncertainty", NOT_APPLICABLE)),
                scientific.get("policy_entropy", NOT_APPLICABLE), memory or NOT_APPLICABLE,
                tuple(learning.items()) if learning else NOT_APPLICABLE, change,
            ))
        return RunTimeline(run_id, tuple(points), self.run(run_id).source)

    def agent_view(self, run_id: str, step: int = 0) -> AgentWorldView:
        row = self._rows(run_id)[step]; obs = _json_cell(row.get("observation_t", {}))
        return AgentWorldView(run_id, int(row.get("step", step)), freeze(obs.get("channels", ())), freeze(obs.get("mask", ())), obs.get("agent_energy", NOT_APPLICABLE), obs.get("time_fraction", NOT_APPLICABLE))

    def observer_view(self, run_id: str, step: int = 0) -> ObserverWorldView:
        row = self._rows(run_id)[step]; world = _json_cell(row.get("observer_world", {})); annotations = _json_cell(row.get("observer_annotations", {}))
        return ObserverWorldView(run_id, int(row.get("step", step)), int(world.get("grid_width", 0)), int(world.get("grid_height", 0)), freeze(world.get("objects", {})), freeze(world.get("agents", {})), world.get("rules_version", NOT_APPLICABLE), bool(annotations.get("rule_change", False)), freeze(annotations.get("opportunity_lifecycle", NOT_APPLICABLE)))

    def world_snapshot(self, run_id: str, step: int = 0): return self.observer_view(run_id, step)
    def metrics(self, run_id: str): return self.timeline(run_id)
