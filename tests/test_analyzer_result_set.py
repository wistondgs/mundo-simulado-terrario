from terrario.lab.analyzer import AnalyzerResultSet, ExternalAnalyzerResult

def test_analyzer_consensus_does_not_vote_truth():
    a=ExternalAnalyzerResult("a",("shared",),(),(),(),.5,()); b=ExternalAnalyzerResult("b",("shared","different"),(),(),(),.5,())
    compared=AnalyzerResultSet((a,b)).compare()
    assert compared["agreements"]==("shared",) and compared["truth_by_vote"] is False
