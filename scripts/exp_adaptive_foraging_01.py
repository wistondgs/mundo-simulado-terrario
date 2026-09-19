#!/usr/bin/env python
"""EXP-ADAPTIVE-FORAGING-01 · la primera capacidad conductual del organismo.

    ¿Puede A4 adquirir de la experiencia una capacidad de forrajeo que
    PERSISTA y mejore después su conducta autónoma?

Dos partes, y la primera no afirma autonomía.

E2-A · APRENDIBILIDAD. Los tres brazos reciben EXACTAMENTE el mismo stream
informativo -- acciones forzadas, que aquí son instrumento del experimento y no
conducta del organismo. Después se congela el aprendizaje en TODOS y se corre un
probe autónomo con recursos no adyacentes. Si el brazo que pudo adaptar se
comporta mejor en el probe CONGELADO, lo adquirido persistió y se usó; si la
diferencia sólo existía durante la adquisición, no hubo capacidad.

E2-B · ADQUISICIÓN AUTÓNOMA. Sin acciones forzadas: el organismo tiene que
conseguirse él mismo las experiencias de las que aprende. Una familia de
disponibilidad de recurso, porque el piloto mostró que la relación no es
monótona -- con el recurso demasiado cerca el paseo aleatorio compite, porque
el encuentro domina sobre la política.

Tres brazos y un control mecanístico:

    N  NORMAL                  adapta
    P  PARAMETRIC_FREEZE       `learning_commit_enabled=False`: sólo theta
    F  FULL_ADAPTIVE_FREEZE    la frontera entera, certificada en OCF-G3
    A0 aleatorio               suelo de encuentro, no de política

**El planner va ENCENDIDO en todos los brazos de A4.** Medido: con
`use_planner=False` A4 no emite un solo CONSUME en 201 pasos y se muere, así que
ese brazo no es «A4 sin una pieza», es otro organismo. Aparece sólo como control
mecanístico declarado.

Disciplina de afirmación: no se declara capacidad por más comidas, ni por menos
pérdida, ni por sobrevivir. Hace falta la cadena entera --
experiencia → cambio adaptativo → persistencia → efecto conductual posterior --
y que FULL la destruya.

    python scripts/exp_adaptive_foraging_01.py --parte A
    python scripts/exp_adaptive_foraging_01.py --parte B --semillas 8
"""

from __future__ import annotations

import argparse
import statistics
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Sequence

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch  # noqa: E402
import torch.nn.functional as F_  # noqa: E402

from terrario.agent.adaptive_freeze import (  # noqa: E402
    ADAPTIVE_FINGERPRINT_VERSION, adaptive_components, adaptive_fingerprint, regime_of,
)
from terrario.agent.agents import create_agent  # noqa: E402
from terrario.core.rng import RNGManager  # noqa: E402
from terrario.core.types import ActionType, Direction, NUM_DIRECTIONS, TOTAL_ACTIONS  # noqa: E402
from terrario.world.transition import build_episode_components, run_step  # noqa: E402

# --- Contrato de configuración ----------------------------------------------
#
# `view_size` del agente y `view_radius` del mundo NO se negocian: el encoder
# fija `64*ceil(view_size/2)^2` al construirse y un mundo de radio 3 contra un
# agente de 5 revienta con un error de formas. Aquí se declaran juntos y se
# comprueban antes de cada mundo.

VIEW_RADIUS = 2
VIEW_SIZE = 2 * VIEW_RADIUS + 1

BASE: dict[str, Any] = {
    "use_planner": True, "use_world_model": True, "use_uncertainty": True,
    "use_episodic_memory": True, "use_longterm_memory": True, "use_temporal": True,
    "use_online_learning": True, "view_size": VIEW_SIZE,
    "latent_dim": 16, "hidden_dim": 24, "memory_dim": 8, "memory_slots": 4,
    "memory_capacity": 16, "ensemble_size": 2,
    "planner_horizon": 5, "planner_candidates": 10,
}

