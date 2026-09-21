#!/usr/bin/env python3
"""¿Recorre el endpoint realmente Z? AUDITORÍA · sobre la ruta de campaña.

81 tests verdes convivieron con un scoring que nunca movía el estado. Así que
esto no comprueba números bonitos: comprueba el orden causal, paso a paso, sobre
`terrario.level18.life.live` --el mismo camino que recorrerá la campaña.

    O_t, A_t, Z_t  ->  P_18  ->  Z_{t+1}

Cinco condiciones, cada una con su demostración:

  1 puntuar usa el estado correcto      P18 == predict(O_t,A_t)[O_{t+1}] desde Z_t
  2 la transición ocurre DESPUÉS        Z_{t+1} == _next_state(Z_t, A_t, O_{t+1})
  3 evaluar no aprende                  updates y splits constantes en todo el banco
  4 entrenar sí actualiza               updates == T_18 al acabar el entrenamiento
  5 sin fuga de O_{t+1}                 la distribución suma 1 ANTES de revelarlo
"""
from __future__ import annotations

import sys

import numpy as np

sys.path.insert(0, ".")

from terrario.level16.temporal import OBSERVATION_INDEX          # noqa: E402
from terrario.level17.efference import ALL_COMMANDS, EfferenceCopy  # noqa: E402
from terrario.level18.life import live                            # noqa: E402
from terrario.level18.predictive_state import PredictiveStateModel  # noqa: E402

SEED = 150000011
BUDGET = 4096


def main() -> None:
    trace: list = []
    row = live(SEED, BUDGET, trace=trace)

    print(f"=== traza del endpoint · semilla {SEED} · T_18={BUDGET} ===\n")
    print(f"{'t':>4} {'O_t':>4} {'A_t':>4} {'Z_t':>5} {'O_t+1':>6} {'P18':>9} "
          f"{'Z_t+1':>6} {'movió':>6}")
    for entry in trace[:14]:
        print(f"{entry['t']:>4} {entry['O_t']:>4} {entry['A_t']:>4} "
              f"{entry['Z_t']:>5} {entry['O_next']:>6} {entry['P18']:>9.5f} "
              f"{entry['Z_next']:>6} {'sí' if entry['Z_next'] != entry['Z_t'] else '·':>6}")

    cambios = sum(1 for e in trace if e["Z_next"] != e["Z_t"])
    visitados = {e["Z_t"] for e in trace}
    print(f"\n  pasos puntuados {len(trace)} · transiciones de estado {cambios} "
          f"({100*cambios/len(trace):.1f}%) · estados distintos visitados {len(visitados)}")

    print("\n=== las cinco condiciones ===\n")
    veredictos = []

    # 3 · evaluar no aprende
    updates = {e["updates"] for e in trace}
    splits = {e["splits"] for e in trace}
    veredictos.append(("3 · evaluar no aprende",
                       len(updates) == 1 and len(splits) == 1,
                       f"updates {sorted(updates)} · splits {sorted(splits)}"))

    # 4 · entrenar sí actualiza
    veredictos.append(("4 · entrenar sí actualiza",
                       trace[0]["updates"] == BUDGET,
                       f"updates al acabar entrenamiento = {trace[0]['updates']} "
                       f"(esperado {BUDGET})"))

    # 1, 2 y 5 · reconstrucción independiente del recorrido
    modelo = PredictiveStateModel(np.zeros((16, 4, 16)))  # sólo para tipar
    del modelo
    trace_b: list = []
    fugas, desalineados, sumas = 0, 0, []
    replica: list = []
    live(SEED, BUDGET, trace=trace_b)
    assert [e["P18"] for e in trace_b] == [e["P18"] for e in trace], \
        "la ruta no es determinista: la auditoría no aplica"

    # Reejecutar el banco comprobando, paso a paso, la distribución COMPLETA
    from terrario.level18 import life as ruta
    inspeccion: list = []

    original = PredictiveStateModel.probability
    def espia(self, previous, efference, following):
        distribucion = self.predict(previous, efference)
        inspeccion.append({
            "estado": self._here,
            "suma": float(distribucion.sum()),
            "coordenada": float(distribucion[OBSERVATION_INDEX[following]]),
            "siguiente_esperado": self._next_state(
                self._here, ALL_COMMANDS.index(efference.command),
                OBSERVATION_INDEX[following]),
        })
        return original(self, previous, efference, following)
    PredictiveStateModel.probability = espia
    trace_c: list = []
    live(SEED, BUDGET, trace=trace_c)
    PredictiveStateModel.probability = original

    banco = inspeccion[:len(trace_c)]
    for miro, dice in zip(banco, trace_c):
        if abs(miro["suma"] - 1.0) > 1e-12:
            fugas += 1
        sumas.append(miro["suma"])
        if miro["coordenada"] != dice["P18"] or miro["estado"] != dice["Z_t"]:
            desalineados += 1
        if miro["siguiente_esperado"] != dice["Z_next"]:
            desalineados += 1

    veredictos.append(("1 · puntuar usa el estado correcto", desalineados == 0,
                       f"{len(banco)} pasos · desalineados {desalineados}"))
    veredictos.append(("2 · la transición ocurre DESPUÉS", desalineados == 0,
                       f"Z_t+1 == _next_state(Z_t, A_t, O_t+1) en {len(banco)} pasos"))
    veredictos.append(("5 · sin fuga de O_t+1", fugas == 0,
                       f"la distribución suma 1 antes de revelar O_t+1 · "
                       f"desviación máx {max(abs(s-1.0) for s in sumas):.2e}"))

    for nombre, ok, evidencia in veredictos:
        print(f"  [{'PASA' if ok else 'FALLA'}] {nombre:38s} {evidencia}")

    print(f"\n  L(C17)={row['l_c17']:.4f}  L(DEPTH-1)={row['l_depth1']:.4f}  "
          f"L(FULL)={row['l_full']:.4f}  L(ORACLE)={row['l_oracle']:.4f}")
    print(f"  ΔL={row['l_c17']-row['l_full']:+.4f}  "
          f"margen sobre DEPTH-1={row['l_depth1']-row['l_full']:+.4f}")
    if not all(ok for _n, ok, _e in veredictos):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
