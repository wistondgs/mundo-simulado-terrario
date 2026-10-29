#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UNIDAD-MINIMA-13 · Fase 3 · dos que viven, uno que observa, y el hijo del observador.

**EXPLORATORIO.** Todo artefacto de este módulo lleva `exploratorio: true`. No certifica
nada, no cierra nada, no entra a ninguna puerta de fase. Se construye para **verlo
funcionar** (T5) y se corre esta noche por orden de Wis (T5-bis); la ficha y la corrida
confirmatoria vienen después, con mutantes.

**Importa 08, 09, 10 y 12 y no los toca.**

LOS TRES ELEMENTOS (`ORIENTACIONES_FASE_3_TRES_ELEMENTOS.md`):
- **Actor A** y **Actor B**: la unidad de 08 con una **variable esencial V**, en vértices
  distintos del mundo y con itinerarios desplazados — la asimetría es obligatoria, porque dos
  unidades deterministas idénticas en la misma corriente no cruzan ni un bit (E-47, medido).
- **Observador O**: lee las dos corrientes `(acción, reacción, ΔV)` con marca de quién,
  **no actúa**, y escribe el **genoma del linaje**: primero lo que mató, después lo que
  restringió, al final lo que benefició.
- **El hijo de O**: nace con el genoma y **sin traza**, y **sí actúa**.

LAS TRES DECISIONES DE WIS, **SUMINISTRADAS POR FABLE** y revisables mañana (T5-bis):
el observador **no actúa, actúa su hijo** · la V de los otros **es pública** · **cinco
generaciones**. Van en todo artefacto como `decisiones_suministradas`.

DOS COSAS QUE SE DECLARAN CONTRA HALLAZGOS YA EXISTENTES (cartografía de Fable):
1. **V no es la recompensa** y no es señal de aprendizaje en ningún sitio. En Terrario
   `energy_delta` **es** la recompensa en las cuatro arquitecturas plásticas
   (`VARIABLES_ESENCIALES_Y_REORGANIZACION_01.md` §1-§3, 16-sep, `SOURCE-VERIFIED`). Aquí V
   entra **sólo** como coordenada de lo observado; una aserción lo garantiza (`_sin_premio`).
2. **El observador es una extensión declarada del `Teacher` de Genesis**
   (`runtime/organism/teacher.py`, clase `Teacher`, `reflect`: ordena las heridas por
   severidad y destila `avoid` antes que `prefer`; `SOURCE-VERIFIED` por lectura de Fable).
   Lo que esto añade y él no tiene: el que reflexiona es **otra unidad** y no un modelo de
   lenguaje, es **determinista**, lee **dos vidas** y compara, y escribe **al genoma del
   linaje** en vez de a la experiencia del mismo organismo.

Sin azar: todo empate por shortlex. Sin `break` en ningún bucle de vida (E-39): morir es un
estado, no una salida del bucle. Reanudable con `fsync` por fila.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import time
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unidad_minima_10_maestro as m10                                    # noqa: E402
from unidad_minima_01 import LETTERS, predict, run_world, shortlex, states_of  # noqa: E402
from unidad_minima_05_banco import (                                      # noqa: E402
    L_de, alcanzables, canonica, mealy_verdadera, minimizar, paso_de, sistema_por_indice,
)
from unidad_minima_08_fase2 import (                                      # noqa: E402
    N1, UnidadFase2, medir, mundo_2, mundos_1, patrones, verdad, vivir,
)
from guardas import informe, no_vacio, salida_a_fichero, sin_azar_usado    # noqa: E402

SHA_13 = hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()
ARRANQUE = time.strftime("%Y-%m-%dT%H:%M:%S")

EXPLORATORIO = True
DECISIONES = dict(
    cuando_actua_el_observador="nunca; actúa su hijo",
    ve_la_V_de_los_otros=True,
    generaciones=5,
    origen="SUMINISTRADAS POR FABLE (T5-bis); revisables por Wis antes de la ficha")

