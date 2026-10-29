#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""T1 · Las dos columnas del mundo caro, y el banco madre de la Fase 3.

E-53: «caro» mezclaba el coste del MUNDO con el coste del OLVIDO de esta unidad. Aquí van
las dos columnas separadas, con el MISMO criterio de éxito en las dos (isomorfismo con la
mínima verdadera), y el banco madre se elige **por el mundo**.

Fuentes, y por qué cada una:
- **n=8 · columna del mundo:** las **5 000 filas limpias de la Fase 1** (`07`), que traen el
  identificador exacto —unidad de 02, sin ventana y sin olvido— con `ultimo_error` e
  `igual_salvo_isomorfismo`. Es cobertura **completa** de la muestra limpia, mejor que la
  submuestra de `12`, así que el banco madre sale de aquí y no necesita `12`.
- **n=8 · columna del olvido:** las filas de `12` que haya (su corrida con la columna nueva
  sigue en marcha; lo que falte se dice). Las 2 807 filas de la corrida anterior **se
  perdieron** al relanzar sobre su propio fichero: E-54, con su guarda ya puesta.
- **n=6:** `12` trae las dos columnas nativas (el banco limpio de la Fase 1 para n=6 usó el
  paso con retículo de E-27, así que sus índices no cruzan con los nuestros y no se usa).
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import Counter

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, AQUI)
from guardas import no_vacio  # noqa: E402

UMBRAL = 256
N_MIN = 4


def cargar(ruta):
    with open(ruta, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip() and not l.startswith("#")]


def caro_por_el_mundo_07(c):
    """El criterio FUERTE sobre la fila limpia de la Fase 1: o el identificador exacto no
    llegó a la mínima verdadera, o llegó y le costó más de 256 pasos."""
    resuelto = (c["clase"] == "identificada" and c["igual_salvo_isomorfismo"]
                and not c["tope_tocado"])
    if not resuelto:
        return True, None, ("tope_de_estados" if c["tope_tocado"] else "maquina_distinta")
    return (c["ultimo_error"] + 1) > UMBRAL, c["ultimo_error"] + 1, "isomorfa"


def tabla(nombre, filas, out):
    """La 2×2 por n_min: caro por el mundo × caro para esta unidad."""
    out.append(f"\n### {nombre} · {len(filas)} mundos con n_min >= {N_MIN}\n")
    out.append("| n_min | mundos | caro mundo ∧ caro unidad | caro mundo, unidad no | "
               "**sólo olvido** | ninguno | **banco madre** |")
    out.append("|---|---|---|---|---|---|---|")
    tot = Counter()
    for nm in sorted({f["n_min"] for f in filas}):
        g = [f for f in filas if f["n_min"] == nm]
        c = Counter((f["caro_mundo"], f["caro_unidad"]) for f in g)
        bm = sum(1 for f in g if f["banco_madre"])
        tot.update(c)
        tot["banco"] += bm
        out.append(f"| {nm} | {len(g)} | {c[(True, True)]} | {c[(True, False)]} | "
                   f"**{c[(False, True)]}** | {c[(False, False)]} | **{bm}** |")
    out.append(f"| **todos** | **{len(filas)}** | {tot[(True, True)]} | {tot[(True, False)]} | "
               f"**{tot[(False, True)]}** | {tot[(False, False)]} | **{tot['banco']}** |")
    caros_u = tot[(True, True)] + tot[(False, True)]
    solo_olv = tot[(False, True)]
    if caros_u:
        out.append(f"\n**De lo caro para esta unidad, el {100*solo_olv/caros_u:.1f} % lo es "
                   f"sólo por su olvido y no por el mundo** ({solo_olv} de {caros_u}).")
    olv_c = [f["olvidos"] for f in filas if f["caro_unidad"] and f["olvidos"] is not None]
    olv_b = [f["olvidos"] for f in filas if not f["caro_unidad"] and f["olvidos"] is not None]
    if olv_c and olv_b:
        a, b = sum(olv_c)/len(olv_c), sum(olv_b)/len(olv_b)
        out.append(f"Olvidos por vida: **{a:.1f}** en los caros para la unidad contra "
                   f"**{b:.1f}** en los baratos"
                   f"{' — más de un orden de magnitud: la etiqueta mide el instrumento (E-53)' if a > 10*max(b,1e-9) else ''}.")
    return tot


