#!/usr/bin/env python
"""¿Puede A4 aprender la relación 0.82/0.18 si se le da experiencia suficiente?

P1 midió cero adquisición sobre 1200 pasos de D4T, y la causa próxima medida fue
que el organismo recibe ~6 ejemplos informativos por vida. Eso es una afirmación
sobre el MUNDO, no sobre el learner. Esta prueba separa las dos: entrega al
mismo A4 un stream controlado fuera del mundo, con N ejemplos informativos, y
mide si la cabeza de energía llega a discriminar.

Dos curvas, porque responden a preguntas distintas:

  PURA      N ejemplos informativos consecutivos.
            → ¿puede el learner aprenderlo, y con cuántas muestras?

  DILUIDA   los mismos N ejemplos repartidos 1 de cada 100 pasos metabólicos,
            que es la densidad real de D4T.
            → ¿es la dilución lo que lo impide, o el número de ejemplos?

Las observaciones se construyen con `WorldStateManager.get_observation`, nunca a
mano. Esto importa: el formato real pone OCCUPANCY en el canal 0 y desplaza los
canales del objeto a 1..3, y un banco escrito a mano que ponga el canal causal en
el índice 0 entrega al encoder algo que nunca vio durante el entrenamiento.

Banco de examen: entidades con valores de canal DISJUNTOS de los entrenados, en
el mismo formato. Azar = 0.5.

Engineering sandbox. No es evidencia.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import numpy as np
import torch

from terrario.agent.agents import create_agent
from terrario.core.contracts import Transition
from terrario.core.types import (
    NUM_DIRECTIONS, Action, ActionType, Consequence, Direction,
)
from terrario.experiment.controller import build_world_state
from terrario.world.state import WorldStateManager

GRID, VIEW_RADIUS, CHANNELS = 14, 2, 4
FAVOURABLE, UNFAVOURABLE = +1.0, -1.0
STEP_COST = -0.06

TRAIN_BANDS = {"fav": (0.70, 0.84), "unfav": (0.16, 0.30)}
TEST_BANDS = {"fav": (0.86, 0.98), "unfav": (0.02, 0.14)}

DIRECTIONS = [Direction.UP, Direction.DOWN, Direction.LEFT, Direction.RIGHT]
DELTA = {Direction.UP: (-1, 0), Direction.DOWN: (1, 0),
         Direction.LEFT: (0, -1), Direction.RIGHT: (0, 1)}


def _world(objects, agent_pos=(7, 7)):
    """A real world state, so observations come out in the runtime's own format."""
    scenario = {"grid_size": [GRID, GRID], "objects": objects,
                "agent_start": {"pos": list(agent_pos), "energy": 60.0}}
    return WorldStateManager(build_world_state(scenario), 1200, 100.0, 0.06, False)


def _channels(rng, band, decorrelate=False):
    primary = rng.uniform(*band)
    rest = ([rng.uniform(0.0, 1.0) for _ in range(3)] if decorrelate
            else [1.0 - primary, rng.uniform(0.1, 0.4), rng.uniform(0.1, 0.4)])
    return [round(primary, 4)] + [round(v, 4) for v in rest]


def informative_example(rng, bands):
    """One (observation, action, consequence) where a consume lands on a class."""
    favourable = rng.random() < 0.5
    band = bands["fav"] if favourable else bands["unfav"]
    direction = rng.choice(DIRECTIONS)
    dx, dy = DELTA[direction]
    world = _world([{"pos": [7 + dx, 7 + dy], "channels": _channels(rng, band),
                     "movable": False}])
    observation = world.get_observation(0, VIEW_RADIUS, CHANNELS)
    action = Action(action_type=ActionType.CONSUME, direction=direction)
    delta = (FAVOURABLE if favourable else UNFAVOURABLE) + STEP_COST
    return observation, action, delta


def metabolic_example(rng):
    """A step where nothing happens except the cost -- the other 99% of D4T."""
    direction = rng.choice(DIRECTIONS)
    world = _world([{"pos": [3, 3], "channels": [0.5, 0.5, 0.5, 0.5], "movable": False}])
    observation = world.get_observation(0, VIEW_RADIUS, CHANNELS)
    return observation, Action(action_type=ActionType.MOVE, direction=direction), STEP_COST


def feed(agent, stream):
    """Perceive, decide, force the recorded action, learn. Same shape as a rollout."""
    import torch.nn.functional as F
    for observation, action, delta in stream:
        agent.perceive(observation)
        agent.decide()
        state = agent._last_state
        if state is not None:
            agent._last_action = action.to_int()
            logits = agent.policy_head(state)
            agent._last_log_prob = torch.log(
                F.softmax(logits, dim=-1)[action.to_int()] + 1e-8)
        agent.learn(Transition(
            observation_t=observation, internal_state_ref=None, action_t=action,
            consequence_t1=Consequence(energy_delta=delta, events=[],
                                       new_observation=observation, done=False),
            observation_t1=observation, terminated=False, truncated=False,
            step=0, seed=0))


