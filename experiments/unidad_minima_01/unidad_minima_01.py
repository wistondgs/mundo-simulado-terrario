#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""UNIDAD-MINIMA-01 · demostración determinista de la unidad de dos letras.

Qué se afirma y se mide aquí, y nada más:

  1. Una unidad con dos letras {A, B}, que lee un bit de reacción y retiene
     (historia, letra) -> reacción, construye por sí sola una distinción que NO
     está en su observación, cuando la misma letra produce reacciones distintas.
  2. Esa distinción predice reacciones a secuencias que nunca vivió, y en
     particular a corridas más largas que cualquier corrida vivida.
  3. De su propio modelo salen palabras con efecto constante que no son letras
     (el tercer elemento, BA) y relaciones entre palabras (AB = B, AA = id).
  4. Si se lesiona la distinción, se pierde la capacidad y nada más.
  5. El test discrimina: en un mundo donde la observación ya lo dice todo, el
     control reactivo acierta igual; y en un mundo con un bit oculto INERTE la
     unidad NO inventa la distinción (no sobrefragmenta).
  6. Todo es determinista: no se importa `random` y la salida se hashea dos veces.

Lo SUMINISTRADO, declarado:
  - el alfabeto {A, B} y la lectura de un bit por paso;
  - la política de exploración: todas las palabras en orden shortlex, concatenadas
    en una sola vida continua, sin reset y sin maestro;
  - el criterio de retención: la máquina de Mealy MÁS CHICA compatible con toda la
    experiencia; ante empate, la primera en orden canónico (sesgo declarado);
  - el criterio de nombre: palabra con efecto constante sobre los estados propios.
Lo ADQUIRIDO: número de estados, transiciones, salidas, el testigo de la
distinción y las palabras.

