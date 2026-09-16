#!/usr/bin/env python3
"""Read-only runtime evidence for CL-3: composed hypergraph to hypothesis draft."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.hypergraph.theory_operational import (
    BindingRequirement, CompositionRule, RoleCompatibility, compose, load_bindings,
    materialize, provenance_forward,
)
from terrario.lab.theory.compiler import HypothesisCompiler, OperationalHypothesisCompiler
from terrario.lab.theory.ingestion import TheoryIngestor
from terrario.lab.theory.models import HypothesisDraft


def _rejects(operation) -> str:
    try:
        operation()
    except (PermissionError, ValueError) as exc:
        return f"{type(exc).__name__}: {exc}"
    raise AssertionError("negative case was accepted")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--primary-source-root", type=Path, required=True)
    args = parser.parse_args()

    imported = TheoryIngestor(args.snapshot, include_operational_evidence=True).ingest()
    evidence = args.snapshot.parent.parent / "theory_operational_artifacts" / args.snapshot.name

    def edge(candidate_id: str):
        candidate = next(item for item in imported.hyperedges if item.id == candidate_id)
        return materialize(
            candidate,
            load_bindings(evidence / "HYPEREDGE_ROLE_BINDINGS_v0.2.csv", candidate_id),
            imported,
            primary_source_root=args.primary_source_root,
        )

    edge02, edge08 = edge("HYPERCAND-02"), edge("HYPERCAND-08")
    derived = compose(
        edge02, edge08,
        compatibility=(RoleCompatibility(
            BindingRequirement("agent", "agent"),
            BindingRequirement("actor", "action_sequence_proposer"),
            "both source-backed roles explicitly produce actions",
        ),),
        rule=CompositionRule(
            "ACTION_PRODUCING_AGENT_REFINEMENT", "v1",
            "architectural actor refines the formal agent action-producing role",
        ),
        provenance="role-compatible structural refinement; TI-0071 + TI-0077",
    )
    index = {item.semantic_id: item for item in (edge02, edge08, derived)}
    compiler = OperationalHypothesisCompiler()
    draft = compiler.compile(derived, index)
    reloaded = HypothesisDraft.from_payload(json.loads(json.dumps(draft.payload())))

    print(json.dumps({
        "input": {
            "source_backed_candidates": [edge02.candidate_id, edge08.candidate_id],
            "source_backed_hyperedges": [edge02.semantic_id, edge08.semantic_id],
            "derived_hyperedge": derived.semantic_id,
            "parent_hyperedges": list(derived.parent_semantic_ids),
        },
        "hypothesis": {
            "draft_id": draft.id,
            "semantic_id": draft.semantic_id,
            "epistemic_status": draft.epistemic_status,
            "composition_path": list(draft.composition_path),
            "derivation_rule": draft.derivation_rule,
            "premises": [item.__dict__ for item in draft.premises],
            "prediction": draft.prediction,
            "testability": draft.testability,
            "novelty_evidence": draft.novelty_evidence,
        },
        "provenance_forward": sorted({
            (item.claim_id, item.source_record_id, item.source_locator)
            for item in provenance_forward(derived, index)
        }),
        "serialize_reload": {
            "semantic_identity_preserved": reloaded.semantic_id == draft.semantic_id,
            "epistemic_status_preserved": reloaded.epistemic_status == draft.epistemic_status,
        },
        "negative_cases": {
            "SOURCE_BACKED_TO_HYPOTHESIS": _rejects(lambda: compiler.compile(edge02, index)),
            "MISSING_PARENT": _rejects(lambda: compiler.compile(derived, {edge02.semantic_id: edge02})),
            "AUTO_ACTIVATION": _rejects(lambda: HypothesisCompiler().activate(draft)),
        },
    }, indent=2))


if __name__ == "__main__":
    main()
