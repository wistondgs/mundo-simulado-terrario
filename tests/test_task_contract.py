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
    NATURE as _NATURE, RoleNature,
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
    retention_credit_signal_time=3, feedback_is_attributable_to_that_retention=True,
    encoder_adaptive=True, decoder_adaptive=False,
    encoder_semantics_given=False, decoder_semantics_given=True,
    performance_depends_on_encoder=True, performance_depends_on_decoder=True,
    performance_depends_on_compatibility=False,
    counterfactual_replay_allowed=False,
    alternative_retention_can_be_intervened=False,
    outcome_of_alternative_is_observable=False)


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
    retention_credit_signal_time=3, feedback_is_attributable_to_that_retention=True,
    encoder_adaptive=True, decoder_adaptive=True,
    encoder_semantics_given=False, decoder_semantics_given=False,
    performance_depends_on_encoder=True, performance_depends_on_decoder=True,
    performance_depends_on_compatibility=False,
    counterfactual_replay_allowed=False,
    alternative_retention_can_be_intervened=False,
    outcome_of_alternative_is_observable=False)


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
    retention_credit_signal_time=3, feedback_is_attributable_to_that_retention=True,
    encoder_adaptive=False, decoder_adaptive=True,
    #: Fijo no es «significado dado»: una proyección aleatoria fija no
    #: aprende y nadie dijo nunca qué codifica.
    encoder_semantics_given=False, decoder_semantics_given=False,
    performance_depends_on_encoder=True, performance_depends_on_decoder=True,
    performance_depends_on_compatibility=False,
    counterfactual_replay_allowed=False,
    alternative_retention_can_be_intervened=False,
    outcome_of_alternative_is_observable=False)


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
    retention_credit_signal_time=3, feedback_is_attributable_to_that_retention=True,
    encoder_adaptive=True, decoder_adaptive=False,
    encoder_semantics_given=False, decoder_semantics_given=True,
    performance_depends_on_encoder=True, performance_depends_on_decoder=True,
    #: Y el rendimiento SÍ depende de que encajen: el encoder debe aprender a
    #: aterrizar donde el decoder fijo espera.
    performance_depends_on_compatibility=True,
    counterfactual_replay_allowed=False,
    alternative_retention_can_be_intervened=False,
    outcome_of_alternative_is_observable=False)


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


# --- T5 · demora cero entre la retención y una señal atribuible a ella ---------------
#
# A3b.1 le corrigió el nombre. No demuestra «el feedback inmediato elimina el
# crédito temporal»: con las desigualdades de este contrato, feedback en el
# mismo instante que la retención arrastra la consulta consigo, así que el caso
# es más estrecho de lo que su nombre prometía. Lo que demuestra es que si no
# hay demora entre decidir y recibir una señal atribuible a esa decisión, no
# queda crédito que asignar hacia atrás. La versión general de eso, con las dos
# temporalidades ya separadas, está más abajo.

T5 = TaskContract(
    label="T5-ZERO_RETENTION_CREDIT_DELAY",
    source_information_bits=4.0, retention_capacity_bits=2.0,
    relevance_known_before_retention=True,
    retention_time=0, query_time=0, response_time=0, feedback_time=0,
    retention_credit_signal_time=0, feedback_is_attributable_to_that_retention=True,
    encoder_adaptive=True, decoder_adaptive=True,
    encoder_semantics_given=False, decoder_semantics_given=False,
    performance_depends_on_encoder=True, performance_depends_on_decoder=True,
    performance_depends_on_compatibility=True,
    counterfactual_replay_allowed=False,
    alternative_retention_can_be_intervened=False,
    outcome_of_alternative_is_observable=False)


