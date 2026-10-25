#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UNIDAD-MINIMA-02 · la misma unidad, pero viviendo: paso a paso, desde adentro.

Cierra el hueco declarado en 01: allí la máquina mínima se recomputaba de cero
sobre toda la experiencia. Aquí la unidad lleva UNA hipótesis y, en cada paso,
(1) predice la reacción antes de actuar, (2) actúa y lee, (3) si la hipótesis
explica lo leído, avanza; si la refuta, retrocede a su última decisión y toma la
siguiente, repasando sólo lo vivido desde esa decisión; (4) si ninguna decisión
queda, abre una distinción nueva (un estado más) y relee su vida con ella.

Es el mismo orden canónico que en 01, así que la máquina final debe coincidir con
la de 01 (se comprueba). Lo que cambia es que ahora el proceso es el del organismo:
hipótesis conservada, refutación por experiencia, corrección mínima, nueva
distinción sólo cuando hace falta. Sin maestro, sin reset, sin probabilidad.

Lo SUMINISTRADO: lo mismo que en 01 más el orden de las decisiones (primero el
estado 0, luego el 1, …; estado nuevo sólo cuando los existentes fallan).
Lo ADQUIRIDO: la hipótesis, cuándo se refutó, cuántas veces, cuándo dejó de
errar, y cuánto le costó cada corrección (pasos repasados).
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
    LETTERS, LIFE_MAX_LEN, TEST_LENS, WORLDS, apartness_witness, classify, lesion,
    letter_only_predict, letter_only_table, longest_run, majority, minimal_mealy,
    monoid, predict, reactive_predict, run_world, shortlex, states_of, track,
    word_partition,
)


class Unidad:
    """Hipótesis + experiencia retenida + pila de decisiones."""

    def __init__(self, n_max=4):
        self.trace = []          # experiencia retenida: (letra, reacción)
        self.n = 1               # distinciones permitidas (estados)
        self.n_max = n_max
        self.trans = {}          # hipótesis: (q, letra) -> (q', reacción)
        self.q = 0               # dónde cree estar
        self.used = 1
        self.choices = []        # [t, key, elegido, used_antes]
        self.c = Counter()

    # --- lo que la unidad hace antes de actuar
    def predecir(self, a):
        t = self.trans.get((self.q, a))
        return None if t is None else t[1]

    # --- lo que la unidad hace después de leer
    def leer(self, a, o):
        self.trace.append((a, o))
        i = len(self.trace) - 1
        while i < len(self.trace):
            a_i, o_i = self.trace[i]
            if self._avanzar(i, a_i, o_i):
                i += 1
                continue
            # refutada: retroceder a la última decisión con alternativa
            self.c["refutaciones"] += 1
            while True:
                if not self.choices:
                    # nada que corregir: hace falta una distinción nueva
                    self.n += 1
                    self.c["distinciones_abiertas"] += 1
                    if self.n > self.n_max:
                        raise RuntimeError("tope de estados")
                    self.trans, self.used, self.q = {}, 1, 0
                    i = 0
                    break
                cp = self.choices[-1]
                t0, key, elegido, used_antes = cp
                del self.trans[key]
                siguiente = elegido + 1
                if siguiente < min(used_antes + 1, self.n):
                    cp[2] = siguiente
                    self.trans[key] = (siguiente, self.trace[t0][1])
                    self.used = max(used_antes, siguiente + 1)
                    self.q = siguiente
                    i = t0 + 1
                    break
                self.choices.pop()
            self.c["pasos_repasados"] += len(self.trace) - i
            self.c["repaso_max"] = max(self.c["repaso_max"], len(self.trace) - i)

    def _avanzar(self, i, a, o):
        key = (self.q, a)
        if key in self.trans:
            q2, o2 = self.trans[key]
            if o2 != o:
                return False
            self.q = q2
            return True
        # transición nueva: primera opción, y se anota la decisión
        self.choices.append([i, key, 0, self.used])
        self.trans[key] = (0, o)
        self.used = max(self.used, 1)
        self.q = 0
        return True


