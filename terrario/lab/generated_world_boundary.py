"""Canonical boundary from a diagnostic ``GeneratedWorld`` to Lab runtime.

The generator remains a scientific constructor, not a runtime.  This module
turns its explicit scenario into the pre-existing WorldDraft -> CompiledWorld
pipeline and records why it was generated in ``WorldProvenance.delta``.
"""
from __future__ import annotations

from typing import Any, Mapping

from terrario.lab import world_generator as generator
from terrario.lab.world_authoring import CompiledWorld, WorldDraft, compile_draft, generate_instance
from terrario.lab.world_contracts import (
    SCHEMA_VERSION, ConfigurationState, DifficultyDimension, DifficultyProfile,
    DimensionState, LabConfiguration, WorldProvenance,
    scientific_hash,
)
from terrario.lab.world_registry import scenario_from_runtime

MERGE_SEMANTICS_VERSION = "terrario.lab.world_generator.merge/v1"


def generated_world_provenance(world: generator.GeneratedWorld) -> WorldProvenance:
    """Return the complete, deterministic scientific origin of ``world``.

    It deliberately separates the *reason* for generation (capabilities and
    demands) from the definition's physical semantics and from the explicit
    seed materialization.  ``WorldProvenance`` is the established extension
    point for this information; no parallel provenance contract is needed.
    """
    caps = tuple(world.capabilities)
    per_capability = {
        capability: {
            "axis": generator.DEMAND_OF[capability][0],
            "demand": {axis: getattr(generator.DEMAND_OF[capability][1], axis)
                       for axis in generator.AXES},
        }
        for capability in caps
    }
    scenario_hash = scientific_hash(world.scenario)
    delta = {
        "kind": "CANONICAL_GENERATED_WORLD",
        "generator_identity": "terrario.lab.world_generator",
        "generator_version": generator.SEMANTICS_VERSION,
        "merge_semantics_version": MERGE_SEMANTICS_VERSION,
        "capability_set": list(caps),
        "per_capability_demands": per_capability,
        "merged_demand": {axis: getattr(world.demand, axis) for axis in generator.AXES},
        "generator_seed": world.seed,
        "generated_scenario_hash": scenario_hash,
        "station_key_hash": scientific_hash(world.stations),
        "economy": {name: getattr(world.economy, name) for name in world.economy.__dataclass_fields__},
    }
    return WorldProvenance(
        "DIAGNOSTIC_WORLD_GENERATOR", "capability-demand world generation",
        generator.SEMANTICS_VERSION, source=generator.SEMANTICS_VERSION,
        parent_id=f"generated-{scenario_hash[:16]}", parent_hash=scenario_hash,
        delta=delta,
    )


def _definition_semantics(world: generator.GeneratedWorld) -> dict[str, Any]:
    """Seed-independent properties that identify the scientific world class."""
    return {
        "generator_version": generator.SEMANTICS_VERSION,
        "merge_semantics_version": MERGE_SEMANTICS_VERSION,
        "demand": {axis: getattr(world.demand, axis) for axis in generator.AXES},
        "economy": {name: getattr(world.economy, name) for name in world.economy.__dataclass_fields__},
        "grid_height": int(world.scenario["grid_size"][1]),
        "station_count": len(world.stations),
        "view_radius": int(world.scenario["view_radius"]),
        "num_channels": int(world.scenario["num_channels"]),
        "rule_schema": world.scenario["rules"],
        "change_schema": [
            {key: value for key, value in change.items() if key != "at_step"}
            for change in world.scenario.get("changes", [])
        ],
    }


def generated_world_draft(world: generator.GeneratedWorld) -> WorldDraft:
    """Losslessly express the executable part of a generated world as a draft."""
    raw = world.scenario
    provenance = generated_world_provenance(world)
    definition_semantics = _definition_semantics(world)
    semantic_id = "generated-" + scientific_hash(definition_semantics)[:16]
    resources: dict[str, Any] = {
        "max_energy": raw["max_energy"],
        "step_energy_cost": raw["step_energy_cost"],
        "expose_time_fraction": raw["expose_time_fraction"],
        "view_radius": raw["view_radius"],
        "num_channels": raw["num_channels"],
        "canonical_world_id": semantic_id,
        "source_seed": world.seed,
        "generated_definition": definition_semantics,
        "generated_provenance": dict(provenance.delta),
    }
    return WorldDraft(
        draft_id=f"draft-{semantic_id}", schema_version=SCHEMA_VERSION,
        purpose=raw.get("description", "generated diagnostic world"),
        topology="bounded rectangular grid", dimensions=tuple(raw["grid_size"]),
        entities=tuple(raw.get("objects", ())), object_distributions=(),
        initial_conditions=raw.get("agent_start", {}),
        deterministic_rules=tuple(raw.get("rules", {}).get("rules", ())),
        stochastic_rules=(),
        observation_sources=("channels", "mask", "agent_energy", "time_fraction"),
        action_availability=("MOVE", "PUSH", "CONSUME", "INSPECT", "NOOP"),
        termination_conditions=(f"duration:{raw['duration']}", "agent death"),
        intervention_targets=("world rules",),
        scheduled_events=tuple(raw.get("changes", ()),),
        resource_structure=resources,
        seed_semantics="GeneratedWorld.seed is the WorldInstance seed; explicit layout is already materialized",
        provenance=provenance,
    )


