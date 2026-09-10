#!/usr/bin/env python
"""Build a content-addressed Theory of Intelligence snapshot and graph."""

import argparse
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from terrario.lab.read_model import LabReadModel
from terrario.lab.theory.ingestion import TheoryIngestor
from terrario.lab.theory.compiler import HypothesisCompiler
from terrario.lab.theory.snapshot import TheorySnapshotBuilder
from terrario.lab.theory.store import build_graph


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="/home/wis/Documentos/teoria de la inteligencia")
    parser.add_argument("--output", default="theory_snapshots")
    parser.add_argument("--project-root", default=".")
    args = parser.parse_args()
    project = Path(args.project_root).resolve()
    snapshot = TheorySnapshotBuilder().build(args.source, project / args.output)
    manifest = json.loads((snapshot / "snapshot_manifest.json").read_text())
    imported = TheoryIngestor(snapshot).ingest()
    lab = LabReadModel(project)
    graph = build_graph(manifest["snapshot_id"], imported, lab.experiments(), lab.runs())
    compiler = HypothesisCompiler()
    for hyperedge in imported.hyperedges:
        draft = compiler.compile(hyperedge)
        draft_id = graph.add_theory(draft)
        graph.link_theory(f"HyperedgeCandidateRecord:{hyperedge.id}", draft_id, "COMPILES_TO_REVIEW_DRAFT", hyperedge.provenance, "REVIEW_REQUIRED")
    graph.add_evidence("H-ADAPT-001", {
        "node_type": "ProjectHypothesis", "status": "UNTESTED_HYPOTHESIS",
        "linkage_status": "PROJECT_HYPOTHESIS_WITHOUT_COMPLETE_THEORY_LINKAGE",
        "provenance": str(project / "configs/h_adapt_001.yaml"),
    })
    for experiment in lab.experiments():
        if "h_adapt" in experiment.source.lower():
            graph.link_evidence("H-ADAPT-001", experiment.id, "PROJECT_HYPOTHESIS_HAS_EXPERIMENT", str(project / "configs/h_adapt_001.yaml"), "UNTESTED_HYPOTHESIS")
    graph.save(snapshot / "theory_graph.json")
    summary = {"snapshot_id": manifest["snapshot_id"], "snapshot_hash": manifest["snapshot_hash"],
               "missing": manifest["missing_artifacts"], **imported.counts(),
               "theory_nodes": len(graph.theory_nodes), "theory_edges": len(graph.theory_edges),
               "evidence_nodes": len(graph.evidence_nodes), "evidence_edges": len(graph.evidence_edges)}
    (snapshot / "ingestion_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__": main()
