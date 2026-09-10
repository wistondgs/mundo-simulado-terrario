from pathlib import Path

from terrario.lab.agent_inspector import AgentInspector
from terrario.lab.capabilities import (
    CapabilityAssessment, CapabilityEvidence, CapabilityStatus, SupportBasis,
    assess_compatibility, audited_agent_assessments, requirements_hash,
    scenario_requirements,
)
from terrario.lab.world_registry import WorldScenarioRegistry


def scenario(identifier="D2"):
    return WorldScenarioRegistry(Path(".")).get(identifier).scenario


def test_supported_requires_evidence_and_is_not_derived_from_name():
    try:
        CapabilityAssessment("FAKE_WORLD_MODEL", "world_model", CapabilityStatus.SUPPORTED, ())
        assert False
    except ValueError:
        pass
    fake = audited_agent_assessments("agent_named_world_model")
    assert next(x for x in fake if x.capability == "world_model").status == CapabilityStatus.UNKNOWN


def test_unknown_is_distinct_from_missing():
    rows = audited_agent_assessments("A0")
    assert next(x for x in rows if x.capability == "planning").status == CapabilityStatus.MISSING
    assert next(x for x in rows if x.capability == "communication").status == CapabilityStatus.UNKNOWN


def test_supported_retains_evidence_reference():
    row = next(x for x in audited_agent_assessments("A4") if x.capability == "world_model")
    assert row.status == CapabilityStatus.SUPPORTED
    assert row.evidence[0].basis == SupportBasis.STRUCTURAL_INTERFACE
    assert "a4_advanced" in row.evidence[0].reference


def test_scenario_requirements_are_versioned_reproducible():
    first = scenario_requirements(scenario())
    assert first == scenario_requirements(scenario())
    assert requirements_hash(first) == requirements_hash(scenario_requirements(scenario()))
    assert all(x.provenance.startswith("terrario.lab.world/v1:") for x in first)


def test_control_can_lack_cognitive_capability_and_remain_execution_compatible():
    report = assess_compatibility(scenario(), "A0")
    assert report.execution_compatible is True
    assert report.cognitive_expectation_blocks_execution is False
    assert "online_learning" in report.optional_absent


def test_invalid_observation_or_action_interface_is_technical_blocker():
    report = assess_compatibility(scenario(), "A4", observation_interface=False)
    assert report.status == "INVALID_INTERFACE"
    assert report.execution_compatible is False
    assert "INVALID_OBSERVATION_INTERFACE" in report.technical_blockers


def test_a0_a4_static_inspection_uses_real_parameter_counts_without_mutation():
    before = {p: p.read_bytes() for p in Path("terrario/agent/agents").glob("a[0-4]*.py")}
    descriptors = AgentInspector().all()
    after = {p: p.read_bytes() for p in before}
    assert [x.agent_id for x in descriptors] == ["A0", "A1", "A2", "A3", "A4"]
    assert descriptors[0].parameter_count == 0
    assert all(x.parameter_count >= 0 and x.parameter_count == x.trainable_parameter_count for x in descriptors)
    assert before == after


def test_runtime_absence_is_not_fiction_and_internal_state_is_not_a_concept():
    snap = AgentInspector().runtime(type("S", (), {"get": lambda *_: (_ for _ in ()).throw(KeyError())})(), "missing")
    assert snap.availability == "NOT_EXPOSED"
    assert snap.scientific_state == "NOT_EXPOSED"
    assert snap.warning == "INTERPRETATION_REQUIRES_ANALYSIS"
    assert "concept" not in snap.warning.lower()
