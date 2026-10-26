#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UNIDAD-MINIMA-05b · corredor paralelo del banco. NO es una medida: es un reloj.

Cada sistema del banco se calcula sólo desde (n, idx), sin estado compartido y de
forma determinista, así que repartirlos entre procesos no puede cambiar ninguna
cifra: sólo el orden en que las filas caen al JSONL.

Este fichero **no reimplementa nada**. Importa `un_sistema` de
`unidad_minima_05_banco` y la llama tal cual, de modo que «paralelizar no cambió
la medida» no es una afirmación: la función que mide es literalmente el mismo
objeto. Por eso el corredor vive aparte y 05 no se toca.

Decisiones declaradas (orientaciones del 25-oct, §2):
  - 4 trabajadores, no 6: con un solo hilo el paquete ya está a 92 °C de 100, y
    con seis el portátil estrangula y puede ir más lento.
  - un solo escritor: los trabajadores devuelven la fila y el proceso padre la
    añade al JSONL y la vuelca en el momento, para que la corrida se reanude.
  - olas de tamaño fijo con `as_completed`: se escribe cada fila en cuanto llega,
    así un sistema de 182 s no bloquea la custodia de los que ya terminaron. El
    orden del fichero deja de ser canónico; el resumen y el hash se calculan
    SIEMPRE sobre las filas ordenadas por (n, idx).
  - PROHIBIDO un tope de tiempo por sistema: descartar los lentos sería
    seleccionar contra la cola, y la cola es parte de la respuesta de la fase.

Uso:
  python3 unidad_minima_05b_paralelo.py verificar       # prueba de identidad
  python3 unidad_minima_05b_paralelo.py correr 6 8      # reanuda y completa
