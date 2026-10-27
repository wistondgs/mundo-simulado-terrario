#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Punto de entrada idempotente de n=8 limpio. Se puede ejecutar cien veces seguidas.

POR QUÉ EXISTE (E-31). Un corte de luz se llevó el guion que encadenaba los pasos, porque
vivía en el temporal de la sesión, y con él el paso que debía escribir los mutantes en la
ficha. La receta de recuperación tiene que ser UNA línea que siempre es la misma, y el
estado tiene que estar en el árbol, no en un proceso vivo.

Lee el estado del árbol, decide qué falta y hace lo siguiente. Nada más.

    paso 1 · mutantes          -> artifacts/pruebas/mutantes_n8_limpio.txt
    paso 2 · mutantes a ficha  -> marca en APERTURA_N8_MUESTRA_LIMPIA.md
    paso 3 · corrida real      -> artifacts/unidad_minima_07_n8_limpio.jsonl (reanudable)
    paso 4 · digest            -> artifacts/digest_n8.json (lo que lee el vigilante)
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import time

AQUI = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(AQUI, "artifacts")
PRUEBAS = os.path.join(ART, "pruebas")
MUT = os.path.join(PRUEBAS, "mutantes_n8_limpio.txt")
FICHA = os.path.join(AQUI, "APERTURA_N8_MUESTRA_LIMPIA.md")
JSONL = os.path.join(ART, "unidad_minima_07_n8_limpio.jsonl")
DIGEST = os.path.join(ART, "digest_n8.json")
MARCA_FICHA = "### Resultado de los mutantes · escrito por el orquestador"
TOPE = 5000

sys.path.insert(0, AQUI)


def _py(*args):
    return subprocess.run([sys.executable, "-u", *args], cwd=AQUI).returncode


def mutantes_hechos():
    return os.path.exists(MUT) and "EL GATE SIRVE" in open(MUT, encoding="utf-8").read()


def mutantes_rotos():
    return os.path.exists(MUT) and "ESTÁ ROTO" in open(MUT, encoding="utf-8").read()


def mutantes_en_ficha():
    return MARCA_FICHA in open(FICHA, encoding="utf-8").read()


def filas():
    if not os.path.exists(JSONL):
        return []
    out = []
    with open(JSONL, encoding="utf-8") as f:
        for linea in f:
            try:
                out.append(json.loads(linea))
            except ValueError:
                pass
    return out