def test_t5_zero_retention_credit_delay_is_not_the_same_as_prompt_feedback():
    """Kills: «the encoder learns and performance depends on it, therefore
    credit is delayed».

    Learning is present -- the encoder is adaptive and performance depends on
    it -- so the absence of the role is about the distance and not about the
    absence of a learner.  A control that passed because nothing was learning
    would not be a control.

    The distance that matters is between the retention and a signal
    attributable to it, which in this contract happens to coincide with
    everything else being simultaneous.  The general form, where the response
    is judged late and the retention is credited at once, is
    `test_zero_retention_credit_delay_leaves_nothing_to_assign_backwards`."""
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
    retention_credit_signal_time=3, feedback_is_attributable_to_that_retention=True,
    encoder_adaptive=True, decoder_adaptive=True,
    encoder_semantics_given=False, decoder_semantics_given=False,
    performance_depends_on_encoder=True, performance_depends_on_decoder=True,
    performance_depends_on_compatibility=True,
    counterfactual_replay_allowed=False,
    alternative_retention_can_be_intervened=False,
    outcome_of_alternative_is_observable=False)


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


# --- A3b.1 · replay no es crédito resuelto -------------------------------------------
#
# Hubo una version que afirmaba que `counterfactual_replay_allowed` disolvia el
# credito diferido. Se retiro. Despues hubo un rol
# `DIRECT_RETENTION_CREDIT_AVAILABLE` con su propia clase
# `AVAILABLE_INSTRUMENT`, y ese tambien se retiro: era una propiedad del arnes
# experimental vestida de exigencia de la tarea. Los CAMPOS siguen aqui --son
# hechos del aparato-- y lo que estas pruebas fijan es que no llegan a la
# salida del organismo.

def test_replay_without_an_observable_alternative_leaves_the_credit_where_it_was():
    """Kills: «the situation can be re-run, therefore credit is no longer
    delayed».

    Nothing can be seen of the other choice, so re-running buys nothing and
    the signal about the retention still arrives three apart from it."""
    ciego = dataclasses.replace(T6, label="T6-replay-ciego",
                                counterfactual_replay_allowed=True)
    r = derive_roles(ciego)
    assert CREDITO in r.roles
    assert set(r.roles) == set(derive_roles(T6).roles)


def test_a_fully_capable_apparatus_changes_nothing_the_organism_faces():
    """FASE F. All four harness conditions true — the situation can be re-run,
    the alternative retention can be imposed, its outcome can be seen and the
    result can be assigned — and the organism observes none of it.

    Every organism-facing output is identical to the contract where the
    apparatus can do nothing at all. The delay is still there, because a delay
    is a fact about when a signal arrives and no instrument moves it."""
    entero = dataclasses.replace(
        T6, label="T6-aparato-entero", counterfactual_replay_allowed=True,
        alternative_retention_can_be_intervened=True,
        outcome_of_alternative_is_observable=True,
        feedback_is_attributable_to_that_retention=True)
    r, base = derive_roles(entero), derive_roles(T6)
    assert set(r.roles) == set(base.roles)
    assert r.pressures == base.pressures
    assert r.controls == base.controls
    assert r.acquisition_candidates == base.acquisition_candidates
    assert r.coordination_requirements == base.coordination_requirements
    assert CREDITO in r.roles, "the delay is still real"


@pytest.mark.parametrize("campo", [
    "counterfactual_replay_allowed",
    "alternative_retention_can_be_intervened",
    "outcome_of_alternative_is_observable"])
def test_no_harness_field_alone_can_move_an_organism_facing_output(campo):
    """G2/G3/G4 per field. Flipping any single apparatus property must leave
    acquisition_candidates, pressures and controls untouched."""
    campos = {campo: True}
    if campo == "outcome_of_alternative_is_observable":
        campos["alternative_retention_can_be_intervened"] = True
    variado = derive_roles(dataclasses.replace(T6, label=f"T6-{campo}", **campos))
    base = derive_roles(T6)
    assert variado.acquisition_candidates == base.acquisition_candidates
    assert variado.pressures == base.pressures
    assert variado.controls == base.controls


