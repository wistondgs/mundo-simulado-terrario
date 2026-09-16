import json
from pathlib import Path

import pytest

from terrario.lab.hypergraph.theory_operational import (
    BindingRequirement, CompositionRule, RoleCompatibility,
    TheoryHyperedgeBinding, TheoryOperationalHyperedge, compose,
    load_bindings, materialize, provenance_forward, provenance_reverse, query,
)
from terrario.lab.theory.store import build_graph
from terrario.lab.theory.ingestion import TheoryIngestor
from tests.theory_helpers import primary_corpus_root, snapshot_dir


PRIMARY_CORPUS = primary_corpus_root()


def _imported():
    return TheoryIngestor(snapshot_dir(), include_operational_evidence=True).ingest()


def _artifact_root():
    snapshot = snapshot_dir()
    return snapshot.parent.parent / "theory_operational_artifacts" / snapshot.name


def _candidate(candidate_id="HYPERCAND-02"):
    return next(item for item in _imported().hyperedges if item.id == candidate_id)


def _bindings(candidate_id="HYPERCAND-02"):
    return load_bindings(_artifact_root() / "HYPEREDGE_ROLE_BINDINGS_v0.2.csv", candidate_id)


def _edge(candidate_id="HYPERCAND-02", *, source_root=PRIMARY_CORPUS):
    return materialize(_candidate(candidate_id), _bindings(candidate_id), _imported(), primary_source_root=source_root)


def test_real_candidates_materialize_nary_with_verifiable_source_backed_roles():
    edge02, edge08 = _edge(), _edge("HYPERCAND-08")
    assert len(edge02.bindings) == len(edge08.bindings) == 6
    assert edge02.semantic_id == "THEORY-HYPEREDGE-aad3cda4f6acaa63"
    assert edge08.semantic_id == "THEORY-HYPEREDGE-f5a2bce46a032ba8"
    assert edge02.epistemic_status is edge08.epistemic_status
    assert {item.source_record_id for item in edge02.bindings} == {"TI-0071"}
    assert {item.source_record_id for item in edge08.bindings} == {"TI-0077"}
    assert {item.claim_id for item in edge08.bindings} == {f"CLM-H08-00{number}" for number in range(1, 7)}


def test_snapshot_mount_prefix_does_not_change_operational_semantic_identity():
    relative = snapshot_dir()
    absolute = relative.resolve()
    relative_import = TheoryIngestor(relative, include_operational_evidence=True).ingest()
    absolute_import = TheoryIngestor(absolute, include_operational_evidence=True).ingest()
    bindings = _bindings()
    relative_candidate = next(item for item in relative_import.hyperedges if item.id == "HYPERCAND-02")
    absolute_candidate = next(item for item in absolute_import.hyperedges if item.id == "HYPERCAND-02")
    assert materialize(relative_candidate, bindings, relative_import, primary_source_root=PRIMARY_CORPUS).semantic_id == materialize(
        absolute_candidate, bindings, absolute_import, primary_source_root=PRIMARY_CORPUS,
    ).semantic_id == "THEORY-HYPEREDGE-aad3cda4f6acaa63"


def test_hypercand08_primary_source_hash_is_required_at_materialization(tmp_path):
    with pytest.raises(ValueError, match="primary source artifact"):
        _edge("HYPERCAND-08", source_root=tmp_path)


def test_primary_source_claims_are_connected_in_the_runtime_theory_graph():
    graph = build_graph(snapshot_dir().name, _imported())
    path = graph.paths("SourceRecord:TI-0077", "ClaimRecord:CLM-H08-006")
    assert len(path) == 1
    assert path[0].edges[0]["relation"] == "SUPPORTS_AUTHORED_CLAIM"


def test_joint_query_requires_all_role_participant_and_metadata_constraints():
    edge = _edge()
    assert query(
        (edge,),
        requirements=(BindingRequirement("agent", "agent"), BindingRequirement("goal", "goal")),
        status=edge.epistemic_status,
        provenance="HYPEREDGE_CANDIDATES_v0.2.md",
    ) == (edge,)
    assert query(
        (edge,), requirements=(BindingRequirement("agent", "agent"), BindingRequirement("goal", "agent"))
    ) == ()


def test_round_trip_preserves_semantic_identity_and_epistemic_status_under_reordering():
    edge = _edge("HYPERCAND-08")
    payload = json.loads(json.dumps(edge.payload()))
    payload["bindings"] = list(reversed(payload["bindings"]))
    reloaded = TheoryOperationalHyperedge.from_payload(payload)
    assert reloaded.semantic_id == edge.semantic_id
    assert reloaded.epistemic_status is edge.epistemic_status


def test_other_candidates_missing_roles_and_broken_locator_fail_closed():
    other = _candidate("HYPERCAND-01")
    with pytest.raises(ValueError, match="NOT_MATERIALIZABLE"):
        materialize(other, (), _imported())
    with pytest.raises(ValueError, match="exactly one binding"):
        materialize(_candidate(), _bindings()[:-1], _imported())
    broken = list(_bindings("HYPERCAND-08"))
    broken[0] = TheoryHyperedgeBinding(**{**broken[0].__dict__, "source_locator": "§broken"})
    with pytest.raises(ValueError, match="locator mismatch"):
        materialize(_candidate("HYPERCAND-08"), broken, _imported(), primary_source_root=PRIMARY_CORPUS)


def test_real_semantic_composition_requires_explicit_rule_and_preserves_lineage():
    edge02, edge08 = _edge(), _edge("HYPERCAND-08")
    rule = CompositionRule(
        "ACTION_PRODUCING_AGENT_REFINEMENT", "v1",
        "An architectural actor refines the formal agent action-producing role; this is structural, not corroborative evidence.",
    )
    derived = compose(
        edge02, edge08,
        compatibility=(RoleCompatibility(
            BindingRequirement("agent", "agent"),
            BindingRequirement("actor", "action_sequence_proposer"),
            "Both roles are explicitly action-producing; TI-0077 specifies the architectural implementation of that role.",
        ),),
        rule=rule,
        provenance="role-compatible structural refinement; TI-0071 + TI-0077",
    )
    index = {item.semantic_id: item for item in (edge02, edge08, derived)}
    assert derived.origin == "DERIVED"
    assert derived.composition_rule == "ACTION_PRODUCING_AGENT_REFINEMENT@v1"
    assert derived.corroboration_status == "STRUCTURAL_COMPOSITION_NOT_CORROBORATION"
    assert set(derived.parent_semantic_ids) == {edge02.semantic_id, edge08.semantic_id}
    assert {item.source_record_id for item in provenance_forward(derived, index)} == {"TI-0071", "TI-0077"}
    assert provenance_reverse("CLM-H08-006", (edge02, edge08, derived), index) == (edge08, derived)
    reloaded = TheoryOperationalHyperedge.from_payload(json.loads(json.dumps(derived.payload())))
    assert reloaded.semantic_id == derived.semantic_id
    with pytest.raises(ValueError, match="NO_COMPOSITION"):
        compose(
            edge02, edge08,
            compatibility=(RoleCompatibility(BindingRequirement("goal", "agent"), BindingRequirement("actor", "action_sequence_proposer"), "invalid role bridge"),),
            rule=rule, provenance="must fail",
        )
