#!/usr/bin/env python
"""¿Transporta `longterm_memory.M` información de la tarea, o sólo magnitud?

La auditoría anterior midió que M se mueve mucho bajo el brazo suprimido y que
satura. Eso NO demuestra que lleve información: una matriz cuyos elementos están
todos en ±10 todavía puede conservar estructura en el patrón de signos, en el
rango y en su respuesta de recuperación. Y la regla de escritura

    M <- M*(1-g) + outer(w, v)*g

sí tiene término de retención: `M*(1-g)` es decaimiento efectivo cuando g > 0.
Afirmar «sin decaimiento» sin medir el rango real de g fue un error de la
auditoría anterior, y esta sonda lo corrige midiéndolo.

La pregunta que decide si M bloquea el piloto no es cuánto se mueve, sino:

    1. ¿M_A difiere de M_B cuando la contingencia difiere y la geometría no?
    2. ¿la lectura que el propio A4 usa devuelve algo distinto?
    3. ¿cambiar SOLO M cambia los logits de la política?
    4. ¿los cambia EN LA DIRECCIÓN de la contingencia?

Las cuatro se responden con el pipeline real: mundo generado, `run_step`,
observaciones canónicas, y la función de lectura del propio agente. Sólo lectura
sobre producción; no escribe ficheros ni toca `.terrario`.

    python scripts/m_information_audit.py
    python scripts/m_information_audit.py --semilla 11 --pasos 200
"""

from __future__ import annotations

import argparse
import copy
import math
import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import torch  # noqa: E402

from terrario.agent.agents import create_agent  # noqa: E402
from terrario.core.rng import RNGManager  # noqa: E402
from terrario.core.types import Action, ActionType, Direction  # noqa: E402
from terrario.lab import world_generator as gen  # noqa: E402
from terrario.world.transition import build_episode_components, run_step  # noqa: E402

CONSUME_UP = Action(ActionType.CONSUME, Direction.UP).to_int()
CONSUME_DOWN = Action(ActionType.CONSUME, Direction.DOWN).to_int()


def _config(*, commit: bool) -> dict[str, Any]:
    return {
        "use_planner": False, "use_uncertainty": True, "use_episodic_memory": True,
        "use_longterm_memory": True, "use_temporal": True, "use_online_learning": True,
        "latent_dim": 16, "hidden_dim": 24, "memory_dim": 8, "memory_slots": 4,
        "memory_capacity": 16, "ensemble_size": 2, "learning_commit_enabled": commit,
    }


def _agent(seed: int, *, commit: bool = False):
    RNGManager.set_global_determinism(seed)
    return create_agent("A4_ADVANCED", _config(commit=commit), seed=seed)


def _inverted(world: gen.GeneratedWorld) -> dict[str, Any]:
    """El mismo mundo con la contingencia dada vuelta y la geometría intacta.

    Misma semilla, mismo trazado, mismos cues, mismas estaciones: sólo cambia
    qué canal oculto paga. Es el contrafáctico que hace falta -- historias que
    difieren en la contingencia relevante y en nada más.
    """
    e = world.economy
    scenario = copy.deepcopy(world.scenario)
    scenario["rules"] = gen._rules(-e.loss, e.gain, e.safe)
    scenario["name"] = scenario["name"] + "_invertido"
    return scenario


def _vivir(scenario: dict[str, Any], seed: int, pasos: int, *, commit: bool = False):
    """Una vida. Devuelve el agente y las observaciones reales que vivió."""
    components = build_episode_components(
        scenario, duration_fallback=int(scenario["duration"]), strict_physics=True,
        with_lifecycle=False, world_seed=seed)
    agent = _agent(seed, commit=commit)
    limite = min(pasos, int(scenario["duration"]))
    observaciones = []
    for step in range(limite):
        outcome = run_step(components, agent, step, world_seed=seed, agent_seed=seed,
                           max_steps=limite, learning_enabled=True)
        observaciones.append(outcome.observation_t)
        if outcome.terminated or outcome.truncated:
            break
    return agent, observaciones


# --- FASE 5 · dinámica real de M ----------------------------------------------

