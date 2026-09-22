"""Las tres intervenciones · cada una cambia una cosa y ninguna otra."""

from __future__ import annotations

import numpy as np
import pytest

from terrario.lab import world_generator as gen
from terrario.lab.n10_arms import (
    Arm, CompleteArm, HistoryShuffledArm, MemoryReadLesionArm, build_arm)
from terrario.lab.n10_u1 import Mode, U1, U1Config
from terrario.lab.n10_u1_spec import DOWN, EMPTY, UP, opaque_token

CFG = U1Config(alpha=0.3, exploration=0.0, seed=0)


def entrenado():
    u = U1(CFG)
    for cue, accion in ((0.9, UP), (0.1, DOWN)) * 6:
        u.perceive(cue)
        u.learn(accion, 4.0)
    u.freeze()
    return u


def mundo():
    w = gen.world_for(['EPMEM-A1'], seed=0, stations=8)
    w.scenario['expose_time_fraction'] = False
    return w


def test_the_three_arms_start_bit_identical():
    s = entrenado()
    brazos = [build_arm(a, mundo(), s, CFG) for a in
              (Arm.COMPLETE, Arm.MEMORY_READ_LESION, Arm.HISTORY_SHUFFLED)]
    digests = {b.core.theta_digest() for b in brazos}
    assert len(digests) == 1
    assert digests == {s.theta_digest()}
    assert all(b.core.mode is Mode.EVALUATION for b in brazos)


def test_arm_b_keeps_writing_the_token_and_only_blocks_the_read():
    """It is a read lesion, not an ablation: the write path is untouched and
    stays observable between decisions."""
    b = build_arm(Arm.MEMORY_READ_LESION, mundo(), entrenado(), CFG)
    b.core.perceive(0.9)
    assert b.core.memory == opaque_token(0.9), "la escritura sigue"
    b._doors_here = True
    b.decide()
    assert b.core.memory == opaque_token(0.9), "y se restaura tras decidir"


def test_arm_b_cannot_use_the_retained_token_to_choose():
    s = entrenado()
    a = build_arm(Arm.COMPLETE, mundo(), s, CFG)
    b = build_arm(Arm.MEMORY_READ_LESION, mundo(), s, CFG)
    elegidas_a, elegidas_b = [], []
    for cue in (0.9, 0.1) * 8:
        for agente, salida in ((a, elegidas_a), (b, elegidas_b)):
            agente.core.perceive(cue)
            agente._doors_here = True
            salida.append(agente.decide().direction.name)
    assert elegidas_a == ["UP", "DOWN"] * 8, elegidas_a
    assert len(set(elegidas_b)) >= 1
    assert elegidas_a != elegidas_b


def test_arm_c_reads_the_substituted_token_and_restores_the_real_one():
    c = build_arm(Arm.HISTORY_SHUFFLED, mundo(), entrenado(), CFG)
    c.core.perceive(0.9)
    real = c.core.memory
    c.override_token(opaque_token(0.1))
    c._doors_here = True
    accion = c.decide()
    assert accion.direction.name == "DOWN", "decidió con el token sustituido"
    assert c.core.memory == real, "y el real vuelve a su sitio"
    assert c.substitutions == [(real, opaque_token(0.1))]


def test_arm_c_touches_neither_the_table_nor_the_mode():
    s = entrenado()
    c = build_arm(Arm.HISTORY_SHUFFLED, mundo(), s, CFG)
    antes = c.core.theta_digest()
    c.core.perceive(0.9)
    c.override_token(opaque_token(0.1))
    c._doors_here = True
    c.decide()
    assert c.core.theta_digest() == antes == s.theta_digest()
    assert c.core.mode is Mode.EVALUATION


def test_arm_c_without_a_substitute_behaves_as_complete():
    """So the intervention is the substitution and not the wrapper."""
    s = entrenado()
    a = build_arm(Arm.COMPLETE, mundo(), s, CFG)
    c = build_arm(Arm.HISTORY_SHUFFLED, mundo(), s, CFG)
    for cue in (0.9, 0.1):
        for agente in (a, c):
            agente.core.perceive(cue)
            agente._doors_here = True
        assert a.decide().direction.name == c.decide().direction.name


def test_a_clone_for_an_arm_is_independent_of_the_snapshot():
    s = entrenado()
    a = build_arm(Arm.COMPLETE, mundo(), s, CFG)
    a.core.mode = Mode.ACQUISITION
    a.core.learn(UP, -99.0)
    assert a.core.theta_digest() != s.theta_digest()


def test_the_arms_do_not_learn_during_evaluation():
    from terrario.core.contracts import Transition
    from terrario.core.types import Consequence
    s = entrenado()
    for arm in (Arm.COMPLETE, Arm.MEMORY_READ_LESION, Arm.HISTORY_SHUFFLED):
        ag = build_arm(arm, mundo(), s, CFG)
        antes = ag.core.theta_digest()
        ag.core.perceive(0.9)
        ag._pending = UP
        ag.learn(Transition(observation_t=None, internal_state_ref=None,
                            action_t=None,
                            consequence_t1=Consequence(energy_delta=-4.15, events=[]),
                            observation_t1=None, terminated=False, truncated=False,
                            step=0, seed=0))
        assert ag.core.theta_digest() == antes, arm
