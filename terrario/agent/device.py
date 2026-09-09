"""Central device selection and diagnostics for Terrario agents."""

from __future__ import annotations

from typing import Any

import torch


def device_status(requested: str | torch.device = "auto") -> dict[str, Any]:
    requested_name = str(requested).lower()
    if requested_name not in {"auto", "cpu", "cuda"}:
        return {
            "requested": requested_name, "resolved": None, "available": False,
            "reason": "unsupported_device",
        }
    cuda_available = torch.cuda.is_available()
    resolved = "cuda" if requested_name == "auto" and cuda_available else "cpu" if requested_name == "auto" else requested_name
    available = resolved != "cuda" or cuda_available
    status: dict[str, Any] = {
        "requested": requested_name,
        "resolved": resolved,
        "available": available,
        "cuda_available": cuda_available,
        "torch_version": torch.__version__,
        "torch_cuda_version": torch.version.cuda,
        "cuda_device_count": torch.cuda.device_count() if cuda_available else 0,
    }
    if cuda_available:
        status["cuda_device_name"] = torch.cuda.get_device_name(0)
    elif resolved == "cuda":
        status["reason"] = "cuda_requested_but_unavailable"
    return status


def resolve_device(requested: str | torch.device = "auto") -> torch.device:
    status = device_status(requested)
    if not status["available"]:
        raise RuntimeError(status.get("reason", "requested_device_unavailable"))
    return torch.device(status["resolved"])
