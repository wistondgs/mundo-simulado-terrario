#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UNIDAD-MINIMA-05f · n=6 con la vida de n=8: ¿el hueco es transitorio o recurrente?

A igual n_min la identificación es plana en n=3, 4 y 6, y n=8 salta 20 puntos junto
a un colapso de la transitoriedad relativa. La diferencia entre n=6 y n=8 no es el
tamaño del mundo (4,38 frente a 4,53 estados alcanzables a igual n_min) sino cuánto
se vive: 3 586 frente a 18 434 pasos.

Esto corre n=6 con L=10 —la vida de n=8— y nada más cambiado. Si la identificación
sube, el hueco es TRANSITORIO y lo cura vivir mucho más. Si se queda, es RECURRENTE.

Predicción y falsador: `APERTURA_ESCALADO_SIN_AZAR.md`, «Segunda variante de cobertura».
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
import time
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unidad_minima_05_banco import (  # noqa: E402
    FUTURO_MAX, L_de, alcanzables, shortlex, un_sistema,
)

N = 6
L_LARGA = L_de(8)          # 10, la vida de n=8
POR_ESTRATO = 200          # submuestra declarada por estrato de n_min


def transitoriedad(A, B, vida):
    S = alcanzables(A, B)
    c = Counter()
    x = 0
    for a in vida:
        c[x] += 1
        x = A[x] if a == "A" else B[x]
    c[x] += 1
    vis = [c[y] for y in S]
    media = sum(vis) / len(vis)
    return sum(1 for v in vis if v < 0.10 * media), len(S)


def correr():
    aqui = os.path.dirname(os.path.abspath(__file__))
    filas = [json.loads(l) for l in
             open(os.path.join(aqui, "artifacts", "unidad_minima_05_banco.jsonl"),
                  encoding="utf-8") if l.strip()]
    g6 = [r for r in filas if r["n"] == N and r["n_min"] >= 2]
    por_nmin = defaultdict(list)
    for r in sorted(g6, key=lambda r: r["idx"]):
        por_nmin[r["n_min"]].append(r)
    # submuestra determinista: uno de cada k del estrato, para cubrirlo entero
    muestra = {}
    for nm, lista in sorted(por_nmin.items()):
        paso = max(1, len(lista) // POR_ESTRATO)
        muestra[nm] = lista[::paso][:POR_ESTRATO]

    vida_corta = shortlex(range(1, L_de(N) + 1))
    vida_larga = shortlex(range(1, L_LARGA + 1))
    futuro = shortlex([L_LARGA + 1])[:FUTURO_MAX]
    print(f"n={N} · vida corta L={L_de(N)} ({len(vida_corta)} pasos) frente a "
          f"vida larga L={L_LARGA} ({len(vida_larga)} pasos)")
    print(f"submuestra declarada: hasta {POR_ESTRATO} sistemas por estrato de n_min, "
          f"uno de cada k del estrato en orden canónico\n")
    print(f"{'n_min':>6} {'sist.':>6} {'ident. L=8':>11} {'ident. L=10':>12} {'Δ':>7} "
          f"{'transit. L=8':>13} {'transit. L=10':>14} {'s/sistema':>10}")
    rep = {"n": N, "L_corta": L_de(N), "L_larga": L_LARGA,
           "vida_corta": len(vida_corta), "vida_larga": len(vida_larga),
           "por_estrato": POR_ESTRATO, "estratos": {}}
    for nm, lista in sorted(muestra.items()):
        t0 = time.perf_counter()
        ident_corta = 100.0 * sum(1 for r in lista if r["igual_salvo_isomorfismo"]) / len(lista)
        ok = tr_c = tr_l = al = 0
        for r in lista:
            A, B = tuple(r["A"]), tuple(r["B"])
            nuevo = un_sistema(N, r["idx"], vida_larga, futuro, False)
            ok += int(bool(nuevo["igual_salvo_isomorfismo"]))
            a, s = transitoriedad(A, B, vida_corta)
            b, _ = transitoriedad(A, B, vida_larga)
            tr_c += a
            tr_l += b
            al += s
        ident_larga = 100.0 * ok / len(lista)
        dt = (time.perf_counter() - t0) / len(lista)
        print(f"{nm:>6} {len(lista):>6} {ident_corta:>10.1f}% {ident_larga:>11.1f}% "
              f"{ident_larga - ident_corta:>+6.1f} {100 * tr_c / al:>12.1f}% "
              f"{100 * tr_l / al:>13.1f}% {dt:>10.2f}")
        rep["estratos"][str(nm)] = dict(
            sistemas=len(lista), ident_corta=round(ident_corta, 2),
            ident_larga=round(ident_larga, 2), delta=round(ident_larga - ident_corta, 2),
            transit_corta=round(100 * tr_c / al, 2), transit_larga=round(100 * tr_l / al, 2),
            s_por_sistema=round(dt, 4))
    rep["sha256_codigo"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    rep["python"] = sys.version.split()[0]
    with open(os.path.join(aqui, "artifacts", "unidad_minima_05f_vida_larga.json"), "w",
              encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    return rep


if __name__ == "__main__":
    correr()
