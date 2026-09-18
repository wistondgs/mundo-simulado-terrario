"""DIAGNOSTIC_WORLD_PIPELINE_PARITY for canonical generated worlds.

The three runners deliberately use independent runtime objects.  A shared
``run_step`` implementation is necessary but not sufficient: this test keeps
the conversion, materialization, observation and trace boundaries honest.
"""
from __future__ import annotations

import pytest

from terrario.experiment.config import ExperimentConfig
from terrario.experiment.controller import ExperimentController, materialize_scenario
from terrario.lab import world_generator as gen
from terrario.lab import world_oracles as oracle
from terrario.lab.generated_world_boundary import (
    compile_generated_world, controller_scenario_provenance,
    generated_world_configuration,
)
from terrario.lab.sandbox_runtime import SandboxService, derive_sandbox, make_spec
from terrario.observer.logger import ScientificObserver
from terrario.world.transition import build_episode_components, run_step


def _observation(observation):
    return {"channels": observation.channels.tolist(), "mask": observation.mask.tolist(),
            "agent_energy": observation.agent_energy, "time_fraction": observation.time_fraction}


def _objects(snapshot):
    return tuple(sorted((int(key), tuple(value["pos"]), tuple(value["channels"]))
                        for key, value in snapshot["objects"].items()))


def _direct(world, *, agent_seed: int, steps: int, faculties=oracle.FULL):
    components = build_episode_components(world.scenario, duration_fallback=steps,
                                          strict_physics=True, with_lifecycle=True,
                                          world_seed=world.seed)
    agent = oracle.Oracle(world, faculties, seed=agent_seed)
    traces = []
    for tick in range(steps):
        outcome = run_step(components, agent, tick, world_seed=world.seed,
                           agent_seed=agent_seed, max_steps=steps,
                           learning_enabled=False)
        state = components.world._mutable_state()
        snapshot = components.world.serialize()
        traces.append({
            "time": state.time, "state_hash": state.state_hash(),
            "agent_position": tuple(snapshot["agents"]["0"]["pos"]),
            "agent_energy": snapshot["agents"]["0"]["energy"],
            "alive": snapshot["agents"]["0"]["alive"], "objects": _objects(snapshot),
            "rules_version": state.rules_version, "observation": _observation(outcome.observation_t),
            "action": outcome.action.to_int(),
            "resolved_target_id": outcome.target.object_id if outcome.target is not None else None,
            "events": tuple(outcome.consequence.events), "energy_delta": outcome.energy_delta,
            "effects_applied": bool(outcome.effects), "terminated": outcome.terminated,
            "scheduled_changes": tuple((event.step, event.old_version, event.new_version)
                                       for event in outcome.change_events),
        })
        if outcome.terminated or outcome.truncated:
            break
    return traces


def _sandbox(world, compiled, *, agent_seed: int, steps: int, root, faculties=oracle.FULL):
    config = derive_sandbox(generated_world_configuration(world, compiled))
    service = SandboxService(root / "sandbox")
    run = service.create(make_spec(config, compiled, world.seed, agent_seed, steps), config, compiled)
    # The runner is the actual SandboxService; replacing only its organism
    # gives all three paths an identical non-learning action source.
    service._runtime[run.run_id]["agent"] = oracle.Oracle(world, faculties, seed=agent_seed)
    service.run_bounded(run.run_id, steps)
    rows = []
    for trace in run.timeline:
        state = trace.observer_world
        action = trace.agent_action
        rows.append({
            "time": state["time"], "state_hash": state["state_hash"],
            "agent_position": tuple(state["agents"]["0"]["pos"]),
            "agent_energy": state["agents"]["0"]["energy"],
            "alive": state["agents"]["0"]["alive"], "objects": _objects(state),
            "rules_version": state["rules_version"], "observation": dict(trace.agent_observation),
            "action": action["action_int"],
            "resolved_target_id": action["resolved_target_id"],
            "events": tuple(trace.agent_events), "energy_delta": action["energy_delta"],
            "effects_applied": action["effects_applied"], "terminated": trace.terminated,
            "scheduled_changes": tuple(
                (trace.step, *map(int, event.removeprefix("rule_change:").replace("->", ":").split(":")))
                for event in trace.world_events if event.startswith("rule_change:")),
        })
    return rows


