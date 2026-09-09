"""Read-only normalized scientific state for every supported architecture."""

from __future__ import annotations

import math
from typing import Any

NOT_APPLICABLE = "NOT_APPLICABLE"


def scientific_state(agent: Any) -> dict[str, Any]:
    """Return a normalized observer snapshot without mutating ``agent``."""
    raw = agent.get_scientific_state() if hasattr(agent, "get_scientific_state") else {}
    probabilities = raw.get("probabilities")
    entropy = NOT_APPLICABLE
    if probabilities is not None:
        values = probabilities.detach().cpu().tolist() if hasattr(probabilities, "detach") else probabilities
        entropy = float(-sum(value * math.log(value + 1e-12) for value in values if value > 0))
    return {
        "agent_id": 0,
        "architecture_id": agent.agent_identity.get("architecture_id", type(agent).__name__) if hasattr(agent, "agent_identity") else type(agent).__name__,
        "step": raw.get("step", agent.get_internal_state().get("step", 0)),
        "policy_logits": raw.get("logits", NOT_APPLICABLE), "policy_probabilities": probabilities if probabilities is not None else NOT_APPLICABLE,
        "policy_entropy": entropy, "selected_action": getattr(agent, "_last_action", NOT_APPLICABLE),
        "latent_state": raw.get("latent", NOT_APPLICABLE), "temporal_state": raw.get("temporal", NOT_APPLICABLE),
        "memory_summary": {"episodic_size": raw.get("episodic_memory_size", NOT_APPLICABLE), "longterm_norm": raw.get("longterm_memory_norm", NOT_APPLICABLE)},
        "prediction": raw.get("prediction", NOT_APPLICABLE), "prediction_error": raw.get("prediction_error", NOT_APPLICABLE),
        "uncertainty": raw.get("uncertainty", NOT_APPLICABLE), "current_loss": raw.get("current_loss", NOT_APPLICABLE),
        "gradient_norm": raw.get("gradient_norm", NOT_APPLICABLE), "parameter_delta_norm": raw.get("parameter_delta_norm", NOT_APPLICABLE),
        "active_ablations": raw.get("active_ablations", []),
    }
