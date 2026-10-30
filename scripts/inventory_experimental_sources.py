"""Emit a metadata-only, read-only inventory of experimental source roots.

The tool never opens SQLite databases, JSONL payloads, checkpoints, or source
artifacts for content. It only uses stat metadata and filenames, so it is safe
to run against a live laboratory tree. Output goes to stdout unless --output is
explicitly supplied; --output refuses to overwrite an existing file.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path


DEFAULT_ROOTS = ("runs", ".terrario", "experiments", "artifacts", "research")


def classify(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".sqlite", ".db", ".wal", ".shm"}:
        return "database_or_sidecar"
    if suffix == ".jsonl":
        return "event_or_trace_jsonl"
    if suffix == ".json":
        return "structured_json"
    if suffix in {".pt", ".pth", ".ckpt", ".bin"}:
        return "checkpoint_or_binary"
    return "other"


def inventory(root: Path, include_hashes: bool) -> dict:
    files = []
    classes: Counter[str] = Counter()
    total = 0
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        stat = path.stat()
        relative = path.relative_to(root).as_posix()
        record = {"path": relative, "bytes": stat.st_size, "class": classify(path)}
        if include_hashes:
            digest = hashlib.sha256()
            with path.open("rb") as source:
                for chunk in iter(lambda: source.read(1024 * 1024), b""):
                    digest.update(chunk)
            record["sha256"] = digest.hexdigest()
        files.append(record)
        classes[record["class"]] += 1
        total += stat.st_size
    return {"root": root.as_posix(), "files": len(files), "bytes": total,
            "by_class": dict(sorted(classes.items())), "entries": files}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--source", action="append", dest="sources")
    parser.add_argument("--hash", action="store_true", dest="hashes")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    base = args.root.resolve()
    names = tuple(args.sources or DEFAULT_ROOTS)
    result = {"schema": "terrario.experimental-knowledge/metadata-inventory/v1",
              "mode": "read_only_metadata", "roots": []}
    for name in names:
        target = (base / name).resolve()
        if target.exists() and target.is_dir() and base in (set(target.parents) | {base}):
            result["roots"].append(inventory(target, args.hashes))
        else:
            result["roots"].append({"root": name, "status": "absent_or_outside_root"})
    payload = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        if args.output.exists():
            raise SystemExit(f"refusing to overwrite {args.output}")
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
