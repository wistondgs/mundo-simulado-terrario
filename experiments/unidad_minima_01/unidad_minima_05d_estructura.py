#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UNIDAD-MINIMA-05d · ¿qué estructura del mundo decide si la vida lo determina?

La Fase 1 midió QUÉ fracción de mundos no queda determinada por una vida shortlex
sin reset (30,6 % en n=3, 37,4 % en n=4, 44,4 % en n=6). Esta pieza pregunta POR
QUÉ: qué tiene la dinámica de un mundo que lo hace determinable o no.

No corre ningún experimento nuevo: lee las tablas A y B de las filas ya grabadas
y calcula, sobre la parte alcanzable, la estructura cíclica de cada letra:
  - si la letra es una permutación de lo alcanzable (biyectiva), es decir reversible;
  - cuántos estados caen en ciclos (la parte recurrente del grafo funcional);
  - la longitud del ciclo más largo.

Y compara esas estructuras entre los sistemas IDENTIFICADOS y los de la clase
«dos máquinas del mismo tamaño la explican», **a igual n y a igual n_min**, que
es la única comparación que no mezcla dificultad con estructura.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unidad_minima_05_banco import alcanzables  # noqa: E402


def estructura(T, S):
    """Estructura cíclica del mapa T restringido a S (grafo funcional)."""
    Sset = set(S)
    es_perm = len({T[x] for x in S}) == len(Sset)
    # la parte recurrente: iterar |S| veces lleva a los ciclos
    enciclo = set()
    for x in S:
        y = x
        for _ in range(len(S)):
            y = T[y]
        # y está en un ciclo; recorrerlo
        z, ciclo = y, []
        while True:
            ciclo.append(z)
            z = T[z]
            if z == y:
                break
        enciclo.update(ciclo)
    # longitud del ciclo más largo
    visto, maxciclo = set(), 0
    for x in enciclo:
        if x in visto:
            continue
        z, largo = x, 0
        while z not in visto:
            visto.add(z)
            z = T[z]
            largo += 1
        maxciclo = max(maxciclo, largo)
    return es_perm, len(enciclo), maxciclo


