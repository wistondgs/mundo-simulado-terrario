"""Content-addressed, immutable working snapshots of structured artifacts."""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path


PARSER_VERSION = "theory-ingestion/1"
PRIORITY_ARTIFACTS = (
    "SOURCE_PROVENANCE_v0.3.csv", "SOURCE_SAMPLE_v0.1.md",
    "CLAIMS_RELATIONS_v0.1.csv", "CLAIMS_RELATIONS_PATCH_v0.3.csv",
    "CONCEPTS_RAW_PATCH_v0.3.csv", "CONCEPT_CANONICAL_MAP_v0.2.csv",
    "RELATIONS_AUDIT_v0.2.csv", "HYPEREDGE_CANDIDATES_v0.2.md",
    "CONCEPT_CONFLICTS_v0.1.md", "AMBIGUITIES_v0.2.md", "ONTOLOGY_v0.2.md",
    "COVERAGE_MATRIX_v0.3.csv", "CONCEPT_COVERAGE_AUDIT_v0.3.csv",
    "CORPUS_EXPANSION_INVENTORY_v0.3.csv", "CORPUS_EXPANSION_REPORT_v0.3.md",
    "CORPUS_GAPS_v0.3.md", "DEVELOPMENTAL_COGNITION_PATCH_v0.1.md",
    "CORPUS_INTEGRITY_PATCH_v0.1.md",
)
SUPPLEMENTAL_ARTIFACTS = (
    "CONCEPTS_RAW_v0.1.csv", "COVERAGE_MATRIX_v0.2.csv", "ONTOLOGY_v0.1.md",
)


def artifact_version(name: str) -> str:
    found = re.search(r"_v(\d+\.\d+)", name, re.I)
    return f"v{found.group(1)}" if found else "UNVERSIONED"


def artifact_type(name: str) -> str:
    upper = name.upper()
    for token in ("SOURCE", "CLAIM", "CONCEPT", "RELATION", "HYPEREDGE", "AMBIGUIT", "ONTOLOGY", "COVERAGE", "INTEGRITY", "CORPUS"):
        if token in upper: return token
    return "STRUCTURED_DERIVED_ARTIFACT"


class TheorySnapshotBuilder:
    def discover(self, source_dir: str | Path, extra_roots: tuple[str | Path, ...] = ()) -> tuple[dict[str, Path], tuple[str, ...]]:
        roots = (Path(source_dir), *(Path(p) for p in extra_roots))
        found = {}
        for name in (*PRIORITY_ARTIFACTS, *SUPPLEMENTAL_ARTIFACTS):
            match = next((root / name for root in roots if (root / name).is_file()), None)
            if match: found[name] = match.resolve()
        return found, tuple(name for name in PRIORITY_ARTIFACTS if name not in found)

    def build(self, source_dir: str | Path, destination: str | Path, extra_roots: tuple[str | Path, ...] = ()) -> Path:
        found, missing = self.discover(source_dir, extra_roots)
        entries = []
        for name, path in sorted(found.items()):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            entries.append({"filename": name, "sha256": digest, "artifact_version": artifact_version(name),
                            "artifact_type": artifact_type(name), "source_path": str(path),
                            "ingestion_status": "READY", "parser_version": PARSER_VERSION})
        identity = hashlib.sha256(json.dumps(entries, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        snapshot_id = f"theory-{identity[:16]}"
        target = Path(destination) / snapshot_id
        if target.exists():
            manifest = json.loads((target / "snapshot_manifest.json").read_text())
            if manifest["snapshot_hash"] != identity: raise ValueError("snapshot identity collision")
            return target
        target.mkdir(parents=True)
        for name, source in found.items(): shutil.copyfile(source, target / name)
        manifest = {"snapshot_id": snapshot_id, "snapshot_hash": identity, "parser_version": PARSER_VERSION,
                    "artifacts": entries, "missing_artifacts": list(missing), "immutable": True}
        (target / "snapshot_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        (target / "MISSING_THEORY_ARTIFACTS.json").write_text(json.dumps({"missing": list(missing)}, indent=2), encoding="utf-8")
        return target
