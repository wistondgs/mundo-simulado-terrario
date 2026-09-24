"""ETP-AUTOPSY-01, sections 12-13: scaling and nearby variants.

Run only after the N=4 mechanism is closed (run_autopsy01_mechanism.py).
Every variant states, in this file and before it runs, the prediction derived
from the closed mechanism; each run records whether it was met.  Mathematical,
architectural and computational claims are kept in separate outputs.
"""
from __future__ import annotations

import csv
import json
import random
import time
from collections import Counter
from itertools import combinations
from math import comb, ceil, log2
from pathlib import Path

from autopsy01_core import (
    AND, A_AND_NOT_B, CONST0, COPY, XNOR, XOR, Net, Rule, battery, battery_passes,
    classify, public, pulse_events, run, specimen_a, summarize_run, witness_net,
)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "artifacts"
PREFIX = "autopsy01_"
T0 = time.time()
LOG = []


def log(message):
    line = f"[{time.time() - T0:7.1f}s] {message}"
    LOG.append(line)
    print(line, flush=True)


def write_csv(name, rows):
    rows = list(rows)
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with (OUT / (PREFIX + name)).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def bstr(bits):
    return "".join(map(str, bits))


def states_of(n):
    return [tuple((code >> (n - 1 - j)) & 1 for j in range(n)) for code in range(1 << n)]