V_INICIAL, V_MIN, V_MAX = 0.6, 0.2, 0.9
V_BAJA, V_SUBE = 0.12, 0.10        # cuánto baja δ⁻ y cuánto repone δ⁺
V_DESGASTE = 0.002                 # coste de vivir por paso
# Los tres valores son DISPOSICIÓN SUMINISTRADA y se subieron tras el primer piloto: con
# 0,05 / 0,10 / 0,001 **nadie moría nunca** (vivas 1,000 en todas las generaciones), así que
# la libreta de lo que mató quedaba vacía y el genoma no podía probarse en lo único que Wis
# puso primero. Con algo en juego de verdad, morir es posible; que ocurra se mide, no se
# supone.
BANDAS = (0.2, 0.5)               # V se observa en tres bandas: la coordenada que cruza
TOPE_GENOMA = dict(prohibiciones=8, relaciones=8)
SALTOS = ("orden_del_itinerario", "elegir", "ventana")   # lista FIJA de ultraestabilidad
HITOS = (16, 64, 256, 1024)
CELDAS = ("TRES", "DOS", "hijo-sin-genoma", "O-todo", "simetrico")


def banda(v):
    """V entra en lo observado como una coordenada de tres bandas. Discretizarla es una
    DISPOSICIÓN SUMINISTRADA: la unidad lee símbolos, no reales."""
    return 0 if v < BANDAS[0] else (1 if v < BANDAS[1] else 2)


