#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PRIMITIVO - N=2 - instrumento exhaustivo de referencia (v0.1, 2026-09-22)

Estado epistemico de TODO lo que produce este script: REPORTED.
Pasa a VERIFIED solo si una implementacion independiente, escrita desde una
especificacion y sin ver este codigo, produce los mismos valores deterministicos.

Uso:     python3 primitivo_n2.py [directorio_salida]
Salidas: por_sistema.jsonl  (256 lineas, una por dinamica; para localizar discrepancias)
         resumen.json       (agregados; seccion 'deterministico' + seccion 'montecarlo')
Solo biblioteca estandar. Todo es deterministico salvo el bloque Monte Carlo (semilla fija).

CONVENCIONES. Son elecciones del instrumento, no hechos: cambiarlas cambia resultados.
  C1  Estado s en {0,1,2,3}, s = 2*x1 + x2.
  C2  Dinamica F = (F[0],F[1],F[2],F[3]), F[s] en {0..3}: 4^4 = 256 dinamicas.
      Enumerar F equivale a actualizacion SINCRONICA de las reglas locales.
  C3  Particiones binarias del estado: P1(s)=x1, P2(s)=x2, P3(s)=x1 XOR x2.
      Cortes = pares de particiones: C12 (el corte dado), C13, C23.
  C4  Perturbacion en un corte (Pa,Pb): cambiar la etiqueta de una particion
      manteniendo la otra; se implementa como mascara XOR unica (calculada, no escrita a mano).
  C5  Dependencia estructural en un corte: la etiqueta i de F depende de la etiqueta j
      si existe s tal que F(s) y F(s XOR mascara_j) difieren en la etiqueta i.
      Se evalua sobre los 4 estados (no solo sobre el regimen de atractores).
      Categoria cruzada: separable (ninguna dependencia cruzada), unidir (una), mutua (ambas).
  C6  Atractor: ciclo alcanzado iterando F, identificado por el CONJUNTO de sus estados.
  C7  Robustez de F en un corte: fraccion exacta de pares (estado de un atractor A,
      perturbacion del corte) cuyo trayecto vuelve al MISMO atractor A.
  C8  Scheduler (sobre las reglas locales de C12): 'sinc' = F; 'sec12' = actualiza x1 y
      luego x2 usando el x1 nuevo; 'sec21' = al reves. 'atractores_distintos' = el conjunto
      de atractores de sinc difiere del de sec12 o del de sec21. 'ciclo_muere_sin_reloj' =
      algun ciclo sincronico de periodo >= 2 no aparece ni en sec12 ni en sec21.
  C9  Lesion de la variable i (en C12): 'congelar' = x_i siguiente = x_i actual;
      'fijar0' = x_i siguiente = 0. Veredicto = la union de estados de atractor cambia
      respecto del sistema intacto.
  C10 Tipos: orbitas por conjugacion p.F.p^-1 bajo S4 (dinamica sin corte) y bajo las
      8 simetrias del corte C12 (permutar x1,x2 y negar cada una). Se reporta el
      representante minimo lexicografico.
  C11 Vocabularios V (particiones de las 256 dinamicas) contra consecuencia K
      = (periodos ordenados, robustez en C12), con peso uniforme. I(V;K) en bits.
      Linea base EXACTA: informacion mutua esperada bajo permutacion aleatoria con
      marginales fijos (modelo hipergeometrico, la misma de la AMI). Debe coincidir exacto.
      Linea base Monte Carlo: permutar etiquetas de V; coincide solo dentro del error MC.
