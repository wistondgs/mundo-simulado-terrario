"""Read-only scientific state plus bounded frame transport projection."""

from __future__ import annotations

import json
import math
from numbers import Integral, Real
from typing import Any, Mapping

NOT_APPLICABLE = "NOT_APPLICABLE"
NON_FINITE = "NON_FINITE"
MALFORMED = "MALFORMED"

SCIENTIFIC_TRANSPORT_SCHEMA = "terrario.scientific-cognitive-transport/v1"
TRANSPORT_PREVIEW_LIMIT = 16
MAX_TRANSPORT_MAPPING_ENTRIES = 16
MAX_TRANSPORT_STRING_CHARS = 160
MAX_TRANSPORT_KEY_CHARS = 80
MAX_TRANSPORT_SHAPE_DIMS = 8
MAX_COGNITIVE_TRANSPORT_BYTES = 16 * 1024


def _transport_value(value: Any) -> Any:
    """Detach scientific telemetry into JSON-compatible, read-only values."""
    if hasattr(value, "detach"):
        value = value.detach()
    if hasattr(value, "cpu"):
        value = value.cpu()
    if hasattr(value, "tolist"):
        return _transport_value(value.tolist())
    if isinstance(value, Mapping):
        return {str(key): _transport_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_transport_value(item) for item in value]
    if hasattr(value, "item") and not isinstance(value, (str, bytes)):
        try:
            return _transport_value(value.item())
        except (TypeError, ValueError):
            pass
    if isinstance(value, Integral) and not isinstance(value, bool):
        return int(value)
    if isinstance(value, Real) and not isinstance(value, bool):
        numeric = float(value)
        return numeric if math.isfinite(numeric) else NON_FINITE
    return value


def _numeric_values(value: Any) -> tuple[list[float] | None, bool]:
    """Read probabilities before non-finite values become transport strings."""
    if hasattr(value, "detach"):
        value = value.detach()
    if hasattr(value, "cpu"):
        value = value.cpu()
    if hasattr(value, "tolist"):
        value = value.tolist()
    if not isinstance(value, (list, tuple)):
        return None, False
    values: list[float] = []
    non_finite = False
    for item in value:
        if isinstance(item, (list, tuple)):
            nested, nested_non_finite = _numeric_values(item)
            if nested is None:
                return None, non_finite or nested_non_finite
            values.extend(nested)
            non_finite = non_finite or nested_non_finite
        elif isinstance(item, Real) and not isinstance(item, bool):
            numeric = float(item)
            non_finite = non_finite or not math.isfinite(numeric)
            values.append(numeric)
        else:
            return None, non_finite
    return values, non_finite


def _policy_entropy(probabilities: Any) -> float | str:
    if probabilities is None:
        return NOT_APPLICABLE
    values, non_finite = _numeric_values(probabilities)
    if values is None or not values:
        return MALFORMED
    if non_finite:
        return NON_FINITE
    if any(value < 0 for value in values):
        return MALFORMED
    # Zero is excluded exactly, rather than nudged with an epsilon: a policy
    # probability of zero is a valid value with a zero entropy contribution.
    return float(-sum(value * math.log(value) for value in values if value > 0))


def _selected_probability(probabilities: Any, selected_action: Any) -> float | str:
    if probabilities is None or selected_action == NOT_APPLICABLE:
        return NOT_APPLICABLE
    values, non_finite = _numeric_values(probabilities)
    if values is None or not isinstance(selected_action, int) or not 0 <= selected_action < len(values):
        return MALFORMED
    if non_finite:
        return NON_FINITE
    if any(value < 0 for value in values):
        return MALFORMED
    return values[selected_action]


