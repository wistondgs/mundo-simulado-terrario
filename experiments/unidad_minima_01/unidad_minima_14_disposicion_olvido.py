#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UNIDAD-MINIMA-14 · T2 · la disposición del olvido, medida antes de que Wis elija.

La pregunta del cierre de la Fase 2 es de Wis: **el olvido que salva impide heredarse,
¿se cambia el órgano o se cambia el mundo?** Fable señala una tercera opción que no está
medida y es la más barata: **cambiar la disposición** —ventana, núcleo, presupuesto— sin
tocar el mecanismo. Esto la mide, para que mañana la decisión tenga los tres caminos con
número en vez de dos con número y uno con intuición.

**Factores** (24 celdas):
- `ventana` ∈ {128, 512, 2048, ∞} — cuántos pasos retiene.
- `nucleo` ∈ {64, 256, **`maquina`**} — qué conserva al fracasar. `maquina` es la opción
  «cambiar el órgano» de Wis traída aquí **como disposición**: al no poder explicar su
  memoria, **conserva la máquina y suelta la traza**, que es exactamente lo que C5 hace al
  cambiar de mundo, en vez de volver a sus últimos 64 pasos.
- `presupuesto` ∈ {200 000, 2 000 000} pasos por intento.
- La celda (∞, —, ∞) es **M-c** y debe reproducir el ahogo: es el mutante del instrumento.

**Bancos:** los 174 W₁ de n=3 con sus W₂ (barato; control de que nada se pierde donde todo
satura) **y** el banco madre de T1, donde el olvido se dispara 31–86 veces por vida.

**Predicción, escrita antes de correr** (de Fable, y la hago mía porque es falsable): en n=3
ninguna celda cambia el alcance —todo satura—; en el banco madre, el núcleo `maquina` baja
los olvidos **por debajo de 2 por vida sin perder exactitud**, y es la única celda donde eso
pasa. Si no pasa, «cambiar la disposición» muere con número y quedan las dos opciones de Wis.

Sin azar. Reanudable con `fsync` por fila. Ningún `break` en un bucle de vida (E-39): agotar
el presupuesto dispara el olvido, no termina la vida. Tope de reloj **por celda**, declarado,
porque sin él la celda (∞, ∞) no termina (E-32).
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
import time
from collections import Counter
from statistics import NormalDist

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import unidad_minima_08_fase2 as m8                                       # noqa: E402
from unidad_minima_01 import predict, run_world, shortlex                 # noqa: E402
from unidad_minima_02_incremental import Unidad                           # noqa: E402
from unidad_minima_05_banco import L_de, alcanzables, paso_de, sistema_por_indice  # noqa: E402
from unidad_minima_08_fase2 import (                                      # noqa: E402
    N1, PresupuestoAgotado, UnidadFase2, medir, mundo_2, mundos_1, patrones, verdad, vivir,
)
from guardas import informe, no_vacio, salida_a_fichero, sin_azar_usado    # noqa: E402

SHA_14 = hashlib.sha256(open(os.path.abspath(__file__), "rb").read()).hexdigest()
ARRANQUE = time.strftime("%Y-%m-%dT%H:%M:%S")

INFINITO = 10 ** 15
VENTANAS = (128, 512, 2048, INFINITO)
NUCLEOS = (64, 256, "maquina", "maquina+reparacion")
# 29-oct, DESPUÉS de la primera pasada y antes de concluir: «conservar la máquina y soltar la
# traza» a secas **no** es la opción de Wis, es media. Medido: dispara los olvidos a 110-875
# por vida y pierde alcance (0,500 contra 1,000), porque al quedarse sin pila de decisiones la
# siguiente refutación vuelve a fracasar en el acto y vuelve a olvidar, en bucle. Lo que C5
# tiene y esto no es la **reparación local**: la transición refutada se vuelve revisable en el
# paso actual en vez de disparar la relectura. Se prueban las dos formas: declarar muerta la
# tercera opción con la forma incompleta habría sido un falso negativo.
PRESUPUESTOS = (200_000, 2_000_000)
HITOS = (64, 128, 256, 512, 1024, 2048)
TOPE_CELDA_S = 45          # tope de reloj por celda; al alcanzarlo la unidad queda
                           # PARALIZADA (sigue viviendo, deja de intentar explicar), nunca
                           # se corta el bucle de vida (E-39)
