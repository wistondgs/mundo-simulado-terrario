#!/usr/bin/env python3
"""Static validator for A2b-PREP; it never imports or computes A2b science."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
EXPECTED_HASHES = {
    "input/SPEC_PRIMITIVO_N2_A_REPLICA_CERRADA_v0_1.md": "f19324cd5039cc6f83176a77afe8ff23b07e817e1a1471e5e56d05823515a430",
    "input/TASK_A2B.txt": "245f922101df5cdfaaf5415efa9b4d87a2532c471c4e023ca9c2cfbf0133830a",
}
REQUIRED_FILES = set(EXPECTED_HASHES) | {
    "custody/A2B_INPUT_PROVENANCE.json",
    "custody/A2B_INPUT_PROVENANCE.md",
    "protocol/A2B_SCIENTIFIC_FREEDOM_FREEZE.json",
    "protocol/A2B_SCIENTIFIC_FREEDOM_FREEZE.md",
    "protocol/A2B_ENVIRONMENT.json",
    "protocol/A2B_ENVIRONMENT_CONTRACT.md",
    "protocol/A2B_EXECUTION_CONTRACT.json",
    "protocol/A2B_EXECUTION_CONTRACT.md",
    "protocol/A2B_RAW_RESULT_QUARANTINE.md",
    "protocol/A2B_BLINDNESS_POLICY.md",
    "protocol/A2B_SYNTHETIC_TEST_POLICY.md",
    "protocol/A2B_GATE_A_TRANSITION_RULES.md",
    "schemas/A2B_OUTPUT_MANIFEST.json",
    "schemas/A2B_RUN_MANIFEST_TEMPLATE.json",
    "blind_build/A2B_BLIND_BUILD_TASK.md",
    "blind_build/A2B_FRESH_SESSION_HANDOFF.md",
}
EXPECTED_OUTPUTS = {
    "por_sistema.jsonl",
    "resumen.json",
    "ambiguity_register.jsonl",
    "runtime_environment.json",
    "execution_manifest.json",
    "stdout.log",
    "stderr.log",
    "raw_hashes.sha256",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_json(relative: str) -> object:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


def main() -> int:
    errors: list[str] = []
    for relative in sorted(REQUIRED_FILES):
        if not (ROOT / relative).is_file():
            errors.append(f"missing required PREP artifact: {relative}")

    for relative, expected in EXPECTED_HASHES.items():
        path = ROOT / relative
        if path.is_file() and sha256(path) != expected:
            errors.append(f"input hash mismatch: {relative}")

    try:
        provenance = load_json("custody/A2B_INPUT_PROVENANCE.json")
        if provenance["repository_parent"]["classification"] != "REPOSITORY_PARENT_ONLY":
            errors.append("repository parent is not explicitly prospective-only")
        if not provenance["repository_parent"]["not_historical_a2b_base"]:
            errors.append("manifest permits a historical-base claim")
        if {item["sha256"] for item in provenance["inputs"]} != set(EXPECTED_HASHES.values()):
            errors.append("provenance input hashes are incomplete")
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append(f"invalid input provenance manifest: {exc}")

    try:
        environment = load_json("protocol/A2B_ENVIRONMENT.json")
        if environment["network"] != "disabled" or environment["runtime"]["exact_version"] != "3.12.3":
            errors.append("environment contract is not closed")
        if environment["dependencies"]["allowed"] != ["Python 3.12 standard library"]:
            errors.append("dependency surface is not closed")
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append(f"invalid environment contract: {exc}")

    try:
        execution = load_json("protocol/A2B_EXECUTION_CONTRACT.json")
        if execution["scientific_invocations_per_run_id"] != 1 or execution["interactive_input"]:
            errors.append("execution interface is not fixed")
        if execution["command"][-2:] != ["--output", "raw_results"]:
            errors.append("execution command does not target raw_results")
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append(f"invalid execution contract: {exc}")

    try:
        output_manifest = load_json("schemas/A2B_OUTPUT_MANIFEST.json")
        artifacts = output_manifest["artifacts"]
        paths = {item["path"] for item in artifacts}
        if paths != EXPECTED_OUTPUTS:
            errors.append("output manifest is not complete and closed")
        if any(not item["required"] for item in artifacts):
            errors.append("a raw output artifact is discretionary")
        raw_hash = next((item for item in artifacts if item["path"] == "raw_hashes.sha256"), None)
        if raw_hash is None or raw_hash["checksum"]:
            errors.append("raw hash manifest has an invalid circularity rule")
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append(f"invalid output manifest: {exc}")

    try:
        run_template = load_json("schemas/A2B_RUN_MANIFEST_TEMPLATE.json")
        required_at_seal = set(run_template["required_at_raw_seal"])
        required = {"prep_protocol_commit", "future_executable_commit", "network_disabled", "result_artifact_hashes", "executor_session_id"}
        if not required.issubset(required_at_seal):
            errors.append("run manifest lacks required custody fields")
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append(f"invalid run manifest template: {exc}")

    if (ROOT / "blind_build/src/run_a2b.py").exists():
        errors.append("scientific solver exists in contaminated PREP context")
    if (ROOT / "raw_results").exists():
        errors.append("scientific raw-results directory exists during PREP")

    result = {"validator": "A2B_PREP_STATIC", "pass": not errors, "errors": errors}
    print(json.dumps(result, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
