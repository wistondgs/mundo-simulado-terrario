"""Explicit factory for all supported Terrario agent architectures."""

from __future__ import annotations

import hashlib
from typing import Any

import torch

from terrario.agent.agents.a0_random import A0Random
from terrario.agent.agents.a1_reactive import A1Reactive
from terrario.agent.agents.a2_gru import A2GRUBaseline
from terrario.agent.agents.a3_worldmodel import A3WorldModel
from terrario.agent.agents.a4_advanced import A4Advanced


class AgentFactoryError(ValueError):
    """Raised when a requested architecture cannot be instantiated exactly."""


_AGENT_IDS = {
    "A0": "A0_RANDOM",
    "A0_RANDOM": "A0_RANDOM",
    "A1": "A1_REACTIVE",
    "A1_REACTIVE": "A1_REACTIVE",
    "A2": "A2_GRU",
    "A2_GRU": "A2_GRU",
    "A2_GRU_BASELINE": "A2_GRU",
    "A3": "A3_WORLD_MODEL",
    "A3_WORLD_MODEL": "A3_WORLD_MODEL",
    "A4": "A4_ADVANCED",
    "A4_ADVANCED": "A4_ADVANCED",
}


def _parameter_hash(agent: Any) -> str:
    digest = hashlib.sha256()
    for name, tensor in sorted(agent.get_parameters().items()):
        digest.update(name.encode())
        digest.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


def create_agent(
    agent_spec: str | dict[str, Any],
    config: dict[str, Any] | None = None,
    seed: int = 0,
    device: str | torch.device = "cpu",
) -> Any:
    """Instantiate exactly the requested agent or raise ``AgentFactoryError``.

    No fallback architecture is permitted. ``agent_spec`` may be an ID or a
    mapping containing ``agent_id`` and optional local configuration.
    """
    spec = dict(agent_spec) if isinstance(agent_spec, dict) else {"agent_id": agent_spec}
    requested_agent_id = str(spec.get("agent_id", ""))
    architecture_id = _AGENT_IDS.get(requested_agent_id.upper())
    if architecture_id is None:
        raise AgentFactoryError(f"Unsupported agent '{requested_agent_id}'")

    target_device = torch.device(device)
    if target_device.type == "cuda" and not torch.cuda.is_available():
        raise AgentFactoryError("CUDA was requested but is unavailable on this host")

    agent_config = {**(config or {}), **spec.get("config", {})}
    generator = torch.Generator(device="cpu")
    generator.manual_seed(seed)
    common = {
        "num_channels": int(agent_config.get("num_channels", 4)),
        "view_size": int(agent_config.get("view_size", 5)),
        "latent_dim": int(agent_config.get("latent_dim", 128)),
        "lr": float(agent_config.get("learning_rate", agent_config.get("lr", 3e-4))),
        "generator": generator,
    }

    try:
        if architecture_id == "A0_RANDOM":
            agent = A0Random(generator=generator)
        elif architecture_id == "A1_REACTIVE":
            agent = A1Reactive(**common)
        elif architecture_id == "A2_GRU":
            agent = A2GRUBaseline(
                **common,
                hidden_dim=int(agent_config.get("hidden_dim", 256)),
            )
        elif architecture_id == "A3_WORLD_MODEL":
            agent = A3WorldModel(
                **common,
                hidden_dim=int(agent_config.get("hidden_dim", 256)),
            )
        else:
            agent = A4Advanced(config=agent_config, generator=generator)
    except Exception as exc:
        raise AgentFactoryError(
            f"Could not instantiate requested agent '{requested_agent_id}'"
        ) from exc

    for value in vars(agent).values():
        if isinstance(value, torch.nn.Module):
            value.to(target_device)

    agent.agent_identity = {
        "requested_agent_id": requested_agent_id,
        "instantiated_agent_class": type(agent).__name__,
        "architecture_id": architecture_id,
        "parameter_count": agent.parameter_count(),
        "device": str(target_device),
        "initial_parameters_hash": _parameter_hash(agent),
    }
    return agent


__all__ = [
    "A0Random", "A1Reactive", "A2GRUBaseline", "A3WorldModel", "A4Advanced",
    "AgentFactoryError", "create_agent",
]
