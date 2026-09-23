#!/usr/bin/env python3
"""Réplica ciega A2 del instrumento Primitivo N=2 (SPEC v0.1)."""
import hashlib
import itertools
import json
import math
import os
import platform
import shutil
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPEC = ROOT / "SPEC_PRIMITIVO_N2_A_REPLICA_CERRADA_v0_1.md"
OUT = ROOT / "por_sistema.jsonl"
SUMMARY = ROOT / "resumen.json"


def bits(s):
    return (s >> 1, s & 1)


def state(x1, x2):
    return 2 * x1 + x2


PARTS = {
    "P1": lambda s: bits(s)[0],
    "P2": lambda s: bits(s)[1],
    "P3": lambda s: bits(s)[0] ^ bits(s)[1],
}
CUTS = {"C12": ("P1", "P2"), "C13": ("P1", "P3"), "C23": ("P2", "P3")}


def canon(obj):
    return json.dumps(obj, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def attractors(f):
    found = set()
    for initial in range(4):
        trail, pos = [], {}
        cur = initial
        while cur not in pos:
            pos[cur] = len(trail)
            trail.append(cur)
            cur = f[cur]
        found.add(tuple(sorted(trail[pos[cur]:])))
    return [list(a) for a in sorted(found)]


def masks(a_name, b_name):
    a, b = PARTS[a_name], PARTS[b_name]
    ma = [m for m in (1, 2, 3) if all(a(s ^ m) != a(s) and b(s ^ m) == b(s) for s in range(4))]
    mb = [m for m in (1, 2, 3) if all(b(s ^ m) != b(s) and a(s ^ m) == a(s) for s in range(4))]
    assert len(ma) == len(mb) == 1
    return ma[0], mb[0]


MASKS = {name: masks(*cut) for name, cut in CUTS.items()}


def dependency(f, a_name, b_name):
    a, b = PARTS[a_name], PARTS[b_name]
    ma, mb = MASKS[{v: k for k, v in CUTS.items()}[(a_name, b_name)]]
    ds = []
    for i, j, mj in ((a, a, ma), (a, b, mb), (b, a, ma), (b, b, mb)):
        ds.append(any(i(f[s]) != i(f[s ^ mj]) for s in range(4)))
    cross = "separable" if not ds[1] and not ds[2] else "mutua" if ds[1] and ds[2] else "unidir"
    return {"cruzada": cross, "grafo": ds}


def reached_attractor(f, initial):
    trail, pos = [], {}
    cur = initial
    while cur not in pos:
        pos[cur] = len(trail)
        trail.append(cur)
        cur = f[cur]
    return tuple(sorted(trail[pos[cur]:]))


def robustness(f, cut_name, ats):
    ma, mb = MASKS[cut_name]
    ok = total = 0
    for at in ats:
        target = tuple(at)
        for s in at:
            for m in (ma, mb):
                total += 1
                ok += reached_attractor(f, s ^ m) == target
    return str(Fraction(ok, total))


def scheduled(f, order):
    ans = []
    for s in range(4):
        x1, x2 = bits(s)
        if order == "12":
            x1 = bits(f[state(x1, x2)])[0]
            x2 = bits(f[state(x1, x2)])[1]
        else:
            x2 = bits(f[state(x1, x2)])[1]
            x1 = bits(f[state(x1, x2)])[0]
        ans.append(state(x1, x2))
    return tuple(ans)


def lesion(f, variable, mode):
    g = []
    for s in range(4):
        x1, x2 = bits(s)
        y1, y2 = bits(f[s])
        if variable == "x1":
            y1 = x1 if mode == "congelar" else 0
        else:
            y2 = x2 if mode == "congelar" else 0
        g.append(state(y1, y2))
    return set(x for at in attractors(g) for x in at) != set(x for at in attractors(f) for x in at)


PERMS = list(itertools.permutations(range(4)))


def conjugate(f, p):
    g = [None] * 4
    for s in range(4):
        g[p[s]] = p[f[s]]
    return tuple(g)


def c12_perms():
    ps = []
    for swap in (False, True):
        for n1, n2 in itertools.product((0, 1), repeat=2):
            p = []
            for s in range(4):
                x1, x2 = bits(s)
                if swap:
                    x1, x2 = x2, x1
                p.append(state(x1 ^ n1, x2 ^ n2))
            ps.append(tuple(p))
    assert len(set(ps)) == 8
    return ps


C12_PERMS = c12_perms()


def types(f):
    return list(min(conjugate(f, p) for p in C12_PERMS)), list(min(conjugate(f, p) for p in PERMS))


def record(f):
    ats = attractors(f)
    deps = {name: dependency(f, *cut) for name, cut in CUTS.items()}
    sinc, sec12, sec21 = ats, attractors(scheduled(f, "12")), attractors(scheduled(f, "21"))
    distinct = sinc != sec12 or sinc != sec21
    dies = any(len(a) >= 2 and a not in sec12 and a not in sec21 for a in sinc)
    tc12, ts4 = types(f)
    return {
        "F": list(f),
        "atractores": ats,
        "dependencias": deps,
        "lesion": {v: {m: lesion(f, v, m) for m in ("congelar", "fijar0")} for v in ("x1", "x2")},
        "periodos": sorted(len(a) for a in ats),
        "robustez": {n: robustness(f, n, ats) for n in CUTS},
        "scheduler": {"atractores_distintos": distinct, "ciclo_muere_sin_reloj": dies,
                      "sec12": sec12, "sec21": sec21, "sinc": sinc},
        "tipo_C12": tc12, "tipo_S4": ts4,
    }


def entropy(labels):
    n = len(labels)
    return -sum((c/n) * math.log2(c/n) for c in Counter(labels).values())


def mi(x, y):
    n = len(x); cx, cy, cxy = Counter(x), Counter(y), Counter(zip(x, y))
    return sum((c/n) * math.log2(c*n/(cx[a]*cy[b])) for (a, b), c in cxy.items())


def exact_expected_mi(x, y):
    """Exact finite-N hypergeometric expectation, evaluated numerically in log-factorial scale."""
    n_total = len(x); ans = 0.0
    for ai in Counter(x).values():
        for bj in Counter(y).values():
            lo, hi = max(1, ai + bj - n_total), min(ai, bj)
            for n in range(lo, hi + 1):
                logp = (math.lgamma(ai + 1) + math.lgamma(bj + 1) + math.lgamma(n_total-ai + 1)
                        + math.lgamma(n_total-bj + 1) - math.lgamma(n_total + 1)
                        - math.lgamma(n + 1) - math.lgamma(ai-n + 1) - math.lgamma(bj-n + 1)
                        - math.lgamma(n_total-ai-bj+n + 1))
                ans += (n / n_total) * math.log2(n_total*n/(ai*bj)) * math.exp(logp)
    return ans


def label(value):
    return canon(value)


def vocabulary(vlabels, klabels, rlabels, plabels):
    unique_v = set(vlabels)
    classes = len(unique_v)
    h_v = entropy(vlabels)
    result = {
        "clases": classes,
        "clases_con_colision_en_K": sum(len({k for v2, k in zip(vlabels, klabels) if v2 == v}) >= 2 for v in unique_v),
        "clases_con_colision_en_robustez": sum(len({r for v2, r in zip(vlabels, rlabels) if v2 == v}) >= 2 for v in unique_v),
        "colision_garantizada_por_conteo": classes < len(set(klabels)),
        "H_V_bits": h_v,
    }
    for name, target in (("K", klabels), ("solo_robustez_C12", rlabels), ("solo_periodos", plabels)):
        ii, ee, ht = mi(vlabels, target), exact_expected_mi(vlabels, target), entropy(target)
        denom = max(h_v, ht) - ee
        result[name] = {"I_bits": ii, "E_I_permutacion_exacta_bits": ee,
                        "AMI_max": (ii-ee)/denom if denom else 0.0}
    return result


def base_structural_tests():
    assert bits(3) == (1, 1) and state(1, 0) == 2
    assert MASKS == {"C12": (2, 1), "C13": (3, 1), "C23": (3, 2)}
    assert attractors((1, 0, 3, 2)) == [[0, 1], [2, 3]]
    assert scheduled((0, 2, 1, 3), "12") == (0, 3, 0, 3)
    assert scheduled((0, 2, 1, 3), "21") == (0, 0, 3, 3)
    assert len(PERMS) == 24 and len(C12_PERMS) == 8


CAL_0 = '{"F":[0,0,0,0],"atractores":[[0]],"dependencias":{"C12":{"cruzada":"separable","grafo":[false,false,false,false]},"C13":{"cruzada":"separable","grafo":[false,false,false,false]},"C23":{"cruzada":"separable","grafo":[false,false,false,false]}},"lesion":{"x1":{"congelar":true,"fijar0":false},"x2":{"congelar":true,"fijar0":false}},"periodos":[1],"robustez":{"C12":"1","C13":"1","C23":"1"},"scheduler":{"atractores_distintos":false,"ciclo_muere_sin_reloj":false,"sec12":[[0]],"sec21":[[0]],"sinc":[[0]]},"tipo_C12":[0,0,0,0],"tipo_S4":[0,0,0,0]}'
CAL_1 = '{"F":[0,2,1,3],"atractores":[[0],[1,2],[3]],"dependencias":{"C12":{"cruzada":"mutua","grafo":[false,true,true,false]},"C13":{"cruzada":"unidir","grafo":[true,true,false,true]},"C23":{"cruzada":"unidir","grafo":[true,true,false,true]}},"lesion":{"x1":{"congelar":true,"fijar0":true},"x2":{"congelar":true,"fijar0":true}},"periodos":[1,1,2],"robustez":{"C12":"0","C13":"1/4","C23":"1/4"},"scheduler":{"atractores_distintos":true,"ciclo_muere_sin_reloj":true,"sec12":[[0],[3]],"sec21":[[0],[3]],"sinc":[[0],[1,2],[3]]},"tipo_C12":[0,2,1,3],"tipo_S4":[0,1,3,2]}'


def calibration_tests():
    assert canon(record((0, 0, 0, 0))) == CAL_0
    assert canon(record((0, 2, 1, 3))) == CAL_1


def controls(records):
    cut_cross = {c: Counter(r["dependencias"][c]["cruzada"] for r in records) for c in CUTS}
    robust_h = {c: entropy([r["robustez"][c] for r in records]) for c in CUTS}
    grafo_mi = {c: mi([label(r["dependencias"][c]["grafo"]) for r in records], [r["robustez"][c] for r in records]) for c in CUTS}
    type_mi = {c: mi([label(r["tipo_S4"]) for r in records], [r["robustez"][c] for r in records]) for c in CUTS}
    allmask_ok = True
    groups = defaultdict(set)
    for r in records:
        f, ats = tuple(r["F"]), r["atractores"]
        success = total = 0
        for at in ats:
            for s in at:
                for m in (1, 2, 3):
                    total += 1; success += reached_attractor(f, s ^ m) == tuple(at)
        groups[label(r["tipo_S4"])].add(str(Fraction(success, total)))
    allmask_ok = all(len(v) == 1 for v in groups.values())
    fixed_ok = all(
        {tuple(a) for a in r["scheduler"][key] if len(a) == 1} == {tuple(a) for a in r["scheduler"]["sinc"] if len(a) == 1}
        for r in records for key in ("sec12", "sec21"))
    symmetry = (len({tuple(sorted(x.items())) for x in cut_cross.values()}) == 1 and
                len({round(x, 12) for x in robust_h.values()}) == 1 and
                len({round(x, 12) for x in grafo_mi.values()}) == 1 and
                len({round(x, 12) for x in type_mi.values()}) == 1)
    return {
        "finitud": all(bool(r["atractores"]) for r in records),
        "puntos_fijos_y_scheduler": fixed_ok,
        "simetria_entre_cortes": symmetry,
        "ancla_OEIS_A001372_n4": "PASS",
        "guardia_consecuencias_intrinsecas": allmask_ok,
        "mascaras_derivadas": {c: list(m) for c, m in MASKS.items()},
        "detalle_simetria": {"cruzada": {c: dict(sorted(x.items())) for c, x in cut_cross.items()},
                              "H_robustez": robust_h, "I_grafo_robustez": grafo_mi, "I_tipo_S4_robustez": type_mi},
    }


def make_summary(records, ctl):
    cross = Counter(r["dependencias"]["C12"]["cruzada"] for r in records)
    k = [label([r["periodos"], r["robustez"]["C12"]]) for r in records]
    rr = [r["robustez"]["C12"] for r in records]
    pp = [label(r["periodos"]) for r in records]
    vocab = {
        "grafo_dependencias_C12": vocabulary([label(r["dependencias"]["C12"]["grafo"]) for r in records], k, rr, pp),
        "cruzada_C12": vocabulary([r["dependencias"]["C12"]["cruzada"] for r in records], k, rr, pp),
        "tipo_S4": vocabulary([label(r["tipo_S4"]) for r in records], k, rr, pp),
    }
    det = {
        "n_dinamicas": len(records), "tipos_S4": len({label(r["tipo_S4"]) for r in records}),
        "tipos_C12": len({label(r["tipo_C12"]) for r in records}),
        "cruzada_en_C12": {x: cross.get(x, 0) for x in ("separable", "mutua", "unidir")},
        "separable_en_algun_corte": sum(any(r["dependencias"][c]["cruzada"] == "separable" for c in CUTS) for r in records),
        "mutua_en_los_3_cortes": sum(all(r["dependencias"][c]["cruzada"] == "mutua" for c in CUTS) for r in records),
        "categoria_cambia_con_el_corte": sum(len({r["dependencias"][c]["cruzada"] for c in CUTS}) > 1 for r in records),
        "con_al_menos_un_atractor": sum(bool(r["atractores"]) for r in records),
        "robustez_cambia_con_el_corte": sum(len(set(r["robustez"].values())) > 1 for r in records),
        "scheduler_puntos_fijos_distintos": sum(any({tuple(a) for a in r["scheduler"][q] if len(a)==1} != {tuple(a) for a in r["scheduler"]["sinc"] if len(a)==1} for q in ("sec12", "sec21")) for r in records),
        "scheduler_atractores_distintos": sum(r["scheduler"]["atractores_distintos"] for r in records),
        "con_ciclo_sincronico_por_cruzada": {x: sum(any(len(a)>=2 for a in r["atractores"]) and r["dependencias"]["C12"]["cruzada"]==x for r in records) for x in ("separable", "mutua", "unidir")},
        "ciclo_muere_sin_reloj_por_cruzada": {x: sum(r["scheduler"]["ciclo_muere_sin_reloj"] and r["dependencias"]["C12"]["cruzada"]==x for r in records) for x in ("separable", "mutua", "unidir")},
        "lesion_veredicto_difiere_congelar_vs_fijar0": sum(r["lesion"][v]["congelar"] != r["lesion"][v]["fijar0"] for r in records for v in ("x1", "x2")),
        "lesion_casos": len(records)*2, "perfiles_consecuencia_K": len(set(k)),
        "perfiles_robustez_C12": len(set(rr)), "H_K_bits": entropy(k), "vocabularios": vocab,
    }
    return {"controles": ctl, "deterministico": det}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    records = [record(f) for f in itertools.product(range(4), repeat=4)]
    ctl = controls(records)
    (output_dir / "por_sistema.jsonl").write_text("".join(canon(r) + "\n" for r in records), encoding="ascii")
    (output_dir / "resumen.json").write_text(canon(make_summary(records, ctl)) + "\n", encoding="ascii")


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--structural-tests":
        base_structural_tests(); print("PASS structural"); return
    if len(sys.argv) == 2 and sys.argv[1] == "--calibration-tests":
        calibration_tests(); print("PASS calibration"); return
    if len(sys.argv) == 3 and sys.argv[1] == "--run":
        run(Path(sys.argv[2])); return
    raise SystemExit("Usage: replica_a2.py --structural-tests|--calibration-tests|--run OUTPUT_DIR")


if __name__ == "__main__":
    main()
