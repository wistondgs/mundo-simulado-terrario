from terrario.agent.agents import create_agent
from terrario.agent.scientific import NOT_APPLICABLE, scientific_state


def test_every_architecture_exposes_normalized_read_only_scientific_fields():
    for architecture in ("A0_RANDOM", "A1_REACTIVE", "A2_GRU", "A3_WORLD_MODEL", "A4_ADVANCED"):
        state = scientific_state(create_agent(architecture, {"use_planner": False}, seed=1))
        assert {
            "architecture_id", "policy_logits", "memory_summary", "prediction_error",
            "parameter_delta_norm", "active_ablations",
        } <= set(state)
    assert scientific_state(create_agent("A0_RANDOM", seed=1))["prediction_error"] == NOT_APPLICABLE
