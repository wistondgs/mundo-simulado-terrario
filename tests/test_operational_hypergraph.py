from terrario.lab.hypergraph.adapter import HypergraphAdapter
from terrario.lab.hypergraph.operational import OperationalNodeType, hyperedges_for
from terrario.lab.api import LabAPI


def test_operational_hypergraph_connects_experiment_observer_and_execution_without_evidence_promotion():
    edges = HypergraphAdapter.operational_catalog()
    assert {edge.edge_id for edge in edges} == {f"OHG-{index:02d}" for index in range(1, 8)}
    materialization = next(edge for edge in edges if edge.edge_id == "OHG-02")
    assert {member.node_type for member in materialization.members} >= {
        OperationalNodeType.PREREGISTRATION, OperationalNodeType.EXECUTION_PLAN,
        OperationalNodeType.TRIAL_INTENT, OperationalNodeType.OBSERVER_PROFILE,
    }
    frame = next(edge for edge in edges if edge.edge_id == "OHG-03")
    assert {member.node_type for member in frame.members} >= {
        OperationalNodeType.WORLD_TRUTH, OperationalNodeType.AGENT_OBSERVATION,
        OperationalNodeType.SCIENTIFIC_OBSERVER,
    }
    assert all(edge.output.value != "EVIDENCE_GRAPH" for edge in edges)


def test_fork_and_playback_are_explicit_operational_hyperedges():
    assert {edge.edge_id for edge in hyperedges_for(OperationalNodeType.CAUSAL_FORK)} >= {"OHG-06", "OHG-07"}
    assert {edge.edge_id for edge in hyperedges_for(OperationalNodeType.PLAYBACK)} == {"OHG-05"}


def test_operational_hypergraph_read_endpoint_is_not_evidence_graph(tmp_path):
    status, payload = LabAPI(".", data_root=tmp_path / ".terrario").dispatch("GET", "/api/operational-hypergraph")
    assert status == 200
    assert payload["classification"] == "OPERATIONAL_DERIVED_NOT_EVIDENCE"
    assert len(payload["hyperedges"]) == 7
