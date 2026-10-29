#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UNIDAD-MINIMA-09 · Fase 2 · C5 (heredar la máquina sin la traza) y los seis mutantes.

**No toca `unidad_minima_08_fase2.py`: lo IMPORTA.** Igual que 05b importaba a 05, así
«C5 corre en la misma campaña que F1» es estructural y no una afirmación: el mundo, la
vida, el futuro fijo, las cuatro medidas y el filtro de familias son LITERALMENTE los
de 08. Lo único nuevo aquí es el brazo C5, los seis mutantes de la ficha (§10 de
`APERTURA_FASE_2_ACUMULACION.md`) y la comprobación de la garantía que C5 cede.

C5 (§5-bis de la ficha): al cambiar el mundo la unidad conserva `trans` y `q` y **vacía
la memoria**. Con 02 tal cual eso no funciona — la primera refutación de una transición
heredada encuentra la pila de decisiones vacía, abre un estado nuevo y relee una memoria
vacía: la máquina heredada se borra. La reparación es **local**: cuando se refuta una
transición heredada que no tiene decisión en la pila, esa transición se vuelve revisable
**en el paso actual** (se empuja como decisión con el destino que toca ahora) en vez de
disparar la relectura.

Lo que se pierde al hacer eso, dicho antes de medirlo: la búsqueda de 02 deja de ser
exhaustiva en orden canónico sobre la traza, porque las transiciones heredadas se
eligieron sobre otra traza que ya no está. Se pierde la **minimalidad** y con ella la
coincidencia con 01. Lo que queda es **consistencia con la traza retenida**, y las dos
cosas se miden celda a celda: `c5_consistente` (debe ser 1,000), `c5_minima` (se espera
< 1,000: ésa es la garantía cedida) y `c5_estados_sobre_minimo`.

Sin azar. Doble corrida con hash. El cómputo se registra y no decide (norma de Wis).
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import time
from collections import Counter, deque
from statistics import NormalDist

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unidad_minima_08_fase2 as m8                                      # noqa: E402
from unidad_minima_01 import LETTERS, lesion, shortlex, states_of        # noqa: E402
from unidad_minima_02_incremental import Unidad                          # noqa: E402
from unidad_minima_05_banco import L_de, alcanzables, paso_de, sistema_por_indice  # noqa: E402
from unidad_minima_08_fase2 import (                                     # noqa: E402
    HITOS, N1, PRESUPUESTO_PASOS, PresupuestoAgotado, UnidadFase2,
    medir, mundo_2, mundos_1, patrones, verdad, vivir,
)
from guardas import (  # noqa: E402
    GuardaViolada, informe, no_vacio, salida_a_fichero, sin_azar_usado,
)

ALFA = 0.05                 # mismo alfa que E-18, repartido por Bonferroni entre comparaciones
TOPE_MINIMA = 2_000_000     # pasos de búsqueda al recomputar la mínima de una traza (E-32: lo que
                            # valida la campaña también lleva tope; sin él, 4 h para cero filas)
PRESUPUESTO_MC = 3_000_000   # M-c: 15× el presupuesto normal por INTENTO. «Infinito» no es
                             # medible (E-32); agotar un presupuesto declarado y grande ES la
                             # firma del ahogo
TOPE_CELDA_MC = 20_000_000   # y un tope por CELDA, porque sin olvido y sin `break` la celda no
                             # termina: al alcanzarlo la unidad queda PARALIZADA —sigue viviendo
                             # con la hipótesis que tenga y deja de intentar explicar—, que es
                             # exactamente lo que «no puedo explicar mi memoria» significa cuando
                             # explicarla no se puede pagar. Se cuenta `pasos_sin_aprender`
BRAZOS = ("F1", "C5", "M-e", "M-f")

# E-49 · el sha256 del fuente se calcula AL IMPORTARSE, no al terminar la corrida: si el
# fichero se edita mientras la campaña corre, el hash del artefacto sería de un código que
# no corrió. Lo mismo para el módulo importado.
SHA_09 = hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()
SHA_08 = hashlib.sha256(open(m8.__file__, "rb").read()).hexdigest()
ARRANQUE = time.strftime("%Y-%m-%dT%H:%M:%S")

# Los criterios que la puerta de la ficha §11 enumera. El programa informa cuáles evalúa y
# cuáles NO: una puerta que calla los que le faltan deja el veredicto en manos de la prosa
# (E-50, el error más caro de esta fase).
CRITERIOS_FICHA = {
    "a": "c5_consistente == 1,000 en todas las celdas C5",
    "b": "los seis mutantes se comportan como §10 dice",
    "c": "acumulación: C5 > F1 en el hito 64 (componible) con z sobre el umbral; y C5 <= F1 en el control",
    "d": "no sobreatribución: C1 <= F1 en los tres hitos (componible) y C2 ~ C1",
    "e": "repertorio: C5 >= F1 en la clase componible",
    "f": "actividad: transiciones_heredadas_revisadas > 0",
    "g": "no saturación: en el hito 64 hay varianza entre brazos por encima del ruido; si no, NULO",
}


