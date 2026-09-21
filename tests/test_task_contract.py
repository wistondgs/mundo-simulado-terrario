"""A3b fase 1 · la gramática de tarea, y los casos donde la intuición sobreafirma.

Six contracts and one mutant, written before the rules.  Each exists to kill
one plausible-sounding rule, and the rule it kills is named in its docstring:
a case that refutes nothing is decoration, and this project has already
catalogued the mirror failure --a criterion that only ever fails-- once.

Nothing here reads level 1.5's artefacts.  `T6` is written by hand to be
structurally equivalent to it; if a rule needed a condition that only 1.5
satisfies, the stop condition is `TASK_DECOMPOSER_OVERFIT` and it would show
up as `T6` green with `T1`-`T5` bent to fit.
"""

from __future__ import annotations

import dataclasses

import pytest

from terrario.lab.relation_ledger import EvidenceClass, HypothesisOrigin
from terrario.lab.task_contract import (
    ContractRefused, DerivedRole, DerivedRoleKind, RoleNature, TaskContract,
    derive_roles,
)

CAPACIDAD = DerivedRoleKind.CAPACITY_CONSTRAINED_RETENTION
INCERTIDUMBRE = DerivedRoleKind.FUTURE_RELEVANCE_UNCERTAINTY
SELECCION = DerivedRoleKind.SELECTIVE_RETENTION_PRESSURE
POLITICA = DerivedRoleKind.ADAPTIVE_RETENTION_POLICY
CREDITO = DerivedRoleKind.DELAYED_CREDIT_TO_RETENTION
COORDINACION = DerivedRoleKind.COORDINATION_PRESSURE


# --- T1 · cuello de botella, pero la relevancia se conoce antes de retener -----------

T1 = TaskContract(
    label="T1",
    source_information_bits=4.0, retention_capacity_bits=2.0,
    relevance_known_before_retention=True,
    retention_time=0, query_time=1, response_time=2, feedback_time=3,
    encoder_adaptive=True, decoder_adaptive=False,
    encoder_semantics_given=False, decoder_semantics_given=True,
    performance_depends_on_encoder=True, performance_depends_on_decoder=True,
    performance_depends_on_compatibility=False,
    counterfactual_replay_allowed=False)


def test_t1_a_bottleneck_with_known_relevance_is_not_uncertainty_about_the_future():
    """Kills: «the query arrives later, therefore future relevance is uncertain».

    The organism already knows what will be asked of what it keeps.  It has to
    compress; it does not have to guess.  Those are different problems and a
    rule that cannot tell them apart would make every bottleneck an epistemic
    one."""
    r = derive_roles(T1)
    assert CAPACIDAD in r.roles
    assert INCERTIDUMBRE not in r.roles
    assert SELECCION not in r.roles
    assert set(r.roles) == {CAPACIDAD, CREDITO}


# --- T2 · consulta posterior, pero el canal conserva todo -----------------------------

T2 = TaskContract(
    label="T2",
    source_information_bits=2.0, retention_capacity_bits=4.0,
    relevance_known_before_retention=False,
    retention_time=0, query_time=1, response_time=2, feedback_time=3,
    encoder_adaptive=True, decoder_adaptive=True,
    encoder_semantics_given=False, decoder_semantics_given=False,
    performance_depends_on_encoder=True, performance_depends_on_decoder=True,
    performance_depends_on_compatibility=False,
    counterfactual_replay_allowed=False)


def test_t2_a_later_query_with_room_to_spare_creates_no_selection_pressure():
    """Kills: «the query arrives later, therefore something must be selected».

    Not knowing what will be asked costs nothing when nothing has to be
    dropped.  The uncertainty is real and stays; the pressure needs both."""
    r = derive_roles(T2)
    assert CAPACIDAD not in r.roles
    assert SELECCION not in r.roles
    assert INCERTIDUMBRE in r.roles
    assert set(r.roles) == {INCERTIDUMBRE, CREDITO}


# --- T3 · cuello de botella + consulta posterior + encoder fijo -----------------------

