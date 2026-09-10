"""Non-invasive static descriptors and sandbox runtime read models."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from terrario.agent.agents import create_agent
from terrario.lab.capabilities import CapabilityAssessment, audited_agent_assessments

INTERPRETATION_WARNING = "INTERPRETATION_REQUIRES_ANALYSIS"


@dataclass(frozen=True)
class AgentModuleDescriptor:
    name: str
    class_name: str
    active: bool | str
    interpretation: str = "INTERNAL_STATE"


@dataclass(frozen=True)
class AgentDescriptor:
    agent_id: str
    class_name: str
    source: str
    configuration: dict[str, Any]
    modules: tuple[AgentModuleDescriptor, ...]
    parameter_count: int
    trainable_parameter_count: int
    device: str
    interfaces: tuple[str, ...]
    serialization: str
    supported_ablations: tuple[str, ...]
    capabilities: tuple[CapabilityAssessment, ...]
    warning: str = INTERPRETATION_WARNING


@dataclass(frozen=True)
class AgentRuntimeSnapshot:
    availability: str
    run_id: str | None
    classification: str | None
    step: int | None
    current_action: Any
    scientific_state: Any
    observer_payload_in_agent_internals: bool = False
    warning: str = INTERPRETATION_WARNING


class AgentInspector:
    IDS = ("A0", "A1", "A2", "A3", "A4")

    def describe(self, agent_id: str) -> AgentDescriptor:
        aid = agent_id.upper().split("_")[0]
        if aid not in self.IDS: raise KeyError(agent_id)
        agent = create_agent(aid, {"num_channels": 4, "view_size": 5}, seed=0, device="cpu")
        modules = []
        for name, value in vars(agent).items():
            if hasattr(value, "parameters"):
                active = any(p.requires_grad for p in value.parameters())
                modules.append(AgentModuleDescriptor(name, type(value).__name__, active))
        config = dict(getattr(agent, "config", {}))
        ablations = tuple(sorted(k for k in config if k.startswith("use_")))
        return AgentDescriptor(aid, type(agent).__name__, f"{type(agent).__module__}:{type(agent).__name__}",
            config, tuple(modules), agent.parameter_count(), agent.parameter_count(),
            str(agent.agent_identity["device"]),
            ("perceive", "decide", "learn", "reset", "get_parameters", "set_parameters"),
            "get_parameters/set_parameters", ablations, audited_agent_assessments(aid))

    def all(self) -> tuple[AgentDescriptor, ...]:
        return tuple(self.describe(aid) for aid in self.IDS)

    def runtime(self, sandbox_service, run_id: str | None) -> AgentRuntimeSnapshot:
        if not run_id:
            return AgentRuntimeSnapshot("NOT_EXPOSED", None, None, None, "NOT_EXPOSED", "NOT_EXPOSED")
        try: run = sandbox_service.get(run_id)
        except KeyError:
            return AgentRuntimeSnapshot("NOT_EXPOSED", run_id, None, None, "NOT_EXPOSED", "NOT_EXPOSED")
        if not run.timeline:
            return AgentRuntimeSnapshot("NOT_EXPOSED", run_id, "ENGINEERING_SANDBOX", None, "NOT_EXPOSED", "NOT_EXPOSED")
        trace = run.timeline[-1]
        return AgentRuntimeSnapshot("AVAILABLE", run_id, "ENGINEERING_SANDBOX", trace.step,
            trace.agent_action, trace.scientific_state)
