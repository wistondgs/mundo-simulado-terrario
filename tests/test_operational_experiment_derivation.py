from dataclasses import replace
from pathlib import Path

import pytest

from terrario.lab.experiment_composer import HypothesisExperimentMapping, build_trial_matrix, validate_draft
from terrario.lab.hypergraph.theory_operational import (
    BindingRequirement, CompositionRule, RoleCompatibility, compose, load_bindings, materialize,
)
from terrario.lab.metrics_observer import MetricRegistry, ObserverRegistry
from terrario.lab.models import thaw
from terrario.lab.persistence.codecs import experiment_draft_from_payload
from terrario.lab.theory.compiler import OperationalExperimentCompiler, OperationalHypothesisCompiler
from terrario.lab.theory.ingestion import TheoryIngestor
from terrario.lab.world_registry import WorldScenarioRegistry, configuration_for
from tests.theory_helpers import primary_corpus_root, snapshot_dir


PRIMARY_CORPUS = primary_corpus_root()


def _operational_hypothesis():
    snapshot = snapshot_dir()
    imported = TheoryIngestor(snapshot, include_operational_evidence=True).ingest()
    evidence = snapshot.parent.parent / "theory_operational_artifacts" / snapshot.name

    def edge(candidate_id):
        candidate = next(item for item in imported.hyperedges if item.id == candidate_id)
        return materialize(candidate, load_bindings(evidence / "HYPEREDGE_ROLE_BINDINGS_v0.2.csv", candidate_id), imported,
                           primary_source_root=PRIMARY_CORPUS)

    edge02, edge08 = edge("HYPERCAND-02"), edge("HYPERCAND-08")
    derived = compose(edge02, edge08, compatibility=(RoleCompatibility(
        BindingRequirement("agent", "agent"), BindingRequirement("actor", "action_sequence_proposer"),
        "both source-backed roles explicitly produce actions",
    ),), rule=CompositionRule("ACTION_PRODUCING_AGENT_REFINEMENT", "v1", "architectural actor refines formal agent action role"),
        provenance="role-compatible structural refinement; TI-0071 + TI-0077")
    return OperationalHypothesisCompiler().compile(derived, {
        edge02.semantic_id: edge02, edge08.semantic_id: edge08, derived.semantic_id: derived,
    })


def _compile():
    registry = WorldScenarioRegistry(Path("."))
    entry = registry.get("D2")
    return _operational_hypothesis(), entry.scenario, configuration_for(entry).difficulty.fingerprint


def test_operational_hypothesis_maps_to_inspectable_nonexecuting_d2_draft():
    hypothesis, scenario, fingerprint = _compile()
    draft = OperationalExperimentCompiler().compile(hypothesis, scenario=scenario, difficulty_fingerprint=fingerprint)
    mapping = draft.hypothesis_mapping
    assert draft.state.value == "REVIEW_BLOCKED"
    assert mapping and mapping.hypothesis_semantic_id == hypothesis.semantic_id
    assert mapping.metric_id == "planned-action-evaluation-pathway"
    assert len(mapping.conditions) == 2
    assert mapping.source_claim_ids == tuple(sorted(item.claim_id for item in hypothesis.premises))
    findings = validate_draft(draft, scenario, MetricRegistry(), ObserverRegistry())
    codes = {item.code for item in findings}
    assert {"REVIEW_REQUIRED", "DESIGN_NOT_APPROVED"} <= codes
    assert "WEAK_PROXY" not in codes
    assert "APPROVED_FOR_EXECUTION" not in codes


def test_operational_trial_matrix_carries_exact_role_ablation_config_not_prose():
    hypothesis, scenario, fingerprint = _compile()
    draft = OperationalExperimentCompiler().compile(hypothesis, scenario=scenario, difficulty_fingerprint=fingerprint)
    matrix = build_trial_matrix(draft)
    bindings = {cell.condition_id: dict(cell.agent_config) for cell in matrix.cells}
    assert set(bindings) == {"actor-role-preserved", "actor-role-ablated"}
    assert bindings["actor-role-preserved"] == {"use_planner": True, "use_world_model": True}
    assert bindings["actor-role-ablated"] == {"use_planner": False, "use_world_model": True}
    assert all(cell.agent_id == "A4" for cell in matrix.cells)


def test_operational_experiment_draft_round_trip_and_identity_are_deterministic():
    hypothesis, scenario, fingerprint = _compile()
    compiler = OperationalExperimentCompiler()
    first = compiler.compile(hypothesis, scenario=scenario, difficulty_fingerprint=fingerprint)
    second = compiler.compile(hypothesis, scenario=scenario, difficulty_fingerprint=fingerprint)
    reloaded = experiment_draft_from_payload(thaw(first))
    assert (first.draft_id, first.content_hash) == (second.draft_id, second.content_hash)
    assert reloaded.content_hash == first.content_hash
    assert reloaded.hypothesis_mapping == first.hypothesis_mapping


def test_operational_experiment_derivation_fails_closed_for_invalid_transition_or_mapping():
    hypothesis, scenario, fingerprint = _compile()
    compiler = OperationalExperimentCompiler()
    with pytest.raises(ValueError, match="review-required"):
        compiler.compile(replace(hypothesis, epistemic_status="UNTESTED_HYPOTHESIS"), scenario=scenario, difficulty_fingerprint=fingerprint)
    with pytest.raises(ValueError, match="only for D2"):
        compiler.compile(hypothesis, scenario=WorldScenarioRegistry(Path(".")).get("D3").scenario, difficulty_fingerprint=fingerprint)
    draft = compiler.compile(hypothesis, scenario=scenario, difficulty_fingerprint=fingerprint)
    with pytest.raises(ValueError, match="every scientific field"):
        HypothesisExperimentMapping(**{**draft.hypothesis_mapping.__dict__, "field_rationales": {}})
    invalid = replace(draft, provenance=replace(draft.provenance, source_artifact="HYPOTHESIS-tampered"))
    assert "HYPOTHESIS_PROVENANCE_MISMATCH" in {item.code for item in validate_draft(invalid, scenario, MetricRegistry(), ObserverRegistry())}