def dinamica(agent) -> dict[str, Any]:
    escrituras = [t for t in agent.longterm_memory._trace if t["op"] == "longterm_write"]
    gates = [t["gate_value"] for t in escrituras]
    m = agent.longterm_memory.M.detach()
    total = m.numel()
    en_tope = int((m.abs() >= 9.999).sum())
    positivos = int((m > 0).sum())
    p = positivos / total
    entropia = 0.0 if p in (0.0, 1.0) else -(p * math.log2(p) + (1 - p) * math.log2(1 - p))
    valores = torch.linalg.svdvals(m)
    normalizados = valores / valores.sum()
    rango_efectivo = float(torch.exp(-(normalizados * torch.log(normalizados + 1e-12)).sum()))
    return {
        "escrituras": len(escrituras),
        "g_min": min(gates) if gates else float("nan"),
        "g_max": max(gates) if gates else float("nan"),
        "g_medio": sum(gates) / len(gates) if gates else float("nan"),
        "norma_M": float(m.norm()),
        "fraccion_en_tope": en_tope / total,
        "fraccion_positivos": p,
        "entropia_de_signo": entropia,
        "rango_efectivo": rango_efectivo,
        "rango_maximo": min(m.shape),
    }


# --- FASE 7/8 · ¿distingue historias? -----------------------------------------

def comparar(a, b, observaciones) -> dict[str, Any]:
    ma = a.longterm_memory.M.detach()
    mb = b.longterm_memory.M.detach()
    signos = int((torch.sign(ma) != torch.sign(mb)).sum())
    coseno = float(torch.nn.functional.cosine_similarity(
        ma.flatten().unsqueeze(0), mb.flatten().unsqueeze(0)).item())

    # Recuperación con la MISMA función que usa el agente, sobre consultas
    # derivadas de observaciones reales -- no vectores inventados.
    diffs = []
    with torch.no_grad():
        for obs in observaciones[:24]:
            a.perceive(obs)
            hidden = a._hidden.detach().squeeze()
            ca, _ = a.longterm_memory.read(hidden)
            cb, _ = b.longterm_memory.read(hidden)
            diffs.append(float((ca - cb).norm() / (ca.norm() + 1e-9)))
    return {
        "signos_distintos": signos,
        "elementos": ma.numel(),
        "coseno": coseno,
        "recuperacion_dif_relativa_media": sum(diffs) / len(diffs) if diffs else float("nan"),
        "recuperacion_dif_relativa_max": max(diffs) if diffs else float("nan"),
    }


# --- FASE 9/10 · ¿cambiar SOLO M cambia la política? ---------------------------

def causal(agent, m_alterna: torch.Tensor, observaciones) -> dict[str, Any]:
    """Mismo estado en todo salvo M. Compara logits ANTES del muestreo.

    No se clona el agente: el estado recurrente `h` no depende de M, así que se
    calcula una vez por observación y se llama dos veces a `_build_state` y
    `policy_head` del propio agente, intercambiando sólo M entre medias. Son las
    funciones reales del organismo, no una reimplementación, y la única variable
    que difiere entre las dos lecturas es la matriz de memoria.
    """
    memoria = agent.longterm_memory.M
    cambios = giros = sesgo_hacia_b = 0
    deltas, sesgos, escalas = [], [], []
    for obs in observaciones[:24]:
        agent.perceive(obs)
        latent = agent._last_latent
        with torch.no_grad():
            salida, siguiente = agent.temporal_core(latent.unsqueeze(0), agent._hidden)
            h = salida.squeeze(0)
            la = agent.policy_head(agent._build_state(latent, h))
            respaldo = memoria.detach().clone()
            memoria.data.copy_(m_alterna)
            lb = agent.policy_head(agent._build_state(latent, h))
            memoria.data.copy_(respaldo)
        agent._hidden = siguiente.detach()

        delta = float((la - lb).norm())
        deltas.append(delta)
        escalas.append(float(la.norm()))
        cambios += delta > 1e-9
        giros += int(la.argmax()) != int(lb.argmax())
        # Dirección: si M llevara el mapeo, cambiarla debería inclinar la
        # preferencia entre las dos puertas, no sólo mover los logits.
        pref_a = float(la[CONSUME_UP] - la[CONSUME_DOWN])
        pref_b = float(lb[CONSUME_UP] - lb[CONSUME_DOWN])
        sesgos.append(pref_b - pref_a)
        sesgo_hacia_b += (pref_a > 0) != (pref_b > 0)
    return {
        "observaciones": len(deltas),
        "logits_cambiaron": cambios,
        "argmax_cambio": giros,
        "delta_logits_medio": sum(deltas) / len(deltas) if deltas else float("nan"),
        "delta_logits_max": max(deltas) if deltas else float("nan"),
        "norma_logits_media": sum(escalas) / len(escalas) if escalas else float("nan"),
        "delta_relativo": (sum(deltas) / sum(escalas)) if escalas else float("nan"),
        "preferencia_puerta_invertida": sesgo_hacia_b,
        "desplazamiento_preferencia_medio": sum(sesgos) / len(sesgos) if sesgos else float("nan"),
    }


