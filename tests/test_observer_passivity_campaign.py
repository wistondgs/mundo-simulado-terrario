from __future__ import annotations

from terrario.core.rng import RNGManager
from terrario.experiment.config import ExperimentConfig
from terrario.experiment.controller import ExperimentController, build_world_state, load_scenario, materialize_scenario
from terrario.observer.logger import ScientificObserver
from terrario.world.physics import Physics
from terrario.world.rules import RuleEngine
from terrario.world.scheduler import ChangeScheduler
from terrario.world.state import WorldStateManager


def _trajectory(tmp_path, mode: str, frame_sink=None) -> tuple[list[int], list[float], list[str], list[dict]]:
    scenario = materialize_scenario(load_scenario("scenarios/d0_differences.yaml"), 73)
    config = ExperimentConfig(
        "observer-passivity", None, "scenarios/d0_differences.yaml", ["A0_RANDOM"], {},
        [73], 1, 12, mode, 0, str(tmp_path),
    )
    controller = ExperimentController(config)
    agent_seed = 1_000_076
    RNGManager.set_global_determinism(agent_seed)
    world = WorldStateManager(build_world_state(scenario), 12, 100.0, 0.0, True)
    rules = RuleEngine()
    rules.load_rules(scenario["rules"])
    world.set_rules_version(rules.version)
    agent = controller._create_agent("A0_RANDOM", agent_seed, scenario)
    with ScientificObserver(str(tmp_path / mode), mode, {"seed": 73}) as observer:
        episode = controller.run_episode(
            agent, world, Physics(), rules, ChangeScheduler([], rules), observer, agent_seed,
            scenario=scenario, frame_sink=frame_sink,
        )
    return (
        episode["actions"], episode["energy_history"],
        [trace["state_hash"] for trace in episode["traces"]], episode["observation_faults"],
    )


def test_standard_and_forensic_observation_are_trajectory_passive(tmp_path):
    standard = _trajectory(tmp_path, "scientific_standard")
    forensic = _trajectory(tmp_path, "forensic_full")

    assert forensic == standard


def test_atomic_scientific_frame_capture_is_trajectory_passive(tmp_path):
    baseline = _trajectory(tmp_path / "baseline", "scientific_standard")
    observed = _trajectory(tmp_path / "observed", "scientific_standard", frame_sink=lambda _frame: None)
    assert observed[:3] == baseline[:3]
    assert observed[3] == baseline[3] == []


def test_observer_failure_cannot_change_the_completed_experimental_trajectory(tmp_path):
    baseline = _trajectory(tmp_path / "baseline", "scientific_standard")
    observed = _trajectory(tmp_path / "observed", "scientific_standard", frame_sink=lambda _frame: None)
    failed = _trajectory(tmp_path / "failed", "scientific_standard",
                         frame_sink=lambda _frame: (_ for _ in ()).throw(RuntimeError("injected observer fault")))
    assert baseline[:3] == observed[:3] == failed[:3]
    assert baseline[3] == observed[3] == []
    assert len(failed[3]) == len(failed[0])
    assert {fault["kind"] for fault in failed[3]} == {"FRAME_SINK_FAILURE"}
