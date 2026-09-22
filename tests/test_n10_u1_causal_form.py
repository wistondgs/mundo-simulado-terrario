"""N1.0 · la forma causal, y once degeneraciones que tienen que caer.

The reference mechanism lives HERE and not in `terrario/lab/`, deliberately.
Running D1-D11 needs something for the gates to intervene on, and anything
that passes every gate is structurally U1; keeping it in the test file means
no campaign can import it by accident and mistake a specification fixture for
the organism.
"""

from __future__ import annotations

import pytest

from terrario.lab.n10_u1_spec import (
    ACQUIRED, ACTIONS, CAUSAL_FORM, CF_GATES, DOWN, EMPTY, FORBIDDEN_INPUTS,
    SUPPLIED, UP, CFResult, causal_form_report, cf1_cue_writes_memory,
    cf2_retention, cf3_memory_can_modulate_decision, cf4_consequence_enters_update,
    cf5_memory_enters_update, cf6_action_enters_update, cf7_evaluation_freezes,
    cf8_neutral_initialization, contingency_reversal, opaque_token,
    token_permutation, world_truth_nonleakage, _digest,
)

ALFA, EPSILON = 0.3, 0.2


class Referencia:
    """La forma sellada, y nada más que ella.

    Fixture de especificación: existe para que los mutantes tengan contra qué
    fallar. No es el organismo y no vive en la librería.
    """

    def __init__(self) -> None:
        self.memory: str = EMPTY
        self.theta: dict = {}
        self.learning: bool = True

    def perceive(self, cue_value):
        if cue_value is not None:
            self.memory = opaque_token(cue_value)

    def decide(self, rng):
        if rng.random() < EPSILON:
            return ACTIONS[int(rng.integers(2))]
        arriba = self.theta.get((self.memory, UP), 0.0)
        abajo = self.theta.get((self.memory, DOWN), 0.0)
        if arriba == abajo:
            # Desempate por azar y no por orden de acciones: un desempate
            # posicional sería conducta condicionada sin que la tabla lo diga.
            return ACTIONS[int(rng.integers(2))]
        return UP if arriba > abajo else DOWN

    def learn(self, action, consequence):
        if not self.learning:
            return
        clave = (self.memory, action)
        q = self.theta.get(clave, 0.0)
        self.theta[clave] = q + ALFA * (consequence - q)

    def theta_digest(self):
        return _digest(self.theta)


def test_the_reference_passes_every_causal_form_gate():
    informe = causal_form_report(Referencia, source=Referencia)
    assert informe["G_U1_CAUSAL_FORM"] == CFResult.PASS.value, informe["failed"]
    assert len(informe["gates"]) == 11


def test_contingency_reversal_learns_both_worlds_from_one_starting_state():
    """The guard no wiring survives. Grepping for a hard-coded mapping finds
    the clumsy version and misses every other one; learning the normal
    correspondence AND its inverse from one identical start cannot be faked."""
    informe = contingency_reversal(Referencia)
    assert informe["result"] == CFResult.PASS.value
    assert set(informe["world_A_learned"].values()) == {UP, DOWN}
    assert list(informe["world_A_learned"].values()) != \
        list(informe["world_B_learned"].values())


def test_renaming_the_tokens_preserves_learnability():
    assert token_permutation(Referencia)["result"] == CFResult.PASS.value


def test_the_token_carries_no_semantics_and_no_raw_float_equality():
    import inspect
    a, b = opaque_token(0.1), opaque_token(0.9)
    assert a != b and a.startswith("tau_") and b.startswith("tau_")
    assert opaque_token(0.1) == opaque_token(0.100001)
    fuente = inspect.getsource(opaque_token)
    for prohibido in ("up", "down", "reward", "correct"):
        assert prohibido not in fuente.split('"""')[-1]


# --- D1 a D11 · cada degeneración tumba al menos un gate ------------------------------

def _mutante(**cambios):
    return type("Mutante", (Referencia,), cambios)


D1 = _mutante(perceive=lambda self, cue: None)
D2 = _mutante(perceive=lambda self, cue: setattr(
    self, "memory", opaque_token(cue) if cue is not None else EMPTY))
D3 = _mutante(decide=lambda self, rng: ACTIONS[int(rng.integers(2))])
D4 = _mutante(learn=lambda self, a, c: self.theta.__setitem__(
    ("SIN_TOKEN", a), self.theta.get(("SIN_TOKEN", a), 0.0) + ALFA * c)
    if self.learning else None)
D5 = _mutante(learn=lambda self, a, c: self.theta.__setitem__(
    (self.memory, UP), self.theta.get((self.memory, UP), 0.0) + ALFA * c)
    if self.learning else None)
D6 = _mutante(learn=lambda self, a, c: self.theta.__setitem__(
    (self.memory, a), self.theta.get((self.memory, a), 0.0) + ALFA * 1.0)
    if self.learning else None)
D7 = _mutante(learn=lambda self, a, c: self.theta.__setitem__(
    (self.memory, a), self.theta.get((self.memory, a), 0.0) + ALFA * (250.0 - 0.0))
    if self.learning else None)
