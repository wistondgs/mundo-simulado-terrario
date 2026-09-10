from tests.hypothesis_factory_helpers import design
def test_predictions_compare_rivals_under_an_intervention():
    assert all(p.hypothesis_a != p.hypothesis_b and p.intervention_id and 0 <= p.diagnosticity_score <= 1 for p in design().predictions)
