"""The scientific gate: only SUPPLIED may become configuration.

This is where the schema can be destroyed rather than merely described.  If
what the organism was meant to acquire arrives as a parameter, the run still
completes, still produces numbers, and measures nothing -- and the separation
built in c2958d5 would have been documentation with a type annotation.
"""

from __future__ import annotations

import pytest

from terrario.agent.agents.a4_advanced import DEFAULT_CONFIG
from terrario.lab.capability_bridge import resolve_capability
from terrario.lab.capability_materialization import (
    MaterializationRefused, authorised_configuration_keys,
    forbidden_configuration_keys, materialize_execution,
)
from terrario.lab.capability_passport import REGISTRY as PASSPORTS

CAPACIDAD = "LEARN-A1-V2"


def _materializar(base=None):
    return materialize_execution(resolve_capability(CAPACIDAD),
                                 dict(base if base is not None else DEFAULT_CONFIG),
                                 agent_type="A4_ADVANCED")


# --- el invariante, campo por campo -------------------------------------------------

def test_only_supplied_and_the_activation_flag_may_be_written():
    autorizadas = authorised_configuration_keys(CAPACIDAD)
    passport = PASSPORTS[CAPACIDAD]
    esperadas = {"learning_rate", "grad_clip", "update_frequency",
                 passport.composition_flag}
    assert set(autorizadas) == esperadas


def test_acquisition_target_and_non_claims_are_forbidden_keys():
    prohibidas = set(forbidden_configuration_keys(CAPACIDAD))
    passport = PASSPORTS[CAPACIDAD]
    assert {e.identity for e in passport.acquisition_target} <= prohibidas
    assert set(passport.non_claims) <= prohibidas
    assert not (prohibidas & set(authorised_configuration_keys(CAPACIDAD)))


def test_the_formalization_reference_configures_nothing():
    """It resolves and it describes; it is not a source of keys."""
    materializada = _materializar()
    assert materializada.mechanism_id == "online-gradient-update"
    assert "online-gradient-update" not in materializada.agent_config
    assert "formalization_ref" not in materializada.agent_config


def test_materialising_adds_no_key_the_base_did_not_have():
    """A capability that can introduce keys can introduce the unauthorised one."""
    materializada = _materializar()
    assert set(materializada.agent_config) == set(DEFAULT_CONFIG)


def test_supplied_authorises_keys_and_never_invents_their_values():
    """The passport is not where a learning rate gets decided."""
    sin_valor = {k: v for k, v in DEFAULT_CONFIG.items() if k != "learning_rate"}
    with pytest.raises(MaterializationRefused) as refused:
        _materializar(sin_valor)
    assert "AUTHORISED_KEY_ABSENT_FROM_BASE:learning_rate" in refused.value.codes


# --- EL MUTANTE CRÍTICO ---------------------------------------------------------------

def test_an_acquisition_target_reaching_the_runtime_fails_closed():
    """The defect this whole schema exists to make impossible.

    Handing the organism the parameter values it was supposed to acquire leaves
    an experiment that runs, reports, and answers a question nobody asked."""
    objetivo = PASSPORTS[CAPACIDAD].acquisition_target[0].identity
    contaminada = {**DEFAULT_CONFIG, objetivo: [0.1, 0.2, 0.3]}
    with pytest.raises(MaterializationRefused) as refused:
        _materializar(contaminada)
    assert f"ACQUISITION_TARGET_IN_RUNTIME_CONFIG:{objetivo}" in refused.value.codes


def test_declaring_the_acquisition_target_as_supplied_is_refused_at_the_passport():
    """The same collapse one layer earlier, already refused in c2958d5."""
    from dataclasses import replace
    from terrario.lab.capability_passport import ElementKind, ElementRef

    passport = PASSPORTS[CAPACIDAD]
    objetivo = passport.acquisition_target[0]
    with pytest.raises(ValueError, match="suministrado y como objetivo"):
        replace(passport, supplied=(*passport.supplied,
                                    ElementRef(ElementKind.CONTENT, objetivo.identity)))


def test_a_non_claim_smuggled_as_configuration_is_refused():
    limite = PASSPORTS[CAPACIDAD].non_claims[0]
    with pytest.raises(MaterializationRefused) as refused:
        _materializar({**DEFAULT_CONFIG, limite: True})
    assert any(c.startswith("ACQUISITION_TARGET_IN_RUNTIME_CONFIG") for c in refused.value.codes)