ALFA = 0.05


class UnidadDisposicion(UnidadFase2):
    """La unidad de 08 con sus tres disposiciones como parámetros de instancia, y una
    tercera forma de olvidar."""

    def __init__(self, n_max=4, ventana=512, nucleo=64, presupuesto=200_000,
                 tope_s=TOPE_CELDA_S):
        UnidadFase2.__init__(self, n_max=n_max)
        self.ventana, self.nucleo, self.presupuesto = ventana, nucleo, presupuesto
        self.tope_s, self.t0 = tope_s, time.perf_counter()
        self.paralizada = False

    # --- la ventana, por instancia
    def leer(self, a, o):
        if self.paralizada or (time.perf_counter() - self.t0) > self.tope_s:
            if not self.paralizada:
                self.paralizada = True
                self.c["paralizada_desde"] = len(self.trace)
            self.c["pasos_sin_aprender"] += 1
            return
        while len(self.trace) >= self.ventana:
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

    def _avanzar(self, i, a, o):
        """Con el núcleo `maquina+reparacion`, una transición refutada que no tiene decisión
        en la pila se vuelve **revisable en el paso actual** —es el `_avanzar` de C5— en vez
        de disparar la relectura o el olvido."""
        if self.nucleo == "maquina+reparacion":
            key = (self.q, a)
            t = self.trans.get(key)
            if t is not None and t[1] != o and not any(cp[1] == key for cp in self.choices):
                self.c["pasos_avanzados"] += 1
                self.c["reparaciones_locales"] += 1
                self._intento = getattr(self, "_intento", 0) + 1
                if self._intento > self.presupuesto:
                    raise PresupuestoAgotado()
                self.choices.append([i, key, 0, self.used])
                self.trans[key] = (0, o)
                self.used = max(self.used, 1)
                self.q = 0
                return True
        self.c["pasos_avanzados"] += 1
        self._intento = getattr(self, "_intento", 0) + 1
        if self._intento > self.presupuesto:
            raise PresupuestoAgotado()
        return Unidad._avanzar(self, i, a, o)

    def _olvidar(self):
        """Tres formas de no poder explicar la memoria:
        · un número → conservar los últimos k pasos y releerlos (lo de 08);
        · `maquina`  → **conservar la máquina y soltar la traza**: la hipótesis sigue en pie
          y la memoria se vacía, que es lo que C5 hace al cambiar de mundo. La pila de
          decisiones se vacía también, así que lo que queda es revisable en el paso actual.
        """
        self.c["olvidos"] += 1
        if str(self.nucleo).startswith("maquina"):
            self.trace, self.choices = [], []     # la máquina (`trans`, `q`, `n`) se conserva
            self._intento = 0
            return
        nucleo = self.trace[-self.nucleo:] if self.nucleo else []
        self.trace, self.trans, self.choices, self.q, self.n, self.used = [], {}, [], 0, 1, 1
        self._intento = 0
        try:
            for a, o in nucleo:
                self.trace.append((a, o))
                Unidad.leer(self, *self.trace.pop())
        except (PresupuestoAgotado, RuntimeError):
            self.trace, self.trans, self.choices, self.q, self.n, self.used = [], {}, [], 0, 1, 1
            self.c["olvidos_totales"] += 1


def vivir_simple(u, step, x, itinerario, futuro):
    """Vivir y medir la curva. Sin maestro, sin elegir, **sin `break`** (E-39)."""
    curva = {}
    for t in range(1, len(itinerario) + 1):
        if t - 1 in HITOS:
            vf, _ = run_world(step, x, futuro)
            h, nr, _ = predict(u.trans, u.q, futuro, vf)
            curva[t - 1] = dict(exactitud=h / len(futuro),
                                identifica=(h == len(futuro) and nr == 0))
        a = itinerario[t - 1]
        p = u.predecir(a)
        x, o = step(x, a)
        u.leer(a, o)
    vf, _ = run_world(step, x, futuro)
    h, nr, _ = predict(u.trans, u.q, futuro, vf)
    fin = dict(exactitud=h / len(futuro), identifica=(h == len(futuro) and nr == 0))
    for hh in HITOS:
        curva.setdefault(hh, fin)
    return dict(x=x, curva=curva, fin=fin)


