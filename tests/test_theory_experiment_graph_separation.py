from tests.theory_helpers import theory_graph

def test_theory_and_evidence_graphs_are_separate():
    graph=theory_graph().export()
    assert graph["theory_graph"]["nodes"] and graph["evidence_graph"]["nodes"]
    assert all(x["graph_layer"]=="THEORY" for x in graph["theory_graph"]["nodes"])
