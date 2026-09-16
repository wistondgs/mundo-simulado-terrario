from pathlib import Path
import os

from terrario.lab.theory.ingestion import TheoryIngestor
from terrario.lab.theory.store import TheoryGraphStore


def snapshot_dir() -> Path:
    return next(Path("theory_snapshots").glob("*/snapshot_manifest.json")).parent


def theory_import(): return TheoryIngestor(snapshot_dir()).ingest()
def theory_graph(): return TheoryGraphStore.load(snapshot_dir() / "theory_graph.json")


def primary_corpus_root() -> Path:
    """Resolve the verified physical corpus without baking in a WSL mount."""
    configured = os.environ.get("TERRARIO_PRIMARY_SOURCE_ROOT")
    candidates = ((Path(configured),) if configured else ()) + (
        Path.home() / "Documentos" / "teoria de la inteligencia",
        Path.home() / "Documents" / "teoria de la inteligencia",
    )
    marker = Path("09_Inteligencia_Formal_AGI/TI-0077_Yann_LeCun_A_Path_Towards_Autonomous_Machine_Intelligence.pdf")
    for candidate in candidates:
        if (candidate / marker).is_file():
            return candidate
    raise RuntimeError("verified primary corpus unavailable; set TERRARIO_PRIMARY_SOURCE_ROOT")