T3 = TaskContract(
    label="T3",
    source_information_bits=4.0, retention_capacity_bits=2.0,
    relevance_known_before_retention=False,
    retention_time=0, query_time=1, response_time=2, feedback_time=3,
    encoder_adaptive=False, decoder_adaptive=True,
    #: Fijo no es «significado dado»: una proyección aleatoria fija no
    #: aprende y nadie dijo nunca qué codifica.
    encoder_semantics_given=False, decoder_semantics_given=False,
    performance_depends_on_encoder=True, performance_depends_on_decoder=True,
    performance_depends_on_compatibility=False,
    counterfactual_replay_allowed=False)


def test_t3_pressure_exists_and_no_selection_policy_can_be_learned():
    """Kills: «there is a bottleneck and a later query, so a retention policy
    must be learned».

    The most important control of this unit.  Every ingredient of the pressure
    is present and the encoder cannot change, so there is nothing to learn a
    policy with.  Reading the pressure as a policy is how a task description
    becomes an unearned training plan."""
    r = derive_roles(T3)
    assert SELECCION in r.roles, "the pressure is real"
    assert POLITICA not in r.roles, "and nothing here can learn one"
    assert r.pressures and r.controls == ()
    assert set(r.roles) == {CAPACIDAD, INCERTIDUMBRE, SELECCION}


# --- T4 · encoder adaptable, decoder fijo con semántica dada --------------------------

T4 = TaskContract(
    label="T4",
    source_information_bits=4.0, retention_capacity_bits=2.0,
    relevance_known_before_retention=False,
    retention_time=0, query_time=1, response_time=2, feedback_time=3,
    encoder_adaptive=True, decoder_adaptive=False,
    encoder_semantics_given=False, decoder_semantics_given=True,
    performance_depends_on_encoder=True, performance_depends_on_decoder=True,
    #: Y el rendimiento SÍ depende de que encajen: el encoder debe aprender a
    #: aterrizar donde el decoder fijo espera.
    performance_depends_on_compatibility=True,
    counterfactual_replay_allowed=False)


def test_t4_one_learner_against_a_fixed_target_is_not_coordination():
    """Kills: «performance depends on compatibility, therefore they must
    coordinate».

    Compatibility matters here and there is still only one party that can
    move.  Adapting to a fixed target is not two parties learning to agree,
    and the difference is exactly what the word coordination carries."""
    r = derive_roles(T4)
    assert COORDINACION not in r.roles
    assert POLITICA in r.roles
    assert set(r.roles) == {CAPACIDAD, INCERTIDUMBRE, SELECCION, POLITICA, CREDITO}


# --- T5 · feedback inmediato respecto de la decisión de retención ---------------------

T5 = TaskContract(
    label="T5",
    source_information_bits=4.0, retention_capacity_bits=2.0,
    relevance_known_before_retention=True,
    retention_time=0, query_time=0, response_time=0, feedback_time=0,
    encoder_adaptive=True, decoder_adaptive=True,
    encoder_semantics_given=False, decoder_semantics_given=False,
    performance_depends_on_encoder=True, performance_depends_on_decoder=True,
    performance_depends_on_compatibility=True,
    counterfactual_replay_allowed=False)


def test_t5_learning_about_retention_is_not_delayed_credit():
    """Kills: «the encoder learns and performance depends on it, therefore
    credit is delayed».

    Learning is present -- the encoder is adaptive and performance depends on
    it -- so the absence of the role is about the timing and not about the
    absence of a learner.  A control that passed because nothing was learning
    would not be a control."""
    r = derive_roles(T5)
    assert T5.encoder_adaptive and T5.performance_depends_on_encoder
    assert CREDITO not in r.roles
    assert set(r.roles) == {CAPACIDAD, COORDINACION}


# --- T6 · contrato completo, estructuralmente equivalente al problema de nivel 1.5 ----

T6 = TaskContract(
    label="T6",
    source_information_bits=4.0, retention_capacity_bits=2.0,
    relevance_known_before_retention=False,
    retention_time=0, query_time=1, response_time=2, feedback_time=3,
    encoder_adaptive=True, decoder_adaptive=True,
    encoder_semantics_given=False, decoder_semantics_given=False,
    performance_depends_on_encoder=True, performance_depends_on_decoder=True,
    performance_depends_on_compatibility=True,
    counterfactual_replay_allowed=False)


