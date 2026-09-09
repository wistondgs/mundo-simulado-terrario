from terrario.lab.hypergraph.adapter import HypergraphAdapter

def test_hypergraph_provenance_survives_ingestion(tmp_path):
    p=tmp_path/"claims.json";p.write_text('{"records":[{"id":"c","status":"AUTHOR_CLAIM","provenance":"page:4"}]}')
    assert HypergraphAdapter.ingest([p]).export()["nodes"][0]["provenance"] == "page:4"
