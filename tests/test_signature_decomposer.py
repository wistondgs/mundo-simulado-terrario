"""A3a · what two signatures disagree about, derived rather than recalled.

The synthetic cases come first on purpose.  A decomposer that only satisfies
1.8 is an explanation of 1.8 with a function's manners, and the seven cases
below are what separate the two.
"""

from __future__ import annotations

import pytest

from terrario.lab.signature_decomposer import (
    Argument, ArgumentRole, DiscrepancyKind, FunctionalConstraint, FunctionalRole,
    FunctionalSignature, OutputRole, SignatureError, decompose,
    resolve_against_catalogue,
)

DISTINGUIBLE = frozenset({FunctionalConstraint.HISTORY_DISTINGUISHABILITY})

X = ArgumentRole.PRIOR_STATE
Y = ArgumentRole.ACTION
Z = ArgumentRole.NEW_OBSERVATION
W = ArgumentRole.REWARD


def _sig(label, *roles, output=OutputRole.PREDICTION, participation=None):
    return FunctionalSignature(
        label=label, output=output,
        arguments=tuple(Argument(f"arg_{r.value.lower()}", r) for r in roles),
        causal_participation=participation)


# --- 1 · un argumento que lo requerido tiene y lo realizado no ----------------------

def test_1_a_required_argument_the_realized_family_lacks_is_detected():
    d = decompose(_sig("req", X, Y, Z), _sig("real", X, Y))
    faltantes = [x for x in d.discrepancies if x.kind is DiscrepancyKind.MISSING_INPUT]
    assert [x.role for x in faltantes] == [Z]
    assert FunctionalRole.NEW_EVIDENCE_SENSITIVITY in d.roles


# --- 2 · firmas idénticas ------------------------------------------------------------

def test_2_identical_signatures_produce_no_candidate():
    d = decompose(_sig("req", X, Y), _sig("real", X, Y))
    assert d.candidates == () and d.discrepancies == () and d.roles == ()


# --- 3 · un argumento de más en lo realizado ------------------------------------------

def test_3_a_spare_argument_invents_no_requirement():
    """A mechanism may take more than it needs; manufacturing a precursor out
    of generosity would fill the graph with demands nobody made."""
    d = decompose(_sig("req", X, Y), _sig("real", X, Y, Z))
    assert d.candidates == () and d.roles == ()


# --- 4 · presente pero sin participación causal ----------------------------------------

def test_4_an_argument_that_does_not_participate_is_detected():
    """1.8's actual defect: the observation was in the routing key and never
    discriminated."""
    d = decompose(_sig("req", X, Y, Z),
                  _sig("real", X, Y, Z, participation=frozenset({X, Y})))
    sin_part = [x for x in d.discrepancies
                if x.kind is DiscrepancyKind.MISSING_CAUSAL_PARTICIPATION]
    assert [x.role for x in sin_part] == [Z]
    assert FunctionalRole.NEW_EVIDENCE_SENSITIVITY in d.roles


def test_4b_a_signature_cannot_claim_participation_from_a_non_argument():
    with pytest.raises(SignatureError, match="without being arguments"):
        _sig("mal", X, participation=frozenset({X, Z}))


# --- 5 · los nombres no llevan nada ----------------------------------------------------

def test_5_renaming_every_argument_changes_nothing():
    con_nombres = FunctionalSignature(
        "req", OutputRole.PREDICTION,
        (Argument("estado_previo", X), Argument("acto", Y), Argument("nueva_obs", Z)))
    con_otros = FunctionalSignature(
        "req", OutputRole.PREDICTION,
        (Argument("s", X), Argument("a", Y), Argument("o_prime", Z)))
    real = _sig("real", X, Y)
    assert decompose(con_nombres, real).as_record()["candidates"] == \
        decompose(con_otros, real).as_record()["candidates"]


# --- 6 · dos faltantes, sin elegir -------------------------------------------------------

