"""La huella adaptativa cubre la frontera adoptada, y sólo esa frontera.

Esto existe porque `_adaptive_state_hash` no veía `_energy_baseline` durante
meses y nadie lo notó: la huella se usaba como prueba de «no hubo adaptación» y
para esa pieza se satisfacía en vacío. Un control permanente lo habría cazado
solo, y eso es lo que son estas pruebas.

Dos mitades, y hacen falta las dos:

  sensibilidad   mover una pieza de la frontera SIEMPRE mueve la huella
  especificidad  mover algo de fuera NUNCA la mueve

Sin la segunda, un digest que hashease A4 entero pasaría la primera y no
serviría para nada: cualquier paso de percepción lo movería.
"""

from __future__ import annotations

import pytest
import torch

from terrario.agent.adaptive_freeze import (
    ADAPTIVE_FINGERPRINT_VERSION,
    CANONICAL_ORDER,
    AdaptiveRegime,
    adaptive_components,
    adaptive_fingerprint,
    regime_of,
)
from terrario.agent.agents import create_agent
from terrario.core.rng import RNGManager

CONFIG = {
    "use_planner": False, "use_uncertainty": True, "use_episodic_memory": True,
    "use_longterm_memory": True, "use_temporal": True, "use_online_learning": True,
    "latent_dim": 16, "hidden_dim": 24, "memory_dim": 8, "memory_slots": 4,
    "memory_capacity": 16, "ensemble_size": 2,
}


def agent(**overrides):
    RNGManager.set_global_determinism(0)
    return create_agent("A4_ADVANCED", dict(CONFIG) | overrides, seed=0)


# --- La huella es una función, no una casualidad -----------------------------

def test_two_identical_agents_fingerprint_the_same():
    assert adaptive_fingerprint(agent()) == adaptive_fingerprint(agent())


def test_fingerprint_is_deterministic_across_calls():
    a = agent()
    assert adaptive_fingerprint(a) == adaptive_fingerprint(a)


def test_the_canonical_order_covers_every_component():
    assert set(adaptive_components(agent())) == set(CANONICAL_ORDER)


def test_m_appears_once_and_not_inside_parameters():
    """`M` es un `nn.Parameter` y está DENTRO del optimizador, así que sin
    excluirla de `parameters` contaría dos veces -- y el brazo heredado parecería
    mover parámetros cuando lo que movió fue la memoria."""
    a = agent()
    assert "longterm_memory.M" in a.get_parameters()
    before = adaptive_components(a)
    a.longterm_memory.M.data.add_(1.0)
    after = adaptive_components(a)
    assert after["longterm_M"] != before["longterm_M"]
    assert after["parameters"] == before["parameters"]


# --- Sensibilidad: una pieza cada vez ----------------------------------------

def _move_parameters(a):
    """Mueve un parámetro del optimizador que no sea `M`, sea cual sea el head."""
    with torch.no_grad():
        for prefix, module in a._parameter_modules():
            for name, parameter in module.named_parameters():
                if f"{prefix}.{name}" != "longterm_memory.M":
                    parameter.add_(1.0)
                    return
    raise AssertionError("no hay parámetros fuera de M")


def _move_episodic_buffer(a):
    a.episodic_memory.write(embedding=torch.zeros(CONFIG["latent_dim"]), action=1,
                            energy_delta=0.5, prediction_error=0.1, timestamp=0)


def _move_longterm_M(a):
    a.longterm_memory.M.data.add_(1.0)


def _move_baseline_value(a):
    a._energy_baseline = float(a._energy_baseline) + 42.0


def _move_baseline_count(a):
    a._baseline_count = int(a._baseline_count) + 17


MOVES = {
    "parameters": _move_parameters,
    "episodic_buffer": _move_episodic_buffer,
    "longterm_M": _move_longterm_M,
    "baseline value": _move_baseline_value,
    # `_baseline_count` no es contabilidad: es el denominador del paso de la
    # media corrida. Medido -- contador 1 frente a 50, todo lo demás idéntico,
    # un solo evento elegible: línea base 0.175 frente a 0.487254901961 y
    # parámetros distintos. Pertenece a la frontera.
    "baseline count": _move_baseline_count,
}


@pytest.mark.parametrize("piece", sorted(MOVES))
def test_moving_one_adaptive_piece_moves_the_fingerprint(piece):
    a = agent()
    before = adaptive_fingerprint(a)
    MOVES[piece](a)
    assert adaptive_fingerprint(a) != before, f"la huella no ve {piece}"


@pytest.mark.parametrize("piece", sorted(MOVES))
def test_moving_one_adaptive_piece_moves_exactly_one_component(piece):
    a = agent()
    before = adaptive_components(a)
    MOVES[piece](a)
    moved = [k for k, v in adaptive_components(a).items() if v != before[k]]
    assert len(moved) == 1, f"{piece} movió {moved}"


def test_the_historical_hash_would_have_failed_this_very_test():
    """El fallo concreto que estas pruebas existen para impedir."""
    from terrario.experiment.adaptation import _adaptive_state_hash

    a = agent()
    before = _adaptive_state_hash(a)
    _move_baseline_value(a)
    _move_baseline_count(a)
    assert _adaptive_state_hash(a) == before      # la histórica NO lo ve
    assert adaptive_fingerprint(a) != before      # la nueva sí


# --- Especificidad: lo que está fuera no la mueve ----------------------------

def _move_hidden(a):
    a._hidden = torch.ones_like(a._hidden)


def _move_step(a):
    a._step += 7


def _move_homeostasis_energy(a):
    a.homeostasis._energy = 0.123


def _move_last_prediction_error(a):
    a.last_prediction_error = 0.99


def _move_learner_step_count(a):
    a.learner._step_count += 3


def _move_gradients(a):
    for parameter in a.policy_head.parameters():
        parameter.grad = torch.ones_like(parameter)


OUTSIDE = {
    "_hidden (recurrente)": _move_hidden,
    "_step": _move_step,
    "homeostasis._energy": _move_homeostasis_energy,
    "last_prediction_error": _move_last_prediction_error,
    "learner._step_count": _move_learner_step_count,
    "parameter.grad": _move_gradients,
}


@pytest.mark.parametrize("piece", sorted(OUTSIDE))
def test_moving_something_outside_the_boundary_leaves_the_fingerprint_alone(piece):
    """Sin esto, un digest que hashease A4 entero pasaría la mitad de arriba."""
    a = agent()
    before = adaptive_fingerprint(a)
    OUTSIDE[piece](a)
    assert adaptive_fingerprint(a) == before, f"la huella ve {piece}, que está fuera"


# --- Versionado y régimen ----------------------------------------------------

def test_the_fingerprint_declares_its_version_and_differs_from_the_historical():
    from terrario.experiment.adaptation import _adaptive_state_hash

    a = agent()
    assert ADAPTIVE_FINGERPRINT_VERSION.endswith("/ocf-1")
    assert adaptive_fingerprint(a) != _adaptive_state_hash(a)


def test_the_regime_is_read_from_what_governs_not_from_a_label():
    assert regime_of(agent()) is AdaptiveRegime.NORMAL
    assert regime_of(agent(learning_commit_enabled=False)) is AdaptiveRegime.PARAMETRIC_FREEZE
    assert regime_of(agent(full_adaptive_freeze=True)) is AdaptiveRegime.FULL_ADAPTIVE_FREEZE


def test_undeclared_exists_so_old_evidence_is_not_read_as_normal():
    assert AdaptiveRegime.UNDECLARED.value == "UNDECLARED"
    assert AdaptiveRegime.UNDECLARED is not AdaptiveRegime.NORMAL
