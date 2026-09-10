from terrario.lab.theory.factory import DesignValidator
from tests.hypothesis_factory_helpers import design
def test_unaddressed_critical_confounders_block_design():
    assert "critical confounders unaddressed" in DesignValidator().validate(design())