def _una_celda(args):
    banco, idx, ventana, nucleo, presupuesto, meta = args
    nombre = f"v{'inf' if ventana >= INFINITO else ventana}_n{nucleo}_p{presupuesto}"
    t0 = time.perf_counter()
    if banco == "n3":
        A, B = sistema_por_indice(N1, idx["w1"])
        A2, B2 = mundo_2(A, B, N1, tuple(idx["patron"]), idx["componible"])
        vida1 = shortlex(range(1, L_de(N1) + 1))
        vida = shortlex(range(1, L_de(2 * N1) + 1))
        futuro = shortlex((2 * N1, 2 * N1 + 1))
        n_max = 2 * N1 + 2
        madre = UnidadFase2(n_max=n_max)
        x0 = vivir(madre, paso_de(A, B), 0, vida1, False)["x"]
        step = paso_de(A2, B2)
        est = alcanzables(A2, B2)
        _, nmin, _ = verdad(A2, B2)
    else:                                   # banco madre: W1 de n=8, la vida entera
        n = idx["n"]
        A, B = sistema_por_indice(n, idx["idx"])
        vida = shortlex(range(1, L_de(n) + 1))
        futuro = shortlex((n, n + 1))
        n_max, x0 = n + 2, 0
        step = paso_de(A, B)
        est = alcanzables(A, B)
        nmin = idx["n_min"]
    u = UnidadDisposicion(n_max=n_max, ventana=ventana, nucleo=nucleo,
                          presupuesto=presupuesto)
    v = vivir_simple(u, step, x0, vida, futuro)
    m = medir(u, step, v["x"], futuro, est, {})
    return dict(banco=banco, celda=nombre, ventana=("inf" if ventana >= INFINITO else ventana),
                nucleo=str(nucleo), presupuesto=presupuesto,
                n_min=nmin, pasos=len(vida), coste_intrinseco=meta.get("coste_intrinseco"),
                olvidos=u.c["olvidos"], olvidos_totales=u.c["olvidos_totales"],
                olvidados=u.c["pasos_olvidados"], sin_aprender=u.c["pasos_sin_aprender"],
                reparaciones_locales=u.c["reparaciones_locales"],
                paralizada=bool(u.paralizada), estados=u.n,
                identifica=bool(m["identifica"]), exactitud=m["exactitud"],
                curva={h: v["curva"][h] for h in HITOS}, reloj=round(time.perf_counter() - t0, 2),
                **{k: idx[k] for k in ("w1", "patron", "componible", "idx") if k in idx})


def _ee(p, n):
    return (p * (1 - p) / n) ** 0.5 if n else 0.0


def resumen(filas, out):
    R = {}
    for banco in sorted({f["banco"] for f in filas}):
        F = [f for f in filas if f["banco"] == banco]
        base = [f for f in F if f["ventana"] == 512 and f["nucleo"] == "64"
                and f["presupuesto"] == 200_000]
        out.append(f"\n### Banco «{banco}» · {len(F)} celdas medidas sobre "
                   f"{len({f.get('idx', (f.get('w1'), str(f.get('patron')))) for f in F})} mundos\n")
        out.append("| ventana | núcleo | presupuesto | mundos | **olvidos/vida** | alcance 64 | "
                   "alcance 256 | alcance final | exactitud | paralizadas |")
        out.append("|---|---|---|---|---|---|---|---|---|---|")
        R[banco] = {}
        for vt in ("128", "512", "2048", "inf"):
            for nu in ("64", "256", "maquina", "maquina+reparacion"):
                for pr in PRESUPUESTOS:
                    G = [f for f in F if str(f["ventana"]) == vt and f["nucleo"] == nu
                         and f["presupuesto"] == pr]
                    if not G:
                        continue
                    k = len(G)
                    g = lambda c: sum(f[c] for f in G) / k
                    r = dict(mundos=k, olvidos=g("olvidos"),
                             a64=sum(f["curva"][64]["identifica"] for f in G) / k,
                             a256=sum(f["curva"][256]["identifica"] for f in G) / k,
                             afin=sum(f["identifica"] for f in G) / k,
                             exactitud=g("exactitud"),
                             paralizadas=sum(f["paralizada"] for f in G))
                    R[banco][f"v{vt}_n{nu}_p{pr}"] = r
                    marca = " ←" if (nu == "maquina" and r["olvidos"] < 2) else ""
                    out.append(f"| {vt} | {nu} | {pr} | {k} | **{r['olvidos']:.1f}**{marca} | "
                               f"{r['a64']:.3f} | {r['a256']:.3f} | {r['afin']:.3f} | "
                               f"{r['exactitud']:.4f} | {r['paralizadas']} |")
    return R


