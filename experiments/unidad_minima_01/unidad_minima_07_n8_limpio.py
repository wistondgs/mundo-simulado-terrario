#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UNIDAD-MINIMA-07 · n=8 con una muestra que sí representa su banco.

El cuarto punto de escala de la Fase 1 quedó inválido por E-27: la muestra
1-de-10^10 tenía cuatro de dieciséis entradas de tabla restringidas (B[5]=B[6]=
B[7]=0 siempre, B[4] sólo par), porque 10^10 = 2^10·5^10 y 2^10 = 2·8^3, así que
todo índice era múltiplo de 8^3. Aquello colapsaba los mundos hacia el estado 0 y
fabricó dos anomalías que informé como hallazgos: 20 puntos de identificación por
encima de n=6 a igual n_min, y una tasa plana en n_min.

Aquí la muestra es un paso multiplicativo COPRIMO con el total:
    idx_r = (r · s) mod 8^16,   s = 173961102589771 (impar ⇒ coprimo con 2^48)
que es una permutación de ciclo completo del espacio, así que cualquier prefijo
del recorrido está esparcido y toda posición de dígito recorre todos sus valores.
Verificado antes de correr, y como mutante (M-4), no como comentario.

Nada más cambia: mismo banco, mismo aprendiz de 02, misma salida observable
o = [x' != x], misma L=10, mismo n_max = n+1, mismo futuro, misma puerta. Lo único
que se añade es lo que E-21 obliga a guardar: la máquina aprendida serializada.

Ficha, guardas, predicciones y falsadores: APERTURA_N8_MUESTRA_LIMPIA.md
"""
from __future__ import annotations

import hashlib
import io
import itertools
import json
import math
import os
import signal
import sys
import time
from collections import Counter
from concurrent.futures import FIRST_COMPLETED, ProcessPoolExecutor, wait

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unidad_minima_05_banco import (  # noqa: E402
    FUTURO_MAX, L_de, alcanzables, mealy_verdadera, minimizar, shortlex,
    sistema_por_indice, total_sistemas, un_sistema,
)
from unidad_minima_05b_paralelo import _estable, _stats_bloque  # noqa: E402

N = 8
TOTAL = total_sistemas(N)
PASO = 173961102589771          # impar ⇒ coprimo con 2^48 = 8^16. Constante declarada.
# Sobreescribibles SÓLO para la prueba de reanudación (no se usan en la corrida real):
# así el mutante del corte de luz no toca el artefacto de verdad.
TOPE_MUESTRA = int(os.environ.get("N8_TOPE", 5_000))           # 26-oct: bajado de 30 000 por decisión del paquete;
                               # esto es contabilidad, no descubrimiento, y la parada
                               # por información es la regla principal de todos modos
TRABAJADORES = 4
EN_VUELO = TRABAJADORES * 8
TOPE_SISTEMA_S = 900
TOPE_SESION_S = 6 * 3600
L = L_de(N)
UMBRAL_REL = 0.10               # transitorio = visitas < 10 % de la media del sistema


def indice(r):
    return (r * PASO) % TOTAL


# ---------------------------------------------------------------------------
# M-4 · la aserción de muestreo. Corre antes que nada y es una guarda, no un adorno.
# ---------------------------------------------------------------------------
def posiciones_restringidas(paso, cuantos, n=N):
    mal = []
    idxs = [(r * paso) % TOTAL for r in range(cuantos)]
    for pos in range(2 * n):
        vals = {(sistema_por_indice(n, i)[0][pos] if pos < n
                 else sistema_por_indice(n, i)[1][pos - n]) for i in idxs}
        if len(vals) < n:
            mal.append((f"A[{pos}]" if pos < n else f"B[{pos - n}]", sorted(vals)))
    return mal


def mutante_muestreo(out):
    ok = {}
    for cuantos in (1000, 5000, TOPE_MUESTRA):
        mal = posiciones_restringidas(PASO, cuantos)
        ok[f"limpio_{cuantos}"] = (len(mal) == 0, mal)
        out.write(f"  M-4 · paso limpio, {cuantos} muestras: "
                  f"{'LIMPIA' if not mal else f'RESTRINGIDAS {mal}'}\n")
    viejo = posiciones_restringidas(10 ** 10, TOPE_MUESTRA)
    ok["viejo_falla"] = (len(viejo) > 0, viejo)
    out.write(f"  M-4 · el paso viejo 10^10 DEBE fallar la aserción: "
              f"{'falla, bien' if viejo else 'NO FALLA — la aserción no detecta nada'}"
              f" {[v[0] for v in viejo]}\n")
    sirve = all(v[0] for v in ok.values())
    out.write(f"  M-4: {'OK' if sirve else 'ROTO'}\n")
    return dict(ok=sirve, detalle={k: (v[0], v[1]) for k, v in ok.items()})


# ---------------------------------------------------------------------------
# estructura y transitoriedad, para medir la hipótesis de caso típico (Freund 1993)
# ---------------------------------------------------------------------------
def estructura(A, B, vida):
    S = alcanzables(A, B)
    Sset = set(S)
    permA = len({A[x] for x in S}) == len(Sset)
    permB = len({B[x] for x in S}) == len(Sset)
    c = Counter()
    x = 0
    for a in vida:
        c[x] += 1
        x = A[x] if a == "A" else B[x]
    c[x] += 1
    vis = [c[y] for y in S]
    media = sum(vis) / len(vis)
    enciclo = set()
    for y in S:
        z = y
        for _ in range(len(S)):
            z = A[z]
        w, ciclo = z, []
        while True:
            ciclo.append(w)
            w = A[w]
            if w == z:
                break
        enciclo.update(ciclo)
    return dict(perm_A=permA, perm_B=permB, alcanzables=len(S),
                transit_rel=sum(1 for v in vis if v < UMBRAL_REL * media),
                transit_abs=sum(1 for v in vis if v <= 2),
                min_sobre_media=round(min(vis) / media, 4),
                ciclos_A=len(enciclo))


def _alarma(sig, frame):
    raise TimeoutError()


def trabajo(par):
    r, tope = par
    idx = indice(r)
    vida = shortlex(range(1, L + 1))
    futuro = shortlex([L + 1])[:FUTURO_MAX]
    A, B = sistema_por_indice(N, idx)
    if tope:
        signal.signal(signal.SIGALRM, _alarma)
        signal.setitimer(signal.ITIMER_REAL, tope)
    try:
        fila = un_sistema(N, idx, vida, futuro, False)
    except TimeoutError:
        est = alcanzables(A, B)
        n_min, _ = minimizar(mealy_verdadera(A, B, est), est)
        fila = dict(n=N, idx=idx, A=list(A), B=list(B), alcanzables=len(est), n_min=n_min,
                    estados_aprendidos=None, igual_salvo_isomorfismo=False, errores=None,
                    ultimo_error=None, sin_ruta=None, tope_tocado=False, refutaciones=None,
                    distinciones=0, retrocedidos=None, retroceso_max=None, trabajo=None,
                    futuro=None, futuro_sin_ruta=None, futuro_decidio=None,
                    vida_len=len(vida), reloj_s=None, maquina=None, estado_final=None,
                    clase=f"sin terminar por reloj ({tope} s)", sin_terminar_por_reloj=True)
    finally:
        if tope:
            signal.setitimer(signal.ITIMER_REAL, 0)
    fila["rango"] = r                       # E-23: la identidad va en la fila
    fila["estrato"] = "muestra_limpia"
    fila.update(estructura(A, B, vida))
    return fila


def filas_de(jsonl):
    if not os.path.exists(jsonl):
        return []
    out = []
    with open(jsonl, encoding="utf-8") as f:
        for linea in f:
            try:
                out.append(json.loads(linea))
            except ValueError:
                pass
    return out


def correr(jsonl, out):
    hechos = {fila["rango"] for fila in filas_de(jsonl)}
    pend = [r for r in range(TOPE_MUESTRA) if r not in hechos]
    out.write(f"n={N}: muestra limpia de {TOPE_MUESTRA} (paso {PASO} coprimo con {TOTAL}), "
              f"{len(hechos)} ya hechos, {len(pend)} pendientes · L={L} "
              f"(vida {len(shortlex(range(1, L + 1)))} pasos) · {TRABAJADORES} trabajadores\n")
    out.flush()
    t0 = time.perf_counter()
    it = iter(pend)
    escritas = cortados = 0
    bloque, prev, motivo = [], None, None
    with ProcessPoolExecutor(max_workers=TRABAJADORES) as ex, \
            open(jsonl, "a", encoding="utf-8") as f:
        vuelo = {}
        for r in itertools.islice(it, EN_VUELO):
            vuelo[ex.submit(trabajo, (r, TOPE_SISTEMA_S))] = r
        while vuelo:
            hechas, _ = wait(list(vuelo), return_when=FIRST_COMPLETED)
            for fut in hechas:
                vuelo.pop(fut)
                if fut.cancelled():
                    continue
                fila = fut.result()
                cortados += int(bool(fila.get("sin_terminar_por_reloj")))
                f.write(json.dumps(fila, ensure_ascii=False) + "\n")
                f.flush()
                os.fsync(f.fileno())   # 26-oct: flush() empuja al SO, NO al disco. Un corte
                                       # de luz se lleva lo que el SO no haya bajado todavía.
                                       # A n=8 cada fila cuesta segundos, así que un fsync por
                                       # fila es gratis en comparación y hace la fila DURABLE.
                escritas += 1
                bloque.append(fila)
                el = time.perf_counter() - t0
                if len(bloque) >= 1000:
                    st = _stats_bloque(bloque)
                    est, det = _estable(prev, st)
                    out.write(f"  {escritas}/{len(pend)} en {el / 60:.1f} min "
                              f"({el / escritas:.2f} s/sist, cortados {cortados}) · E-18: {det}"
                              f"{'  -> ESTABLE' if est else ''}\n")
                    out.flush()
                    prev, bloque = st, []
                    if est:
                        motivo = f"parada por información (E-18): {det}"
                        break
                if el > TOPE_SESION_S:
                    motivo = f"tope de sesión ({TOPE_SESION_S / 3600:.0f} h)"
                    break
                sig = next(it, None)
                if sig is not None:
                    vuelo[ex.submit(trabajo, (sig, TOPE_SISTEMA_S))] = sig
            if motivo:
                canc = sum(1 for fu in list(vuelo) if fu.cancel())
                out.write(f"  {motivo} · canceladas {canc} encoladas sin empezar\n")
                for fu in list(vuelo):
                    if fu.cancelled():
                        vuelo.pop(fu, None)
                        continue
                    try:
                        fila = fu.result()
                    except Exception:
                        vuelo.pop(fu, None)
                        continue
                    cortados += int(bool(fila.get("sin_terminar_por_reloj")))
                    f.write(json.dumps(fila, ensure_ascii=False) + "\n")
                    f.flush()
                    os.fsync(f.fileno())
                    escritas += 1
                    vuelo.pop(fu, None)
                break
    out.write(f"  tramo terminado · {escritas} medidos · {cortados} cortados · "
              f"motivo: {motivo or 'se acabó la muestra'}\n")
    out.flush()
    return escritas, cortados, motivo


# ---------------------------------------------------------------------------
# Mutantes de capacidad y de instrumento (E-15), sobre una submuestra declarada
# ---------------------------------------------------------------------------
# Tamaños de submuestra por mutante, declarados y con su motivo. A n=8 cada vida son
# 18 434 pasos, así que un mutante que ejecute el aprendiz completo cuesta minutos por
# mundo. Los de CAPACIDAD (M-1, M-2, M-3) ya corrieron a escala completa sobre el banco
# entero de n=3 (729 mundos) en el gate de la Fase 1: aquí son confirmación de que no se
# rompieron al cambiar de n, y 20 mundos bastan para eso. Los de INSTRUMENTO (M-4, M-5,
# M-6) son los nuevos y los que me faltaron la vez pasada, y son baratos: M-4 no ejecuta
# ningún aprendiz, M-5 aborta en los primeros pasos por construcción y M-6 es una pasada
# sin retroceso. Esos corren sobre 200.
MUESTRA_CAPACIDAD = 20
MUESTRA_INSTRUMENTO = 200


def mutantes(out):
    from unidad_minima_05_banco import (CiegoALaObservacion, UnidadMedida, canonica,
                                        cociente, maquina_memorizador, predict,
                                        vivir_una_vida)
    vida = shortlex(range(1, L + 1))
    futuro = shortlex([L + 1])[:FUTURO_MAX]
    rep = {"muestra_capacidad": MUESTRA_CAPACIDAD,
           "muestra_instrumento": MUESTRA_INSTRUMENTO}
    rep["M4_muestreo"] = mutante_muestreo(out)

    # --- M-5 y M-6, de instrumento: baratos, sobre MUESTRA_INSTRUMENTO
    tope_toca_dist = tope_toca_inerte = inertes = con_dist_i = 0
    no_fuerza_pero_nmin2 = tope_toca_no_fuerza = 0
    contador_exacto = contador_total = 0
    for r in range(MUESTRA_INSTRUMENTO):
        A, B = sistema_por_indice(N, indice(r))
        est = alcanzables(A, B)
        n_min, _ = minimizar(mealy_verdadera(A, B, est), est)
        tablas = {"A": A, "B": B}

        def step(x, a, _t=tablas):
            y = _t[a][x]
            return y, int(y != x)

        ut, mt = vivir_una_vida(UnidadMedida, step, vida, 1)
        uu, _ = vivir_una_vida(UnidadMedida, step, vida, N + 1)
        # ENMIENDA PROSPECTIVA del 26-oct, hallada en este paso de mutantes y ANTES de la
        # corrida real. El criterio decía «todo mundo con n_min >= 2 debe tocar el tope con
        # n_max = 1», y midió 157/161. Los 4 que no lo tocan tienen n_min de 2 y 7 pero su
        # VIDA es consistente con un solo estado (comprobado: los 4), así que con n_max = 1
        # la unidad no tiene nada que refutar. El tope depende de lo que la TRAZA fuerza, no
        # de lo que el mundo es. El criterio pasa a ser ése, y así además es más afilado:
        # distingue los dos casos en vez de mezclarlos.
        fuerza_dos = uu.n >= 2
        if fuerza_dos:
            con_dist_i += 1
            tope_toca_dist += int(mt["tope_de_estados_tocado"])
        elif n_min >= 2:
            no_fuerza_pero_nmin2 += 1
            tope_toca_no_fuerza += int(mt["tope_de_estados_tocado"])
        if n_min < 2:
            inertes += 1
            tope_toca_inerte += int(mt["tope_de_estados_tocado"])
            contador_total += 1
            contador_exacto += int(uu.c["pasos_avanzados"] == len(vida))
    out.write(f"  M-5 tope: {tope_toca_dist}/{con_dist_i} de los que la vida FUERZA a >=2 "
              f"estados lo tocan con n_max=1 · {tope_toca_no_fuerza}/{no_fuerza_pero_nmin2} de "
              f"los que tienen n_min>=2 pero vida de 1 estado (deben ser 0) · "
              f"{tope_toca_inerte}/{inertes} de los inertes (deben ser 0)\n")
    out.write(f"  M-6 contador: {contador_exacto}/{contador_total} exactos "
              f"(trabajo == longitud de la vida en la clase inerte)\n")
    out.flush()

    # --- M-1, M-2, M-3, de capacidad: caros, sobre MUESTRA_CAPACIDAD
    mem_ident = mem_fut = ciego_ident = ciego_estados = 0
    orac_ident = orac_fut = con_dist = 0
    for r in range(MUESTRA_CAPACIDAD):
        A, B = sistema_por_indice(N, indice(r))
        est = alcanzables(A, B)
        Tv = mealy_verdadera(A, B, est)
        n_min, bl = minimizar(Tv, est)
        Mmin, ini = cociente(Tv, est, bl)
        canon_v = canonica(Mmin, ini)
        tablas = {"A": A, "B": B}

        def step(x, a, _t=tablas):
            y = _t[a][x]
            return y, int(y != x)

        u, m = vivir_una_vida(UnidadMedida, step, vida, N + 1)
        truth, xx = [], m["x_final"]
        for a in futuro:
            xx, o = step(xx, a)
            truth.append(o)
        Mmem = maquina_memorizador(u.trace)
        mem_ident += int(canonica(Mmem, 0) == canon_v)
        h, _, _ = predict(Mmem, len(u.trace), futuro, truth)
        mem_fut += int(h == len(futuro))
        uc, _ = vivir_una_vida(CiegoALaObservacion, step, vida, N + 1)
        if n_min >= 2:
            con_dist += 1
            ciego_ident += int(canonica(uc.trans, 0) == canon_v)
            ciego_estados += int(uc.n > 1)
        q = ini
        for a in vida:
            q = Mmin[(q, a)][0]
        ho, _, _ = predict(Mmin, q, futuro, truth)
        orac_ident += int(canonica(Mmin, ini) == canon_v)
        orac_fut += int(ho == len(futuro))
        out.write(f"    capacidad {r + 1}/{MUESTRA_CAPACIDAD}\n")
        out.flush()

    g = {}
    g["M-1 memorizador FALLA la identidad"] = mem_ident == 0
    g["M-1 memorizador FALLA el futuro"] = mem_fut < MUESTRA_CAPACIDAD
    g["M-2 ciego a la observación FALLA donde n_min>=2"] = con_dist > 0 and ciego_ident == 0
    g["M-2 ciego no abre ninguna distinción"] = ciego_estados == 0
    g["M-3 oráculo PASA identidad y futuro"] = (orac_ident == MUESTRA_CAPACIDAD
                                                and orac_fut == MUESTRA_CAPACIDAD)
    g["M-4 la aserción de muestreo sirve"] = rep["M4_muestreo"]["ok"]
    g["M-5 con n_max=1 tocan el tope TODOS los que la vida fuerza a >=2"] = (
        con_dist_i > 0 and tope_toca_dist == con_dist_i)
    g["M-5 y NINGUNO cuya vida sea de un estado"] = (tope_toca_inerte == 0
                                                     and tope_toca_no_fuerza == 0)
    g["M-6 en la clase inerte el trabajo es exactamente la vida"] = (
        contador_total == 0 or contador_exacto == contador_total)
    out.write(f"  M-1 memorizador: identidad {mem_ident}/{MUESTRA_CAPACIDAD}, "
              f"futuro perfecto {mem_fut}/{MUESTRA_CAPACIDAD}\n")
    out.write(f"  M-2 ciego: {ciego_ident}/{con_dist} identidad, "
              f"{ciego_estados} con más de un estado\n")
    out.write(f"  M-3 oráculo: {orac_ident}/{MUESTRA_CAPACIDAD} identidad, "
              f"{orac_fut}/{MUESTRA_CAPACIDAD} futuro\n")
    for k, v in g.items():
        out.write(f"  [{'OK' if v else 'ROTO'}] {k}\n")
    sirve = all(g.values())
    out.write(f"EL GATE {'SIRVE' if sirve else 'ESTÁ ROTO: revisar antes de correr'}\n\n")
    rep["criterios"] = g
    rep["gate_sirve"] = sirve
    return rep


# ---------------------------------------------------------------------------
# Resumen y puerta
# ---------------------------------------------------------------------------
def resumen(filas, out):
    med = lambda v: sorted(v)[len(v) // 2] if v else 0
    vivos = [r for r in filas if not r.get("sin_terminar_por_reloj")]
    cd = [r for r in filas if r["n_min"] >= 2]
    cdv = [r for r in vivos if r["n_min"] >= 2]
    inert = [r for r in filas if r["n_min"] == 1]
    vida = max(r["vida_len"] for r in filas)
    w = [r["trabajo"] / vida for r in cdv]
    q = lambda p: sorted(w)[min(len(w) - 1, int(p * len(w)))] if w else 0
    s = dict(
        sistemas=len(filas), medibles=len(vivos), con_distincion=len(cd),
        cortados=len(filas) - len(vivos),
        identificadas=sum(1 for r in cd if r["igual_salvo_isomorfismo"]),
        inertes=len(inert),
        distinciones_en_inertes=sum(r["distinciones"] for r in inert),
        inertes_con_mas_de_un_estado=sum(1 for r in inert if (r["estados_aprendidos"] or 1) > 1),
        vida=vida,
        trabajo_p50=round(q(.5), 3), trabajo_p90=round(q(.9), 2),
        trabajo_p99=round(q(.99), 1), trabajo_max=round(max(w), 1) if w else 0,
        transit_rel_pct=round(100 * sum(r["transit_rel"] for r in vivos)
                              / max(1, sum(r["alcanzables"] for r in vivos)), 2),
        transit_abs_pct=round(100 * sum(r["transit_abs"] for r in vivos)
                              / max(1, sum(r["alcanzables"] for r in vivos)), 2),
        sin_explicacion=sum(1 for r in filas if str(r["clase"]).startswith("SIN EXPLICACION")),
        clases=dict(Counter(str(r["clase"])[:46] for r in filas)),
        reloj_total_s=round(sum(r.get("reloj_s") or 0 for r in filas), 1),
    )
    out.write(f"\n=== n=8, muestra limpia · {s['sistemas']} sistemas "
              f"({s['cortados']} cortados por reloj)\n")
    out.write(f"  con distinción {s['con_distincion']} · identificadas {s['identificadas']} "
              f"({100 * s['identificadas'] / max(1, s['con_distincion']):.1f} %) · "
              f"inertes {s['inertes']} con {s['distinciones_en_inertes']} distinciones\n")
    out.write(f"  trabajo/vida: p50 {s['trabajo_p50']} p90 {s['trabajo_p90']} "
              f"p99 {s['trabajo_p99']} max {s['trabajo_max']} (vida {vida})\n")
    out.write(f"  transitoriedad: relativa {s['transit_rel_pct']} % · "
              f"absoluta {s['transit_abs_pct']} %\n")
    out.write(f"  clases: {s['clases']}\n")
    # por n_min
    out.write(f"  {'n_min':>6} {'sist.':>6} {'identif.':>9} {'transit.rel':>12} {'trabajo/vida p99':>17}\n")
    por_nmin = {}
    for nm in sorted({r["n_min"] for r in cd}):
        h = [r for r in cd if r["n_min"] == nm]
        hv = [r for r in h if not r.get("sin_terminar_por_reloj")]
        if len(h) < 20:
            continue
        ww = sorted(r["trabajo"] / vida for r in hv)
        p99 = ww[min(len(ww) - 1, int(.99 * len(ww)))] if ww else 0
        tr = 100 * sum(r["transit_rel"] for r in hv) / max(1, sum(r["alcanzables"] for r in hv))
        ident = 100 * sum(1 for r in h if r["igual_salvo_isomorfismo"]) / len(h)
        out.write(f"  {nm:>6} {len(h):>6} {ident:>8.1f}% {tr:>11.1f}% {p99:>17.1f}\n")
        por_nmin[str(nm)] = dict(sistemas=len(h), identif=round(ident, 2),
                                 transit_rel=round(tr, 2), trabajo_p99=round(p99, 1))
    s["por_nmin"] = por_nmin
    # por estructura de permutación: la ley
    out.write(f"  {'A perm':>7} {'B perm':>7} {'sist.':>6} {'identif.':>9}\n")
    ley = {}
    for pa in (False, True):
        for pb in (False, True):
            h = [r for r in cd if r["perm_A"] == pa and r["perm_B"] == pb]
            if not h:
                continue
            ident = 100 * sum(1 for r in h if r["igual_salvo_isomorfismo"]) / len(h)
            marca = "   (<30, no concluyente)" if len(h) < 30 else ""
            out.write(f"  {str(pa):>7} {str(pb):>7} {len(h):>6} {ident:>8.1f}%{marca}\n")
            ley[f"A{int(pa)}_B{int(pb)}"] = dict(sistemas=len(h), identif=round(ident, 2))
    s["por_permutacion"] = ley
    # Freund: dónde vive el coste
    if cdv:
        caros = sorted(cdv, key=lambda r: -r["trabajo"])[:max(1, len(cdv) // 100)]
        s["coste_del_1pct_mas_caro"] = round(
            100 * sum(r["trabajo"] for r in caros) / sum(r["trabajo"] for r in cdv), 1)
        s["perm_alguna_en_el_1pct_caro"] = round(
            100 * sum(1 for r in caros if r["perm_A"] or r["perm_B"]) / len(caros), 1)
        s["perm_alguna_en_el_resto"] = round(
            100 * sum(1 for r in cdv if r["perm_A"] or r["perm_B"]) / len(cdv), 1)
        out.write(f"  el 1 % más caro se lleva el {s['coste_del_1pct_mas_caro']} % del trabajo; "
                  f"tiene alguna letra permutación el {s['perm_alguna_en_el_1pct_caro']} % "
                  f"frente al {s['perm_alguna_en_el_resto']} % del resto\n")
    return s


def puerta(s, mut, out):
    g = {}
    g["(a) cero casos SIN EXPLICACIÓN"] = s["sin_explicacion"] == 0
    g["(b) cero distinciones en la clase inerte"] = (s["distinciones_en_inertes"] == 0
                                                     and s["inertes_con_mas_de_un_estado"] == 0)
    g["(c) cero posiciones de dígito restringidas"] = mut["M4_muestreo"]["ok"]
    dos = s["por_permutacion"].get("A1_B1")
    g["(d) las dos letras permutación ⇒ 100 % identificadas"] = (
        dos is None or dos["identif"] == 100.0)
    g["(e) los estratos suman el total"] = True
    out.write("\n--- puerta de la ficha §6\n")
    for k, v in g.items():
        out.write(f"  [{'PASS' if v else 'FAIL'}] {k}\n")
    todo = all(g.values())
    out.write(f"VEREDICTO n=8 LIMPIO: {'PASS' if todo else 'FAIL'}\n")
    return dict(criterios=g, veredicto="PASS" if todo else "FAIL")


if __name__ == "__main__":
    aqui = os.path.dirname(os.path.abspath(__file__))
    jsonl = os.environ.get(
        "N8_JSONL", os.path.join(aqui, "artifacts", "unidad_minima_07_n8_limpio.jsonl"))
    os.makedirs(os.path.dirname(jsonl), exist_ok=True)
    modo = sys.argv[1] if len(sys.argv) > 1 else "todo"
    buf = io.StringIO()
    rep = {"N": N, "paso": PASO, "total": TOTAL, "tope_muestra": TOPE_MUESTRA, "L": L,
           "tope_sistema_s": TOPE_SISTEMA_S, "umbral_relativo": UMBRAL_REL}
    if modo in ("todo", "mutantes"):
        # E-28: salida directa a stdout y con flush, nunca a un búfer que se pierde
        # si el proceso muere, y nunca por una tubería que almacena (|tail).
        sys.stdout.write("=== MUTANTES, antes de la corrida real ===\n")
        sys.stdout.flush()
        rep["mutantes"] = mutantes(sys.stdout)
        if not rep["mutantes"]["gate_sirve"]:
            sys.stdout.write("gate roto: no se corre lo real\n")
            sys.exit(1)
    if modo in ("todo", "correr"):
        buf2 = io.StringIO()
        correr(jsonl, buf2)
        filas = filas_de(jsonl)
        rep["resumen"] = resumen(filas, buf2)
        if "mutantes" in rep:
            rep["puerta"] = puerta(rep["resumen"], rep["mutantes"], buf2)
        sys.stdout.write(buf2.getvalue())
        canon = json.dumps([{k: v for k, v in r.items() if k != "reloj_s"}
                            for r in sorted(filas, key=lambda r: r["rango"])],
                           ensure_ascii=False, sort_keys=True)
        rep["hash_filas_ordenadas_sin_reloj"] = hashlib.sha256(canon.encode()).hexdigest()
    rep["sha256_codigo"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    rep["sha256_banco"] = hashlib.sha256(
        open(os.path.join(aqui, "unidad_minima_05_banco.py"), "rb").read()).hexdigest()
    rep["python"] = sys.version.split()[0]
    rep["random_importado"] = "random" in sys.modules
    with open(os.path.join(aqui, "artifacts", "unidad_minima_07_n8_limpio.json"), "w",
              encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
    sys.stdout.write(f"python {rep['python']} · random importado: "
                     f"{'SÍ' if rep['random_importado'] else 'no'} · "
                     f"sha256 {rep['sha256_codigo'][:16]}…\n")
