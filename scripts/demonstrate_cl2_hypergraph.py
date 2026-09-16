#!/usr/bin/env python3
"""Read-only runtime evidence for CL-2 operational theory hypergraphs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.hypergraph.theory_operational import (
    BindingRequirement, CompositionRule, RoleCompatibility, TheoryHyperedgeBinding,
    TheoryOperationalHyperedge, compose, load_bindings, materialize,
    provenance_forward, provenance_reverse, query,
)
from terrario.lab.theory.ingestion import TheoryIngestor


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--primary-source-root", type=Path, required=True)
    args = parser.parse_args()

    imported = TheoryIngestor(args.snapshot, include_operational_evidence=True).ingest()
    evidence = args.snapshot.parent.parent / "theory_operational_artifacts" / args.snapshot.name

    def edge(candidate_id: str):
        candidate = next(item for item in imported.hyperedges if item.id == candidate_id)
        bindings = load_bindings(evidence / "HYPEREDGE_ROLE_BINDINGS_v0.2.csv", candidate_id)
        return materialize(candidate, bindings, imported, primary_source_root=args.primary_source_root)

    edge02, edge08 = edge("HYPERCAND-02"), edge("HYPERCAND-08")
    rule = CompositionRule(
        "ACTION_PRODUCING_AGENT_REFINEMENT", "v1",
        "architectural actor refines the formal action-producing agent role",
    )
    derived = compose(
        edge02, edge08,
        compatibility=(RoleCompatibility(
            BindingRequirement("agent", "agent"),
            BindingRequirement("actor", "action_sequence_proposer"),
            "both roles are explicitly action-producing in their primary claims",
        ),),
        rule=rule,
        provenance="role-compatible structural refinement; TI-0071 + TI-0077",
    )
    index = {item.semantic_id: item for item in (edge02, edge08, derived)}
    reloaded = TheoryOperationalHyperedge.from_payload(json.loads(json.dumps(derived.payload())))

    def rejects(callable_):
        try:
            callable_()
        except ValueError as exc:
            return str(exc)
        raise AssertionError("negative case was accepted")

    negative_one = rejects(lambda: materialize(
        next(item for item in imported.hyperedges if item.id == "HYPERCAND-01"), (), imported,
    ))
    broken = list(load_bindings(evidence / "HYPEREDGE_ROLE_BINDINGS_v0.2.csv", "HYPERCAND-08"))
    broken[0] = TheoryHyperedgeBinding(**{**broken[0].__dict__, "source_locator": "§broken"})
    negative_two = rejects(lambda: materialize(
        next(item for item in imported.hyperedges if item.id == "HYPERCAND-08"), broken, imported,
        primary_source_root=args.primary_source_root,
    ))
    negative_three = rejects(lambda: compose(
        edge02, edge08,
        compatibility=(RoleCompatibility(BindingRequirement("goal", "agent"), BindingRequirement("actor", "action_sequence_proposer"), "invalid role bridge"),),
        rule=rule, provenance="deliberately incompatible",
    ))

    print(json.dumps({
        "input": [edge02.candidate_id, edge08.candidate_id],
        "materialized": [edge02.semantic_id, edge08.semantic_id],
        "joint_query": [item.semantic_id for item in query(
            (edge02,), requirements=(BindingRequirement("agent", "agent"), BindingRequirement("goal", "goal")),
            status=edge02.epistemic_status, provenance="HYPEREDGE_CANDIDATES_v0.2.md",
        )],
        "composition": {"semantic_id": derived.semantic_id, "rule": derived.composition_rule,
                        "parents": derived.parent_semantic_ids, "corroboration": derived.corroboration_status},
        "provenance_forward": sorted({(item.claim_id, item.source_record_id) for item in provenance_forward(derived, index)}),
        "provenance_reverse": [item.semantic_id for item in provenance_reverse("CLM-H08-006", (edge02, edge08, derived), index)],
        "serialize_reload": {"semantic_identity_preserved": reloaded.semantic_id == derived.semantic_id,
                              "epistemic_status_preserved": reloaded.epistemic_status.value == derived.epistemic_status.value},
        "negatives": {"NEG-01": negative_one, "NEG-02": negative_two, "NEG-03": negative_three},
    }, indent=2))


if __name__ == "__main__":
    main()
