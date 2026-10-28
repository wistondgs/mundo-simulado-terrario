#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UNIDAD-MINIMA-08 · Fase 2 · ¿lo vivido se acumula?

Una unidad vive un mundo W1 (3 estados). Sin aviso, el mundo pasa a ser W2: el mismo
W1 con UN bit nuevo encima, que cambia en una sola situación (estado, letra). La unidad
sigue viviendo. Se compara con una unidad fresca que sólo vive W2, con el mismo
presupuesto de vida. Seis celdas, mismo código:

    F1 fresca, itinerario fijo          F3 fresca, ELIGE qué vivir
    C1 heredera, itinerario fijo        C3 heredera, ELIGE
    C2 heredera LESIONADA (máquina colapsada, memoria conservada), itinerario fijo
    C4 heredera lesionada, ELIGE

Dos clases de W2, mismo tamaño y misma salida:
    componible      las letras mueven x igual que en W1; el bit b depende de x
                    (la distinción de W1 sigue siendo congruencia: cascada de Krohn–Rhodes)
    no componible   cuando b = 1 las letras actúan intercambiadas sobre x
                    (la distinción de W1 deja de valer)

Heredar la máquina = seguir viviendo con la misma unidad de 02, que no sabe que el
mundo cambió: su reparación ya es local (retrocede a la última decisión). No hay una
línea nueva de herencia. Elegir qué vivir = en vez de la siguiente letra del
itinerario, ir por el camino más corto de la propia hipótesis hasta una transición
que nunca vio, y ejecutarla (acción epistémica mínima; sin oráculo, sin marca).

Medidas de DESARROLLO (ninguna de coste; el coste se registra y no decide):
    alcance        ¿identifica W2? (futuro fijo predicho sin un solo error y sin rutas vacías)
    exactitud      fracción del futuro fijo bien predicha
    repertorio     palabras (<= 3 letras) que escriben o permutan en su máquina final
    instruibilidad metas externas «reacción a L = v» cumplidas con palabra robusta,
                   verificada en el mundo real desde TODOS sus estados alcanzables
Registro: pasos avanzados (trabajo), refutaciones, estados, si agotó presupuesto.