def exam(agent, probes):
    """Does the energy head rank the favourable entity above the unfavourable one?"""
    correct = evaluated = 0
    for good_dir, bad_dir, world in probes:
        observation = world.get_observation(0, VIEW_RADIUS, CHANNELS)
        agent.perceive(observation)
        if agent._last_latent is None:
            continue
        hidden = torch.zeros(agent.config["hidden_dim"])
        state = agent._build_state(agent._last_latent, hidden)
        scores = []
        for direction in (good_dir, bad_dir):
            action_int = int(ActionType.CONSUME) * NUM_DIRECTIONS + int(direction)
            with torch.no_grad():
                _, energy, _ = agent.world_model(state, agent._action_to_onehot(action_int))
            scores.append(float(energy.item()))
        if abs(scores[0] - scores[1]) < 1e-9:
            continue          # sin preferencia: fuera del denominador
        evaluated += 1
        correct += scores[0] > scores[1]
    return (correct / evaluated) if evaluated else None, evaluated


def build_probes(count, rng, bands, decorrelate=False):
    probes = []
    for _ in range(count):
        good_dir, bad_dir = rng.sample(DIRECTIONS, 2)
        gdx, gdy = DELTA[good_dir]
        bdx, bdy = DELTA[bad_dir]
        probes.append((good_dir, bad_dir, _world([
            {"pos": [7 + gdx, 7 + gdy], "channels": _channels(rng, bands["fav"], decorrelate),
             "movable": False},
            {"pos": [7 + bdx, 7 + bdy], "channels": _channels(rng, bands["unfav"], decorrelate),
             "movable": False}])))
    return probes


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sizes", default="6,12,24,48,96,192,384,768")
    ap.add_argument("--seeds", type=int, default=5)
    ap.add_argument("--probes", type=int, default=200)
    ap.add_argument("--dilution", type=int, default=100)
    ap.add_argument("--modes", default="pure,diluted",
                    help="La curva diluida cuesta N x dilution pasos por semilla: "
                         "a 1:100 son cinco horas. Se corre aparte, a proposito.")
    ap.add_argument("--max-diluted", type=int, default=192)
    ap.add_argument("--out", default="artifacts/learner_sample_efficiency.json")
    args = ap.parse_args()

    sizes = [int(s) for s in args.sizes.split(",")]
    # El banco se construye UNA vez. Reconstruirlo por semilla levantaba 200
    # mundos en cada iteración, que era casi todo el coste de la corrida.
    held_out = build_probes(args.probes, random.Random(20260917), TEST_BANDS)
    rows = []
    for n in sizes:
        for mode in args.modes.split(","):
            if mode == "diluted" and n > args.max_diluted:
                continue
            scores = []
            for offset in range(args.seeds):
                seed = 1000041 + offset
                rng = random.Random(seed)
                torch.manual_seed(seed)
                agent = create_agent("A4", {"num_channels": CHANNELS, "view_size": 5}, seed=seed)

                stream = []
                for _ in range(n):
                    stream.append(informative_example(rng, TRAIN_BANDS))
                    if mode == "diluted":
                        stream.extend(metabolic_example(rng)
                                      for _ in range(args.dilution - 1))
                before, _ = exam(agent, held_out)
                feed(agent, stream)
                after, support = exam(agent, held_out)
                scores.append({"seed": seed, "before": before, "after": after,
                               "support": support, "stream_length": len(stream)})
            usable = [s["after"] for s in scores if s["after"] is not None]
            mean_after = sum(usable) / len(usable) if usable else None
            rows.append({"n_informative": n, "mode": mode, "seeds": scores,
                         "mean_after": round(mean_after, 4) if mean_after is not None else None,
                         "above_chance_seeds": sum(1 for v in usable if v > 0.5)})
            print(f"  n={n:>4} {mode:<8} examen={mean_after}  "
                  f"por encima de azar: {rows[-1]['above_chance_seeds']}/{len(usable)}",
                  flush=True)

    out = {"schema_version": "terrario.lab.sample-efficiency/v1",
           "classification": "ENGINEERING_SANDBOX_NOT_EVIDENCE",
           "chance_level": 0.5, "train_bands": TRAIN_BANDS, "test_bands": TEST_BANDS,
           "dilution": args.dilution, "rows": rows}
    path = PROJECT_ROOT / args.out
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nwrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