def scientific_state(agent: Any) -> dict[str, Any]:
    """Return a normalized observer snapshot without mutating ``agent``."""
    raw_source = agent.get_scientific_state() if hasattr(agent, "get_scientific_state") else {}
    raw = _transport_value(raw_source)
    if not isinstance(raw, Mapping):
        raw = {}
    probabilities = raw.get("probabilities")
    probabilities_source = raw_source.get("probabilities") if isinstance(raw_source, Mapping) else None
    learning = raw.get("learning") if isinstance(raw.get("learning"), Mapping) else {}
    selected_action = _transport_value(getattr(agent, "_last_action", NOT_APPLICABLE))
    return {
        "agent_id": 0,
        "architecture_id": agent.agent_identity.get("architecture_id", type(agent).__name__) if hasattr(agent, "agent_identity") else type(agent).__name__,
        "step": raw.get("step", agent.get_internal_state().get("step", 0)),
        "policy_logits": raw.get("logits", NOT_APPLICABLE), "policy_probabilities": probabilities if probabilities is not None else NOT_APPLICABLE,
        "policy_entropy": _policy_entropy(probabilities_source), "selected_action": selected_action,
        "selected_action_probability": _selected_probability(probabilities_source, selected_action),
        "latent_state": raw.get("latent", NOT_APPLICABLE), "temporal_state": raw.get("temporal", NOT_APPLICABLE),
        "memory_summary": {"episodic_size": raw.get("episodic_memory_size", NOT_APPLICABLE), "longterm_norm": raw.get("longterm_memory_norm", NOT_APPLICABLE)},
        "prediction": raw.get("prediction", NOT_APPLICABLE), "prediction_error": raw.get("prediction_error", NOT_APPLICABLE),
        "uncertainty": raw.get("uncertainty", NOT_APPLICABLE), "current_loss": raw.get("current_loss", NOT_APPLICABLE),
        "gradient_norm": raw.get("gradient_norm", NOT_APPLICABLE), "parameter_delta_norm": raw.get("parameter_delta_norm", NOT_APPLICABLE),
        "learning_summary": {"update_count": learning.get("updates", NOT_APPLICABLE), "online_learning": learning.get("online_learning", NOT_APPLICABLE)},
        "active_ablations": raw.get("active_ablations", []),
    }


def _shape_and_scalars(value: Any) -> tuple[list[int], list[float], int]:
    if isinstance(value, (list, tuple)):
        children = [_shape_and_scalars(item) for item in value]
        shape = [len(value)]
        if children and all(child[0] == children[0][0] for child in children):
            shape.extend(children[0][0])
        return shape, [number for _shape, numbers, _nonfinite in children for number in numbers], sum(child[2] for child in children)
    if isinstance(value, Real) and not isinstance(value, bool):
        number = float(value)
        return [], [number] if math.isfinite(number) else [], 0 if math.isfinite(number) else 1
    return [], [], 1 if value == NON_FINITE else 0


def _bounded_projection(value: Any) -> Any:
    if value is None or (isinstance(value, str) and value in {NOT_APPLICABLE, NON_FINITE, MALFORMED}):
        return value
    if isinstance(value, Integral) and not isinstance(value, bool):
        return int(value)
    if isinstance(value, Real) and not isinstance(value, bool):
        return float(value)
    if isinstance(value, str):
        return value[:MAX_TRANSPORT_STRING_CHARS]
    if isinstance(value, (list, tuple)):
        shape, values, non_finite_count = _shape_and_scalars(value)
        finite_count = len(values)
        return {
            "kind": "ARRAY_PROJECTION", "shape": shape[:MAX_TRANSPORT_SHAPE_DIMS],
            "shape_truncated": len(shape) > MAX_TRANSPORT_SHAPE_DIMS,
            "count": finite_count + non_finite_count,
            "finite_count": finite_count, "non_finite_count": non_finite_count,
            "norm": math.sqrt(sum(number * number for number in values)) if values else 0.0,
            "min": min(values) if values else None, "max": max(values) if values else None,
            "mean": sum(values) / finite_count if finite_count else None,
            "preview": [_bounded_projection(item) for item in value[:TRANSPORT_PREVIEW_LIMIT]],
            "preview_truncated": len(value) > TRANSPORT_PREVIEW_LIMIT,
        }
    if isinstance(value, Mapping):
        entries = sorted(value.items(), key=lambda item: str(item[0]))[:MAX_TRANSPORT_MAPPING_ENTRIES]
        return {"kind": "MAPPING_PROJECTION", "entries": {str(key)[:MAX_TRANSPORT_KEY_CHARS]: _bounded_projection(item) for key, item in entries},
                "truncated": len(value) > MAX_TRANSPORT_MAPPING_ENTRIES}
    return MALFORMED


def scientific_transport_projection(state: Mapping[str, Any]) -> dict[str, Any]:
    """Create the bounded UI/SSE representation without replacing raw evidence."""
    payload = {
        "schema_version": SCIENTIFIC_TRANSPORT_SCHEMA,
        "preview_limit": TRANSPORT_PREVIEW_LIMIT,
        "raw_evidence": "OBSERVER_ARTIFACT",
        **{key: _bounded_projection(value) for key, value in state.items()},
    }
    if len(json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()) > MAX_COGNITIVE_TRANSPORT_BYTES:
        raise ValueError("COGNITIVE_TRANSPORT_BUDGET_EXCEEDED")
    return payload
