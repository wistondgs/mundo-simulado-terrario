import time
from terrario.lab.theory.store import TheoryGraphStore

def test_graph_store_handles_thousands_of_test_only_records():
    graph=TheoryGraphStore("TEST_ONLY"); start=time.perf_counter()
    for i in range(1500): graph.theory_nodes[f"TEST_ONLY:{i}"]={"id":f"TEST_ONLY:{i}","status":"TEST_ONLY"}
    for i in range(1499): graph.link_theory(f"TEST_ONLY:{i}",f"TEST_ONLY:{i+1}","TEST_ONLY","TEST_ONLY","UNRESOLVED")
    assert len(graph.theory_nodes)==1500 and time.perf_counter()-start<2