def test_an_authorised_key_the_implementation_ignores_is_refused(monkeypatch):
    from dataclasses import replace
    from terrario.lab.capability_passport import ElementKind, ElementRef

    passport = replace(PASSPORTS[CAPACIDAD],
                       supplied=(*PASSPORTS[CAPACIDAD].supplied,
                                 ElementRef(ElementKind.PARAMETER, "clave_que_nadie_lee")))
    monkeypatch.setitem(PASSPORTS, CAPACIDAD, passport)
    with pytest.raises(MaterializationRefused) as refused:
        _materializar({**DEFAULT_CONFIG, "clave_que_nadie_lee": 1})
    assert ("CONFIG_KEY_NOT_READ_BY_IMPLEMENTATION:clave_que_nadie_lee"
            in refused.value.codes)


# --- F · la ruta manual y la dirigida por capacidad -----------------------------------

def test_the_capability_directed_route_materialises_the_same_intervention():
    """The comparison that matters: same class, same implementation, same
    effective configuration.  Not a new proof of learning -- a proof that the
    directed route lands on the intervention the manual one already runs."""
    from terrario.agent.agents import _AGENT_IDS

    MANUAL_BASELINE = {**DEFAULT_CONFIG, "use_online_learning": True}
    CAPABILITY_DIRECTED = _materializar()

    assert _AGENT_IDS.get("A4_ADVANCED") == _AGENT_IDS.get(CAPABILITY_DIRECTED.agent_type)
    assert dict(CAPABILITY_DIRECTED.agent_config) == MANUAL_BASELINE
    assert CAPABILITY_DIRECTED.implementation_path == (
        "terrario.agent.agents.a4_advanced:A4Advanced.learn")
    assert CAPABILITY_DIRECTED.endpoint_id == "conversion_aprendizaje"


def test_the_directed_route_carries_provenance_the_manual_one_cannot():
    """The one asymmetry, and the reason for the exercise."""
    materializada = _materializar()
    assert materializada.mechanism_spec_hash
    assert materializada.capability_id == CAPACIDAD
    assert materializada.authorised_keys


def test_both_routes_build_the_same_agent_down_to_its_parameters():
    """Not a configuration comparison: two real agents, same seed.

    Identical parameter hashes and identical first actions is the only version
    of "same intervention" that cannot be satisfied by two dictionaries that
    merely look alike."""
    import torch
    from terrario.agent.agents import _parameter_hash, create_agent

    MANUAL = {**DEFAULT_CONFIG, "use_online_learning": True}
    DIRIGIDA = dict(_materializar().agent_config)

    # `torch.manual_seed` antes de construir, que es lo que hace la ruta real
    # (`experiment_capability_acquisition.py:210`). Medido al escribir esto:
    # sin esa línea, dos construcciones idénticas con la misma `seed` dan
    # parámetros distintos, porque el `generator` que recibe `create_agent` no
    # gobierna la inicialización de los módulos. Es del árbol, no de esta ruta.
    torch.manual_seed(4242)
    manual = create_agent("A4_ADVANCED", MANUAL, seed=4242, device="cpu")
    torch.manual_seed(4242)
    dirigida = create_agent("A4_ADVANCED", DIRIGIDA, seed=4242, device="cpu")

    assert type(manual) is type(dirigida)
    assert _parameter_hash(manual) == _parameter_hash(dirigida)
    assert manual.config["use_online_learning"] is dirigida.config["use_online_learning"] is True
    # y el mecanismo llegó: el aprendiz existe con los tres parámetros vivos
    for agente in (manual, dirigida):
        assert agente.learner.lr == DEFAULT_CONFIG["learning_rate"]
        assert agente.learner.grad_clip == DEFAULT_CONFIG["grad_clip"]
        assert agente.learner.update_frequency == DEFAULT_CONFIG["update_frequency"]


def test_the_directed_route_is_engineering_not_science():
    """A v2 passport does not promote a run.

    The firewall still refuses SCIENTIFIC from this path, and NO_CORPUS_PROVENANCE
    not blocking an engineering run says nothing about certification."""
    from terrario.lab.capability_passport import PassportState, status_of
    from terrario.lab.sandbox_runtime import ExecutionClassification

    assert status_of(PASSPORTS[CAPACIDAD]) is PassportState.NO_CORPUS_PROVENANCE
    # La materialización ocurre igual: correcto para ingeniería.
    assert _materializar().agent_config
    # Y la clasificación por defecto sigue siendo la de ingeniería.
    assert ExecutionClassification.ENGINEERING_SANDBOX.value == "ENGINEERING_SANDBOX"
