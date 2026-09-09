import pytest
from terrario.lab.analyzer import ExternalAnalyzerInput

def test_external_analyzer_cannot_mutate_raw():
    request=ExternalAnalyzerInput({},"p","1",{"rows":[1]}, {},(),(),{})
    with pytest.raises(TypeError): request.evidence_manifest["rows"] = (2,)
