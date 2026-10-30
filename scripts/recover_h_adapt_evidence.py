#!/usr/bin/env python3
"""Build public, bounded H-ADAPT execution and behavioural evidence.

This recovery tool reads one named pilot result file and writes only into a
new destination directory.  It does not execute an experiment, modify source
data, or copy checkpoints/raw parquet files.  The public bundle intentionally
contains only the recorded fields required to interpret a run.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def public(value):
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, dict):
        return {key: public(item) for key, item in value.items()}
    if isinstance(value, list):
        return [public(item) for item in value]
    return value


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot", type=Path, required=True)
    parser.add_argument("--d4-source", type=Path, action="append", default=[])
    parser.add_argument("--operational-out", type=Path)
    parser.add_argument("--all-extracts-out", type=Path)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    pilot = args.pilot.resolve()
    out = args.out.resolve()
    payload = json.loads(pilot.read_text(encoding="utf-8"))
    if args.all_extracts_out:
        all_out = args.all_extracts_out.resolve()
        if all_out.exists():
            raise SystemExit(f"refusing to overwrite {all_out}")
        windows = []
        for record in payload["records"]:
            change = record["change_step"]
            windows.append(public({
                "run_id": f"{record['variant_id']}:seed-{record['seed']}",
                "source_sha256": sha256(pilot),
                "positions": [change - 1, change, change + 1],
                "classification": record["classification"],
                "learning_accounting": {"updates": record["updates"], "gradient_steps": record["gradient_steps"]},
                "events": record["primary"]["traces"][change - 1:change + 2],
                "unknown": {"raw_observation_vector": "not recorded", "per_step_parameter_delta": "not recorded"},
            }))
        all_out.write_text(json.dumps({"schema": "terrario.behavioral-window-index/v1", "source_sha256": sha256(pilot), "windows": windows}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return
    if out.exists():
        raise SystemExit(f"refusing to overwrite {out}")
    evidence = {item["run_id"]: item for item in payload["evidence"]}
    records = []
    for ordinal, record in enumerate(payload["records"], start=1):
        run_id = f"{record['variant_id']}:seed-{record['seed']}"
        item = evidence[record["variant_id"] + ":seed-" + str(record["seed"])]
        records.append(public({
            "catalog_id": f"H-ADAPT-001-PILOT-{ordinal:02d}",
            "run_id": run_id,
            "agent": record["agent_identity"],
            "world": {"world_seed": record["world_seed"], "world_spec_hash": record["world_spec_hash"], "change_step": record["change_step"]},
            "configuration": {"protocol_hash": payload["protocol_hash"], "code_hash": payload["code_hash"], "phase": "pilot", "device": record["agent_identity"]["device"]},
            "result": {"classification": record["classification"], "invalid_reason": record["invalid_reason"], "metrics": record["metrics"], "numerical_health": record["numerical_health"]},
            "controls": {"variant_id": record["variant_id"], "transfer_parameters_unchanged": record["transfer_parameters_unchanged"], "transfer_adaptive_state_unchanged": record["transfer_adaptive_state_unchanged"]},
            "learning_accounting": {"updates": record["updates"], "gradient_steps": record["gradient_steps"], "internal_state_sequence_recorded": False},
            "available_references": {"source_file": "runs/h_adapt_001_pilot_clean/h_adapt_001_pilot_results.json", "source_sha256": sha256(pilot), "checkpoint_ref": record["checkpoint_ref"], "event_streams_local_only": ["sensation.parquet", "transition.parquet", "consequence.parquet", "world.parquet", "provenance.parquet"]},
            "declared_evidence": item["metrics"],
            "unknown": {"raw_observation_vector": "not recorded in public result", "per_step_parameter_delta": "not recorded", "execution_id": "not recorded"},
        }))
    out.mkdir(parents=True)
    (out / "h_adapt_001_pilot_execution_catalog.json").write_text(json.dumps({
        "schema": "terrario.execution-catalog/v1",
        "campaign": "H-ADAPT-001 pilot",
        "source_sha256": sha256(pilot),
        "status": "INCONCLUSIVE: pilot_diagnostic=FAIL; not a confirmatory result",
        "pilot_diagnostic": public(payload["pilot_diagnostic"]),
        "records": records,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    samples = [("recovered", "A3_WORLD_MODEL", 23), ("failed_to_recover", "A4_ADVANCED", 53), ("not_learned_pre_change", "A0_RANDOM", 11)]
    extracts = []
    for label, variant, seed in samples:
        record = next(item for item in payload["records"] if item["variant_id"] == variant and item["seed"] == seed)
        change = record["change_step"]
        extracts.append(public({
            "extract_id": f"H-ADAPT-001-{label}", "selection": label,
            "run_id": f"{variant}:seed-{seed}", "source": {"path": "runs/h_adapt_001_pilot_clean/h_adapt_001_pilot_results.json", "sha256": sha256(pilot), "json_pointer": f"/records/{payload['records'].index(record)}", "positions": {"primary_steps": [change - 1, change, change + 1], "transfer_steps": [0, 1, 2]}},
            "result": {"classification": record["classification"], "metrics": record["metrics"], "updates": record["updates"], "gradient_steps": record["gradient_steps"]},
            "interpretation_limit": "The trace records selected action, observer event, consequence, prediction error and state hash. It does not record a raw observation vector or per-step parameter delta.",
            "primary_change_window": record["primary"]["traces"][change - 1:change + 2],
            "transfer_window": record["transfer"]["traces"][:3],
        }))
    (out / "h_adapt_001_behavioral_extracts.json").write_text(json.dumps({
        "schema": "terrario.behavioral-evidence/v1", "source_sha256": sha256(pilot),
        "selection_policy": "one recovered, one failed-to-recover, and one not-learned-pre-change run; no raw checkpoints or full event streams exported", "extracts": extracts,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    d4_records = []
    for source in args.d4_source:
        source = source.resolve()
        digest = sha256(source)
        for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
            row = json.loads(line)
            d4_records.append({
                "catalog_id": f"D4T-OPERATIVE-{len(d4_records)+1:03d}",
                "source": {"path": source.name, "sha256": digest, "line": line_number},
                "condition": row.get("condition"), "seed": row.get("seed"), "world": row.get("world"),
                "configured_steps": row.get("steps"), "result": row.get("measures"),
                "agent": "UNKNOWN: JSONL has no agent identity", "configuration": "UNKNOWN beyond condition/world/steps",
                "controls": "condition labels only; no protocol manifest attached", "behavioural_sequence": "not recorded: aggregate measures only",
            })
    if args.operational_out:
        operational_out = args.operational_out.resolve()
        if operational_out.exists():
            raise SystemExit(f"refusing to overwrite {operational_out}")
        operational_out.write_text(json.dumps({
            "schema": "terrario.execution-catalog/v1", "kind": "operational/screening records, not confirmatory evidence",
            "records": d4_records,
        }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