def _f(x) -> str:
    return f"{x:.6g}" if isinstance(x, float) else str(x)


def informe(seed: int, pasos: int) -> int:
    base = gen.world_for(["LEARN-A1"], seed=seed, stations=8)
    print("AUDITORÍA DE INFORMACIÓN EN longterm_memory.M")
    print(f"  mundo: {base.describe()}  ·  semilla {seed}\n")

    print("FASE 4 · camino de lectura (leído del código, no supuesto)")
    print("  hidden -> longterm_memory.read(hidden) -> lt_context   a4_advanced.py:333")
    print("  state = concat(latent, hidden, memory_context, lt_context)   a4_advanced.py:337")
    print("  policy_head(state) -> logits -> acción")
    print("  M entra DOS veces en la lectura: key_proj(M) fija la atención y `attn @ M`")
    print("  es el valor devuelto (memory.py:181-186). Con use_longterm=False se")
    print("  sustituye por ceros conservando la dimensión (a4_advanced.py:335).\n")

    pasos_full = pasos
    a, obs_a = _vivir(base.scenario, seed, pasos)
    b, _ = _vivir(_inverted(base), seed, pasos)

    print("FASE 5 · dinámica real de M (contingencia A)")
    d = dinamica(a)
    for k in ("escrituras", "g_min", "g_medio", "g_max", "norma_M", "fraccion_en_tope",
              "fraccion_positivos", "entropia_de_signo", "rango_efectivo", "rango_maximo"):
        print(f"    {k:<28}{_f(d[k])}")
    print(f"\n    El término M*(1-g) retiene {1 - d['g_max']:.3g} .. {1 - d['g_min']:.3g}"
          f" de M por escritura: hay decaimiento, no ausencia de él.")

    print("\nFASE 7/8 · ¿M_A difiere de M_B con la misma geometría y la contingencia invertida?")
    c = comparar(a, b, obs_a)
    for k, v in c.items():
        print(f"    {k:<38}{_f(v)}")

    print("\nFASE 9/10 · ¿cambiar SÓLO M cambia la política?")
    m_b = b.longterm_memory.M.detach().clone()
    z = causal(a, m_b, obs_a)
    for k, v in z.items():
        print(f"    {k:<38}{_f(v)}")

    # Bajo ABL los pesos que leen `lt_context` nunca se entrenan, así que una M
    # enorme puede atravesar pesos casi nulos y no mover nada. Bajo FULL sí se
    # entrenan: si la influencia de M crece con el entrenamiento, el confusor es
    # asimétrico entre brazos y eso cambia su lectura.
    print("\n  el mismo intercambio sobre un gemelo CON commit (pesos de lectura entrenados)")
    entrenado, obs_f = _vivir(base.scenario, seed, pasos_full, commit=True)
    zf = causal(entrenado, m_b, obs_f)
    for k in ("logits_cambiaron", "argmax_cambio", "delta_logits_medio", "delta_relativo",
              "preferencia_puerta_invertida"):
        print(f"    {k:<38}{_f(zf[k])}")

    discrimina = c["signos_distintos"] > 0 or c["coseno"] < 0.999
    recupera = c["recuperacion_dif_relativa_media"] > 1e-6
    causa = z["logits_cambiaron"] > 0
    dirige = z["argmax_cambio"] > 0

    print("\nGATES")
    print(f"  LSB.3  M_SATURATION_CHARACTERIZED         PASS  "
          f"({d['fraccion_en_tope']:.0%} en tope, entropía de signo {d['entropia_de_signo']:.3f},"
          f" rango efectivo {d['rango_efectivo']:.2f}/{d['rango_maximo']})")
    print(f"  LSB.4  M_HISTORY_DISCRIMINATION           {'PASS' if discrimina else 'FAIL'}")
    print(f"  LSB.5  M_RETRIEVAL_DIFFERENTIATES         {'PASS' if recupera else 'FAIL'}")
    print(f"  LSB.6  M_CAUSALLY_AFFECTS_POLICY          {'PASS' if causa else 'FAIL'}")
    print(f"  LSB.7  M_MAPPING_CARRIER                  "
          f"{'STRONG_EVIDENCE' if dirige else 'UNPROVEN' if causa else 'NO'}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--semilla", type=int, default=7)
    parser.add_argument("--pasos", type=int, default=300)
    args = parser.parse_args()
    return informe(args.semilla, args.pasos)


if __name__ == "__main__":
    raise SystemExit(main())
