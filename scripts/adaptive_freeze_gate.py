#!/usr/bin/env python
"""OCF-G3 · Falsar FULL_ADAPTIVE_FREEZE sobre la frontera adaptativa adoptada.

    A = { θ, EpisodicBuffer, M, energy_baseline }

Un brazo congelado que termina idéntico no demuestra nada si el organismo
tampoco habría aprendido sin congelarlo. Por eso esto no comprueba un hash:
corre TRES gemelos sobre EXACTAMENTE la misma experiencia y exige el contraste.

    N  NORMAL                  parámetros mutan, memorias mutan
    P  PARAMETRIC (heredado)   `learning_commit_enabled=False`
    F  FULL_ADAPTIVE_FREEZE    los cuatro writers bloqueados

La experiencia es un stream grabado, no una vida autónoma: si cada gemelo actúa
por su cuenta las políticas divergen, la experiencia diverge con ellas y deja de
saberse qué se está comparando. El gradiente de política se toma sobre la acción
GRABADA evaluada bajo la política de ESE gemelo -- el patrón de
`scripts/experiment_capability_acquisition.py`.

Sólo lectura sobre el repositorio y sobre la base viva.

    python scripts/adaptive_freeze_gate.py
    python scripts/adaptive_freeze_gate.py --pasos 120 --semilla 3
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch  # noqa: E402
import torch.nn.functional as F_  # noqa: E402

from terrario.agent.adaptive_freeze import COMPONENTS  # noqa: E402
from terrario.agent.agents import create_agent  # noqa: E402
from terrario.core.rng import RNGManager  # noqa: E402
from terrario.core.types import Action  # noqa: E402
from terrario.lab import world_generator as gen  # noqa: E402
from terrario.world.transition import build_episode_components, run_step  # noqa: E402

NUM_DIRECTIONS = 5

BASE: dict[str, Any] = {
    "use_planner": False, "use_uncertainty": True, "use_episodic_memory": True,
    "use_longterm_memory": True, "use_temporal": True, "use_online_learning": True,
    "latent_dim": 16, "hidden_dim": 24, "memory_dim": 8, "memory_slots": 4,
    "memory_capacity": 16, "ensemble_size": 2,
}

ARMS = {
    "N": {},
    "P": {"learning_commit_enabled": False},
    "F": {"full_adaptive_freeze": True},
}
ARM_LABEL = {"N": "NORMAL", "P": "congelación heredada", "F": "FULL_ADAPTIVE_FREEZE"}

PIECES = ("parameters", "episodic_buffer", "longterm_M", "energy_baseline")


# --- Huellas, pieza por pieza ------------------------------------------------
#
# Nivel 1 de la prueba: identidad estructural por componente. El hash agregado
# es sólo el checksum final; si mañana `_adaptive_state_hash` dejara de
# serializar `M`, comparar sólo el agregado dejaría el gate ciego.

def digest(agent: Any, component: str) -> str:
    if component == "parameters":
        # `longterm_memory.M` ES un `nn.Parameter` y está dentro de
        # `get_parameters()`, pero NO lo gobierna el optimizador: se escribe en
        # `memory.py` con `M.data.copy_()`. Incluirlo aquí solapa dos piezas de
        # la frontera y hace que el brazo heredado parezca mover parámetros
        # cuando lo que movió fue la memoria. `scripts/learned_state_audit.py`
        # ya lo excluía por la misma razón.
        h = hashlib.sha256()
        for name, value in sorted(agent.get_parameters().items()):
            if name == "longterm_memory.M":
                continue
            h.update(name.encode())
            h.update(value.detach().cpu().contiguous().numpy().tobytes())
        return h.hexdigest()[:16]
    if component == "longterm_M":
        m = getattr(getattr(agent, "longterm_memory", None), "M", None)
        return ("—" if m is None else
                hashlib.sha256(m.detach().cpu().contiguous().numpy().tobytes()).hexdigest()[:16])
    if component == "episodic_buffer":
        buf = getattr(getattr(agent, "episodic_memory", None), "_buffer", None)
        if buf is None:
            return "—"
        h = hashlib.sha256()
        for item in buf:
            h.update(item["embedding"].detach().cpu().contiguous().numpy().tobytes())
            h.update(str((item["action"], item["energy_delta"], item["timestamp"])).encode())
        return h.hexdigest()[:16]
    if component == "energy_baseline":
        return (f"{float(getattr(agent, '_energy_baseline', 0.0)):.12g}"
                f"/{int(getattr(agent, '_baseline_count', 0))}")
    raise KeyError(component)


def adaptive_hash(agent: Any) -> str:
    """Nivel 2: el agregado, construido de las mismas piezas."""
    h = hashlib.sha256()
    for piece in PIECES:
        h.update(piece.encode())
        h.update(digest(agent, piece).encode())
    return h.hexdigest()[:16]


def snapshot(agent: Any) -> dict[str, str]:
    return {p: digest(agent, p) for p in PIECES} | {"adaptive_hash": adaptive_hash(agent)}


# --- El stream grabado -------------------------------------------------------

def record(*, seed: int, steps: int) -> tuple[list[dict[str, Any]], Any]:
    """Una vida del organismo real, guardada paso a paso."""
    world = gen.world_for(["LEARN-A1"], seed=seed, stations=8)
    components = build_episode_components(
        world.scenario, duration_fallback=world.duration, strict_physics=True,
        with_lifecycle=False, world_seed=world.seed)
    RNGManager.set_global_determinism(seed)
    agent = create_agent("A4_ADVANCED", dict(BASE), seed=seed)

    stream: list[dict[str, Any]] = []
    limit = min(steps, world.duration)
    for step in range(limit):
        out = run_step(components, agent, step, world_seed=world.seed, agent_seed=seed,
                       max_steps=limit, learning_enabled=True)
        stream.append({
            "observation": out.observation_t,
            "action_int": out.action.to_int(),
            "transition": out.transition if hasattr(out, "transition") else None,
            "energy_delta": float(out.energy_delta),
            "outcome": out,
        })
        if out.terminated or out.truncated:
            break
    return stream, world


def force_action(agent: Any, action_int: int) -> None:
    """Que la actualización del gemelo use la acción que el stream contenía.

    Reproducir un stream sólo es fiel si el gradiente de política se toma sobre
    la acción GRABADA, evaluada bajo la política de ESTE gemelo -- no sobre la
    que este gemelo habría elegido.
    """
    state = getattr(agent, "_last_state", None)
    if state is None:
        return
    agent._last_action = action_int
    if getattr(agent, "_use_factored_action", False):
        operation = action_int // NUM_DIRECTIONS
        selector = action_int % NUM_DIRECTIONS
        op_logits = agent.operation_head(state)
        op_log = torch.log(F_.softmax(op_logits, dim=-1)[operation] + 1e-8)
        head = getattr(agent, "direction_head", None) or agent.selector_head
        sel_logits = head(state)
        index = min(selector, sel_logits.numel() - 1)
        sel_log = torch.log(F_.softmax(sel_logits, dim=-1)[index] + 1e-8)
        agent._last_log_prob = op_log + sel_log
    else:
        logits = agent.policy_head(state)
        agent._last_log_prob = torch.log(F_.softmax(logits, dim=-1)[action_int] + 1e-8)


def replay(arm: str, stream: list[dict[str, Any]], *, seed: int,
           witness: bool = False) -> dict[str, Any]:
    """Un gemelo, el stream entero, el mismo para los tres."""
    RNGManager.set_global_determinism(seed)
    agent = create_agent("A4_ADVANCED", dict(BASE) | ARMS[arm], seed=seed)
    if witness:
        agent.adaptive_freeze.set_witness(lambda c: digest(agent, c))

    before = snapshot(agent)
    per_step: list[str] = [before["adaptive_hash"]]
    for i, rec in enumerate(stream):
        agent.adaptive_freeze.set_step(i)
        agent.perceive(rec["observation"])
        agent.decide()
        force_action(agent, rec["action_int"])
        agent.learn(rec["outcome"].transition)
        agent.adaptive_freeze.settle()
        per_step.append(adaptive_hash(agent))
    after = snapshot(agent)
    return {
        "arm": arm, "before": before, "after": after,
        "summary": agent.adaptive_freeze.summary(),
        "escaped": agent.adaptive_freeze.mutated_under_block(),
        "per_step": per_step,
        "baseline_opportunities": int(getattr(agent, "_baseline_count", 0)),
    }


# --- Ruta real de A4 (OCF-G3.I/J) y pasividad (OCF-G3.H) ----------------------

def live(arm: str, *, seed: int, steps: int, witness: bool) -> dict[str, Any]:
    """El mismo contrato atravesando `run_step`, no el replay.

    El stream controlado certifica el mecanismo sin que la divergencia de
    política contamine la experiencia. Pero un contrato que sólo funciona en el
    arnés no es un contrato: esto lo ejerce por la ruta que el experimento usa
    de verdad.
    """
    world = gen.world_for(["LEARN-A1"], seed=seed, stations=8)
    comps = build_episode_components(
        world.scenario, duration_fallback=world.duration, strict_physics=True,
        with_lifecycle=False, world_seed=world.seed)
    RNGManager.set_global_determinism(seed)
    agent = create_agent("A4_ADVANCED", dict(BASE) | ARMS[arm], seed=seed)
    if witness:
        agent.adaptive_freeze.set_witness(lambda c: digest(agent, c))

    before = snapshot(agent)
    actions: list[int] = []
    deltas: list[float] = []
    limit = min(steps, world.duration)
    for step in range(limit):
        agent.adaptive_freeze.set_step(step)
        out = run_step(comps, agent, step, world_seed=world.seed, agent_seed=seed,
                       max_steps=limit, learning_enabled=True)
        agent.adaptive_freeze.settle()
        actions.append(out.action.to_int())
        deltas.append(round(float(out.energy_delta), 9))
        if out.terminated or out.truncated:
            break
    return {"before": before, "after": snapshot(agent), "actions": actions,
            "deltas": deltas, "summary": agent.adaptive_freeze.summary(),
            "escaped": agent.adaptive_freeze.mutated_under_block()}


# --- Informe -----------------------------------------------------------------

def report(seed: int, steps: int) -> int:
    stream, world = record(seed=seed, steps=steps)
    print(f"OCF-G3 · FULL_ADAPTIVE_FREEZE — {len(stream)} pasos de stream grabado, "
          f"mundo LEARN-A1 semilla {seed}\n")

    runs = {a: replay(a, stream, seed=seed, witness=(a == "F")) for a in ("N", "P", "F")}

    print("MATRIZ  ·  ¿cambió cada pieza entre el inicio y el final?\n")
    print(f"  {'pieza':<22}" + "".join(f"{ARM_LABEL[a]:>24}" for a in ("N", "P", "F")))
    print("  " + "-" * (22 + 24 * 3))
    changed: dict[str, dict[str, bool]] = {}
    for piece in PIECES + ("adaptive_hash",):
        row = {}
        cells = []
        for a in ("N", "P", "F"):
            r = runs[a]
            moved = r["before"][piece] != r["after"][piece]
            row[a] = moved
            cells.append("cambia" if moved else "no cambia")
        changed[piece] = row
        print(f"  {piece:<22}" + "".join(f"{c:>24}" for c in cells))

    print("\n\nINTENTOS DE ESCRITURA BAJO FULL FREEZE  (OCF-G3.4)\n")
    print(f"  {'componente':<20}{'intentados':>12}{'concedidos':>12}{'bloqueados':>12}   writer")
    print("  " + "-" * 92)
    for c in PIECES:
        s = runs["F"]["summary"][c]
        print(f"  {c:<20}{s['attempted']:>12}{s['committed']:>12}{s['blocked']:>12}   {COMPONENTS[c]}")

    # --- Los ocho criterios --------------------------------------------------
    n, p, f = runs["N"], runs["P"], runs["F"]
    sumF = f["summary"]

    boundary_ok = set(sumF) == set(COMPONENTS)
    positive = all(changed[c]["N"] for c in PIECES)
    frozen = not any(changed[c]["F"] for c in PIECES) and not changed["adaptive_hash"]["F"]
    block_evidence = all(sumF[c]["blocked"] > 0 for c in PIECES)
    no_masquerade = (not f["escaped"]) and len(set(f["per_step"])) == 1
    legacy_ok = (not changed["parameters"]["P"]) and (
        changed["episodic_buffer"]["P"] or changed["longterm_M"]["P"])
    f2 = replay("F", stream, seed=seed)
    deterministic = (f2["after"] == f["after"] == f["before"])

    # Pasividad: el testigo de F no puede cambiar su resultado.
    passive = f2["after"] == f["after"]

    print("\n\nOPORTUNIDADES DE LÍNEA BASE  (no pasos: `_energy_baseline` es event-driven)\n")
    print(f"  NORMAL     oportunidades elegibles = {n['baseline_opportunities']}  "
          f"de {len(stream)} pasos")
    print(f"  FULL       oportunidades elegibles = {f['baseline_opportunities']}  "
          f"(intentos registrados = {sumF['energy_baseline']['attempted']})")

    # --- Ruta real y pasividad ----------------------------------------------
    live_n = live("N", seed=seed, steps=steps, witness=False)
    live_f_on = live("F", seed=seed, steps=steps, witness=True)
    live_f_off = live("F", seed=seed, steps=steps, witness=False)

    runtime_frozen = all(live_f_on["before"][c] == live_f_on["after"][c]
                         for c in PIECES) and (
        live_f_on["before"]["adaptive_hash"] == live_f_on["after"]["adaptive_hash"])
    runtime_positive = any(live_n["before"][c] != live_n["after"][c] for c in PIECES)
    runtime_attempts = all(live_f_on["summary"][c]["blocked"] > 0 for c in PIECES)

    audit_passive = (
        live_f_on["actions"] == live_f_off["actions"]
        and live_f_on["deltas"] == live_f_off["deltas"]
        and live_f_on["after"] == live_f_off["after"])

    print("\n\nRUTA REAL DE A4  (run_step, no replay)  ·  OCF-G3.I/J\n")
    print(f"  NORMAL     {len(live_n['actions'])} pasos · "
          f"piezas que cambian: "
          f"{sum(live_n['before'][c] != live_n['after'][c] for c in PIECES)}/4")
    print(f"  FULL       {len(live_f_on['actions'])} pasos · "
          f"piezas que cambian: "
          f"{sum(live_f_on['before'][c] != live_f_on['after'][c] for c in PIECES)}/4 · "
          f"intentos bloqueados: "
          f"{sum(live_f_on['summary'][c]['blocked'] for c in PIECES)}")

    print("\n\nPASIVIDAD DE LA AUDITORÍA  (mismo brazo F, testigo ON vs OFF)  ·  OCF-G3.H\n")
    for label, same in (("acciones", live_f_on["actions"] == live_f_off["actions"]),
                        ("energía por paso", live_f_on["deltas"] == live_f_off["deltas"]),
                        ("estado adaptativo", live_f_on["after"] == live_f_off["after"])):
        print(f"  {label:<24}{'iguales' if same else 'DIFIEREN'}")

    print("\n\nCRITERIOS\n")
    crit = [
        ("OCF-G3.1  fidelidad de frontera   (exactamente las cuatro piezas)", boundary_ok),
        ("OCF-G3.2  control positivo        (N mueve las cuatro)", positive),
        ("OCF-G3.3  congelación completa    (F no mueve ninguna, ni el hash)", frozen),
        ("OCF-G3.4  evidencia de bloqueo    (cada writer intentó y fue bloqueado)", block_evidence),
        ("OCF-G3.5  sin reversión disfrazada(ninguna pieza mutó y volvió)", no_masquerade),
        ("OCF-G3.6  discriminación heredada (P congela θ y NO las memorias)", legacy_ok),
        ("OCF-G3.7  determinismo            (dos F dan lo mismo y lo inicial)", deterministic),
        ("OCF-G3.8  pasividad del testigo   (replay: instrumentar no altera nada)", passive),
        ("OCF-G3.H  pasividad de auditoría  (ruta real: ON y OFF dan lo mismo)", audit_passive),
        ("OCF-G3.I  integración en runtime  (F congela atravesando run_step)", runtime_frozen),
        ("OCF-G3.J  control positivo real   (N muta atravesando run_step)", runtime_positive),
        ("OCF-G3.K  evidencia en runtime    (writers alcanzados y bloqueados)", runtime_attempts),
    ]
    for label, ok in crit:
        print(f"  [{'✓' if ok else '✗'}]  {label}")

    if f["escaped"]:
        print("\n  ESCAPES (condición de parada 6):")
        for a in f["escaped"][:6]:
            print(f"    · {a.component} en el paso {a.step}: "
                  f"{a.before_digest} → {a.after_digest}")

    # --- Condición de parada 10 ---------------------------------------------
    #
    # El criterio E exige que `_adaptive_state_hash` -- la huella agregada que
    # el experimento real usa -- permanezca idéntica. Pero eso sólo demuestra lo
    # que la huella incluye. Si omite una pieza de la frontera adoptada, el
    # criterio se satisface en vacío, que es exactamente el modo de fallo contra
    # el que se pidió comparar pieza por pieza Y agregado.
    from terrario.experiment.adaptation import _adaptive_state_hash

    RNGManager.set_global_determinism(seed)
    canary = create_agent("A4_ADVANCED", dict(BASE), seed=seed)
    covers: dict[str, bool] = {}
    h0 = _adaptive_state_hash(canary)
    canary._energy_baseline = float(canary._energy_baseline) + 42.0
    canary._baseline_count = int(canary._baseline_count) + 17
    covers["energy_baseline"] = _adaptive_state_hash(canary) != h0

    RNGManager.set_global_determinism(seed)
    canary = create_agent("A4_ADVANCED", dict(BASE), seed=seed)
    h0 = _adaptive_state_hash(canary)
    canary.longterm_memory.M.data.add_(1.0)
    covers["longterm_M"] = _adaptive_state_hash(canary) != h0

    RNGManager.set_global_determinism(seed)
    canary = create_agent("A4_ADVANCED", dict(BASE), seed=seed)
    h0 = _adaptive_state_hash(canary)
    canary.episodic_memory.write(embedding=torch.zeros(BASE["latent_dim"]), action=1,
                                 energy_delta=0.5, prediction_error=0.1, timestamp=0)
    covers["episodic_buffer"] = _adaptive_state_hash(canary) != h0

    uncovered = [c for c, ok in covers.items() if not ok]

    print("\n\nCONDICIÓN DE PARADA 10  ·  ¿`_adaptive_state_hash` cubre la frontera adoptada?\n")
    for c in ("episodic_buffer", "longterm_M", "energy_baseline"):
        print(f"  {c:<22}{'la ve' if covers[c] else 'NO LA VE'}")
    print("  parameters            (no comprobable por separado: `get_parameters()` "
          "incluye M)")

    passed = all(ok for _, ok in crit)
    print(f"\n\n  LEARNING_COMMIT_IS_COMPLETE_FREEZE = "
          f"{'NO' if (changed['episodic_buffer']['P'] or changed['longterm_M']['P']) else 'SÍ'}"
          f"   (se conserva la distinción ya medida)")
    if uncovered:
        print(f"\n  OCF-G3 = ABIERTO POR CONDICIÓN DE PARADA 10")
        print(f"  Los {len(crit)} criterios pasan, pero `_adaptive_state_hash` omite "
              f"{', '.join(uncovered)},")
        print(f"  que la frontera adoptada SÍ incluye. El criterio E se satisface en "
              f"vacío para esa pieza.")
        print(f"  No se repara aquí: cambiar esa huella toca `adaptation.py`, que está "
              f"fuera de este alcance.")
        return 2
    print(f"  OCF-G3 = {'PASA' if passed else 'NO PASA'}")
    return 0 if passed else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--semilla", type=int, default=7)
    ap.add_argument("--pasos", type=int, default=80)
    a = ap.parse_args()
    return report(a.semilla, a.pasos)


if __name__ == "__main__":
    raise SystemExit(main())
