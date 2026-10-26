#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UNIDAD-MINIMA-05e · ¿la no identificabilidad es transitoria o recurrente?

Un estado que la vida visita una o dos veces no da material para separarlo de
otro: no es que la unidad no lo distinga, es que no ha estado allí. Eso es una
no identificabilidad TRANSITORIA, y una vida más larga o mejor elegida podría
curarla. Un estado visitado muchas veces y aun así no separado es una no
identificabilidad RECURRENTE, y esa no la cura vivir más: es el límite de lo
que una sola vida no elegida puede saber.

Se calcula SIN volver a correr el aprendiz: la trayectoria del mundo sobre la
vida shortlex depende sólo de las tablas A y B, que sí están en la fila (E-20).
Por sistema: cuántos estados alcanzables son visitados <= 2 veces en la vida.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unidad_minima_05_banco import L_de, alcanzables, shortlex  # noqa: E402

UMBRAL = 2      # «transitorio» = visitado <= 2 veces en toda la vida


def visitas(A, B, acciones):
    """Trayectoria del mundo sobre la vida. Devuelve el conteo por estado."""
    c = Counter()
    x = 0
    for a in acciones:
        c[x] += 1
        x = A[x] if a == "A" else B[x]
    c[x] += 1
    return c


def correr(ns=(6, 8)):
    aqui = os.path.dirname(os.path.abspath(__file__))
    filas = []
    with open(os.path.join(aqui, "artifacts", "unidad_minima_05_banco.jsonl"),
              encoding="utf-8") as f:
        for linea in f:
            try:
                filas.append(json.loads(linea))
            except ValueError:
                pass
    # el prefijo canónico de n=8 y el tramo esparcido se tratan por separado
    objetivo8 = None
    rep = {"umbral_visitas": UMBRAL}
    for n in ns:
        g = [r for r in filas if r["n"] == n and r["n_min"] >= 2
             and not r.get("sin_terminar_por_reloj")]
        if not g:
            continue
        vida = shortlex(range(1, L_de(n) + 1))
        if n == 8:
            # El prefijo canónico son los RANGOS bajos del conjunto 1-de-k, no las primeras
            # filas del fichero: en orden esparcido los índices altos vienen entremezclados.
            # rango = idx // k, y el tramo canónico recorrió los rangos 0..6565.
            from unidad_minima_05_banco import K_DECLARADA
            k8 = K_DECLARADA[8]
            RANGO_PREFIJO = 6566
            prefijo = [r for r in g if r["idx"] // k8 < RANGO_PREFIJO]
            esparcido = [r for r in g if r["idx"] // k8 >= RANGO_PREFIJO]
            tramos = [("prefijo canónico", prefijo), ("tramo esparcido", esparcido)]
        else:
            tramos = [("completo", g)]
        for nombre, tramo in tramos:
            if not tramo:
                continue
            print(f"=== n={n} · {nombre} · {len(tramo)} sistemas con distinción "
                  f"(vida {len(vida)} pasos)")
            # una sola pasada: se calculan las visitas UNA vez por sistema
            marcados = []
            for r in tramo:
                A, B = tuple(r["A"]), tuple(r["B"])
                S = alcanzables(A, B)
                c = visitas(A, B, vida)
                trans = sum(1 for x in S if c[x] <= UMBRAL)
                clase = ("identificada" if r["igual_salvo_isomorfismo"] else
                         "mismo tamaño" if "mismo tamaño" in r["clase"] else
                         "admite menor" if "menor" in r["clase"] else "otra")
                marcados.append((r["n_min"], clase, trans, len(S)))
            acc = defaultdict(lambda: [0, 0, 0, 0])
            for nm, clase, trans, nS in marcados:
                d = acc[(nm, clase)]
                d[0] += 1
                d[1] += trans
                d[2] += nS
                d[3] += int(trans > 0)
            print(f"    {'n_min':>6} {'clase':<14} {'sistemas':>9} {'estados':>8} "
                  f"{'transitorios':>13} {'% transit.':>11} {'con >=1 trans.':>15}")
            det = {}
            for (nm, clase), (ns_, tr, es, conuno) in sorted(acc.items()):
                if ns_ < 30:
                    continue
                print(f"    {nm:>6} {clase:<14} {ns_:>9} {es / ns_:>8.2f} {tr / ns_:>13.3f} "
                      f"{100 * tr / es:>10.1f}% {100 * conuno / ns_:>14.1f}%")
                det[f"nmin{nm}_{clase}"] = dict(sistemas=ns_, estados_medios=round(es / ns_, 3),
                                                transitorios_medios=round(tr / ns_, 3),
                                                pct_transitorios=round(100 * tr / es, 2),
                                                pct_sistemas_con_transitorio=round(100 * conuno / ns_, 2))
            rep[f"n{n}_{nombre.replace(' ', '_')}"] = det
            print()
    rep["sha256_codigo"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    rep["python"] = sys.version.split()[0]
    with open(os.path.join(aqui, "artifacts", "unidad_minima_05e_transitorios.json"), "w",
              encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    return rep


if __name__ == "__main__":
    correr()
