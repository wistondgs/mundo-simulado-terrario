from terrario.lab.theory.factory import DesignRepository
from tests.hypothesis_factory_helpers import design
def test_revisions_are_new_immutable_versions_with_delta():
    repo=DesignRepository(); first=design(); repo.save(first); second=repo.revise(first,"mitigated compute")
    assert second.version == 2 and first.version == 1 and second.provenance.modifications[-1] == "mitigated compute"
