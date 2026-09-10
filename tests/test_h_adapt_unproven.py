from tests.theory_helpers import theory_graph

def test_h_adapt_is_unproven_and_has_no_directional_evidence_claim():
    graph=theory_graph(); node=graph.evidence_nodes["H-ADAPT-001"]
    assert node["status"]=="UNTESTED_HYPOTHESIS"
    assert node["linkage_status"]=="PROJECT_HYPOTHESIS_WITHOUT_COMPLETE_THEORY_LINKAGE"
    assert not any(e["source"]=="H-ADAPT-001" and e["epistemic_status"] in {"EVIDENCE_FOR","EVIDENCE_AGAINST"} for e in graph.evidence_edges)
