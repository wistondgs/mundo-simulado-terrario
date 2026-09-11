"""Deterministic, read-only behavioral characterization for SYSTEM-BASELINE-01.

The module records existing behavior; it deliberately does not repair or
reinterpret scientific semantics.  Volatile timestamps, temporary paths and
observer run IDs are excluded from the semantic snapshot.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

from terrario.experiment.campaign import build_trace_manifest
from terrario.experiment.config import ExperimentConfig
from terrario.experiment.controller import ExperimentController, load_scenario, materialize_scenario

SCHEMA_VERSION = "terrario.system-baseline/v1"
BASELINE_SEED = 1729
BASELINE_STEPS = 4
SCENARIOS = {
    "D2": "scenarios/d2_properties.yaml",
    "D3": "scenarios/d3_causality.yaml",
    "D4": "scenarios/d4_change.yaml",
}
AGENTS = ("A0_RANDOM", "A1_REACTIVE", "A4_ADVANCED")
PROTECTED_PREFIXES = (
    "terrario/agent", "terrario/core", "terrario/world", "terrario/experiment",
    "theory_snapshots", "scientific_reviews",
)
PROTECTED_FILES = ("configs/h_adapt_001.yaml", "scripts/run_h_adapt_001.py")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def protected_file_hashes(root: str | Path) -> dict[str, str]:
    root = Path(root).resolve()
    paths: set[Path] = set()
    for prefix in PROTECTED_PREFIXES:
        base = root / prefix
        if base.is_dir():
            paths.update(path for path in base.rglob("*") if path.is_file())
    paths.update(root / name for name in PROTECTED_FILES if (root / name).is_file())
    return {
        str(path.relative_to(root)): file_sha256(path)
        for path in sorted(paths)
        if "__pycache__" not in path.parts and path.suffix not in {".pyc", ".pyo"}
    }


def protected_manifest(root: str | Path, baseline_head: str) -> dict[str, Any]:
    files = protected_file_hashes(root)
    root_hash = hashlib.sha256(_canonical(files).encode()).hexdigest()
    return {
        "schema_version": SCHEMA_VERSION,
        "baseline_head": baseline_head,
        "classification": "CHARACTERIZATION_ONLY",
        "protected_file_count": len(files),
        "protected_root_hash": root_hash,
        "files": files,
    }


def characterize_matrix(root: str | Path, output_root: str | Path,
                        seed: int = BASELINE_SEED, steps: int = BASELINE_STEPS,
                        scenarios: Iterable[str] = tuple(SCENARIOS),
                        agents: Iterable[str] = AGENTS) -> dict[str, Any]:
    root = Path(root).resolve(); output_root = Path(output_root).resolve()
    cases = {}
    for scenario_id in scenarios:
        for agent_id in agents:
            case_id = f"{scenario_id}:{agent_id}"
            cases[case_id] = characterize_case(root, output_root / _slug(case_id), scenario_id, agent_id, seed, steps)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "classification": "ENGINEERING_CHARACTERIZATION_NOT_EVIDENCE",
        "seed_policy": {"world_seed": seed, "agent_seed": seed + 1_000_003},
        "steps": steps,
        "cases": cases,
    }
    return {**payload, "semantic_digest": hashlib.sha256(_canonical(payload).encode()).hexdigest()}


def characterize_case(root: Path, output_dir: Path, scenario_id: str, agent_id: str,
                      seed: int = BASELINE_SEED, steps: int = BASELINE_STEPS) -> dict[str, Any]:
    scenario_rel = SCENARIOS[scenario_id]
    scenario_path = root / scenario_rel
    experiment_id = f"system-baseline-{scenario_id.lower()}-{agent_id.lower()}"
    config = ExperimentConfig(experiment_id, None, str(scenario_path), [agent_id], {}, [seed],
        1, steps, "scientific_standard", 2, str(output_dir), "cpu")
    result = ExperimentController(config).run()
    episode = result["episodes"][0]
    run_dir = Path(episode["observer_run_dir"])
    world_rows = _trace_rows(run_dir, "world")
    transition_rows = _trace_rows(run_dir, "transition")
    trace_manifest = build_trace_manifest(run_dir, "characterization", "scientific_standard")
    trace_counts = {name: len(_trace_rows(run_dir, name)) for name in ("world", "consequence", "sensation", "transition", "provenance")}
    identity = episode["agent_identity"]
    materialized = materialize_scenario(load_scenario(str(scenario_path)), seed)
    case = {
        "scenario_id": scenario_id,
        "scenario_source": scenario_rel,
        "scenario_materialization_hash": hashlib.sha256(_canonical(_stable(materialized)).encode()).hexdigest(),
        "scheduled_changes": _stable(materialized.get("changes", [])),
        "agent_id": agent_id,
        "world_seed": episode["world_seed"],
        "agent_seed": episode["agent_seed"],
        "actions": [row["action_t"] for row in transition_rows],
        "observation_t_hashes": [row["observation_t_hash"] for row in transition_rows],
        "observation_t1_hashes": [row["observation_t1_hash"] for row in transition_rows],
        "world_state_hashes": [row["world_state_hash"] for row in world_rows],
        "rules_versions": [row["rules_version"] for row in world_rows],
        "consequences": [_json_value(row["consequence"]) for row in transition_rows],
        "termination": [{"terminated": row["terminated"], "truncated": row["truncated"]} for row in transition_rows],
        "metrics": _stable(episode["metrics"]),
        "num_steps": episode["num_steps"],
        "final_energy": _stable(episode["final_energy"]),
        "agent_identity": {key: identity[key] for key in ("requested_agent_id", "instantiated_agent_class", "architecture_id", "parameter_count", "device", "initial_parameters_hash")},
        "checkpoint_steps": sorted(int(path.name.removeprefix("step_")) for path in (run_dir / "checkpoints").glob("step_*") if path.is_dir()),
        "trace_counts": trace_counts,
        "trace_manifest_verified": trace_manifest.verify(run_dir),
        "trace_file_kinds": sorted(trace_manifest.files),
    }
    return _stable(case)


def _trace_rows(run_dir: Path, name: str) -> list[dict[str, Any]]:
    parquet = run_dir / "events" / f"{name}.parquet"
    jsonl = run_dir / "events" / f"{name}.jsonl"
    if parquet.is_file():
        import pyarrow.parquet as pq
        return pq.read_table(parquet).to_pylist()
    if jsonl.is_file():
        return [json.loads(line) for line in jsonl.read_text().splitlines() if line]
    return []


def _json_value(value: Any) -> Any:
    if isinstance(value, str):
        try: return json.loads(value)
        except json.JSONDecodeError: return value
    return value


def _stable(value: Any) -> Any:
    if isinstance(value, float): return round(value, 10)
    if isinstance(value, dict): return {str(k): _stable(v) for k, v in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (list, tuple)): return [_stable(v) for v in value]
    return value


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _slug(value: str) -> str:
    return value.lower().replace(":", "-").replace("_", "-")
