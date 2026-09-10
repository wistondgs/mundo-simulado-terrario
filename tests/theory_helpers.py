from pathlib import Path

from terrario.lab.theory.ingestion import TheoryIngestor
from terrario.lab.theory.store import TheoryGraphStore


def snapshot_dir() -> Path:
    return next(Path("theory_snapshots").glob("*/snapshot_manifest.json")).parent


def theory_import(): return TheoryIngestor(snapshot_dir()).ingest()
def theory_graph(): return TheoryGraphStore.load(snapshot_dir() / "theory_graph.json")
