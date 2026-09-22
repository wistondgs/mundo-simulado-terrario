"""U1 productivo · la misma especificación sellada, ahora sobre el organismo.

That the reference in `test_n10_u1_causal_form.py` passes these gates shows
they are satisfiable. It says nothing about this implementation, which was
written from the contract and has to pass them on its own.
"""

from __future__ import annotations

import numpy as np
import pytest

from terrario.lab.n10_u1 import Mode, U1, U1Agent, U1Config
from terrario.lab.n10_u1_spec import (
    ACTIONS, DOWN, EMPTY, UP, CFResult, causal_form_report, contingency_reversal,
    cf7_evaluation_freezes, cf8_neutral_initialization, opaque_token,
    world_truth_nonleakage,
)


def hacer():
    return U1(U1Config(alpha=0.3, exploration=0.2, seed=0))


# --- la spec sellada, sobre producción ------------------------------------------------

def test_production_u1_passes_every_sealed_gate():
    informe = causal_form_report(hacer, source=U1)
    assert informe["G_U1_CAUSAL_FORM"] == CFResult.PASS.value, informe["failed"]
    assert len(informe["gates"]) == 11


def test_production_u1_names_no_world_truth():
    assert world_truth_nonleakage(U1)["forbidden_found"] == []
    assert world_truth_nonleakage(U1Agent)["forbidden_found"] == []


def test_production_does_not_import_the_test_reference():
    """The fixture proves the gates are satisfiable; production may not lean
    on it to produce a single decision.

    Read over the executable module with docstrings stripped by AST. The
    first version grepped the raw source and caught its own docstring, which
    says the word `tests` in order to forbid it — the same text-guard failure
    this project has now recorded three times, which is why every guard here
    strips prose before looking."""
    import ast
    import inspect

    from terrario.lab import n10_u1
    arbol = ast.parse(inspect.getsource(n10_u1))
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Expr) and isinstance(nodo.value, ast.Constant) \
                and isinstance(nodo.value.value, str):
            nodo.value.value = ""
    codigo = ast.unparse(arbol)
    for prohibido in ("tests", "test_n10", "Referencia", "ReferenceU1"):
        assert prohibido not in codigo, prohibido


def test_the_input_signatures_are_closed():
    """No **kwargs, no raw world object, no metadata dict: a channel that can
    grow later is a leak that has not happened yet."""
    import inspect
    for metodo in (U1.perceive, U1.decide, U1.learn):
        parametros = inspect.signature(metodo).parameters
        assert not any(p.kind is p.VAR_KEYWORD for p in parametros.values()), metodo
        assert not any(p.kind is p.VAR_POSITIONAL for p in parametros.values()), metodo
    assert set(inspect.signature(U1.perceive).parameters) == {"self", "cue_value"}
    assert set(inspect.signature(U1.learn).parameters) == {"self", "action", "consequence"}


# --- la congelación la defiende U1, no el runner ----------------------------------------

def test_u1_refuses_the_update_itself_under_evaluation():
    """A runner that simply stops calling learn looks identical, from the
    outside, to one that forgot to."""
    u = hacer()
    u.perceive(0.9)
    u.learn(UP, 4.0)
    u.freeze()
    antes = u.theta_digest()
    for c in (+4.0, -4.0, +4.0):
        u.learn(DOWN, c)
    assert u.theta_digest() == antes
    assert u.mode is Mode.EVALUATION
    assert cf7_evaluation_freezes(hacer)["result"] == CFResult.PASS.value


def test_the_initial_policy_is_neutral_when_run_and_not_when_inspected():
    u = hacer()
    assert u.theta == {}
    assert cf8_neutral_initialization(hacer)["result"] == CFResult.PASS.value


def test_a_tie_is_broken_by_a_draw_and_not_by_the_order_of_the_actions():
    """First-action-wins would be a preference nobody put in the table and
    nobody could see in it."""
    u = hacer()
    u.perceive(0.9)
    elegidas = {u.decide(np.random.default_rng(s)) for s in range(32)}
    assert elegidas == set(ACTIONS)


# --- el token es opaco -------------------------------------------------------------------

def test_the_token_has_no_motor_meaning():
    assert opaque_token(0.1) != opaque_token(0.9)
    u = hacer()
    u.perceive(0.1)
    primero = u.memory
    u.perceive(0.9)
    assert u.memory != primero
    assert u.memory not in (UP, DOWN, EMPTY)


def test_production_learns_both_the_contingency_and_its_inverse():
    informe = contingency_reversal(hacer)
    assert informe["result"] == CFResult.PASS.value
    assert list(informe["world_A_learned"].values()) != \
        list(informe["world_B_learned"].values())


