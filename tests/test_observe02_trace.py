from terrario.experiment.controller import build_world_state, load_scenario, materialize_scenario
from terrario.observer.windows import ForensicWindowPolicy
from terrario.world.state import WorldStateManager


def test_forensic_windows_prioritize_change_interval_over_pre_change_overlap():
    policy = ForensicWindowPolicy(change_step=450)
    assert policy.label(425) == "change"
    assert policy.label(424) == "pre_change"
    assert policy.label(451) == "change"
    assert policy.label(576) == "recovery"


def test_forensic_window_manifest_is_disjoint_and_clipped_to_episode():
    policy = ForensicWindowPolicy(change_step=20, pre_steps=100, change_before=5, change_after=10, recovery_after=30)

    windows = policy.windows(total_steps=40)

    assert windows == [
        {"phase": "pre_change", "start_step": 0, "end_step": 19},
        {"phase": "change", "start_step": 15, "end_step": 30},
        {"phase": "recovery", "start_step": 31, "end_step": 39},
    ]


def test_observation_has_no_causal_labels_or_hidden_change_time():
    scenario = materialize_scenario(load_scenario("scenarios/d4_adaptation_scientific.yaml"), 3)
    manager = WorldStateManager(
        build_world_state(scenario), scenario["duration"], scenario["max_energy"],
        scenario["step_energy_cost"], scenario["expose_time_fraction"],
    )
    observation = manager.get_observation(0, scenario["view_radius"], scenario["num_channels"])
    assert not hasattr(observation, "causal_class")
    assert not hasattr(observation, "rule_version")
    assert observation.time_fraction == 0.0