def test_an_unobservable_outcome_of_an_alternative_nobody_can_bring_about():
    """The refusal that pairs two of the apparatus fields survives the role's
    removal: it never referenced the role."""
    with pytest.raises(ContractRefused, match="nothing whose outcome that would be"):
        _contrato(outcome_of_alternative_is_observable=True,
                  alternative_retention_can_be_intervened=False)


# --- A3b.1 · las dos temporalidades del crédito no son la misma ----------------------

def test_feedback_glued_to_the_response_can_still_be_far_from_the_retention():
    """Kills: «the feedback arrives with the response, therefore there is no
    temporal credit problem».

    The judgement of the answer and the credit of the retention are different
    clocks.  Here they are as close as they can be to the response and three
    apart from the decision we actually want to credit."""
    tardio = dataclasses.replace(T6, label="T6-credito-tardio",
                                 response_time=3, feedback_time=3,
                                 retention_credit_signal_time=3)
    assert tardio.feedback_time == tardio.response_time
    assert tardio.retention_credit_delay == 3
    assert CREDITO in derive_roles(tardio).roles


def test_zero_retention_credit_delay_leaves_nothing_to_assign_backwards():
    """`T5` generalised, and named for what it actually shows.

    Not «immediate feedback»: the response is judged three later and the
    query has not even arrived when retention is decided.  What is zero is
    the distance between the decision and a signal attributable to it, and
    that is the only distance the role was ever about."""
    sin_demora = dataclasses.replace(T6, label="T6-demora-cero",
                                     retention_credit_signal_time=0)
    assert sin_demora.feedback_time == 3 and sin_demora.retention_credit_delay == 0
    r = derive_roles(sin_demora)
    assert CREDITO not in r.roles
    assert set(derive_roles(T6).roles) - set(r.roles) == {CREDITO}


# --- A3b.1 · una presión de tarea no es una capacidad que adquirir --------------------

def test_a_pressure_can_never_reach_the_acquisition_candidates():
    """A task can impose a pressure with no mechanism in existence able to
    answer it.  Reading the pressure as something the organism must acquire
    is how the question stops being a question."""
    for contrato in (T1, T2, T3, T4, T5, T6, MUTANTE):
        r = derive_roles(contrato)
        assert not set(r.pressures) & set(r.acquisition_candidates), contrato.label
        assert set(r.acquisition_candidates) <= set(r.controls)


def test_the_pressure_with_no_control_is_the_case_that_proves_it():
    """`T3` again, read through the typing: every ingredient of the pressure
    and nothing to acquire."""
    r = derive_roles(T3)
    assert SELECCION in r.pressures
    assert r.acquisition_candidates == ()


def test_the_three_classes_partition_what_comes_out():
    for contrato in (T1, T2, T3, T4, T5, T6, MUTANTE):
        r = derive_roles(contrato)
        clases = (set(r.pressures) | set(r.controls)
                  | set(r.coordination_requirements))
        assert clases == set(r.roles), contrato.label
        assert (len(r.pressures) + len(r.controls)
                + len(r.coordination_requirements)) == len(r.roles)


def test_t6_still_derives_the_same_six_now_split_by_class():
    r = derive_roles(T6)
    assert set(r.roles) == {CAPACIDAD, INCERTIDUMBRE, SELECCION, POLITICA,
                            CREDITO, COORDINACION}
    assert set(r.pressures) == {CAPACIDAD, INCERTIDUMBRE, SELECCION, CREDITO}
    assert r.controls == (POLITICA,)
    assert r.coordination_requirements == (COORDINACION,)


def test_coordination_is_neither_a_pressure_nor_something_one_part_can_learn():
    """It is a demand on the pair, and it may have no owner."""
    r = derive_roles(T6)
    assert COORDINACION not in r.pressures
    assert COORDINACION not in r.acquisition_candidates


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
    retention_credit_signal_time=3, feedback_is_attributable_to_that_retention=True,
    encoder_adaptive=True, decoder_adaptive=True,
    encoder_semantics_given=False, decoder_semantics_given=False,
    performance_depends_on_encoder=True, performance_depends_on_decoder=True,
    performance_depends_on_compatibility=True,
    counterfactual_replay_allowed=False,
    alternative_retention_can_be_intervened=False,
    outcome_of_alternative_is_observable=False)


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
        assert isinstance(rol.nature, RoleNature)


