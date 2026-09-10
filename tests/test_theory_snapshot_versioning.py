from terrario.lab.theory.store import TheoryGraphStore

def test_snapshot_comparison_does_not_overwrite_versions():
    old=TheoryGraphStore("v0.3"); new=TheoryGraphStore("v0.4")
    old.theory_nodes["a"]={"id":"a"}; new.theory_nodes.update({"a":{"id":"a"},"b":{"id":"b"}})
    assert old.compare(new)["nodes_added"]==["b"] and old.snapshot_id=="v0.3"
