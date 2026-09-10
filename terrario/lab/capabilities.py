"""Evidence-backed capability registry and scenario compatibility for LAB-UI-02C."""
from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Iterable

from terrario.lab.world_contracts import ScenarioDefinition, scientific_hash

SCHEMA_VERSION = "terrario.lab.capability/v1"


class CapabilityStatus(StrEnum):
    SUPPORTED = "SUPPORTED"
    PARTIAL = "PARTIAL"
    MISSING = "MISSING"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    UNKNOWN = "UNKNOWN"
    UNVERIFIED = "UNVERIFIED"


class SupportBasis(StrEnum):
    STRUCTURAL_INTERFACE = "STRUCTURAL_INTERFACE"
    CONFIGURATION = "CONFIGURATION"
    RUNTIME_PROBE = "RUNTIME_PROBE"
    TEST_EVIDENCE = "TEST_EVIDENCE"
    HISTORICAL_RESULT = "HISTORICAL_RESULT"
    MANUAL_ASSERTION = "MANUAL_ASSERTION"


class Necessity(StrEnum):
    REQUIRED = "REQUIRED"
    OPTIONAL = "OPTIONAL"
    CONTROL_DEPENDENT = "CONTROL_DEPENDENT"
    NOT_REQUIRED = "NOT_REQUIRED"


class CompatibilityStatus(StrEnum):
    COMPATIBLE = "COMPATIBLE"
    PARTIALLY_COMPATIBLE = "PARTIALLY_COMPATIBLE"
    MISSING_REQUIRED_CAPABILITY = "MISSING_REQUIRED_CAPABILITY"
    INVALID_INTERFACE = "INVALID_INTERFACE"
    UNVERIFIED = "UNVERIFIED"
    NOT_EVALUABLE = "NOT_EVALUABLE"


@dataclass(frozen=True)
class CapabilityDefinition:
    capability_id: str
    title: str
    definition: str
    schema_version: str = SCHEMA_VERSION


@dataclass(frozen=True)
class CapabilityEvidence:
    basis: SupportBasis
    reference: str
    statement: str
    verified_version: str


@dataclass(frozen=True)
class CapabilityAssessment:
    agent_id: str
    capability: str
    status: CapabilityStatus
    evidence: tuple[CapabilityEvidence, ...]
    limitations: tuple[str, ...] = ()
    last_verified_version: str = "LAB-UI-02C"

    def __post_init__(self):
        if self.status == CapabilityStatus.SUPPORTED and not self.evidence:
            raise ValueError("SUPPORTED requires an evidence reference")


@dataclass(frozen=True)
class CapabilityRequirement:
    capability: str
    necessity: Necessity
    minimum_contract: str
    reason: str
    provenance: str


@dataclass(frozen=True)
class CompatibilityReport:
    scenario_id: str
    agent_id: str
    status: CompatibilityStatus
    execution_compatible: bool
    technical_blockers: tuple[str, ...]
    satisfied: tuple[str, ...]
    partial: tuple[str, ...]
    missing: tuple[str, ...]
    unverifiable: tuple[str, ...]
    optional_absent: tuple[str, ...]
    provenance: tuple[str, ...]
    cognitive_expectation_blocks_execution: bool = False


_TAXONOMY = (
    "perception", "temporal_state", "working_memory", "episodic_memory",
    "world_model", "prediction", "uncertainty_estimation", "online_learning",
    "planning", "credit_assignment", "transfer", "adaptation", "communication",
    "tool_use", "self_modification",
)


class CapabilityRegistry:
    """Extensible registry; names alone never produce assessments."""

    def __init__(self):
        self._definitions = {
            name: CapabilityDefinition(name, name.replace("_", " ").title(),
                f"Operational capability contract for {name}; support requires explicit evidence.")
            for name in _TAXONOMY
        }

    def register(self, definition: CapabilityDefinition) -> None:
        self._definitions[definition.capability_id] = definition

    def definitions(self) -> tuple[CapabilityDefinition, ...]:
        return tuple(self._definitions[k] for k in sorted(self._definitions))


def _e(basis: SupportBasis, reference: str, statement: str) -> tuple[CapabilityEvidence, ...]:
    return (CapabilityEvidence(basis, reference, statement, "source@LAB-UI-02C"),)


