from tests.theory_helpers import theory_import

def test_quarantined_or_mismatched_source_stays_visible_but_not_citable():
    source=next(x for x in theory_import().sources if x.id=="TI-0046")
    assert source.integrity_status=="MISMATCH" and source.valid_evidence_source is False
