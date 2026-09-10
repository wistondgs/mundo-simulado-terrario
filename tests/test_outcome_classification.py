from terrario.lab.theory.factory import OutcomeClass, classify_outcome
def test_outcomes_never_claim_proof():
    values={classify_outcome(valid=False,expected=True),classify_outcome(valid=True,expected=True),classify_outcome(valid=True,expected=False),classify_outcome(valid=True,expected=None)}
    assert OutcomeClass.EXPERIMENT_INVALID in values and "PROVEN_TRUE" not in {x.value for x in OutcomeClass}