def test_6_two_missing_arguments_come_back_both():
    d = decompose(_sig("req", X, Y, Z, W), _sig("real", X, Y))
    sensibilidad = {c.about for c in d.candidates
                    if c.role is FunctionalRole.NEW_EVIDENCE_SENSITIVITY}
    assert sensibilidad == {Z, W}


# --- 7 · el empate se conserva -------------------------------------------------------------

def test_7_equivalent_candidates_are_not_ordered_by_the_decomposer():
    """Two missing arguments with the same standing must not come back ranked."""
    d = decompose(_sig("req", X, Y, Z, W), _sig("real", X, Y))
    de_z = [c for c in d.candidates if c.about is Z]
    de_w = [c for c in d.candidates if c.about is W]
    assert len(de_z) == len(de_w)
    assert {c.role for c in de_z} == {c.role for c in de_w}


# --- la tercera regla dispara por recursión, no por el caso -----------------------------------

def test_a_non_recursive_signature_does_not_demand_disambiguation():
    """The difference between deriving and remembering."""
    d = decompose(_sig("req", X, Y, Z), _sig("real", X, Y))
    assert FunctionalRole.HISTORY_CONDITIONAL_DISAMBIGUATION not in d.roles


# --- A3a.1 · la recursión sola no exige desambiguación ------------------------------

def test_r1_recursive_but_history_irrelevant_demands_no_disambiguation():
    """`Z' = Z + O` is recursive and accumulates history without requiring that
    two histories stay apart.

    Deriving a precursor from recursion alone would populate the graph with a
    requirement the specification never made -- which is the over-derivation
    this control exists to catch, and it did catch it."""
    d = decompose(
        FunctionalSignature("Z' = F(Z, O)", OutputRole.NEXT_STATE,
                            (Argument("Z", X), Argument("O", Z))),
        FunctionalSignature("Z' = F(Z)", OutputRole.NEXT_STATE, (Argument("Z", X),)))
    assert set(d.roles) == {FunctionalRole.NEW_EVIDENCE_SENSITIVITY,
                            FunctionalRole.STATE_UPDATE_WITH_NEW_EVIDENCE}
    assert FunctionalRole.HISTORY_CONDITIONAL_DISAMBIGUATION not in d.roles


def test_r2_recursive_and_history_must_separate_demands_it():
    """Same signature, one constraint more: two admissible histories sharing a
    present must lead to different futures."""
    d = decompose(
        FunctionalSignature("Z' = F(Z, O)", OutputRole.NEXT_STATE,
                            (Argument("Z", X), Argument("O", Z)),
                            constraints=DISTINGUIBLE),
        FunctionalSignature("Z' = F(Z)", OutputRole.NEXT_STATE, (Argument("Z", X),)))
    assert FunctionalRole.HISTORY_CONDITIONAL_DISAMBIGUATION in d.roles


def test_the_constraint_alone_without_recursion_demands_nothing_extra():
    """State that does not carry forward cannot fail to keep histories apart."""
    d = decompose(_sig("req", X, Y, Z, output=OutputRole.PREDICTION),
                  _sig("real", X, Y, output=OutputRole.PREDICTION))
    con = FunctionalSignature("req", OutputRole.PREDICTION,
                              (Argument("a", X), Argument("b", Y), Argument("c", Z)),
                              constraints=DISTINGUIBLE)
    otra = decompose(con, _sig("real", X, Y, output=OutputRole.PREDICTION))
    assert set(d.roles) == set(otra.roles)


def test_a_recursive_signature_does():
    d = decompose(_sig("req", X, Y, Z, output=OutputRole.NEXT_STATE),
                  _sig("real", X, Y, output=OutputRole.NEXT_STATE))
    assert FunctionalRole.HISTORY_CONDITIONAL_DISAMBIGUATION not in d.roles