def test_roles_come_back_ordered_by_nothing_the_derivation_chose():
    r = derive_roles(T6)
    assert list(r.roles) == sorted(r.roles, key=lambda k: k.value)
    assert set(r.pressures) | set(r.controls) \
        | set(r.coordination_requirements) == set(r.roles)


def test_a_credit_that_can_never_be_assigned_is_not_merely_delayed():
    """A declared gap, written down rather than filled.

    With nothing attributable arriving, the credit is not late -- it is
    absent, and calling it delayed would say that waiting is enough.  No role
    comes out for that today.  Inventing one here is exactly the
    over-assertion this unit exists to avoid, so the hole is named instead."""
    sin_atribucion = dataclasses.replace(
        T6, label="T6-sin-atribucion",
        feedback_is_attributable_to_that_retention=False)
    r = derive_roles(sin_atribucion)
    assert CREDITO not in r.roles
    assert set(derive_roles(T6).roles) - set(r.roles) == {CREDITO}


# --- FASE E · la totalidad de NATURE deja de ser una coincidencia ----------------------

def test_nature_covers_every_derived_role_kind():
    """`NATURE[kind]` is a bare subscript in two places, so the table must be
    total. It was total by accident and nothing checked it."""
    from terrario.lab.task_contract import NATURE
    assert set(NATURE) == set(DerivedRoleKind)


def test_a_holed_nature_table_is_refused_by_the_contract():
    """G1. The mutant: remove an entry deliberately."""
    from terrario.lab.task_contract import NATURE, check_nature_total

    agujereada = dict(NATURE)
    quitada = agujereada.pop(DerivedRoleKind.ADAPTIVE_RETENTION_POLICY)
    assert quitada is not None
    with pytest.raises(RuntimeError, match="does not cover"):
        check_nature_total(agujereada)
    check_nature_total(NATURE)


def test_the_holed_table_would_have_been_a_keyerror_not_a_red_test():
    """Why the contract is needed at all, shown rather than asserted.

    With an entry missing, the failure is an uncaught KeyError inside
    `acquisition_candidates` on a whole class of legal contracts -- not an
    assertion mismatch a reviewer would read as cosmetic."""
    from terrario.lab import task_contract

    original = dict(task_contract.NATURE)
    try:
        del task_contract.NATURE[DerivedRoleKind.ADAPTIVE_RETENTION_POLICY]
        derivacion = derive_roles(T6)
        assert POLITICA in derivacion.roles
        with pytest.raises(KeyError):
            _ = derivacion.acquisition_candidates
    finally:
        task_contract.NATURE.clear()
        task_contract.NATURE.update(original)
    assert derive_roles(T6).acquisition_candidates == (POLITICA,)


# --- FASE G · el aparato no puede convertirse en nada del organismo --------------------

def NATURE_DE(kind):
    return _NATURE[kind]


def _todos_los_contratos():
    return (T1, T2, T3, T4, T5, T6, MUTANTE)


def test_g2_no_apparatus_property_can_become_an_acquisition_candidate():
    for contrato in _todos_los_contratos():
        for candidato in derive_roles(contrato).acquisition_candidates:
            assert NATURE_DE(candidato) is RoleNature.LEARNABLE_CONTROL, candidato


