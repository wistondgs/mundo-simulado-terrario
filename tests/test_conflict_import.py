from tests.theory_helpers import theory_import

def test_conflicts_are_first_class_unresolved_records():
    conflicts=theory_import().conflicts
    assert len(conflicts)==12 and all(x.conflict_type=="UNRESOLVED_CONFLICT_TYPE" for x in conflicts)