# ---------------------------------------------------------------------------
# C5 · la unidad que hereda la máquina y no la traza
# ---------------------------------------------------------------------------
class UnidadC5(UnidadFase2):
    """Hereda `trans` y `q`; memoria vacía; reparación local de lo heredado."""

    def heredar(self, madre):
        self.original = dict(madre.trans)      # para contar supervivientes al final
        self.trans = dict(madre.trans)
        self.heredadas = set(self.trans)       # las que aún no se han revisado aquí
        self.q, self.n, self.used = madre.q, madre.n, madre.used
        self.trace, self.choices = [], []      # ← la traza NO se hereda: eso es C5
        self.c = Counter(madre.c)
        self.c["pasos_avanzados"] = 0
        self.refutaciones_al_heredar = self.c["refutaciones"]
        self.c["transiciones_heredadas"] = len(self.original)

    def leer(self, a, o):
        antes = self.c["distinciones_abiertas"]
        r = UnidadFase2.leer(self, a, o)
        if self.c["distinciones_abiertas"] > antes and self.heredadas:
            # la pila se agotó sin que la transición culpable fuera heredada: 02 abre un
            # estado y vacía `trans`. La herencia se perdió por ahí, y se cuenta: es el
            # otro camino por el que C5 puede degenerar en F1, y hay que poder verlo.
            self.c["herencia_borrada_por_distincion"] += 1
            self.heredadas = set()
        return r

    def _avanzar(self, i, a, o):
        key = (self.q, a)
        if key in self.heredadas and self.trans.get(key, (None, None))[1] != o:
            # REPARACIÓN LOCAL: en vez de retroceder (no hay a dónde: la traza empezó
            # vacía), la transición heredada se vuelve revisable aquí mismo, con el
            # destino enumerado desde 0 y la reacción que acaba de leerse.
            self.c["pasos_avanzados"] += 1
            self._intento = getattr(self, "_intento", 0) + 1
            if self._intento > self.presupuesto:
                raise PresupuestoAgotado()
            self.heredadas.discard(key)
            self.c["transiciones_heredadas_revisadas"] += 1
            self.choices.append([i, key, 0, self.used])
            self.trans[key] = (0, o)
            self.used = max(self.used, 1)
            self.q = 0
            return True
        return UnidadFase2._avanzar(self, i, a, o)

    def supervivientes(self):
        orig = getattr(self, "original", {})
        return sum(1 for k, v in orig.items() if self.trans.get(k) == v)


# El presupuesto vive en la instancia (M-c lo sube) y por defecto es el de 08.
UnidadFase2.presupuesto = PRESUPUESTO_PASOS
UnidadC5.presupuesto = PRESUPUESTO_PASOS


class UnidadMb(UnidadFase2):
    """M-b · elegir AL REVÉS: la transición no vista más LEJANA de la propia hipótesis.
    Mismo mecanismo, criterio invertido. Si gana, el órgano no es lo que creemos."""

    def letra_elegida(self):
        if not self.trans:
            return None
        vistos, cola, ultima = {self.q}, deque([(self.q, None)]), None
        for a in LETTERS:                                  # el agujero de aquí mismo cuenta como el más cercano
            if (self.q, a) not in self.trans:
                ultima = a
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
                    ultima = f                             # no devuelve: sigue buscando más lejos
                cola.append((s2, f))
        return ultima


class UnidadMa(UnidadFase2):
    """M-a · OLVIDO TOTAL (núcleo = 0): al fracasar no conserva nada y empieza de cero.
    Debe quedar ≈ fresca con retraso; si queda IGUAL que con núcleo 64, esos 64 pasos no
    aportan nada y hay que decirlo.

    No se puede hacer poniendo `NUCLEO = 0` en 08: `self.trace[-0:]` es la traza ENTERA,
    no la vacía, así que el mutante habría conservado TODO y no habría probado nada —un
    mutante que no puede saltar (E-44). Por eso el olvido total se escribe aparte.
    """

    def _olvidar(self):
        self.c["olvidos"] += 1
        self.trace, self.trans, self.choices, self.q, self.n, self.used = [], {}, [], 0, 1, 1
        self._intento = 0


class UnidadMc(UnidadFase2):
    """M-c · SIN OLVIDO: presupuesto grande, tope 8 estados, `_olvidar` desactivado y
    sin `break` (agotar el presupuesto no termina la vida: E-39). Debe reproducir el
    ahogo del piloto —curva plana, 100 % de celdas en el tope—. Es la verificación con
    ojos frescos del hallazgo del que depende todo C5."""

    presupuesto = PRESUPUESTO_MC
    tope_celda = TOPE_CELDA_MC

    def _olvidar(self):
        self.c["topes"] += 1       # no olvida, no muere: se queda con lo que el mecanismo dejó

    def leer(self, a, o):
        if self.c["pasos_avanzados"] >= self.tope_celda:
            self.c["pasos_sin_aprender"] += 1   # paralizada: vive y ya no intenta explicar
            return
        return UnidadFase2.leer(self, a, o)


def _avanzar_con_presupuesto(self, i, a, o):
    """El `_avanzar` de 08 mira la constante del módulo; aquí el presupuesto es de la
    instancia para que M-c pueda subirlo sin tocar a 08 ni a las demás celdas."""
    self.c["pasos_avanzados"] += 1
    self._intento = getattr(self, "_intento", 0) + 1
    if self._intento > self.presupuesto:
        raise PresupuestoAgotado()
    return Unidad._avanzar(self, i, a, o)


UnidadFase2._avanzar = _avanzar_con_presupuesto


# Las clases de unidad que el pool puede reconstruir tras el fork. Se deriva de lo
# definido en este módulo en vez de escribirse a mano: una lista a mano se queda corta
# en silencio (pasó con UnidadMa en la primera corrida de los mutantes).
CLASES = {c.__name__: c for c in (UnidadFase2, UnidadC5, UnidadMa, UnidadMb, UnidadMc)}


# ---------------------------------------------------------------------------
# La garantía que C5 cede, medida
# ---------------------------------------------------------------------------
def explica(trans, trace):
    """¿Existe un estado desde el que la máquina reproduce TODA la traza retenida?
    (Con ventana de memoria la traza se trunca por la izquierda, así que el estado
    inicial de la traza no es necesariamente el 0; se prueban todos.)"""
    estados = sorted(set(states_of(trans)) | {0})
    for q0 in estados:
        q, ok = q0, True
        for a, o in trace:
            t = trans.get((q, a))
            if t is None or t[1] != o:
                ok = False
                break
            q = t[0]
        if ok:
            return True
    return not trace


def minima_con_tope(trace, n_max, tope=TOPE_MINIMA):
    """`minimal_mealy` de 01 con tope de pasos de búsqueda. Devuelve (n, agotado):
    n = estados de la mínima, o None si se agotó el tope o ninguna de <= n_max explica."""
    T = len(trace)
    if T == 0:
        return 1, False
    sys.setrecursionlimit(max(10000, 4 * T + 100))
    pasos = [0]

    class Agotado(Exception):
        pass

    for n in range(1, n_max + 1):
        def search(i, q, trans, used):
            pasos[0] += 1
            if pasos[0] > tope:
                raise Agotado()
            if i == T:
                return True
            a, o = trace[i]
            key = (q, a)
            if key in trans:
                q2, o2 = trans[key]
                return o2 == o and search(i + 1, q2, trans, used)
            for q2 in range(min(used + 1, n)):
                trans[key] = (q2, o)
                if search(i + 1, q2, trans, max(used, q2 + 1)):
                    return True
                del trans[key]
            return False

        try:
            if search(0, 0, {}, 1):
                return n, False
        except Agotado:
            return None, True
    return None, False