def campaign(out):
    report = {"mundos": {}}
    life_actions = shortlex(range(1, LIFE_MAX_LEN + 1))
    test_actions = shortlex(TEST_LENS)
    max_run = longest_run(life_actions, "A")
    N = len(test_actions)
    out.write(f"vida: {len(life_actions)} pasos; futuro: {N} pasos; corrida máxima de A vivida: {max_run}\n\n")

    for name, step, expectation in WORLDS:
        out.write(f"=== {name} · {expectation}\n")
        R = {}
        u = Unidad()
        x = 0
        react = {}
        prev_o = 0
        err_u = err_r = sin_ruta = 0
        last_err_u = last_err_r = -1
        marks = {}
        hitos = (8, 16, 32, 64, 128, 256, 512, 1024, len(life_actions))
        for t, a in enumerate(life_actions, start=1):
            # la unidad predice ANTES de actuar
            p = u.predecir(a)
            if p is None:
                sin_ruta += 1
                p = 0
            pr = majority(react.get((prev_o, a), Counter()))
            # actúa y lee
            x, o = step(x, a)
            if p != o:
                err_u += 1
                last_err_u = t
            if pr != o:
                err_r += 1
                last_err_r = t
            u.leer(a, o)
            react.setdefault((prev_o, a), Counter())[o] += 1
            prev_o = o
            if t in hitos:
                marks[t] = dict(estados=u.n, errores_unidad=err_u, errores_reactivo=err_r,
                                refutaciones=u.c["refutaciones"], repasados=u.c["pasos_repasados"])
        out.write(f"{'t':>5} {'estados':>7} {'err.unidad':>10} {'err.react':>9} {'refutac.':>8} {'repasados':>9}\n")
        for t in hitos:
            m = marks[t]
            out.write(f"{t:>5} {m['estados']:>7} {m['errores_unidad']:>10} {m['errores_reactivo']:>9} "
                      f"{m['refutaciones']:>8} {m['repasados']:>9}\n")
        R["hitos"] = marks
        R["ultimo_error_unidad"] = last_err_u
        R["ultimo_error_reactivo"] = last_err_r
        R["sin_ruta"] = sin_ruta
        R["contadores"] = dict(u.c)
        out.write(f"último error en vida: unidad t={last_err_u}, reactivo t={last_err_r}; "
                  f"predicciones sin ruta: {sin_ruta}; refutaciones: {u.c['refutaciones']}; "
                  f"distinciones abiertas: {u.c['distinciones_abiertas']}; "
                  f"pasos repasados: {u.c['pasos_repasados']} (máx. por corrección {u.c['repaso_max']})\n")

        # --- ¿coincide con la máquina mínima calculada de cero (01)?
        n01, M01, _ = minimal_mealy(u.trace)
        same = (n01 == u.n and M01 == u.trans)
        R["coincide_con_01"] = same
        out.write(f"máquina final: {u.n} estado(s); {'IGUAL' if same else 'DISTINTA'} a la de 01 recomputada de cero\n")

        # --- futuro, sonda, lesión, palabras: como en 01, sobre la hipótesis viva
        life_out = [o for _, o in u.trace]
        test_out, _ = run_world(step, x, test_actions)
        qs = states_of(u.trans)
        hits, nr, dec = predict(u.trans, u.q, test_actions, test_out)
        rh = reactive_predict(react, life_out[-1], test_actions, test_out)
        lh = letter_only_predict(letter_only_table(u.trace), test_actions, test_out)
        lesh, _, _ = predict(lesion(u.trans), 0, test_actions, test_out)
        R["futuro"] = dict(unidad=hits / N, reactivo=rh / N, solo_letra=lh / N, lesion=lesh / N,
                           sin_ruta=nr, decidio=dec)
        out.write(f"futuro ({N} pasos): unidad {hits / N:.4f}  reactivo {rh / N:.4f}  "
                  f"sólo-letra {lh / N:.4f}  lesión {lesh / N:.4f}; la distinción decidió en {dec} pasos\n")
        R["testigo"] = apartness_witness(u.trans, qs)
        probes = []
        for k in (max_run + 1, max_run + 2):
            acts = ["A"] * k + ["B"]
            truth, _ = run_world(step, x, acts)
            h, _, _ = predict(u.trans, u.q, acts, truth)
            r = reactive_predict(react, life_out[-1], acts, truth)
            probes.append(dict(k=k, verdad_B=truth[-1], unidad=(h == len(acts)), reactivo=(r == len(acts))))
            out.write(f"sonda A^{k}B: B real={truth[-1]}  unidad {'acierta' if h == len(acts) else 'FALLA'}  "
                      f"reactivo {'acierta' if r == len(acts) else 'FALLA'}\n")
        R["sondas"] = probes
        learned = monoid(u.trans, qs, True)
        true = monoid(step, [0, 1], False)
        R["palabras"] = {ws[0]: dict(clase=classify(m, qs), iguales=ws[1:]) for m, ws in learned.items()}
        R["monoide_igual_al_real"] = word_partition(learned) == word_partition(true)
        out.write("palabras: " + "; ".join(f"{ws[0]} {classify(m, qs)}" for m, ws in
                  sorted(learned.items(), key=lambda kv: (len(kv[1][0]), kv[1][0]))) +
                  f" · testigo {R['testigo']} · partición {'IGUAL' if R['monoide_igual_al_real'] else 'DISTINTA'} a la del mundo\n\n")
        report["mundos"][name] = R
    return report


def main():
    buf = io.StringIO()
    rep = campaign(buf)
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
    report["determinismo"] = dict(identicas=(h1 == h2), random_importado=("random" in sys.modules))
    report["sha256_codigo"] = src
    os.makedirs(os.path.join(here, "artifacts"), exist_ok=True)
    with open(os.path.join(here, "artifacts", "unidad_minima_02_incremental.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