def test_g3_no_apparatus_property_can_become_a_pressure():
    """Exhaustive over the apparatus fields: every combination of the three
    harness booleans, on every contract, leaves the pressures identical."""
    import itertools
    for contrato in _todos_los_contratos():
        base = derive_roles(contrato).pressures
        for repetir, intervenir, observar in itertools.product((False, True), repeat=3):
            if observar and not intervenir:
                continue
            variado = dataclasses.replace(
                contrato, counterfactual_replay_allowed=repetir,
                alternative_retention_can_be_intervened=intervenir,
                outcome_of_alternative_is_observable=observar)
            assert derive_roles(variado).pressures == base, contrato.label


def test_g4_no_apparatus_property_can_become_a_control():
    import itertools
    for contrato in _todos_los_contratos():
        base = derive_roles(contrato).controls
        for repetir, intervenir, observar in itertools.product((False, True), repeat=3):
            if observar and not intervenir:
                continue
            variado = dataclasses.replace(
                contrato, counterfactual_replay_allowed=repetir,
                alternative_retention_can_be_intervened=intervenir,
                outcome_of_alternative_is_observable=observar)
            assert derive_roles(variado).controls == base, contrato.label


def test_g5_the_record_no_longer_emits_the_removed_role():
    """Serialisation must not carry a phantom of something that is gone."""
    entero = dataclasses.replace(
        T6, label="T6-aparato-entero", counterfactual_replay_allowed=True,
        alternative_retention_can_be_intervened=True,
        outcome_of_alternative_is_observable=True)
    registro = derive_roles(entero).as_record()
    texto = repr(registro)
    assert "instruments" not in registro
    assert "DIRECT_RETENTION_CREDIT_AVAILABLE" not in texto
    assert "AVAILABLE_INSTRUMENT" not in texto
    assert set(registro["roles"]) == set(
        registro["pressures"] + registro["controls"]
        + registro["coordination_requirements"])


def test_g6_the_apparatus_facts_survive_and_produce_no_role():
    """Every one of the six associated fields was adjudicated APPARATUS_FACT,
    so the data stays. What must be gone is the role, not the fact."""
    campos = {f.name for f in dataclasses.fields(TaskContract)}
    for nombre in ("counterfactual_replay_allowed",
                   "alternative_retention_can_be_intervened",
                   "outcome_of_alternative_is_observable",
                   "feedback_is_attributable_to_that_retention",
                   "retention_credit_signal_time", "encoder_adaptive"):
        assert nombre in campos, nombre

    entero = dataclasses.replace(
        T6, label="T6-aparato-entero", counterfactual_replay_allowed=True,
        alternative_retention_can_be_intervened=True,
        outcome_of_alternative_is_observable=True)
    assert entero.counterfactual_replay_allowed is True
    assert entero.as_record()["counterfactual_replay_allowed"] is True
    assert len(derive_roles(entero).roles) == len(derive_roles(T6).roles)


def test_g7_nothing_was_role_only_so_no_field_was_deleted():
    """Six fields audited one at a time and each adjudicated APPARATUS_FACT;
    zero ROLE_ONLY and zero UNKNOWN, so the deletion touched the ontology and
    not the data."""
    campos = tuple(f.name for f in dataclasses.fields(TaskContract))
    assert campos == (
        "label", "source_information_bits", "retention_capacity_bits",
        "relevance_known_before_retention", "retention_time", "query_time",
        "response_time", "feedback_time", "encoder_adaptive", "decoder_adaptive",
        "encoder_semantics_given", "decoder_semantics_given",
        "performance_depends_on_encoder", "performance_depends_on_decoder",
        "performance_depends_on_compatibility", "retention_credit_signal_time",
        "feedback_is_attributable_to_that_retention",
        "counterfactual_replay_allowed", "alternative_retention_can_be_intervened",
        "outcome_of_alternative_is_observable")


def test_the_role_and_its_nature_are_gone_from_the_vocabulary():
    assert not hasattr(DerivedRoleKind, "DIRECT_RETENTION_CREDIT_AVAILABLE")
    assert not hasattr(RoleNature, "AVAILABLE_INSTRUMENT")
    assert len(list(RoleNature)) == 3
    assert len(list(DerivedRoleKind)) == 6