def escribir_digest(fs):
    """Lo que el vigilante lee: pequeño, suficiente para juzgar, barato de producir."""
    vivos = [r for r in fs if not r.get("sin_terminar_por_reloj")]
    cd = [r for r in fs if r.get("n_min", 0) >= 2]
    por_nmin = {}
    for nm in sorted({r["n_min"] for r in cd}):
        h = [r for r in cd if r["n_min"] == nm]
        if len(h) >= 20:
            por_nmin[str(nm)] = dict(
                sistemas=len(h),
                identif=round(100 * sum(1 for r in h if r["igual_salvo_isomorfismo"]) / len(h), 1))
    w = sorted((r["trabajo"] / r["vida_len"]) for r in vivos if r.get("trabajo"))
    q = lambda p: round(w[min(len(w) - 1, int(p * len(w)))], 2) if w else None
    d = dict(
        actualizado=time.strftime("%Y-%m-%dT%H:%M:%S"),
        experimento="n=8 muestra limpia",
        medidos=len(fs), objetivo=TOPE,
        pct=round(100 * len(fs) / TOPE, 1),
        cortados_por_reloj=sum(1 for r in fs if r.get("sin_terminar_por_reloj")),
        identificacion_por_nmin=por_nmin,
        trabajo_sobre_vida=dict(p50=q(.5), p90=q(.9), p99=q(.99),
                                max=round(w[-1], 1) if w else None),
        refutaciones_totales=sum(r.get("refutaciones") or 0 for r in vivos),
        transit_rel_pct=round(100 * sum(r.get("transit_rel", 0) for r in vivos)
                              / max(1, sum(r.get("alcanzables", 0) for r in vivos)), 2) if vivos else None,
        mutantes_ok=mutantes_hechos(), mutantes_rotos=mutantes_rotos(),
        mutantes_en_ficha=mutantes_en_ficha(),
        proceso_vivo=None,   # lo rellena el vigilante; aquí no se sabe
    )
    os.makedirs(ART, exist_ok=True)
    json.dump(d, open(DIGEST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    return d


CERROJO = os.path.join(ART, "orquestar_n8.lock")


def tomar_cerrojo():
    """Idempotente de verdad: si ya hay una instancia trabajando, ésta se retira sin
    hacer nada. Sin esto, un systemd con Restart lanzaría dos campañas a la vez."""
    os.makedirs(ART, exist_ok=True)
    if os.path.exists(CERROJO):
        try:
            viejo = int(open(CERROJO).read().strip())
        except (ValueError, OSError):
            viejo = None
        if viejo:
            try:
                os.kill(viejo, 0)
            except ProcessLookupError:
                pass            # el cerrojo quedó huérfano de un corte: se reclama
            except PermissionError:
                return False
            else:
                return False    # hay una instancia viva
    open(CERROJO, "w").write(str(os.getpid()))
    return True


def soltar_cerrojo():
    try:
        if os.path.exists(CERROJO) and int(open(CERROJO).read().strip()) == os.getpid():
            os.remove(CERROJO)
    except (ValueError, OSError):
        pass


def main():
    os.makedirs(PRUEBAS, exist_ok=True)
    if not tomar_cerrojo():
        print("ya hay una instancia trabajando; esta se retira sin hacer nada")
        return 0

    # paso 1 · mutantes, si no están
    if not mutantes_hechos():
        if mutantes_rotos():
            print("ALTO: los mutantes están en ROJO. No se corre lo real. "
                  "Revisar artifacts/pruebas/mutantes_n8_limpio.txt")
            return 1
        print("paso 1 · mutantes (no están hechos)")
        with open(MUT, "a", encoding="utf-8") as f:
            f.write(f"\n# reintento del orquestador · {time.strftime('%Y-%m-%dT%H:%M:%S')}\n")
        r = subprocess.run([sys.executable, "-u", "unidad_minima_07_n8_limpio.py", "mutantes"],
                           cwd=AQUI, stdout=open(MUT, "a", encoding="utf-8"),
                           stderr=subprocess.STDOUT)
        if not mutantes_hechos():
            print("los mutantes no dejaron el gate en verde; no se sigue")
            return r.returncode or 1

    # paso 2 · los mutantes van a la ficha EN CUANTO pasan, no al final de todo
    if not mutantes_en_ficha():
        print("paso 2 · escribiendo los mutantes en la ficha")
        texto = open(MUT, encoding="utf-8").read()
        cuerpo = [l for l in texto.splitlines() if not l.startswith("    capacidad")]
        with open(FICHA, "a", encoding="utf-8") as f:
            f.write(f"\n{MARCA_FICHA} · {time.strftime('%Y-%m-%d %H:%M')}\n\n")
            f.write("Corridos y escritos aquí **antes** de medir, con la salida en el árbol "
                    "y no en un temporal (E-31):\n\n```\n")
            f.write("\n".join(cuerpo[-40:]) + "\n```\n")

    # paso 3 · corrida real, reanudable: 07 salta lo ya hecho por `rango`
    fs = filas()
    if len(fs) < TOPE:
        print(f"paso 3 · corrida real ({len(fs)}/{TOPE} hechos)")
        escribir_digest(fs)
        _py("unidad_minima_07_n8_limpio.py", "correr")
        fs = filas()

    # paso 4 · digest siempre al día
    d = escribir_digest(fs)
    print(f"paso 4 · digest: {d['medidos']}/{TOPE} ({d['pct']} %), "
          f"cortados {d['cortados_por_reloj']}")
    if len(fs) >= TOPE:
        print("n=8 limpio: COMPLETO")
    return 0


def _main_con_cerrojo():
    try:
        return main()
    finally:
        soltar_cerrojo()


if __name__ == "__main__":
    sys.exit(_main_con_cerrojo())