ARMS: dict[str, dict[str, Any]] = {
    "NORMAL": {},
    "PARAMETRIC": {"learning_commit_enabled": False},
    "FULL": {"full_adaptive_freeze": True},
}

MAX_ENERGY = 60.0
INITIAL_ENERGY = 30.0
STEP_COST = 0.15
FOOD_GAIN = 10.0
GRID = 7
CENTRE = GRID // 2


def _check_view_contract(scenario: dict[str, Any]) -> None:
    if int(scenario["view_radius"]) != VIEW_RADIUS:
        raise ValueError(
            f"contrato de percepción roto: el mundo declara radio {scenario['view_radius']} "
            f"y el agente se construye con view_size {VIEW_SIZE}. No se negocian.")


# --- Mundos, por configuración ----------------------------------------------

def _world(food_positions: Sequence[Sequence[int]], *, seed: int,
           duration: int) -> dict[str, Any]:
    scenario = {
        "name": f"foraging_{len(food_positions)}_{seed}",
        "grid_size": [GRID, GRID], "duration": duration, "seed": seed,
        "view_radius": VIEW_RADIUS, "num_channels": 4,
        "max_energy": MAX_ENERGY, "step_energy_cost": STEP_COST,
        "expose_time_fraction": True,
        "objects": [{"pos": list(p), "channels": [0.9, 0.9, 0.9, 0.9],
                     "movable": False, "energy_value": 0.0} for p in food_positions],
        "agent_start": {"pos": [CENTRE, CENTRE], "energy": INITIAL_ENERGY},
        "rules": {"rules": [{"id": "comer",
                             "condition": {"object_channel": {"index": 3, "min": 0.8},
                                           "action": "CONSUME"},
                             "effect": {"energy_delta": FOOD_GAIN}}]},
        "changes": [],
    }
    _check_view_contract(scenario)
    return scenario


def rich_world(seed: int, duration: int = 400) -> dict[str, Any]:
    """Adquisición: comida en las cuatro celdas adyacentes. El encuentro está
    garantizado, así que lo que se mide es aprender, no tropezarse."""
    return _world([[CENTRE - 1, CENTRE], [CENTRE + 1, CENTRE],
                   [CENTRE, CENTRE - 1], [CENTRE, CENTRE + 1]],
                  seed=seed, duration=duration)


def ring_world(distance: int, seed: int, duration: int = 400) -> dict[str, Any]:
    """Probe y campaña: comida en un anillo, nunca adyacente al arranque."""
    return _world([[CENTRE - distance, CENTRE], [CENTRE + distance, CENTRE],
                   [CENTRE, CENTRE - distance], [CENTRE, CENTRE + distance]],
                  seed=seed, duration=duration)


# --- Sondas de estado interno -----------------------------------------------

