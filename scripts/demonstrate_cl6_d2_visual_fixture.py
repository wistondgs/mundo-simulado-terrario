#!/usr/bin/env python3
"""Emit deterministic runtime evidence for the canonical CL-6 D2 fixture."""
from __future__ import annotations

import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.d2_visual_fixture import build_d2_visual_validation_fixture, validate_visual_fixture_payload


def main() -> None:
    fixture = build_d2_visual_validation_fixture(PROJECT_ROOT / "scenarios" / "d2_properties.yaml")
    payload = fixture.payload()
    validate_visual_fixture_payload(payload)
    frames = {frame["phase"]: frame for frame in payload["frames"]}
    print(json.dumps({
        "CL6_D2_VISUAL_DEMONSTRATION": True,
        "fixture_id": payload["fixture_id"], "fixture_version": payload["fixture_version"],
        "protocol_version": payload["protocol_version"], "semantic_hash": payload["semantic_hash"],
        "frames": {phase: {"tick": frame["tick"], "errors": frame["observer_view"]["errors"]}
                   for phase, frame in frames.items()},
        "agent_executed": payload["agent_executed"], "evidence_graph_writes": payload["evidence_graph_writes"],
        "tick_alignment": all(frame["tick"] == frame["projection_tick"] == frame["evaluation_tick"] for frame in payload["frames"]),
        "view_separation": all(frame["agent_observation"]["availability"] == "NOT_APPLICABLE" and frame["cognitive_state"]["availability"] == "NOT_APPLICABLE" for frame in payload["frames"]),
        "binding_error_scope": frames["BINDING_ERROR"]["observer_view"]["scope"],
        "manual_inspection_available": True,
    }, indent=2))


if __name__ == "__main__":
    main()