# ---------------------------------------------------------------------------
# Una familia (W1, W2) con los brazos de 09
# ---------------------------------------------------------------------------
def _construir(brazo, madre, n_max, clase_fresca=UnidadFase2):
    """Cada brazo, con lo que se le da y lo que se le quita, en un solo sitio."""
    if brazo in ("F1", "F3"):
        return clase_fresca(n_max=n_max)
    if brazo == "M-e":
        # fresca CON la vida de la heredera: vivió W1 y se borra TODO al cambiar.
        # Debe coincidir exactamente con F1; si no, algo se filtra del mundo viejo.
        u = clase_fresca(n_max=n_max)
        u.trace, u.trans, u.choices, u.q, u.n, u.used, u.c = [], {}, [], 0, 1, 1, Counter()
        return u
    if brazo in ("C1", "C3"):
        u = clase_fresca(n_max=n_max)
        u.trace, u.trans, u.choices = list(madre.trace), dict(madre.trans), [list(c) for c in madre.choices]
        u.q, u.n, u.used, u.c = madre.q, madre.n, madre.used, Counter(madre.c)
        u.c["pasos_avanzados"] = 0
        return u
    if brazo in ("C2",):
        u = _construir("C1", madre, n_max, clase_fresca)
        u.trans, u.choices, u.q, u.n, u.used = lesion(u.trans), [], 0, 1, 1
        return u
    if brazo in ("C5", "M-f"):
        u = UnidadC5(n_max=n_max)
        u.heredar(madre)
        if brazo == "M-f":
            # hereda y SE IGNORA lo heredado: la hipótesis queda vacía antes del primer
            # paso. Debe dar exactamente F1; si no, C5 no mide la herencia.
            u.trans, u.heredadas, u.q, u.n, u.used = {}, set(), 0, 1, 1
        return u
    raise ValueError(brazo)


def una_familia(idx, patron, componible, vida1, vida2, fut1, fut2, n_max,
                brazos=BRAZOS, clase=UnidadFase2, con_garantia=True, intercambio=False):
    A, B = sistema_por_indice(N1, idx)
    if intercambio:
        # CONTROL DE ASIMETRÍA A↔B, pendiente desde la Fase 1 (§7 de la ficha). La unidad
        # recorre el itinerario shortlex —que empieza por A— y rompe sus empates hacia A;
        # intercambiar las dos tablas del mundo es exactamente intercambiar itinerario y
        # desempates, sin tocar ni el mecanismo ni la medida. Si una conclusión cambia de
        # signo al intercambiar, no era una conclusión sobre el ser: era sobre la letra A.
        A, B = B, A
    A2, B2 = mundo_2(A, B, N1, patron, componible)
    step1, step2 = paso_de(A, B), paso_de(A2, B2)
    est2, nmin2, _ = verdad(A2, B2)
    madre = clase(n_max=n_max)
    v1 = vivir(madre, step1, 0, vida1, False)
    m1 = medir(madre, step1, v1["x"], fut1, alcanzables(A, B), dict(olvidos=v1["agotado"]))
    base = dict(w1=idx, patron=f"{patron[0]}@{patron[1]}",
                clase="componible" if componible else "no_componible",
                n_min_w2=nmin2, w1_identificado=m1["identifica"],
                repertorio_w1=m1["escribe"] + m1["permuta"],
                # E-50: el primer paso desde el que la fresca ya no yerra en W1, o sea lo
                # que cuesta por su cuenta aquello que C5 recibe heredado
                coste_w1=v1["ultimo_error"] + 1)
    x_cambio = v1["x"]
    filas = []
    for brazo in brazos:
        elige = brazo in ("F3", "C3", "C4", "M-b")
        u = _construir(brazo, madre, n_max, clase)
        v2 = vivir(u, step2, x_cambio, vida2, elige, fut2)
        extra = dict(brazo=brazo, errores=v2["errores"], ultimo_error=v2["ultimo_error"],
                     olvidos=v2["agotado"], pasos_elegidos=v2["pasos_elegidos"],
                     curva=v2["curva"], olvidados=u.c["pasos_olvidados"],
                     topes=u.c["topes"], sin_aprender=u.c["pasos_sin_aprender"])
        if isinstance(u, UnidadC5):
            extra.update(transiciones_heredadas=u.c["transiciones_heredadas"],
                         transiciones_heredadas_revisadas=u.c["transiciones_heredadas_revisadas"],
                         transiciones_heredadas_supervivientes=u.supervivientes(),
                         herencia_borrada_por_distincion=u.c["herencia_borrada_por_distincion"],
                         refutaciones_en_w2=u.c["refutaciones"] - u.refutaciones_al_heredar)
            if con_garantia:
                nmin, agotado = minima_con_tope(u.trace, n_max)
                extra.update(c5_consistente=explica(u.trans, u.trace),
                             c5_minima=(None if nmin is None else (u.n == nmin)),
                             c5_estados_sobre_minimo=(None if nmin is None else u.n - nmin),
                             c5_minima_agotada=agotado)
        m2 = medir(u, step2, v2["x"], fut2, est2, extra)
        m2.update(base)
        m2["repertorio"] = m2["escribe"] + m2["permuta"]
        m2["curva"][len(vida2)] = dict(exactitud=m2["exactitud"], identifica=m2["identifica"])
        filas.append(m2)
    return filas


