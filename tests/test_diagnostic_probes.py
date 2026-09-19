"""El banco de sondas mide sin tocar, o no mide nada.

La pasividad es el requisito, no una cortesía: la sonda anterior de esta familia
infló dos magnitudes ×18.6 y ×10 por contaminarse a sí misma, y sólo lo vio una
verificación adversarial.
"""

from __future__ import annotations

import pytest
import torch

from terrario.lab.causal_bench import (
    REGIME_INTERVENTIONS, BirthSnapshot, birth_certificate, causal_state_digest,
)
from terrario.lab.diagnostic_probes import (
    build_probe_bank, consume_advantage_on, gain, passive_probe, read_bank,
)

CONFIG = {
    "use_planner": True, "use_world_model": True, "use_uncertainty": True,
    "use_episodic_memory": True, "use_longterm_memory": True, "use_temporal": True,
    "use_online_learning": True, "view_size": 5,
    "latent_dim": 16, "hidden_dim": 24, "memory_dim": 8, "memory_slots": 4,
    "memory_capacity": 16, "ensemble_size": 2,
    "planner_horizon": 5, "planner_candidates": 10,
}


def agent():
    return BirthSnapshot.materialize("p", CONFIG, seed=0).prototype


def test_the_bank_has_favourable_situations_and_their_controls():
    bank = build_probe_bank()
    assert sum(p.favourable for p in bank) == 4          # las cuatro direcciones
    assert sum(not p.favourable for p in bank) == 3      # distancia 2, 3 y vacío
    assert len({p.probe_id for p in bank}) == len(bank)


def test_every_arm_receives_identical_observations():
    """Que los estados difieran es el órgano; que las OBSERVACIONES difieran
    sería contaminación."""
    one, other = build_probe_bank(), build_probe_bank()
    for a, b in zip(one, other):
        assert a.probe_id == b.probe_id
        assert torch.equal(torch.as_tensor(a.observation.channels),
                           torch.as_tensor(b.observation.channels))


# --- Pasividad, que es el punto ---------------------------------------------

def test_reading_the_bank_leaves_no_trace():
    a = agent()
    before = birth_certificate(a)
    rng_before = a._generator.get_state().clone()
    read_bank(a, build_probe_bank())
    assert birth_certificate(a) == before
    assert torch.equal(a._generator.get_state(), rng_before)


def test_reading_twice_gives_the_same_reading():
    a, bank = agent(), build_probe_bank()
    assert read_bank(a, bank).by_probe == read_bank(a, bank).by_probe


def test_passive_probe_restores_volatile_state():
    a = agent()
    a._hidden = torch.ones_like(a._hidden)
    a._step = 41
    hidden_before, step_before = a._hidden.clone(), a._step
    with passive_probe(a):
        a._hidden = torch.zeros_like(a._hidden)
        a._step = 999
        torch.randint(0, 10, (7,), generator=a._generator)
    assert torch.equal(a._hidden, hidden_before)
    assert a._step == step_before


def test_probing_does_not_move_any_adaptive_component():
    a = agent()
    before = causal_state_digest(a)
    read_bank(a, build_probe_bank())
    after = causal_state_digest(a)
    assert {k: v for k, v in after.items() if k.startswith("adaptive.")} == \
           {k: v for k, v in before.items() if k.startswith("adaptive.")}


# --- Lo que la lectura significa --------------------------------------------

def test_discrimination_is_favourable_minus_control():
    """Aprender que CONSUME paga SIEMPRE es sesgo, no conocimiento."""
    reading = read_bank(agent(), build_probe_bank())
    assert reading.discrimination == pytest.approx(
        reading.favourable - reading.control)


def test_gain_is_post_minus_pre_on_all_three():
    a, bank = agent(), build_probe_bank()
    pre = read_bank(a, bank)
    with torch.no_grad():                      # mover el world model a mano
        a.world_model.energy_head.bias.add_(0.5)
    post = read_bank(a, bank)
    g = gain(pre, post)
    assert g["favourable"] == pytest.approx(post.favourable - pre.favourable)
    assert g["discrimination"] == pytest.approx(post.discrimination - pre.discrimination)


def test_a_uniform_shift_moves_the_level_but_not_the_discrimination():
    """Un sesgo que sube CONSUME en todas las situaciones no es aprendizaje, y
    el estimando de F1 tiene que ignorarlo."""
    a, bank = agent(), build_probe_bank()
    pre = read_bank(a, bank)
    with torch.no_grad():
        a.world_model.energy_head.bias.add_(1.0)
    post = read_bank(a, bank)
    g = gain(pre, post)
    assert abs(g["discrimination"]) < 1e-6      # el sesgo uniforme se cancela


def test_two_arms_from_one_birth_read_identically_before_acquisition():
    arms = BirthSnapshot.materialize("p", CONFIG, seed=0).triplet()
    bank = build_probe_bank()
    readings = [read_bank(a.specimen, bank).by_probe for a in arms.values()]
    assert readings[0] == readings[1] == readings[2]