def _controller(world, compiled, *, agent_seed: int, steps: int, root, faculties=oracle.FULL):
    config = ExperimentConfig(
        "generated-parity", None, "", ["A0_RANDOM"], {}, [world.seed], 1, steps,
        "performance", 0, str(root / "controller"), scenario_payload=compiled.runtime_template,
        scenario_provenance=controller_scenario_provenance(world, compiled),
    )
    controller = ExperimentController(config)
    scenario = materialize_scenario(controller.scenario, world.seed)
    components = build_episode_components(scenario, duration_fallback=steps, strict_physics=True,
                                          with_lifecycle=True, world_seed=world.seed)
    frames = []
    observer = ScientificObserver(str(root / "observer"), "performance", {})
    try:
        episode = controller.run_episode(
            oracle.Oracle(world, faculties, seed=agent_seed), components.world,
            components.physics, components.rules, components.scheduler, observer, agent_seed,
            scenario=scenario, learning_enabled=False, frame_sink=frames.append)
    finally:
        observer.close()
    rows = []
    for trace, frame in zip(episode["traces"], frames):
        state = frame["world_truth"]
        rows.append({
            "time": state["time"], "state_hash": trace["state_hash"],
            "agent_position": tuple(state["agents"]["0"]["pos"]),
            "agent_energy": state["agents"]["0"]["energy"],
            "alive": state["agents"]["0"]["alive"], "objects": _objects(state),
            "rules_version": state["rules_version"], "observation": trace["agent_observation"],
            "action": trace["action"], "resolved_target_id": trace["resolved_target_id"],
            "events": tuple(trace["events"]), "energy_delta": trace["energy_delta"],
            "effects_applied": trace["effects_applied"], "terminated": trace["terminated"],
            "scheduled_changes": tuple((event["step"], event["old_version"], event["new_version"])
                                       for event in trace["rule_changes"]),
        })
    return rows


def first_divergence(direct, sandbox, controller):
    """Diagnostic report required by DIAGNOSTIC_WORLD_PIPELINE_PARITY."""
    names = ("DIRECT", "SANDBOX", "CONTROLLER")
    last_equal = None
    for tick, rows in enumerate(zip(direct, sandbox, controller)):
        for field in rows[0]:
            values = tuple(row[field] for row in rows)
            if not (values[0] == values[1] == values[2]):
                return {"PIPELINE_PARITY": "FAIL", "FIRST_DIVERGENT_TICK": tick,
                        "FIRST_DIVERGENT_FIELD": field,
                        **{f"{name}_VALUE": value for name, value in zip(names, values)},
                        "LAST_EQUAL_STATE_HASH": last_equal}
        last_equal = rows[0]["state_hash"]
    if not (len(direct) == len(sandbox) == len(controller)):
        return {"PIPELINE_PARITY": "FAIL", "FIRST_DIVERGENT_TICK": min(map(len, (direct, sandbox, controller))),
                "FIRST_DIVERGENT_FIELD": "trace_length", "DIRECT_VALUE": len(direct),
                "SANDBOX_VALUE": len(sandbox), "CONTROLLER_VALUE": len(controller),
                "LAST_EQUAL_STATE_HASH": last_equal}
    return {"PIPELINE_PARITY": "PASS", "LAST_EQUAL_STATE_HASH": last_equal}


def test_generated_world_boundary_preserves_identity_provenance_and_physics():
    world = gen.world_for(["EPMEM-A1", "PLAST-A1"], seed=42, stations=2)
    compiled = compile_generated_world(world)
    instance = __import__("terrario.lab.world_authoring", fromlist=["generate_instance"]).generate_instance(compiled, world.seed)
    assert instance.identity.seed == world.seed
    assert instance.structure["objects"] == world.scenario["objects"]
    for field in ("rules", "changes", "max_energy", "step_energy_cost", "expose_time_fraction", "view_radius", "num_channels"):
        assert instance.structure[field] == world.scenario[field]
    provenance = compiled.definition.provenance.delta
    assert provenance["capability_set"] == ["EPMEM-A1", "PLAST-A1"]
    assert provenance["merged_demand"]["inversion"] == 0.3
    assert provenance["generator_seed"] == world.seed
    assert controller_scenario_provenance(world, compiled)["world_instance_hash"] == instance.instance_hash
    # Definition is a seed-independent class; instance identity is not.
    sibling = compile_generated_world(gen.world_for(["EPMEM-A1", "PLAST-A1"], seed=43, stations=2))
    assert sibling.definition.content_hash == compiled.definition.content_hash


