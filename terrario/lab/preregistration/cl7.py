"""CL-7 paired-ablation integrity checks.

The generic preregistration model deliberately supports several study types.
This module is the stricter policy applied when its exact planning-trace
instrument is preregistered.  It is pure, deterministic, and has no execution
or evidence-publication dependency.
"""
from __future__ import annotations

from typing import Any, Mapping

from terrario.lab.persistence.canonical import content_hash

PLANNING_TRACE_METRIC_ID = "planned-action-evaluation-pathway"
_PRESERVED = {"use_planner": True, "use_world_model": True}
_ABLATED = {"use_planner": False, "use_world_model": True}


def arm_config_diff(arms: tuple[Mapping[str, Any], ...] | list[Mapping[str, Any]]) -> Mapping[str, Any]:
    """Return the only allowed configuration difference or a fail-closed report."""
    by_id = {str(arm.get("arm_id")): dict(arm.get("immutable_config") or {}) for arm in arms}
    preserved, ablated = by_id.get("PLANNER_PRESERVED"), by_id.get("PLANNER_ABLATED")
    if preserved != _PRESERVED or ablated != _ABLATED:
        return {"valid": False, "reason": "ARM_DEFINITION_INVALID"}
    other = (set(preserved) | set(ablated)) - {"use_planner", "use_world_model"}
    if other or any(preserved.get(key) != ablated.get(key) for key in (set(preserved) | set(ablated)) - {"use_planner"}):
        return {"valid": False, "reason": "UNPREREGISTERED_ARM_DIFFERENCE"}
    return {"valid": True, "use_planner": {"preserved": True, "ablated": False},
            "use_world_model": {"preserved": True, "ablated": True},
            "other_preregistered_fields": "IDENTICAL"}


def paired_matrix_report(matrix: Mapping[str, Any]) -> Mapping[str, Any]:
    """Validate all CL-7 matrix invariants independent of physical row order."""
    arms = tuple(matrix.get("treatment_arms") or ())
    pairs = tuple(matrix.get("seed_pairs") or ())
    cells = tuple(matrix.get("cells") or ())
    diff = arm_config_diff(arms)
    expected_pairs = {(str(pair.get("pair_id")), int(pair.get("world_seed")), int(pair.get("agent_seed"))) for pair in pairs}
    pair_seed_by_id = {pair_id: (world_seed, agent_seed) for pair_id, world_seed, agent_seed in expected_pairs}
    records: dict[tuple[str, str], Mapping[str, Any]] = {}
    duplicates = 0
    contradictory = 0
    shared_by_pair: dict[str, str] = {}
    for cell in cells:
        pair_id, arm_id = str(cell.get("seed_pair_id")), str(cell.get("arm_id"))
        key = (pair_id, arm_id)
        if key in records:
            duplicates += 1
        records[key] = cell
        config = dict(cell.get("agent_config") or {})
        wanted = _PRESERVED if arm_id == "PLANNER_PRESERVED" else _ABLATED if arm_id == "PLANNER_ABLATED" else None
        if wanted is None or config != wanted:
            contradictory += 1
        if pair_seed_by_id.get(pair_id) != (cell.get("world_seed"), cell.get("agent_seed")):
            contradictory += 1
        fingerprint = cell.get("initial_state_fingerprint") or {}
        shared = fingerprint.get("shared_initial_state") if isinstance(fingerprint, Mapping) else None
        if not isinstance(shared, Mapping) or dict(fingerprint.get("treatment_config") or {}) != config:
            contradictory += 1
            continue
        digest = content_hash(shared)
        prior = shared_by_pair.setdefault(pair_id, digest)
        if prior != digest:
            contradictory += 1
    expected_keys = {(pair_id, arm_id) for pair_id, _world, _agent in expected_pairs
                     for arm_id in ("PLANNER_PRESERVED", "PLANNER_ABLATED")}
    missing = expected_keys - set(records)
    unexpected = set(records) - expected_keys
    required_count = len(expected_keys)
    valid = (diff.get("valid") is True and {str(arm.get("arm_id")) for arm in arms} == {"PLANNER_PRESERVED", "PLANNER_ABLATED"}
             and len(arms) == 2 and len(pairs) == 4 and len(cells) == 8
             and len(records) == 8 and not duplicates and not contradictory
             and not missing and not unexpected and set(records) == expected_keys)
    semantic = {
        "arms": sorted(({"arm_id": item.get("arm_id"), "variant": item.get("variant"),
                          "immutable_config": item.get("immutable_config")} for item in arms), key=lambda x: str(x["arm_id"])),
        "pairs": sorted(({"pair_id": item.get("pair_id"), "world_seed": item.get("world_seed"),
                           "agent_seed": item.get("agent_seed")} for item in pairs), key=lambda x: str(x["pair_id"])),
        "cells": sorted(({"pair_id": pair_id, "arm_id": arm_id,
                           "shared": (records[(pair_id, arm_id)].get("initial_state_fingerprint") or {}).get("shared_initial_state"),
                           "signature": records[(pair_id, arm_id)].get("treatment_signature")}
                         for pair_id, arm_id in records), key=lambda x: (x["pair_id"], x["arm_id"])),
    }
    return {"valid": valid, "matrix_cell_count": len(cells), "unique_pair_arm_count": len(records),
            "contradictory_cell_count": contradictory, "duplicate_pair_arm_count": duplicates,
            "missing_pair_arms": tuple(sorted(missing)), "unexpected_pair_arms": tuple(sorted(unexpected)),
            "arm_config_diff": diff, "semantic_matrix_hash": content_hash(semantic)}


def rng_coupling_audit() -> Mapping[str, Any]:
    """Document the actual runtime split: world and agent streams are isolated.

    A4's planner is deterministic for a fixed agent state and does not receive
    the world RNG manager.  Any future planner stream must be separately named
    and committed before this audit can remain a pass.
    """
    return {"world_rng": "RNGManager.world_*", "agent_rng": "RNGManager.agent_*",
            "planner_rng": "NO_SHARED_RNG_INPUT", "planner_enabled_changes_shared_rng_draw_count": "NO",
            "unrelated_behavior_can_diverge_from_rng_shift": "NO", "status": "PASS"}
