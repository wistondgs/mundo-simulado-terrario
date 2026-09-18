#!/usr/bin/env python
"""LEARNED-STATE-BOUNDARY-01 — qué de A4 es conocimiento adquirido y qué no.

La intervención aprobada en G4, `learning_commit_enabled`, suprime exactamente
`optimizer.step()`. La pregunta que nadie había contestado por escrito es si eso
congela TODO el estado que depende de la experiencia, o sólo la parte que pasa
por el optimizador. De la respuesta depende si el brazo suprimido es un control
de «cero aprendizaje» o un brazo que también aprende, por otra vía.

Esta sonda no decide nada: mide. Corre una historia de exposición producida por
la física canónica —mundo generado, `run_step`, observaciones reales— sobre dos
gemelos idénticos, uno con commit y otro sin, y reporta cuánto se mueve cada
pieza de estado bajo cada brazo.

Es de sólo lectura sobre el repositorio y sobre la base viva: no escribe
ficheros, no toca `.terrario`, no modifica agentes fuera de su propio proceso.

    python scripts/learned_state_audit.py
    python scripts/learned_state_audit.py --pasos 400 --semilla 11
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch  # noqa: E402

from terrario.agent.agents import create_agent  # noqa: E402
from terrario.core.rng import RNGManager  # noqa: E402
from terrario.lab import world_generator as gen  # noqa: E402
from terrario.world.transition import build_episode_components, run_step  # noqa: E402


# --- El inventario, leído del código -----------------------------------------
#
# `under_intervention` es la columna decisiva: es lo único que
# `learning_commit_enabled` puede detener. Todo lo demás se mueve en los dos
# brazos por construcción, no por defecto.

@dataclass(frozen=True)
class Entry:
    state: str
    writer: str
    phase: str
    experience_dependent: bool
    under_intervention: bool


INVENTORY: tuple[Entry, ...] = (
    Entry("nn.Parameter de todos los módulos registrados", "learner.py:159 optimizer.step()",
          "learn", True, True),
    Entry("momentos de Adam (exp_avg, exp_avg_sq, step)", "learner.py:159 optimizer.step()",
          "learn", True, True),
    Entry("longterm_memory.M", "memory.py:239 M.data.copy_(proposed)", "learn", True, False),
    Entry("episodic_memory._buffer / _write_idx", "memory.py:51-54 write()", "learn", True, False),
    Entry("_energy_baseline / _baseline_count", "a4_advanced.py:648-651", "learn", True, False),
    Entry("last_prediction_error / _last_prediction", "a4_advanced.py:597-605", "learn", True, False),
    Entry("homeostasis._energy", "a4_advanced.py:352 (perceive sobrescribe)", "perceive", False, False),
    Entry("_hidden (recurrente, detached)", "a4_advanced.py:403", "perceive", False, False),
    Entry("_last_state / _last_latent / _last_action", "a4_advanced.py:349,409-412", "decide", False, False),
    Entry("parameter.grad", "learner.py:117 backward()", "learn", True, False),
    Entry("_step / learner._step_count", "a4_advanced.py:747, learner.py:91", "learn", False, False),
    Entry("_trace (agente y submódulos)", "varios", "todas", False, False),
)


# --- Medición ----------------------------------------------------------------

def _config(*, commit: bool) -> dict[str, Any]:
    return {
        "use_planner": False, "use_uncertainty": True, "use_episodic_memory": True,
        "use_longterm_memory": True, "use_temporal": True, "use_online_learning": True,
        "latent_dim": 16, "hidden_dim": 24, "memory_dim": 8, "memory_slots": 4,
        "memory_capacity": 16, "ensemble_size": 2, "learning_commit_enabled": commit,
    }


def _agent(*, commit: bool, seed: int):
    RNGManager.set_global_determinism(seed)
    return create_agent("A4_ADVANCED", _config(commit=commit), seed=seed)


def _params(agent) -> dict[str, torch.Tensor]:
    """Sólo lo que el optimizador gobierna, sin `M`, que se escribe aparte."""
    out = {}
    for name, module in agent.learner._modules.items():
        for pname, parameter in module.named_parameters():
            if name == "longterm_memory" and pname == "M":
                continue
            out[f"{name}.{pname}"] = parameter.detach().clone()
    return out


def _drift(before: dict[str, torch.Tensor], agent) -> float:
    after = _params(agent)
    total = sum(float((after[k] - before[k]).norm() ** 2) for k in before)
    return total ** 0.5


def medir(*, commit: bool, seed: int, pasos: int) -> dict[str, Any]:
    world = gen.world_for(["LEARN-A1"], seed=seed, stations=8)
    components = build_episode_components(
        world.scenario, duration_fallback=world.duration, strict_physics=True,
        with_lifecycle=False, world_seed=world.seed)
    agent = _agent(commit=commit, seed=seed)

    m0 = agent.longterm_memory.M.detach().clone()
    p0 = _params(agent)
    base0 = float(agent._energy_baseline)

    limite = min(pasos, world.duration)
    aprendizajes = 0
    for step in range(limite):
        outcome = run_step(components, agent, step, world_seed=world.seed,
                           agent_seed=seed, max_steps=limite, learning_enabled=True)
        if agent.learner.step_count > aprendizajes:
            aprendizajes = agent.learner.step_count
        if outcome.terminated or outcome.truncated:
            break

    m = agent.longterm_memory.M.detach()
    return {
        "brazo": "FULL" if commit else "ABL",
        "pasos": step + 1,
        "pasos_de_aprendizaje": aprendizajes,
        "delta_M": float((m - m0).norm()),
        "norma_M_inicial": float(m0.norm()),
        "norma_M_final": float(m.norm()),
        # `M` se satura en ±10 (`memory.py:239` recorta ahí), así que la
        # saturación da la escala absoluta: un desplazamiento sólo es grande
        # respecto a lo que la pieza puede recorrer.
        "saturacion_M": float(m.abs().max()) / 10.0,
        "slots_M_movidos": int(((m - m0).abs().sum(dim=1) > 1e-9).sum()),
        "slots_M_total": int(m.shape[0]),
        "delta_parametros": _drift(p0, agent),
        "baseline_energia": (base0, float(agent._energy_baseline)),
        "buffer_episodico": len(agent.episodic_memory._buffer),
        "capacidad_buffer": agent.episodic_memory.capacity,
        "rotaciones_buffer": agent.learner.step_count // agent.episodic_memory.capacity,
    }


# --- Informe -----------------------------------------------------------------

def inventario() -> None:
    print("INVENTARIO DE ESTADO MUTABLE DE A4\n")
    print(f"  {'estado':<46}{'fase':<10}{'dep. exp.':<12}{'bajo intervención'}")
    print("  " + "-" * 92)
    for e in INVENTORY:
        print(f"  {e.state:<46}{e.phase:<10}"
              f"{('sí' if e.experience_dependent else 'no'):<12}"
              f"{'SÍ' if e.under_intervention else 'no'}")
    fuera = [e for e in INVENTORY if e.experience_dependent and not e.under_intervention]
    print(f"\n  Dependen de la experiencia y la intervención NO los controla: {len(fuera)}")
    for e in fuera:
        print(f"    · {e.state:<44} {e.writer}")


def informe(seed: int, pasos: int) -> int:
    inventario()
    print("\n\nMEDICIÓN — mundo generado que exige LEARN-A1, física canónica\n")
    brazos = [medir(commit=c, seed=seed, pasos=pasos) for c in (True, False)]
    campos = [
        ("pasos vividos", "pasos"),
        ("pasos de aprendizaje", "pasos_de_aprendizaje"),
        ("‖Δ parámetros‖ (bajo optimizador)", "delta_parametros"),
        ("‖Δ M‖ (fuera del optimizador)", "delta_M"),
        ("‖Δ M‖ / ‖M inicial‖", None),
        ("saturación de M (|M|max / 10)", "saturacion_M"),
        ("slots de M movidos", None),
        ("baseline de energía", None),
        ("buffer episódico", None),
    ]
    print(f"  {'':<38}{'FULL':>16}{'ABL':>16}")
    print("  " + "-" * 70)
    for etiqueta, clave in campos:
        if clave:
            vals = [f"{b[clave]:.6g}" if isinstance(b[clave], float) else str(b[clave]) for b in brazos]
        elif etiqueta.startswith("‖Δ M‖ /"):
            vals = [f"{b['delta_M'] / b['norma_M_inicial']:.1f}×" for b in brazos]
        elif etiqueta.startswith("slots"):
            vals = [f"{b['slots_M_movidos']}/{b['slots_M_total']}" for b in brazos]
        elif etiqueta.startswith("baseline"):
            vals = [f"{b['baseline_energia'][0]:.3f}→{b['baseline_energia'][1]:.3f}" for b in brazos]
        else:
            vals = [f"{b['buffer_episodico']}/{b['capacidad_buffer']} ×{b['rotaciones_buffer']}" for b in brazos]
        print(f"  {etiqueta:<38}{vals[0]:>16}{vals[1]:>16}")

    abl = brazos[1]
    congelado = abl["delta_parametros"] < 1e-9
    m_quieta = abl["delta_M"] < 1e-9
    print()
    print(f"  Bajo ABL, los parámetros del optimizador {'NO se mueven' if congelado else 'SE MUEVEN'}"
          f" (‖Δ‖ = {abl['delta_parametros']:.3g})")
    print(f"  Bajo ABL, M {'no se mueve' if m_quieta else 'SÍ SE MUEVE'}"
          f" (‖Δ‖ = {abl['delta_M']:.3g} = {abl['delta_M'] / abl['norma_M_inicial']:.1f}× su norma"
          f" inicial, {abl['slots_M_movidos']}/{abl['slots_M_total']} slots,"
          f" {abl['saturacion_M']:.0%} de saturación)")
    veredicto = "YES" if (congelado and m_quieta) else "NO"
    print(f"\n  LEARNING_COMMIT_IS_COMPLETE_FREEZE = {veredicto}")
    if veredicto == "NO":
        print("\n  El brazo suprimido conserva cambio dependiente de experiencia. El contraste")
        print("  FULL−ABL no mide «aprender frente a no aprender»: mide el commit del")
        print("  optimizador sobre un sustrato que se movió en los dos brazos.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--semilla", type=int, default=7)
    parser.add_argument("--pasos", type=int, default=300)
    args = parser.parse_args()
    return informe(args.semilla, args.pasos)


if __name__ == "__main__":
    raise SystemExit(main())
