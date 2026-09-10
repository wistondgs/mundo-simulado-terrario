import pytest
from terrario.lab.theory.compiler import HypothesisCompiler
from tests.theory_helpers import theory_import

def test_hypothesis_draft_requires_explicit_review():
    compiler=HypothesisCompiler(); draft=compiler.compile(theory_import().hyperedges[0])
    assert draft.epistemic_status=="REVIEW_REQUIRED"
    with pytest.raises(PermissionError): compiler.activate(draft)
    assert compiler.activate(draft,approved=True).epistemic_status=="UNTESTED_HYPOTHESIS"
