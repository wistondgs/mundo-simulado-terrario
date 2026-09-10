from tests.theory_helpers import theory_graph

def test_metric_lineage_returns_to_hypothesis():
    graph=theory_graph(); metric=next(x for x in graph.evidence_nodes if x.startswith("Metric:") and "h_adapt" in x)
    lineage=graph.lineage(metric,8)
    assert any("H-ADAPT-001" in path.node_ids for path in lineage)
    assert all(edge["provenance"] for path in lineage for edge in path.edges)
