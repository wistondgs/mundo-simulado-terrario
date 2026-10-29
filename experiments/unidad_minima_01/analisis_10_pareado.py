#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Análisis pareado de la campaña del maestro, sobre las filas que ella escribió.

POR QUÉ ESTO EXISTE, Y ES UN DEFECTO DEL RESUMEN DE `10` (E-50). Las celdas U1 y U2 no
corren sobre todas las familias: U1 sólo donde la maestra de vida completa identificó W₂,
U2 sólo donde la de 64 pasos **no** identificó. Comparar la media de U2 contra la media de
F1 sobre **todo** el banco mezcla el efecto del maestro con la dificultad del subconjunto:
las familias de U2 son, por construcción, las que al primer hito se resisten. La
comparación válida es **pareada**: para cada celda, F1 restringido a las mismas familias.

Esto se calcula aquí, leyendo el `.jsonl` que la corrida escribió, sin volver a correr nada
y sin tocar el módulo mientras su campaña está en marcha (E-49).
"""
from __future__ import annotations

import json
import os
import sys
from collections import defaultdict
from statistics import NormalDist

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from guardas import no_vacio  # noqa: E402

ALFA = 0.05
HITOS = (64, 128, 256, 512, 1024, 2048)


def cargar(ruta):
    with open(ruta, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def mcnemar(b, c):
    """Prueba pareada exacta en su forma normal: b = sólo la celda, c = sólo F1.
    Devuelve z con corrección de continuidad; 0 si no hay discordantes."""
    n = b + c
    if n == 0:
        return 0.0
    return (abs(b - c) - 1) / (n ** 0.5) if abs(b - c) >= 1 else 0.0


def main(ruta):
    filas = cargar(ruta)
    no_vacio(filas, "filas de la campaña del maestro")
    por = defaultdict(dict)
    for f in filas:
        por[(f["clase"], f["w1"], f["patron"])][f["celda"]] = f
    celdas = sorted({f["celda"] for f in filas})
    clases = sorted({f["clase"] for f in filas})
    comparaciones = [(cl, c, h) for cl in clases for c in celdas if c != "F1" for h in HITOS]
    z_umbral = NormalDist().inv_cdf(1 - ALFA / (2 * max(1, len(comparaciones))))
    print(f"filas {len(filas)} · familias {len(por)} · celdas {', '.join(celdas)}")
    print(f"umbral de z, Bonferroni sobre {len(comparaciones)} comparaciones: {z_umbral:.2f}\n")
    R = {}
    for cl in clases:
        print(f"=== clase {cl} · comparación PAREADA contra F1 (sólo familias donde corren las dos)")
        print(f"{'celda':<20}{'hito':>6}{'fam.':>6}{'celda':>8}{'F1':>8}{'Δ':>8}"
              f"{'sólo celda':>11}{'sólo F1':>8}{'z pareado':>10}{'':>4}")
        for c in celdas:
            if c == "F1":
                continue
            for h in HITOS:
                comunes = [d for (k_cl, _, _), d in por.items()
                           if k_cl == cl and c in d and "F1" in d
                           and str(h) in d[c]["curva"] and str(h) in d["F1"]["curva"]]
                if not comunes:
                    continue
                ic = sum(bool(d[c]["curva"][str(h)]["identifica"]) for d in comunes)
                i1 = sum(bool(d["F1"]["curva"][str(h)]["identifica"]) for d in comunes)
                b = sum(1 for d in comunes if d[c]["curva"][str(h)]["identifica"]
                        and not d["F1"]["curva"][str(h)]["identifica"])
                cc = sum(1 for d in comunes if d["F1"]["curva"][str(h)]["identifica"]
                         and not d[c]["curva"][str(h)]["identifica"])
                n = len(comunes)
                z = mcnemar(b, cc)
                marca = "  ***" if z > z_umbral else ""
                R[f"{cl}|{c}|{h}"] = dict(familias=n, celda=ic / n, f1=i1 / n,
                                          solo_celda=b, solo_f1=cc, z=z,
                                          supera=(b > cc and z > z_umbral))
                print(f"{c:<20}{h:>6}{n:>6}{ic / n:>8.3f}{i1 / n:>8.3f}{(ic - i1) / n:>+8.3f}"
                      f"{b:>11}{cc:>8}{z:>10.2f}{marca}")
        print()
    return R, z_umbral


if __name__ == "__main__":
    ruta = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        AQUI, "artifacts", "unidad_minima_10_maestro.jsonl")
    R, u = main(ruta)
    with open(os.path.join(AQUI, "artifacts", "analisis_10_pareado.json"), "w",
              encoding="utf-8") as f:
        json.dump(dict(pareado=R, z_umbral=u), f, ensure_ascii=False, indent=1)
        f.flush()
        os.fsync(f.fileno())
