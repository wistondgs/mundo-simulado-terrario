"""Read-only indexing of historical Terrario artifacts as immutable references."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from terrario.lab.persistence.store import ArtifactRepository, ArtifactVersionRecord


@dataclass(frozen=True)
class HistoricalIndexResult:
    theory_snapshots: tuple[ArtifactVersionRecord, ...]
    scientific_reviews: tuple[ArtifactVersionRecord, ...]
    historical_runs: tuple[ArtifactVersionRecord, ...]


class HistoricalArtifactIndexer:
    """Index existing files by path/hash; never copy, edit, or classify them as evidence."""

    SCHEMA_VERSION = "terrario.external-artifact-reference/v1"

    def __init__(self, project_root: str | Path, repository: ArtifactRepository):
        self.project_root = Path(project_root).resolve()
        self.repository = repository

    def index(self) -> HistoricalIndexResult:
        theory = tuple(
            self._index_file(path, "TheorySnapshotRef", "EXTERNAL_IMMUTABLE_THEORY_SNAPSHOT")
            for path in sorted((self.project_root / "theory_snapshots").glob("*/snapshot_manifest.json"))
        )
        reviews = tuple(
            self._index_file(path, "ScientificReviewRef", "EXTERNAL_IMMUTABLE_SCIENTIFIC_REVIEW")
            for path in sorted((self.project_root / "scientific_reviews").glob("*/review_manifest.json"))
        )
        runs = tuple(
            self._index_file(path, "HistoricalRunRef", "LEGACY_UNVERIFIED_RUN_REFERENCE")
            for path in sorted((self.project_root / "runs").glob("**/*_results.json"))
        )
        return HistoricalIndexResult(theory, reviews, runs)

    def _index_file(self, path: Path, kind: str, classification: str) -> ArtifactVersionRecord:
        resolved = path.resolve()
        if self.project_root not in resolved.parents:
            raise ValueError(f"historical path escapes project root: {path}")
        digest = self._file_hash(resolved)
        relative = resolved.relative_to(self.project_root).as_posix()
        payload = {
            "schema_version": self.SCHEMA_VERSION,
            "relative_path": relative,
            "sha256": digest,
            "size_bytes": resolved.stat().st_size,
            "immutable_external_reference": True,
            "copy_performed": False,
            "scientific_evidence_published": False,
        }
        identity = hashlib.sha256(f"{kind}:{relative}".encode("utf-8")).hexdigest()[:20]
        return self.repository.create_artifact(
            kind, payload, self.SCHEMA_VERSION, artifact_id=f"external-{kind.casefold()}-{identity}",
            classification=classification, created_by="historical-indexer",
            reason="read-only historical reference indexing", initial_state="INDEXED_REFERENCE",
            sealed=True, deduplicate=True,
        )

    @staticmethod
    def _file_hash(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as handle:
            for block in iter(lambda: handle.read(1 << 20), b""):
                digest.update(block)
        return digest.hexdigest()
