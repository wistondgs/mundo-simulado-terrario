from tests.hypothesis_factory_helpers import design
def test_design_retains_source_snapshot_and_claims():
    p=design().provenance; assert p.source_hyperedge_id and p.source_claim_ids == ("claim:1",) and p.theory_snapshot_id == "snapshot-test" and p.generator_version
