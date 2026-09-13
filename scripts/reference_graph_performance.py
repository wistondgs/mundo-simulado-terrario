"""Performance characterization for the scientific reference graph.

Builds synthetic corpora at stepped scales and measures bulk import, DOI
lookup, construct query, neighborhood traversal, snapshot creation,
verification, and snapshot diff. Reports real measurements only; it makes no
scalability claim. Run directly:

    .venv/bin/python scripts/reference_graph_performance.py
"""
from __future__ import annotations

import hashlib
import json
import statistics
import tempfile
import time
from pathlib import Path

from terrario.lab.persistence import ArtifactRepository
from terrario.lab.referencegraph.import_corpus import CorpusImporter
from terrario.lab.referencegraph.queries import ReferenceGraphQueries
from terrario.lab.referencegraph.service import ReferenceGraphService


def build_corpus(root: Path, count: int) -> Path:
    corpus = root / f"corpus_{count}"
    for sub in ("manifest", "metadata", "bibliography", "provenance", "docs"):
        (corpus / sub).mkdir(parents=True, exist_ok=True)
    manifest_path = corpus / "manifest" / "CORPUS_MANIFEST.jsonl"
    records_path = corpus / "metadata" / "REFERENCE_RECORDS.jsonl"
    bib_path = corpus / "bibliography" / "references.csv"
    constructs = ["OBJECT_PERSISTENCE", "FEATURE_BINDING", "OCCLUSION", "TRANSFER",
                  "INDIVIDUATION", "PROPERTY_DISCRIMINATION"]
    with manifest_path.open("w") as man, records_path.open("w") as rec, bib_path.open("w") as bib:
        bib.write("reference_id,bibtex_key,title,authors,year,venue,doi,url\n")
        for index in range(count):
            ref_id = f"PERF-REF-{index:05d}"
            doc_id = f"{ref_id}-DOC-001"
            data = b"%PDF-1.4\n" + (b"x" * 200) + str(index).encode()
            sha = hashlib.sha256(data).hexdigest()
            rel = f"docs/{ref_id}.pdf"
            (corpus / rel).write_bytes(data)
            construct = constructs[index % len(constructs)]
            man.write(json.dumps({
                "document_id": doc_id, "reference_id": ref_id, "sha256": sha,
                "local_relative_path": rel, "mime_type": "application/pdf",
                "file_size_bytes": str(len(data)), "version_type": "PREPRINT",
                "doi": f"10.1234/perf.{index}", "title": f"Perf Paper {index}",
                "authors": f"Author {index % 100}", "year": str(1990 + index % 35),
                "venue": "arXiv", "license": "arXiv", "access_status": "ACQUIRED",
                "terrario_levels": "D2", "d2_constructs": construct,
                "experimental_paradigm": f"paradigm {index % 20}", "discipline": "psychology",
                "provenance": "synthetic perf"}) + "\n")
            rec.write(json.dumps({
                "reference_id": ref_id, "reference_type": "benchmark paper",
                "title": f"Perf Paper {index}", "authors": f"Author {index % 100}",
                "year": str(1990 + index % 35), "constructs": [construct],
                "experimental_paradigms": [f"paradigm {index % 20}"],
                "design_principles": [], "known_limitations": [f"limitation {index}"],
                "paper_document_ids": [doc_id], "terrario_levels": ["D2"], "d2_relevance": "",
                "discipline": "psychology", "code_url": "UNKNOWN",
                "verification_status": "ACQUIRED"}) + "\n")
            bib.write(f"{ref_id},key{index},Perf Paper {index},Author {index % 100},"
                      f"{1990 + index % 35},arXiv,10.1234/perf.{index},http://x\n")
    for name, header, row in (
        ("D2_PROTOCOL_EXTRACTION.csv", "reference_id,extraction_status,subjects_or_agents\n", ""),
        ("REFERENCE_LIMITATIONS.csv", "reference_id,limitation_id,limitation_type,limitation,source_basis,notes\n", ""),
        ("DESIGN_PRINCIPLES.csv", "reference_id,principle_id,source_basis,principle,terrario_possible_use,adaptation_type,limitations\n", ""),
        ("VERSION_RELATIONSHIPS.csv", "source_document_id,relation_type,target_document_id,notes\n", ""),
    ):
        (corpus / "metadata" / name).write_text(header + row, encoding="utf-8")
    return corpus


def _time(fn, repeat=1):
    samples = []
    result = None
    for _ in range(repeat):
        start = time.perf_counter()
        result = fn()
        samples.append(time.perf_counter() - start)
    return result, statistics.median(samples)


def characterize(scale: int) -> dict:
    root = Path(tempfile.mkdtemp())
    corpus = build_corpus(root, scale)
    artifacts = ArtifactRepository(root / ".terrario")
    service = ReferenceGraphService(artifacts)
    queries = ReferenceGraphQueries(artifacts)
    importer = CorpusImporter(artifacts)

    _, import_s = _time(lambda: importer.import_corpus(corpus))
    counts = service.counts()

    _, doi_s = _time(lambda: queries.find_references(doi="10.1234/perf.5000"), repeat=20)
    _, construct_s = _time(lambda: queries.find_by_construct("OCCLUSION"), repeat=20)
    with artifacts._connect() as connection:
        center = connection.execute("SELECT node_id FROM ref_nodes LIMIT 1").fetchone()["node_id"]
    _, neighborhood_s = _time(lambda: queries.get_neighborhood(center, depth=2), repeat=20)
    _, snapshot_s = _time(lambda: service.create_snapshot("perf"))
    _, verify_s = _time(lambda: service.verify())
    latest = service.repository.latest_snapshot()
    second = service.create_snapshot("perf-2")
    _, diff_s = _time(lambda: queries.snapshot_diff(latest["snapshot_id"], second.snapshot_id), repeat=20)

    return {"scale": scale, "counts": counts,
            "bulk_import_s": round(import_s, 3),
            "doi_lookup_ms": round(doi_s * 1000, 3),
            "construct_query_ms": round(construct_s * 1000, 3),
            "neighborhood_ms": round(neighborhood_s * 1000, 3),
            "snapshot_create_s": round(snapshot_s, 3),
            "verify_s": round(verify_s, 3),
            "snapshot_diff_ms": round(diff_s * 1000, 3)}


if __name__ == "__main__":
    results = [characterize(scale) for scale in (10_000, 25_000)]
    print(json.dumps(results, indent=2))
