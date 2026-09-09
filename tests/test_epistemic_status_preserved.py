from terrario.lab.models import EpistemicStatus

def test_all_epistemic_statuses_remain_distinct():
    expected={"RAW","CANONICAL_CANDIDATE","AUTHOR_CLAIM","ANALYST_INFERENCE","TESTABLE_CONJUNCTION","UNTESTED_HYPOTHESIS","EVIDENCE_FOR","EVIDENCE_AGAINST","UNRESOLVED"}
    assert {x.value for x in EpistemicStatus} == expected
