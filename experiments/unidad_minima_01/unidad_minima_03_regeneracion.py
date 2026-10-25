#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UNIDAD-MINIMA-03 · regeneración tras lesión: qué paga la experiencia retenida.

Completa el test de lesión de 01, que quitaba la distinción y medía la pérdida,
pero no medía la VUELTA. Aquí se destruye la hipótesis de una unidad que ya
predecía sin error y se la deja seguir viviendo la misma vida que iba a vivir.

La pregunta tiene dos monedas y el experimento las separa: pasos de VIDA NUEVA
frente a pasos de REPASO sobre lo retenido. Cuatro brazos:

  sham                 se contabiliza la lesión y no se borra nada (control de
                       que la medida discrimina: debe dar 0 en todo).
  con_traza_y_repaso   se borra la hipótesis y la unidad RELEE su vida retenida
                       con el mecanismo congelado de 02. Ninguna línea nueva de
                       reparación: se la hace pasar por la vía que ya tenía.
  con_traza_sin_repaso se borra la hipótesis, se conserva la vida retenida y NO
                       se relee: que la refutación conduzca la reparación.
  sin_traza            se borra la hipótesis Y la vida retenida: regenerar
                       viviendo, desde cero, a mitad de la vida.

El control reactivo sólo admite el brazo `sin_traza`, y eso no es una omisión:
su tabla (reacción previa, letra) ES a la vez su hipótesis y su experiencia, así
que no tiene traza que conservar aparte. La separación entre lo que se cree y lo
que se ha vivido es justamente lo que la unidad tiene y el reactivo no.

Lo SUMINISTRADO: la lesión, qué se borra en cada brazo, los momentos de lesión,
y el orden shortlex de la vida heredado de 01 sin cambio.
Lo ADQUIRIDO: la máquina recuperada, los pasos de vida nueva que costó, los
repasos, las refutaciones, y si la máquina recuperada es la de antes.

Predicciones escritas antes de correr: APERTURA_REGENERACION_TRAS_LESION.md §4.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from unidad_minima_01 import (  # noqa: E402
    LIFE_MAX_LEN, TEST_LENS, WORLDS, majority, predict, run_world, shortlex,
)
from unidad_minima_02_incremental import Unidad  # noqa: E402

T_LES = (64, 128, 256, 512, 1024)
BRAZOS = ("sham", "con_traza_y_repaso", "con_traza_sin_repaso", "sin_traza",
          "con_traza_que_se_relee")
TOPE_VIDA_NUEVA = 60          # declarado en la ficha §4: el brazo sin traza no debe pasar de aquí


class UnidadQueSeRelee(Unidad):
    """La reparación única del ítem, declarada en la ficha antes de correrla.

    El disparador es INTERNO y la unidad puede ejecutarlo con lo que ya tiene: al ir a
    predecir, si su hipótesis está vacía y su memoria no, se relee antes de responder.
    No es un detector de daño —un organismo no recibe ese aviso—, es notar que no tiene
    modelo y sí tiene recuerdos. La relectura usa el mecanismo congelado de 02, sin una
    línea de reparación nueva.
    """

    def _releerse(self):
        traza = list(self.trace)
        self.trace, self.trans, self.choices, self.q, self.n, self.used = [], {}, [], 0, 1, 1
        for a, o in traza:
            Unidad.leer(self, a, o)
        self.c["autorelecturas"] += 1
        self.c["pasos_releidos"] += len(traza)

    def predecir(self, a):
        if not self.trans and self.trace:
            self._releerse()
        return Unidad.predecir(self, a)


def vivir(u, step, x, actions, react, prev_o):
    """Vive `actions` paso a paso: predecir ANTES de actuar, leer después.

    Devuelve el estado del mundo y, por separado, lo que erró la unidad y lo que
    erró el reactivo, con el paso (relativo a este tramo) del último error.
    """
    err_u = err_r = sin_ruta = 0
    last_u = last_r = 0
    for k, a in enumerate(actions, start=1):
        p = u.predecir(a)
        if p is None:
            sin_ruta += 1
            p = 0
        pr = majority(react.get((prev_o, a), Counter()))
        x, o = step(x, a)
        if p != o:
            err_u += 1
            last_u = k
        if pr != o:
            err_r += 1
            last_r = k
        u.leer(a, o)
        react.setdefault((prev_o, a), Counter())[o] += 1
        prev_o = o
    return dict(x=x, prev_o=prev_o, err_unidad=err_u, err_reactivo=err_r,
                ultimo_error_unidad=last_u, ultimo_error_reactivo=last_r, sin_ruta=sin_ruta)


