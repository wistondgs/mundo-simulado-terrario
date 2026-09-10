from terrario.lab.theory.factory import PredictionCompiler
from tests.hypothesis_factory_helpers import family
def test_prediction_is_operationally_structured():
    p=PredictionCompiler().compile(family().hypotheses[0])
    assert p.observable and p.comparison and p.temporal_window and p.expected_pattern and p.contradictory_pattern and p.ambiguous_pattern
