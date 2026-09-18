#!/usr/bin/env python
"""Los cuatro estados adaptativos que faltaban, y la prueba que los cubre a todos.

`m_information_audit.py` caracterizó `longterm_memory.M`. Quedaban cuatro piezas
que cambian con la experiencia y que la intervención de G4 no controla: buffer
episódico, estado recurrente, homeostasis y baseline del learner. Esta sonda les
aplica el mismo contrafáctico —misma geometría, contingencia invertida— y añade
la prueba que vale por todas ellas juntas:

    bajo SUPPRESS_COMMIT los parámetros de A_HA y A_HB son idénticos.
    Si además se limpian los estados transitorios que no pertenecen a LEARN-A1,
    sus políticas deberían ser indistinguibles. Si no lo son, queda información
    adquirida en algún sitio que no hemos caracterizado.

Es más fuerte que inspeccionar atributos uno a uno: no depende de haber acertado
la lista. Y su contraparte —que los gemelos CON commit sigan difiriendo tras la
misma limpieza— comprueba que el saneamiento no borra lo que el piloto quiere
medir.

Sólo lectura sobre producción. No escribe ficheros ni toca `.terrario`.

    python scripts/adaptive_state_boundary_audit.py
    python scripts/adaptive_state_boundary_audit.py --semilla 11
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Callable

PROJECT_ROOT = Path(__file__).resolve().parents[1]
for extra in (str(PROJECT_ROOT), str(Path(__file__).resolve().parent)):
    if extra not in sys.path:
        sys.path.insert(0, extra)

import torch  # noqa: E402

from m_information_audit import _inverted, _vivir  # noqa: E402
from terrario.lab import world_generator as gen  # noqa: E402

MUESTRAS = 24


# --- El banco de pruebas causal ------------------------------------------------

def _decidir(agent, obs, tras_percibir: Callable | None = None) -> dict[str, torch.Tensor]:
    """Los logits y las probabilidades por el camino real, sin muestrear.

    `policy_head` da los logits crudos; la temperatura homeostática entra en la
    softmax (`a4_advanced.py:442`), así que un estado que sólo mueve la
    temperatura no aparece en los logits y sí en la distribución. Las dos se
    miden por separado a propósito.
    """
    agent.perceive(obs)
    # `perceive` sobrescribe `homeostasis._energy` desde la observación
    # (a4_advanced.py:352), así que un estado que se quiera probar en el momento
    # de decidir tiene que fijarse AQUÍ, no antes.
    if tras_percibir is not None:
        tras_percibir(agent)
    latent = agent._last_latent
    with torch.no_grad():
        salida, siguiente = agent.temporal_core(latent.unsqueeze(0), agent._hidden)
        h = salida.squeeze(0)
        state = agent._build_state(latent, h)
        logits = agent.policy_head(state)
        temperatura = (1.0 + agent.homeostasis.exploration_bias) if agent._use_homeostasis else 1.0
        probs = torch.softmax(logits / temperatura, dim=-1)
    return {"logits": logits, "probs": probs, "siguiente": siguiente.detach(),
            "temperatura": torch.tensor(float(temperatura))}


def efecto(agent, observaciones, poner_a: Callable, poner_b: Callable) -> dict[str, Any]:
    """Mismo estado en todo salvo la pieza intercambiada."""
    d_logits, d_probs, giros, d_temp = [], [], 0, []
    escalas = []
    for obs in observaciones[:MUESTRAS]:
        antes = agent._hidden.detach().clone()
        # El orden importa: se restaura el estado recurrente comun PRIMERO y se
        # aplica la variante DESPUES, o la restauracion anula el intercambio que
        # se quiere medir.  La primera version de esta sonda lo hacia al reves y
        # daba un delta de cero para el estado recurrente.
        agent._hidden = antes.clone()
        a = _decidir(agent, obs, poner_a)
        agent._hidden = antes.clone()
        b = _decidir(agent, obs, poner_b)
        agent._hidden = a["siguiente"]

        d_logits.append(float((a["logits"] - b["logits"]).norm()))
        escalas.append(float(a["logits"].norm()))
        d_probs.append(float((a["probs"] - b["probs"]).abs().sum()))
        d_temp.append(abs(float(a["temperatura"] - b["temperatura"])))
        giros += int(a["probs"].argmax()) != int(b["probs"].argmax())
    n = len(d_logits)
    return {
        "delta_logits_rel": sum(d_logits) / sum(escalas) if escalas else float("nan"),
        "delta_probs_L1": sum(d_probs) / n if n else float("nan"),
        "delta_temperatura": max(d_temp) if d_temp else float("nan"),
        "acciones_preferidas_cambiadas": giros,
        "muestras": n,
    }


def efecto_recurrente(agent, observaciones, ha, hb) -> dict[str, Any]:
    """El recurrente entra ANTES del temporal core, no despues de percibir."""
    d_logits, d_probs, giros, escalas = [], [], 0, []
    for obs in observaciones[:MUESTRAS]:
        agent._hidden = ha.clone()
        a = _decidir(agent, obs)
        agent._hidden = hb.clone()
        b = _decidir(agent, obs)
        d_logits.append(float((a["logits"] - b["logits"]).norm()))
        escalas.append(float(a["logits"].norm()))
        d_probs.append(float((a["probs"] - b["probs"]).abs().sum()))
        giros += int(a["probs"].argmax()) != int(b["probs"].argmax())
    n = len(d_logits)
    return {"delta_logits_rel": sum(d_logits) / sum(escalas) if escalas else float("nan"),
            "delta_probs_L1": sum(d_probs) / n if n else float("nan"),
            "delta_temperatura": 0.0, "acciones_preferidas_cambiadas": giros, "muestras": n}


# --- Los cuatro estados ---------------------------------------------------------

def _clonar_episodica(agent):
    return ([dict(e) for e in agent.episodic_memory._buffer], agent.episodic_memory._write_idx)


def _poner_episodica(estado):
    def aplicar(agent):
        agent.episodic_memory._buffer = [dict(e) for e in estado[0]]
        agent.episodic_memory._write_idx = estado[1]
    return aplicar


def _poner_homeostasis(valor):
    def aplicar(agent):
        agent.homeostasis._energy = valor
    return aplicar


def _poner_baseline(valor, cuenta):
    def aplicar(agent):
        agent._energy_baseline, agent._baseline_count = valor, cuenta
    return aplicar


def _sanear(agent, energia_canonica: float = 0.5) -> None:
    """El contrato de limpieza propuesto, con APIs existentes y nada más.

    NO incluye `longterm_memory`: M no demostró transportar el mapeo y borrarla
    sería una intervención distinta. NO incluye parámetros ni estado del
    optimizador, que es justo lo que el piloto quiere medir.
    """
    agent.episodic_memory.reset()
    agent._hidden = agent.temporal_core.initial_state(1)
    agent._last_hidden = None
    agent.homeostasis._energy = energia_canonica
    agent._energy_baseline, agent._baseline_count = 0.0, 0


def _hash_politica(agent, observaciones) -> tuple[str, float]:
    import hashlib
    h = hashlib.sha256()
    total = 0.0
    for obs in observaciones[:MUESTRAS]:
        d = _decidir(agent, obs)
        agent._hidden = d["siguiente"]
        v = d["logits"].numpy()
        h.update(v.tobytes())
        total += float(abs(v).sum())
    return h.hexdigest()[:16], total


def _f(x) -> str:
    return f"{x:.6g}" if isinstance(x, float) else str(x)


def informe(seed: int, pasos: int) -> int:
    base = gen.world_for(["LEARN-A1"], seed=seed, stations=8)
    print(f"FRONTERA DE ESTADO ADAPTATIVO · semilla {seed}\n")

    a, obs = _vivir(base.scenario, seed, pasos)
    b, _ = _vivir(_inverted(base), seed, pasos)

    print("CAMINOS (leídos del código)")
    print("  episódica  write: embedding=_last_latent, action, energy_delta, prediction_error,")
    print("                    timestamp   (memory.py:41-47)")
    print("             read : SÓLO embeddings por coseno; action y energy_delta se escriben")
    print("                    y nunca se leen hacia la decisión   (a4_advanced.py:325-327)")
    print("  recurrente write: temporal_core, detach cada paso   (a4_advanced.py:402-403)")
    print("  homeostasis     : perceive() la SOBRESCRIBE desde la observación cada paso")
    print("                    (a4_advanced.py:352); sólo entra por temperature en la softmax")
    print("                    (a4_advanced.py:442), no en los logits")
    print("  baseline        : leído únicamente en learn() para `advantage`")
    print("                    (a4_advanced.py:653); no aparece en decide ni en _build_state\n")

    print("DISCRIMINACIÓN DE HISTORIAS (H_A vs H_B, contingencia invertida)")
    ea, eb = _clonar_episodica(a), _clonar_episodica(b)
    emb_a = torch.stack([e["embedding"] for e in ea[0]]) if ea[0] else torch.zeros(1)
    emb_b = torch.stack([e["embedding"] for e in eb[0]]) if eb[0] else torch.zeros(1)
    dif_emb = float((emb_a - emb_b).norm()) if emb_a.shape == emb_b.shape else float("nan")
    dif_out = sum(1 for x, y in zip(ea[0], eb[0]) if x["energy_delta"] != y["energy_delta"])
    print(f"  episódica · entradas                 {len(ea[0])} vs {len(eb[0])}")
    print(f"  episódica · ‖Δ embeddings‖           {_f(dif_emb)}")
    print(f"  episódica · outcomes distintos       {dif_out} / {min(len(ea[0]), len(eb[0]))}")
    print(f"  recurrente · ‖Δ hidden‖              {_f(float((a._hidden - b._hidden).norm()))}")
    print(f"  homeostasis · energía                {_f(a.homeostasis.energy)} vs {_f(b.homeostasis.energy)}")
    print(f"  baseline                             {_f(a._energy_baseline)} vs {_f(b._energy_baseline)}\n")

    print("CAUSALIDAD SOBRE LA POLÍTICA (intercambio, mismo estado en todo lo demás)")
    pruebas = [
        ("episódica", _poner_episodica(ea), _poner_episodica(eb)),
        ("homeostasis", _poner_homeostasis(a.homeostasis.energy), _poner_homeostasis(b.homeostasis.energy)),
        ("baseline", _poner_baseline(a._energy_baseline, a._baseline_count),
         _poner_baseline(b._energy_baseline, b._baseline_count)),
    ]
    print(f"  {'estado':<14}{'Δlogits rel':>14}{'Δprobs L1':>12}{'Δtemp':>10}{'acciones':>10}")
    resultados = {}
    for nombre, pa, pb in pruebas:
        r = efecto(a, observaciones=obs, poner_a=pa, poner_b=pb)
        resultados[nombre] = r
        print(f"  {nombre:<14}{r['delta_logits_rel']:>14.3g}{r['delta_probs_L1']:>12.3g}"
              f"{r['delta_temperatura']:>10.3g}{r['acciones_preferidas_cambiadas']:>10}")

    dif_hidden = float((a._hidden - b._hidden).norm())
    ha, hb = a._hidden.detach().clone(), b._hidden.detach().clone()
    r = efecto_recurrente(a, obs, ha, hb)
    resultados["recurrente"] = r
    print(f"  {'recurrente':<14}{r['delta_logits_rel']:>14.3g}{r['delta_probs_L1']:>12.3g}"
          f"{r['delta_temperatura']:>10.3g}{r['acciones_preferidas_cambiadas']:>10}")

    print("\nPRUEBA DE SANEAMIENTO — el gate fuerte")
    print("  bajo ABL los parámetros de A_HA y A_HB son idénticos por construcción.")
    _sanear(a); _sanear(b)
    fa, ta = _hash_politica(a, obs)
    fb, tb = _hash_politica(b, obs)
    equivalentes = fa == fb
    print(f"    política ABL(H_A) saneada         {fa}")
    print(f"    política ABL(H_B) saneada         {fb}")
    print(f"    equivalentes                      {'SÍ' if equivalentes else 'NO'}")

    fa2, _ = _vivir(base.scenario, seed, pasos, commit=True)
    fb2, _ = _vivir(_inverted(base), seed, pasos, commit=True)
    _sanear(fa2); _sanear(fb2)
    ga, _ = _hash_politica(fa2, obs)
    gb, _ = _hash_politica(fb2, obs)
    print(f"    política FULL(H_A) saneada        {ga}")
    print(f"    política FULL(H_B) saneada        {gb}")
    print(f"    conservan diferencia              {'SÍ' if ga != gb else 'NO'}")

    print("\nGATES")
    print(f"  LSB.16 EPISODIC_HISTORY_DISCRIMINATION   "
          f"{'PASS' if dif_emb > 1e-9 or dif_out else 'NO'}")
    print(f"  LSB.17 EPISODIC_POLICY_CAUSALITY         "
          f"{'PASS' if resultados['episódica']['delta_logits_rel'] > 1e-9 else 'NO'}")
    print(f"  LSB.19 RECURRENT_HISTORY_DISCRIMINATION  "
          f"{'PASS' if dif_hidden > 1e-9 else 'NO'}  (‖Δ hidden‖ = {dif_hidden:.3g})")
    print(f"  LSB.20 RECURRENT_POLICY_CAUSALITY        "
          f"{'PASS' if resultados['recurrente']['delta_logits_rel'] > 1e-9 else 'NO'}")
    print(f"  LSB.23 HOMEOSTASIS_POLICY_CAUSALITY      "
          f"logits {'no' if resultados['homeostasis']['delta_logits_rel'] <= 1e-9 else 'SÍ'}"
          f" · distribución {'no' if resultados['homeostasis']['delta_probs_L1'] <= 1e-9 else 'SÍ'}")
    print(f"  LSB.25 BASELINE_POLICY_CAUSALITY         "
          f"{'NO (esperado)' if resultados['baseline']['delta_logits_rel'] <= 1e-9 else 'SÍ — INESPERADO'}")
    print(f"  LSB.26 SANITIZED_ABL_HISTORY_EQUIVALENCE {'PASS' if equivalentes else 'FAIL'}")
    print(f"  LSB.27 SANITIZATION_PRESERVES_TARGET     {'PASS' if ga != gb else 'FAIL'}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--semilla", type=int, default=7)
    parser.add_argument("--pasos", type=int, default=300)
    args = parser.parse_args()
    return informe(args.semilla, args.pasos)


if __name__ == "__main__":
    raise SystemExit(main())