def lesionar(u, react, brazo):
    """Destruye la hipótesis. NO reconstruye: la reconstrucción, si la hay, la
    hace la vía de reparación que la unidad ya traía de 02."""
    coste = dict(releidos=0, refutaciones_repaso=0, repasados_repaso=0)
    if brazo == "sham":
        return u, coste
    if brazo == "con_traza_y_repaso":
        traza = list(u.trace)
        nueva = Unidad()
        for a, o in traza:
            nueva.leer(a, o)          # mecanismo congelado de 02, sin una línea nueva
        coste.update(releidos=len(traza), refutaciones_repaso=nueva.c["refutaciones"],
                     repasados_repaso=nueva.c["pasos_repasados"])
        return nueva, coste
    u.trans, u.choices, u.q, u.n, u.used = {}, [], 0, 1, 1
    if brazo == "sin_traza":
        u.trace = []
        react.clear()                 # el reactivo no tiene traza aparte: su tabla es todo
    return u, coste


def un_caso(step, t_les, brazo, life, test_actions):
    pre, post = life[:t_les], life[t_les:]
    clase = UnidadQueSeRelee if brazo == "con_traza_que_se_relee" else Unidad
    u, x, react, prev_o = clase(), 0, {}, 0

    antes = vivir(u, step, x, pre, react, prev_o)
    maquina_previa, n_previo = dict(u.trans), u.n
    c_previo = Counter(u.c)

    u, coste = lesionar(u, react, brazo)
    c_tras_lesion = Counter(u.c)

    despues = vivir(u, step, antes["x"], post, react, antes["prev_o"])
    delta = Counter(u.c) - c_tras_lesion

    test_out, _ = run_world(step, despues["x"], test_actions)
    hits, nr, dec = predict(u.trans, u.q, test_actions, test_out)
    N = len(test_actions)
    return dict(
        brazo=brazo, t_lesion=t_les,
        vida_nueva_hasta_sin_error=despues["ultimo_error_unidad"],
        errores_vida_nueva=despues["err_unidad"],
        reactivo_vida_nueva_hasta_sin_error=despues["ultimo_error_reactivo"],
        errores_reactivo_vida_nueva=despues["err_reactivo"],
        releidos=coste["releidos"], refutaciones_repaso=coste["refutaciones_repaso"],
        repasados_repaso=coste["repasados_repaso"],
        refutaciones_post=delta["refutaciones"], distinciones_post=delta["distinciones_abiertas"],
        repasados_post=delta["pasos_repasados"],
        autorelecturas=delta["autorelecturas"], releidos_por_si_mismo=delta["pasos_releidos"],
        estados_previos=n_previo, estados_finales=u.n,
        maquina_recuperada_igual=(dict(u.trans) == maquina_previa and u.n == n_previo),
        futuro=hits / N, futuro_sin_ruta=nr, futuro_decidio=dec,
        errores_antes_de_la_lesion=antes["err_unidad"],
        ultimo_error_antes=antes["ultimo_error_unidad"],
        refutaciones_antes=c_previo["refutaciones"],
    )


def campaign(out):
    life = shortlex(range(1, LIFE_MAX_LEN + 1))
    test_actions = shortlex(TEST_LENS)
    out.write(f"vida: {len(life)} pasos; futuro: {len(test_actions)} pasos; "
              f"lesiones en t = {', '.join(map(str, T_LES))}\n")
    out.write("vida nueva = pasos vividos tras la lesión hasta el último error (0 = no erró nunca más)\n\n")
    report = {"mundos": {}, "t_lesion": list(T_LES), "brazos": list(BRAZOS)}

    for name, step, _ in WORLDS:
        out.write(f"=== {name}\n")
        out.write(f"{'brazo':<21}{'t':>6}{'vida nueva':>11}{'err.vida':>9}{'releídos':>9}"
                  f"{'refut.':>7}{'repasos':>8}{'autorel.':>9}{'estados':>8}{'máq.igual':>10}{'futuro':>8}{'react.vn':>9}\n")
        filas = []
        for brazo in BRAZOS:
            for t_les in T_LES:
                r = un_caso(step, t_les, brazo, life, test_actions)
                filas.append(r)
                out.write(f"{brazo:<21}{t_les:>6}{r['vida_nueva_hasta_sin_error']:>11}"
                          f"{r['errores_vida_nueva']:>9}{r['releidos'] + r['releidos_por_si_mismo']:>9}{r['refutaciones_post']:>7}"
                          f"{r['repasados_post']:>8}{r['autorelecturas']:>9}{r['estados_finales']:>8}"
                          f"{'sí' if r['maquina_recuperada_igual'] else 'NO':>10}"
                          f"{r['futuro']:>8.4f}{r['reactivo_vida_nueva_hasta_sin_error']:>9}\n")
            out.write("\n")
        report["mundos"][name] = filas
    return report