def audited_agent_assessments(agent_id: str) -> tuple[CapabilityAssessment, ...]:
    """Curated source audit. No class/module-name heuristic is used here."""
    aid = agent_id.upper().split("_")[0]
    source = {
        "A0": "terrario.agent.agents.a0_random:A0Random",
        "A1": "terrario.agent.agents.a1_reactive:A1Reactive",
        "A2": "terrario.agent.agents.a2_gru:A2GRUBaseline",
        "A3": "terrario.agent.agents.a3_worldmodel:A3WorldModel",
        "A4": "terrario.agent.agents.a4_advanced:A4Advanced",
    }.get(aid)
    if source is None:
        return tuple(CapabilityAssessment(agent_id, c, CapabilityStatus.UNKNOWN, ()) for c in _TAXONOMY)
    supported = {"perception"}
    missing: set[str] = set()
    partial: set[str] = set()
    if aid == "A0":
        missing |= {"temporal_state", "working_memory", "episodic_memory", "world_model", "prediction", "uncertainty_estimation", "online_learning", "planning"}
    elif aid == "A1":
        supported |= {"online_learning", "credit_assignment"}
        missing |= {"temporal_state", "working_memory", "episodic_memory", "world_model", "prediction", "uncertainty_estimation", "planning"}
    elif aid == "A2":
        supported |= {"temporal_state", "working_memory", "online_learning", "credit_assignment"}
        missing |= {"episodic_memory", "world_model", "prediction", "uncertainty_estimation", "planning"}
    elif aid == "A3":
        supported |= {"temporal_state", "working_memory", "world_model", "prediction", "online_learning", "credit_assignment"}
        missing |= {"episodic_memory", "uncertainty_estimation", "planning"}
    elif aid == "A4":
        supported |= {"temporal_state", "working_memory", "episodic_memory", "world_model", "prediction", "uncertainty_estimation", "online_learning", "planning", "credit_assignment"}
        partial |= {"adaptation"}
    rows = []
    for capability in _TAXONOMY:
        if capability in supported:
            evidence = _e(SupportBasis.STRUCTURAL_INTERFACE, source, f"audited implementation exposes the {capability} contract")
            status = CapabilityStatus.SUPPORTED
        elif capability in missing:
            evidence = _e(SupportBasis.STRUCTURAL_INTERFACE, source, f"source contract explicitly omits or disables {capability}")
            status = CapabilityStatus.MISSING
        elif capability in partial:
            evidence = _e(SupportBasis.CONFIGURATION, source + ":DEFAULT_CONFIG", "online update mechanisms exist; cross-condition adaptation is not established")
            status = CapabilityStatus.PARTIAL
        else:
            evidence = ()
            status = CapabilityStatus.UNKNOWN
        rows.append(CapabilityAssessment(aid, capability, status, evidence,
            ("structural support is not scientific competence",) if status in {CapabilityStatus.SUPPORTED, CapabilityStatus.PARTIAL} else ()))
    return tuple(rows)


def scenario_requirements(scenario: ScenarioDefinition) -> tuple[CapabilityRequirement, ...]:
    """Versioned explicit adapter from the scenario contract, never its display name."""
    provenance = f"{scenario.schema_version}:{scenario.content_hash}"
    rows = [CapabilityRequirement("perception", Necessity.REQUIRED,
        "AgentInterface.perceive(Observation)", "scenario declares an observation contract", provenance)]
    # These are explicitly encoded technical contracts, not cognitive claims.
    rows.append(CapabilityRequirement("online_learning", Necessity.CONTROL_DEPENDENT,
        "AgentInterface.learn(Transition)", "learning may be disabled or absent in a valid control", provenance))
    return tuple(rows)


def requirements_hash(requirements: Iterable[CapabilityRequirement]) -> str:
    return scientific_hash(tuple(requirements))


def assess_compatibility(scenario: ScenarioDefinition, agent_id: str,
                         observation_interface: bool = True, action_interface: bool = True,
                         device_compatible: bool = True, reset_interface: bool = True) -> CompatibilityReport:
    technical = []
    if not observation_interface: technical.append("INVALID_OBSERVATION_INTERFACE")
    if not action_interface: technical.append("INVALID_ACTION_INTERFACE")
    if not device_compatible: technical.append("UNSUPPORTED_DEVICE")
    if not reset_interface: technical.append("INVALID_RESET_INTERFACE")
    assessments = {x.capability: x for x in audited_agent_assessments(agent_id)}
    satisfied = []; partial = []; missing = []; unknown = []; optional = []; refs = []
    for req in scenario_requirements(scenario):
        row = assessments.get(req.capability)
        if row is None or row.status in {CapabilityStatus.UNKNOWN, CapabilityStatus.UNVERIFIED}:
            unknown.append(req.capability)
        elif row.status == CapabilityStatus.SUPPORTED:
            satisfied.append(req.capability); refs.extend(e.reference for e in row.evidence)
        elif row.status == CapabilityStatus.PARTIAL:
            partial.append(req.capability)
        elif row.status == CapabilityStatus.MISSING:
            (optional if req.necessity in {Necessity.OPTIONAL, Necessity.CONTROL_DEPENDENT} else missing).append(req.capability)
    if technical: status = CompatibilityStatus.INVALID_INTERFACE
    elif missing: status = CompatibilityStatus.MISSING_REQUIRED_CAPABILITY
    elif unknown: status = CompatibilityStatus.UNVERIFIED
    elif partial: status = CompatibilityStatus.PARTIALLY_COMPATIBLE
    else: status = CompatibilityStatus.COMPATIBLE
    return CompatibilityReport(scenario.scenario_id, agent_id, status, not technical,
        tuple(technical), tuple(satisfied), tuple(partial), tuple(missing), tuple(unknown),
        tuple(optional), tuple(sorted(set(refs))))
