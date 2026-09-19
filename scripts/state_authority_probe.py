#!/usr/bin/env python
"""OCF-G1 · Quién escribe cada pieza de estado del organismo, medido.

La tabla de escritores de `FRONTERA_ESTADO_APRENDIDO_01` se llenó leyendo el
código. Esta sonda no lee: instrumenta `__setattr__` del agente y de cada
submódulo, envuelve `perceive` / `decide` / `learn`, y registra qué atributo se
escribe en qué fase y cuántas veces. Lo que el código hace y lo que su lectura
sugiere no siempre coinciden -- `homeostasis._energy` es el caso que motivó
esto: `update()` lo acumula en `learn` y `perceive` lo pisa por asignación.

Escritura en sitio (`M.data.copy_`) no pasa por `__setattr__`, así que además
se hashea el conjunto adaptativo al final de cada fase y se atribuye el cambio
a la fase que lo produjo.

Sólo lectura sobre el repositorio y sobre la base viva.

    python scripts/state_authority_probe.py
    python scripts/state_authority_probe.py --pasos 120 --semilla 3
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from collections import Counter, defaultdict
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

PHASES = ("perceive", "decide", "learn", "fuera-de-fase")

CONFIG: dict[str, Any] = {
    "use_planner": False, "use_uncertainty": True, "use_episodic_memory": True,
    "use_longterm_memory": True, "use_temporal": True, "use_online_learning": True,
    "latent_dim": 16, "hidden_dim": 24, "memory_dim": 8, "memory_slots": 4,
    "memory_capacity": 16, "ensemble_size": 2,
}


class _Phase:
    """La fase en curso, compartida por todos los interceptores."""

    now: str = "fuera-de-fase"


def _instrument_writes(obj: Any, label: str, log: Counter) -> None:
    """Registrar cada `setattr` sobre `obj` como (fase, label.atributo)."""
    cls = type(obj)
    if getattr(cls, "_authority_probed", False):
        return
    original = cls.__setattr__

    def probed(self, name, value, _o=original, _l=label):
        if not name.startswith("__"):
            log[(_Phase.now, f"{_l}.{name}")] += 1
        _o(self, name, value)

    probed_cls = type(cls.__name__, (cls,), {"__setattr__": probed,
                                             "_authority_probed": True})
    obj.__class__ = probed_cls


def _adaptive_digest(agent: Any) -> dict[str, str]:
    """Una huella por pieza del conjunto adaptativo, para atribuir cambios en
    sitio a la fase que los hizo. La frontera es la que adoptó
    `FRONTERA_ESTADO_APRENDIDO_01`: parámetros + buffer + M + baseline."""
    out: dict[str, str] = {}
    h = hashlib.sha256()
    for name, value in sorted(agent.get_parameters().items()):
        h.update(name.encode())
        h.update(value.detach().cpu().contiguous().numpy().tobytes())
    out["parámetros (optimizador)"] = h.hexdigest()[:12]

    m = getattr(getattr(agent, "longterm_memory", None), "M", None)
    out["longterm_memory.M"] = (
        hashlib.sha256(m.detach().cpu().contiguous().numpy().tobytes()).hexdigest()[:12]
        if m is not None else "—")

    buf = getattr(getattr(agent, "episodic_memory", None), "_buffer", None)
    if buf is None:
        out["episodic_memory._buffer"] = "—"
    else:
        hb = hashlib.sha256()
        for item in buf:
            hb.update(item["embedding"].detach().cpu().contiguous().numpy().tobytes())
            hb.update(str((item["action"], item["energy_delta"], item["timestamp"])).encode())
        out["episodic_memory._buffer"] = hb.hexdigest()[:12]

    out["_energy_baseline"] = f"{float(getattr(agent, '_energy_baseline', 0.0)):.9g}"
    out["homeostasis._energy"] = f"{float(agent.homeostasis.energy):.9g}"
    out["homeostasis._threshold"] = f"{float(agent.homeostasis.threshold):.9g}"
    return out


def probe(*, seed: int, steps: int) -> dict[str, Any]:
    world = gen.world_for(["LEARN-A1"], seed=seed, stations=8)
    components = build_episode_components(
        world.scenario, duration_fallback=world.duration, strict_physics=True,
        with_lifecycle=False, world_seed=world.seed)

    RNGManager.set_global_determinism(seed)
    agent = create_agent("A4_ADVANCED", CONFIG, seed=seed)

    writes: Counter = Counter()
    _instrument_writes(agent, "agente", writes)
    for attr in ("homeostasis", "episodic_memory", "longterm_memory", "learner"):
        sub = getattr(agent, attr, None)
        if sub is not None:
            _instrument_writes(sub, attr, writes)

    # Envolver las tres fases para saber en cuál estamos.
    changed: dict[str, Counter] = defaultdict(Counter)
    prev = _adaptive_digest(agent)

    def wrap(name: str):
        original = getattr(agent, name)

        def wrapped(*a, **k):
            nonlocal prev
            _Phase.now = name
            try:
                return original(*a, **k)
            finally:
                _Phase.now = "fuera-de-fase"
                now = _adaptive_digest(agent)
                for piece, digest in now.items():
                    if digest != prev[piece]:
                        changed[piece][name] += 1
                prev = now
        return wrapped

    for name in ("perceive", "decide", "learn"):
        setattr(agent, name, wrap(name))

    limit = min(steps, world.duration)
    lived = 0
    for step in range(limit):
        out = run_step(components, agent, step, world_seed=world.seed, agent_seed=seed,
                       max_steps=limit, learning_enabled=True)
        lived = step + 1
        if out.terminated or out.truncated:
            break
    return {"writes": writes, "changed": changed, "steps": lived, "world": world,
            "final": _adaptive_digest(agent)}


def run_clean(*, seed: int, steps: int) -> dict[str, str]:
    """La misma vida SIN instrumentar, para comparar la huella final."""
    world = gen.world_for(["LEARN-A1"], seed=seed, stations=8)
    components = build_episode_components(
        world.scenario, duration_fallback=world.duration, strict_physics=True,
        with_lifecycle=False, world_seed=world.seed)
    RNGManager.set_global_determinism(seed)
    agent = create_agent("A4_ADVANCED", CONFIG, seed=seed)
    limit = min(steps, world.duration)
    for step in range(limit):
        out = run_step(components, agent, step, world_seed=world.seed, agent_seed=seed,
                       max_steps=limit, learning_enabled=True)
        if out.terminated or out.truncated:
            break
    return _adaptive_digest(agent)


def _adaptive_digest_of(r: dict[str, Any]) -> dict[str, str]:
    return r["final"]


def report(seed: int, steps: int) -> int:
    r = probe(seed=seed, steps=steps)
    print(f"OCF-G1 · AUTORIDAD DE ESTADO — medido sobre {r['steps']} pasos "
          f"de un mundo generado (semilla {seed})\n")

    print("A · QUIÉN ESCRIBE QUÉ, POR FASE  (asignaciones de atributo)\n")
    by_attr: dict[str, dict[str, int]] = defaultdict(dict)
    for (phase, attr), n in r["writes"].items():
        by_attr[attr][phase] = n
    print(f"  {'estado':<42}" + "".join(f"{p:>16}" for p in PHASES))
    print("  " + "-" * (42 + 16 * len(PHASES)))
    multi = []
    for attr in sorted(by_attr):
        row = by_attr[attr]
        phases_touching = [p for p in PHASES if row.get(p)]
        if len(phases_touching) > 1:
            multi.append((attr, phases_touching))
        print(f"  {attr:<42}" + "".join(f"{row.get(p, 0) or '·':>16}" for p in PHASES))

    print("\n\nB · ESTADO CON MÁS DE UN ESCRITOR  (lo que OCF-G1 tiene que resolver)\n")
    if not multi:
        print("  ninguno")
    for attr, phases in sorted(multi):
        print(f"  {attr:<42}escrito en: {', '.join(phases)}")

    print("\n\nC · CAMBIOS EN SITIO DEL CONJUNTO ADAPTATIVO  (no pasan por setattr)\n")
    print(f"  {'pieza':<34}" + "".join(f"{p:>14}" for p in PHASES[:3]))
    print("  " + "-" * (34 + 14 * 3))
    for piece in ("parámetros (optimizador)", "longterm_memory.M",
                  "episodic_memory._buffer", "_energy_baseline",
                  "homeostasis._energy", "homeostasis._threshold"):
        row = r["changed"].get(piece, Counter())
        print(f"  {piece:<34}" + "".join(f"{row.get(p, 0) or '·':>14}" for p in PHASES[:3]))

    dueños = {p: [f for f in PHASES[:3] if r["changed"].get(p, Counter()).get(f)]
              for p in r["changed"]}
    disputadas = {p: f for p, f in dueños.items() if len(f) > 1}
    print("\n  Piezas del conjunto adaptativo con más de una fase escribiéndolas:")
    if not disputadas:
        print("    ninguna")
    for p, f in sorted(disputadas.items()):
        print(f"    · {p:<32}{', '.join(f)}")

    # --- La sonda se falsa a sí misma -------------------------------------
    #
    # Una sonda que no demuestra su propia pasividad no es evidencia. La
    # anterior de esta familia infló dos magnitudes 18.6x y 10x por
    # contaminarse a sí misma, y nadie lo vio hasta una verificación
    # adversarial. Aquí la vida instrumentada y la limpia tienen que terminar
    # con la MISMA huella, pieza por pieza.
    print("\n\nD · PASIVIDAD DE LA SONDA  (misma vida con y sin instrumentar)\n")
    clean = run_clean(seed=seed, steps=steps)
    probed = _adaptive_digest_of(r)
    print(f"  {'pieza':<34}{'instrumentada':>20}{'limpia':>20}   igual")
    print("  " + "-" * 82)
    passive = True
    for piece in sorted(clean):
        a, b = probed.get(piece, "?"), clean[piece]
        same = a == b
        passive &= same
        print(f"  {piece:<34}{a:>20}{b:>20}   {'sí' if same else 'NO'}")

    ok = not multi and not disputadas
    print(f"\n\n  OBSERVER_PASSIVITY = {'SÍ' if passive else 'NO'}"
          f"   -- sin esto, nada de lo de arriba es evidencia")
    print(f"  OCF-G1 = {'PASA' if ok and passive else 'NO PASA'}"
          f"   ({len(multi)} atributos y {len(disputadas)} piezas adaptativas "
          f"con escritor múltiple)")
    return 0 if (ok and passive) else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--semilla", type=int, default=7)
    ap.add_argument("--pasos", type=int, default=120)
    a = ap.parse_args()
    return report(a.semilla, a.pasos)


if __name__ == "__main__":
    raise SystemExit(main())
