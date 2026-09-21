"""The bridge from a formalised capability to the code that realises it.

One positive proof and six mutants.  The positive one matters as much as the
rest: it must reach `A4Advanced.learn` without anyone restating which algorithm
belongs to which capability, because restating it is the manual step this
exists to remove.
"""

from __future__ import annotations

from dataclasses import replace

import pytest

from terrario.lab import mechanism_spec as mechanisms
from terrario.lab.capability_bridge import (
    BridgeRefused, algorithm_index, resolve_capability,
    assert_configuration_is_read_by_the_implementation,
)
from terrario.lab.capability_passport import REGISTRY as PASSPORTS


# --- la prueba positiva ------------------------------------------------------------

def test_the_capability_addresses_its_own_implementation_with_no_human_restating_it():
    resolved = resolve_capability("LEARN-A1-V2")

    assert resolved.mechanism.mechanism_id == "online-gradient-update"
    assert resolved.algorithm_id == "OnlineLearner"
    assert resolved.implementation_path == (
        "terrario.agent.agents.a4_advanced:A4Advanced.learn")
    assert callable(resolved.implementation)
    assert resolved.implementation.__qualname__ == "A4Advanced.learn"
    assert resolved.endpoint_id == "conversion_aprendizaje"


def test_the_configuration_it_dictates_is_the_one_the_implementation_reads():
    """Checked against the source, not asserted.

    A passport promising `learning_rate` against an implementation reading `lr`
    is a contract nobody can act on, and neither side would complain."""
    resolved = resolve_capability("LEARN-A1-V2")
    assert resolved.agent_configuration["use_online_learning"] is True
    assert set(resolved.agent_configuration) == {
        "use_online_learning", "learning_rate", "grad_clip", "update_frequency"}
    assert assert_configuration_is_read_by_the_implementation(resolved) == ()


def test_the_mechanism_is_not_the_implementation():
    """The split the whole schema exists for, at the far end of the chain."""
    resolved = resolve_capability("LEARN-A1-V2")
    assert resolved.mechanism.mechanism_id != resolved.algorithm_id
    assert not (set(mechanisms.MechanismSpec.__dataclass_fields__)
                & {"algorithm_id", "implementation_id"})


# --- los mutantes --------------------------------------------------------------------

def test_an_unknown_capability_is_refused():
    with pytest.raises(BridgeRefused) as refused:
        resolve_capability("NO-EXISTE")
    assert refused.value.codes == ("UNKNOWN_CAPABILITY:NO-EXISTE",)


def test_a_changed_mechanism_breaks_the_route(monkeypatch):
    """Semantic drift under the same version: the code did not move, the
    promise did."""
    alterado = replace(mechanisms.REGISTRY[("online-gradient-update", 1)],
                       semantic_definition="something else")
    monkeypatch.setitem(mechanisms.REGISTRY, ("online-gradient-update", 1), alterado)
    with pytest.raises(BridgeRefused) as refused:
        resolve_capability("LEARN-A1-V2")
    # Sale como código y no como excepción cruda: el puente falla cerrado y
    # dice cuál de las tres derivas ocurrió, que es lo accionable.
    assert refused.value.codes == ("MECHANISM_SPEC_DRIFT:LEARN-A1-V2",)


def test_a_binding_to_another_algorithm_breaks_the_route(monkeypatch):
    passport = replace(PASSPORTS["LEARN-A1-V2"], algorithm_id="SomeOtherLearner")
    monkeypatch.setitem(PASSPORTS, "LEARN-A1-V2", passport)
    with pytest.raises(BridgeRefused) as refused:
        resolve_capability("LEARN-A1-V2")
    assert any(c.startswith("NO_IMPLEMENTATION_FOR_ALGORITHM") for c in refused.value.codes)


def test_a_v2_passport_without_an_acquisition_target_cannot_address_anything(monkeypatch):
    """Refused before the walk starts: without knowing what must be acquired,
    addressing an implementation would build something nobody is measuring."""
    passport = PASSPORTS["LEARN-A1-V2"]
    roto = object.__new__(type(passport))
    for name, value in vars(passport).items():
        object.__setattr__(roto, name, value)
    object.__setattr__(roto, "acquisition_target", ())
    monkeypatch.setitem(PASSPORTS, "LEARN-A1-V2", roto)
    with pytest.raises(BridgeRefused) as refused:
        resolve_capability("LEARN-A1-V2")
    assert "MISSING:acquisition_target" in refused.value.codes


def test_an_implementation_path_that_does_not_import_is_refused(monkeypatch):
    monkeypatch.setattr("terrario.lab.capability_bridge.algorithm_index",
                        lambda: {("OnlineLearner", "v1"): "terrario.no.such:Thing"})
    with pytest.raises(BridgeRefused) as refused:
        resolve_capability("LEARN-A1-V2")
    assert any(c.startswith("IMPLEMENTATION_MODULE_ABSENT") for c in refused.value.codes)


def test_a_path_whose_attribute_is_gone_is_refused(monkeypatch):
    monkeypatch.setattr(
        "terrario.lab.capability_bridge.algorithm_index",
        lambda: {("OnlineLearner", "v1"):
                 "terrario.agent.agents.a4_advanced:A4Advanced.no_such_method"})
    with pytest.raises(BridgeRefused) as refused:
        resolve_capability("LEARN-A1-V2")
    assert any(c.startswith("IMPLEMENTATION_ATTRIBUTE_ABSENT") for c in refused.value.codes)


def test_an_endpoint_belonging_to_another_capability_is_refused(monkeypatch):
    passport = replace(PASSPORTS["LEARN-A1-V2"],
                       primary_endpoint="PENDIENTE-regulacion-condicionada-al-estado")
    monkeypatch.setitem(PASSPORTS, "LEARN-A1-V2", passport)
    with pytest.raises(BridgeRefused) as refused:
        resolve_capability("LEARN-A1-V2")
    assert any(c.startswith("ENDPOINT_NOT_REGISTERED") for c in refused.value.codes)


def test_two_records_disagreeing_about_an_implementation_are_refused(monkeypatch):
    """Measured today: five algorithms, zero conflicts.  Picking one on a
    conflict would make the route silently address the wrong code."""
    from terrario.lab import capability_operationalization as ops

    real = ops.REGISTRY["OPR-LEARN-A1-RL-01"]
    otro = replace(real, operationalization_id="OPR-CLON",
                   implementation=replace(real.implementation,
                                          implementation_id="terrario.otro:Cosa"))
    monkeypatch.setitem(ops.REGISTRY, "OPR-CLON", otro)
    with pytest.raises(BridgeRefused) as refused:
        algorithm_index()
    assert any(c.startswith("AMBIGUOUS_IMPLEMENTATION") for c in refused.value.codes)
