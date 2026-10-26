#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UNIDAD-MINIMA-05c · variante declarada: ¿la cobertura falla por longitud o por itinerario?

La clase «la vida no determina la verdad» de la Fase 1 mezcla dos causas. Esta
variante las separa volviendo a vivir los sistemas NO determinados de n=3 y n=4
con una letra más de vida (L = n + 3 en vez de n + 2) y nada más cambiado.

  pasa a identificado con una letra más  ->  estaba limitado por LONGITUD
  sigue no determinado                   ->  está limitado por ITINERARIO

No reimplementa ninguna medida: importa `un_sistema` de `unidad_minima_05_banco`
y la llama con otra vida. La lectura y la predicción están declaradas en
`APERTURA_ESCALADO_SIN_AZAR.md`, «Variante declarada», antes de esta corrida.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unidad_minima_05_banco import FUTURO_MAX, L_de, shortlex, un_sistema  # noqa: E402


def correr(ns=(3, 4)):
    aqui = os.path.dirname(os.path.abspath(__file__))
    jsonl = os.path.join(aqui, "artifacts", "unidad_minima_05_banco.jsonl")
    filas = []
    with open(jsonl, encoding="utf-8") as f:
        for linea in f:
            try:
                filas.append(json.loads(linea))
            except ValueError:
                pass
    rep = {}
    for n in ns:
        base = [r for r in filas if r["n"] == n and r["clase"].startswith("la vida no determina")]
        L2 = L_de(n) + 1                     # n + 3
        vida = shortlex(range(1, L2 + 1))
        futuro = shortlex([L2 + 1])[:FUTURO_MAX]
        print(f"n={n}: {len(base)} sistemas no determinados con L={L_de(n)} "
              f"(vida {len(shortlex(range(1, L_de(n) + 1)))}); se reviven con L={L2} (vida {len(vida)})")
        mov = Counter()
        detalle = []
        for r in sorted(base, key=lambda r: r["idx"]):
            antes = "mismo tamaño" if "mismo tamaño" in r["clase"] else "admite menor"
            nuevo = un_sistema(n, r["idx"], vida, futuro, n <= 4)
            ahora = ("identificada" if nuevo["igual_salvo_isomorfismo"] else
                     "mismo tamaño" if "mismo tamaño" in nuevo["clase"] else
                     "admite menor" if "menor" in nuevo["clase"] else nuevo["clase"])
            mov[(antes, ahora)] += 1
            detalle.append(dict(idx=r["idx"], antes=antes, ahora=ahora,
                                estados_antes=r["estados_aprendidos"],
                                estados_ahora=nuevo["estados_aprendidos"],
                                n_min=r["n_min"], trabajo=nuevo["trabajo"],
                                vida_len=nuevo["vida_len"]))
        tot = sum(mov.values())
        res = {}
        for origen in ("mismo tamaño", "admite menor"):
            de = sum(v for k, v in mov.items() if k[0] == origen)
            resueltos = sum(v for k, v in mov.items() if k[0] == origen and k[1] == "identificada")
            res[origen] = dict(total=de, resueltos=resueltos,
                               fraccion=round(resueltos / de, 4) if de else None)
            if de:
                print(f"   de «{origen}»: {resueltos}/{de} = {100 * resueltos / de:.1f} % "
                      f"pasan a identificada con una letra más")
        resueltos_tot = sum(v for k, v in mov.items() if k[1] == "identificada")
        print(f"   total: {resueltos_tot}/{tot} = {100 * resueltos_tot / tot:.1f} % limitados por LONGITUD; "
              f"{tot - resueltos_tot} por ITINERARIO")
        print(f"   movimientos: { {f'{a} -> {b}': v for (a, b), v in sorted(mov.items())} }")
        rep[str(n)] = dict(L_base=L_de(n), L_variante=L2, sistemas=tot,
                           por_longitud=resueltos_tot, por_itinerario=tot - resueltos_tot,
                           por_origen=res,
                           movimientos={f"{a} -> {b}": v for (a, b), v in sorted(mov.items())},
                           detalle=detalle)
    rep["sha256_codigo"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    rep["python"] = sys.version.split()[0]
    with open(os.path.join(aqui, "artifacts", "unidad_minima_05c_cobertura.json"), "w",
              encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    return rep


if __name__ == "__main__":
    correr()
