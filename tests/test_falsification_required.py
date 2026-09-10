from dataclasses import replace
from terrario.lab.theory.factory import DesignValidator
from tests.hypothesis_factory_helpers import design
def test_design_without_falsification_is_rejected():
    assert "falsification required" in DesignValidator().validate(replace(design(), falsification_rules=()))
