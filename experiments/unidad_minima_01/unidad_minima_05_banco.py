#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UNIDAD-MINIMA-05 · el banco poblacional: ¿escala el mecanismo de 02 sin azar?

Pregunta de la fase: la unidad de 02 —una vida, sin maestro, sin reset, sin
probabilidad— ¿identifica la máquina mínima de mundos ocultos de 3 a 8 estados,
con coste que crece polinomialmente y no exponencialmente?

Si la respuesta es sí con el mecanismo que ya existe, no se escribe ninguno nuevo.

EL BANCO. Un sistema son dos mapas arbitrarios A, B: S -> S sobre {0..n-1}; hay
n^(2n). Orden canónico: los 2n dígitos en base n, letra A primero, el último
variando más rápido. Ese orden se indexa directamente (`sistema_por_indice`), lo
que permite recorrer el banco completo o una fracción 1-de-k **determinista** sin
enumerar lo que no se usa. Nada de muestreo aleatorio.

Estado inicial 0; sólo cuenta la parte alcanzable desde 0, porque lo inalcanzable
no existe para la unidad y no se le exige. Salida observable: el bit de cambio
o = [x' != x], única y declarada como disposición suministrada.

LA VERDAD DE REFERENCIA se calcula de libro y se cita, no se redescubre:
minimización por refinamiento de particiones (Hopcroft 1971,
10.1016/b978-0-12-417750-5.50022-1). n_min = 1 marca la clase «inerte bajo esta
salida», que es el control negativo gratis del banco: ahí la unidad NO debe abrir
distinciones.

IDENTIDAD salvo isomorfismo, por forma canónica: renumerar por BFS desde el
estado inicial con orden fijo de letras y comparar. Etiquetas distintas con la
misma conducta no son fallo.

Lo SUMINISTRADO: el banco y su orden, la salida observable, la longitud de vida
L(n), el tope n_max = n+1, el segmento de futuro, y que la unidad relea sólo al
refutar (el comportamiento de 02; el disparador interno de 03 no se usa porque
aquí no hay lesiones).
Lo ADQUIRIDO: la máquina de cada sistema, cuándo dejó de errar y lo que costó.
"""
from __future__ import annotations

import hashlib
import io
import itertools
import json
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unidad_minima_01 import (  # noqa: E402
    LETTERS, majority, minimal_mealy, predict, shortlex,
)
from unidad_minima_02_incremental import Unidad  # noqa: E402

# --- disposición suministrada, declarada antes de correr (ver la ficha de apertura)
def L_de(n):
    """Longitud máxima de palabra de la vida. Suelo estructural: en una máquina
    mínima de n estados, dos estados cualesquiera se separan con una palabra de
    longitud < n y cualquier estado se alcanza con una de longitud < n, y la vida
    shortlex hasta L contiene toda palabra de longitud <= L como bloque. Así que
    L >= n-1 es el suelo; el margen de +3 es A OJO y se declara como tal, porque
    el gate no encontró ninguna cota publicada para una sola traza sin reset."""
    return n + 2

FUTURO_MAX = 2048          # tope de pasos del segmento de futuro, declarado
NS = (3, 4, 6, 8)


# ---------------------------------------------------------------------------
# El banco
# ---------------------------------------------------------------------------
def total_sistemas(n):
    return n ** (2 * n)


def sistema_por_indice(n, idx):
    """Decodifica un índice del orden canónico en (tablaA, tablaB)."""
    d = []
    for _ in range(2 * n):
        d.append(idx % n)
        idx //= n
    d.reverse()
    return tuple(d[:n]), tuple(d[n:])


def paso_de(A, B):
    tablas = {"A": A, "B": B}

    def step(x, a):
        y = tablas[a][x]
        return y, int(y != x)
    return step


def alcanzables(A, B):
    vistos, cola = {0}, [0]
    while cola:
        x = cola.pop()
        for T in (A, B):
            y = T[x]
            if y not in vistos:
                vistos.add(y)
                cola.append(y)
    return sorted(vistos)


def mealy_verdadera(A, B, estados):
    tablas = {"A": A, "B": B}
    return {(x, a): (tablas[a][x], int(tablas[a][x] != x)) for x in estados for a in LETTERS}


# ---------------------------------------------------------------------------
# Verdad de referencia: minimización por refinamiento de particiones
# ---------------------------------------------------------------------------
def minimizar(trans, estados):
    """Hopcroft 1971 en su forma de refinamiento por particiones (Moore). Devuelve
    (n_bloques, bloque_de_estado)."""
    bloque = {x: tuple(trans[(x, a)][1] for a in LETTERS) for x in estados}
    bloque = _renumerar(bloque, estados)
    while True:
        firma = {x: (bloque[x], tuple(bloque[trans[(x, a)][0]] for a in LETTERS)) for x in estados}
        nuevo = _renumerar(firma, estados)
        if len(set(nuevo.values())) == len(set(bloque.values())):
            return len(set(bloque.values())), bloque
        bloque = nuevo


def _renumerar(firma, estados):
    orden, nums = {}, {}
    for x in estados:
        f = firma[x]
        if f not in orden:
            orden[f] = len(orden)
        nums[x] = orden[f]
    return nums


def cociente(trans, estados, bloque):
    """La máquina mínima verdadera, sobre los bloques."""
    out = {}
    for x in estados:
        for a in LETTERS:
            y, o = trans[(x, a)]
            out[(bloque[x], a)] = (bloque[y], o)
    return out, bloque[0]


# ---------------------------------------------------------------------------
# Identidad salvo isomorfismo
# ---------------------------------------------------------------------------
def canonica(trans, inicio):
    """Renumera por BFS desde `inicio` con orden fijo de letras. Devuelve una
    forma comparable, o None si la máquina está vacía."""
    if not trans:
        return ()
    mapa, orden, i = {inicio: 0}, [inicio], 0
    while i < len(orden):
        x = orden[i]
        i += 1
        for a in LETTERS:
            t = trans.get((x, a))
            if t is None:
                continue
            y = t[0]
            if y not in mapa:
                mapa[y] = len(orden)
                orden.append(y)
    res = []
    for x in orden:
        for a in LETTERS:
            t = trans.get((x, a))
            if t is not None:
                res.append((mapa[x], a, mapa[t[0]], t[1]))
    return tuple(sorted(res))


# ---------------------------------------------------------------------------
# Los aprendices: el de 02 y los tres mutantes
# ---------------------------------------------------------------------------
class UnidadMedida(Unidad):
    """La unidad de 02, con un contador de TRABAJO REAL añadido por fuera.

    DEFECTO HALLADO el 2026-10-25 en el contador de 02: `pasos_repasados` suma la
    DISTANCIA RETROCEDIDA (len(traza) - i) en cada refutación, no los pasos que de
    hecho se vuelven a recorrer. Si al reanudar refuta en el primer paso, cuenta un
    repaso completo que nunca ocurrió. En n=2 daba 79 y no se notaba; en n=6 llega a
    contar 13,9 millones de pasos en 0,06 s de reloj, que es imposible.

    `pasos_avanzados` cuenta las llamadas reales a `_avanzar`, que es el trabajo que
    la unidad hace de verdad. Los dos se informan por separado: la distancia
    retrocedida sigue siendo un dato (dice cuánto deshace), pero no es el coste.
    No se toca 02: está congelado y commiteado.
    """

    def _avanzar(self, i, a, o):
        self.c["pasos_avanzados"] += 1
        return Unidad._avanzar(self, i, a, o)


class CiegoALaObservacion(Unidad):
    """El mutante de 1.8: el estado nunca ve una observación. Asigna la primera
    transición y jamás refuta, así que nunca abre una segunda distinción. Debe
    FALLAR en todo sistema con n_min >= 2."""

    def leer(self, a, o):
        self.trace.append((a, o))
        key = (self.q, a)
        if key not in self.trans:
            self.trans[key] = (0, o)
        self.q = self.trans[key][0]


def maquina_memorizador(trace):
    """El mutante que memoriza: un estado por paso vivido. Acierta en todo lo
    vivido y no tiene ruta para nada nuevo. Debe FALLAR en identidad y en futuro."""
    return {(i, a): (i + 1, o) for i, (a, o) in enumerate(trace)}


def vivir_una_vida(clase, step, life, n_max):
    """Vive la vida prediciendo ANTES de actuar. Devuelve la unidad y lo medido.

    DEFECTO CORREGIDO el 2026-10-25: esta función instanciaba `clase()` sin pasar
    `n_max`, así que toda la campaña corría con el tope por omisión de 02 (4 estados)
    en vez del `n + 1` declarado en la ficha. Las corridas de n=6 y n=8 hechas con el
    defecto quedan NULAS —no ejecutaron la configuración declarada— y se repiten."""
    u, x = clase(n_max=n_max), 0
    err = ultimo = sin_ruta = 0
    tope_tocado = False
    for t, a in enumerate(life, start=1):
        p = u.predecir(a)
        if p is None:
            sin_ruta += 1
            p = 0
        x, o = step(x, a)
        if p != o:
            err += 1
            ultimo = t
        try:
            u.leer(a, o)
        except RuntimeError:
            tope_tocado = True
            break
    return u, dict(errores=err, ultimo_error=ultimo, sin_ruta=sin_ruta,
                   tope_de_estados_tocado=tope_tocado, x_final=x)


# ---------------------------------------------------------------------------
# Un sistema
# ---------------------------------------------------------------------------
def un_sistema(n, idx, life, futuro, con_identificabilidad, vida_invertida=False):
    A, B = sistema_por_indice(n, idx)
    step = paso_de(A, B)
    est = alcanzables(A, B)
    Tv = mealy_verdadera(A, B, est)
    n_min, bloque = minimizar(Tv, est)
    Mmin, inicio_min = cociente(Tv, est, bloque)
    canon_verdadera = canonica(Mmin, inicio_min)

    vida = list(reversed(life)) if vida_invertida else life
    t0 = time.perf_counter()
    u, m = vivir_una_vida(UnidadMedida, step, vida, n + 1)
    reloj = time.perf_counter() - t0

    canon_aprendida = canonica(u.trans, 0)
    igual = (canon_aprendida == canon_verdadera)

    # futuro: segmento fijo declarado, desde donde quedó el mundo
    x = m["x_final"]
    truth = []
    xx = x
    for a in futuro:
        xx, o = step(xx, a)
        truth.append(o)
    hits, nr, dec = predict(u.trans, u.q, futuro, truth)

    r = dict(n=n, idx=idx, A=list(A), B=list(B), alcanzables=len(est), n_min=n_min,
             estados_aprendidos=u.n, igual_salvo_isomorfismo=igual,
             errores=m["errores"], ultimo_error=m["ultimo_error"], sin_ruta=m["sin_ruta"],
             tope_tocado=m["tope_de_estados_tocado"],
             refutaciones=u.c["refutaciones"], distinciones=u.c["distinciones_abiertas"],
             retrocedidos=u.c["pasos_repasados"], retroceso_max=u.c["repaso_max"],
             trabajo=u.c["pasos_avanzados"],
             futuro=hits / len(futuro), futuro_sin_ruta=nr, futuro_decidio=dec,
             vida_len=len(vida), reloj_s=round(reloj, 6))

    # Clasificación obligatoria de los que no coinciden. REPARACIÓN ÚNICA del 2026-10-25,
    # declarada en la ficha antes de volver a medir: se decide por comparación de tamaños,
    # que es exacta y no requiere ninguna búsqueda, en vez de por «¿hay >= 2 mínimas?»,
    # que sólo cubría una de las dos formas en que una vida puede no determinar la verdad
    # (la otra es: hay exactamente una mínima y no es la verdad). Endurece el criterio y
    # además escala a n = 8, donde la búsqueda exhaustiva era impracticable.
    if igual:
        r["clase"] = "identificada"
    elif m["tope_de_estados_tocado"]:
        r["clase"] = "tope de estados tocado"
    elif u.n > n_min:
        # la verdad, de tamaño n_min, es consistente con la traza: existía una más chica
        r["clase"] = "SIN EXPLICACION: sobrefragmentó, más estados que el mínimo verdadero"
    elif u.n < n_min:
        r["clase"] = "la vida no determina la verdad: admite una máquina menor"
    else:
        r["clase"] = "la vida no determina la verdad: dos máquinas del mismo tamaño la explican"

    # Cruce obligatorio contra el retroceso exhaustivo de 01, sólo en |S| <= 4 y sólo en
    # los no coincidentes. Si las dos vías discrepan, se para y se informa.
    if con_identificabilidad and not igual:
        res = minimal_mealy(u.trace, n_max=n + 1, count_cap=2)
        r["cruce_tamano_minimo"] = res[0] if res else None
        r["cruce_minimas_contadas"] = res[2] if res else None
        r["cruce_coincide"] = bool(res) and res[0] == u.n
    return r


# ---------------------------------------------------------------------------
# Campaña por n, reanudable
# ---------------------------------------------------------------------------
def indices(n, k):
    tot = total_sistemas(n)
    return range(0, tot, k)


def campana_n(n, k, jsonl, out, limite_reloj=None):
    L = L_de(n)
    life = shortlex(range(1, L + 1))
    futuro = shortlex([L + 1])[:FUTURO_MAX]
    con_id = (n <= 4)
    hechos = set()
    if os.path.exists(jsonl):
        with open(jsonl, encoding="utf-8") as f:
            for linea in f:
                try:
                    d = json.loads(linea)
                except ValueError:
                    continue
                if d.get("n") == n:
                    hechos.add(d["idx"])
    idxs = [i for i in indices(n, k) if i not in hechos]
    out.write(f"n={n}: {total_sistemas(n)} sistemas en el banco, 1 de cada {k} -> "
              f"{len(list(indices(n, k)))} a medir, {len(hechos)} ya hechos, "
              f"L={L} (vida {len(life)} pasos), futuro {len(futuro)} pasos, "
              f"identificabilidad exacta: {'sí' if con_id else 'sólo en los no coincidentes'}\n")
    filas, t0 = [], time.perf_counter()
    with open(jsonl, "a", encoding="utf-8") as f:
        for i in idxs:
            r = un_sistema(n, i, life, futuro, con_id)
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            f.flush()
            filas.append(r)
            if limite_reloj and time.perf_counter() - t0 > limite_reloj:
                out.write(f"  ALTO por presupuesto de reloj tras {len(filas)} sistemas\n")
                break
    # releer todo lo de este n (incluye lo ya hecho en corridas anteriores)
    todas = []
    with open(jsonl, encoding="utf-8") as f:
        for linea in f:
            try:
                d = json.loads(linea)
            except ValueError:
                continue
            if d.get("n") == n:
                todas.append(d)
    return todas


# ---------------------------------------------------------------------------
# Mutantes del gate (§3.5 de las orientaciones). Corren ANTES de la corrida real.
# ---------------------------------------------------------------------------
def mutantes(n, out):
    """Cuatro mutantes sobre el banco completo de n. Tres deben FALLAR y uno PASAR.
    Un criterio que sólo falla no es criterio, y uno que sólo pasa tampoco."""
    L = L_de(n)
    life = shortlex(range(1, L + 1))
    futuro = shortlex([L + 1])[:FUTURO_MAX]
    res = dict(n=n, sistemas=0, memorizador=Counter(), ciego=Counter(),
               oraculo=Counter(), vida_invertida=Counter())

    for idx in indices(n, 1):
        A, B = sistema_por_indice(n, idx)
        step = paso_de(A, B)
        est = alcanzables(A, B)
        Tv = mealy_verdadera(A, B, est)
        n_min, bloque = minimizar(Tv, est)
        Mmin, ini = cociente(Tv, est, bloque)
        canon_v = canonica(Mmin, ini)
        res["sistemas"] += 1

        # la unidad de verdad, para referencia de los mutantes
        u, m = vivir_una_vida(Unidad, step, life, n + 1)
        ok_real = canonica(u.trans, 0) == canon_v
        truth, xx = [], m["x_final"]
        for a in futuro:
            xx, o = step(xx, a)
            truth.append(o)

        # 1 · memorizador: un estado por paso vivido; nunca generaliza
        Mmem = maquina_memorizador(u.trace)
        igual_mem = canonica(Mmem, 0) == canon_v
        hmem, _, _ = predict(Mmem, len(u.trace), futuro, truth)
        res["memorizador"]["identidad_ok"] += int(igual_mem)
        res["memorizador"]["futuro_perfecto"] += int(hmem == len(futuro))

        # 2 · ciego a la observación (el fallo de 1.8)
        uc, mc = vivir_una_vida(CiegoALaObservacion, step, life, n + 1)
        igual_ciego = canonica(uc.trans, 0) == canon_v
        if n_min >= 2:
            res["ciego"]["con_distincion"] += 1
            res["ciego"]["identidad_ok"] += int(igual_ciego)
            res["ciego"]["estados_mayor_que_1"] += int(uc.n > 1)

        # 3 · oráculo: se le da la máquina verdadera; debe PASAR
        q = ini
        for a in life:
            q = Mmin[(q, a)][0]
        hor, _, _ = predict(Mmin, q, futuro, truth)
        res["oraculo"]["identidad_ok"] += int(canonica(Mmin, ini) == canon_v)
        res["oraculo"]["futuro_perfecto"] += int(hor == len(futuro))

        # 4 · vida invertida: debe cambiar el paso del último error y NO la máquina
        # Enmienda prospectiva del 2026-10-25, hallada en este mismo paso de mutantes y
        # ANTES de la corrida real. El criterio original —«la vida invertida no debe
        # cambiar la máquina en los identificables»— confundía dos cosas: que el MECANISMO
        # dependa del orden (defecto) y que la vida invertida sea una EXPERIENCIA distinta
        # y a veces más pobre (esperado). Medido: de 567 sistemas identificados hacia
        # delante, 54 dan otra máquina hacia atrás, y en los 54 la máquina aprendida es la
        # mínima de su propia traza invertida (18 de ellos no identificables desde esa
        # vida, 8 sin ver nunca la distinción). Lo que prueba independencia del orden es
        # que el aprendiz devuelva la mínima de lo que vivió, no que vivir otra cosa dé lo
        # mismo. El criterio pasa a ser ése, y las diferencias con la verdad se clasifican.
        ui, mi = vivir_una_vida(Unidad, step, list(reversed(life)), n + 1)
        if ok_real:
            res["vida_invertida"]["base_identificada"] += 1
            igual_i = canonica(ui.trans, 0) == canon_v
            res["vida_invertida"]["maquina_igual"] += int(igual_i)
            res["vida_invertida"]["ultimo_error_distinto"] += int(mi["ultimo_error"] != m["ultimo_error"])
            if not igual_i:
                r2 = minimal_mealy(ui.trace, n_max=n + 1, count_cap=2)
                res["vida_invertida"]["difiere_de_la_verdad"] += 1
                res["vida_invertida"]["y_es_minima_de_su_traza"] += int(bool(r2) and r2[0] == ui.n)
                res["vida_invertida"]["y_no_identificable_asi"] += int(bool(r2) and r2[2] >= 2)

    S = res["sistemas"]
    g = {}
    g["memorizador FALLA la identidad"] = res["memorizador"]["identidad_ok"] == 0
    g["memorizador FALLA el futuro"] = res["memorizador"]["futuro_perfecto"] < S
    cd = res["ciego"]["con_distincion"]
    g["ciego a la observación FALLA donde n_min>=2"] = cd > 0 and res["ciego"]["identidad_ok"] == 0
    g["ciego no abre ninguna distinción"] = res["ciego"]["estados_mayor_que_1"] == 0
    g["oráculo PASA la identidad"] = res["oraculo"]["identidad_ok"] == S
    g["oráculo PASA el futuro"] = res["oraculo"]["futuro_perfecto"] == S
    bi = res["vida_invertida"]["base_identificada"]
    dif = res["vida_invertida"]["difiere_de_la_verdad"]
    g["vida invertida: lo aprendido es la mínima de la traza vivida"] = \
        dif == res["vida_invertida"]["y_es_minima_de_su_traza"]
    g["vida invertida SÍ cambia el paso del último error"] = \
        res["vida_invertida"]["ultimo_error_distinto"] > 0

    out.write(f"--- mutantes del gate sobre el banco completo de n={n} ({S} sistemas)\n")
    for k, v in g.items():
        out.write(f"  [{'OK' if v else 'ROTO'}] {k}\n")
    out.write(f"  memorizador: {dict(res['memorizador'])}\n")
    out.write(f"  ciego: {dict(res['ciego'])}\n")
    out.write(f"  oráculo: {dict(res['oraculo'])}\n")
    out.write(f"  vida invertida: {dict(res['vida_invertida'])}\n")
    sirve = all(g.values())
    out.write(f"EL GATE {'SIRVE' if sirve else 'ESTÁ ROTO'}: "
              f"{'los tres mutantes malos fallan y el bueno pasa' if sirve else 'revisar antes de correr'}\n\n")
    res["criterios"] = g
    res["gate_sirve"] = sirve
    for k in ("memorizador", "ciego", "oraculo", "vida_invertida"):
        res[k] = dict(res[k])
    return res



def resumen(filas, out):
    """Resumen por n. Vida nueva, repaso y refutaciones se informan SEPARADOS, como
    dejó escrito la Fase 0: el coste de relectura es un eje propio."""
    if not filas:
        return {}
    vida = max(r["vida_len"] for r in filas if r.get("vida_len"))
    # La clase «sin terminar por reloj» (declarada en la ficha el 25-oct ANTES de aplicarla)
    # CUENTA en los denominadores —no identificó— y se EXCLUYE de los estadísticos de valor,
    # porque su coste es un corte, no una medida. Los sistemas afectados se listan por índice.
    sin_term = [r for r in filas if r.get("sin_terminar_por_reloj")]
    medibles = [r for r in filas if not r.get("sin_terminar_por_reloj")]
    con_dist = [r for r in filas if r["n_min"] >= 2]
    con_dist_med = [r for r in medibles if r["n_min"] >= 2]
    inertes = [r for r in filas if r["n_min"] == 1]
    med = lambda v: sorted(v)[len(v) // 2] if v else 0
    ue = [r["ultimo_error"] for r in con_dist_med]
    rp = [r["trabajo"] for r in con_dist_med]
    rt = [r["retrocedidos"] for r in con_dist_med]
    clases = Counter(r["clase"] for r in filas)
    s = dict(
        n=filas[0]["n"], sistemas=len(filas), vida=vida,
        con_distincion=len(con_dist), inertes=len(inertes),
        identificadas_con_distincion=sum(1 for r in con_dist if r["igual_salvo_isomorfismo"]),
        no_coincidentes=sum(1 for r in con_dist if not r["igual_salvo_isomorfismo"]),
        ultimo_error_mediana=med(ue), ultimo_error_max=max(ue) if ue else 0,
        trabajo_mediana=med(rp), trabajo_max=max(rp) if rp else 0,
        repasados_sobre_vida_mediana=round(med(rp) / vida, 4),
        repasados_sobre_vida_max=round((max(rp) if rp else 0) / vida, 3),
        retrocedidos_mediana=med(rt), retrocedidos_max=max(rt) if rt else 0,
        refutaciones_total=sum(r["refutaciones"] for r in con_dist),
        distinciones_en_inertes=sum(r["distinciones"] for r in inertes),
        inertes_con_mas_de_un_estado=sum(1 for r in inertes if r["estados_aprendidos"] > 1),
        futuro_min=min((r["futuro"] for r in medibles), default=None),
        futuro_perfecto=sum(1 for r in medibles if r["futuro"] == 1.0),
        sin_terminar_por_reloj=len(sin_term),
        indices_sin_terminar=sorted(r["idx"] for r in sin_term)[:200],
        medibles=len(medibles),
        topes_tocados=sum(1 for r in filas if r["tope_tocado"]),
        sin_explicacion=sum(v for k, v in clases.items() if k.startswith("SIN EXPLICACION")),
        cruce_discrepa=sum(1 for r in filas if r.get("cruce_coincide") is False),
        cruce_hecho=sum(1 for r in filas if "cruce_coincide" in r),
        clases=dict(clases), reloj_total_s=round(sum(r["reloj_s"] for r in filas), 2),
    )
    pct = 100.0 * s["identificadas_con_distincion"] / max(1, s["con_distincion"])
    out.write(f"  n={s['n']}: {s['sistemas']} sistemas · con distinción {s['con_distincion']} · "
              f"identificadas {s['identificadas_con_distincion']} ({pct:.1f} %) · inertes {s['inertes']} "
              f"con {s['distinciones_en_inertes']} distinciones abiertas\n")
    out.write(f"     último error: mediana {s['ultimo_error_mediana']}, máx {s['ultimo_error_max']} "
              f"(vida {vida}) · trabajo real: mediana {s['trabajo_mediana']}, máx {s['trabajo_max']} "
              f"· trabajo/vida: mediana {s['repasados_sobre_vida_mediana']}, máx {s['repasados_sobre_vida_max']} "
              f"· distancia retrocedida (contador de 02): mediana {s['retrocedidos_mediana']}, máx {s['retrocedidos_max']}\n")
    out.write(f"     futuro mínimo {s['futuro_min']:.4f} · perfecto en {s['futuro_perfecto']}/{s['medibles']} "
              f"· topes tocados {s['topes_tocados']} · SIN EXPLICACIÓN {s['sin_explicacion']} "
              f"· cruce: {s['cruce_hecho']} hechos, {s['cruce_discrepa']} discrepan "
              f"· sin terminar por reloj: {s['sin_terminar_por_reloj']} · {s['reloj_total_s']}s\n")
    out.write(f"     clases: {s['clases']}\n")
    return s


# --- cobertura declarada en la ficha §4, antes de correr
K_DECLARADA = {3: 1, 4: 1, 6: 20_000, 8: 10_000_000_000}


def puerta(res, out):
    """La puerta numérica de la ficha §11, evaluada sobre los números y no a ojo."""
    g, det = {}, {}
    g["(i) cero casos SIN EXPLICACIÓN en todo el banco"] = \
        all(r["sin_explicacion"] == 0 for r in res.values())
    g["(ii) cero distinciones abiertas en la clase inerte"] = \
        all(r["distinciones_en_inertes"] == 0 and r["inertes_con_mas_de_un_estado"] == 0
            for r in res.values())
    g["(iii) mediana de repasados <= 5x la vida en todo n"] = \
        all(r["repasados_sobre_vida_mediana"] <= 5 for r in res.values())
    g["(iii) máximo de repasados <= 100x la vida en todo n"] = \
        all(r["repasados_sobre_vida_max"] <= 100 for r in res.values())
    if 3 in res and 8 in res:
        base = res[3]["repasados_sobre_vida_mediana"] or 1e-9
        raz = res[8]["repasados_sobre_vida_mediana"] / base
        det["razon_repaso_por_vida_n8_sobre_n3"] = round(raz, 3)
        g["(iv) repasados/vida en n=8 no supera 10x la de n=3"] = raz <= 10
    if 8 in res:
        r8 = res[8]
        sin_excusa = sum(v for k, v in r8["clases"].items()
                         if k != "identificada" and not k.startswith("la vida no determina"))
        frac = sin_excusa / max(1, r8["con_distincion"])
        det["fraccion_sin_identificar_sin_excusa_n8"] = round(frac, 4)
        g["(iv) menos del 20 % sin identificar por causa distinta en n=8"] = frac < 0.20
    g["(iv) tope de estados tocado en menos del 1 % de los sistemas"] = all(
        r["topes_tocados"] / max(1, r["sistemas"]) < 0.01 for r in res.values())
    g["cruce con el retroceso exhaustivo: cero discrepancias en n<=4"] = \
        all(r.get("cruce_discrepa", 0) == 0 for r in res.values())
    det["sin_terminar_por_reloj_por_n"] = {str(n): r.get("sin_terminar_por_reloj", 0)
                                           for n, r in res.items()}
    g["actividad: hubo refutaciones en la clase con distinción"] = \
        all(r["refutaciones_total"] > 0 for r in res.values() if r["con_distincion"] > 0)

    out.write("\n--- puerta de la ficha §11, sobre los números\n")
    for k, v in g.items():
        out.write(f"  [{'PASS' if v else 'FAIL'}] {k}\n")
    for k, v in det.items():
        out.write(f"  · {k} = {v}\n")
    todo = all(g.values())
    out.write(f"VEREDICTO DE LA FASE 1: {'PASS' if todo else 'FAIL'}\n")
    return dict(criterios=g, detalle=det, veredicto="PASS" if todo else "FAIL")


def main(ns, aqui):
    buf = io.StringIO()
    rep = {"K_declarada": {str(k): v for k, v in K_DECLARADA.items()},
           "L_por_n": {str(n): L_de(n) for n in NS}, "futuro_max": FUTURO_MAX}
    jsonl = os.path.join(aqui, "artifacts", "unidad_minima_05_banco.jsonl")
    os.makedirs(os.path.dirname(jsonl), exist_ok=True)
    if 3 in ns:
        rep["mutantes"] = mutantes(3, buf)
    res = {}
    for n in ns:
        filas = campana_n(n, K_DECLARADA[n], jsonl, buf)
        res[n] = resumen(filas, buf)
    rep["por_n"] = {str(n): v for n, v in res.items()}
    if all(n in res for n in NS):
        rep["puerta"] = puerta(res, buf)
    return buf.getvalue(), rep


if __name__ == "__main__":
    aqui = os.path.dirname(os.path.abspath(__file__))
    ns = [int(x) for x in sys.argv[1:]] or list(NS)
    texto, rep = main(ns, aqui)
    sys.stdout.write(texto)
    rep["sha256_codigo"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    rep["python"] = sys.version.split()[0]
    rep["random_importado"] = ("random" in sys.modules)
    sys.stdout.write(f"sha256 del codigo: {rep['sha256_codigo'][:16]}… · python {rep['python']} · "
                     f"random importado: {'SI' if rep['random_importado'] else 'no'}\n")
    ruta = os.path.join(aqui, "artifacts", "unidad_minima_05_banco.json")
    previo = {}
    if os.path.exists(ruta):
        try:
            previo = json.load(open(ruta, encoding="utf-8"))
        except ValueError:
            previo = {}
    if "por_n" in previo:
        fusion = dict(previo["por_n"]); fusion.update(rep["por_n"]); rep["por_n"] = fusion
        if all(str(n) in fusion for n in NS):
            buf2 = io.StringIO()
            rep["puerta"] = puerta({int(k): v for k, v in fusion.items()}, buf2)
            sys.stdout.write(buf2.getvalue())
        rep.setdefault("mutantes", previo.get("mutantes"))
    with open(ruta, "w", encoding="utf-8") as f:
        json.dump(rep, f, ensure_ascii=False, indent=1)
