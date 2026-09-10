from tests.hypothesis_factory_helpers import family

def test_all_nonempty_subsets_are_generated_without_author_attribution():
    f=family(); rivals=[h for h in f.hypotheses if h.kind != "NULL_HYPOTHESIS"]
    assert len(rivals) == 7
    assert all(h.epistemic_status == "SYSTEM_GENERATED_RIVAL" for h in rivals)
    assert all(h.provenance.source_artifact == "HYPEREDGE_CANDIDATES_v0.2.md" for h in rivals)
