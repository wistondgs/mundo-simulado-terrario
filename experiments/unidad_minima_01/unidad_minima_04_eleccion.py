#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UNIDAD-MINIMA-04 · elección por conveniencia bajo orientación externa.

La meta viene de fuera: «que la próxima reacción a L sea v». La unidad recorre
las palabras de su propio repertorio en orden shortlex, predice con su máquina
adquirida, y ejecuta la más corta que cumple. No se le dice cuál es.

Dos criterios, que no son la misma pregunta y se informan por separado:
  desde_q    la palabra cumple desde el estado que la unidad cree ocupar;
  robusto    la palabra cumple desde TODOS sus estados, es decir, es una palabra
             de reset con imagen prescrita (Volkov, LNCS 5196; ver el gate).
El robusto es el que discrimina, porque es el que ninguna letra sola satisface.

Tres partes compiten con la misma meta: la unidad con su máquina, la unidad
LESIONADA (la distinción colapsada a un estado, nada más) y el control REACTIVO
(tabla (reacción previa, letra) -> reacción mayoritaria), que planifica igual de
bien que puede: simula su propia tabla sobre la palabra y mira qué predice.

La robustez NO se cree, se mide por fuera: la palabra elegida se ejecuta en el
mundo real desde los dos estados ocultos posibles, y se comprueba si la meta se
cumple en ambos. Certificar no es cumplir.

Lo SUMINISTRADO: la meta, el alfabeto, el tope de longitud 4, el orden shortlex
como desempate, y la predicción 0 por defecto cuando no hay ruta.
Lo ADQUIRIDO: la máquina, sus palabras, y cuál se eligió.

