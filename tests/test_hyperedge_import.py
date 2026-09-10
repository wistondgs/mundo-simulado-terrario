from tests.theory_helpers import theory_import

def test_all_real_hyperedges_remain_testable_conjunctions():
    hyperedges=theory_import().hyperedges
    assert [x.id for x in hyperedges]==[f"HYPERCAND-{i:02d}" for i in range(1,9)]
    assert all(x.epistemic_status.value=="TESTABLE_CONJUNCTION" and x.necessity and x.sufficiency for x in hyperedges)