"""
from __future__ import annotations

import json
import os
import sys
import time
import itertools
import signal
from collections import Counter
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unidad_minima_05_banco import (  # noqa: E402
    FUTURO_MAX, K_DECLARADA, L_de, NS, alcanzables, indices, mealy_verdadera, minimizar,
    puerta, resumen, shortlex, sistema_por_indice, un_sistema,
)

TRABAJADORES = 4
EN_VUELO = TRABAJADORES * 8   # ventana de futuros pendientes: el pool nunca se queda vacío
CAMPO_RELOJ = "reloj_s"       # el único campo no determinista: es reloj de pared

# --- Topes declarados el 2026-10-25 ANTES de aplicarlos (ficha, «Topes de reloj»).
# Son logística, no ciencia, y por eso se declaran con su coste epistémico:
#   TOPE_SISTEMA_S: corta UN sistema y lo registra en la clase «sin terminar por reloj»,
#                   que cuenta en el denominador como no identificado. Introduce la única
#                   clasificación NO determinista de la campaña, y por eso los índices
#                   afectados se listan: una corrida posterior los puede acabar sin tope.
#   TOPE_SESION_S:  deja de ENVIAR sistemas nuevos; los en vuelo terminan. Los que no se
#                   enviaron no se clasifican: quedan sin medir y la muestra pasa a ser un
#                   PREFIJO del orden canónico, lo que sesga y hay que advertirlo en todo
#                   número que salga de ella.
TOPE_SISTEMA_S = 900
TOPE_SESION_S = 4 * 3600

# --- Recorrido esparcido (declarado el 2026-10-25). NO cambia la muestra ni la medida:
# el conjunto 1-de-k es el mismo y `un_sistema` es el mismo; cambia sólo EN QUÉ ORDEN se
# recorren los pendientes. Motivo medido: el prefijo del orden canónico está sesgado
# 17–28 puntos de identificación A IGUAL n_min respecto de los otros dos tercios (n=4 y
# n=6 completos, medido por tercios). Con permutación por inversión de bits del rango,
# cualquier prefijo de lo recorrido es una muestra aproximadamente uniforme del conjunto.
BLOQUE_E18 = 1000      # tamaño de bloque del criterio de parada por información (E-18)
ESTRATO_MIN = 50       # estratos con menos de esto no entran en la comparación
DELTA_E18 = 3.0        # puntos porcentuales


def orden_esparcido(M):
    """Rangos 0..M-1 en orden de inversión de bits: determinista, sin azar, y esparce
    cualquier prefijo sobre todo el rango. Depende sólo de M, no de qué haya hecho ya."""
    b = max(1, (M - 1).bit_length())
    for j in range(1 << b):
        r = int(format(j, f"0{b}b")[::-1], 2)
        if r < M:
            yield r

_CACHE = {}


def _vida_y_futuro(n):
    if n not in _CACHE:
        L = L_de(n)
        _CACHE[n] = (shortlex(range(1, L + 1)), shortlex([L + 1])[:FUTURO_MAX])
    return _CACHE[n]


def _alarma(sig, frame):
    raise TimeoutError()


def trabajo(par):
    """Lo que corre en el trabajador: exactamente `un_sistema` de 05, sin cambios. El tope
    por sistema es un reloj de guardia alrededor, no una modificación de la medida."""
    n, idx, tope, vida_len = par
    vida, futuro = _vida_y_futuro(n)
    if tope:
        signal.signal(signal.SIGALRM, _alarma)
        signal.setitimer(signal.ITIMER_REAL, tope)
    try:
        return un_sistema(n, idx, vida, futuro, n <= 4)
    except TimeoutError:
        return fila_cortada(n, idx, vida_len, tope)
    finally:
        if tope:
            signal.setitimer(signal.ITIMER_REAL, 0)


def filas_de(jsonl, n=None):
    if not os.path.exists(jsonl):
        return []
    out = []
    with open(jsonl, encoding="utf-8") as f:
        for linea in f:
            try:
                d = json.loads(linea)
            except ValueError:
                continue
            if n is None or d.get("n") == n:
                out.append(d)
    return out


def ordenadas(jsonl):
    """Las filas por (n, idx). El orden del fichero es incidental; éste no."""
    return sorted(filas_de(jsonl), key=lambda r: (r["n"], r["idx"]))


def fila_cortada(n, idx, vida_len, tope):
    """La fila de un sistema cortado por reloj. Lleva n_min —que es barato y no depende
    del aprendiz— para que cuente en el denominador, e `igual_salvo_isomorfismo` en
    falso, porque no identificó."""
    A, B = sistema_por_indice(n, idx)
    est = alcanzables(A, B)
    n_min, _ = minimizar(mealy_verdadera(A, B, est), est)
    return dict(n=n, idx=idx, A=list(A), B=list(B), alcanzables=len(est), n_min=n_min,
                estados_aprendidos=None, igual_salvo_isomorfismo=False,
                errores=None, ultimo_error=None, sin_ruta=None, tope_tocado=False,
                refutaciones=None, distinciones=0, retrocedidos=None, retroceso_max=None,
                trabajo=None, futuro=None, futuro_sin_ruta=None, futuro_decidio=None,
                vida_len=vida_len, reloj_s=None,
                clase=f"sin terminar por reloj ({tope} s)", sin_terminar_por_reloj=True)


def _stats_bloque(bloque):
    """Identificación por n_min y proporción de clases, de un bloque de filas."""
    por_nmin = {}
    for r in bloque:
        if r["n_min"] < 2:
            continue
        d = por_nmin.setdefault(r["n_min"], [0, 0])
        d[1] += 1
        d[0] += int(bool(r["igual_salvo_isomorfismo"]))
    ident = {k: (100.0 * v[0] / v[1], v[1]) for k, v in por_nmin.items()}
    cl = Counter(r["clase"].split(":")[0] for r in bloque)
    tot = max(1, len(bloque))
    clases = {k: 100.0 * v / tot for k, v in cl.items()}
    return ident, clases


def _estable(a, b):
    """¿Dos bloques consecutivos difieren menos de DELTA_E18 puntos en todos los estratos
    con más de ESTRATO_MIN sistemas, y en las proporciones de clase? (E-18)"""
    if a is None or b is None:
        return False, "primer bloque"
    ia, ca = a
    ib, cb = b
    comunes = [k for k in set(ia) & set(ib) if ia[k][1] > ESTRATO_MIN and ib[k][1] > ESTRATO_MIN]
    if not comunes:
        return False, "ningún estrato con suficientes sistemas"
    peor_n, peor_v = None, 0.0
    for k in comunes:
        d = abs(ia[k][0] - ib[k][0])
        if d > peor_v:
            peor_n, peor_v = f"n_min={k}", d
    for k in set(ca) | set(cb):
        d = abs(ca.get(k, 0.0) - cb.get(k, 0.0))
        if d > peor_v:
            peor_n, peor_v = f"clase «{k}»", d
    return peor_v < DELTA_E18, f"peor diferencia {peor_v:.1f} pts en {peor_n}"


def correr(n, jsonl, out, trabajadores=TRABAJADORES, tope=TOPE_SISTEMA_S,
           tope_sesion=TOPE_SESION_S, esparcido=True, parar_por_informacion=True):
    """Alimenta el pool de forma CONTINUA con una ventana fija que se rellena en cuanto
    uno termina. Recorre los pendientes en orden esparcido (inversión de bits del rango),
    y puede detenerse solo cuando deja de aprender (E-18)."""
    k = K_DECLARADA[n]
    hechos = {r["idx"] for r in filas_de(jsonl, n)}
    objetivo = list(indices(n, k))
    if esparcido:
        pend = [objetivo[r] for r in orden_esparcido(len(objetivo)) if objetivo[r] not in hechos]
    else:
        pend = [i for i in objetivo if i not in hechos]
    vida, _ = _vida_y_futuro(n)
    out.write(f"n={n}: {len(objetivo)} a medir (1 de cada {k}), {len(hechos)} ya hechos, "
              f"{len(pend)} pendientes · orden {'ESPARCIDO (inversión de bits)' if esparcido else 'canónico'}"
              f" · {trabajadores} trabajadores, ventana {EN_VUELO}"
              f" · tope por sistema {tope} s · tope de sesión {tope_sesion / 3600:.1f} h"
              f" · parada por información {'sí' if parar_por_informacion else 'no'} "
              f"(bloques de {BLOQUE_E18}, {DELTA_E18} pts, estratos > {ESTRATO_MIN})\n")
    out.flush()
    t0 = time.perf_counter()
    it = iter(pend)
    escritas = cortados = 0
    bloque, prev_stats, motivo_parada = [], None, None
    with ProcessPoolExecutor(max_workers=trabajadores) as ex, \
            open(jsonl, "a", encoding="utf-8") as f:
        vuelo = {}
        for i in itertools.islice(it, EN_VUELO):
            vuelo[ex.submit(trabajo, (n, i, tope, len(vida)))] = i
        while vuelo:
            hechas, _ = wait(list(vuelo), return_when=FIRST_COMPLETED)
            for fut in hechas:
                vuelo.pop(fut)
                if fut.cancelled():
                    continue
                fila = fut.result()
                if fila.get("sin_terminar_por_reloj"):
                    cortados += 1
                f.write(json.dumps(fila, ensure_ascii=False) + "\n")
                f.flush()
                escritas += 1
                bloque.append(fila)
                el = time.perf_counter() - t0

                if len(bloque) >= BLOQUE_E18:
                    stats = _stats_bloque(bloque)
                    est, detalle = _estable(prev_stats, stats)
                    out.write(f"  n={n}: bloque de {len(bloque)} · {escritas}/{len(pend)} en "
                              f"{el / 60:.1f} min · cortados {cortados} · E-18: {detalle}"
                              f"{' -> ESTABLE' if est else ''}\n")
                    out.flush()
                    prev_stats, bloque = stats, []
                    if parar_por_informacion and est:
                        motivo_parada = f"parada por información (E-18): {detalle}"
                        break

                if tope_sesion is not None and el > tope_sesion:
                    motivo_parada = f"tope de sesión ({tope_sesion / 3600:.1f} h)"
                    break

                siguiente = next(it, None)
                if siguiente is not None:
                    vuelo[ex.submit(trabajo, (n, siguiente, tope, len(vida)))] = siguiente

            if motivo_parada:
                # cancelar lo encolado y no empezado, para que la parada sea limpia y no
                # arrastre un drenaje de hasta 32/4 x 900 s
                canceladas = sum(1 for fut in list(vuelo) if fut.cancel())
                out.write(f"  n={n}: {motivo_parada} · canceladas {canceladas} encoladas sin "
                          f"empezar · se espera a las que ya corrían\n")
                out.flush()
                for fut in list(vuelo):
                    if fut.cancelled():
                        vuelo.pop(fut, None)
                        continue
                    try:
                        fila = fut.result()
                    except Exception:
                        vuelo.pop(fut, None)
                        continue
                    if fila.get("sin_terminar_por_reloj"):
                        cortados += 1
                    f.write(json.dumps(fila, ensure_ascii=False) + "\n")
                    f.flush()
                    escritas += 1
                    vuelo.pop(fut, None)
                break
    sobrantes = len(pend) - escritas
    out.write(f"  n={n}: tramo terminado · {escritas} medidos · {cortados} cortados por reloj "
              f"· {sobrantes} sin medir · motivo: {motivo_parada or 'se acabaron los pendientes'}\n")
    if sobrantes:
        out.write(f"  AVISO: la muestra de n={n} queda incompleta ({escritas + len(hechos)} de "
                  f"{len(objetivo)}). Lo recorrido en orden ESPARCIDO es aproximadamente "
                  f"uniforme; el prefijo canónico previo NO lo es y se informa como estrato "
                  f"aparte. Toda cifra de este n lleva esa advertencia.\n")
    out.flush()
    return escritas


def verificar(jsonl, cuantos=200, n=4):
    """Prueba de identidad: los mismos índices, ya medidos en serie, recalculados en
    paralelo deben dar filas IDÉNTICAS campo a campo, salvo el reloj de pared."""
    previas = {r["idx"]: r for r in filas_de(jsonl, n)}
    if len(previas) < cuantos:
        return dict(ok=False, motivo=f"sólo hay {len(previas)} filas de n={n} en el JSONL")
    idxs = sorted(previas)[:cuantos]
    with ProcessPoolExecutor(max_workers=TRABAJADORES) as ex:
        nuevas = {r["idx"]: r for r in ex.map(
            trabajo, ((n, i, None, 0) for i in idxs), chunksize=8)}
    difs, campos = [], set()
    for i in idxs:
        a, b = previas[i], nuevas[i]
        for c in set(a) | set(b):
            if c == CAMPO_RELOJ:
                continue
            if a.get(c) != b.get(c):
                campos.add(c)
                difs.append((i, c, a.get(c), b.get(c)))
    return dict(ok=not difs, n=n, comparados=len(idxs), trabajadores=TRABAJADORES,
                campos_comparados=sorted(set(previas[idxs[0]]) - {CAMPO_RELOJ}),
                diferencias=len(difs), campos_que_difieren=sorted(campos),
                primeras=difs[:5])


if __name__ == "__main__":
    aqui = os.path.dirname(os.path.abspath(__file__))
    jsonl = os.path.join(aqui, "artifacts", "unidad_minima_05_banco.jsonl")
    modo = sys.argv[1] if len(sys.argv) > 1 else "verificar"

    if modo == "verificar":
        objetivo = sys.argv[2] if len(sys.argv) > 2 else jsonl
        r = verificar(objetivo, cuantos=int(sys.argv[3]) if len(sys.argv) > 3 else 200)
        print(json.dumps(r, ensure_ascii=False, indent=1))
        print("PRUEBA DE IDENTIDAD:", "IDÉNTICO campo a campo" if r["ok"] else "DIFIERE")
        sys.exit(0 if r["ok"] else 1)

    if modo == "correr":
        ns = [int(x) for x in sys.argv[2:]] or list(NS)
        for n in ns:
            correr(n, jsonl, sys.stdout)
        # resumen y puerta SIEMPRE sobre las filas ordenadas por (n, idx)
        todas = ordenadas(jsonl)
        import hashlib
        import io
        buf = io.StringIO()
        res = {}
        for n in NS:
            filas = [r for r in todas if r["n"] == n]
            if filas:
                res[n] = resumen(filas, buf)
        rep = {"por_n": {str(n): v for n, v in res.items()}}
        if all(n in res for n in NS):
            rep["puerta"] = puerta(res, buf)
        sys.stdout.write(buf.getvalue())
        canon = json.dumps([{k: v for k, v in r.items() if k != CAMPO_RELOJ} for r in todas],
                           ensure_ascii=False, sort_keys=True)
        rep["hash_filas_ordenadas_sin_reloj"] = hashlib.sha256(canon.encode()).hexdigest()
        rep["sha256_codigo_banco"] = hashlib.sha256(
            open(os.path.join(aqui, "unidad_minima_05_banco.py"), "rb").read()).hexdigest()
        rep["sha256_codigo_corredor"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
        rep["python"] = sys.version.split()[0]
        rep["trabajadores"] = TRABAJADORES
        rep["ola"] = OLA
        rep["K_declarada"] = {str(k): v for k, v in K_DECLARADA.items()}
        rep["L_por_n"] = {str(n): L_de(n) for n in NS}
        rep["futuro_max"] = FUTURO_MAX
        anterior = os.path.join(aqui, "artifacts", "unidad_minima_05_banco.json")
        if os.path.exists(anterior):
            try:
                prev = json.load(open(anterior, encoding="utf-8"))
                if "mutantes" in prev:
                    rep["mutantes"] = prev["mutantes"]
            except ValueError:
                pass
        with open(anterior, "w", encoding="utf-8") as f:
            json.dump(rep, f, ensure_ascii=False, indent=1)
        print(f"hash de las filas ordenadas (sin reloj): {rep['hash_filas_ordenadas_sin_reloj'][:16]}…")
