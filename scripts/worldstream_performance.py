#!/usr/bin/env python3
"""Reproducible trace-v2 append/seek benchmark (synthetic, never evidence)."""
from __future__ import annotations

import argparse
import json
import random
import statistics
import sys
import tempfile
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.worldstream.contracts import WORLDSTREAM_SCHEMA
from terrario.lab.worldstream.trace import TraceArchive


def _frame(tick: int) -> dict:
    """Small but structurally complete WorldFrame for a trace-only benchmark."""
    return {"schema_version": WORLDSTREAM_SCHEMA, "session_id": "synthetic-session",
        "world_instance_id": "synthetic-world", "scenario_id": "SYNTHETIC", "world_seed": 0,
        "agent_identity": {}, "tick": tick, "sequence": tick, "simulation_time": float(tick),
        "frame_origin": "INITIAL_SNAPSHOT" if tick == 0 else "TRANSITION_RESULT", "trace_id": "synthetic-benchmark",
        "views": [{"kind": kind, "tick": tick, "simulation_time": float(tick), "status": "SYNCHRONIZED", "payload": {}, "provenance": {}}
                  for kind in ("WORLD_TRUTH_PRIVILEGED", "AGENT_OBSERVATION", "OBSERVER_VIEW")]}


def _percentile(values: list[float], quantile: float) -> float:
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, int((len(ordered) - 1) * quantile))]


def measure(records: int, samples: int = 32, checkpoint_interval: int = 256) -> dict:
    with tempfile.TemporaryDirectory(prefix="terrario-worldstream-bench-") as root:
        archive = TraceArchive(root, "synthetic-benchmark", checkpoint_interval=checkpoint_interval)
        started = time.perf_counter()
        for sequence in range(records):
            frame = _frame(sequence)
            envelope = {"schema_version": WORLDSTREAM_SCHEMA, "session_id": "synthetic-session", "sequence": sequence,
                "message_type": "SNAPSHOT" if sequence == 0 else "DELTA", "tick": sequence, "payload": {"frame": frame},
                "trace_id": "synthetic-benchmark", "emitted_at": "synthetic"}
            archive.append(sequence=sequence, tick=sequence, record_type=envelope["message_type"], payload=envelope)
            if sequence and sequence % checkpoint_interval == 0:
                archive.checkpoint(sequence, sequence, frame, "INTERVAL")
        append_seconds = time.perf_counter() - started
        ticks = [0, records // 4, records // 2, records * 3 // 4, max(0, records - 1)]
        rng = random.Random(0); ticks.extend(rng.randrange(records) for _ in range(max(0, samples - len(ticks))))
        cold_samples, warm_samples = [], []
        for tick in ticks:
            began = time.perf_counter(); archive.frame_at(tick); cold_samples.append((time.perf_counter() - began) * 1000)
            began = time.perf_counter(); archive.frame_at(tick); warm_samples.append((time.perf_counter() - began) * 1000)
        size = archive.trace_path.stat().st_size
        checkpoints = list(archive.checkpoint_dir.glob("*.json"))
        return {"classification": "SYNTHETIC_ENGINEERING_BENCHMARK", "records": records, "seek_samples": len(ticks),
            "checkpoint_interval": checkpoint_interval, "append_seconds": append_seconds,
            "append_records_per_second": records / append_seconds,
            "frame_seek_cold_ms": {"p50": _percentile(cold_samples, .5), "p95": _percentile(cold_samples, .95), "max": max(cold_samples)},
            "frame_seek_warm_ms": {"p50": _percentile(warm_samples, .5), "p95": _percentile(warm_samples, .95), "max": max(warm_samples)},
            "trace_bytes": size, "index_bytes": archive.index_path.stat().st_size,
            "checkpoint_count": len(checkpoints), "checkpoint_bytes": sum(path.stat().st_size for path in checkpoints),
            "integrity": archive.verify()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--records", type=int, default=1000); parser.add_argument("--samples", type=int, default=32)
    parser.add_argument("--checkpoint-interval", type=int, default=256)
    args = parser.parse_args(); print(json.dumps(measure(args.records, args.samples, args.checkpoint_interval), indent=2, sort_keys=True))