Predicciones escritas antes de correr: APERTURA_ELECCION_BAJO_ORIENTACION.md §5.
"""
from __future__ import annotations

import hashlib
import io
import itertools
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unidad_minima_01 import (  # noqa: E402
    LETTERS, LIFE_MAX_LEN, WORLDS, lesion, majority, reactive_table, run_world,
    shortlex, states_of,
)
from unidad_minima_02_incremental import Unidad  # noqa: E402

MAX_LEN = 4                      # tope declarado; la búsqueda es exhaustiva hasta aquí
METAS = (("B", 1), ("A", 1))     # (letra, valor) — suministradas, ver la enmienda de la ficha


def palabras_shortlex(max_len):
    for n in range(0, max_len + 1):
        for w in itertools.product(LETTERS, repeat=n):
            yield w


def cumple_desde(M, q, w, letra, valor):
    """¿Tras la palabra w, la máquina M predice `valor` para `letra`? None = sin ruta."""
    for a in w:
        t = M.get((q, a))
        if t is None:
            return None
        q = t[0]
    t = M.get((q, letra))
    return None if t is None else (t[1] == valor)


def elegir_maquina(M, q, letra, valor, robusto):
    qs = states_of(M)
    evaluadas = 0
    for w in palabras_shortlex(MAX_LEN):
        evaluadas += 1
        desde = qs if robusto else [q]
        res = [cumple_desde(M, s, w, letra, valor) for s in desde]
        if all(r is True for r in res):
            return "".join(w), evaluadas
    return None, evaluadas


def elegir_reactivo(tbl, prev_o, letra, valor):
    """El reactivo planifica con lo único que tiene: su tabla. No tiene estados
    sobre los que exigir robustez, así que sólo puede responder desde su reacción
    previa; esa carencia es el punto, no un handicap que le pongamos."""
    evaluadas = 0
    for w in palabras_shortlex(MAX_LEN):
        evaluadas += 1
        p = prev_o
        for a in w:
            p = majority(tbl.get((p, a), Counter()))
        if majority(tbl.get((p, letra), Counter())) == valor:
            return "".join(w), evaluadas
    return None, evaluadas


def ejecutar_en_el_mundo(step, x0, w, letra):
    """Ejecuta la palabra y luego la letra de la meta. Devuelve la reacción real."""
    x = x0
    for a in w:
        x, _ = step(x, a)
    _, o = step(x, letra)
    return o


def verdad_robusta(step, w, letra, valor):
    """¿La palabra cumple la meta desde los dos estados ocultos del mundo?"""
    return [ejecutar_en_el_mundo(step, x0, w, letra) == valor for x0 in (0, 1)]


def minimo_por_enumeracion(step, letra, valor):
    """La palabra más corta que cumple la meta en el MUNDO (no en ninguna máquina),
    desde los dos estados. Es el patrón de oro contra el que se mide la elección."""
    for w in palabras_shortlex(MAX_LEN):
        if all(verdad_robusta(step, w, letra, valor)):
            return "".join(w) or "ε", len(w)
    return None, None


def un_caso(name, step, letra, valor, out):
    life = shortlex(range(1, LIFE_MAX_LEN + 1))
    u, x = Unidad(), 0
    for a in life:
        x, o = step(x, a)
        u.leer(a, o)
    M, qs = u.trans, states_of(u.trans)
    tbl = reactive_table(u.trace)
    prev_o = u.trace[-1][1]
    Mles = lesion(M)

    # ¿la distinción está en condiciones de decidir esta meta?
    salidas_meta = {M[(s, letra)][1] for s in qs if (s, letra) in M}
    decide = len(salidas_meta) > 1

    oro, oro_len = minimo_por_enumeracion(step, letra, valor)
    r = dict(mundo=name, meta=f"reacción a {letra} = {valor}", estados=len(qs),
             la_distincion_decide_la_meta=decide,
             minimo_del_mundo=oro, minimo_longitud=oro_len)

    for etiqueta, elector in (
        ("unidad robusto", lambda: elegir_maquina(M, u.q, letra, valor, True)),
        ("unidad desde_q", lambda: elegir_maquina(M, u.q, letra, valor, False)),
        ("lesionada robusto", lambda: elegir_maquina(Mles, 0, letra, valor, True)),
        ("reactivo", lambda: elegir_reactivo(tbl, prev_o, letra, valor)),
    ):
        w, ev = elector()
        if w is None:
            r[etiqueta] = dict(palabra=None, declara_insatisfacible=True, evaluadas=ev)
            out.write(f"  {etiqueta:<19} declara INSATISFACIBLE (evaluó {ev} palabras)\n")
            continue
        wt = tuple(w)
        desde_los_dos = verdad_robusta(step, wt, letra, valor)
        desde_el_actual = ejecutar_en_el_mundo(step, x, wt, letra) == valor
        r[etiqueta] = dict(palabra=w or "ε", longitud=len(w), evaluadas=ev,
                           cumple_desde_el_estado_actual=desde_el_actual,
                           cumple_desde_los_dos_estados=all(desde_los_dos),
                           detalle_por_estado=desde_los_dos,
                           es_minima=(oro_len is not None and len(w) == oro_len))
        out.write(f"  {etiqueta:<19} elige «{w or 'ε'}» (long {len(w)}, evaluó {ev}) · "
                  f"real desde el estado actual: {'sí' if desde_el_actual else 'NO'} · "
                  f"desde los dos estados: {'sí' if all(desde_los_dos) else 'NO'} {desde_los_dos} · "
                  f"{'mínima' if r[etiqueta]['es_minima'] else 'NO mínima'}\n")
    return r


def campaign(out):
    report = {"casos": [], "max_len": MAX_LEN}
    out.write(f"palabras evaluadas en orden shortlex hasta longitud {MAX_LEN}, exhaustivo\n")
    out.write("«real desde los dos estados» se mide ejecutando en el mundo, no preguntando al agente\n\n")
    for name, step, _ in WORLDS:
        for letra, valor in METAS:
            oro, oro_len = minimo_por_enumeracion(step, letra, valor)
            clase = ("insatisfacible" if oro is None else
                     "trivial" if oro_len == 0 else f"exige {oro_len} paso(s)")
            out.write(f"=== {name} · meta: reacción a {letra} = {valor} · "
                      f"mínimo del mundo: {oro if oro else '—'} ({clase})\n")
            report["casos"].append(un_caso(name, step, letra, valor, out))
            out.write("\n")
    return report


def veredicto(report, out):
    def caso(mundo, letra):
        return next(c for c in report["casos"] if c["mundo"] == mundo and c["meta"].startswith(f"reacción a {letra}"))

    alias_B = caso("latch-edge (aliasado)", "B")
    vis_A = caso("visible (control)", "A")
    inerte_B = caso("bit inerte (control)", "B")
    g = {}
    g["aliasado: la unidad elige BA"] = alias_B["unidad robusto"].get("palabra") == "BA"
    g["aliasado: la palabra de la unidad cumple desde los dos estados"] = \
        alias_B["unidad robusto"].get("cumple_desde_los_dos_estados") is True
    g["aliasado: y es la mínima del mundo"] = alias_B["unidad robusto"].get("es_minima") is True
    g["aliasado: la lesionada no cumple desde los dos estados"] = \
        alias_B["lesionada robusto"].get("cumple_desde_los_dos_estados") is not True
    g["aliasado: el reactivo no cumple desde los dos estados"] = \
        alias_B["reactivo"].get("cumple_desde_los_dos_estados") is not True
    g["aliasado: la distinción decide la meta (actividad)"] = alias_B["la_distincion_decide_la_meta"]
    # Enmienda prospectiva del 2026-10-25, hallada en el paso de mutantes y ANTES de
    # correr lo real: aquí se le exigía al reactivo robustez frente a la ignorancia del
    # estado. En el mundo visible el reactivo NO es ignorante (su reacción previa es el
    # bit), así que esa exigencia le pide resolver un problema que allí no existe, y el
    # control no podría pasar nunca. Lo que discrimina es que el reactivo cumpla desde el
    # estado en que de hecho está, cosa que en el mundo aliasado no puede garantizar.
    g["visible: el reactivo cumple desde el estado actual (el test discrimina)"] = \
        vis_A["reactivo"].get("cumple_desde_el_estado_actual") is True
    g["bit inerte: las tres declaran insatisfacible"] = all(
        inerte_B[k].get("declara_insatisfacible") is True
        for k in ("unidad robusto", "lesionada robusto", "reactivo"))
    out.write("--- puerta de la ficha §11\n")
    for k, v in g.items():
        out.write(f"  [{'PASS' if v else 'FAIL'}] {k}\n")
    todo = all(g.values())
    out.write(f"VEREDICTO: {'PASS' if todo else 'FAIL'}\n")
    return dict(criterios=g, veredicto="PASS" if todo else "FAIL")


def main():
    buf = io.StringIO()
    rep = campaign(buf)
    rep["puerta"] = veredicto(rep, buf)
    return buf.getvalue(), rep


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    t1, report = main()
    t2, _ = main()
    h1, h2 = (hashlib.sha256(t.encode()).hexdigest() for t in (t1, t2))
    src = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    sys.stdout.write(t1)
    sys.stdout.write(f"determinismo: {'IDÉNTICAS' if h1 == h2 else 'DIFIEREN'}; random importado: "
                     f"{'SÍ' if 'random' in sys.modules else 'no'}; sha256 del código: {src[:16]}…\n")
    report["determinismo"] = dict(hash_1=h1, hash_2=h2, identicas=(h1 == h2),
                                  random_importado=("random" in sys.modules))
    report["sha256_codigo"] = src
    report["python"] = sys.version.split()[0]
    os.makedirs(os.path.join(here, "artifacts"), exist_ok=True)
    with open(os.path.join(here, "artifacts", "unidad_minima_04_eleccion.json"), "w",
              encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
