from tests.theory_helpers import theory_import, theory_graph

def test_raw_and_canonical_records_both_survive():
    imported=theory_import(); graph=theory_graph()
    assert len(imported.raw_concepts)==283 and len(imported.canonical_candidates)==224
    assert any(e["relation"]=="MAPS_TO_CANDIDATE" for e in graph.theory_edges)