def test_t6_the_full_contract_derives_every_role_and_no_case_specific_condition():
    """Nothing in the rules mentions this contract, and it is the conjunction
    of what T1-T5 each isolate.  If it needed a condition of its own, that is
    the `TASK_DECOMPOSER_OVERFIT` stop and it would be visible here."""
    r = derive_roles(T6)
    assert set(r.roles) == {CAPACIDAD, INCERTIDUMBRE, SELECCION, POLITICA,
                            CREDITO, COORDINACION}


def test_t6_is_exactly_t4_plus_an_adaptive_decoder():
    """The minimal pair.  One field differs and one role differs with it."""
    r6, r4 = derive_roles(T6), derive_roles(T4)
    assert set(r6.roles) - set(r4.roles) == {COORDINACION}


def test_every_role_is_a_hypothesis_and_says_where_it_came_from():
    for contrato in (T1, T2, T3, T4, T5, T6):
        for rol in derive_roles(contrato).derived:
            assert rol.evidence is EvidenceClass.HYPOTHESIS, rol.kind
            assert rol.origin is HypothesisOrigin.DERIVED_FROM_TASK_CONTRACT, rol.kind


# --- el mutante obligatorio · dos adaptativos sin acoplamiento ------------------------

MUTANTE = dataclasses.replace(T6, label="MUTANTE",
                              performance_depends_on_compatibility=False)


def test_mutant_two_adaptive_components_that_need_not_agree():
    """Kills: «both halves are adaptive, therefore they must coordinate».

    The exact analogue of the recursion case in the previous unit: a
    structural feature that sounds like a demand and is not one.  Both parts
    learn at the same time and nothing about the task requires the pair to
    fit."""
    r = derive_roles(MUTANTE)
    assert MUTANTE.encoder_adaptive and MUTANTE.decoder_adaptive
    assert COORDINACION not in r.roles
    assert set(derive_roles(T6).roles) - set(r.roles) == {COORDINACION}


# --- dos controles más, por los dos campos que si no nadie leería ---------------------

def test_counterfactual_replay_dissolves_delayed_credit():
    """Re-running the same situation with a different retention measures what
    the other choice would have yielded, and there is no longer a credit to
    assign backwards."""
    con_replay = dataclasses.replace(T6, label="T6-replay",
                                     counterfactual_replay_allowed=True)
    assert CREDITO not in derive_roles(con_replay).roles
    assert set(derive_roles(T6).roles) - set(derive_roles(con_replay).roles) == {CREDITO}


def test_knowing_what_will_matter_collapses_the_whole_selection_chain():
    """One field, three roles: uncertainty, the pressure built on it, and the
    policy built on that."""
    sabido = dataclasses.replace(T6, label="T6-sabido",
                                 relevance_known_before_retention=True)
    assert set(derive_roles(T6).roles) - set(derive_roles(sabido).roles) == {
        INCERTIDUMBRE, SELECCION, POLITICA}


def test_a_fixed_encoder_removes_the_policy_and_leaves_the_pressure():
    fijo = dataclasses.replace(T6, label="T6-fijo", encoder_adaptive=False)
    r = derive_roles(fijo)
    assert SELECCION in r.roles and POLITICA not in r.roles


# --- las siete negativas · una tarea que no se puede escribir no existe ----------------

BASE = dict(
    label="base", source_information_bits=4.0, retention_capacity_bits=2.0,
    relevance_known_before_retention=False,
    retention_time=0, query_time=1, response_time=2, feedback_time=3,
    encoder_adaptive=True, decoder_adaptive=True,
    encoder_semantics_given=False, decoder_semantics_given=False,
    performance_depends_on_encoder=True, performance_depends_on_decoder=True,
    performance_depends_on_compatibility=True,
    counterfactual_replay_allowed=False)


def _contrato(**cambios):
    return TaskContract(**{**BASE, **cambios})


def test_refusal_negative_information():
    with pytest.raises(ContractRefused, match="below zero"):
        _contrato(source_information_bits=-1.0)


def test_refusal_a_response_before_its_question():
    with pytest.raises(ContractRefused, match="precedes the query"):
        _contrato(query_time=5, response_time=2, feedback_time=6)


def test_refusal_feedback_before_the_response_it_judges():
    with pytest.raises(ContractRefused, match="precedes the response"):
        _contrato(response_time=4, feedback_time=3)