def compile_generated_world(world: generator.GeneratedWorld) -> CompiledWorld:
    """Compile through the ordinary Lab draft compiler, never a special runtime."""
    return compile_draft(generated_world_draft(world))


def _difficulty(world: generator.GeneratedWorld) -> DifficultyProfile:
    """An explicit, descriptive profile; no capability threshold is inferred."""
    raw = world.scenario
    cells = int(raw["grid_size"][0]) * int(raw["grid_size"][1])
    objects = len(raw.get("objects", ()))
    value = lambda number, unit, text: DifficultyDimension(DimensionState.VALUE, number, unit, text)
    na = lambda unit, text: DifficultyDimension(DimensionState.NOT_APPLICABLE, None, unit, text)
    dims = {
        "world_size": value(cells, "cells", "explicit generated grid"),
        "object_density": value(objects / cells, "ratio", "explicit generated objects"),
        "distractor_density": value(world.demand.distractors, "ratio", "declared distractors per station"),
        "observation_noise": value(0.0, "ratio", "generator declares none"),
        "partial_observability": value(1.0, "ratio", "local observation window"),
        "temporal_dependency": value(world.demand.delay, "steps", "declared cue-to-door delay"),
        "memory_horizon": value(world.demand.delay, "steps", "declared diagnostic demand"),
        "rule_complexity": value(len(raw["rules"]["rules"]), "rule count", "explicit generated rules"),
        "rule_volatility": value(len(raw.get("changes", ())), "changes/episode", "explicit generated schedule"),
        "action_cost": value(float(raw["step_energy_cost"]), "energy/action", "declared step energy cost"),
        "resource_pressure": na("ratio", "not inferred from a diagnostic demand"),
        "planning_depth": na("steps", "not declared by generator"),
        "transfer_distance": na("declared distance", "no transfer phase"),
        "causal_ambiguity": value(float(world.demand.novelty), "confound count", "declared novelty fraction"),
    }
    return DifficultyProfile(dims)


def generated_world_configuration(world: generator.GeneratedWorld,
                                  compiled: CompiledWorld | None = None) -> LabConfiguration:
    """Make the standard sandbox configuration associated with a compiled world."""
    compiled = compiled or compile_generated_world(world)
    provenance = compiled.definition.provenance
    scenario_hash = scientific_hash(world.scenario)
    scenario = scenario_from_runtime(
        f"generated-{scenario_hash[:16]}", dict(compiled.runtime_template),
        compiled.definition, provenance, required_capabilities=tuple(world.capabilities),
    )
    return LabConfiguration(
        config_id=f"config-generated-{scenario_hash[:16]}", schema_version=SCHEMA_VERSION,
        state=ConfigurationState.DRAFT, scenario=scenario, variant=None,
        difficulty=_difficulty(world), seeds=(world.seed,),
        observer_configuration={"mode": "scientific_standard"},
        agent_reference="A0_RANDOM", metric_bindings=scenario.metric_bindings,
        provenance=provenance, ui_preferences={"panel": "generated-world"},
    )


def controller_scenario_provenance(world: generator.GeneratedWorld,
                                   compiled: CompiledWorld) -> Mapping[str, Any]:
    """Small immutable projection used by ExperimentController artifacts."""
    delta = dict(compiled.definition.provenance.delta)
    instance = generate_instance(compiled, world.seed)
    return {
        "generated_scenario_hash": delta["generated_scenario_hash"],
        "world_definition_hash": compiled.definition.content_hash,
        "world_instance_hash": instance.instance_hash,
        "generator_provenance": delta,
    }
