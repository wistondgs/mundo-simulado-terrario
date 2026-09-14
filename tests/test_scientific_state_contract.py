from terrario.agent.agents import create_agent
import json

import pytest

from terrario.agent.scientific import (MAX_COGNITIVE_TRANSPORT_BYTES, NON_FINITE, NOT_APPLICABLE,
    SCIENTIFIC_TRANSPORT_SCHEMA, TRANSPORT_PREVIEW_LIMIT, scientific_state, scientific_transport_projection)


def test_every_architecture_exposes_normalized_read_only_scientific_fields():
    for architecture in ("A0_RANDOM", "A1_REACTIVE", "A2_GRU", "A3_WORLD_MODEL", "A4_ADVANCED"):
        state = scientific_state(create_agent(architecture, {"use_planner": False}, seed=1))
        assert {
            "architecture_id", "policy_logits", "memory_summary", "prediction_error",
            "parameter_delta_norm", "learning_summary", "active_ablations",
        } <= set(state)
    assert scientific_state(create_agent("A0_RANDOM", seed=1))["prediction_error"] == NOT_APPLICABLE


def test_capability_matrix_is_derived_from_actual_agent_observer_contracts():
    a0 = scientific_state(create_agent("A0_RANDOM", seed=1))
    a1 = scientific_state(create_agent("A1_REACTIVE", seed=1))
    a2 = scientific_state(create_agent("A2_GRU", seed=1))
    a3 = scientific_state(create_agent("A3_WORLD_MODEL", seed=1))
    a4 = scientific_state(create_agent("A4_ADVANCED", {"use_planner": False}, seed=1))

    # A0-A2 do not implement get_scientific_state(): normalization must state
    # absence, never infer policy, memory or prediction from private fields.
    for state in (a0, a1, a2):
        assert state["policy_logits"] == NOT_APPLICABLE
        assert state["policy_probabilities"] == NOT_APPLICABLE
        assert state["temporal_state"] == NOT_APPLICABLE
        assert state["prediction"] == NOT_APPLICABLE
        assert state["memory_summary"]["longterm_norm"] == NOT_APPLICABLE

    # A3's declared observer contract exposes temporal/world-model telemetry,
    # but not policy or long-term memory.  A4 explicitly adds memory and
    # learning summary telemetry.  These are direct contract observations,
    # not inferences from architecture labels.
    assert a3["temporal_state"] != NOT_APPLICABLE
    assert a3["prediction"] == {}
    assert a3["policy_probabilities"] == NOT_APPLICABLE
    assert a3["memory_summary"]["longterm_norm"] == NOT_APPLICABLE
    assert a4["temporal_state"] != NOT_APPLICABLE
    assert a4["memory_summary"]["longterm_norm"] != NOT_APPLICABLE
    assert a4["learning_summary"]["update_count"] == 0


def test_non_finite_scientific_telemetry_is_explicitly_not_transportable():
    class Agent:
        agent_identity = {"architecture_id": "TEST"}
        def get_scientific_state(self): return {"uncertainty": float("nan")}
        def get_internal_state(self): return {"step": 0}
    assert scientific_state(Agent())["uncertainty"] == NON_FINITE


@pytest.mark.parametrize(("probabilities", "expected_entropy"), [
    ([0.0, 1.0], 0.0), ([float("nan"), 1.0], NON_FINITE),
    ([float("inf"), 0.0], NON_FINITE), ([-float("inf"), 1.0], NON_FINITE),
    ([0.5, float("nan")], NON_FINITE), ([-0.5, 1.0], "MALFORMED"), ([], "MALFORMED"),
])
def test_policy_entropy_is_computed_before_non_finite_transport_encoding(probabilities, expected_entropy):
    class Agent:
        agent_identity = {"architecture_id": "TEST"}
        _last_action = 0
        def get_scientific_state(self): return {"probabilities": probabilities}
        def get_internal_state(self): return {"step": 0}
    state = scientific_state(Agent())
    assert state["policy_entropy"] == expected_entropy
    if probabilities == [0.0, 1.0]:
        assert state["selected_action_probability"] == 0.0
    if expected_entropy == NON_FINITE:
        assert NON_FINITE in state["policy_probabilities"]


def test_transport_projection_is_bounded_and_keeps_raw_observer_state_separate():
    class Agent:
        agent_identity = {"architecture_id": "LARGE"}
        _last_action = 0
        def get_scientific_state(self): return {"latent": list(range(10_000)), "probabilities": [1.0, 0.0]}
        def get_internal_state(self): return {"step": 7}
    raw = scientific_state(Agent())
    projection = scientific_transport_projection(raw)
    assert len(raw["latent_state"]) == 10_000
    assert projection["schema_version"] == SCIENTIFIC_TRANSPORT_SCHEMA
    assert projection["latent_state"]["count"] == 10_000
    assert len(projection["latent_state"]["preview"]) == TRANSPORT_PREVIEW_LIMIT
    assert len(json.dumps(projection, sort_keys=True).encode()) <= MAX_COGNITIVE_TRANSPORT_BYTES