Predicciones: ORIENTACIONES_FASE_2_RECETA.md §4. Sin azar. Doble corrida con hash.
"""
from __future__ import annotations

import hashlib
import io
import itertools
import json
import os
import sys
import time
from collections import Counter, deque

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unidad_minima_01 import (  # noqa: E402
    LETTERS, classify, lesion, monoid, predict, run_world, shortlex, states_of,
)
from unidad_minima_02_incremental import Unidad  # noqa: E402
from unidad_minima_05_banco import (  # noqa: E402
    L_de, alcanzables, canonica, cociente, mealy_verdadera, minimizar, paso_de,
    sistema_por_indice, total_sistemas,
)

N1 = 3                                   # estados de W1
PRESUPUESTO_PASOS = 200_000              # trabajo máximo por INTENTO de explicar; agotarlo dispara el olvido
VENTANA = 512                            # memoria acotada: la unidad retiene sus últimos 512 pasos
NUCLEO = 64                              # lo que conserva al olvidar: sus últimos 64 pasos
HITOS = (64, 128, 256, 512, 1024, 2048)  # la curva de alcance en W2, no el punto final
METAS = (("B", 1), ("A", 1))             # instrucción externa, como en 04
MAX_PALABRA_META = 4
BRAZOS = ("F1", "F3", "C1", "C3", "C2", "C4")


class PresupuestoAgotado(RuntimeError):
    pass


class UnidadFase2(Unidad):
    """La unidad de 02 con tres añadidos declarados: contador de trabajo real,
    presupuesto, y MEMORIA ACOTADA (ventana).

    HALLAZGO DEL PILOTO (27-oct, 12 familias): la unidad de 02 tal cual, que exige UNA
    máquina consistente con TODO lo vivido, se ahoga cuando el mundo cambia: 12/12
    herederas agotaron 3 000 000 de pasos sin identificar nada, mientras la fresca
    identificó 12/12. Un ser que no puede olvidar no puede vivir en un mundo que
    cambia (Cropper 2020: una biblioteca sin podar deja de servir). La ventana es la
    forma mínima de olvido: lo que sale de ella queda como transición FIJA de la
    hipótesis (ya no se revisa) hasta que una refutación sin salida obliga a releer
    sólo la ventana. Misma ventana en las seis celdas.
    """

    def leer(self, a, o):
        while len(self.trace) >= VENTANA:
            self.trace.pop(0)
            for cp in self.choices:
                cp[0] -= 1
            self.choices = [cp for cp in self.choices if cp[0] >= 0]
            self.c["pasos_olvidados"] += 1
        self._intento = 0
        try:
            return Unidad.leer(self, a, o)
        except (PresupuestoAgotado, RuntimeError):
            self._olvidar()

    def _olvidar(self):
        """OLVIDO POR FRACASO (segundo hallazgo del piloto, 27-oct). Con ventana de 512 la
        heredera seguía ahogándose (21/21 y 44/44 celdas agotadas): la ventana aún
        contenía el mundo viejo y ninguna máquina de <= 8 estados explica los dos a la
        vez. Y mi bucle la mataba al agotarse, que es un error de instrumento: un ser
        que no logra explicar no deja de vivir. Regla interna, sin aviso externo: si
        explicar la memoria cuesta más que el presupuesto o pide más estados que el
        tope, la unidad conserva sólo sus últimos NUCLEO pasos y empieza de nuevo
        sobre ellos. Es el disparador de 03 («no explico mi memoria») llevado a su
        consecuencia: lo que no se puede explicar junto, se suelta."""
        self.c["olvidos"] += 1
        nucleo = self.trace[-NUCLEO:]
        self.trace, self.trans, self.choices, self.q, self.n, self.used = [], {}, [], 0, 1, 1
        self._intento = 0
        try:
            for a, o in nucleo:
                self.trace.append((a, o))
                # releer el núcleo con el mecanismo de 02, paso a paso
                i = len(self.trace) - 1
                Unidad.leer(self, *self.trace.pop())
        except (PresupuestoAgotado, RuntimeError):
            self.trace, self.trans, self.choices, self.q, self.n, self.used = [], {}, [], 0, 1, 1
            self.c["olvidos_totales"] += 1

    def _avanzar(self, i, a, o):
        self.c["pasos_avanzados"] += 1
        self._intento = getattr(self, "_intento", 0) + 1
        if self._intento > PRESUPUESTO_PASOS:
            raise PresupuestoAgotado()
        return Unidad._avanzar(self, i, a, o)

    # --- elegir qué vivir: la transición no vista más cercana en la propia hipótesis
    def letra_elegida(self):
        if not self.trans:
            return None
        qs = states_of(self.trans)
        for a in LETTERS:                        # agujero aquí mismo
            if (self.q, a) not in self.trans:
                return a
        vistos, cola = {self.q}, deque([(self.q, None)])
        while cola:
            s, primera = cola.popleft()
            for a in LETTERS:
                t = self.trans.get((s, a))
                if t is None:
                    continue
                s2 = t[0]
                if s2 in vistos:
                    continue
                vistos.add(s2)
                f = primera if primera is not None else a
                if any((s2, b) not in self.trans for b in LETTERS):
                    return f
                cola.append((s2, f))
        return None                              # hipótesis completa: nada que preguntar


# ---------------------------------------------------------------------------
# Los mundos
# ---------------------------------------------------------------------------
def patrones(n):
    """El bit nuevo es un CERROJO (latch): se pone a 1 en la situación (A, x_s) y a 0 en
    la situación (B, x_r). DEFECTO DEL PILOTO corregido: un bit que sólo se CONMUTA en una
    situación nunca influye en la salida (la conmutación no depende de b), así que era
    inobservable y toda la clase componible quedó descartada (0 familias). El cerrojo sí
    depende de b: ponerlo cuando ya está puesto no cambia nada."""
    for xs in range(n):
        for xr in range(n):
            yield (xs, xr)


def mundo_2(A, B, n, patron, componible):
    x_set, x_reset = patron
    tablas = {"A": A, "B": B}
    A2, B2 = [0] * (2 * n), [0] * (2 * n)
    for b in (0, 1):
        for x in range(n):
            for letra, T2 in (("A", A2), ("B", B2)):
                if componible or b == 0:
                    y = tablas[letra][x]
                else:                            # dependencia invertida: b reescribe la acción
                    y = tablas["B" if letra == "A" else "A"][x]
                if letra == "A" and x == x_set:
                    b2 = 1
                elif letra == "B" and x == x_reset:
                    b2 = 0
                else:
                    b2 = b
                T2[x + n * b] = y + n * b2
    return tuple(A2), tuple(B2)


def verdad(A, B):
    est = alcanzables(A, B)
    Tv = mealy_verdadera(A, B, est)
    n_min, bloque = minimizar(Tv, est)
    Mmin, ini = cociente(Tv, est, bloque)
    return est, n_min, canonica(Mmin, ini)


# ---------------------------------------------------------------------------
# Vivir
# ---------------------------------------------------------------------------
def vivir(u, step, x, itinerario, elige, futuro=None):
    err = ultimo = sin_ruta = 0
    agotado = False
    it = iter(itinerario)
    pasos_elegidos = 0
    curva = {}
    for t in range(1, len(itinerario) + 1):
        if futuro is not None and t - 1 in HITOS:
            truth, _ = run_world(step, x, futuro)
            hits, nr, _ = predict(u.trans, u.q, futuro, truth)
            curva[t - 1] = dict(exactitud=hits / len(futuro), identifica=(hits == len(futuro) and nr == 0))
        a = u.letra_elegida() if elige else None
        if a is None:
            a = next(it)
        else:
            pasos_elegidos += 1
        p = u.predecir(a)
        if p is None:
            sin_ruta += 1
            p = 0
        x, o = step(x, a)
        if p != o:
            err += 1
            ultimo = t
        u.leer(a, o)
    agotado = u.c["olvidos"]
    if futuro is not None:
        truth, _ = run_world(step, x, futuro)
        hits, nr, _ = predict(u.trans, u.q, futuro, truth)
        fin = dict(exactitud=hits / len(futuro), identifica=(hits == len(futuro) and nr == 0))
        for h in HITOS:                      # si cortó antes de un hito, lo que sabe es lo que sabe
            curva.setdefault(h, fin)
    return dict(x=x, errores=err, ultimo_error=ultimo, sin_ruta=sin_ruta,
                agotado=agotado, pasos_elegidos=pasos_elegidos, curva=curva)


def repertorio(M):
    qs = states_of(M)
    tabla = monoid(M, qs, True)
    cls = Counter(classify(m, qs) for m in tabla)
    return dict(escribe=cls["escribe"], permuta=cls["permuta"], clases=len(tabla))


def palabra_robusta(M, letra, valor):
    """La palabra más corta que, según M, cumple la meta desde TODOS sus estados (04)."""
    qs = states_of(M)
    for k in range(0, MAX_PALABRA_META + 1):
        for w in itertools.product(LETTERS, repeat=k):
            ok = True
            for q in qs:
                for a in w:
                    t = M.get((q, a))
                    if t is None:
                        ok = False
                        break
                    q = t[0]
                if not ok:
                    break
                t = M.get((q, letra))
                if t is None or t[1] != valor:
                    ok = False
                    break
            if ok:
                return w
    return None


def instruibilidad(M, step, estados_reales):
    cumplidas = 0
    for letra, valor in METAS:
        w = palabra_robusta(M, letra, valor)
        if w is None:
            continue
        bien = True
        for x0 in estados_reales:
            x = x0
            for a in w:
                x, _ = step(x, a)
            _, o = step(x, letra)
            if o != valor:
                bien = False
                break
        cumplidas += int(bien)
    return cumplidas


def medir(u, step, x, futuro, estados_reales, extra):
    truth, _ = run_world(step, x, futuro)
    hits, nr, _ = predict(u.trans, u.q, futuro, truth)
    N = len(futuro)
    r = dict(exactitud=hits / N, sin_ruta_futuro=nr,
             identifica=(hits == N and nr == 0),
             estados=u.n, pasos_avanzados=u.c["pasos_avanzados"],
             refutaciones=u.c["refutaciones"], memoria=len(u.trace),
             instruibilidad=instruibilidad(u.trans, step, estados_reales))
    r.update(repertorio(u.trans))
    r.update(extra)
    return r


def una_familia(idx, patron, componible, vida1, vida2, fut1, fut2, n_max):
    A, B = sistema_por_indice(N1, idx)
    A2, B2 = mundo_2(A, B, N1, patron, componible)
    step1, step2 = paso_de(A, B), paso_de(A2, B2)
    est2, nmin2, _ = verdad(A2, B2)
    filas = []
    # --- la vida en W1, compartida por todos los brazos herederos
    madre = UnidadFase2(n_max=n_max)
    v1 = vivir(madre, step1, 0, vida1, False)
    est1 = alcanzables(A, B)
    m1 = medir(madre, step1, v1["x"], fut1, est1, dict(olvidos=v1["agotado"]))
    base = dict(w1=idx, patron=f"{patron[0]}@{patron[1]}", clase="componible" if componible else "no_componible",
                n_min_w2=nmin2, w1_identificado=m1["identifica"], repertorio_w1=m1["escribe"] + m1["permuta"])
    x_cambio = v1["x"]                    # el mundo cambia donde W1 quedó; b empieza en 0
    for brazo in BRAZOS:
        elige = brazo in ("F3", "C3", "C4")
        if brazo.startswith("F"):
            u = UnidadFase2(n_max=n_max)
        else:
            u = UnidadFase2(n_max=n_max)
            u.trace, u.trans, u.choices = list(madre.trace), dict(madre.trans), [list(c) for c in madre.choices]
            u.q, u.n, u.used, u.c = madre.q, madre.n, madre.used, Counter(madre.c)
            u.c["pasos_avanzados"] = 0
            if brazo in ("C2", "C4"):     # lesión: la máquina se colapsa, la memoria queda
                u.trans, u.choices, u.q, u.n, u.used = lesion(u.trans), [], 0, 1, 1
        v2 = vivir(u, step2, x_cambio, vida2, elige, fut2)
        m2 = medir(u, step2, v2["x"], fut2, est2,
                   dict(brazo=brazo, errores=v2["errores"], ultimo_error=v2["ultimo_error"],
                        olvidos=v2["agotado"], pasos_elegidos=v2["pasos_elegidos"],
                        curva=v2["curva"], olvidados=u.c["pasos_olvidados"]))
        m2.update(base)
        m2["repertorio"] = m2["escribe"] + m2["permuta"]
        m2["curva"][len(vida2)] = dict(exactitud=m2["exactitud"], identifica=m2["identifica"])
        filas.append(m2)
    return filas


def mundos_1(vida1, fut1, n_max, out):
    """W1 elegibles: alcanzable con n_min >= 2 y que la unidad identifica en su vida."""
    elegibles, total, nmin2, vistos = [], 0, 0, set()
    for idx in range(total_sistemas(N1)):
        A, B = sistema_por_indice(N1, idx)
        est, n_min, canon = verdad(A, B)
        total += 1
        if n_min < 2:
            continue
        nmin2 += 1
        u = UnidadFase2(n_max=n_max)
        v = vivir(u, paso_de(A, B), 0, vida1, False)
        m = medir(u, paso_de(A, B), v["x"], fut1, est, {})
        if m["identifica"]:
            if canon in vistos:              # un W1 por clase de isomorfismo: relabelar no es replicar
                continue
            vistos.add(canon)
            elegibles.append(idx)
    out.write(f"W1: {total} sistemas de {N1} estados; {nmin2} con n_min >= 2; "
              f"{len(elegibles)} identificados por la unidad y distintos salvo isomorfismo → elegibles\n")
    return elegibles


def _una_w1(args):
    idx, vida1, vida2, fut1, fut2, n_max = args
    A, B = sistema_por_indice(N1, idx)
    _, nmin1, _ = verdad(A, B)
    filas, descartadas = [], 0
    for comp in (True, False):
        for patron in patrones(N1):
            A2, B2 = mundo_2(A, B, N1, patron, comp)
            _, nmin2, _ = verdad(A2, B2)
            if nmin2 <= nmin1:            # el bit nuevo no abre ninguna distinción nueva
                descartadas += 1
                continue
            filas.extend(una_familia(idx, patron, comp, vida1, vida2, fut1, fut2, n_max))
    return filas, descartadas


def campana(out, limite_w1=None, trabajadores=1):
    vida1 = shortlex(range(1, L_de(N1) + 1))
    vida2 = shortlex(range(1, L_de(2 * N1) + 1))
    fut1 = shortlex((L_de(N1) + 1, L_de(N1) + 2))
    fut2 = shortlex((2 * N1, 2 * N1 + 1))     # palabras de 6 y 7 letras: separan cualquier par de 6 estados
    n_max = 2 * N1 + 2
    out.write(f"vida en W1: {len(vida1)} pasos; vida en W2: {len(vida2)} pasos; futuro W2: {len(fut2)} pasos; "
              f"tope de estados {n_max}; presupuesto {PRESUPUESTO_PASOS} pasos avanzados por celda\n")
    elegibles = mundos_1(vida1, fut1, n_max, out)
    if limite_w1:
        elegibles = elegibles[:limite_w1]
    filas, descartadas = [], 0
    t0 = time.perf_counter()
    tareas = [(idx, vida1, vida2, fut1, fut2, n_max) for idx in elegibles]
    if trabajadores > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(trabajadores) as pool:
            res = pool.map(_una_w1, tareas, chunksize=1)   # map conserva el orden: determinista
    else:
        res = [_una_w1(t) for t in tareas]
    for f, d in res:
        filas.extend(f)
        descartadas += d
    out.write(f"familias (W1, W2) corridas: {len(filas) // len(BRAZOS)}; descartadas por no abrir "
              f"distinción nueva: {descartadas}\n\n")
    sys.stderr.write(f"reloj: {time.perf_counter() - t0:.1f} s\n")
    return filas


def resumen(filas, out):
    R = {}
    for clase in ("componible", "no_componible"):
        F = [f for f in filas if f["clase"] == clase]
        if not F:
            continue
        fam = len(F) // len(BRAZOS)
        out.write(f"=== clase {clase}: {fam} familias\n")
        out.write(f"{'brazo':<6}{'alcance':>9}{'exactitud':>11}{'repert.':>9}{'Δrep.':>7}{'instr.':>8}"
                  f"{'estados':>9}{'olvidos':>8}{'trabajo medio':>15}{'elegidos':>10}  (alcance/exactitud = al FINAL de W2)\n")
        R[clase] = {}
        for b in BRAZOS:
            Fb = [f for f in F if f["brazo"] == b]
            k = len(Fb)
            r = dict(
                alcance=sum(f["identifica"] for f in Fb) / k,
                exactitud=sum(f["exactitud"] for f in Fb) / k,
                repertorio=sum(f["repertorio"] for f in Fb) / k,
                delta_repertorio=sum(f["repertorio"] - f["repertorio_w1"] for f in Fb) / k,
                instruibilidad=sum(f["instruibilidad"] for f in Fb) / k,
                estados=sum(f["estados"] for f in Fb) / k,
                agotados=sum(f["olvidos"] for f in Fb),
                trabajo=sum(f["pasos_avanzados"] for f in Fb) / k,
                elegidos=sum(f["pasos_elegidos"] for f in Fb) / k,
            )
            R[clase][b] = r
            out.write(f"{b:<6}{r['alcance']:>9.3f}{r['exactitud']:>11.4f}{r['repertorio']:>9.2f}"
                      f"{r['delta_repertorio']:>+7.2f}{r['instruibilidad']:>8.2f}{r['estados']:>9.2f}"
                      f"{r['agotados']:>8}{r['trabajo']:>15.0f}{r['elegidos']:>10.1f}\n")
        hitos = sorted({int(k) for f in F for k in f["curva"]})
        out.write("curva de alcance (fracción que identifica W2) por pasos vividos en W2:\n")
        out.write(f"{'brazo':<6}" + "".join(f"{h:>8}" for h in hitos) + f"{'media':>8}\n")
        for b in BRAZOS:
            Fb = [f for f in F if f["brazo"] == b]
            fila = [sum(f["curva"][h]["identifica"] for f in Fb) / len(Fb) for h in hitos]
            R[clase][b]["curva_alcance"] = dict(zip(hitos, fila))
            R[clase][b]["alcance_medio_curva"] = sum(fila) / len(fila)
            out.write(f"{b:<6}" + "".join(f"{v:>8.3f}" for v in fila) + f"{sum(fila) / len(fila):>8.3f}\n")
        # pareado por familia: ¿en cuántas familias la heredera identifica y la fresca no, y al revés?
        por_fam = {}
        for f in F:
            por_fam.setdefault((f["w1"], f["patron"]), {})[f["brazo"]] = f
        def pares(a, b):
            solo_a = sum(1 for d in por_fam.values() if d[a]["identifica"] and not d[b]["identifica"])
            solo_b = sum(1 for d in por_fam.values() if d[b]["identifica"] and not d[a]["identifica"])
            return solo_a, solo_b
        for a, b in (("C1", "F1"), ("C3", "F3"), ("F3", "F1"), ("C3", "C1"), ("C2", "F1"), ("C2", "C1")):
            sa, sb = pares(a, b)
            R[clase][f"{a}_vs_{b}"] = dict(solo_primero=sa, solo_segundo=sb)
            out.write(f"  pareado {a} vs {b}: identifica sólo {a} en {sa} familias; sólo {b} en {sb}\n")
        out.write("\n")
    return R


def puerta(R, out):
    g = {}
    c, nc = R.get("componible", {}), R.get("no_componible", {})
    if c:
        A = lambda b: c[b]["alcance_medio_curva"]
        g["P1 acumulación: C1 > F1 en alcance a lo largo de la vida (componible)"] = A("C1") > A("F1")
        g["P2 elegir: F3 > F1 en alcance a lo largo de la vida"] = A("F3") > A("F1")
        g["P2 elegir: C3 > C1 en alcance a lo largo de la vida"] = A("C3") > A("C1")
        g["P4 lesión: C2 ≈ F1 (|Δ alcance medio| <= 0.02)"] = abs(A("C2") - A("F1")) <= 0.02
        g["P5 repertorio: C1 >= F1 al final de W2"] = c["C1"]["repertorio"] >= c["F1"]["repertorio"]
        g["P5 instruibilidad: C1 >= F1"] = c["C1"]["instruibilidad"] >= c["F1"]["instruibilidad"]
        act = any(c[b]["elegidos"] > 0 for b in ("F3", "C3", "C4"))
        g["actividad: el órgano 'elegir' actuó"] = act
    if nc:
        g["P1 control: C1 <= F1 en alcance a lo largo de la vida (no componible)"] = \
            nc["C1"]["alcance_medio_curva"] <= nc["F1"]["alcance_medio_curva"]
    out.write("--- puerta (receta §4)\n")
    for k, v in g.items():
        out.write(f"  [{'PASS' if v else 'FAIL'}] {k}\n")
    if c:
        fals = (abs(A("C1") - A("F1")) <= 0.02 and abs(A("C3") - A("F3")) <= 0.02)
        out.write(f"  [{'SE CUMPLE' if fals else 'no'}] falsador: heredar no cambia el alcance ni con ni sin elegir\n")
    return g


def guardar_filas(filas, ruta):
    with open(ruta, "w", encoding="utf-8") as f:
        for fila in filas:
            f.write(json.dumps(fila, ensure_ascii=False) + "\n")


def main(limite_w1=None, trabajadores=1, ruta_filas=None):
    buf = io.StringIO()
    filas = campana(buf, limite_w1, trabajadores)
    if ruta_filas:
        guardar_filas(filas, ruta_filas)     # antes del resumen: un resumen que falla no borra la corrida
    R = resumen(filas, buf)
    g = puerta(R, buf)
    return buf.getvalue(), filas, R, g


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    lim = int(args[0]) if args else None
    trab = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--trabajadores=")), 1)
    doble = "--doble" in sys.argv
    suf = f"_pilot{lim}" if lim else ""
    os.makedirs(os.path.join(here, "artifacts"), exist_ok=True)
    ruta = os.path.join(here, "artifacts", f"unidad_minima_08_fase2{suf}.jsonl")
    t1, filas, R, g = main(lim, trab, ruta)
    sys.stdout.write(t1)
    if doble:
        t2, _, _, _ = main(lim, trab)
        h1, h2 = (hashlib.sha256(t.encode()).hexdigest() for t in (t1, t2))
        sys.stdout.write(f"determinismo: {'IDÉNTICAS' if h1 == h2 else 'DIFIEREN'}\n")
    src = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    sys.stdout.write(f"random usado en nuestros módulos: no (no se importa); sha256 del código: {src[:16]}…\n")
    with open(os.path.join(here, "artifacts", f"unidad_minima_08_fase2{suf}.json"), "w", encoding="utf-8") as f:
        json.dump(dict(resumen=R, puerta=g, sha256_codigo=src, texto=t1), f, ensure_ascii=False, indent=1)