D8 = _mutante(learn=lambda self, a, c: self.theta.__setitem__(
    (self.memory, a), self.theta.get((self.memory, a), 0.0)
    + ALFA * (c - self.theta.get((self.memory, a), 0.0))))


class D9(Referencia):
    """Preferencias de acción por token, precableadas al nacer."""
    def __init__(self):
        super().__init__()
        self.theta = {(opaque_token(0.9), UP): 9.0, (opaque_token(0.9), DOWN): 0.0,
                      (opaque_token(0.1), UP): 0.0, (opaque_token(0.1), DOWN): 9.0}


class D10(Referencia):
    """Consume la verdad del experimento."""
    def decide(self, rng, history_id=None):
        return UP if history_id == "0.90" else DOWN


class D11(Referencia):
    """Consume directamente la acción correcta."""
    def decide(self, rng, correct_action=None):
        return correct_action or UP


MUTANTES = [
    ("D1 ignora el cue al escribir memoria", D1, "CF1"),
    ("D2 borra la memoria durante el delay", D2, "CF2"),
    ("D3 ignora la memoria al decidir", D3, "CF3"),
    ("D4 ignora la memoria al actualizar", D4, "CF5"),
    ("D5 ignora la accion al actualizar", D5, "CF6"),
    ("D6 ignora la consecuencia", D6, "CF4"),
    ("D7 usa el NIVEL de energia, no el delta", D7, "CF4"),
    ("D8 sigue aprendiendo en evaluacion", D8, "CF7"),
    ("D9 nace con preferencias por token", D9, "CF8"),
]


@pytest.mark.parametrize("nombre,mutante,gate_esperado", MUTANTES)
def test_each_degeneration_fails_a_named_gate(nombre, mutante, gate_esperado):
    informe = causal_form_report(mutante)
    assert informe["G_U1_CAUSAL_FORM"] == CFResult.FAIL.value, nombre
    assert gate_esperado in informe["failed"], (nombre, informe["failed"])


def test_d10_and_d11_are_refused_by_the_input_contract_not_by_a_gate():
    """A mechanism that reads world truth cannot even be offered to the
    gates: `decide` is called with an rng and nothing else, so the extra
    argument is never supplied and the leak is structural rather than
    detected after the fact."""
    import inspect
    for clase in (D10, D11):
        parametros = set(inspect.signature(clase.decide).parameters)
        assert parametros & {"history_id", "correct_action"}
        informe = causal_form_report(clase)
        assert informe["G_U1_CAUSAL_FORM"] == CFResult.FAIL.value


def test_the_source_guard_catches_a_mechanism_that_names_world_truth():
    assert world_truth_nonleakage(D10)["result"] == CFResult.FAIL.value
    assert "history_id" in world_truth_nonleakage(D10)["forbidden_found"]
    assert world_truth_nonleakage(D11)["forbidden_found"] == ["correct_action"]
    assert world_truth_nonleakage(Referencia)["result"] == CFResult.PASS.value


def test_every_gate_has_at_least_one_mutant_that_fails_it():
    """A gate nobody can fail is not a gate. D1-D9 cover CF1 through CF8."""
    cubiertos = {g for _, _, g in MUTANTES}
    assert cubiertos == {"CF1", "CF2", "CF3", "CF4", "CF5", "CF6", "CF7", "CF8"}


def test_contingency_reversal_does_not_catch_a_wired_in_mapping():
    """Measured, and it corrects the expectation this gate was added with.

    Reversal was meant to be the guard no wiring survives. It is not: D9 is
    born preferring UP under one token and DOWN under the other, and it still
    learns BOTH worlds — because a learner can un-learn what it was born
    with, and after four hundred trials what it prefers follows what it
    experienced either way.

    So the two gates prove different things and neither substitutes for the
    other. Reversal shows the learned mapping FOLLOWS experience; it says
    nothing about what was there before. Only CF8, which runs the policy at
    initialization instead of inspecting the table, shows there was no
    mapping to begin with. Had this suite carried reversal alone, D9 would
    have walked through it."""
    assert contingency_reversal(D9)["result"] == CFResult.PASS.value
    assert cf8_neutral_initialization(D9)["result"] == CFResult.FAIL.value
    assert "CF8" in causal_form_report(D9)["failed"]


# --- lo que la especificación declara ---------------------------------------------------

def test_the_spec_states_what_is_supplied_and_what_is_acquired():
    assert len(SUPPLIED) == 8 and len(ACQUIRED) == 2
    assert all("which action becomes preferable" in a for a in ACQUIRED)
    assert "history_id" in FORBIDDEN_INPUTS
    assert "correct_action" in FORBIDDEN_INPUTS
    assert len(CAUSAL_FORM) == 5


def test_the_spec_says_what_the_gate_does_not_prove():
    from terrario.lab.n10_u1_spec import WHAT_THIS_GATE_DOES_NOT_PROVE
    assert len(WHAT_THIS_GATE_DOES_NOT_PROVE) == 4
    assert any("budget" in s for s in WHAT_THIS_GATE_DOES_NOT_PROVE)