def puerta(R, out):
    g = {}
    for banco, cel in R.items():
        if not cel:
            continue
        base = cel.get("v512_n64_p200000")
        maq = [v for k, v in cel.items() if "_nmaquina" in k]
        if base and maq:
            mejor = min(maq, key=lambda v: v["olvidos"])
            g[f"{banco}: el núcleo «maquina» baja los olvidos por debajo de 2 por vida"] = \
                mejor["olvidos"] < 2.0
            g[f"{banco}: y lo hace SIN perder exactitud respecto de la disposición de 08"] = \
                mejor["exactitud"] >= base["exactitud"] - 0.01
            g[f"{banco}: y es la ÚNICA familia de celdas donde los olvidos bajan de 2"] = \
                (mejor["olvidos"] < 2.0 and
                 all(v["olvidos"] >= 2.0 for k, v in cel.items() if "_nmaquina" not in k))
        mc = cel.get("vinf_n64_p2000000") or cel.get("vinf_n256_p2000000")
        if mc and base:
            g[f"{banco}: M-c (ventana ∞, presupuesto grande) reproduce el ahogo"] = \
                mc["afin"] < base["afin"] - 0.02 or mc["paralizadas"] > 0
    out.append("\n### Puerta de T2\n")
    for k, v in sorted(g.items()):
        out.append(f"- [{'PASS' if v else 'FAIL'}] {k}")
    return g


