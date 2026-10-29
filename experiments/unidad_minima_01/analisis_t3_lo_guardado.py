#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T3 · los dos análisis sobre lo guardado · piezas 4 y 6 de `ORIENTACIONES_TRABAJO_DESDE_EL_CORPUS.md`.

**Pieza 4 · la medida de Wolf, CONDICIONADA AL MUNDO.** La corrección de la revisión externa
es la que manda: medir I(W₁; conducta) **no** mide herencia, porque W₂ se genera desde W₁ y
la conducta de cualquier unidad en W₂ lleva información sobre W₁ aunque nunca lo haya vivido.
Lo que se mide es **I(historia; conducta en W₂ | W₂)**: para un mismo W₂, variar la historia
previa y ver cuánto dice la historia sobre la conducta. Fuente: Wolf et al. 2008, `HD-005`,
nivel `LC` (no leída aquí; el marco se usa por su forma, no se cita un resultado).

**Estimador, declarado.** La familia (W₁, patrón, clase) es la variable de condicionamiento.
Dentro de cada familia hay **una** observación por historia, así que H(C | W, H) = 0 y
I(H; C | W) = **H(C | W)**: la entropía de la conducta entre las historias de esa familia.
Es la forma honesta de decir «cuánto cambia la conducta cuando cambia la historia, con el
mundo fijo», y su techo es log₂(número de historias). **Dos historias disponibles en los
artefactos** —ninguna (F1) y vida en W₁ con el itinerario fijo (C1 en `08`, C5 en `09`)—, así
que el techo es **1 bit**; las otras tres historias de la pieza exigen una corrida corta.

**Conducta** (discretizada y declarada): identifica en el hito 64 · identifica en el 256 ·
repertorio al final. Y se cruza con la **exactitud**, que es lo que separa «retener
información» de «conservar una capacidad».

