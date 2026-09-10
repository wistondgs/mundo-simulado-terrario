from terrario.lab.theory.factory import build_portfolio
from tests.hypothesis_factory_helpers import edge
def test_portfolio_covers_all_eight_candidates_and_is_filterable():
    portfolio=build_portfolio([edge(f"HYPERCAND-{n:02d}") for n in range(1,9)],"snapshot-test")
    assert len(portfolio.entries) == 8 and len(portfolio.search("CPU_READY")) == 8
