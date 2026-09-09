import torch

from terrario.agent.device import device_status, resolve_device


def test_device_status_reports_cuda_unavailability_without_cpu_fallback(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)

    status = device_status("cuda")

    assert status["available"] is False
    assert status["resolved"] == "cuda"
    assert status["reason"] == "cuda_requested_but_unavailable"


def test_auto_device_has_explicit_cpu_fallback(monkeypatch):
    monkeypatch.setattr(torch.cuda, "is_available", lambda: False)

    assert resolve_device("auto").type == "cpu"
