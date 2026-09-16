import json
from dataclasses import replace
from pathlib import Path

import pytest

from terrario.lab.hypergraph.theory_operational import (
    BindingRequirement, CompositionRule, RoleCompatibility, compose, load_bindings,
    materialize,
)
from terrario.lab.theory.compiler import HypothesisCompiler, OperationalHypothesisCompiler
from terrario.lab.theory.ingestion import TheoryIngestor
from terrario.lab.theory.models import HypothesisDraft
from tests.theory_helpers import primary_corpus_root, snapshot_dir


PRIMARY_CORPUS = primary_corpus_root()


def _derived_input():
    snapshot = snapshot_dir()
    imported = TheoryIngestor(snapshot, include_operational_evidence=True).ingest()
    evidence = snapshot.parent.parent / "theory_operational_artifacts" / snapshot.name

    def edge(candidate_id):
        candidate = next(item for item in imported.hyperedges if item.id == candidate_id)
        return materialize(candidate, load_bindings(evidence / "HYPEREDGE_ROLE_BINDINGS_v0.2.csv", candidate_id), imported, primary_source_root=PRIMARY_CORPUS)

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
    return imported, edge02, edge08, derived


def test_composed_operational_hyperedge_derives_falsifiable_review_gated_hypothesis():
    imported, edge02, edge08, derived = _derived_input()
    draft = OperationalHypothesisCompiler().compile(derived, {
        edge02.semantic_id: edge02, edge08.semantic_id: edge08, derived.semantic_id: derived,
    })
    assert draft.id.startswith("DRAFT-DERIVED-")
    assert draft.source_hyperedge_id == derived.semantic_id
    assert draft.composition_path == derived.parent_semantic_ids
    assert draft.derivation_rule == "ROLE_REFINEMENT_ABLATION_PREDICTION@v1"
    assert draft.epistemic_status == "REVIEW_REQUIRED"
    assert draft.testability == "REVIEW_REQUIRED_TESTABLE"
    assert {item.claim_id for item in draft.premises} == {"CLM-0074", "CLM-H08-003", "CLM-H08-005", "CLM-H08-006"}
    assert {item.source_id for item in draft.premises} == {"TI-0071", "TI-0077"}
    assert draft.prediction not in {item.original_text for item in imported.claims}


def test_derived_hypothesis_round_trip_preserves_semantics_and_epistemic_status():
    _, edge02, edge08, derived = _derived_input()
    draft = OperationalHypothesisCompiler().compile(derived, {
        edge02.semantic_id: edge02, edge08.semantic_id: edge08, derived.semantic_id: derived,
    })
    payload = json.loads(json.dumps(draft.payload()))
    payload["premises"] = list(reversed(payload["premises"]))
    reloaded = HypothesisDraft.from_payload(payload)
    assert reloaded.semantic_id == draft.semantic_id
    assert reloaded.epistemic_status == draft.epistemic_status
    with pytest.raises(ValueError, match="semantic identity"):
        HypothesisDraft.from_payload({**payload, "confounders": ["tampered confounder"]})


def test_derivation_is_deterministic_and_cannot_activate_without_review():
    _, edge02, edge08, derived = _derived_input()
    edges = {edge02.semantic_id: edge02, edge08.semantic_id: edge08, derived.semantic_id: derived}
    first = OperationalHypothesisCompiler().compile(derived, edges)
    second = OperationalHypothesisCompiler().compile(derived, edges)
    assert (first.id, first.semantic_id, first.prediction) == (second.id, second.semantic_id, second.prediction)
    with pytest.raises(PermissionError, match="human review"):
        HypothesisCompiler().activate(first)


def test_source_backed_or_unresolvable_inputs_fail_closed():
    _, edge02, edge08, derived = _derived_input()
    compiler = OperationalHypothesisCompiler()
    with pytest.raises(ValueError, match="only a derived"):
        compiler.compile(edge02, {edge02.semantic_id: edge02})
    with pytest.raises(ValueError, match="resolvable immediate parents"):
        compiler.compile(derived, {edge02.semantic_id: edge02, derived.semantic_id: derived})
    with pytest.raises(ValueError, match="cannot treat structural composition as corroboration"):
        compiler.compile(replace(derived, corroboration_status="CORROBORATED"), {
            edge02.semantic_id: edge02, edge08.semantic_id: edge08, derived.semantic_id: derived,
        })
    with pytest.raises(ValueError, match="declared compatible composition rule"):
        compiler.compile(replace(derived, composition_rule="OTHER_RULE@v1"), {
            edge02.semantic_id: edge02, edge08.semantic_id: edge08, derived.semantic_id: derived,
        })
