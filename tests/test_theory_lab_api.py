from terrario.lab.api import LabAPI

def test_theory_api_serves_real_snapshot_and_readonly_analyzer(tmp_path):
    api=LabAPI(".", data_root=tmp_path/".terrario")
    status,summary=api.dispatch("GET","/api/theory/summary")
    graph=api.dispatch("GET","/api/hypergraph")[1]
    analysis=api.dispatch("GET","/api/analyzer/deterministic")[1]
    assert status==200 and summary["hyperedges"]==8 and len(graph["nodes"])>1000
    assert analysis["artifact_type"]=="DERIVED_ANALYSIS"

def test_scientific_review_api_is_unapproved_and_read_only(tmp_path):
    status,payload=LabAPI(".", data_root=tmp_path/".terrario").dispatch("GET","/api/theory/scientific-review")
    assert status==200 and len(payload["reviews"])==8 and len(payload["top_candidates"])<=3
    assert all(p["human_decision"]["decision"] is None for p in payload["packages"])