# ====================================================================== §12
def mathematical_scaling():
    """Repetition code {0^n, 1^n}: exact counts, no architecture involved."""
    rows = []
    for n in range(2, 13):
        t = (n - 1) // 2
        covered = 2 * sum(comb(n, w) for w in range(t + 1))
        rows.append({
            "n": n, "d_min": n, "correction_radius_t": t, "detection_capability": n - 1,
            "tie_states": comb(n, n // 2) if n % 2 == 0 else 0,
            "tie_weight": n // 2 if n % 2 == 0 else "",
            "states_uniquely_decodable": covered, "states_total": 1 << n,
            "perfect_code": covered == 1 << n,
            "min_essential_arity_of_one_shot_decision": 2 * t + 1,
            "min_fan_in_2_depth_of_that_decision": ceil(log2(2 * t + 1)) if t else 0,
            "min_fan_in_2_gates_per_coordinate": 2 * t,
        })
    return rows


def essential(func, n):
    return tuple(j for j in range(n) if any(func(c) != func(c ^ (1 << (n - 1 - j))) for c in range(1 << n)))


def arity_lower_bound_check(n, t):
    """No function of <= 2t essential inputs restores coordinate x1 on every
    state within distance t of a codeword; some function of 2t+1 inputs does."""
    domain = [c for c in range(1 << n) if min(bin(c).count("1"), n - bin(c).count("1")) <= t]
    want = {c: int(bin(c).count("1") > n - bin(c).count("1")) for c in domain}
    best_below = 0
    for k in range(0, 2 * t + 1):
        for subset in combinations(range(n), k):
            for table in range(1 << (1 << k)):
                def f(code, subset=subset, table=table):
                    idx = 0
                    for pos, j in enumerate(subset):
                        idx |= ((code >> (n - 1 - j)) & 1) << pos
                    return (table >> idx) & 1
                if all(f(c) == want[c] for c in domain):
                    best_below += 1
    # arity 2t+1 witness: majority of x1 and 2t other coordinates
    subset = tuple(range(2 * t + 1))
    maj_ok = all(int(sum((c >> (n - 1 - j)) & 1 for j in subset) > t) == want[c] for c in domain)
    return {"n": n, "t": t, "functions_with_arity_le_2t_that_restore_x1": best_below,
            "majority_of_2t_plus_1_coordinates_restores_x1": maj_ok}


def tri_pendant(n):
    wit = {1: (2, 3), 2: (1, 3), 3: (1, 2)}
    for i in range(4, n + 1):
        wit[i] = (1, 2)
    return wit


def cycle(n):
    return {i: (((i - 2) % n) + 1, (i % n) + 1) for i in range(1, n + 1)}


def architecture_scaling():
    """Specimen-A architecture (radius-1 witness locators) at other n.

    Prediction written before running, derived from the N=4 proof:
      P1 every single error is restored exactly, DATA at t4, full at t7, for all n;
      P2 for n >= 5 (mathematical radius >= 2) some double errors are NOT
         restored: the architecture's radius stays 1.
    """
    rows = []
    for n in range(3, 9):
        for label, wit in (("triangle_plus_pendants", tri_pendant(n)), ("cycle", cycle(n))):
            if label == "cycle" and n == 3:
                continue
            net = witness_net(n, wit, name=f"{label}_{n}")
            m = battery(net)
            singles = m["_pdata"]
            p1 = all(r["outcome"] == "FULL_ORIGINAL_TARGET" and r["data_recovery_t"] == 4 and r["full_recovery_t"] == 7
                     for r in singles)
            doubles = Counter()
            for c in net.codewords:
                for a, b in combinations(range(n), 2):
                    x = list(c)
                    x[a] ^= 1
                    x[b] ^= 1
                    r = run(net, net.from_x(x))
                    doubles[classify(net, r, c)] += 1
            dtotal = sum(doubles.values())
            restored = doubles["FULL_ORIGINAL_TARGET"]
            p2 = (restored < dtotal) if n >= 5 else None
            qstar = m["_qstar"]
            # Law found at N=4: from q*, the final codeword is the majority of
            # the mutually-witnessing triangle (x1,x2,x3); pendants follow.
            triangle_law = None
            if label == "triangle_plus_pendants":
                triangle_law = all(
                    r["terminal_x"] == str(int(r["x"][:3].count("1") >= 2)) * n and r["terminal_aux_zero"]
                    for r in qstar)
            unique = [r for r in qstar if 2 * r["weight"] != n]
            to_nearest = sum(r["terminal_x"] == (("0" * n) if 2 * r["weight"] < n else ("1" * n)) and r["terminal_aux_zero"]
                             for r in unique)
            rows.append({
                "n": n, "witness_structure": label, "mathematical_radius": (n - 1) // 2,
                "n_D": len(net.families["D"]), "n_aux": len(net.aux_names), "static_edges": public(m)["n_static_edges"],
                "single_errors_restored": f"{m['pdata_full_recovery']}/{m['pdata_total']}",
                "P1_met": p1,
                "double_errors_restored": f"{restored}/{dtotal}",
                "double_to_opposite": doubles["FULL_OPPOSITE_TARGET"],
                "double_stalled": doubles["NON_CODEWORD_FIXED_POINT"],
                "double_cycling": sum(v for k, v in doubles.items() if k.startswith("CYCLE")),
                "P2_met": p2,
                "qstar_unique_to_nearest": f"{to_nearest}/{len(unique)}",
                "final_codeword_is_triangle_majority_for_all_x": triangle_law,
                "qstar_cycles_or_stalls": m["qstar_stalls"] + sum((r["cycle_length"] or 0) > 1 for r in qstar),
                "pfull_exact": f"{m['pfull_full_recovery']}/{m['pfull_total']}",
                "passes_battery": battery_passes(m),
            })
            log(f"  n={n} {label}: singles {m['pdata_full_recovery']}/{m['pdata_total']}, doubles {restored}/{dtotal}")
    return rows


# ====================================================================== §13
def build(name, xs, d_rules, e_rules, codewords, extra=None, l_delay=False, p_delay=False):
    """Generic syndrome-decoder builder with optional delay registers."""
    names = list(xs) + list(d_rules)
    rules = dict(d_rules)
    families = {"X": tuple(xs), "D": tuple(d_rules)}
    for k, v in (extra or {}).items():
        names.append(k)
        rules[k] = v
    families["R"] = tuple((extra or {}).keys())
    names += list(e_rules)
    rules.update(e_rules)
    families["E"] = tuple(e_rules)
    ls, ps, l2s, pds = [], [], [], []
    for i, x in enumerate(xs, start=1):
        e = f"e{i}"
        rules[f"l{i}"] = Rule((e,), COPY)
        ls.append(f"l{i}")
        memory = f"l{i}"
        if l_delay:
            rules[f"m{i}"] = Rule((f"l{i}",), COPY)
            l2s.append(f"m{i}")
            memory = f"m{i}"
        rules[f"p{i}"] = Rule((e, memory), A_AND_NOT_B)
        ps.append(f"p{i}")
        source = f"p{i}"
        if p_delay:
            rules[f"q{i}"] = Rule((f"p{i}",), COPY)
            pds.append(f"q{i}")
            source = f"q{i}"
        rules[x] = Rule((x, source), XOR)
    names += ls + l2s + ps + pds
    families.update({"L": tuple(ls + l2s), "P": tuple(ps), "Q": tuple(pds)})
    return Net(name, names, rules, families, codewords)


def a_with_d_delay():
    base = specimen_a()
    xs = base.x_names
    d_rules = {d: base.rules[d] for d in base.families["D"]}
    extra = {f"r{d[1:]}": Rule((d,), COPY) for d in base.families["D"]}
    e_rules = {}
    for i in range(1, 5):
        a, b = base.rules[f"e{i}"].parents
        e_rules[f"e{i}"] = Rule((f"r{a[1:]}", f"r{b[1:]}"), AND)
    return build("A_extra_delay_D_to_E", xs, d_rules, e_rules, base.codewords, extra=extra)


def a_rebuilt(name, **kwargs):
    base = specimen_a()
    return build(name, base.x_names, {d: base.rules[d] for d in base.families["D"]},
                 {e: base.rules[e] for e in base.families["E"]}, base.codewords, **kwargs)


def c3_net():
    """Codewords 0000 and 1110 (distance 3): triangle checks plus the
    weight-1 check x4 (x4 = 0 in both codewords)."""
    xs = ("x1", "x2", "x3", "x4")
    d_rules = {"d12": Rule(("x1", "x2"), XOR), "d13": Rule(("x1", "x3"), XOR),
               "d23": Rule(("x2", "x3"), XOR), "d4": Rule(("x4",), COPY)}
    e_rules = {"e1": Rule(("d12", "d13"), AND), "e2": Rule(("d12", "d23"), AND),
               "e3": Rule(("d13", "d23"), AND), "e4": Rule(("d4",), COPY)}
    return build("C3_0000_1110", xs, d_rules, e_rules, ((0, 0, 0, 0), (1, 1, 1, 0)))


def translated_net(a):
    """Distance-4 pair {a, not a}: checks x_i XOR x_j XOR (a_i XOR a_j)."""
    base = specimen_a()
    d_rules = {}
    for d in base.families["D"]:
        i, j = (int(p[1:]) - 1 for p in base.rules[d].parents)
        d_rules[d] = Rule(base.rules[d].parents, XOR if a[i] == a[j] else XNOR)
    e_rules = {e: base.rules[e] for e in base.families["E"]}
    na = tuple(1 - b for b in a)
    return build(f"A_translated_{bstr(a)}", base.x_names, d_rules, e_rules, (tuple(a), na))


def rep3_sum():
    wit = {1: (2, 3), 2: (1, 3), 3: (1, 2), 4: (5, 6), 5: (4, 6), 6: (4, 5)}
    cws = ((0,) * 6, (1, 1, 1, 0, 0, 0), (0, 0, 0, 1, 1, 1), (1,) * 6)
    return witness_net(6, wit, name="Rep3_plus_Rep3", codewords=cws)


def codeword_tests(net):
    """Single errors of every codeword; restoration to the same codeword."""
    rows = []
    for c in net.codewords:
        for k in range(len(net.x_names)):
            x = list(c)
            x[k] ^= 1
            r = run(net, net.from_x(x))
            rows.append({"codeword": bstr(c), "lesion": net.x_names[k], **summarize_run(net, r, c)})
    return rows


def update_one(net, s, i):
    _, ps, tab = net._compiled[i]
    k = 0
    for j, p in enumerate(ps):
        k |= ((s >> p) & 1) << j
    return (s | (1 << i)) if tab[k] else (s & ~(1 << i))


def run_async(net, s, rng, mode, horizon=5000):
    order = list(range(net.n_vars))
    for step in range(horizon):
        if net.step(s) == s:
            return s, step
        if mode == "random_sweep":
            rng.shuffle(order)
            for i in order:
                s = update_one(net, s, i)
        else:
            s = update_one(net, s, rng.randrange(net.n_vars))
    return s, None


def run_lossy(net, s, rng, loss, horizon=200):
    pulses = [net.index[p] for p in net.families["P"]]
    xs = [net.index[x] for x in net.x_names]
    for step in range(horizon):
        nxt = net.step(s)
        if nxt == s:
            return s, step
        for pi, xi in zip(pulses, xs):
            if (s >> pi) & 1 and rng.random() < loss:
                nxt = (nxt & ~(1 << xi)) | (s & (1 << xi))     # the toggle fails
        s = nxt
    return s, None


def run_with_flip(net, initial, t_flip, var):
    s = initial
    for _ in range(t_flip):
        s = net.step(s)
    s = net.flip(s, var)
    return run(net, s)


def dual_weight2_span(code_words, n):
    """Dimension of the span of the weight <=2 vectors orthogonal to the code."""
    def dot(u, v):
        return sum(a & b for a, b in zip(u, v)) % 2
    low = [v for v in states_of(n) if 0 < sum(v) <= 2 and all(dot(v, c) == 0 for c in code_words)]
    rows = [int(bstr(v), 2) for v in low]
    rank = 0
    for bit in reversed(range(n)):
        pivot = next((r for r in rows if (r >> bit) & 1), None)
        if pivot is None:
            continue
        rows = [r ^ pivot if (r >> bit) & 1 else r for r in rows if r != pivot]
        rank += 1
    dual_dim = n - gf2_rank([int(bstr(c), 2) for c in code_words], n)
    return {"weight_le2_checks": [bstr(v) for v in low], "span_of_weight_le2_checks": rank, "dual_dimension": dual_dim}


def gf2_rank(rows, n):
    rows = list(rows)
    rank = 0
    for bit in reversed(range(n)):
        pivot = next((r for r in rows if (r >> bit) & 1), None)
        if pivot is None:
            continue
        rows = [r ^ pivot if (r >> bit) & 1 else r for r in rows if r != pivot]
        rank += 1
    return rank


def variants():
    rows = []
    A = specimen_a()

    def add(variant, question, prediction, met, observation, **extra):
        rows.append({"variant": variant, "question": question, "prediction": prediction,
                     "prediction_met": met, "observation": observation, **extra})

    # V1 codeword pairs.
    for net, pred in ((c3_net(), "linear code {0000,1110}: same mechanism restores all 8 single errors; q identical per error position"),
                      (translated_net((0, 1, 0, 1)), "any distance-4 pair is a relabelling: XNOR where the codeword bits differ; 8/8")):
        tests = codeword_tests(net)
        ok = sum(r["outcome"] == "FULL_ORIGINAL_TARGET" for r in tests)
        # q identical for the same error position across codewords
        same_q = True
        for k in range(4):
            qs = []
            for c in net.codewords:
                x = list(c)
                x[k] ^= 1
                qs.append(tuple(net.aux_of(s) for s in run(net, net.from_x(x)).states[:8]))
            same_q &= qs[0] == qs[1]
        add(net.name, "otros pares de palabras de código", pred, ok == len(tests) and same_q,
            f"{ok}/{len(tests)} restaurados; q idéntico por posición: {same_q}")
    for d in (2, 1):
        c1 = (0, 0, 0, 0)
        c2 = tuple(int(i < d) for i in range(4))
        b1 = {tuple(b ^ (i == k) for i, b in enumerate(c1)) for k in range(4)} | {c1}
        b2 = {tuple(b ^ (i == k) for i, b in enumerate(c2)) for k in range(4)} | {c2}
        overlap = sorted(bstr(v) for v in (b1 & b2))
        add(f"distance_{d}_pair_{bstr(c1)}_{bstr(c2)}", "otros pares de palabras de código",
            "radius-1 balls overlap: no decoder of any kind can restore every single error", len(overlap) > 0,
            f"estados en ambas bolas: {','.join(overlap)}")

    # V2 more than two attractors.
    net = rep3_sum()
    tests = codeword_tests(net)
    ok = sum(r["outcome"] == "FULL_ORIGINAL_TARGET" for r in tests)
    one_per_block = within = 0
    within_to_other = 0
    for c in net.codewords:
        for a in range(3):
            for b in range(3, 6):
                x = list(c)
                x[a] ^= 1
                x[b] ^= 1
                one_per_block += classify(net, run(net, net.from_x(x)), c) == "FULL_ORIGINAL_TARGET"
        for a, b in list(combinations(range(3), 2)) + list(combinations(range(3, 6), 2)):
            x = list(c)
            x[a] ^= 1
            x[b] ^= 1
            out = classify(net, run(net, net.from_x(x)), c)
            within += 1
            within_to_other += out in ("FULL_OTHER_CODEWORD", "FULL_OPPOSITE_TARGET")
    add(net.name, "más de dos atractores",
        "two independent triangle decoders: 4 attractors; all 24 single errors and all 36 one-per-block double errors restored; "
        "two errors inside one block move that block to its other value (another codeword)",
        ok == 24 and one_per_block == 36 and within_to_other == within,
        f"simples {ok}/24; dobles uno por bloque {one_per_block}/36; dobles dentro de un bloque a otra palabra {within_to_other}/{within}")
    code523 = [(0, 0, 0, 0, 0), (1, 1, 1, 0, 0), (0, 0, 1, 1, 1), (1, 1, 0, 1, 1)]
    dual = dual_weight2_span(code523, 5)
    add("linear_[5,2,3]_code", "más de dos atractores (código acoplado)",
        "no parity-check basis of weight <=2 exists: the syndrome needs a weight-3 check (fan-in 3 or an extra XOR stage)",
        dual["span_of_weight_le2_checks"] < dual["dual_dimension"],
        f"checks de peso <=2: {dual['weight_le2_checks']}; generan {dual['span_of_weight_le2_checks']} de {dual['dual_dimension']} dimensiones del dual")

    # V3 two simultaneous DATA errors in A (from q*).
    outcomes = Counter()
    detail = []
    for c in ((0,) * 4, (1,) * 4):
        for a, b in combinations(range(4), 2):
            x = list(c)
            x[a] ^= 1
            x[b] ^= 1
            out = classify(A, run(A, A.from_x(x)), c)
            outcomes[out] += 1
            detail.append(f"{bstr(c)}+x{a + 1}x{b + 1}->{out}")
    triangle_pairs_opposite = all(("FULL_OPPOSITE" in d) == (d.split("+")[1][:4] in ("x1x2", "x1x3", "x2x3")) for d in detail)
    add("A_two_simultaneous_errors", "dos errores simultáneos",
        "a double error is a tie (distance 2 from both codewords): the triangle majority decides; pairs inside {1,2,3} go to the opposite codeword",
        triangle_pairs_opposite, f"{dict(outcomes)}")

    # V4 delays.
    for net, pred, expect in (
            (a_with_d_delay(), "extra delay D->E keeps the E block contiguous: 8/8 restored, one step later", "restore"),
            (a_rebuilt("A_extra_delay_P_to_X", p_delay=True), "extra delay P->X: 8/8 restored, one step later", "restore"),
            (a_rebuilt("A_one_shot_memory_two_steps_old", l_delay=True), "one-shot memory two steps old: the first burst has two pulses (repair, then re-break)", "burst2")):
        m = battery(net)
        pd = m["_pdata"]
        if expect == "restore":
            met = all(r["outcome"] == "FULL_ORIGINAL_TARGET" for r in pd)
        else:
            met = all(r["x_toggles"] >= 2 for r in pd)
        add(net.name, "retardos", pred, met,
            f"{m['pdata_full_recovery']}/8 restaurados; toggles por lesión {sorted({r['x_toggles'] for r in pd})}; "
            f"latencia full {sorted({r['full_recovery_t'] for r in pd if r['full_recovery_t'] is not None})}; "
            f"desenlaces {dict(Counter(r['outcome'] for r in pd))}")

    # V5 asynchronous updates.
    fixed_points_are_absorbing = True
    for mode in ("random_sweep", "random_single_coordinate"):
        rng = random.Random(20260924)
        outcome = Counter()
        for c in ((0,) * 4, (1,) * 4):
            for k in range(4):
                for _ in range(250):
                    x = list(c)
                    x[k] ^= 1
                    s, when = run_async(A, A.from_x(x), rng, mode)
                    if when is None:
                        outcome["NOT_ABSORBED"] += 1
                        continue
                    fixed_points_are_absorbing &= A.step(s) == s
                    if s == A.from_x(c):
                        outcome["ORIGINAL_TARGET"] += 1
                    elif s == A.from_x(tuple(1 - b for b in c)):
                        outcome["OPPOSITE_TARGET"] += 1
                    else:
                        outcome["LATCHED_ALARM"] += 1
        total = sum(outcome.values())
        add(f"A_async_{mode}", "actualización asíncrona",
            "the one-shot needs the synchronous pipeline: restoration is not guaranteed; runs can only end at the 16 fixed points of G",
            outcome["ORIGINAL_TARGET"] < total and fixed_points_are_absorbing,
            f"{dict(outcome)} de {total} (8 lesiones × 250 semillas)")

    # V6 partial actuator loss.
    for loss in (0.1, 0.25, 0.5):
        rng = random.Random(7 + int(loss * 100))
        restored = trials = 0
        for c in ((0,) * 4, (1,) * 4):
            for k in range(4):
                for _ in range(500):
                    x = list(c)
                    x[k] ^= 1
                    s, _ = run_lossy(A, A.from_x(x), rng, loss)
                    trials += 1
                    restored += s == A.from_x(c)
        rate = restored / trials
        add(f"A_pulse_loss_{loss}", "pérdida parcial del actuador",
            f"one-shot means no retry: P(restoration) = 1 - loss = {1 - loss:.2f} within sampling error",
            abs(rate - (1 - loss)) < 3 * ((loss * (1 - loss) / trials) ** 0.5) + 1e-9,
            f"restaurados {restored}/{trials} = {rate:.4f}")

    # V7 lesion semantics.
    stuck_ok = transient_ok = 0
    transient_times = set()
    for c in ((0,) * 4, (1,) * 4):
        for k in range(4):
            x = list(c)
            x[k] ^= 1
            r = run(A, A.from_x(x), clamps=[(f"x{k + 1}", x[k], 0)])
            term = r.states[r.cycle_start]
            stuck_ok += (r.cycle_length == 1 and A.x_of(term) == tuple(x) and len(pulse_events(A, r.states)) == 1
                         and A.get(term, f"e{k + 1}") == 1 and A.get(term, f"l{k + 1}") == 1)
            r = run(A, A.from_x(x), writes={1: {f"x{k + 1}": c[k]}})
            s = summarize_run(A, r, c)
            transient_ok += s["outcome"] == "FULL_ORIGINAL_TARGET" and s["x_toggles"] >= 3
            transient_times.add(s["full_recovery_t"])
    add("A_stuck_at_fault", "semántica de lesión: fallo permanente",
        "one pulse is spent, the toggle is overridden, the alarm latches: no retry", stuck_ok == 8, f"{stuck_ok}/8")
    add("A_self_reverting_lesion", "semántica de lesión: lesión que se revierte en t1",
        "the stale pulse breaks the healthy bit at t4; the detector then repairs its own error", transient_ok == 8,
        f"{transient_ok}/8; recuperación completa en t={sorted(transient_times)}")
    second = Counter()
    by_tau = {}
    for tau in range(1, 9):
        tally = Counter()
        for c in ((0,) * 4, (1,) * 4):
            for k in range(4):
                x = list(c)
                x[k] ^= 1
                for j in range(4):
                    r = run_with_flip(A, A.from_x(x), tau, f"x{j + 1}")
                    tally[classify(A, r, c)] += 1
        by_tau[tau] = dict(tally)
        second.update(tally)
    add("A_second_lesion_during_repair", "semántica de lesión: segundo error durante la reparación",
        "a second error while one correction is in flight acts on stale detection; outcomes depend on timing (no fixed prediction)",
        None, json.dumps(by_tau))
    return rows


def main():
    log("§12 mathematical scaling of the repetition code")
    math_rows = mathematical_scaling()
    write_csv("scaling_math.csv", math_rows)
    log("§12 arity lower bound 2t+1, checked by brute force")
    bounds = [arity_lower_bound_check(4, 1), arity_lower_bound_check(5, 2), arity_lower_bound_check(6, 2)]
    for b in bounds:
        log(f"  {b}")
    log("§12 specimen-A architecture at other n")
    arch_rows = architecture_scaling()
    write_csv("scaling_architecture.csv", arch_rows)
    log("§13 nearby variants")
    variant_rows = variants()
    write_csv("variants.csv", variant_rows)
    for row in variant_rows:
        log(f"  {row['variant']}: met={row['prediction_met']} | {row['observation'][:160]}")
    summary = {
        "instrument": "run_autopsy01_scaling_variants.py",
        "arity_lower_bound_checks": bounds,
        "architecture": {"P1_all_met": all(r["P1_met"] for r in arch_rows),
                         "P2_all_met": all(r["P2_met"] for r in arch_rows if r["P2_met"] is not None)},
        "variants_with_prediction": sum(r["prediction_met"] is not None for r in variant_rows),
        "variants_prediction_met": sum(bool(r["prediction_met"]) for r in variant_rows),
        "log": LOG,
    }
    (OUT / (PREFIX + "scaling_variants.json")).write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
    log(f"architecture P1 {summary['architecture']['P1_all_met']}, P2 {summary['architecture']['P2_all_met']}; "
        f"variants met {summary['variants_prediction_met']}/{summary['variants_with_prediction']}")


if __name__ == "__main__":
    main()