def test_refusal_the_query_is_in_hand_and_relevance_is_somehow_unknown():
    """You are holding the question.  Saying you do not know what will matter
    is not a hard task, it is an inconsistent one."""
    with pytest.raises(ContractRefused, match="already in hand"):
        _contrato(retention_time=2, query_time=1, response_time=3, feedback_time=4,
                  relevance_known_before_retention=False)


def test_a_query_in_hand_with_relevance_known_is_perfectly_writable():
    """The refusal above must not swallow T5's shape."""
    c = _contrato(retention_time=2, query_time=1, response_time=3, feedback_time=4,
                  relevance_known_before_retention=True)
    assert not c.query_after_retention


@pytest.mark.parametrize("parte", ["encoder", "decoder"])
def test_refusal_adaptive_with_its_meaning_already_supplied(parte):
    with pytest.raises(ContractRefused, match="nothing left for it to adapt"):
        _contrato(**{f"{parte}_adaptive": True, f"{parte}_semantics_given": True})


def test_refusal_compatibility_without_two_things_to_be_compatible():
    with pytest.raises(ContractRefused, match="nothing to be compatible"):
        _contrato(performance_depends_on_decoder=False)


def test_fixed_is_not_the_same_as_supplied():
    """A fixed random projection learns nothing and nobody said what it codes.
    Collapsing the two would make every frozen component an explained one."""
    c = _contrato(encoder_adaptive=False, encoder_semantics_given=False)
    assert not c.encoder_adaptive and not c.encoder_semantics_given


# --- lo que este módulo no puede saber -------------------------------------------------

def test_the_contract_never_names_a_capability():
    """Checked over the executable module with docstrings stripped by AST.

    Grepping the raw source would catch the prose that explains what the
    module must not know, which is the text-guard failure already catalogued
    in this project."""
    import ast
    import inspect

    from terrario.lab import task_contract

    arbol = ast.parse(inspect.getsource(task_contract))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Expr) and isinstance(nodo.value, ast.Constant) \
                and isinstance(nodo.value.value, str):
            nodo.value.value = ""
    codigo = ast.unparse(arbol)
    for prohibido in ("LIMRET", "FUTVAL", "TEMPCRED", "SELPOL", "COADAPT",
                      "SELECTION", "PREDSTATE", "EVSENS", "1.5"):
        assert prohibido not in codigo, prohibido


def test_this_stage_cannot_assert_a_dependency_or_a_measurement():
    """`REQUIREMENT_DEPENDENCY` and `SUFFICIENT_SET` are what a measured
    campaign earns.  A task's structure never does, so the vocabulary is not
    available here at all."""
    import ast
    import inspect

    from terrario.lab import task_contract

    arbol = ast.parse(inspect.getsource(task_contract))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Expr) and isinstance(nodo.value, ast.Constant) \
                and isinstance(nodo.value.value, str):
            nodo.value.value = ""
    codigo = ast.unparse(arbol)
    for prohibido in ("REQUIREMENT_DEPENDENCY", "SUFFICIENT_SET", "REQUIRES",
                      "MEASURED", "RelationClaim", "NECESSARY"):
        assert prohibido not in codigo, prohibido


def test_a_role_cannot_be_born_measured():
    with pytest.raises(ContractRefused, match="nothing was run"):
        DerivedRole(kind=CAPACIDAD, rationale="x", falsification_question="y",
                    evidence=EvidenceClass.MEASURED_FACTORIAL)


def test_a_role_cannot_hide_where_it_came_from():
    with pytest.raises(ContractRefused, match="hides where it came from"):
        DerivedRole(kind=CAPACIDAD, rationale="x", falsification_question="y",
                    origin=HypothesisOrigin.HUMAN_PROPOSED)


def test_every_role_carries_a_falsification_question_and_a_nature():
    for rol in derive_roles(T6).derived:
        assert rol.falsification_question.strip().endswith("?"), rol.kind
        assert rol.rationale.strip()
        assert rol.nature in (RoleNature.TASK_PRESSURE, RoleNature.LEARNABLE_CONTROL)


def test_roles_come_back_ordered_by_nothing_the_derivation_chose():
    r = derive_roles(T6)
    assert list(r.roles) == sorted(r.roles, key=lambda k: k.value)
    assert set(r.pressures) | set(r.controls) == set(r.roles)
