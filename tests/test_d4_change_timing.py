from terrario.experiment.controller import build_world_state, load_scenario
from terrario.world.rules import RuleEngine
from terrario.world.scheduler import ChangeScheduler
from terrario.world.state import WorldStateManager


def test_d4_fast_uses_pre_step_change_without_observation_signal():
    scenario = load_scenario("scenarios/d4_change_fast.yaml")
    world = WorldStateManager(build_world_state(scenario), scenario["duration"])
    rules = RuleEngine()
    rules.load_rules(scenario["rules"])
    scheduler = ChangeScheduler(scenario["changes"], rules)
    before = rules.rules[0].rule_id
    assert scheduler.check(world, step=9) == []
    events = scheduler.check(world, step=10)
    assert len(events) == 1 and events[0].step == 10
    assert rules.rules[0].rule_id != before
    observation = world.get_observation(0, scenario["view_radius"], scenario["num_channels"])
    assert not hasattr(observation, "rules_version")
    assert not hasattr(observation, "change_step")