def main(muestra_madre=40, trabajadores=11, aqui=None, solo_madre=False):
    out = ["# T2 · la disposición del olvido · 29-oct-2026", "",
           "**Exploratorio-medido:** celdas con mutante (M-c) y predicción escrita antes; "
           "no cierra fase."]
    # --- los dos bancos
    buf = io.StringIO()
    vida1 = shortlex(range(1, L_de(N1) + 1))
    fut1 = shortlex((L_de(N1) + 1, L_de(N1) + 2))
    elegibles = mundos_1(vida1, fut1, 2 * N1 + 2, buf)
    tareas = []
    # banco n=3: un W2 componible por W1, los 174
    for w1 in elegibles:
        A, B = sistema_por_indice(N1, w1)
        _, nmin1, _ = verdad(A, B)
        for patron in patrones(N1):
            A2, B2 = mundo_2(A, B, N1, patron, True)
            _, nmin2, _ = verdad(A2, B2)
            if nmin2 > nmin1:
                tareas.append(("n3", dict(w1=w1, patron=list(patron), componible=True), {}))
                break
    n3 = len(tareas)
    if solo_madre:
        tareas, n3 = [], 0        # el banco n=3 ya se midió en la primera pasada y satura
    # banco madre, muestra esparcida y declarada
    banco = json.load(open(os.path.join(aqui, "artifacts", "banco_madre.json"), encoding="utf-8"))
    # MUESTRA ESTRATIFICADA POR n_min, y cada estrato pasa `no_vacio` (condición de Fable,
    # 29-oct): una muestra por paso sobre la lista entera puede dejar un estrato vacío sin
    # que nada avise, y entonces «la disposición no cambia nada» sería una frase sobre los
    # estratos que entraron por casualidad. `muestra_madre` es ahora POR ESTRATO.
    madre, estratos = [], {}
    for n, b in sorted(banco["bancos"].items()):
        porestrato = {}
        for idx, coste in zip(b["indices"], b["coste_intrinseco"]):
            A, B = sistema_por_indice(int(n), idx)
            _, nm, _ = verdad(A, B)
            porestrato.setdefault(nm, []).append((idx, coste))
        for nm, lista in sorted(porestrato.items()):
            paso = max(1, len(lista) // max(1, muestra_madre))
            tomados = lista[::paso][:muestra_madre]
            no_vacio(tomados, f"estrato n={n}, n_min={nm} del banco madre")
            estratos[f"n{n}_nmin{nm}"] = len(tomados)
            for idx, coste in tomados:
                madre.append((int(n), idx, coste))
    for n, idx, coste in madre:
        A, B = sistema_por_indice(n, idx)
        _, nmin, _ = verdad(A, B)
        tareas.append(("madre", dict(n=n, idx=idx, n_min=nmin),
                       dict(coste_intrinseco=coste)))
    out.append(f"\n**Bancos:** {n3} mundos W₂ componibles de n=3 (control) y "
               f"**{len(madre)}** del banco madre, **muestra estratificada por n_min** "
               f"(hasta {muestra_madre} por estrato, cada estrato verificado no vacío): "
               f"{estratos}. Total del banco "
               f"{sum(len(b['indices']) for b in banco['bancos'].values())}; sha256 "
               f"`{banco['sha256_del_contenido'][:16]}…`.")
    # --- el producto de factores
    todo = [(b, i, vt, nu, pr, m) for (b, i, m) in tareas
            for vt in VENTANAS for nu in NUCLEOS for pr in PRESUPUESTOS]
    no_vacio(todo, "celdas de T2")
    out.append(f"**Celdas:** {len(VENTANAS)}×{len(NUCLEOS)}×{len(PRESUPUESTOS)} = "
               f"{len(VENTANAS)*len(NUCLEOS)*len(PRESUPUESTOS)} disposiciones × "
               f"{len(tareas)} mundos = **{len(todo)}** corridas de vida. Tope de reloj por "
               f"celda {TOPE_CELDA_S} s; al alcanzarlo la unidad queda paralizada y la vida "
               f"sigue (E-39).")
    ruta = os.path.join(aqui, "artifacts", "unidad_minima_14_disposicion.jsonl")
    salida_a_fichero(ruta, "filas de T2")
    filas, t0 = [], time.perf_counter()
    with open(ruta, "a", encoding="utf-8") as f:
        if trabajadores > 1:
            import multiprocessing as mp
            with mp.get_context("fork").Pool(trabajadores) as pool:
                for fila in pool.imap(_una_celda, todo, chunksize=2):
                    filas.append(fila)
                    f.write(json.dumps(fila, ensure_ascii=False) + "\n")
                    f.flush()
                    os.fsync(f.fileno())
        else:
            for t in todo:
                fila = _una_celda(t)
                filas.append(fila)
                f.write(json.dumps(fila, ensure_ascii=False) + "\n")
                f.flush()
                os.fsync(f.fileno())
    out.append(f"**Reloj:** {time.perf_counter() - t0:.0f} s con {trabajadores} trabajadores.")
    R = resumen(filas, out)
    g = puerta(R, out)
    texto = "\n".join(out) + "\n"
    with open(os.path.join(aqui, "T2_DISPOSICION_OLVIDO.md"), "w", encoding="utf-8") as fh:
        fh.write(texto)
    with open(os.path.join(aqui, "artifacts", "unidad_minima_14_disposicion.json"), "w",
              encoding="utf-8") as fh:
        json.dump(dict(resumen=R, puerta=g, sha256_codigo=SHA_14, arranque=ARRANQUE,
                       texto=texto), fh, ensure_ascii=False, indent=1)
        fh.flush()
        os.fsync(fh.fileno())
    return texto


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    mm = int(args[0]) if args else 40
    trab = next((int(a.split("=")[1]) for a in sys.argv if a.startswith("--trabajadores=")), 11)
    sys.stdout.write(main(mm, trab, here, "--solo-madre" in sys.argv))
    sys.stdout.write(f"azar usado: {sin_azar_usado(['unidad_minima_14_disposicion_olvido'])}; "
                     f"arranque {ARRANQUE}; sha256 de 14 al arrancar: {SHA_14[:16]}…\n")
    informe()
