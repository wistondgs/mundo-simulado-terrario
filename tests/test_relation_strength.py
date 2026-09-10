from terrario.lab.theory.models import RelationStrength
from tests.theory_helpers import theory_import

def test_relation_strength_and_attribution_are_independent():
    relation=theory_import().relations[0]
    assert isinstance(relation.strength,RelationStrength) and relation.attribution
    assert relation.strength.value != relation.attribution
