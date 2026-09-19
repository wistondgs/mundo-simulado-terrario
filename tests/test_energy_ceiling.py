"""`max_energy` es un techo, no solo la escala del sensor.

Medido antes de esta reparacion: en el mundo rico la energia del agente llego a
1725.60 contra un `max_energy` de 60, y `get_observation` la recortaba a 1.0 en
el 96% de los pasos. El organismo dejaba de percibir su propia variable
esencial, y con ella moria el unico acoplamiento homeostatico que A4 tiene
(`a4_advanced.py:427`), que quedaba en el valor exacto de `use_homeostasis=False`
en 286 de 300 pasos.
"""

from __future__ import annotations

import numpy as np

from terrario.world.rules import RuleEngine
from terrario.world.state import WorldStateManager
from terrario.world.transition import build_world_state

MAX_ENERGY = 60.0


def _manager(start_energy: float) -> WorldStateManager:
    scenario = {
        "name": "techo", "grid_size": [5, 5], "duration": 10, "seed": 0,
        "view_radius": 2, "num_channels": 4,
        "max_energy": MAX_ENERGY, "step_energy_cost": 0.0,
        "expose_time_fraction": True,
        "objects": [{"pos": [2, 3], "channels": [0.9, 0.9, 0.9, 0.9],
                     "movable": False, "energy_value": 0.0}],
        "agent_start": {"pos": [2, 2], "energy": start_energy},
        "rules": {}, "changes": [],
    }
    return WorldStateManager(build_world_state(scenario), 10, MAX_ENERGY, 0.0, True)


def test_energy_never_exceeds_max_energy():
    world = _manager(start_energy=MAX_ENERGY - 1.0)
    world.set_agent_energy(0, MAX_ENERGY * 100)
    assert world._mutable_state().agents[0].energy == MAX_ENERGY


def test_death_still_decided_on_the_requested_value():
    """El suelo no se toca: un valor negativo se guarda negativo."""
    world = _manager(start_energy=1.0)
    world.set_agent_energy(0, -5.0)
    assert world._mutable_state().agents[0].energy == -5.0


def test_observation_no_longer_saturates():
    world = _manager(start_energy=MAX_ENERGY - 1.0)
    world.set_agent_energy(0, MAX_ENERGY * 100)
    assert world.get_observation(0, 2, 4).agent_energy == 1.0
    world.set_agent_energy(0, MAX_ENERGY / 2)
    assert world.get_observation(0, 2, 4).agent_energy == 0.5


def test_apply_effects_returns_what_was_realised_not_what_was_asked():
    """Saciedad: con el deposito lleno, consumir no paga.

    `energy_head` se entrena con este numero (`a4_advanced.py:635`). Si
    `apply_effects` devolviera lo pedido, el modelo del mundo aprenderia una
    consecuencia que no ocurrio, y la valoracion de CONSUME nunca bajaria al
    estar saciado.
    """
    from terrario.world.rules import RuleEffect

    rules = RuleEngine()
    effects = [RuleEffect(energy_delta=10.0)]

    hungry = _manager(start_energy=MAX_ENERGY - 10.0)
    assert rules.apply_effects(hungry, 0, 0, effects) == 10.0

    full = _manager(start_energy=MAX_ENERGY)
    assert rules.apply_effects(full, 0, 0, effects) == 0.0

    partial = _manager(start_energy=MAX_ENERGY - 4.0)
    assert rules.apply_effects(partial, 0, 0, effects) == 4.0


# --- P1.0 · el contrato de fisiologia ----------------------------------------

def test_requested_and_realised_separate_and_agree_when_there_is_room():
    from terrario.world.rules import RuleEffect

    rules = RuleEngine()
    effects = [RuleEffect(energy_delta=10.0)]

    room = _manager(start_energy=MAX_ENERGY - 20.0)
    app = rules.apply_effects_detailed(room, 0, 0, effects)
    assert (app.requested, app.realized) == (10.0, 10.0)
    assert app.clipped is False
    assert (app.energy_before, app.energy_after) == (MAX_ENERGY - 20.0, MAX_ENERGY - 10.0)


def test_requested_and_realised_diverge_exactly_by_what_did_not_fit():
    from terrario.world.rules import RuleEffect

    rules = RuleEngine()
    effects = [RuleEffect(energy_delta=10.0)]

    full = _manager(start_energy=MAX_ENERGY)
    app = rules.apply_effects_detailed(full, 0, 0, effects)
    assert app.requested == 10.0
    assert app.realized == 0.0          # saciedad
    assert app.clipped is True

    partial = _manager(start_energy=MAX_ENERGY - 4.0)
    app = rules.apply_effects_detailed(partial, 0, 0, effects)
    assert (app.requested, app.realized) == (10.0, 4.0)
    assert app.clipped is True


# --- D1 · una sola autoridad sobre el estado interoceptivo -------------------

def test_learn_does_not_touch_the_sensed_interoceptive_state():
    """`perceive` fija `homeostasis._energy`; `learn` no lo mueve.

    Antes, `learn` sumaba `consequence.energy_delta` --absoluto-- a una variable
    normalizada. Este test falla si alguien reintroduce esa integracion.
    """
    import sys
    from pathlib import Path as _P
    root = _P(__file__).resolve().parents[1]
    for p in (str(root), str(root / "scripts")):
        if p not in sys.path:
            sys.path.insert(0, p)

    from exp_adaptive_foraging_01 import BASE, rich_world
    from terrario.agent.agents import create_agent
    from terrario.core.rng import RNGManager
    from terrario.world.transition import build_episode_components, run_step

    seed, steps = 909, 25
    scenario = rich_world(seed, duration=steps)
    comps = build_episode_components(scenario, duration_fallback=steps,
                                     strict_physics=True, with_lifecycle=False,
                                     world_seed=seed)
    RNGManager.set_global_determinism(seed)
    agent = create_agent("A4_ADVANCED", dict(BASE), seed=seed)

    saw_a_gain = False
    for step in range(steps):
        out = run_step(comps, agent, step, world_seed=seed, agent_seed=seed,
                       max_steps=steps, learning_enabled=True)
        # tras el paso completo (perceive -> decide -> learn) el estado sentido
        # sigue siendo exactamente el que `perceive` escribio.
        assert agent.homeostasis.energy == out.observation_t.agent_energy
        saw_a_gain = saw_a_gain or out.energy_delta > 0
        if out.terminated or out.truncated:
            break
    assert saw_a_gain, "el episodio no tuvo ninguna ganancia: el test no probaria nada"