def test_merge_is_commutative_idempotent_and_associative():
    a, b, c = gen.Demand(delay=5), gen.Demand(risk=True, inversion=0.6), gen.Demand(inversion=0.3, novelty=.2)
    assert gen.merge((a, b)) == gen.merge((b, a))
    assert gen.merge((a, a)) == a
    assert gen.merge((gen.merge((a, b)), c)) == gen.merge((a, gen.merge((b, c))))


def test_diagnostic_world_pipeline_parity(tmp_path):
    world = gen.world_for(["EPMEM-A1"], seed=5, stations=2)
    compiled = compile_generated_world(world)
    report = first_divergence(
        _direct(world, agent_seed=9, steps=12),
        _sandbox(world, compiled, agent_seed=9, steps=12, root=tmp_path),
        _controller(world, compiled, agent_seed=9, steps=12, root=tmp_path),
    )
    assert report["PIPELINE_PARITY"] == "PASS", report


def test_first_divergence_report_is_actionable():
    a = [{"state_hash": "same", "objects": ((1, (0, 0), (1.0,)),)}]
    b = [{"state_hash": "same", "objects": ((1, (0, 1), (1.0,)),)}]
    report = first_divergence(a, b, a)
    assert report["FIRST_DIVERGENT_TICK"] == 0
    assert report["FIRST_DIVERGENT_FIELD"] == "objects"
    assert report["LAST_EQUAL_STATE_HASH"] is None


def _score_from_trace(world, rows):
    consumptions = [
        gen.Consumption(row_index, row["resolved_target_id"],
                        row["observation"]["agent_energy"] * world.economy.max_energy)
        for row_index, row in enumerate(rows)
        if row["effects_applied"] and row["resolved_target_id"] is not None
    ]
    return gen.score(world, consumptions)


def _metric(world, score):
    axis = gen.DEMAND_OF[world.capabilities[0]][0]
    if axis == "risk":
        return score.modulation
    if axis == "inversion":
        return score.accuracy_after
    return score.accuracy


@pytest.mark.parametrize("capability", [
    "LEARN-A1", "EPMEM-A1", "LTMEM-A1", "TEMP-A1", "HOMEO-A1", "PLAST-A1",
])
def test_demand_is_preserved_by_each_pipeline(capability, tmp_path):
    """No threshold is relaxed at the integration boundary.

    One deterministic seed is sufficient for this focused regression gate; the
    wider eight-seed demand check remains the campaign-level confirmation.
    """
    demanding = gen.world_for([capability], seed=7, stations=8)
    compiled = compile_generated_world(demanding)
    faculty = oracle.FACULTY_OF_AXIS[gen.DEMAND_OF[capability][0]]
    assert faculty is not None
    amputated = oracle.without(faculty)
    routes = {
        "DIRECT": lambda f: _direct(demanding, agent_seed=7, steps=demanding.duration, faculties=f),
        "SANDBOX": lambda f: _sandbox(demanding, compiled, agent_seed=7, steps=demanding.duration,
                                       root=tmp_path / "sandbox", faculties=f),
        "CONTROLLER": lambda f: _controller(demanding, compiled, agent_seed=7, steps=demanding.duration,
                                             root=tmp_path / "controller", faculties=f),
    }
    for name, route in routes.items():
        full = _metric(demanding, _score_from_trace(demanding, route(oracle.FULL)))
        ablated = _metric(demanding, _score_from_trace(demanding, route(amputated)))
        assert full is not None and ablated is not None
        assert full > ablated, {"pipeline": name, "capability": capability,
                                "full": full, "amputated": ablated}


def test_unc_remains_structural_only():
    world = gen.world_for(["UNC-A1"], seed=7, stations=8)
    assert oracle.FACULTY_OF_AXIS[gen.DEMAND_OF["UNC-A1"][0]] is None
    assert sum(station.novel for station in world.stations) > 0
