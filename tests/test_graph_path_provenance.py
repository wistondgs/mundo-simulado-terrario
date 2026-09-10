from tests.theory_helpers import theory_graph

def test_every_returned_path_edge_has_provenance_and_status():
    graph=theory_graph(); paths=graph.paths("SourceRecord:TI-0006","HyperedgeCandidateRecord:HYPERCAND-08")
    assert paths and all(e["provenance"] and e["epistemic_status"] for e in paths[0].edges)
