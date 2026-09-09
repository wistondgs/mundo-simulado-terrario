from terrario.experiment.campaign import storage_governance


def test_storage_governance_reserves_capacity_before_accepting_campaign(tmp_path):
    budget = storage_governance(tmp_path, projected_bytes=1, reserve_bytes=0)

    assert budget["within_budget"] is True
    assert budget["available_after_reserve"] == budget["free_bytes"]
