from terrario.lab.theory.factory import InterventionDesigner
from tests.hypothesis_factory_helpers import family
def test_intervention_catalog_and_specs_are_explicit():
    assert set(InterventionDesigner.TYPES) >= {"ABLATION","SUBSTITUTION","FREEZE","NOISE","DELAY","CAPACITY_LIMIT","INFORMATION_REMOVAL","ENVIRONMENTAL_CHANGE","TRANSFER","PLACEBO","SHAM"}
    assert all(i.target and i.preserved_properties and i.confounds_introduced for i in InterventionDesigner().design(family()))
