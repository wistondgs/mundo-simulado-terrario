from terrario.world.opportunities import summarize_opportunity_contract


def test_opportunity_contract_reports_lifecycle_and_concurrent_balance():
    episode = {
        "opportunity_records": [
            {"causal_class": "A", "reachable_at_spawn": True, "visible_at_spawn": False, "ever_visible": True, "interacted": True},
            {"causal_class": "B", "reachable_at_spawn": True, "visible_at_spawn": False, "ever_visible": False, "interacted": False},
        ],
        "opportunity_events": [{"kind": "despawn"}, {"kind": "respawn"}],
        "traces": [
            {"causal_interaction": {"geometry": {"opportunities_class_A": 16, "opportunities_class_B": 16}}},
            {"causal_interaction": {"geometry": {"opportunities_class_A": 15, "opportunities_class_B": 16}}},
        ],
    }

    contract = summarize_opportunity_contract(episode, max_concurrent_imbalance=1)

    assert contract["class_record_counts"] == {"A": 1, "B": 1}
    assert contract["despawns"] == contract["respawns"] == 1
    assert contract["visible_records"] == 1
    assert contract["concurrent_balance_pass"] is True
