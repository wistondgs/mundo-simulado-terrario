from terrario.lab.theory.factory import structural_dry_run
from tests.hypothesis_factory_helpers import design
def test_structural_dry_run_is_never_scientific_evidence():
    d=design(); result=structural_dry_run(d,d.metrics,d.required_capabilities)
    assert result["artifact_type"] == "ENGINEERING_DRY_RUN" and result["scientific_evidence"] is False