def test_a_recursive_signature_with_nothing_missing_demands_nothing():
    d = decompose(_sig("req", X, Y, output=OutputRole.NEXT_STATE),
                  _sig("real", X, Y, output=OutputRole.NEXT_STATE))
    assert d.roles == ()


def test_signatures_producing_different_things_are_refused():
    with pytest.raises(SignatureError, match="different questions"):
        decompose(_sig("req", X, output=OutputRole.NEXT_STATE),
                  _sig("real", X, output=OutputRole.VALUE))


# --- la aceptación real, sin ninguna condición especial para PREDSTATE -------------------------

#: La restricción sale del oráculo sellado, no de nosotros: pregunta por «una
#: representación interna que desambigüe situaciones perceptualmente idénticas
#: cuyas consecuencias ante la misma acción son distintas» --mismo presente,
#: futuro requerido distinto--.
REQUERIDA = FunctionalSignature(
    "Z_{t+1} = F(Z_t, A_t, O_{t+1})", OutputRole.NEXT_STATE,
    (Argument("Z_t", X), Argument("A_t", Y), Argument("O_{t+1}", Z)),
    constraints=DISTINGUIBLE)
REALIZADA = FunctionalSignature(
    "Z_{t+1} = F(Z_t, A_t)", OutputRole.NEXT_STATE,
    (Argument("Z_t", X), Argument("A_t", Y)))

#: La capa de vocabulario, separada a propósito de la derivación.
VOCABULARIO = {
    FunctionalRole.NEW_EVIDENCE_SENSITIVITY: "EVSENS",
    FunctionalRole.STATE_UPDATE_WITH_NEW_EVIDENCE: "REPUPD",
    FunctionalRole.HISTORY_CONDITIONAL_DISAMBIGUATION: "HISTDIS",
}


def test_the_18_discrepancy_derives_its_three_roles():
    d = decompose(REQUERIDA, REALIZADA)
    assert set(d.roles) == {
        FunctionalRole.NEW_EVIDENCE_SENSITIVITY,
        FunctionalRole.STATE_UPDATE_WITH_NEW_EVIDENCE,
        FunctionalRole.HISTORY_CONDITIONAL_DISAMBIGUATION}


def test_the_decomposer_never_names_a_capability():
    """It emits demands; the catalogue supplies words for them, or does not.

    Checked over the executable module, with docstrings and comments stripped:
    the prose explains what the decomposer must not know and naming a thing to
    forbid it is not knowing it.  Grepping the raw source would have caught its
    own explanation, which is the text-guard failure this project already
    catalogued once."""
    import ast
    import inspect

    from terrario.lab import signature_decomposer

    arbol = ast.parse(inspect.getsource(signature_decomposer))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Expr) and isinstance(nodo.value, ast.Constant) \
                and isinstance(nodo.value.value, str):
            nodo.value.value = ""
    codigo = ast.unparse(arbol)
    for nombre in ("EVSENS", "REPUPD", "HISTDIS", "PREDSTATE", "SELECTION"):
        assert nombre not in codigo, nombre


def test_resolution_against_the_catalogue_is_a_separate_step():
    from terrario.lab.developmental import terrario_graph

    inventario = terrario_graph().capabilities
    resueltos, sin_nombre = resolve_against_catalogue(
        decompose(REQUERIDA, REALIZADA), VOCABULARIO, inventario)
    assert resueltos == ("EVSENS", "HISTDIS", "REPUPD")
    assert sin_nombre == ()


def test_a_role_the_catalogue_cannot_name_is_reported_not_dropped():
    """An unnamed role says the inventory lacks a word for something the
    structure demands, which is a finding and not a failure."""
    resueltos, sin_nombre = resolve_against_catalogue(
        decompose(REQUERIDA, REALIZADA), VOCABULARIO, {"EVSENS": object()})
    assert resueltos == ("EVSENS",)
    assert set(sin_nombre) == {"HISTORY_CONDITIONAL_DISAMBIGUATION",
                               "STATE_UPDATE_WITH_NEW_EVIDENCE"}