**Pieza 6 · Hartmanis: BLOQUEADA, con su arreglo en una línea.** Necesita la **máquina
aprendida** de cada celda para trasladar la congruencia generadora por el isomorfismo
canónico, y las filas de `08`, `09` y `10` **no la serializan** (las de `05` y `07` sí: es la
lección E-21, aplicada en la Fase 1 y no en la Fase 2). Sin la máquina no hay isomorfismo y
sin isomorfismo «aparece una congruencia» no dice nada, que es exactamente lo que el revisor
externo precisó. El arreglo es añadir `maquina=[[q, a, t[0], t[1]] ...]` a `medir` y volver a
correr `09` (249 s). Se declara y no se simula.
"""
from __future__ import annotations

import json
import math
import os
import sys
from collections import Counter, defaultdict

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from guardas import no_vacio  # noqa: E402


def cargar(ruta):
    with open(ruta, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip() and not l.startswith("#")]


def entropia(valores):
    n = len(valores)
    if n <= 1:
        return 0.0
    c = Counter(valores)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def conducta(f):
    """La conducta discretizada: lo que la unidad HACE, no lo que sabe."""
    c = f["curva"]
    g = lambda h: bool(c.get(str(h), c.get(h, {})).get("identifica"))
    rep = f.get("repertorio", f.get("escribe", 0) + f.get("permuta", 0))
    return (g(64), g(256), min(3, int(rep)))


def pieza4(ruta, pares, nombre, out):
    filas = cargar(ruta)
    no_vacio(filas, f"filas de {nombre}")
    por = defaultdict(dict)
    for f in filas:
        por[(f["clase"], f["w1"], f["patron"])][f["brazo"]] = f
    out.append(f"\n### {nombre} · I(historia; conducta en W₂ | W₂), techo 1 bit\n")
    out.append("| clase | historias comparadas | familias | **bits de historia** | "
               "exactitud sin historia | exactitud con historia | lectura |")
    out.append("|---|---|---|---|---|---|---|")
    R = {}
    for clase in ("componible", "no_componible"):
        for sin, con in pares:
            fams = [d for (cl, _, _), d in por.items()
                    if cl == clase and sin in d and con in d]
            if not fams:
                continue
            bits = sum(entropia([conducta(d[sin]), conducta(d[con])]) for d in fams) / len(fams)
            e_sin = sum(d[sin]["exactitud"] for d in fams) / len(fams)
            e_con = sum(d[con]["exactitud"] for d in fams) / len(fams)
            # TOLERANCIA DECLARADA: media unidad del último decimal que se informa.
            # Con 1e-9 la etiqueta «estorba» saltaba por una diferencia de exactitud de
            # 1e-5 entre dos columnas que se imprimen como 1,0000 las dos: una etiqueta que
            # distingue lo que la cifra publicada no distingue es una etiqueta falsa.
            TOL = 5e-4
            if bits < 0.01:
                lec = "la historia **no se nota** en la conducta"
            elif e_con > e_sin + TOL:
                lec = "información **útil**"
            elif e_con < e_sin - TOL:
                lec = "información que **estorba**"
            else:
                lec = "se nota en la conducta y **no cambia la exactitud**"
            R[f"{clase}|{sin}->{con}"] = dict(familias=len(fams), bits=bits,
                                              exactitud_sin=e_sin, exactitud_con=e_con,
                                              lectura=lec)
            out.append(f"| {clase} | {sin} → {con} | {len(fams)} | **{bits:.4f}** | "
                       f"{e_sin:.4f} | {e_con:.4f} | {lec} |")
    return R


def main():
    out = ["# T3 · lo que ya estaba guardado dice · 29-oct-2026", "",
           "Piezas 4 y 6 de `ORIENTACIONES_TRABAJO_DESDE_EL_CORPUS.md`, **con las "
           "correcciones de la revisión externa**. Análisis sobre artefactos existentes: "
           "ninguna corrida nueva."]
    out.append("\n## Pieza 4 · la medida de Wolf, condicionada al mundo")
    out.append("\n**Estimador declarado:** la familia es la variable de condicionamiento; con "
               "una observación por historia, I(H; C | W) = H(C | W), la entropía de la "
               "conducta entre las historias de esa familia. Techo **1 bit** porque los "
               "artefactos traen **dos** historias: ninguna (F1) y vida en W₁ con el "
               "itinerario fijo. Conducta = (identifica@64, identifica@256, repertorio).")
    R = {}
    R["08 (heredar la TRAZA)"] = pieza4(
        os.path.join(AQUI, "artifacts", "unidad_minima_08_fase2.jsonl"),
        [("F1", "C1"), ("F1", "C2")], "`08` · heredar la traza (prototipo exploratorio)", out)
    R["09 (heredar la MÁQUINA)"] = pieza4(
        os.path.join(AQUI, "artifacts", "unidad_minima_09_fase2.jsonl"),
        [("F1", "C5")], "`09` · heredar la máquina sin la traza (C5)", out)
    out.append("\n## Pieza 6 · la descomposición de Hartmanis · **BLOQUEADA**")
    out.append("\nNecesita la **máquina aprendida** de cada celda para trasladar la "
               "congruencia generadora de W₁ por el isomorfismo canónico. Las filas de `08`, "
               "`09` y `10` **no la serializan**; las de `05` y `07` sí —es la lección **E-21**, "
               "aplicada en la Fase 1 y no en la Fase 2—. Sin la máquina no hay isomorfismo, y "
               "sin isomorfismo «aparece una congruencia» no dice nada, que es justo lo que la "
               "revisión externa precisó. **Arreglo, en una línea:** añadir "
               "`maquina=[[q, a, t[0], t[1]] for (q, a), t in sorted(u.trans.items())]` a la "
               "fila y volver a correr `09` (249 s). No se simula ni se estima: se declara "
               "bloqueada y se deja el arreglo escrito.")
    texto = "\n".join(out) + "\n"
    with open(os.path.join(AQUI, "T3_LO_GUARDADO.md"), "w", encoding="utf-8") as f:
        f.write(texto)
    with open(os.path.join(AQUI, "artifacts", "analisis_t3.json"), "w", encoding="utf-8") as f:
        json.dump(dict(pieza4=R, pieza6="BLOQUEADA: las filas de 08/09/10 no serializan la "
                                        "máquina aprendida (E-21)", texto=texto),
                  f, ensure_ascii=False, indent=1)
        f.flush()
        os.fsync(f.fileno())
    sys.stdout.write(texto)


if __name__ == "__main__":
    main()
