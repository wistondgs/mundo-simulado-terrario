from tests.theory_helpers import theory_graph

def test_real_source_to_hyperedge_path_recovers_original_source():
    graph=theory_graph(); path=graph.paths("SourceRecord:TI-0006","HyperedgeCandidateRecord:HYPERCAND-08")[0]
    assert path.node_ids[0]=="SourceRecord:TI-0006"
    assert graph.source_for(path.node_ids[0]).endswith("SOURCE_SAMPLE_v0.1.md:record:TI-0006")
