#!/usr/bin/env python3
"""Read-only CL-7 runtime-readiness report; it never runs or publishes science."""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.metrics_observer import ConstructValidationStatus, MetricRegistry


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", required=True, type=Path)
    args = parser.parse_args()
    root = args.data_root.resolve()
    if not root.is_absolute() or not (root / "terrario.db").is_file():
        raise SystemExit("--data-root must be an absolute Terrario data root containing terrario.db")
    database = f"file:{root / 'terrario.db'}?mode=ro"
    con = sqlite3.connect(database, uri=True)
    try:
        states = dict(con.execute("SELECT state,COUNT(*) FROM scientific_executions GROUP BY state"))
        verification_rows = con.execute("SELECT report_json FROM scientific_execution_verifications").fetchall()
        verified = sum(json.loads(row[0]).get("classification") in {"PASS", "DEVIATED"} for row in verification_rows)
        results = con.execute("SELECT COUNT(*) FROM scientific_results").fetchone()[0]
        evidence = con.execute("SELECT COUNT(*) FROM empirical_evidence").fetchone()[0]
        links = con.execute("SELECT COUNT(*) FROM artifact_links WHERE relation='SUPERSEDED_BY'").fetchone()[0]
    finally:
        con.close()
    valid_metrics = tuple(metric.metric_id for metric in MetricRegistry().definitions()
                          if metric.implementation_status.value == "IMPLEMENTED"
                          and metric.construct_validation_status is ConstructValidationStatus.VALIDATED_FOR_CONSTRUCT)
    blockers = []
    if not states.get("COMPLETED", 0): blockers.append("NO_COMPLETED_EXECUTION")
    if not verified: blockers.append("NO_VERIFIED_TERMINAL_EXECUTION")
    if not valid_metrics: blockers.append("NO_IMPLEMENTED_CONSTRUCT_VALIDATED_METRIC")
    print("CL7_RUNTIME_DEMO")
    print(f"DATA_ROOT: {root}")
    print(f"EXECUTION_STATES: {dict(sorted(states.items()))}")
    print(f"VERIFIED_TERMINAL_EXECUTIONS: {verified}")
    print(f"SCIENTIFIC_RESULTS: {results}")
    print(f"EMPIRICAL_EVIDENCE: {evidence}")
    print(f"SUPERSESSION_LINEAGE_LINKS: {links}")
    print(f"CONSTRUCT_VALIDATED_METRICS: {valid_metrics or 'NONE'}")
    print("AGENT_EXECUTED: NO")
    print("SCIENTIFIC_RESULT: NO")
    print("CL7_RUNTIME_DEMO: " + ("BLOCKED_PENDING_AUTHORIZED_EXPERIMENT" if blockers else "READY_FOR_AUTHORIZED_INGESTION"))
    print("BLOCKERS: " + (", ".join(blockers) if blockers else "NONE"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
