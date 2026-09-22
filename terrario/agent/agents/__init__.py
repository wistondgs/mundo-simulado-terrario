"""Explicit factory for all supported Terrario agent architectures."""

from __future__ import annotations

import hashlib
from contextlib import contextmanager
from typing import Any

import torch

from terrario.agent.device import resolve_device
from terrario.agent.agents.a0_random import A0Random
from terrario.agent.agents.a1_reactive import A1Reactive
from terrario.agent.agents.a2_gru import A2GRUBaseline
from terrario.agent.agents.a3_worldmodel import A3WorldModel
from terrario.agent.agents.a4_advanced import A4Advanced
from terrario.agent.agents.a5_cybernetic import A5Cybernetic


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
    "A5": "A5_CYBERNETIC",
    "A5_CYBERNETIC": "A5_CYBERNETIC",
}


def _parameter_hash(agent: Any) -> str:
    digest = hashlib.sha256()
    for name, tensor in sorted(agent.get_parameters().items()):
        digest.update(name.encode())
        digest.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


@contextmanager
def _global_torch_seed(seed: int):
    """Hold the global torch RNG at ``seed`` while an agent is constructed.

    The ``generator`` that ``create_agent`` builds is the agent's *sampling*
    stream and nothing else. Module weights come from the GLOBAL torch RNG:
    every ``nn.Linear`` and ``nn.Conv2d`` draws from it, and so do the
    hand-written parameters in `memory.py:156` and `temporal.py:81-83`, which
    call ``torch.randn`` with no generator. So a signature that accepts a
    ``seed`` and returns an agent was promising something it did not deliver --
    two calls with the same seed produced different weights, and nothing
    complained.

    The determinism was really supplied by the caller: the scientific path and
    every bench seeded the global RNG by hand on the line immediately above
    their ``create_agent``. That line belongs here, where the promise is made,
    so that a caller who trusts the argument is not silently wrong. The paths
    that already seeded are unaffected -- they seeded with this same value and
    nothing between their seeding and this call consumes the global torch RNG.

    The prior state is restored on exit so that constructing an agent stays
    invisible to whatever stream the caller was drawing from: the factory fixes
    its own randomness instead of spending the caller's.

    Only the CPU generator is touched, and deliberately so. Every module is
    built on CPU and moved to the target device afterwards, so no device stream
    is consumed here; ``torch.manual_seed`` would additionally reseed the CUDA
    generators -- lazily, and so unrestorably when CUDA has not been
    initialised yet -- which would make this helper reach past what it needs.
    Writing a freshly seeded generator's state into the default one is the same
    thing ``torch.manual_seed`` does to the CPU side, and nothing more.
    """
    previous = torch.random.get_rng_state()
    torch.random.set_rng_state(torch.Generator().manual_seed(seed).get_state())
    try:
        yield
    finally:
        torch.random.set_rng_state(previous)


def create_agent(
    agent_spec: str | dict[str, Any],
    config: dict[str, Any] | None = None,
    seed: int = 0,
    device: str | torch.device = "cpu",
) -> Any:
    """Instantiate exactly the requested agent or raise ``AgentFactoryError``.

    No fallback architecture is permitted. ``agent_spec`` may be an ID or a
    mapping containing ``agent_id`` and optional local configuration.

    ``seed`` determines the whole object: both the sampling generator and the
    module weights, which come from the global torch RNG (see
    ``_global_torch_seed``). Two calls with the same spec, config and seed
    return agents with the same ``initial_parameters_hash``, in the same
    process and across processes, and neither call disturbs the caller's
    global RNG stream.
    """
    spec = dict(agent_spec) if isinstance(agent_spec, dict) else {"agent_id": agent_spec}
    requested_agent_id = str(spec.get("agent_id", ""))
    architecture_id = _AGENT_IDS.get(requested_agent_id.upper())
    if architecture_id is None:
        raise AgentFactoryError(f"Unsupported agent '{requested_agent_id}'")

    try:
        target_device = resolve_device(device)
    except RuntimeError as exc:
        raise AgentFactoryError(f"Requested device '{device}' is unavailable: {exc}") from exc

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
        with _global_torch_seed(seed):
            if architecture_id == "A0_RANDOM":
                agent = A0Random(generator=generator,
                    addressing_mode=str(agent_config.get("addressing_mode", "T0_DIRECTIONAL")))
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
            elif architecture_id == "A5_CYBERNETIC":
                agent = A5Cybernetic(config=agent_config, generator=generator)
            else:
                agent = A4Advanced(config=agent_config, generator=generator)
    except Exception as exc:
        raise AgentFactoryError(
            f"Could not instantiate requested agent '{requested_agent_id}'"
        ) from exc

    for value in vars(agent).values():
        if isinstance(value, torch.nn.Module):
            value.to(target_device)
    for name in ("_hidden", "_last_hidden", "_last_latent", "_last_state", "_last_log_prob"):
        value = getattr(agent, name, None)
        if isinstance(value, torch.Tensor):
            setattr(agent, name, value.to(target_device))

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
    "A0Random", "A1Reactive", "A2GRUBaseline", "A3WorldModel", "A4Advanced", "A5Cybernetic",
    "AgentFactoryError", "create_agent",
]
