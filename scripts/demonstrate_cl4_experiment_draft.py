#!/usr/bin/env python3
"""Read-only runtime evidence for CL-4: operational hypothesis to experiment draft."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from terrario.lab.experiment_composer import validate_draft
from terrario.lab.hypergraph.theory_operational import (
    BindingRequirement, CompositionRule, RoleCompatibility, compose, load_bindings, materialize,
)
from terrario.lab.metrics_observer import MetricRegistry, ObserverRegistry
from terrario.lab.models import thaw
from terrario.lab.persistence.codecs import experiment_draft_from_payload
from terrario.lab.theory.compiler import OperationalExperimentCompiler, OperationalHypothesisCompiler
from terrario.lab.theory.ingestion import TheoryIngestor
from terrario.lab.world_registry import WorldScenarioRegistry, configuration_for


def _rejects(operation) -> str:
    try:
        operation()
    except ValueError as exc:
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
        return materialize(candidate, load_bindings(evidence / "HYPEREDGE_ROLE_BINDINGS_v0.2.csv", candidate_id), imported,
                           primary_source_root=args.primary_source_root)

    edge02, edge08 = edge("HYPERCAND-02"), edge("HYPERCAND-08")
    derived = compose(edge02, edge08, compatibility=(RoleCompatibility(
        BindingRequirement("agent", "agent"), BindingRequirement("actor", "action_sequence_proposer"),
        "both source-backed roles explicitly produce actions",
    ),), rule=CompositionRule("ACTION_PRODUCING_AGENT_REFINEMENT", "v1", "architectural actor refines formal agent action role"),
        provenance="role-compatible structural refinement; TI-0071 + TI-0077")
    hypothesis = OperationalHypothesisCompiler().compile(derived, {
        edge02.semantic_id: edge02, edge08.semantic_id: edge08, derived.semantic_id: derived,
    })
    entry = WorldScenarioRegistry(PROJECT_ROOT).get("D2")
    draft = OperationalExperimentCompiler().compile(
        hypothesis, scenario=entry.scenario, difficulty_fingerprint=configuration_for(entry).difficulty.fingerprint,
    )
    findings = validate_draft(draft, entry.scenario, MetricRegistry(), ObserverRegistry())
    reloaded = experiment_draft_from_payload(thaw(draft))

    print(json.dumps({
        "input": {"hypothesis_id": hypothesis.semantic_id, "prediction": hypothesis.prediction,
                  "premise_claims": [item.claim_id for item in hypothesis.premises]},
        "experiment_draft": {
            "draft_id": draft.draft_id, "scientific_hash": draft.content_hash,
            "state": draft.state.value, "scenario": draft.scenario_id,
            "mapping": thaw(draft.hypothesis_mapping),
        },
        "validation": [{"code": item.code, "blocking": item.blocking, "message": item.message} for item in findings],
        "serialize_reload": {
            "scientific_identity_preserved": reloaded.content_hash == draft.content_hash,
            "mapping_preserved": reloaded.hypothesis_mapping == draft.hypothesis_mapping,
        },
        "negative_cases": {
            "WRONG_SCENARIO": _rejects(lambda: OperationalExperimentCompiler().compile(
                hypothesis, scenario=WorldScenarioRegistry(PROJECT_ROOT).get("D3").scenario,
                difficulty_fingerprint=configuration_for(entry).difficulty.fingerprint,
            )),
        },
        "execution_performed": False,
    }, indent=2))


if __name__ == "__main__":
    main()
