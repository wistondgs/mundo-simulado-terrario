#!/usr/bin/env python3
"""Non-scientific integrity validator for a sealed A2b blind package."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
INPUT_HASHES = {
    "input/SPEC_PRIMITIVO_N2_A_REPLICA_CERRADA_v0_1.md": "f19324cd5039cc6f83176a77afe8ff23b07e817e1a1471e5e56d05823515a430",
    "input/TASK_A2B.txt": "245f922101df5cdfaaf5415efa9b4d87a2532c471c4e023ca9c2cfbf0133830a",
}
ALLOWLIST = {
    *INPUT_HASHES,
    "protocol/A2B_ENVIRONMENT.json",
    "protocol/A2B_ENVIRONMENT_CONTRACT.md",
    "protocol/A2B_EXECUTION_CONTRACT.json",
    "protocol/A2B_EXECUTION_CONTRACT.md",
    "protocol/A2B_SCIENTIFIC_FREEDOM_FREEZE.json",
    "protocol/A2B_SCIENTIFIC_FREEDOM_FREEZE.md",
    "protocol/A2B_SYNTHETIC_TEST_POLICY.md",
    "protocol/A2B_BLINDNESS_POLICY.md",
    "protocol/A2B_RAW_RESULT_QUARANTINE.md",
    "protocol/A2B_OEIS_RESOLUTION.md",
    "schemas/A2B_OUTPUT_MANIFEST.json",
    "schemas/resumen.schema.json",
    "schemas/A2B_RUN_MANIFEST_TEMPLATE.json",
    "blind_build/A2B_BLIND_BUILD_TASK.md",
    "blind_build/A2B_FRESH_SESSION_HANDOFF.md",
    "custody/BLIND_PACKAGE_SOURCE.json",
    "custody/BLIND_PACKAGE_SOURCE.md",
    "validate_blind_package.py",
}
CONTENT_EXEMPT = {
    "protocol/A2B_BLINDNESS_POLICY.md",
    "custody/BLIND_PACKAGE_SOURCE.json",
    "custody/BLIND_PACKAGE_SOURCE.md",
    "validate_blind_package.py",
}
FORBIDDEN_CONTENT = (
    "/home/wis/mundo simulado terrario",
    "A2B_GATE_A_TRANSITION_RULES",
    "EXP-04A",
    "entidad_transitoria",
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def canonical_self_hash(manifest: dict[str, object]) -> str:
    projection = dict(manifest)
    projection.pop("manifest_self_hash", None)
    files = []
    for entry in projection["files"]:
        normalized = dict(entry)
        if normalized.get("path") == "custody/BLIND_PACKAGE_SOURCE.json":
            normalized["sha256"] = "0" * 64
        files.append(normalized)
    projection["files"] = files
    payload = json.dumps(projection, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def main() -> int:
    errors: list[str] = []
    try:
        tracked = set(git("ls-files").splitlines())
        if tracked != ALLOWLIST:
            errors.append("tracked inventory differs from exact allowlist")
        if Path(git("rev-parse", "--show-toplevel")).resolve() != ROOT:
            errors.append("Git root is not the package root")
        if git("remote"):
            errors.append("blind package has a Git remote")
        if len(git("rev-list", "--parents", "-n", "1", "HEAD").split()) != 1 or git("rev-list", "--count", "HEAD") != "1":
            errors.append("delivery commit is not a single independent root commit")
        if git("status", "--porcelain"):
            errors.append("blind package worktree is not clean")
    except (OSError, subprocess.CalledProcessError) as exc:
        errors.append(f"independent Git validation failed: {exc}")

    if (ROOT / ".gitmodules").exists():
        errors.append("submodules are forbidden")
    for path in ROOT.rglob("*"):
        if ".git" in path.parts:
            continue
        if path.is_symlink():
            errors.append(f"symlink is forbidden: {path.relative_to(ROOT)}")

    for relative, expected in INPUT_HASHES.items():
        path = ROOT / relative
        if not path.is_file() or sha256(path) != expected:
            errors.append(f"sealed input mismatch: {relative}")

    try:
        manifest = json.loads((ROOT / "custody/BLIND_PACKAGE_SOURCE.json").read_text(encoding="utf-8"))
        entries = manifest["files"]
        by_path = {entry["path"]: entry for entry in entries}
        if set(by_path) != ALLOWLIST:
            errors.append("custody inventory differs from exact allowlist")
        declarations = ("no_additional_files", "gate_b_included", "a1_a2_results_included", "post_seal_references_included")
        if manifest["no_additional_files"] is not True or any(manifest[key] is not False for key in declarations[1:]):
            errors.append("custody exclusion declarations are not closed")
        if manifest["manifest_self_hash"]["sha256"] != canonical_self_hash(manifest):
            errors.append("custody manifest self-hash mismatch")
        for relative in ALLOWLIST - {"custody/BLIND_PACKAGE_SOURCE.json"}:
            entry = by_path.get(relative, {})
            path = ROOT / relative
            if not path.is_file() or entry.get("sha256") != sha256(path) or entry.get("size") != path.stat().st_size:
                errors.append(f"custody hash or size mismatch: {relative}")
        self_entry = by_path.get("custody/BLIND_PACKAGE_SOURCE.json", {})
        if self_entry.get("sha256") != manifest["manifest_self_hash"]["sha256"] or self_entry.get("hash_basis") != "manifest projection without manifest_self_hash; source entry sha256 zeroed":
            errors.append("custody self-entry is not defined correctly")
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        errors.append(f"invalid custody manifest: {exc}")

    for relative in ALLOWLIST - CONTENT_EXEMPT:
        text = (ROOT / relative).read_text(encoding="utf-8")
        if any(marker in text for marker in FORBIDDEN_CONTENT):
            errors.append(f"forbidden historical path in: {relative}")

    for schema_path in ("schemas/resumen.schema.json", "schemas/A2B_OUTPUT_MANIFEST.json", "schemas/A2B_RUN_MANIFEST_TEMPLATE.json"):
        try:
            json.loads((ROOT / schema_path).read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON: {schema_path}: {exc}")

    print(json.dumps({"validator": "A2B_BLIND_PACKAGE", "pass": not errors, "errors": errors}, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