def _una_w1(args):
    (idx, vida1, vida2, fut1, fut2, n_max, brazos, nombre_clase, con_garantia,
     solo_clase, intercambio) = args
    clase = CLASES[nombre_clase]
    A, B = sistema_por_indice(N1, idx)
    _, nmin1, _ = verdad(A, B)
    filas, descartadas = [], 0
    for comp in (True, False):
        if solo_clase is not None and comp != solo_clase:
            continue
        for patron in patrones(N1):
            A2, B2 = mundo_2(A, B, N1, patron, comp)
            _, nmin2, _ = verdad(A2, B2)
            if nmin2 <= nmin1:
                descartadas += 1
                continue
            filas.extend(una_familia(idx, patron, comp, vida1, vida2, fut1, fut2, n_max,
                                     brazos, clase, con_garantia, intercambio))
    return filas, descartadas


def coste_w1_de_la_fresca(filas):
    """E-50 · PRECONDICIÓN DEL BANCO. Lo que C5 hereda es la máquina de W₁; si la unidad
    fresca identifica W₁ ANTES del primer punto de medición, la herencia no tiene dónde
    mostrarse y la celda es nula por techo del diseño, lo mida como lo mida.

    Se usa `ultimo_error_w1 + 1` —el primer paso desde el que la hipótesis ya no vuelve a
    errar en W₁—, que es gratis porque `vivir` ya lo cuenta. Verificado el 28-oct contra la
    medida directa (primer paso desde el que identifica el futuro fijo y no lo pierde) sobre
    los 174 mundos: mediana, p75, p90, p95 y máximo coinciden.
    """
    v = sorted({(f["w1"], f["coste_w1"]) for f in filas if "coste_w1" in f})
    v = sorted(c for _, c in v)
    if not v:
        return None
    n = len(v)
    q = lambda fr: v[min(n - 1, int(fr * n))]
    primer_hito = min(HITOS)
    return dict(mundos=n, minimo=v[0], mediana=v[n // 2], p75=q(.75), p90=q(.90),
                p95=q(.95), maximo=v[-1], primer_hito=primer_hito,
                antes_del_primer_hito=sum(1 for x in v if x < primer_hito),
                suficiente=(v[n // 2] > primer_hito))


def campana(out, limite_w1=None, trabajadores=1, brazos=BRAZOS, clase=UnidadFase2,
            con_garantia=True, solo_clase=None, intercambio=False):
    vida1 = shortlex(range(1, L_de(N1) + 1))
    vida2 = shortlex(range(1, L_de(2 * N1) + 1))
    fut1 = shortlex((L_de(N1) + 1, L_de(N1) + 2))
    fut2 = shortlex((2 * N1, 2 * N1 + 1))
    n_max = 2 * N1 + 2
    out.write(f"vida en W1: {len(vida1)} pasos; vida en W2: {len(vida2)}; futuro W2: {len(fut2)}; "
              f"tope de estados {n_max}; brazos {', '.join(brazos)}; clase de unidad {clase.__name__}; "
              f"presupuesto {clase.presupuesto} pasos por intento"
              f"{'; CONTROL A↔B: las dos letras intercambiadas en el mundo' if intercambio else ''}\n")
    elegibles = mundos_1(vida1, fut1, n_max, out)
    no_vacio(elegibles, "mundos W1 elegibles")
    if limite_w1:
        elegibles = elegibles[:limite_w1]
    tareas = [(idx, vida1, vida2, fut1, fut2, n_max, brazos, clase.__name__, con_garantia,
               solo_clase, intercambio) for idx in elegibles]
    no_vacio(tareas, "tareas (W1 a correr)")
    t0 = time.perf_counter()
    if trabajadores > 1:
        import multiprocessing as mp
        with mp.get_context("fork").Pool(trabajadores) as pool:
            res = pool.map(_una_w1, tareas, chunksize=1)     # map conserva el orden: determinista
    else:
        res = [_una_w1(t) for t in tareas]
    filas, descartadas = [], 0
    for f, d in res:
        filas.extend(f)
        descartadas += d
    no_vacio(filas, "filas medidas")
    out.write(f"mundos W1 corridos: {len(elegibles)}; familias (W1, W2): {len(filas) // len(brazos)}; "
              f"descartadas por no abrir distinción nueva: {descartadas}\n")
    cw = coste_w1_de_la_fresca(filas)
    if cw:
        out.write(
            f"PRECONDICIÓN DEL BANCO (E-50) · lo que C5 hereda es la máquina de W1, y a la "
            f"fresca identificar W1 le cuesta: mediana {cw['mediana']}, p90 {cw['p90']}, "
            f"máximo {cw['maximo']} pasos ({cw['mundos']} mundos); {cw['antes_del_primer_hito']}"
            f"/{cw['mundos']} lo consiguen antes del primer hito ({cw['primer_hito']}).\n"
            f"  ⇒ {'la herencia TIENE dónde mostrarse' if cw['suficiente'] else 'la herencia NO TIENE dónde mostrarse: cualquier resultado de esta celda es NULO POR TECHO DEL DISEÑO'}\n")
    out.write("\n")
    sys.stderr.write(f"reloj: {time.perf_counter() - t0:.1f} s\n")
    return filas


# ---------------------------------------------------------------------------
# Resumen y puerta
# ---------------------------------------------------------------------------
def _ee(p, n):
    return (p * (1 - p) / n) ** 0.5 if n else 0.0


def z_dos(p1, n1, p2, n2):
    e = (_ee(p1, n1) ** 2 + _ee(p2, n2) ** 2) ** 0.5
    return abs(p1 - p2) / e if e else 0.0


def umbral(m):
    """Bonferroni sobre m comparaciones, como en E-22."""
    return NormalDist().inv_cdf(1 - ALFA / (2 * max(1, m)))


def pareado(F, a, b, hito, campo="brazo"):
    por_fam = {}
    for f in F:
        por_fam.setdefault((f["w1"], f["patron"]), {})[f[campo]] = f
    ia = lambda d, br: bool(d[br]["curva"][hito]["identifica"]) if br in d else None
    solo_a = sum(1 for d in por_fam.values() if a in d and b in d and ia(d, a) and not ia(d, b))
    solo_b = sum(1 for d in por_fam.values() if a in d and b in d and ia(d, b) and not ia(d, a))
    return solo_a, solo_b, len(por_fam)


def resumen(filas, out, brazos=BRAZOS):
    R = {}
    hitos = sorted({int(k) for f in filas for k in f["curva"]})
    for clase in ("componible", "no_componible"):
        F = [f for f in filas if f["clase"] == clase]
        if not F:
            continue
        out.write(f"=== clase {clase}: {len(F) // len(brazos)} familias\n")
        out.write(f"{'brazo':<7}{'alcance':>9}{'exactitud':>11}{'repert.':>9}{'instr.':>8}{'estados':>9}"
                  f"{'olvidos':>8}{'topes':>7}{'trabajo medio':>15}  (al FINAL de W2)\n")
        R[clase] = {}
        for b in brazos:
            Fb = [f for f in F if f["brazo"] == b]
            k = len(Fb)
            if not k:
                continue
            r = dict(familias=k,
                     alcance=sum(f["identifica"] for f in Fb) / k,
                     exactitud=sum(f["exactitud"] for f in Fb) / k,
                     repertorio=sum(f["repertorio"] for f in Fb) / k,
                     instruibilidad=sum(f["instruibilidad"] for f in Fb) / k,
                     estados=sum(f["estados"] for f in Fb) / k,
                     olvidos=sum(f["olvidos"] for f in Fb),
                     topes=sum(f["topes"] for f in Fb),
                     trabajo=sum(f["pasos_avanzados"] for f in Fb) / k,
                     sin_aprender=sum(f["sin_aprender"] for f in Fb),
                     curva_alcance={h: sum(f["curva"][h]["identifica"] for f in Fb) / k for h in hitos})
            r["alcance_medio_curva"] = sum(r["curva_alcance"].values()) / len(hitos)
            R[clase][b] = r
            out.write(f"{b:<7}{r['alcance']:>9.3f}{r['exactitud']:>11.4f}{r['repertorio']:>9.2f}"
                      f"{r['instruibilidad']:>8.2f}{r['estados']:>9.2f}{r['olvidos']:>8}{r['topes']:>7}"
                      f"{r['trabajo']:>15.0f}\n")
        out.write("curva de alcance (fracción que identifica W2) por pasos vividos en W2:\n")
        out.write(f"{'brazo':<7}" + "".join(f"{h:>8}" for h in hitos) + f"{'media':>8}\n")
        for b in brazos:
            if b not in R[clase]:
                continue
            r = R[clase][b]
            out.write(f"{b:<7}" + "".join(f"{r['curva_alcance'][h]:>8.3f}" for h in hitos) +
                      f"{r['alcance_medio_curva']:>8.3f}\n")
        # la celda que contesta la pregunta: C5 contra la vara, en el hito 64
        if "C5" in R[clase] and "F1" in R[clase]:
            c5, f1 = R[clase]["C5"], R[clase]["F1"]
            for h in (64, 128, 256):
                if h not in hitos:
                    continue
                p1, p2 = c5["curva_alcance"][h], f1["curva_alcance"][h]
                z = z_dos(p1, c5["familias"], p2, f1["familias"])
                sa, sb, nf = pareado(F, "C5", "F1", h)
                R[clase][f"C5_vs_F1_{h}"] = dict(c5=p1, f1=p2, z=z, solo_c5=sa, solo_f1=sb, familias=nf)
                out.write(f"  hito {h}: C5 {p1:.3f} vs F1 {p2:.3f} · z {z:.2f} · pareado: "
                          f"sólo C5 en {sa} familias, sólo F1 en {sb} (de {nf})\n")
        # la garantía cedida
        C5 = [f for f in F if f["brazo"] == "C5" and "c5_consistente" in f]
        if C5:
            det = [f for f in C5 if f["c5_minima"] is not None]
            g = dict(celdas=len(C5),
                     c5_consistente=sum(bool(f["c5_consistente"]) for f in C5) / len(C5),
                     determinadas=len(det),
                     c5_minima=(sum(bool(f["c5_minima"]) for f in det) / len(det)) if det else None,
                     c5_estados_sobre_minimo=(sum(f["c5_estados_sobre_minimo"] for f in det) / len(det)) if det else None,
                     heredadas=sum(f["transiciones_heredadas"] for f in C5) / len(C5),
                     revisadas=sum(f["transiciones_heredadas_revisadas"] for f in C5),
                     supervivientes=sum(f["transiciones_heredadas_supervivientes"] for f in C5) / len(C5),
                     herencia_borrada=sum(f["herencia_borrada_por_distincion"] for f in C5))
            R[clase]["garantia_c5"] = g
            mini = "—" if g["c5_minima"] is None else f"{g['c5_minima']:.3f}"
            sobre = "—" if g["c5_estados_sobre_minimo"] is None else f"{g['c5_estados_sobre_minimo']:.2f}"
            out.write(f"  garantía C5: consistente {g['c5_consistente']:.3f}; mínima {mini} sobre "
                      f"{g['determinadas']}/{g['celdas']} celdas determinadas; estados de más {sobre}; "
                      f"heredadas {g['heredadas']:.2f}, revisadas {g['revisadas']}, supervivientes "
                      f"{g['supervivientes']:.2f}; herencia borrada por distinción nueva en "
                      f"{g['herencia_borrada']} celdas\n")
        out.write("\n")
    return R


def puerta(filas, R, out, brazos=BRAZOS):
    g = {}
    c = R.get("componible", {})
    nc = R.get("no_componible", {})
    # (a) la garantía que debe cumplirse siempre
    for clase, Rc in (("componible", c), ("no_componible", nc)):
        gc = Rc.get("garantia_c5")
        if gc:
            g[f"(a) C5 consistente con su traza en {clase} (debe ser 1,000)"] = gc["c5_consistente"] == 1.0
            g[f"(actividad) la reparación local actuó en {clase}"] = gc["revisadas"] > 0
    # (b) los dos mutantes que deben dar exactamente F1
    for mut in ("M-e", "M-f"):
        if mut in brazos:
            dif = difieren(filas, mut, "F1")
            g[f"(b) {mut} reproduce F1 en TODAS las medidas ({dif['familias']} familias)"] = \
                not dif["medidas"]
            ord_ = lambda d: (", ".join(f"{k}={v}" for k, v in sorted(d.items()))
                              if d else "ninguno")   # E-48: ordenado, o el texto no es reproducible
            out.write(f"  {mut} vs F1: medidas que difieren {ord_(dif['medidas'])}; "
                      f"registros que difieren {ord_(dif['registros'])}\n")
    # (c) acumulación
    if "C5" in c and "F1" in c:
        d = c.get("C5_vs_F1_64")
        u = umbral(6)
        g["(c) acumulación: C5 > F1 en el hito 64 de la clase componible, z sobre el umbral"] = \
            bool(d and d["c5"] > d["f1"] and d["z"] > u)
        out.write(f"  umbral de z ajustado (alfa {ALFA} sobre 6 comparaciones): {u:.2f}\n")
    if "C5" in nc and "F1" in nc:
        g["(c) control: C5 <= F1 en el hito 64 de la clase no componible"] = \
            nc["C5"]["curva_alcance"][64] <= nc["F1"]["curva_alcance"][64]
    # (e) repertorio
    if "C5" in c and "F1" in c:
        g["(e) repertorio: C5 >= F1 al final de W2 (componible)"] = \
            c["C5"]["repertorio"] >= c["F1"]["repertorio"]
    # (d) no sobreatribución: pide los brazos C1 y C2, que esta campaña no corre
    evaluados = {"a", "b", "c", "e", "f"}
    if "C1" in c and "F1" in c:
        g["(d) no sobreatribución: C1 <= F1 en los tres hitos (componible)"] = all(
            c["C1"]["curva_alcance"].get(h, 0) <= c["F1"]["curva_alcance"].get(h, 0)
            for h in (64, 128, 256))
        evaluados.add("d")
    # (g) NO SATURACIÓN / TECHO: si los brazos no se separan más que el ruido en el punto
    # donde la ficha dijo que se decidía, el veredicto es NULO, nunca negativo (E-50)
    u = umbral(6)
    for clase, Rc in (("componible", c), ("no_componible", nc)):
        vals = [(b, Rc[b]["curva_alcance"][64], Rc[b]["familias"])
                for b in brazos if b in Rc and 64 in Rc[b]["curva_alcance"]]
        if len(vals) < 2:
            continue
        alto = max(vals, key=lambda t: t[1])
        bajo = min(vals, key=lambda t: t[1])
        z = z_dos(alto[1], alto[2], bajo[1], bajo[2])
        hay = z > u
        g[f"(g) no saturación en {clase}: los brazos se separan en el hito 64 "
          f"(rango {bajo[1]:.3f}–{alto[1]:.3f}, z {z:.2f} contra umbral {u:.2f})"] = hay
        if not hay:
            g[f"(g) ⇒ VEREDICTO {clase}: NULO POR TECHO DEL DISEÑO, no negativo"] = True
        evaluados.add("g")
    out.write("--- puerta (ficha §11)\n")
    for k, v in sorted(g.items()):
        out.write(f"  [{'PASS' if v else 'FAIL'}] {k}\n")
    faltan = [k for k in CRITERIOS_FICHA if k not in evaluados]
    if faltan:
        out.write("  criterios que la ficha §11 enumera y esta corrida NO evalúa "
                  "(el veredicto es parcial mientras falten):\n")
        for k in faltan:
            out.write(f"    ({k}) {CRITERIOS_FICHA[k]}\n")
    g["criterios_no_evaluados"] = faltan
    return g


# Qué cuenta como MEDIDA y qué como REGISTRO, dicho antes de comparar. El criterio de
# los mutantes M-e y M-f («dar exactamente F1») recae sobre las medidas; los registros
# se IMPRIMEN siempre con su diferencia, no se esconden. Separarlos hizo falta en la
# primera corrida de prueba (E-45): M-f reproducía F1 en las diecisiete medidas y
# difería en `refutaciones`, que es el contador acumulado de la vida en W1 y llega
# heredado por construcción —en C1 de 08 igual—. Un criterio «idéntico en todo» que
# incluye registros acumulados no distingue un defecto de la contabilidad.
REGISTROS = {"pasos_avanzados", "refutaciones", "pasos_repasados", "repaso_max", "sin_aprender",
             "distinciones_abiertas", "transiciones_heredadas", "refutaciones_en_w2",
             "transiciones_heredadas_revisadas", "transiciones_heredadas_supervivientes",
             "herencia_borrada_por_distincion", "c5_consistente", "c5_minima",
             "c5_estados_sobre_minimo", "c5_minima_agotada"}


def difieren(filas, a, b):
    """Qué difiere entre dos brazos, familia a familia, en dos cubos separados:
    `medidas` (lo que la puerta exige idéntico) y `registros` (se informa, no decide)."""
    por_fam = {}
    for f in filas:
        por_fam.setdefault((f["w1"], f["patron"], f["clase"]), {})[f["brazo"]] = f
    medidas, registros, pares = Counter(), Counter(), 0
    for d in por_fam.values():
        if a not in d or b not in d:
            continue
        pares += 1
        for k in set(d[a]) | set(d[b]):
            if k == "brazo":
                continue
            if d[a].get(k) != d[b].get(k):
                (registros if k in REGISTROS else medidas)[k] += 1
    no_vacio([None] * pares, f"familias donde {a} y {b} se pueden comparar")
    return dict(medidas=dict(medidas), registros=dict(registros), familias=pares)


def mundo_2_conmutado(A, B, n, patron, componible):
    """M-d · el patrón de E-38: el bit se CONMUTA en la situación (A, x) en vez de
    ponerse a 1. Como la conmutación no depende de b, el bit nuevo no puede influir en
    ninguna salida: es inobservable, y el filtro de familias debe descartar el 100 % de
    la clase componible. Es el mundo que hizo falso el primer piloto."""
    x_tog, _ = patron
    tablas = {"A": A, "B": B}
    A2, B2 = [0] * (2 * n), [0] * (2 * n)
    for b in (0, 1):
        for x in range(n):
            for letra, T2 in (("A", A2), ("B", B2)):
                if componible or b == 0:
                    y = tablas[letra][x]
                else:
                    y = tablas["B" if letra == "A" else "A"][x]
                b2 = (1 - b) if (letra == "A" and x == x_tog) else b
                T2[x + n * b] = y + n * b2
    return tuple(A2), tuple(B2)


def mutante_d(elegibles, out):
    """M-d: con el bit conmutado, ¿cuántas familias componibles pasan el filtro de
    «abre una distinción nueva»? Debe ser 0, y `no_vacio` debe abortar sobre ellas."""
    sobreviven = {True: 0, False: 0}
    miradas = 0
    for idx in elegibles:
        A, B = sistema_por_indice(N1, idx)
        _, nmin1, _ = verdad(A, B)
        for comp in (True, False):
            for patron in patrones(N1):
                miradas += 1
                A2, B2 = mundo_2_conmutado(A, B, N1, patron, comp)
                _, nmin2, _ = verdad(A2, B2)
                if nmin2 > nmin1:
                    sobreviven[comp] += 1
    no_vacio(elegibles, "mundos W1 de M-d")
    out.write(f"M-d · bit conmutado: {miradas} (W1, patrón, clase) miradas; pasan el filtro "
              f"{sobreviven[True]} componibles y {sobreviven[False]} no componibles\n")
    abortó = False
    try:
        no_vacio([None] * sobreviven[True], "familias componibles con el bit conmutado")
    except GuardaViolada as e:
        abortó = True
        out.write(f"  `no_vacio` abortó, como debe: {e}\n")
    ok = (sobreviven[True] == 0 and abortó)
    out.write(f"  [{'PASS' if ok else 'FAIL'}] M-d: el filtro descarta el 100 % de la clase "
              f"componible y la guarda aborta\n")
    return dict(miradas=miradas, componibles_que_pasan=sobreviven[True],
                no_componibles_que_pasan=sobreviven[False], guarda_abortó=abortó, pasa=ok)


def mutantes(limite_w1, trabajadores, out, here):
    """Los seis mutantes de la ficha §10. Cada uno con su presupuesto declarado y su
    tope; ninguno enmienda un criterio después de verlo fallar."""
    res = {}
    vida1 = shortlex(range(1, L_de(N1) + 1))
    fut1 = shortlex((L_de(N1) + 1, L_de(N1) + 2))
    n_max = 2 * N1 + 2
    elegibles = mundos_1(vida1, fut1, n_max, out)
    no_vacio(elegibles, "mundos W1 elegibles")
    muestra = elegibles[:limite_w1] if limite_w1 else elegibles
    out.write(f"muestra de mutantes: {no_vacio(muestra, 'W1 de la muestra de mutantes')} "
              f"mundos W1 de {len(elegibles)}\n\n")

    # --- M-d: no necesita vivir, sólo generar mundos. Primero porque es el más barato.
    res["M-d"] = mutante_d(muestra, out)
    out.write("\n")

    # --- M-e y M-f: van dentro de la corrida normal, con F1 y C5
    out.write("M-e (fresca con la vida de la heredera) y M-f (C5 que ignora lo heredado): "
              "deben coincidir EXACTAMENTE con F1\n")
    t, filas, R, g = main(limite_w1, trabajadores,
                          os.path.join(here, "artifacts", "mutantes_09_ef.jsonl"))
    out.write(t)
    for mut in ("M-e", "M-f"):
        res[mut] = dict(difieren=difieren(filas, mut, "F1"))
        res[mut]["pasa"] = not res[mut]["difieren"]["medidas"]
    res["C5_garantia"] = {k: v.get("garantia_c5") for k, v in R.items()}
    res["puerta_ef"] = g
    for mut in ("M-e", "M-f"):
        d = res[mut]["difieren"]
        ord_ = lambda x: (", ".join(f"{k}={v}" for k, v in sorted(x.items())) if x else "ninguno")
        out.write(f"  [{'PASS' if res[mut]['pasa'] else 'FAIL'}] {mut} == F1 en las medidas "
                  f"({d['familias']} familias); medidas distintas: {ord_(d['medidas'])}; "
                  f"registros distintos: {ord_(d['registros'])}\n")
    out.write("\n")

    # --- M-a: olvido total, contra la heredera con núcleo 64 (C1) y contra F1
    out.write("M-a (olvido total, núcleo 0) contra C1 (núcleo 64) y F1\n")
    ta, fa, Ra, _ = main(limite_w1, trabajadores,
                         os.path.join(here, "artifacts", "mutantes_09_a.jsonl"),
                         brazos=("F1", "C1"), clase=UnidadMa, con_garantia=False)
    tb, fb, Rb, _ = main(limite_w1, trabajadores,
                         os.path.join(here, "artifacts", "mutantes_09_a_ref.jsonl"),
                         brazos=("F1", "C1"), clase=UnidadFase2, con_garantia=False)
    out.write("  núcleo 0:\n" + ta + "  núcleo 64 (referencia):\n" + tb)
    cur = lambda R, cl, b: R.get(cl, {}).get(b, {}).get("curva_alcance", {})
    res["M-a"] = dict(nucleo_0={cl: cur(Ra, cl, "C1") for cl in Ra},
                      nucleo_64={cl: cur(Rb, cl, "C1") for cl in Rb},
                      fresca={cl: cur(Rb, cl, "F1") for cl in Rb},
                      identicos=all(cur(Ra, cl, "C1") == cur(Rb, cl, "C1") for cl in Ra))
    out.write(f"  [{'FAIL' if res['M-a']['identicos'] else 'PASS'}] M-a: el olvido total NO da la "
              f"misma curva que el núcleo de 64 (si la da, esos 64 pasos no aportan nada)\n\n")

    # --- M-b: elegir al revés
    out.write("M-b (elegir la transición no vista MÁS LEJANA) contra elegir la más cercana\n")
    tc, fc, Rc, _ = main(limite_w1, trabajadores,
                         os.path.join(here, "artifacts", "mutantes_09_b.jsonl"),
                         brazos=("F1", "F3"), clase=UnidadMb, con_garantia=False)
    td, fd, Rd, _ = main(limite_w1, trabajadores,
                         os.path.join(here, "artifacts", "mutantes_09_b_ref.jsonl"),
                         brazos=("F1", "F3"), clase=UnidadFase2, con_garantia=False)
    out.write("  más lejana:\n" + tc + "  más cercana (referencia):\n" + td)
    med = lambda R, cl, b: R.get(cl, {}).get(b, {}).get("alcance_medio_curva")
    peor = all((med(Rc, cl, "F3") or 0) <= (med(Rd, cl, "F3") or 0) + 1e-12 for cl in Rc)
    res["M-b"] = dict(lejana={cl: med(Rc, cl, "F3") for cl in Rc},
                      cercana={cl: med(Rd, cl, "F3") for cl in Rd}, pasa=peor)
    out.write(f"  [{'PASS' if peor else 'FAIL'}] M-b: la más lejana no supera a la más cercana\n\n")

    # --- M-c: sin olvido. El más caro: va con presupuesto declarado y sobre la muestra.
    out.write(f"M-c (sin olvido; presupuesto {PRESUPUESTO_MC} por intento, tope {n_max} estados): "
              f"debe reproducir el ahogo —curva plana y 100 % en el tope—\n")
    te, fe, Re, _ = main(limite_w1, trabajadores,
                         os.path.join(here, "artifacts", "mutantes_09_c.jsonl"),
                         brazos=("F1", "C1"), clase=UnidadMc, con_garantia=False)
    out.write(te)
    ahogo = {}
    for cl in Re:
        c1 = Re[cl].get("C1", {})
        f1 = Re[cl].get("F1", {})
        curva = c1.get("curva_alcance", {})
        plana = (max(curva.values()) - min(curva.values())) <= 0.02 if curva else None
        ahogo[cl] = dict(curva_C1=curva, curva_F1=f1.get("curva_alcance"),
                         topes=c1.get("topes"), celdas=c1.get("familias"),
                         sin_aprender=c1.get("sin_aprender"),
                         alcance_final=c1.get("alcance"), plana=plana,
                         fresca_identifica=f1.get("alcance"))
    res["M-c"] = ahogo
    comp = ahogo.get("componible", {})
    ok = bool(comp) and (comp.get("alcance_final") or 0) < 0.1 and (comp.get("fresca_identifica") or 0) > 0.5
    res["M-c"]["pasa"] = ok
    out.write(f"  [{'PASS' if ok else 'FAIL'}] M-c: la heredera sin olvido no identifica "
              f"(<0,10) mientras la fresca sí (>0,50) — el ahogo reproducido con ojos frescos\n")
    return res


def guardar_filas(filas, ruta):
    with open(ruta, "w", encoding="utf-8") as f:
        for fila in filas:
            f.write(json.dumps(fila, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())


def main(limite_w1=None, trabajadores=1, ruta_filas=None, brazos=BRAZOS,
         clase=UnidadFase2, con_garantia=True, solo_clase=None, intercambio=False):
    buf = io.StringIO()
    filas = campana(buf, limite_w1, trabajadores, brazos, clase, con_garantia, solo_clase,
                    intercambio)
    if ruta_filas:
        guardar_filas(filas, ruta_filas)     # antes del resumen: un resumen que falla no borra la corrida
    R = resumen(filas, buf, brazos)
    g = puerta(filas, R, buf, brazos)
    return buf.getvalue(), filas, R, g


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    lim = int(args[0]) if args else None
    trab = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--trabajadores=")), 1)
    inter = "--intercambio" in sys.argv
    suf = (f"_pilot{lim}" if lim else "") + ("_ab" if inter else "")
    os.makedirs(os.path.join(here, "artifacts"), exist_ok=True)
    ruta = os.path.join(here, "artifacts", f"unidad_minima_09_fase2{suf}.jsonl")
    if "--mutantes" in sys.argv:
        buf = io.StringIO()
        res = mutantes(lim, trab, buf, here)
        sys.stdout.write(buf.getvalue())
        azar = sin_azar_usado(["unidad_minima_09_fase2", "unidad_minima_08_fase2",
                               "unidad_minima_02_incremental", "unidad_minima_01"])
        src, src8 = SHA_09, SHA_08
        sys.stdout.write(f"azar usado: {azar}; arranque {ARRANQUE}; sha256 de 09 al arrancar: "
                         f"{src[:16]}…; sha256 de 08: {src8[:16]}…\n")
        informe()
        rm = os.path.join(here, "artifacts", f"mutantes_09_fase2{suf}.json")
        salida_a_fichero(rm, "mutantes de 09")
        with open(rm, "w", encoding="utf-8") as f:
            json.dump(dict(mutantes=res, texto=buf.getvalue(), sha256_codigo=src, sha256_08=src8),
                      f, ensure_ascii=False, indent=1)
            f.flush()
            os.fsync(f.fileno())
        sys.exit(0)
    salida_a_fichero(ruta, "filas de 09")
    t1, filas, R, g = main(lim, trab, ruta, BRAZOS, UnidadFase2, True, None, inter)
    sys.stdout.write(t1)
    if "--doble" in sys.argv:
        t2, _, _, _ = main(lim, trab, None, BRAZOS, UnidadFase2, True, None, inter)
        h1, h2 = (hashlib.sha256(t.encode()).hexdigest() for t in (t1, t2))
        sys.stdout.write(f"determinismo: {'IDÉNTICAS' if h1 == h2 else 'DIFIEREN'}\n")
    azar = sin_azar_usado(["unidad_minima_09_fase2", "unidad_minima_08_fase2",
                           "unidad_minima_02_incremental", "unidad_minima_01"])
    src, src8 = SHA_09, SHA_08          # leídos al importar, no ahora (E-49)
    sys.stdout.write(f"azar usado: {azar}; arranque {ARRANQUE}; sha256 de 09 al arrancar: "
                     f"{src[:16]}…; sha256 de 08 (importado, no tocado): {src8[:16]}…\n")
    informe()
    with open(os.path.join(here, "artifacts", f"unidad_minima_09_fase2{suf}.json"), "w", encoding="utf-8") as f:
        json.dump(dict(resumen=R, puerta=g, sha256_codigo=src, sha256_08=src8,
                       arranque=ARRANQUE, python=sys.version, texto=t1), f,
                  ensure_ascii=False, indent=1)