Sin dependencias fuera de la biblioteca estándar.
"""
from __future__ import annotations

import hashlib
import io
import itertools
import json
import sys
from collections import Counter

LETTERS = ("A", "B")
LIFE_MAX_LEN = 7          # vida = todas las palabras de longitud 1..7, en orden
TEST_LENS = (8, 9)        # futuro = todas las palabras de longitud 8 y 9
CURVE_T = (2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)
N_MAX = 4                 # tope de estados en la búsqueda (los mundos tienen 2)


# ----------------------------------------------------------------------------
# Mundos: máquinas de Mealy con estado oculto. step(x, letra) -> (x', reacción)
# ----------------------------------------------------------------------------
def w_latch_edge(x, a):
    """Bit oculto x. A lo conmuta; B lo pone en 0. La reacción es 1 si el bit
    CAMBIÓ. Tras A la reacción es siempre 1 (nada dice de x). Tras B la reacción
    es x. La observación funde x=0 y x=1; sólo la historia los separa."""
    if a == "A":
        return 1 - x, 1
    return 0, x


def w_visible(x, a):
    """Misma dinámica, pero la reacción revela el bit resultante. Sin aliasing:
    el reactivo (reacción previa, letra) basta."""
    if a == "A":
        return 1 - x, 1 - x
    return 0, 0


def w_inert(x, a):
    """El bit oculto existe y se conmuta, pero NINGUNA reacción depende de él.
    Lo correcto es NO construir la distinción."""
    if a == "A":
        return 1 - x, 1
    return 0, 0


WORLDS = (
    ("latch-edge (aliasado)", w_latch_edge, "la distinción hace falta y no está en la observación"),
    ("visible (control)", w_visible, "la observación ya lo dice; el reactivo debe acertar"),
    ("bit inerte (control)", w_inert, "la distinción no hace falta; no debe inventarse"),
)


def shortlex(lengths):
    seq = []
    for n in lengths:
        for w in itertools.product(LETTERS, repeat=n):
            seq.extend(w)
    return seq


def run_world(step, x0, actions):
    x, outs = x0, []
    for a in actions:
        x, o = step(x, a)
        outs.append(o)
    return outs, x


def longest_run(actions, letter):
    best = cur = 0
    for a in actions:
        cur = cur + 1 if a == letter else 0
        best = max(best, cur)
    return best


# ----------------------------------------------------------------------------
# La unidad: la máquina de Mealy más chica compatible con toda la experiencia.
# Búsqueda exacta con los estados numerados por orden de aparición (canónica).
# Sin maestro, sin reset, sin probabilidad.
# ----------------------------------------------------------------------------
def minimal_mealy(trace, n_max=N_MAX, count_cap=2):
    """trace: lista de (letra, reacción). Devuelve (n, maquina, n_soluciones_tope).
    maquina: dict (q, letra) -> (q', reacción). n_soluciones_tope ∈ {1, 2}: 2
    significa «al menos dos máquinas mínimas distintas explican lo vivido»."""
    T = len(trace)
    sys.setrecursionlimit(max(10000, 4 * T + 100))
    for n in range(1, n_max + 1):
        sols = []

        def search(i, q, trans, used):
            if len(sols) >= count_cap:
                return
            if i == T:
                sols.append(dict(trans))
                return
            a, o = trace[i]
            key = (q, a)
            if key in trans:
                q2, o2 = trans[key]
                if o2 == o:
                    search(i + 1, q2, trans, used)
                return
            for q2 in range(min(used + 1, n)):
                trans[key] = (q2, o)
                search(i + 1, q2, trans, max(used, q2 + 1))
                del trans[key]
                if len(sols) >= count_cap:
                    return

        search(0, 0, {}, 1)
        if sols:
            return n, sols[0], len(sols)
    return None


def states_of(machine):
    qs = {0}
    for (q, _), (q2, _) in machine.items():
        qs.add(q)
        qs.add(q2)
    return sorted(qs)


def track(machine, q, actions):
    """Sigue la máquina a lo largo de acciones (sin aprender). Sin ruta: se queda."""
    for a in actions:
        t = machine.get((q, a))
        if t is not None:
            q = t[0]
    return q


def predict(machine, q, actions, truth):
    """Predice la reacción de cada acción. Devuelve (aciertos, sin_ruta,
    veces_que_la_distincion_decidio)."""
    qs = states_of(machine)
    hits = no_route = decided = 0
    for a, o in zip(actions, truth):
        outs = {machine[(s, a)][1] for s in qs if (s, a) in machine}
        if len(outs) > 1:
            decided += 1
        t = machine.get((q, a))
        if t is None:
            pred = 0
            no_route += 1
        else:
            pred, q = t[1], t[0]
        hits += int(pred == o)
    return hits, no_route, decided


def majority(counter):
    if not counter:
        return 0
    best = max(counter.values())
    return min(k for k, v in counter.items() if v == best)   # empate -> 0


def reactive_table(trace, o_first=0):
    tbl = {}
    prev = o_first
    for a, o in trace:
        tbl.setdefault((prev, a), Counter())[o] += 1
        prev = o
    return tbl


def reactive_predict(tbl, prev, actions, truth):
    hits = 0
    for a, o in zip(actions, truth):
        hits += int(majority(tbl.get((prev, a), Counter())) == o)
        prev = o
    return hits


def letter_only_table(trace):
    tbl = {}
    for a, o in trace:
        tbl.setdefault(a, Counter())[o] += 1
    return tbl


def letter_only_predict(tbl, actions, truth):
    return sum(int(majority(tbl.get(a, Counter())) == o) for a, o in zip(actions, truth))


def lesion(machine):
    """Quita la distinción y nada más: colapsa los estados en uno; por letra,
    conserva la reacción mayoritaria entre los estados (empate -> 0)."""
    qs = states_of(machine)
    out = {}
    for a in LETTERS:
        c = Counter(machine[(q, a)][1] for q in qs if (q, a) in machine)
        if c:
            out[(0, a)] = (0, majority(c))
    return out


# ----------------------------------------------------------------------------
# Palabras: qué hace cada palabra sobre los estados propios (el monoide).
# ----------------------------------------------------------------------------
def word_map(step_or_machine, qs, word, is_machine):
    res = []
    for q in qs:
        for a in word:
            if is_machine:
                t = step_or_machine.get((q, a))
                if t is None:
                    return None
                q = t[0]
            else:
                q, _ = step_or_machine(q, a)
        res.append(q)
    return tuple(res)


def monoid(step_or_machine, qs, is_machine, max_len=3):
    """Devuelve {mapa: [palabras que lo realizan]} para palabras de longitud <= max_len."""
    table = {}
    for n in range(0, max_len + 1):
        for w in itertools.product(LETTERS, repeat=n):
            m = word_map(step_or_machine, qs, w, is_machine)
            if m is None:
                continue
            table.setdefault(m, []).append("".join(w) or "ε")
    return table


def classify(m, qs):
    if len(set(m)) == 1:
        return "escribe"
    if set(m) == set(qs):
        return "identidad" if tuple(m) == tuple(qs) else "permuta"
    return "otra"


def word_partition(table):
    """Qué palabras son iguales entre sí, sin mirar etiquetas de estado."""
    return sorted(sorted(ws) for ws in table.values())


def apartness_witness(machine, qs, max_len=4):
    """Palabra más corta cuya secuencia de reacciones difiere entre dos estados."""
    if len(qs) < 2:
        return None
    for n in range(1, max_len + 1):
        for w in itertools.product(LETTERS, repeat=n):
            seqs = set()
            for q in qs:
                outs = []
                for a in w:
                    t = machine.get((q, a))
                    if t is None:
                        outs = None
                        break
                    outs.append(t[1])
                    q = t[0]
                seqs.add(tuple(outs) if outs is not None else None)
            if None not in seqs and len(seqs) > 1:
                return "".join(w)
    return None


# ----------------------------------------------------------------------------
# Campaña
# ----------------------------------------------------------------------------
def campaign(out):
    report = {"mundos": {}}
    life_actions = shortlex(range(1, LIFE_MAX_LEN + 1))
    test_actions = shortlex(TEST_LENS)
    max_run = longest_run(life_actions, "A")
    probe_ks = (max_run + 1, max_run + 2)

    out.write(f"vida: {len(life_actions)} pasos (palabras de 1..{LIFE_MAX_LEN}); "
              f"futuro de prueba: {len(test_actions)} pasos (palabras de {TEST_LENS[0]} y {TEST_LENS[1]}); "
              f"corrida máxima de A vivida: {max_run}\n\n")

    for name, step, expectation in WORLDS:
        out.write(f"=== {name} · {expectation}\n")
        life_out, x_end = run_world(step, 0, life_actions)
        trace = list(zip(life_actions, life_out))
        test_out, _ = run_world(step, x_end, test_actions)
        R = {"esperado": expectation}

        # --- curva de adquisición: aprende hasta T, vive el resto sin aprender, se prueba en el futuro
        out.write(f"{'T':>5} {'estados':>7} {'únicamáq':>8} {'unidad':>7} {'reactivo':>8} {'sólo-letra':>10} {'lesión':>7}\n")
        curve = []
        for T in list(CURVE_T) + [len(trace)]:
            if T > len(trace):
                continue
            n, M, nsol = minimal_mealy(trace[:T])
            q_end = track(M, 0, life_actions)
            hits, nr, dec = predict(M, q_end, test_actions, test_out)
            rt = reactive_table(trace[:T])
            rh = reactive_predict(rt, life_out[-1], test_actions, test_out)
            lt = letter_only_table(trace[:T])
            lh = letter_only_predict(lt, test_actions, test_out)
            Lm = lesion(M)
            lesh, _, _ = predict(Lm, 0, test_actions, test_out)
            N = len(test_actions)
            row = dict(T=T, estados=n, unica=(nsol == 1), unidad=hits / N, reactivo=rh / N,
                       solo_letra=lh / N, lesion=lesh / N, sin_ruta=nr, decidio=dec)
            curve.append(row)
            out.write(f"{T:>5} {n:>7} {'sí' if nsol == 1 else 'no':>8} {hits / N:>7.4f} {rh / N:>8.4f} "
                      f"{lh / N:>10.4f} {lesh / N:>7.4f}\n")
        R["curva"] = curve

        # --- máquina final
        n, M, nsol = minimal_mealy(trace)
        qs = states_of(M)
        R["estados"] = n
        R["maquina"] = {f"{q},{a}": list(v) for (q, a), v in sorted(M.items())}
        R["testigo"] = apartness_witness(M, qs)
        out.write(f"máquina final: {n} estado(s); testigo de la distinción: {R['testigo']}\n")

        # --- sonda: corridas de A más largas que cualquiera vivida, seguidas de B
        q_end = track(M, 0, life_actions)
        probes = []
        for k in probe_ks:
            acts = ["A"] * k + ["B"]
            truth, _ = run_world(step, x_end, acts)
            h, nr, _ = predict(M, q_end, acts, truth)
            rt = reactive_table(trace)
            rh = reactive_predict(rt, life_out[-1], acts, truth)
            probes.append(dict(k=k, verdad_B=truth[-1], unidad_acierta_B=(h == len(acts)),
                               reactivo_acierta_todo=(rh == len(acts))))
            out.write(f"sonda A^{k}B (nunca vivida): B real={truth[-1]}  unidad {'acierta' if h == len(acts) else 'FALLA'}  "
                      f"reactivo {'acierta' if rh == len(acts) else 'FALLA'}\n")
        R["sondas"] = probes

        # --- palabras: lo que la unidad construyó frente a lo que el mundo es
        learned = monoid(M, qs, True)
        true = monoid(step, [0, 1], False)
        R["palabras_aprendidas"] = {}
        out.write("palabras (longitud ≤ 3) sobre los estados propios:\n")
        for m, ws in sorted(learned.items(), key=lambda kv: (len(kv[1][0]), kv[1][0])):
            cls = classify(m, qs)
            R["palabras_aprendidas"][ws[0]] = dict(clase=cls, iguales=ws[1:])
            out.write(f"   {ws[0]:<4} {cls:<10} = {' = '.join(ws[1:]) if len(ws) > 1 else '—'}\n")
        same = word_partition(learned) == word_partition(true)
        R["monoide_igual_al_real"] = same
        R["elementos_aprendidos"] = len(learned)
        R["elementos_reales_visibles"] = len(true)
        out.write(f"elementos distintos: aprendidos {len(learned)}, del mundo {len(true)}; "
                  f"partición de palabras {'IGUAL' if same else 'DISTINTA'} a la del mundo\n\n")
        report["mundos"][name] = R
    return report


def main():
    buf = io.StringIO()
    report = campaign(buf)
    text = buf.getvalue()
    return text, report


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    text1, report = main()
    text2, _ = main()
    h1 = hashlib.sha256(text1.encode()).hexdigest()
    h2 = hashlib.sha256(text2.encode()).hexdigest()
    src = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    sys.stdout.write(text1)
    sys.stdout.write(f"determinismo: corrida 1 {h1[:16]}… corrida 2 {h2[:16]}… -> {'IDÉNTICAS' if h1 == h2 else 'DIFIEREN'}\n")
    sys.stdout.write(f"módulo random importado: {'SÍ' if 'random' in sys.modules else 'no'}\n")
    sys.stdout.write(f"sha256 del código: {src}\n")
    report["determinismo"] = dict(hash_1=h1, hash_2=h2, identicas=(h1 == h2), random_importado=("random" in sys.modules))
    report["sha256_codigo"] = src
    report["python"] = sys.version.split()[0]
    os.makedirs(os.path.join(here, "artifacts"), exist_ok=True)
    with open(os.path.join(here, "artifacts", "unidad_minima_01.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=1)
