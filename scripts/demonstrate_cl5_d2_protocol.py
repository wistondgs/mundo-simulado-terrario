#!/usr/bin/env python3
"""Read-only runtime evidence for CL-5 D2 property/identity/binding instrument."""
from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.d2_operational import D2AgentInternalState, D2BindingProtocol, render_scientific_frame, verify_render_alignment


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenario", type=Path, default=PROJECT_ROOT / "scenarios/d2_properties.yaml")
    args = parser.parse_args()
    protocol = D2BindingProtocol(args.scenario)
    correct = {condition.condition_id: protocol.frame(condition.condition_id, protocol.correct_reports(condition.condition_id))
               for condition in protocol.CONDITIONS}
    left, right = protocol.correct_reports("baseline").reports
    swapped = protocol.frame("baseline", D2AgentInternalState((
        replace(left, position=right.position, property_signature=right.property_signature),
        replace(right, position=left.position, property_signature=left.property_signature),
    )))
    missing = protocol.frame("movement", D2AgentInternalState(protocol.correct_reports("movement").reports[:1]))
    baseline = correct["baseline"]
    with TemporaryDirectory(prefix="terrario-cl5-") as root:
        data_root = Path(root)
        audit = protocol.self_audit()
        result = {
            "D2_SELF_AUDIT_RUNTIME": True,
            "protocol_version": audit["schema_version"],
            "protocol_id": protocol.semantic_id,
            "data_root": str(data_root),
            "pressures": {key: "PASS" if not frame.observer_view.errors else "FAIL" for key, frame in correct.items()},
            "error_classifiers": {
                "PROPERTY_ERROR": "PASS" if "PROPERTY_ERROR" in swapped.observer_view.errors else "FAIL",
                "IDENTITY_ERROR": "PASS" if "IDENTITY_ERROR" in swapped.observer_view.errors else "FAIL",
                "IDENTITY_SWAP_ERROR": "PASS" if "IDENTITY_SWAP_ERROR" in swapped.observer_view.errors else "FAIL",
                "BINDING_ERROR": "PASS" if "BINDING_ERROR" in swapped.observer_view.errors else "FAIL",
            },
            "truth_isolation": "PASS" if set(baseline.agent_observation.__dict__) == {"channels", "mask", "agent_energy", "time_fraction"} else "FAIL",
            "tick_alignment": "PASS" if all(not verify_render_alignment(frame, render_scientific_frame(frame, protocol.semantic_id)) for frame in correct.values()) else "FAIL",
            "determinism": "PASS" if protocol.semantic_id == D2BindingProtocol(args.scenario).semantic_id else "FAIL",
            "agent_executed": False,
            "evidence_graph_writes": 0,
            "epistemic_scope": audit["classification"],
            "separation": {
                "world_truth_fields": list(baseline.world_truth.__dict__),
                "agent_observation_fields": list(baseline.agent_observation.__dict__),
                "agent_internal_state_fields": list(baseline.agent_internal_state.__dict__),
                "observer_view_fields": list(baseline.observer_view.__dict__),
            },
            "missing_report": {
                "diagnostics": list(missing.observer_view.errors),
                "not_evaluable_tracks": list(missing.observer_view.not_evaluable_tracks),
                "metrics": [item.__dict__ | {"rate": item.rate} for item in missing.observer_view.metrics],
            },
        }
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
