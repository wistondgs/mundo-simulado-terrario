from terrario.lab.theory.factory import ControlDesigner
from tests.hypothesis_factory_helpers import family
def test_required_controls_and_dirty_a4_a0_warning_exist():
    controls=ControlDesigner().design(family()); assert set(ControlDesigner.TYPES) == {c.control_type for c in controls}
    assert any("A4 versus A0" in warning for c in controls for warning in c.warnings)
