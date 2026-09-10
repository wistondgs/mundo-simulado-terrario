#!/usr/bin/env python
"""Browser-independent UI contract harness for environments without Chromium."""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from terrario.lab.api import LabAPI


def main():
    root = Path(__file__).resolve().parents[1]
    html = (root / "terrario/lab/static/index.html").read_text(encoding="utf-8")
    js = (root / "terrario/lab/static/app.js").read_text(encoding="utf-8")
    api = LabAPI(root)
    checks = {
        "lab_home": all(token in html for token in ("homeStats", "BLOCKED_CUDA", "Theory snapshot")),
        "experiment_browser": "experimentRows" in html,
        "run_dashboard": all(token in html for token in ("timeline", "metricStrip")),
        "world_viewer": all(token in html for token in ("AGENT VIEW", "OBSERVER VIEW", "worldCanvas")),
        "offline_replay": all(token in js for token in ("causal_change", "forensic", "state.step")),
        "hypergraph_explorer": all(token in html for token in ("graphCanvas", "nodeDetail", "findPaths")),
        "theory_api": api.dispatch("GET", "/api/theory/summary")[0] == 200,
        "graph_api": api.dispatch("GET", "/api/hypergraph")[0] == 200,
        "agent_observer_endpoints_distinct": "agent-view" in js and "observer-view" in js,
    }
    report = {"mode": "MANUAL_HARNESS_NO_BROWSER", "checks": checks, "status": "PASS" if all(checks.values()) else "FAIL",
              "manual_viewports": ["1440x900", "390x844"], "visual_review_required": True}
    print(json.dumps(report, indent=2))
    raise SystemExit(0 if report["status"] == "PASS" else 1)


if __name__ == "__main__": main()
