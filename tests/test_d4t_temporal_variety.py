"""D4T is the first scenario that exercises what ChangeScheduler always supported.

Stage 1 of PLAN_REPRODUCCION_CONDUCTAS_01: temporal variety of the disturbance
-- sequence, rhythm, recurrence, accumulation -- reproduced with no new
mechanism, only a scenario the engine could already run and nobody had written.
"""
from pathlib import Path

import yaml

from terrario.lab.metrics_observer import MetricRegistry
from terrario.lab.world_registry import WorldScenarioRegistry, difficulty_for
from terrario.lab.viability_recovery_metric import (
    evaluate, evaluate_segments, segment_specification, specification,
    validate_construct, validate_segment_construct,
)


def _registry():
    return WorldScenarioRegistry(Path(__file__).resolve().parents[1])


def _scenario():
    root = Path(__file__).resolve().parents[1]
    return yaml.safe_load((root / "scenarios/d4_temporal_variety.yaml").read_text())["scenario"]


def test_d4t_is_registered_additively_without_remapping_anything():
    entries = _registry().entries()
    # Identity, not cardinality: a count would not catch a remapped id.
    assert [x.world_id for x in entries] == ["D0", "D1", "D2", "D3", "D4", "D4S", "D4T"]
    registry = _registry()
    assert Path(registry.get("D4").source).name == "d4_change.yaml"
    assert Path(registry.get("D4S").source).name == "d4_adaptation_scientific.yaml"
    assert Path(registry.get("D4T").source).name == "d4_temporal_variety.yaml"


def test_d4t_is_the_only_scenario_with_more_than_one_disturbance():
    registry = _registry()
    counts = {e.world_id: len(e.scenario.interventions) for e in registry.entries()}
    assert counts["D4T"] == 3
    assert all(v <= 1 for k, v in counts.items() if k != "D4T")


def test_rule_volatility_stops_being_pinned_at_one():
    # The difficulty model has always carried this dimension; until D4T every
    # scenario reported 1 or 0, so it distinguished nothing.
    volatility = {e.world_id: difficulty_for(e).dimensions["rule_volatility"].value
                  for e in _registry().entries()}
    assert volatility["D4T"] == 3
    assert volatility["D4S"] == 1


def test_the_schedule_holds_the_declared_controls_constant():
    scenario = _scenario()
    steps = [c["at_step"] for c in scenario["changes"]]
    gaps = [b - a for a, b in zip(steps, steps[1:])]
    # Equal intervals: "the second recovery was faster" must not be explained
    # by having had more time.
    assert len(set(gaps)) == 1
    # The window after the last disturbance is observed as long as the others.
    assert scenario["duration"] - steps[-1] == gaps[0]
    # No jitter: the schedule is identical across seeds, so a paired design
    # sees exactly the same disturbances in both arms.
    assert int(scenario.get("change_jitter", 0)) == 0
    # Same class of perturbation each time -- a full inversion. Type variety is
    # a different scenario (stage 2), and mixing them here would confound
    # recurrence with novelty of the disturbance.
    effects = [{r["id"]: r["effect"]["energy_delta"] for r in c["rules"]["rules"]}
               for c in scenario["changes"]]
    assert all(sorted(e.values()) == [-1.0, 1.0] for e in effects)


def test_the_single_disturbance_instrument_cannot_read_this_scenario():
    # Not a smaller answer: a wrong one. This is why the segment instrument
    # exists, and the test states the defect rather than trusting the comment.
    rows = [{"tick": i, "energy": 90.0 if (i < 5 or 8 <= i < 15 or 18 <= i < 25 or 28 <= i) else 40.0,
             "max_energy": 100.0, "revision": 1 + (i >= 5) + (i >= 15) + (i >= 25)}
            for i in range(35)]
    base = evaluate(rows, viable_floor=0.5, dwell_k=3, variety_bin=1.0)
    assert base.perturbation_tick == 5           # only the first is seen
    assert base.dwell_outside == 9               # three excursions pooled into one
    segments = evaluate_segments(rows, viable_floor=0.5, dwell_k=3, variety_bin=1.0)
    assert [s.perturbation_tick for s in segments] == [5, 15, 25]
    assert [s.dwell_outside for s in segments] == [3, 3, 3]


def test_segment_instrument_is_a_different_instrument_not_a_setting():
    args = {"viable_floor": 0.23, "dwell_k": 3, "variety_bin": 1.0}
    assert specification(**args)["metric_spec_hash"] != segment_specification(**args)["metric_spec_hash"]
    # A different eta is a different measurement here too.
    assert (segment_specification(**args)["metric_spec_hash"]
            != segment_specification(**{**args, "viable_floor": 0.5})["metric_spec_hash"])


def test_both_construct_validations_pass_and_the_base_report_is_untouched():
    assert validate_construct()["all_passed"] is True
    assert validate_segment_construct()["all_passed"] is True


def test_the_per_disturbance_metric_is_registered_and_not_promoted():
    metric = MetricRegistry().get("viability-recovery-profile-per-disturbance")
    assert metric.applicability == ("D4T",)
    assert metric.construct_validation_status.value == "NOT_VALIDATED_FOR_CONSTRUCT"
    # The instrument must say out loud that it does not answer the design question.
    assert any("comparison is a design" in x for x in metric.limitations)


def test_the_engine_actually_fires_all_three_through_the_real_loading_path():
    """The claim of stage 1 is that the engine already could. This runs it.

    Not a synthetic check: the scenario is loaded, the world built and the
    scheduler driven exactly as ExperimentController wires them.
    """
    from terrario.experiment.controller import build_world_state, load_scenario
    from terrario.world.rules import RuleEngine
    from terrario.world.scheduler import ChangeScheduler
    from terrario.world.state import WorldStateManager

    def fire(path):
        scenario = load_scenario(path)
        world = WorldStateManager(build_world_state(scenario), scenario.get("duration"),
                                  scenario.get("max_energy", 100.0),
                                  scenario.get("step_energy_cost", 0.0),
                                  scenario.get("expose_time_fraction", True))
        rules = RuleEngine()
        rules.load_rules(scenario.get("rules", {}))
        world.set_rules_version(rules.version)
        scheduler = ChangeScheduler(scenario.get("changes", []), rules)
        fired = [(e.step, e.new_version)
                 for step in range(scenario["duration"]) for e in scheduler.check(world, step)]
        return fired, scheduler.pending_count

    fired, pending = fire("scenarios/d4_temporal_variety.yaml")
    assert [step for step, _ in fired] == [300, 600, 900]
    # The rule version must advance once per disturbance: it is the marker the
    # detector segments on, so a version that failed to move would silently
    # merge two excursions.
    assert [version for _, version in fired] == [2, 3, 4]
    assert pending == 0

    # D4S is untouched: additive means the existing scenario still fires once.
    assert fire("scenarios/d4_adaptation_scientific.yaml")[0] == [(450, 2)]
