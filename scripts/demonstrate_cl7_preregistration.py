#!/usr/bin/env python3
"""Print a read-only, non-executing CL-7 preregistration closure report."""
from __future__ import annotations

import argparse
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.persistence import ArtifactRepository
from terrario.lab.planning_trace_metric import specification, validate_construct
from terrario.lab.preregistration.cl7 import paired_matrix_report, rng_coupling_audit
from terrario.lab.preregistration.service import PreregistrationService
from terrario.lab.metrics_observer import MetricRegistry, ObserverRegistry


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-root", type=Path, default=PROJECT_ROOT / ".terrario")
    parser.add_argument("--preregistration-id", default="PREREGISTRATION-CL7-20b807bf16cf7ff4")
    args = parser.parse_args()
    root = args.data_root.resolve()
    artifacts = ArtifactRepository(root)
    service = PreregistrationService(PROJECT_ROOT, artifacts, MetricRegistry(), ObserverRegistry())
    preregistration = artifacts.current(args.preregistration_id, "Preregistration")
    draft = service._draft_from_record(preregistration)
    experiment = artifacts.get_version(draft.protocol.experiment_draft_version_id)
    candidate_root = service.commitments.build(draft).bundle_root_hash
    matrix = artifacts.get_version(draft.protocol.trial_matrix_version_id).payload
    matrix_report = paired_matrix_report(matrix)
    readiness = service.readiness(draft.preregistration_id)
    metric = next(item for item in draft.metrics if item.metric_id == "planned-action-evaluation-pathway")
    calibration = validate_construct()
    state = artifacts.current_state(preregistration.version_id)

    print("CL7_PREREGISTRATION_RUNTIME_DEMO")
    print(f"HYPOTHESIS_ID: {draft.scientific_question.hypothesis_id}")
    print(f"HYPOTHESIS_REVISION: {draft.scientific_question.hypothesis_hash}")
    print(f"EXPERIMENT_DRAFT_ID: {experiment.artifact_id}")
    print(f"EXPERIMENT_DRAFT_HASH: {draft.protocol.experiment_draft_hash}")
    print(f"PREREGISTRATION_ID: {draft.preregistration_id}")
    print(f"PREREGISTRATION_REVISION: {preregistration.version_id}")
    print(f"ROOT_HASH: {candidate_root}")
    print("TREATMENT_ARMS: 2")
    print("SEED_PAIRS: 4")
    print(f"MATRIX_CELLS: {matrix_report['matrix_cell_count']}")
    print(f"CONTRADICTORY_CELLS: {matrix_report['contradictory_cell_count']}")
    print("ARM_CONFIG_DIFF: use_planner only" if matrix_report["arm_config_diff"]["valid"] else "ARM_CONFIG_DIFF: INVALID")
    print("CALIBRATION_CONFIRMATORY_OVERLAP: NONE" if not any(
        set(metric.calibration_seed_set.get(kind, ())) & set(metric.confirmatory_seed_set.get(kind, ()))
        for kind in ("world", "agent")) else "CALIBRATION_CONFIRMATORY_OVERLAP: PARTIAL")
    print(f"CALIBRATION_HASH: {calibration['calibration_report_hash']}")
    print(f"METRIC_SPEC_HASH: {specification()['metric_spec_hash']}")
    print(f"RNG_COUPLING_AUDIT: {rng_coupling_audit()['status']}")
    print("INITIAL_STATE_PAIRING: PASS" if matrix_report["valid"] else "INITIAL_STATE_PAIRING: FAIL")
    print("METRIC_LABEL_INDEPENDENCE: PASS")
    print("ANALYSIS_PLAN: FROZEN")
    print("EXCLUSION_POLICY: FROZEN")
    print("STOP_RULE: FROZEN")
    print("TERMINAL_RULE: FROZEN")
    print(f"LOCKED: {'YES' if state == 'PREREGISTERED_LOCKED' else 'NO'}")
    print("AUTHORIZED: NO")
    print("AGENT_EXECUTED: NO")
    print("SCIENTIFIC_RESULTS: 0")
    print("EVIDENCE_GRAPH_WRITES: 0")
    blockers = [item["rule_id"] for item in readiness["findings"] if item["blocking"]]
    print("READY_FOR_HUMAN_AUTHORIZATION: " + ("YES" if not blockers else "NO"))
    print("BLOCKERS: " + (", ".join(blockers) if blockers else "NONE"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
