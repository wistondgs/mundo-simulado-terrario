from tests.hypothesis_factory_helpers import family
def test_one_null_is_generated():
    nulls=[h for h in family().hypotheses if h.kind == "NULL_HYPOTHESIS"]
    assert len(nulls) == 1 and nulls[0].components == ()
