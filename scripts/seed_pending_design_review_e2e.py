"""Seed ONE undecided EXPERIMENT_DESIGN review request for the E2E review-center test.

`seed_scientific_live_e2e.py` decides every review it opens, so it leaves no
pending card for the ceremony test to act on.  That test used to assert against
a review id and design hash that exist only in the live `.terrario`: it passed
only while the suite ran against the scientist's real root, and it typed into a
real pending human-review form.  This seeds its own subject instead.

Prints `{"review_id", "artifact_hash", "artifact_version_id"}` as JSON.
"""
from __future__ import annotations

import json
import secrets
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.api import LabAPI
from tests.test_lab_02c_api import experiment_payload


def main() -> None:
    if len(sys.argv) < 2:
        raise SystemExit("usage: seed_pending_design_review_e2e.py <absolute data root> "
                         "-- refusing to default to the live .terrario")
    data_root = Path(sys.argv[1])
    if not data_root.is_absolute():
        raise SystemExit("data root must be absolute; refusing an implicit root escape")
    if data_root.resolve() == (PROJECT_ROOT / ".terrario").resolve():
        raise SystemExit("refusing to seed E2E fixtures into the live scientific data root")

    api = LabAPI(PROJECT_ROOT, data_root=data_root)
    tag = secrets.token_hex(6)
    offset = int(tag[:6], 16) % 100000
    payload = experiment_payload(draft_id=f"ED-REVIEW-{tag}", agent_ids=["A4"], controls=[],
                                 world_seeds=[500000 + offset], agent_seeds=[700000 + offset])
    status, experiment = api.dispatch("POST", "/api/experiment-drafts", payload)
    assert status == 201, experiment
    status, request = api.dispatch("POST", "/api/v1/review-requests", {
        "artifact_version_id": experiment["version_id"],
        "reason": "revisar el diseño exacto antes de decidir"})
    assert status == 201, request
    # Deliberately NOT decided: the browser test asserts the ceremony gate on a
    # pending card and must be the only thing that touches it.
    print(json.dumps({"review_id": request["data"]["review_id"],
                      "artifact_hash": experiment["scientific_hash"],
                      "artifact_version_id": experiment["version_id"]}))


if __name__ == "__main__":
    main()
