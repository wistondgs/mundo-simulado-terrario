from terrario.lab.theory.factory import ConfounderRegistry
from tests.hypothesis_factory_helpers import edge
def test_registry_covers_declared_confounder_taxonomy():
    items=ConfounderRegistry().from_edge(edge()); assert {x.category for x in items} == set(ConfounderRegistry.CATEGORIES)
    assert all(x.critical and x.mitigation is None for x in items)