"""
import hashlib
import itertools
import json
import math
import os
import random
import sys
from collections import Counter
from fractions import Fraction

SEED, R_MC = 20260922, 10000
STATES = range(4)


def x1(s): return s >> 1
def x2(s): return s & 1
def st(a, b): return (a << 1) | b


PART = {'P1': x1, 'P2': x2, 'P3': lambda s: x1(s) ^ x2(s)}
CUTS = {'C12': ('P1', 'P2'), 'C13': ('P1', 'P3'), 'C23': ('P2', 'P3')}


def mask(change, keep):
    """Mascara XOR que cambia la particion 'change' y conserva 'keep' en todo estado."""
    ms = [m for m in (1, 2, 3)
          if all(PART[change](s ^ m) != PART[change](s) and PART[keep](s ^ m) == PART[keep](s)
                 for s in STATES)]
    assert len(ms) == 1
    return ms[0]


MASKS = {c: (mask(a, b), mask(b, a)) for c, (a, b) in CUTS.items()}


def deps(F, cut):
    labs = [PART[p] for p in CUTS[cut]]
    return {(i, j): any(labs[i](F[s]) != labs[i](F[s ^ MASKS[cut][j]]) for s in STATES)
            for i in range(2) for j in range(2)}


def cross_cat(d):
    a, b = d[(0, 1)], d[(1, 0)]
    return 'separable' if not (a or b) else ('mutua' if (a and b) else 'unidir')


def attractor_of(F, s):
    pos, path = {}, []
    while s not in pos:
        pos[s] = len(path)
        path.append(s)
        s = F[s]
    return frozenset(path[pos[s]:])


def attractors(F): return {attractor_of(F, s) for s in STATES}
def attr_list(F): return sorted(sorted(A) for A in attractors(F))
def attr_union(F): return frozenset().union(*attractors(F))


def robustness(F, cut):
    ok = tot = 0
    for A in attractors(F):
        for s in A:
            for m in MASKS[cut]:
                tot += 1
                ok += attractor_of(F, s ^ m) == A
    return Fraction(ok, tot)


def conj(F, p):
    inv = [0] * 4
    for i, v in enumerate(p):
        inv[v] = i
    return tuple(p[F[inv[t]]] for t in STATES)


S4 = list(itertools.permutations(STATES))
SYM_C12 = sorted({tuple(st(*((lambda a, b: (b ^ n1, a ^ n2) if sw else (a ^ n1, b ^ n2))(x1(s), x2(s))))
                        for s in STATES)
                  for sw in (0, 1) for n1 in (0, 1) for n2 in (0, 1)})
assert len(SYM_C12) == 8


def canon(F, group): return min(conj(F, p) for p in group)


def sequential(F, order):
    f1 = [x1(F[s]) for s in STATES]
    f2 = [x2(F[s]) for s in STATES]
    G = []
    for s in STATES:
        a, b = x1(s), x2(s)
        if order == '12':
            a = f1[st(a, b)]
            b = f2[st(a, b)]
        else:
            b = f2[st(a, b)]
            a = f1[st(a, b)]
        G.append(st(a, b))
    return tuple(G)


def lesion(F, i, mode):
    G = []
    for s in STATES:
        a, b = x1(F[s]), x2(F[s])
        if i == 0:
            a = x1(s) if mode == 'congelar' else 0
        else:
            b = x2(s) if mode == 'congelar' else 0
        G.append(st(a, b))
    return tuple(G)


def entropy(u):
    n = len(u)
    return -sum(k / n * math.log2(k / n) for k in Counter(u).values())


def mutual_info(u, v):
    n, cu, cv = len(u), Counter(u), Counter(v)
    return sum(k / n * math.log2(k * n / (cu[a] * cv[b])) for (a, b), k in Counter(zip(u, v)).items())


def expected_mi(u, v):
    n, lg, tot = len(u), math.lgamma, 0.0
    for a in Counter(u).values():
        for b in Counter(v).values():
            for k in range(max(1, a + b - n), min(a, b) + 1):
                logp = (lg(a + 1) + lg(b + 1) + lg(n - a + 1) + lg(n - b + 1) - lg(n + 1)
                        - lg(k + 1) - lg(a - k + 1) - lg(b - k + 1) - lg(n - a - b + k + 1))
                tot += k / n * math.log2(n * k / (a * b)) * math.exp(logp)
    return tot


def main(out):
    os.makedirs(out, exist_ok=True)
    maps = list(itertools.product(range(4), repeat=4))
    rows = []
    for F in maps:
        d = {c: deps(F, c) for c in CUTS}
        A_s, A_12, A_21 = attractors(F), attractors(sequential(F, '12')), attractors(sequential(F, '21'))
        cycles = [A for A in A_s if len(A) > 1]
        rows.append({
            'F': list(F),
            'tipo_S4': list(canon(F, S4)),
            'tipo_C12': list(canon(F, SYM_C12)),
            'dependencias': {c: {'grafo': [d[c][k] for k in sorted(d[c])], 'cruzada': cross_cat(d[c])}
                             for c in CUTS},
            'atractores': attr_list(F),
            'periodos': sorted(len(A) for A in A_s),
            'robustez': {c: str(robustness(F, c)) for c in CUTS},
            'scheduler': {'sinc': attr_list(F), 'sec12': attr_list(sequential(F, '12')),
                          'sec21': attr_list(sequential(F, '21')),
                          'atractores_distintos': A_s != A_12 or A_s != A_21,
                          'ciclo_muere_sin_reloj': any(A not in A_12 and A not in A_21 for A in cycles)},
            'lesion': {v: {m: attr_union(lesion(F, i, m)) != attr_union(F) for m in ('congelar', 'fijar0')}
                       for i, v in enumerate(('x1', 'x2'))},
        })

    lines = [json.dumps(r, sort_keys=True, separators=(',', ':')) for r in rows]
    with open(os.path.join(out, 'por_sistema.jsonl'), 'w') as fh:
        fh.write('\n'.join(lines) + '\n')

    cats = lambda r: [r['dependencias'][c]['cruzada'] for c in CUTS]
    with_cycle = [r for r in rows if any(p > 1 for p in r['periodos'])]
    det = {
        'n_dinamicas': len(rows),
        'tipos_S4': len({tuple(r['tipo_S4']) for r in rows}),
        'tipos_C12': len({tuple(r['tipo_C12']) for r in rows}),
        'cruzada_en_C12': dict(Counter(r['dependencias']['C12']['cruzada'] for r in rows)),
        'separable_en_algun_corte': sum('separable' in cats(r) for r in rows),
        'mutua_en_los_3_cortes': sum(all(c == 'mutua' for c in cats(r)) for r in rows),
        'categoria_cambia_con_el_corte': sum(len(set(cats(r))) > 1 for r in rows),
        'con_al_menos_un_atractor': sum(bool(r['atractores']) for r in rows),
        'robustez_cambia_con_el_corte': sum(len(set(r['robustez'].values())) > 1 for r in rows),
        'scheduler_puntos_fijos_distintos': sum(
            {tuple(a) for a in r['scheduler']['sinc'] if len(a) == 1} !=
            {tuple(a) for a in r['scheduler']['sec12'] if len(a) == 1} or
            {tuple(a) for a in r['scheduler']['sinc'] if len(a) == 1} !=
            {tuple(a) for a in r['scheduler']['sec21'] if len(a) == 1} for r in rows),
        'scheduler_atractores_distintos': sum(r['scheduler']['atractores_distintos'] for r in rows),
        'con_ciclo_sincronico_por_cruzada': dict(Counter(r['dependencias']['C12']['cruzada'] for r in with_cycle)),
        'ciclo_muere_sin_reloj_por_cruzada': dict(Counter(r['dependencias']['C12']['cruzada']
                                                          for r in rows if r['scheduler']['ciclo_muere_sin_reloj'])),
        'lesion_veredicto_difiere_congelar_vs_fijar0': sum(
            r['lesion'][v]['congelar'] != r['lesion'][v]['fijar0'] for r in rows for v in ('x1', 'x2')),
        'lesion_casos': 2 * len(rows),
    }

    K = [(tuple(r['periodos']), r['robustez']['C12']) for r in rows]
    vocabs = {
        'grafo_dependencias_C12': [tuple(r['dependencias']['C12']['grafo']) for r in rows],
        'cruzada_C12': [r['dependencias']['C12']['cruzada'] for r in rows],
        'tipo_S4': [tuple(r['tipo_S4']) for r in rows],
    }
    det['perfiles_consecuencia_K'] = len(set(K))
    det['perfiles_robustez_C12'] = len({k[1] for k in K})
    # Los periodos son invariantes de la dinamica sin corte (funcion del tipo S4): comparar
    # vocabularios solo contra K favorece a tipo_S4 por construccion. Por eso se separa K.
    targets = {'K': K, 'solo_robustez_C12': [k[1] for k in K], 'solo_periodos': [k[0] for k in K]}
    rng, vocab_det, vocab_mc = random.Random(SEED), {}, {}
    for name, V in vocabs.items():
        classes = {}
        for lab, k in zip(V, K):
            classes.setdefault(lab, set()).add(k)
        I = mutual_info(V, K)
        HV = entropy(V)
        vocab_det[name] = {
            'clases': len(classes),
            'clases_con_colision_en_K': sum(len(s) > 1 for s in classes.values()),
            'clases_con_colision_en_robustez': sum(len({k[1] for k in s}) > 1 for s in classes.values()),
            'colision_garantizada_por_conteo': len(classes) < len(set(K)),
            'H_V_bits': round(HV, 6),
        }
        for tname, T in targets.items():
            It, Et, HT = mutual_info(V, T), expected_mi(V, T), entropy(T)
            vocab_det[name][tname] = {'I_bits': round(It, 6), 'E_I_permutacion_exacta_bits': round(Et, 6),
                                      'AMI_max': round((It - Et) / (max(HV, HT) - Et), 6)}
        lab = list(V)
        null = []
        for _ in range(R_MC):
            rng.shuffle(lab)
            null.append(mutual_info(lab, K))
        mu = sum(null) / R_MC
        sd = math.sqrt(sum((x - mu) ** 2 for x in null) / (R_MC - 1))
        vocab_mc[name] = {'media_nula_bits': round(mu, 4), 'sd_nula_bits': round(sd, 4),
                          'p_valor': round((1 + sum(x >= I - 1e-12 for x in null)) / (R_MC + 1), 5)}
    det['vocabularios'] = vocab_det
    det['H_K_bits'] = round(entropy(K), 6)

    det_json = json.dumps(det, sort_keys=True, separators=(',', ':'))
    summary = {'estado': 'REPORTED', 'deterministico': det,
               'montecarlo': {'semilla': SEED, 'permutaciones': R_MC, 'vocabularios': vocab_mc},
               'sha256': {'por_sistema.jsonl': hashlib.sha256(('\n'.join(lines) + '\n').encode()).hexdigest(),
                          'deterministico': hashlib.sha256(det_json.encode()).hexdigest()}}
    with open(os.path.join(out, 'resumen.json'), 'w') as fh:
        json.dump(summary, fh, sort_keys=True, indent=2, ensure_ascii=False)
    print(json.dumps(summary, sort_keys=True, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'salida_n2')