# --- D1 a D11 siguen cayendo con el mismo arnés -------------------------------------------

def test_the_mutants_are_still_rejected_by_the_harness_that_certifies_production():
    """The matrix is not archived once production exists."""
    import sys
    sys.path.insert(0, "tests")
    from test_n10_u1_causal_form import D10, D11, MUTANTES

    for nombre, mutante, gate in MUTANTES:
        informe = causal_form_report(mutante)
        assert informe["G_U1_CAUSAL_FORM"] == CFResult.FAIL.value, nombre
        assert gate in informe["failed"], (nombre, informe["failed"])
    for clase in (D10, D11):
        assert world_truth_nonleakage(clase)["result"] == CFResult.FAIL.value
    assert causal_form_report(hacer, source=U1)["G_U1_CAUSAL_FORM"] == CFResult.PASS.value


# --- diferencial referencia ↔ producción ---------------------------------------------------

def test_reference_and_production_satisfy_the_contract_equivalently():
    """Not identity of implementation. Equivalent compliance: same token
    class, same action distribution, same table after the same experience,
    same freeze behaviour."""
    import sys
    sys.path.insert(0, "tests")
    from test_n10_u1_causal_form import Referencia

    banco = [(0.1, UP, +4.0), (0.9, DOWN, +4.0), (0.1, DOWN, -4.0),
             (0.9, UP, -4.0), (0.1, UP, +4.0)]
    ref, prod = Referencia(), hacer()
    for cue, accion, consecuencia in banco:
        for m in (ref, prod):
            m.perceive(cue)
            for _ in range(3):
                m.perceive(None)
            m.learn(accion, consecuencia)
    assert ref.memory == prod.memory
    assert {k: round(v, 9) for k, v in ref.theta.items()} == \
        {k: round(v, 9) for k, v in prod.theta.items()}

    acciones_ref = [ref.decide(np.random.default_rng(s)) for s in range(32)]
    acciones_prod = [prod.decide(np.random.default_rng(s)) for s in range(32)]
    assert acciones_ref == acciones_prod


# --- clonado limpio ------------------------------------------------------------------------

def test_one_acquisition_gives_three_identical_clones():
    """Three independent trainings are forbidden: the arms must differ only
    in the intervention."""
    u = hacer()
    for cue, accion in ((0.1, DOWN), (0.9, UP), (0.1, DOWN)):
        u.perceive(cue)
        u.learn(accion, 4.0)
    u.freeze()
    a, b, c = u.clone(), u.clone(), u.clone()
    assert a.theta_digest() == b.theta_digest() == c.theta_digest() == u.theta_digest()
    assert all(x.mode is Mode.EVALUATION for x in (a, b, c))
    assert all(x.config == u.config for x in (a, b, c))


def test_a_clone_is_independent_of_the_original():
    u = hacer()
    u.perceive(0.9)
    u.learn(UP, 4.0)
    copia = u.clone()
    copia.mode = Mode.ACQUISITION
    copia.learn(UP, -4.0)
    assert copia.theta_digest() != u.theta_digest()


# --- el organismo, dentro del aparato real --------------------------------------------------

def test_the_agent_only_learns_from_the_decision_it_just_made():
    from terrario.core.contracts import Transition
    from terrario.core.types import Consequence
    from terrario.lab import world_generator as gen

    w = gen.world_for(['EPMEM-A1'], seed=0, stations=4)
    ag = U1Agent(w, U1Config())
    t = Transition(observation_t=None, internal_state_ref=None, action_t=None,
                   consequence_t1=Consequence(energy_delta=4.0, events=[]),
                   observation_t1=None, terminated=False, truncated=False,
                   step=0, seed=0)
    antes = ag.core.theta_digest()
    ag.learn(t)
    assert ag.core.theta_digest() == antes, "sin decisión pendiente no se aprende"
    ag.core.perceive(0.9)
    ag._pending = UP
    ag.learn(t)
    assert ag.core.theta_digest() != antes


def test_the_agents_rng_is_its_own():
    """Its exploration must not consume draws that belong to the world, or
    one arm would displace another's world."""
    import inspect
    fuente = inspect.getsource(U1Agent.__init__)
    assert "default_rng(self.core.config.seed)" in fuente
    a = U1Agent(object(), U1Config(seed=1))
    b = U1Agent(object(), U1Config(seed=1))
    assert [a._rng.random() for _ in range(4)] == [b._rng.random() for _ in range(4)]
