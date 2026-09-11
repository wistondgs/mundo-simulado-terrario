"""Index historical manifests/results without rewriting or copying them."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from terrario.lab.persistence import ArtifactRepository
from terrario.lab.persistence.history import HistoricalArtifactIndexer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".")
    parser.add_argument("--data-root")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    repository = ArtifactRepository(Path(args.data_root).resolve() if args.data_root else root / ".terrario")
    result = HistoricalArtifactIndexer(root, repository).index()
    print(json.dumps({
        "classification": "READ_ONLY_HISTORICAL_INDEX",
        "copy_performed": False,
        "theory_snapshots": len(result.theory_snapshots),
        "scientific_reviews": len(result.scientific_reviews),
        "historical_runs": len(result.historical_runs),
        "database_integrity": repository.integrity_check(),
    }, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