def consume_advantage(agent: Any, state: torch.Tensor) -> float:
    """`E[energía prevista | CONSUME] − E[energía prevista | MOVE]`.

    Lo que el organismo tiene que aprender para forrajear es que CONSUME paga y
    MOVE cuesta. Esto lo lee directamente del world model, sin pasar por la
    conducta, así que separa «aprendió» de «lo usó»."""
    if state is None:
        return float("nan")
    with torch.no_grad():
        preds: dict[str, list[float]] = {"CONSUME": [], "MOVE": []}
        for action_int in range(TOTAL_ACTIONS):
            kind = ActionType(action_int // NUM_DIRECTIONS).name
            if kind not in preds:
                continue
            onehot = torch.zeros(TOTAL_ACTIONS, device=state.device, dtype=state.dtype)
            onehot[action_int] = 1.0
            _, energy_pred, _ = agent.world_model(state, onehot)
            preds[kind].append(float(energy_pred.item()))
    return statistics.fmean(preds["CONSUME"]) - statistics.fmean(preds["MOVE"])


def planner_score_spread(agent: Any, state: torch.Tensor, *, repeats: int = 12) -> float:
    """Dispersión de los scores entre candidatos. Con el world model sin
    entrenar los rollouts son indistinguibles y el planner elige al azar."""
    if state is None:
        return float("nan")
    spreads = []
    for _ in range(repeats):
        _, trace = agent.planner.plan(state, agent.world_model,
                                      horizon=BASE["planner_horizon"],
                                      num_candidates=BASE["planner_candidates"])
        scores = [r["score"] for r in trace.get("rollouts", [])]
        if len(scores) > 1:
            spreads.append(statistics.pstdev(scores))
    return statistics.fmean(spreads) if spreads else float("nan")


def _state_of(agent: Any, scenario: dict[str, Any]) -> torch.Tensor | None:
    """Un estado de referencia fijo, el mismo para todos los brazos."""
    comps = build_episode_components(scenario, duration_fallback=10, strict_physics=True,
                                     with_lifecycle=False, world_seed=0)
    agent.perceive(comps.world.get_observation(0, VIEW_RADIUS, 4))
    agent.decide()
    return agent._last_state


# --- Correr una vida ---------------------------------------------------------

@dataclass
class Life:
    steps: int
    effective_consumes: int
    first_consume: int | None
    survived: bool
    final_energy: float
    energy_auc: float

    @property
    def time_to_first(self) -> float:
        return float(self.first_consume) if self.first_consume is not None else float("inf")


def live(agent: Any, scenario: dict[str, Any], *, seed: int, learning: bool) -> Life:
    comps = build_episode_components(scenario, duration_fallback=scenario["duration"],
                                     strict_physics=True, with_lifecycle=False,
                                     world_seed=seed)
    duration = int(scenario["duration"])
    consumes = first = None, None
    consumes, first = 0, None
    energies: list[float] = []
    steps = 0
    survived = True
    for step in range(duration):
        out = run_step(comps, agent, step, world_seed=seed, agent_seed=seed,
                       max_steps=duration, learning_enabled=learning)
        steps = step + 1
        if out.target is not None and out.effects:
            consumes += 1
            if first is None:
                first = step
        energies.append(float(out.observation_t.agent_energy) * MAX_ENERGY)
        if out.terminated:
            survived = False
            break
        if out.truncated:
            break
    return Life(steps, consumes, first, survived,
                energies[-1] if energies else INITIAL_ENERGY,
                sum(energies) / duration if energies else 0.0)


# --- E2-A · aprendibilidad ---------------------------------------------------

def force_action(agent: Any, action_int: int) -> None:
    """Que la actualización use la acción que el stream contenía, evaluada bajo
    la política de ESTE gemelo. Sin esto los tres brazos vivirían experiencias
    distintas y la comparación volvería a ser de trayectorias."""
    state = getattr(agent, "_last_state", None)
    if state is None:
        return
    agent._last_action = action_int
    logits = agent.policy_head(state)
    agent._last_log_prob = torch.log(F_.softmax(logits, dim=-1)[action_int] + 1e-8)


def record_stream(seed: int, steps: int) -> tuple[list[dict[str, Any]], int]:
    """Un stream informativo real: A4 con planner en el mundo rico."""
    scenario = rich_world(seed, duration=steps)
    comps = build_episode_components(scenario, duration_fallback=steps, strict_physics=True,
                                     with_lifecycle=False, world_seed=seed)
    RNGManager.set_global_determinism(seed)
    agent = create_agent("A4_ADVANCED", dict(BASE), seed=seed)
    stream, informative = [], 0
    for step in range(steps):
        out = run_step(comps, agent, step, world_seed=seed, agent_seed=seed,
                       max_steps=steps, learning_enabled=True)
        stream.append({"observation": out.observation_t, "action_int": out.action.to_int(),
                       "transition": out.transition})
        if out.target is not None and out.effects and out.energy_delta > 0:
            informative += 1
        if out.terminated or out.truncated:
            break
    return stream, informative


def acquire(arm: str, stream: list[dict[str, Any]], seed: int) -> dict[str, Any]:
    """Un gemelo recibe el stream entero. Mismo stream para los tres brazos."""
    RNGManager.set_global_determinism(seed)
    agent = create_agent("A4_ADVANCED", dict(BASE) | ARMS[arm], seed=seed)
    probe_scenario = rich_world(seed, duration=10)

    ref_state = _state_of(agent, probe_scenario)
    before = {
        "fingerprint": adaptive_fingerprint(agent),
        "components": adaptive_components(agent),
        "consume_advantage": consume_advantage(agent, ref_state),
        "planner_spread": planner_score_spread(agent, ref_state),
    }
    for i, record in enumerate(stream):
        agent.adaptive_freeze.set_step(i)
        agent.perceive(record["observation"])
        agent.decide()
        force_action(agent, record["action_int"])
        agent.learn(record["transition"])

    ref_state = _state_of(agent, probe_scenario)
    after = {
        "fingerprint": adaptive_fingerprint(agent),
        "components": adaptive_components(agent),
        "consume_advantage": consume_advantage(agent, ref_state),
        "planner_spread": planner_score_spread(agent, ref_state),
    }
    moved = sorted(k for k, v in before["components"].items() if after["components"][k] != v)
    return {"arm": arm, "agent": agent, "before": before, "after": after,
            "moved": moved, "regime": regime_of(agent).value}


def part_a(seed: int, acquisition_steps: int, probe_distance: int) -> int:
    print(f"E2-A · APRENDIBILIDAD  ·  semilla {seed}  ·  huella "
          f"{ADAPTIVE_FINGERPRINT_VERSION}\n")

    stream, informative = record_stream(seed, acquisition_steps)
    print(f"  stream de adquisición: {len(stream)} pasos, "
          f"{informative} experiencias informativas (CONSUME con energía > 0)")
    if informative == 0:
        print("\n  PARADA: el stream no contiene ningún evento informativo. "
              "NORMAL no tendría de qué aprender.")
        return 2
    print()

    runs = {arm: acquire(arm, stream, seed) for arm in ARMS}

    print("  ADQUISICIÓN  ·  mismo stream, tres brazos\n")
    print(f"  {'brazo':<12}{'componentes que cambian':<34}"
          f"{'ventaja CONSUME−MOVE':>24}{'dispersión planner':>20}")
    print("  " + "-" * 92)
    for arm, r in runs.items():
        adv = f"{r['before']['consume_advantage']:+.4f} → {r['after']['consume_advantage']:+.4f}"
        spr = f"{r['before']['planner_spread']:.4f} → {r['after']['planner_spread']:.4f}"
        moved = ", ".join(r["moved"]) if r["moved"] else "ninguno"
        print(f"  {arm:<12}{moved:<34}{adv:>24}{spr:>20}")

    if runs["FULL"]["moved"]:
        print(f"\n  PARADA: bajo FULL cambió {runs['FULL']['moved']}. "
              "El control causal no se sostiene.")
        return 2

    print("\n\n  PROBE CONGELADO  ·  learning_enabled=False para TODOS  ·  "
          f"comida a distancia {probe_distance}\n")
    print(f"  {'brazo':<12}{'pasos':>7}{'consumos':>10}{'1er consumo':>13}"
          f"{'sobrevive':>11}{'E final':>9}{'E media':>9}{'huella intacta':>16}")
    print("  " + "-" * 87)

    probe = ring_world(probe_distance, seed)
    results: dict[str, Life] = {}
    for arm, r in runs.items():
        agent = r["agent"]
        fp_before = adaptive_fingerprint(agent)
        life = live(agent, probe, seed=seed, learning=False)
        intact = adaptive_fingerprint(agent) == fp_before
        results[arm] = life
        print(f"  {arm:<12}{life.steps:>7}{life.effective_consumes:>10}"
              f"{(life.first_consume if life.first_consume is not None else '—'):>13}"
              f"{('sí' if life.survived else 'NO'):>11}{life.final_energy:>9.2f}"
              f"{life.energy_auc:>9.2f}{('sí' if intact else 'NO'):>16}")

    RNGManager.set_global_determinism(seed)
    a0 = create_agent("A0_RANDOM", {}, seed=seed)
    life0 = live(a0, ring_world(probe_distance, seed), seed=seed, learning=False)
    print(f"  {'A0 aleatorio':<12}{life0.steps:>7}{life0.effective_consumes:>10}"
          f"{(life0.first_consume if life0.first_consume is not None else '—'):>13}"
          f"{('sí' if life0.survived else 'NO'):>11}{life0.final_energy:>9.2f}"
          f"{life0.energy_auc:>9.2f}{'—':>16}")

    d_nf = results["NORMAL"].effective_consumes - results["FULL"].effective_consumes
    d_pf = results["PARAMETRIC"].effective_consumes - results["FULL"].effective_consumes
    print(f"\n  Δ(NORMAL − FULL) = {d_nf:+d} consumos en el probe congelado")
    print(f"  Δ(PARAMETRIC − FULL) = {d_pf:+d}   (adaptación NO paramétrica)")
    print("\n  n = 1 semilla. Esto muestra que el contraste es construible; "
          "no es evidencia.")
    return 0


# --- E2-B · adquisición autónoma --------------------------------------------

def part_b(seeds: Sequence[int], distances: Sequence[int]) -> int:
    print(f"E2-B · ADQUISICIÓN AUTÓNOMA  ·  {len(seeds)} semillas pareadas  ·  "
          "sin acciones forzadas\n")
    print("  La disponibilidad de experiencia es el eje. El piloto mostró que la "
          "relación\n  no es monótona: con el recurso muy cerca el encuentro domina "
          "sobre la política.\n")

    for distance in distances:
        rows: dict[str, list[Life]] = {name: [] for name in list(ARMS) + ["A0"]}
        for seed in seeds:
            scenario = ring_world(distance, seed)
            for arm in ARMS:
                RNGManager.set_global_determinism(seed)
                agent = create_agent("A4_ADVANCED", dict(BASE) | ARMS[arm], seed=seed)
                rows[arm].append(live(agent, scenario, seed=seed, learning=True))
            RNGManager.set_global_determinism(seed)
            rows["A0"].append(live(create_agent("A0_RANDOM", {}, seed=seed),
                                   scenario, seed=seed, learning=True))

        print(f"  ── comida a distancia {distance} ──\n")
        print(f"  {'brazo':<12}{'consumos (media)':>18}{'1er consumo':>14}"
              f"{'sobreviven':>13}{'E final':>10}{'E media':>10}")
        print("  " + "-" * 79)
        for arm, lives in rows.items():
            cons = statistics.fmean(l.effective_consumes for l in lives)
            firsts = [l.first_consume for l in lives if l.first_consume is not None]
            first = f"{statistics.fmean(firsts):.0f}" if firsts else "—"
            surv = sum(l.survived for l in lives)
            print(f"  {arm:<12}{cons:>18.2f}{first:>14}"
                  f"{f'{surv}/{len(lives)}':>13}"
                  f"{statistics.fmean(l.final_energy for l in lives):>10.2f}"
                  f"{statistics.fmean(l.energy_auc for l in lives):>10.2f}")

        paired = [rows["NORMAL"][i].effective_consumes - rows["FULL"][i].effective_consumes
                  for i in range(len(seeds))]
        wins = sum(1 for d in paired if d > 0)
        print(f"\n  Δ(NORMAL − FULL) pareado por semilla: {paired}")
        print(f"  media {statistics.fmean(paired):+.2f} · "
              f"NORMAL gana en {wins}/{len(seeds)} semillas\n")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--parte", choices=["A", "B"], default="A")
    parser.add_argument("--semilla", type=int, default=7)
    parser.add_argument("--semillas", type=int, default=6)
    parser.add_argument("--pasos", type=int, default=300)
    parser.add_argument("--distancia", type=int, default=3)
    args = parser.parse_args()
    if args.parte == "A":
        return part_a(args.semilla, args.pasos, args.distancia)
    return part_b(list(range(args.semillas)), (2, 3))


if __name__ == "__main__":
    raise SystemExit(main())
