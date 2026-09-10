from terrario.lab.theory.compiler import HypothesisCompiler
from tests.theory_helpers import theory_import

def test_weak_coverage_is_warning_not_block():
    draft=HypothesisCompiler().compile(theory_import().hyperedges[0],"WEAK")
    assert draft.theory_warning=="THEORY_BASE_WEAK" and draft.epistemic_status=="REVIEW_REQUIRED"
