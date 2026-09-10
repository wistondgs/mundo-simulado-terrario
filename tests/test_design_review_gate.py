import pytest
from terrario.lab.theory.factory import ReviewState, transition_review
from tests.hypothesis_factory_helpers import family
def test_review_states_cannot_be_skipped():
    with pytest.raises(PermissionError): transition_review(family(),ReviewState.APPROVED_FOR_EXECUTION)
    reviewing=transition_review(family(),ReviewState.UNDER_REVIEW); assert transition_review(reviewing,ReviewState.APPROVED_FOR_EXPERIMENT_DESIGN).review_state == ReviewState.APPROVED_FOR_EXPERIMENT_DESIGN