def veredicto(report, out):
    """La puerta de la ficha §11, evaluada sobre los números, no a ojo."""
    alias = report["mundos"]["latch-edge (aliasado)"]
    g = {}
    g["sham en 0"] = all(r["vida_nueva_hasta_sin_error"] == 0 and r["errores_vida_nueva"] == 0
                         for r in alias if r["brazo"] == "sham")
    g["con traza y repaso: 0 pasos de vida nueva"] = all(
        r["vida_nueva_hasta_sin_error"] == 0 for r in alias if r["brazo"] == "con_traza_y_repaso")
    sin_t = [r for r in alias if r["brazo"] == "sin_traza"]
    g[f"sin traza: >0 y <= {TOPE_VIDA_NUEVA} pasos"] = all(
        0 < r["vida_nueva_hasta_sin_error"] <= TOPE_VIDA_NUEVA for r in sin_t)
    con_t = [r for r in alias if r["brazo"] == "con_traza_sin_repaso"]
    g["con traza sin repaso < sin traza (por momento)"] = all(
        a["vida_nueva_hasta_sin_error"] < b["vida_nueva_hasta_sin_error"]
        for a, b in zip(con_t, sin_t))
    g["máquina recuperada = la previa, en todo brazo con traza"] = all(
        r["maquina_recuperada_igual"] for r in alias
        if r["brazo"] in ("sham", "con_traza_y_repaso", "con_traza_sin_repaso"))
    g["futuro de vuelta en 1,0000 en todo brazo"] = all(r["futuro"] == 1.0 for r in alias)
    g["sham distinto de la lesión real (la lesión lesiona)"] = any(
        r["errores_vida_nueva"] > 0 for r in alias if r["brazo"] != "sham")
    act = sum(r["refutaciones_post"] + r["refutaciones_repaso"] for r in alias if r["brazo"] != "sham")
    g["contador de actividad de la vía de reparación > 0"] = act > 0
    falsador = any(
        a["vida_nueva_hasta_sin_error"] >= b["vida_nueva_hasta_sin_error"]
        for a, b in zip(con_t, sin_t))
    # Enmienda prospectiva del 2026-10-25, hallada en el paso de mutantes y ANTES de
    # correr lo real: la ficha §7 decía que en el bit inerte «la lesión no puede
    # costar nada». Es falso y el mutante 2 lo mostró: con un solo estado, borrar la
    # traza obliga a reaprender qué reacciona cada letra, y eso cuesta algún paso. Lo
    # que el mundo inerte controla no es el coste, es que no se invente la distinción.
    inerte = report["mundos"]["bit inerte (control)"]
    g["bit inerte: no se reabre ninguna distinción (1 estado)"] = all(
        r["estados_finales"] == 1 for r in inerte)
    g["bit inerte: con traza 0 pasos; sin traza <= 2"] = all(
        (r["vida_nueva_hasta_sin_error"] == 0 if r["brazo"] != "sin_traza"
         else r["vida_nueva_hasta_sin_error"] <= 2) for r in inerte)

    out.write("--- puerta de la ficha §11, sobre el mundo aliasado\n")
    for k, v in g.items():
        out.write(f"  [{'PASS' if v else 'FAIL'}] {k}\n")
    out.write(f"  [{'SE CUMPLE' if falsador else 'no'}] falsador §5: lo retenido no abarata la vida\n")
    todo = all(g.values()) and not falsador
    out.write(f"VEREDICTO DE LA HIPÓTESIS ORIGINAL: {'PASS' if todo else 'FAIL'} · "
              f"actividad de reparación: {act} refutaciones\n\n")

    # --- la reparación única, con su propia puerta y su propio falsador
    relee = [r for r in alias if r["brazo"] == "con_traza_que_se_relee"]
    rg = {}
    rg["0 pasos de vida nueva"] = all(r["vida_nueva_hasta_sin_error"] == 0 for r in relee)
    rg["máquina recuperada = la previa"] = all(r["maquina_recuperada_igual"] for r in relee)
    rg["el coste se paga en releídos (> 0)"] = all(r["releidos_por_si_mismo"] > 0 for r in relee)
    rg["el disparador interno se ejecutó"] = all(r["autorelecturas"] > 0 for r in relee)
    rg["futuro de vuelta en 1,0000"] = all(r["futuro"] == 1.0 for r in relee)
    f_rep = any(a["vida_nueva_hasta_sin_error"] >= b["vida_nueva_hasta_sin_error"]
                for a, b in zip(relee, sin_t))
    out.write("--- puerta de la reparación única (disparador interno de relectura)\n")
    for k, v in rg.items():
        out.write(f"  [{'PASS' if v else 'FAIL'}] {k}\n")
    out.write(f"  [{'SE CUMPLE' if f_rep else 'no'}] falsador de la reparación: sigue empatando con el brazo sin traza\n")
    rep_ok = all(rg.values()) and not f_rep
    out.write(f"VEREDICTO DE LA REPARACIÓN: {'PASS' if rep_ok else 'FAIL'}\n")
    return dict(criterios=g, falsador_se_cumple=falsador,
                veredicto_hipotesis_original="PASS" if todo else "FAIL",
                reparacion=dict(criterios=rg, falsador_se_cumple=f_rep,
                                veredicto="PASS" if rep_ok else "FAIL"),
                actividad_reparacion=act)


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
    with open(os.path.join(here, "artifacts", "unidad_minima_03_regeneracion.json"), "w",
              encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