def correr():
    aqui = os.path.dirname(os.path.abspath(__file__))
    filas = []
    with open(os.path.join(aqui, "artifacts", "unidad_minima_05_banco.jsonl"),
              encoding="utf-8") as f:
        for linea in f:
            try:
                filas.append(json.loads(linea))
            except ValueError:
                pass
    filas = [r for r in filas if r["n_min"] >= 2 and not r.get("sin_terminar_por_reloj")]
    print(f"{len(filas)} sistemas con distinción, leídos de las filas ya grabadas\n")

    rep = {}
    for r in filas:
        A, B = tuple(r["A"]), tuple(r["B"])
        S = alcanzables(A, B)
        pa, ca, ma = estructura(A, S)
        pb, cb, mb = estructura(B, S)
        r["_perm_A"], r["_perm_B"] = pa, pb
        r["_ciclos"] = (ca + cb) / (2 * len(S))
        r["_maxciclo"] = max(ma, mb)
        r["_clase2"] = ("identificada" if r["igual_salvo_isomorfismo"] else
                        "mismo tamaño" if "mismo tamaño" in r["clase"] else
                        "admite menor" if "menor" in r["clase"] else "otra")

    # --- identificación por (A permutación, B permutación), a igual n y n_min
    print("IDENTIFICACIÓN SEGÚN SI CADA LETRA ES UNA PERMUTACIÓN DE LO ALCANZABLE")
    print("(una letra que es permutación es reversible: no destruye información)\n")
    tabla = {}
    for n in sorted({r["n"] for r in filas}):
        g = [r for r in filas if r["n"] == n]
        nmins = sorted({r["n_min"] for r in g})
        print(f"  n={n}")
        print(f"    {'n_min':>6} {'A perm':>7} {'B perm':>7} {'sistemas':>9} {'identif.':>9} {'mismo tam.':>11} {'admite menor':>13}")
        for nm in nmins:
            h = [r for r in g if r["n_min"] == nm]
            if len(h) < 100:
                continue
            for pa in (False, True):
                for pb in (False, True):
                    s = [r for r in h if r["_perm_A"] == pa and r["_perm_B"] == pb]
                    if len(s) < 30:
                        continue
                    c = Counter(r["_clase2"] for r in s)
                    pct = lambda k: 100.0 * c.get(k, 0) / len(s)
                    print(f"    {nm:>6} {str(pa):>7} {str(pb):>7} {len(s):>9} "
                          f"{pct('identificada'):>8.1f}% {pct('mismo tamaño'):>10.1f}% "
                          f"{pct('admite menor'):>12.1f}%")
                    tabla[f"n{n}_nmin{nm}_A{int(pa)}_B{int(pb)}"] = dict(
                        sistemas=len(s), identificada=round(pct("identificada"), 2),
                        mismo_tamano=round(pct("mismo tamaño"), 2),
                        admite_menor=round(pct("admite menor"), 2))
        print()

    # --- el contraste directo que pide la pregunta
    print("CONTRASTE DIRECTO · identificados frente a «dos del mismo tamaño», a igual n y n_min\n")
    contraste = {}
    for n in sorted({r["n"] for r in filas}):
        for nm in sorted({r["n_min"] for r in filas if r["n"] == n}):
            h = [r for r in filas if r["n"] == n and r["n_min"] == nm]
            ident = [r for r in h if r["_clase2"] == "identificada"]
            mismo = [r for r in h if r["_clase2"] == "mismo tamaño"]
            if len(ident) < 50 or len(mismo) < 50:
                continue
            f1 = lambda s, k: 100.0 * sum(1 for r in s if r[k]) / len(s)
            prom = lambda s, k: sum(r[k] for r in s) / len(s)
            fila = dict(
                n=n, n_min=nm, identificados=len(ident), mismo_tamano=len(mismo),
                permA_ident=round(f1(ident, "_perm_A"), 1), permA_mismo=round(f1(mismo, "_perm_A"), 1),
                permB_ident=round(f1(ident, "_perm_B"), 1), permB_mismo=round(f1(mismo, "_perm_B"), 1),
                ciclos_ident=round(prom(ident, "_ciclos"), 3), ciclos_mismo=round(prom(mismo, "_ciclos"), 3),
                maxciclo_ident=round(prom(ident, "_maxciclo"), 2), maxciclo_mismo=round(prom(mismo, "_maxciclo"), 2))
            contraste[f"n{n}_nmin{nm}"] = fila
            print(f"  n={n} n_min={nm}  ({len(ident)} identificados, {len(mismo)} del mismo tamaño)")
            print(f"     A es permutación:  identificados {fila['permA_ident']:5.1f} %  "
                  f"mismo tamaño {fila['permA_mismo']:5.1f} %   -> {fila['permA_ident'] - fila['permA_mismo']:+6.1f} pts")
            print(f"     B es permutación:  identificados {fila['permB_ident']:5.1f} %  "
                  f"mismo tamaño {fila['permB_mismo']:5.1f} %   -> {fila['permB_ident'] - fila['permB_mismo']:+6.1f} pts")
            print(f"     fracción en ciclos: identificados {fila['ciclos_ident']:.3f}   "
                  f"mismo tamaño {fila['ciclos_mismo']:.3f}   -> {fila['ciclos_ident'] - fila['ciclos_mismo']:+.3f}")
            print(f"     ciclo más largo:    identificados {fila['maxciclo_ident']:.2f}    "
                  f"mismo tamaño {fila['maxciclo_mismo']:.2f}    -> {fila['maxciclo_ident'] - fila['maxciclo_mismo']:+.2f}")
            print()
    rep["por_permutacion"] = tabla
    rep["contraste"] = contraste
    rep["sistemas_leidos"] = len(filas)
    rep["sha256_codigo"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    rep["python"] = sys.version.split()[0]
    with open(os.path.join(aqui, "artifacts", "unidad_minima_05d_estructura.json"), "w",
              encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    return rep


if __name__ == "__main__":
    correr()
