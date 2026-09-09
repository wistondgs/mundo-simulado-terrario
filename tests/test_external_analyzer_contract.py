from terrario.lab.analyzer import ExternalAnalyzerInput, ExternalAnalyzerResult

def test_external_analyzer_result_is_derived_analysis():
    result=ExternalAnalyzerResult("a",(),(),(),(),.5,())
    assert result.artifact_type == "DERIVED_ANALYSIS"

def test_external_analyzer_input_is_frozen():
    raw={"id":"e"}; request=ExternalAnalyzerInput({},"p","1",raw,{},(),(),{})
    raw["id"]="mutated"
    assert request.evidence_manifest["id"] == "e"