# ---------------------------------------------------------------------------
# El mundo con variable esencial
# ---------------------------------------------------------------------------
def mundo_con_V(A, B, n, semilla_canonica):
    """δ⁻ y δ⁺ **deterministas por índice**, sin azar: las situaciones que bajan V se
    eligen por el orden canónico de (estado, letra) desplazado por el índice del mundo, y
    las palabras que la reponen son las dos primeras palabras de longitud 2 en shortlex
    desplazadas igual. Es arbitrario y **declarado**, no aleatorio."""
    est = alcanzables(A, B)
    sits = [(x, a) for x in est for a in LETTERS]
    k = len(sits)
    d_menos = {sits[(semilla_canonica + i * 7) % k] for i in range(max(1, k // 4))}
    palabras = [w for w in (("A", "A"), ("A", "B"), ("B", "A"), ("B", "B"))]
    d_mas = {palabras[(semilla_canonica + i) % 4] for i in range(2)}
    return d_menos, d_mas


def _sin_premio(fuente):
    """E-42 y el hallazgo del 16-sep: V **no** puede ser señal de aprendizaje. Esta aserción
    es la guarda mecánica: el código del actor no puede contener ninguna de estas formas."""
    prohibidas = ("recompensa", "reward", "premio", "v_delta", "delta_v")
    malas = [p for p in prohibidas if p in fuente]
    if malas:
        raise AssertionError(
            f"el actor usa {malas} como señal: V no es la recompensa "
            f"(VARIABLES_ESENCIALES_Y_REORGANIZACION_01.md §1-§3, 16-sep)")
    return True


# ---------------------------------------------------------------------------
# El actor: la unidad de 08 con V y ultraestabilidad
# ---------------------------------------------------------------------------
class Actor:
    """La unidad de 08 envuelta, con V y la lista fija de saltos de disposición.

    V **no entra** en el aprendizaje: lo único que la unidad recibe es el símbolo observado
    `(cambio, banda(V))`. V decide si **sigue viva** y si **salta una disposición**, nunca
    qué transición aprender.
    """

    def __init__(self, n_max, genoma=None, ventana=512, nombre="A"):
        self.u = m10.UnidadFase2(n_max=n_max)
        self.u.ventana = ventana
        self.nombre = nombre
        self.V = V_INICIAL
        self.viva = True
        self.saltos = []
        self.elige = False
        self.orden_letras = tuple(LETTERS)
        self.c = Counter()
        self.genoma = genoma or genoma_vacio()
        self.muertes_evitadas = 0
        self.historia = []            # (acción, reacción, ΔV) — lo que el observador lee

    def prohibida(self, palabra):
        """¿El genoma prohíbe esta palabra? La clave es la **palabra**, nunca la letra
        sola: prohibir una letra es «nunca tomes A» y eso destruye el itinerario (E-56)."""
        return list(palabra) in self.genoma["prohibiciones"]

    def paso(self, step, x, a):
        """Un paso de vida. Devuelve el nuevo estado del mundo. Morir es un ESTADO."""
        if not self.viva:
            self.c["pasos_muerta"] += 1
            return x
        y, o = step(x, a)
        dv = -V_DESGASTE
        if (x, a) in self.d_menos:
            dv -= V_BAJA
        self.ultimas = (getattr(self, "ultimas", ()) + (a,))[-2:]
        if self.ultimas in self.d_mas:
            dv += V_SUBE
        self.V = max(0.0, min(1.0, self.V + dv))
        # E-55 · V se OBSERVA pero **no entra en el símbolo que la unidad debe explicar**.
        # Medido antes de concluir nada: con `simbolo = (o, banda(V))` el alcance fue 0,000
        # en todas las generaciones de todas las celdas, y tiene que serlo: la banda de V
        # depende de la HISTORIA del actor, no del estado del mundo, así que el mundo deja de
        # ser una máquina de Mealy desde el punto de vista de la unidad y **no hay nada que
        # identificar**. La orientación pide que V «entre en lo observado como coordenada»; lo
        # que no puede es entrar en la hipótesis del mundo. Así que: la unidad aprende sobre
        # `o` como siempre, y V queda disponible para el actor (saltos, muerte) y para el
        # observador (ΔV) como coordenada aparte.
        self.banda_V = banda(self.V)
        self.u.leer(a, o)
        self.historia.append((a, o, round(dv, 4), self.banda_V))
        if self.V <= 0.0:
            self.viva = False
            self.c["murio_en"] = len(self.historia)
        elif self.V < V_MIN and len(self.saltos) < len(SALTOS):
            self._saltar()
        return y

    def _saltar(self):
        """ULTRAESTABILIDAD: V fuera de límites salta el siguiente parámetro de la lista
        fija. Es lo único nuevo de la Fase 3 según el inventario de mundos de Terrario
        («reorganización de parámetros · el segundo lazo · primitiva que FALTA»)."""
        cual = SALTOS[len(self.saltos)]
        self.saltos.append(cual)
        self.c[f"salto_{cual}"] += 1
        if cual == "orden_del_itinerario":
            self.orden_letras = tuple(reversed(self.orden_letras))
        elif cual == "elegir":
            self.elige = not self.elige
        elif cual == "ventana":
            self.u.ventana = max(64, self.u.ventana // 4)

    def predice(self, a):
        return self.u.predecir(a)


def genoma_vacio():
    return dict(prohibiciones=[], restricciones=[], relaciones=[], disposiciones={},
                orden="lo que mató → lo que restringió → lo que benefició")


# ---------------------------------------------------------------------------
# El genoma, y la prueba de renombramiento de B₀
# ---------------------------------------------------------------------------
def escribir_genoma(historias, maquinas, muertes, saltos, todo=False):
    """El observador compone. **El orden importa y es la corrección de Wis:** primero lo que
    mató, después lo que restringió, y sólo al final lo que benefició, porque **lo que mata no
    se puede aprender viviendo** —el que lo aprende muere— y sólo el linaje puede saberlo.

    `todo=True` es la celda de control **O-todo**: el mismo contenido sin el orden ni el
    reparto del tope, para ver si el orden cambia algo.

    **Nombra letras y relaciones del cociente, nunca estados** (contrato B₀): cada relación
    es `(palabra, reacción)`, no `(estado, letra) → estado`.
    """
    g = genoma_vacio()
    # 1 · lo que MATÓ: las últimas palabras antes de cada muerte, por daño
    muertes = sorted(muertes, key=lambda m: (-m["dano"], m["palabra"]))
    for m in muertes:
        p = list(m["palabra"])
        if len(p) >= 2 and p not in g["prohibiciones"]:   # E-56: nunca una letra sola
            g["prohibiciones"].append(p)
    # 2 · lo que RESTRINGIÓ: lo que hizo saltar un parámetro
    for s in sorted(set(saltos)):
        g["restricciones"].append(s)
    # 3 · lo que BENEFICIÓ: relaciones certificadas en LAS DOS máquinas, por palabra
    comunes = None
    for M in maquinas:
        rel = {(w, r) for w, r in relaciones_por_palabra(M)}
        comunes = rel if comunes is None else (comunes & rel)
    for w, r in sorted(comunes or set()):
        g["relaciones"].append([list(w), r])
    if not todo:
        g["prohibiciones"] = g["prohibiciones"][:TOPE_GENOMA["prohibiciones"]]
        g["relaciones"] = g["relaciones"][:TOPE_GENOMA["relaciones"]]
    g["disposiciones"] = dict(ventana=512, v_min=V_MIN, v_max=V_MAX)
    return g


def relaciones_por_palabra(M, largo=2):
    """Las relaciones del cociente dichas **por palabra**: para cada palabra corta, la
    reacción que la máquina predice desde cada estado, **sólo si es la misma desde todos**
    —así la relación no nombra estados y sobrevive a un renombramiento."""
    qs = states_of(M)
    if not qs:
        return []
    out = []
    for k in range(1, largo + 1):
        for w in _palabras(k):
            rs = set()
            for q in qs:
                p = q
                ok = True
                for a in w:
                    t = M.get((p, a))
                    if t is None:
                        ok = False
                        break
                    p, r = t[0], t[1]
                if ok:
                    rs.add(r)
                else:
                    rs.add(None)
            if len(rs) == 1 and None not in rs:
                out.append((w, rs.pop()))
    return out


def _palabras(k):
    if k == 0:
        return [()]
    return [w + (a,) for w in _palabras(k - 1) for a in LETTERS]


def prueba_de_renombramiento(A, B, n, genoma):
    """Contrato B₀: el genoma tiene que dar la MISMA salida sobre una copia del mundo con
    los estados permutados. Su mutante —un genoma que nombre índices de estado— debe fallarla.
    """
    perm = [(i + 1) % n for i in range(n)]
    A2 = tuple(perm[A[i]] for i in range(n))
    B2 = tuple(perm[B[i]] for i in range(n))
    reord = [0] * n
    for i in range(n):
        reord[perm[i]] = i
    A3 = tuple(A2[reord[i]] for i in range(n))
    B3 = tuple(B2[reord[i]] for i in range(n))
    est = alcanzables(A3, B3)
    M = mealy_verdadera(A3, B3, est)
    rel_perm = {(tuple(w), r) for w, r in relaciones_por_palabra(M)}
    rel_gen = {(tuple(w), r) for w, r in genoma["relaciones"]}
    return rel_gen <= rel_perm or not rel_gen


def mutante_genoma_con_estados(M):
    """El mutante de la prueba: un genoma que nombra ESTADOS. Debe fallar el renombramiento."""
    g = genoma_vacio()
    g["relaciones"] = [[[q, a], t[1]] for (q, a), t in sorted(M.items())][:TOPE_GENOMA["relaciones"]]
    g["nombra_estados"] = True
    return g


# ---------------------------------------------------------------------------
# El observador · extensión declarada del `Teacher` de Genesis
# ---------------------------------------------------------------------------
class Observador:
    """Lee las dos corrientes, **no actúa**, y escribe el genoma del linaje.

    Extensión declarada del `Teacher` de `runtime/organism/teacher.py` (Genesis), que ya
    ordena las heridas por severidad y destila `avoid` antes que `prefer`. Lo que añade:
    el que reflexiona es **otra unidad** y no un modelo de lenguaje; es **determinista**;
    lee **dos vidas** y se queda con lo que **coincide**; y escribe al **genoma del
    linaje** en vez de a la experiencia del mismo organismo.
    """

    def __init__(self, n_max, ve_V=True):
        self.ve_V = ve_V            # decisión suministrada: la V de los otros es pública
        self.hip = {}               # una hipótesis por corriente, con el mecanismo de 02
        for quien in ("A", "B"):
            self.hip[quien] = m10.UnidadFase2(n_max=n_max)
        self.libro = {}             # palabra -> [veces que precedió una caída, veces que no]
        self.muertes = []
        self.saltos = []
        self.c = Counter()

    def mirar(self, quien, a, simbolo, dv, ultimas):
        """Una observación prestada. El observador aprende de experiencia que no es suya."""
        self.hip[quien].leer(a, simbolo)
        self.c[f"observados_{quien}"] += 1
        if len(ultimas) >= 1:
            w = tuple(ultimas)
            e = self.libro.setdefault(w, [0, 0])
            if dv < -V_DESGASTE:
                e[0] += 1
            elif dv > 0:
                e[1] += 1

    def anotar_muerte(self, quien, ultimas, V_antes):
        self.muertes.append(dict(quien=quien, palabra=list(ultimas), dano=round(V_antes, 4)))
        self.c["muertes_vistas"] += 1

    def anotar_salto(self, cual):
        self.saltos.append(cual)

    def componer(self, todo=False):
        g = escribir_genoma(
            historias=None,
            maquinas=[self.hip["A"].trans, self.hip["B"].trans],
            muertes=[dict(palabra=tuple(m["palabra"]), dano=m["dano"]) for m in self.muertes],
            saltos=self.saltos, todo=todo)
        # y lo que el libro marca como mortal aunque nadie haya muerto allí: lo que bajó V
        # en CUALQUIERA de los dos (la asimetría del riesgo, §2-bis de la Fase 3)
        # Sólo palabras de DOS letras o más: prohibir una letra sola no es una prohibición,
        # es una amputación del alfabeto, y con dos letras deja al actor sin itinerario
        # (E-56). La granularidad de una prohibición es una SITUACIÓN, no un símbolo.
        malas = sorted((w for w, (mal, bien) in self.libro.items()
                        if mal > 0 and bien == 0 and len(w) >= 2),
                       key=lambda w: (-self.libro[w][0], w))
        for w in malas:
            if list(w) not in g["prohibiciones"] and (
                    todo or len(g["prohibiciones"]) < TOPE_GENOMA["prohibiciones"]):
                g["prohibiciones"].append(list(w))
        g["contadores"] = dict(self.c)
        return g


# ---------------------------------------------------------------------------
# Una generación: A y B viven, O mira, y el hijo de O actúa
# ---------------------------------------------------------------------------
def una_generacion(A, B, n, vida, futuro, n_max, genoma_entrada, celda, semilla):
    """Devuelve las medidas de la generación y el genoma que deja para la siguiente."""
    d_menos, d_mas = mundo_con_V(A, B, n, semilla)
    step = paso_de(A, B)
    est = alcanzables(A, B)
    simetrico = (celda == "simetrico")
    xA = 0
    xB = 0 if simetrico else step(0, vida[0])[0]
    itA = list(vida)
    itB = list(vida) if simetrico else list(vida[1:]) + [vida[0]]
    actA = Actor(n_max, genoma_entrada, nombre="A")
    actB = Actor(n_max, genoma_entrada, nombre="B")
    for act in (actA, actB):
        act.d_menos, act.d_mas = d_menos, d_mas
    O = Observador(n_max, ve_V=DECISIONES["ve_la_V_de_los_otros"]) if celda not in ("DOS",) else None
    tope = m10._tope_palabra(n_max)
    colaA, colaB = [], []
    cruces = 0
    for t in range(1, len(vida) + 1):
        for act, it, cola, otro in ((actA, itA, colaA, actB), (actB, itB, colaB, actA)):
            if not act.viva:
                continue
            # la asimetría obliga: sin ella no cruza ni un bit (E-47)
            a = cola.pop(0) if cola else it[(t - 1) % len(it)]
            if act.orden_letras != tuple(LETTERS):
                a = "A" if a == "B" else "B"      # el salto de disposición invierte las letras
            # Lo que act PROHÍBE por genoma: **la palabra que está por completar**, no la
            # letra sola. E-56: preguntaba `prohibida([a])` —«¿está prohibida esta letra?»—
            # cuando el genoma guarda «esta PALABRA mató». Medido: de 23 prohibiciones, 19
            # eran de dos letras y **nunca se consultaban** (genoma escrito y no leído), y
            # las 4 de una letra se consultaban en CADA paso e invertían la letra siempre
            # («nunca tomes A»), con 3 000-6 000 «muertes evitadas» por generación y el
            # alcance cayendo de 0,46 a 0,04. El genoma era lastre muerto o una apisonadora,
            # nunca lo que se quiso. La clave correcta es el sufijo que la acción crearía.
            futura = tuple(getattr(act, "ultimas", ())) + (a,)
            if act.prohibida(list(futura)) or act.prohibida(list(futura[-2:])):
                act.muertes_evitadas += 1
                act.c["evito_una_prohibida"] += 1
                a = "A" if a == "B" else "B"
            V_antes = act.V
            ultimas_antes = getattr(act, "ultimas", ())
            x = xA if act is actA else xB
            y = act.paso(step, x, a)
            if act is actA:
                xA = y
            else:
                xB = y
            if O is not None:
                O.mirar(act.nombre, a, act.historia[-1][1], act.historia[-1][2],
                        getattr(act, "ultimas", ()))   # ve ΔV: la V es pública (decisión)
            if not act.viva and O is not None:
                O.anotar_muerte(act.nombre, getattr(act, "ultimas", ()), V_antes)
            if act.saltos and O is not None and len(O.saltos) < len(act.saltos):
                O.anotar_salto(act.saltos[-1])
        # enseñanza mutua, con el disparo que la Fase 2 midió que es el que enseña
        if actA.viva and actB.viva and not simetrico:
            for quien, otro, cola in ((actA, actB, colaB), (actB, actA, colaA)):
                if cola:
                    continue
                w = m10.palabra_discrepante(otro.u.trans, otro.u.q,
                                            lambda q, b: quien.u.trans.get((q, b)),
                                            quien.u.q, tope, "corta")
                if w:
                    cola.extend(w)
                    cruces += 1
    med = {}
    for act in (actA, actB):
        m = medir(act.u, step, xA if act is actA else xB, futuro, est, {})
        med[act.nombre] = dict(identifica=bool(m["identifica"]), exactitud=m["exactitud"],
                               V=round(act.V, 4), viva=act.viva, saltos=list(act.saltos),
                               muertes_evitadas=act.muertes_evitadas, estados=act.u.n)
    genoma = O.componer(todo=(celda == "O-todo")) if O is not None else genoma_vacio()
    return dict(medidas=med, genoma=genoma, cruces=cruces,
                observador=dict(O.c) if O else {}), genoma


def un_mundo(n, idx, celda, generaciones, aqui=None):
    A, B = sistema_por_indice(n, idx)
    vida = shortlex(range(1, L_de(n) + 1))
    futuro = shortlex((n, n + 1))
    n_max = n + 2
    est = alcanzables(A, B)
    Tv = mealy_verdadera(A, B, est)
    nmin, bloque = minimizar(Tv, est)
    genoma = genoma_vacio()
    gens = []
    for k in range(1, generaciones + 1):
        # el hijo nace con el genoma de la generación anterior y SIN traza; la celda
        # «hijo-sin-genoma» es el control que nace sin él
        entrada = genoma_vacio() if celda == "hijo-sin-genoma" else genoma
        r, genoma = una_generacion(A, B, n, vida, futuro, n_max, entrada, celda, idx + k)
        harlow = sum(1 for q in ("A", "B") if r["medidas"][q]["identifica"]) / 2.0
        gens.append(dict(generacion=k, harlow=harlow,
                         vivas=sum(1 for q in ("A", "B") if r["medidas"][q]["viva"]) / 2.0,
                         muertes_evitadas=sum(r["medidas"][q]["muertes_evitadas"] for q in ("A", "B")),
                         prohibiciones=len(genoma["prohibiciones"]),
                         relaciones=len(genoma["relaciones"]),
                         restricciones=len(genoma["restricciones"]),
                         cruces=r["cruces"], medidas=r["medidas"]))
    # la prueba de renombramiento de B₀, obligatoria antes de dar nada por bueno
    pasa = prueba_de_renombramiento(A, B, n, genoma)
    mut = mutante_genoma_con_estados(Tv)
    pasa_mut = prueba_de_renombramiento(A, B, n, mut)
    return dict(exploratorio=EXPLORATORIO, celda=celda, n=n, idx=idx, n_min=nmin,
                generaciones=gens, genoma_final=genoma,
                renombramiento_ok=bool(pasa), renombramiento_mutante_ok=bool(pasa_mut),
                decisiones_suministradas=DECISIONES)


# ---------------------------------------------------------------------------
# Campaña exploratoria (T5-bis)
# ---------------------------------------------------------------------------
def _una(args):
    n, idx, celda, gens = args
    try:
        return un_mundo(n, idx, celda, gens)
    except Exception as e:                       # una celda que revienta no mata la campaña
        return dict(exploratorio=EXPLORATORIO, celda=celda, n=n, idx=idx,
                    error=f"{type(e).__name__}: {e}")


def banco_de(aqui, por_estrato=3):
    """El banco madre de T1 si existe; si no, los W₂ componibles de n=3. Se dice cuál."""
    ruta = os.path.join(aqui, "artifacts", "banco_madre.json")
    if os.path.exists(ruta):
        b = json.load(open(ruta, encoding="utf-8"))
        mundos, estratos = [], {}
        for n, d in sorted(b["bancos"].items()):
            por = {}
            for idx in d["indices"]:
                A, B = sistema_por_indice(int(n), idx)
                _, nm, _ = verdad(A, B)
                por.setdefault(nm, []).append(idx)
            for nm, lista in sorted(por.items()):
                paso = max(1, len(lista) // por_estrato)
                tom = lista[::paso][:por_estrato]
                no_vacio(tom, f"estrato n={n}, n_min={nm} del banco madre para TRES")
                estratos[f"n{n}_nmin{nm}"] = len(tom)
                mundos += [(int(n), i) for i in tom]
        return mundos, f"banco madre de T1 (estratificado por n_min: {estratos}; sha256 " \
                       f"{b['sha256_del_contenido'][:16]}…)"
    buf = io.StringIO()
    vida1 = shortlex(range(1, L_de(N1) + 1))
    fut1 = shortlex((L_de(N1) + 1, L_de(N1) + 2))
    el = mundos_1(vida1, fut1, 2 * N1 + 2, buf)
    return [(N1, i) for i in el[:12]], "W₂ componibles de n=3 (el banco madre no existía)"


def main(por_estrato=3, trabajadores=11, aqui=None, celdas=CELDAS):
    out = ["# T5-bis · TRES exploratorio · 29-oct-2026", "",
           "**EXPLORATORIO.** No certifica nada, no cierra nada, no entra a ninguna puerta.",
           "",
           f"**Decisiones suministradas por Fable** (revisables por Wis antes de la ficha): "
           f"el observador **{DECISIONES['cuando_actua_el_observador']}**; la V de los otros "
           f"**{'es pública' if DECISIONES['ve_la_V_de_los_otros'] else 'no se ve'}**; "
           f"**{DECISIONES['generaciones']} generaciones**."]
    mundos, de_donde = banco_de(aqui, por_estrato)
    out.append(f"\n**Mundo:** {de_donde} · **{len(mundos)}** mundos.")
    out.append(f"**Celdas:** {', '.join(celdas)}.")
    tareas = [(n, i, c, DECISIONES["generaciones"]) for (n, i) in mundos for c in celdas]
    no_vacio(tareas, "celdas de TRES")
    ruta = os.path.join(aqui, "artifacts", "unidad_minima_13_tres.jsonl")
    salida_a_fichero(ruta, "filas de TRES (exploratorio)")
    filas, t0 = [], time.perf_counter()
    with open(ruta, "a", encoding="utf-8") as f:
        if trabajadores > 1:
            import multiprocessing as mp
            with mp.get_context("fork").Pool(trabajadores) as pool:
                for fila in pool.imap(_una, tareas, chunksize=1):
                    filas.append(fila)
                    f.write(json.dumps(fila, ensure_ascii=False) + "\n")
                    f.flush()
                    os.fsync(f.fileno())
        else:
            for t in tareas:
                fila = _una(t)
                filas.append(fila)
                f.write(json.dumps(fila, ensure_ascii=False) + "\n")
                f.flush()
                os.fsync(f.fileno())
    out.append(f"**Reloj:** {time.perf_counter() - t0:.0f} s. Filas: {len(filas)}; "
               f"con error: {sum(1 for r in filas if 'error' in r)}.")
    errs = Counter(r["error"].split(":")[0] for r in filas if "error" in r)
    if errs:
        out.append(f"**Errores de celda:** {dict(errs)}")
    buenas = [r for r in filas if "error" not in r]
    # --- la prueba de renombramiento y su mutante
    if buenas:
        ok = sum(1 for r in buenas if r["renombramiento_ok"])
        mut = sum(1 for r in buenas if r["renombramiento_mutante_ok"])
        out.append(f"\n### Prueba de renombramiento (contrato B₀)\n")
        out.append(f"- El genoma pasa el renombramiento en **{ok} de {len(buenas)}** mundos.")
        out.append(f"- Su **mutante** —un genoma que nombra estados— lo pasa en **{mut} de "
                   f"{len(buenas)}**: debe ser **0**, y si no lo es la prueba no vigila nada.")
    # --- las curvas por celda y generación
    out.append("\n### Curvas por celda y generación\n")
    out.append("| celda | gen | Harlow (identifica) | vivas | muertes evitadas | prohibiciones | "
               "relaciones | cruces |")
    out.append("|---|---|---|---|---|---|---|---|")
    R = {}
    for c in celdas:
        F = [r for r in buenas if r["celda"] == c]
        if not F:
            continue
        R[c] = {}
        for k in range(1, DECISIONES["generaciones"] + 1):
            G = [g for r in F for g in r["generaciones"] if g["generacion"] == k]
            if not G:
                continue
            m = len(G)
            d = dict(mundos=m,
                     harlow=sum(g["harlow"] for g in G) / m,
                     vivas=sum(g["vivas"] for g in G) / m,
                     evitadas=sum(g["muertes_evitadas"] for g in G) / m,
                     prohibiciones=sum(g["prohibiciones"] for g in G) / m,
                     relaciones=sum(g["relaciones"] for g in G) / m,
                     cruces=sum(g["cruces"] for g in G) / m)
            R[c][k] = d
            out.append(f"| {c} | {k} | {d['harlow']:.3f} | {d['vivas']:.3f} | "
                       f"{d['evitadas']:.1f} | {d['prohibiciones']:.1f} | "
                       f"{d['relaciones']:.1f} | {d['cruces']:.1f} |")
    texto = "\n".join(out) + "\n"
    with open(os.path.join(aqui, "T5bis_TRES_EXPLORATORIO.md"), "w", encoding="utf-8") as fh:
        fh.write(texto)
    with open(os.path.join(aqui, "artifacts", "unidad_minima_13_tres.json"), "w",
              encoding="utf-8") as fh:
        json.dump(dict(exploratorio=EXPLORATORIO, resumen=R, decisiones=DECISIONES,
                       banco=de_donde, sha256_codigo=SHA_13, arranque=ARRANQUE, texto=texto),
                  fh, ensure_ascii=False, indent=1)
        fh.flush()
        os.fsync(fh.fileno())
    return texto


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    _sin_premio(open(os.path.abspath(__file__), encoding="utf-8").read()
                .split("class Actor")[1].split("def genoma_vacio")[0])
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    pe = int(args[0]) if args else 3
    trab = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--trabajadores=")), 11)
    sys.stdout.write(main(pe, trab, here))
    sys.stdout.write(f"azar usado: {sin_azar_usado(['unidad_minima_13_tres_elementos'])}; "
                     f"arranque {ARRANQUE}; sha256 de 13 al arrancar: {SHA_13[:16]}…; "
                     f"EXPLORATORIO={EXPLORATORIO}\n")
    informe()