def main():
    out = ["# T1 · las dos columnas del mundo caro y el banco madre · 29-oct-2026", ""]
    bancos = {}

    # ---------- n=8 ----------
    limpias = {r["idx"]: r for r in cargar(os.path.join(AQUI, "artifacts",
                                                        "unidad_minima_07_n8_limpio.jsonl"))}
    no_vacio(limpias, "filas limpias de n=8 de la Fase 1")
    doce8 = {r["idx"]: r for r in cargar(os.path.join(AQUI, "artifacts",
                                                      "unidad_minima_12_mundo_caro_n8.jsonl"))
             if "coste_barato" in r}
    f8 = []
    for idx, c in limpias.items():
        if c["n_min"] < N_MIN:
            continue
        cm, coste, motivo = caro_por_el_mundo_07(c)
        d = doce8.get(idx)
        f8.append(dict(idx=idx, n=8, n_min=c["n_min"], caro_mundo=cm, coste_mundo=coste,
                       motivo=motivo,
                       caro_unidad=(bool(d["caro"]) if d else None),
                       olvidos=(d["olvidos"] if d else None),
                       banco_madre=bool(motivo == "isomorfa" and coste and coste > UMBRAL)))
    con_u = [f for f in f8 if f["caro_unidad"] is not None]
    out.append(f"**n=8** · columna del mundo sobre las **{len(f8)}** filas limpias de la Fase 1 "
               f"con n_min >= {N_MIN} (de 5 000); columna del olvido sobre las **{len(con_u)}** "
               f"que `12` ha medido hasta ahora con su corrida en marcha.")
    out.append(f"\nPor qué el identificador exacto no resuelve un mundo: "
               f"{dict(sorted(Counter(f['motivo'] for f in f8).items()))}")
    if con_u:
        tabla("n=8 · intersección con lo ya medido por `12`", con_u, out)
    bm8 = [f for f in f8 if f["banco_madre"]]
    cs = sorted(f["coste_mundo"] for f in bm8)
    out.append(f"\n## Banco madre de n=8 · **{len(bm8)} mundos**")
    if cs:
        out.append(f"Coste intrínseco: mediana **{cs[len(cs)//2]}** · p90 "
                   f"**{cs[int(.9*len(cs))]}** · máximo **{cs[-1]}** pasos. "
                   f"n_min: {dict(sorted(Counter(f['n_min'] for f in bm8).items()))}")
    bancos[8] = bm8

    # ---------- n=6 ----------
    r6 = [r for r in cargar(os.path.join(AQUI, "artifacts",
                                         "unidad_minima_12_mundo_caro_n6.jsonl"))
          if "coste_mundo" in r]
    f6 = [dict(idx=r["idx"], n=6, n_min=r["n_min"], caro_mundo=bool(r["caro_por_el_mundo"]),
               coste_mundo=r["coste_mundo"], motivo=r["mundo_motivo"],
               caro_unidad=bool(r["caro"]), olvidos=r["olvidos"],
               banco_madre=bool(r["banco_madre"])) for r in r6]
    if f6:
        out.append(f"\n**n=6** · las dos columnas nativas de `12` sobre **{len(f6)}** mundos "
                   f"con n_min >= {N_MIN}.")
        out.append(f"\nPor qué el identificador exacto no resuelve un mundo: "
                   f"{dict(sorted(Counter(f['motivo'] for f in f6).items()))}")
        tabla("n=6", f6, out)
        bm6 = [f for f in f6 if f["banco_madre"]]
        cs6 = sorted(f["coste_mundo"] for f in bm6)
        out.append(f"\n## Banco madre de n=6 · **{len(bm6)} mundos**")
        if cs6:
            out.append(f"Coste intrínseco: mediana **{cs6[len(cs6)//2]}** · máximo "
                       f"**{cs6[-1]}**. n_min: {dict(sorted(Counter(f['n_min'] for f in bm6).items()))}")
        bancos[6] = bm6

    # ---------- el artefacto del banco, con hash ----------
    banco = dict(
        criterio=dict(umbral_coste=UMBRAL, n_min_minimo=N_MIN,
                      regla="el identificador EXACTO (unidad de 02, sin ventana ni olvido) "
                            "alcanza la mínima verdadera salvo isomorfismo Y le cuesta más de "
                            f"{UMBRAL} pasos",
                      excluido="lo caro sólo por el olvido de la unidad de 08 no entra: es "
                               "defecto de disposición y va a T2 (E-53)"),
        fuentes=dict(n8="artifacts/unidad_minima_07_n8_limpio.jsonl (5 000 filas limpias)",
                     n6="artifacts/unidad_minima_12_mundo_caro_n6.jsonl (columna nativa)"),
        bancos={str(n): dict(mundos=len(v), indices=[f["idx"] for f in v],
                             n_min={str(k): c for k, c in
                                    sorted(Counter(f["n_min"] for f in v).items())},
                             coste_intrinseco=[f["coste_mundo"] for f in v])
                for n, v in bancos.items()},
        exploratorio=False)
    cuerpo = json.dumps(banco, ensure_ascii=False, indent=1, sort_keys=True)
    banco["sha256_del_contenido"] = hashlib.sha256(cuerpo.encode()).hexdigest()
    ruta = os.path.join(AQUI, "artifacts", "banco_madre.json")
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(banco, f, ensure_ascii=False, indent=1, sort_keys=True)
        f.flush()
        os.fsync(f.fileno())
    out.append(f"\n**Artefacto:** `artifacts/banco_madre.json` · sha256 del contenido "
               f"`{banco['sha256_del_contenido'][:16]}…` (calculado del propio objeto que se "
               f"escribió, no de la terminal: E-40).")
    texto = "\n".join(out) + "\n"
    with open(os.path.join(AQUI, "T1_BANCO_MADRE.md"), "w", encoding="utf-8") as f:
        f.write(texto)
    sys.stdout.write(texto)


if __name__ == "__main__":
    main()
