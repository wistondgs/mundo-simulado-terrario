#!/usr/bin/env python3
"""Reproducible trace-v2 append/seek benchmark (synthetic, never evidence)."""
from __future__ import annotations

import argparse
import json
import statistics
import tempfile
import time
from pathlib import Path

from terrario.lab.worldstream.trace import TraceArchive


def measure(records: int) -> dict:
    with tempfile.TemporaryDirectory(prefix="terrario-worldstream-bench-") as root:
        archive = TraceArchive(root, "synthetic-benchmark")
        started = time.perf_counter()
        for sequence in range(records):
            archive.append(sequence=sequence, tick=sequence, record_type="EVENT", payload={"synthetic": True, "entity_id": str(sequence % 1000)})
        append_seconds = time.perf_counter() - started
        samples = []
        for tick in (0, records // 4, records // 2, max(0, records - 1)):
            began = time.perf_counter(); archive.seek(tick); samples.append((time.perf_counter() - began) * 1000)
        size = archive.trace_path.stat().st_size
        return {"classification": "SYNTHETIC_ENGINEERING_BENCHMARK", "records": records,
            "append_records_per_second": records / append_seconds, "seek_ms_median": statistics.median(samples),
            "seek_ms_max": max(samples), "trace_bytes": size, "integrity": archive.verify()}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("--records", type=int, default=1000)
    args = parser.parse_args(); print(json.dumps(measure(args.records), indent=2, sort_keys=True))
