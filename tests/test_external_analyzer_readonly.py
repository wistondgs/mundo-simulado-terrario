from terrario.lab.analyzer import DeterministicScientificAnalyzer, ExternalAnalyzerInput

def test_deterministic_analyzer_reports_completeness_without_mutation():
    raw={"code_hash":"c","config_hash":"x","protocol":"p"}; request=ExternalAnalyzerInput({},"p","1",raw,{"invalid_runs":[1]},(),(),{})
    result=DeterministicScientificAnalyzer().analyze(request)
    assert result.artifact_type=="DERIVED_ANALYSIS" and result.anomalies and raw=={"code_hash":"c","config_hash":"x","protocol":"p"}
