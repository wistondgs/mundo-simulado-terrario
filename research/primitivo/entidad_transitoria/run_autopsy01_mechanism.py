"""ETP-AUTOPSY-01: causal autopsy of specimen A's restoration mechanism.

Central hypothesis, to prove or destroy, not to assume:

    H-CORE: A implements a distributed single-error decoder for the
    repetition code C = {0000, 1111}.

Method.  The frozen transition build_baseline_atlas.step is audited on all
2**21 states and every later claim is computed from a network verified equal
to it.  Committed PRE-01 / EXP-01..03 artifacts are read, not regenerated.
Interventions are explicit (persistent clamps, one-step writes, rule edits),
each family with a no-op sham.  Predictions derived from H-CORE are written in
this file before the runs and each run records whether it met them; a failed
prediction is recorded, never patched.  EXP-04A (preregistered) is not run.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import math
import sys
import time
from array import array
from collections import Counter, defaultdict
from itertools import combinations, product
from pathlib import Path

from build_baseline_atlas import (
    D as ATLAS_D, E as ATLAS_E, L as ATLAS_L, P as ATLAS_P, PARENTS, Q as ATLAS_Q,
    TARGETS, VARS, X as ATLAS_X, effective_edges, step as frozen_step,
)
from autopsy01_core import (
    A_AND_NOT_B, AND, CONST0, COPY, NOT, TWO_INPUT_TABLES, XOR, Net, Rule,
    SPECIMEN_A_WITNESSES, WideNet, WideRule, all_witness_assignments, battery,
    battery_passes, classify, gate_name, public, pulse_events, run, specimen_a,
    summarize_run, terminal_cycle, witness_net, x_toggles,
)

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
OUT = ROOT / "artifacts"
PREFIX = "autopsy01_"
N_STATES = 1 << 21
T0 = time.time()
LOG = []


def log(message):
    line = f"[{time.time() - T0:7.1f}s] {message}"
    LOG.append(line)
    print(line, flush=True)


def write_csv(name, rows):
    rows = list(rows)
    assert rows, name
    fields = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    with (OUT / (PREFIX + name)).open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_json(name, payload):
    (OUT / (PREFIX + name)).write_text(json.dumps(payload, indent=2, sort_keys=False, default=str) + "\n", encoding="utf-8")


def bstr(bits):
    return "".join(map(str, bits))


A = specimen_a()
assert A.names == VARS, "network coordinate order must equal the frozen VARS order"
CODEWORDS = ((0, 0, 0, 0), (1, 1, 1, 1))
CHECKS_OF = {f"e{i}": A.rules[f"e{i}"].parents for i in range(1, 5)}          # E_i -> its two D inputs
ENDPOINTS = {d: tuple(A.rules[d].parents) for d in A.families["D"]}            # D -> its two X inputs
WITNESS = SPECIMEN_A_WITNESSES


def lesions():
    for c in CODEWORDS:
        for k in range(4):
            x = list(c)
            x[k] ^= 1
            yield c, k, tuple(x)


def lesion_id(c, k):
    return f"{bstr(c)}:x{k + 1}"


def snapshot(net, s):
    row = {"x": bstr(net.x_of(s))}
    for fam in ("D", "E", "L", "P"):
        if net.families.get(fam):
            row[fam] = net.pattern(s, fam)
    return row


def trace_rows(run_id, net, states, extra=None):
    rows = []
    for t, s in enumerate(states):
        row = {"run_id": run_id, "t": t, **snapshot(net, s)}
        row["aux_on"] = sum(net.aux_of(s))
        if extra:
            row.update(extra)
        rows.append(row)
    return rows


# ====================================================================== §0
def section0_equation_audit():
    log("§0 exhaustive audit of the frozen transition on 2**21 states")
    succ = array("I", bytes(4 * N_STATES))
    mismatches = 0
    for s in range(N_STATES):
        tup = tuple((s >> i) & 1 for i in range(21))
        nxt = frozen_step(tup)
        v = 0
        for i, b in enumerate(nxt):
            if b:
                v |= 1 << i
        if A.step(s) != v:
            mismatches += 1
        succ[s] = v
    log(f"  frozen step vs rebuilt rules: {mismatches} mismatches")
    assert mismatches == 0

    # Essential inputs of every coordinate, observed on the full truth table.
    essential_acc = []
    for v in range(21):
        m = 1 << v
        acc = 0
        for hi in range(0, N_STATES, 2 * m):
            for s in range(hi, hi + m):
                acc |= succ[s] ^ succ[s + m]
        essential_acc.append(acc)
    observed_parents = {}
    for c, name in enumerate(VARS):
        observed_parents[name] = tuple(VARS[v] for v in range(21) if (essential_acc[v] >> c) & 1)
    parents_match = all(set(observed_parents[n]) == set(PARENTS[n]) for n in VARS)
    log(f"  observed essential inputs equal declared parents: {parents_match}")

    # Global complement of DATA (x -> 1-x, q unchanged) commutes with G.
    xmask = 0b1111
    complement_equivariant = all(succ[s ^ xmask] == succ[s] ^ xmask for s in range(N_STATES))
    log(f"  complement equivariance G(c z) = c G(z): {complement_equivariant}")

    # (x1 x2) with induced relabelling, as declared by PRE-01.
    swap = {"x1": "x2", "x2": "x1", "x3": "x3", "x4": "x4", "d12": "d12", "d13": "d23", "d23": "d13",
            "d14": "d24", "d24": "d14", "e1": "e2", "e2": "e1", "e3": "e3", "e4": "e4",
            "l1": "l2", "l2": "l1", "l3": "l3", "l4": "l4", "p1": "p2", "p2": "p1", "p3": "p3", "p4": "p4"}
    target_bit = [VARS.index(swap[n]) for n in VARS]
    chunk_tables = []
    for chunk in range(3):
        table = []
        for value in range(128):
            out = 0
            for j in range(7):
                if (value >> j) & 1:
                    out |= 1 << target_bit[chunk * 7 + j]
            table.append(out)
        chunk_tables.append(table)

    def permute(s):
        return chunk_tables[0][s & 127] | chunk_tables[1][(s >> 7) & 127] | chunk_tables[2][s >> 14]

    swap_equivariant = all(succ[permute(s)] == permute(succ[s]) for s in range(N_STATES))
    log(f"  (x1 x2) automorphism on all states: {swap_equivariant}")

    fixed = [s for s in range(N_STATES) if succ[s] == s]
    fixed_rows = []
    for s in fixed:
        x = A.x_of(s)
        fixed_rows.append({"x": bstr(x), **snapshot(A, s), "is_target": x in CODEWORDS and A.aux_zero(s)})
    log(f"  fixed points: {len(fixed)}")

    census = state_space_census(succ)
    log(f"  attractors: {len(census['attractors'])}; transient max {census['max_transient']}")

    targets_q = {bstr(c): A.pattern(A.from_x(c), "D") + A.pattern(A.from_x(c), "E") +
                 A.pattern(A.from_x(c), "L") + A.pattern(A.from_x(c), "P") for c in CODEWORDS}
    audit = {
        "states_audited": N_STATES,
        "rebuilt_rules_equal_frozen_step": mismatches == 0,
        "equations": {
            "D": "d12'=x1^x2; d13'=x1^x3; d23'=x2^x3; d14'=x1^x4; d24'=x2^x4",
            "E": "e1'=d12&d13; e2'=d12&d23; e3'=d13&d23; e4'=d14&d24",
            "L": "l_i'=e_i",
            "P": "p_i'=e_i & ~l_i",
            "X": "x_i'=x_i ^ p_i",
        },
        "observed_essential_inputs": observed_parents,
        "observed_equals_declared_parents": parents_match,
        "max_observed_fan_in": max(len(v) for v in observed_parents.values()),
        "inputs_outside_the_21_state_bits": "none: G is a function of the 21 bits (exhaustive table)",
        "time_homogeneous": "one transition table for every t (the audited table)",
        "complement_equivariant_all_states": complement_equivariant,
        "swap_x1_x2_equivariant_all_states": swap_equivariant,
        "aux_baseline_per_target": targets_q,
        "coordinates_that_differ_between_the_two_targets": ["x1", "x2", "x3", "x4"],
        "fixed_point_count": len(fixed),
    }
    write_json("equation_audit.json", audit)
    write_csv("fixed_points.csv", fixed_rows)
    write_json("state_space_census.json", census)
    return succ, audit, census, fixed_rows


def state_space_census(succ):
    n = len(succ)
    status = bytearray(n)           # 0 new, 1 on current path, 2 done
    attractor = array("i", [-1]) * n
    depth = array("i", [0]) * n
    cycles = {}
    for start in range(n):
        if status[start]:
            continue
        path = []
        s = start
        while status[s] == 0:
            status[s] = 1
            path.append(s)
            s = succ[s]
        if status[s] == 1:
            i = path.index(s)
            cycle = path[i:]
            cid = min(cycle)
            cycles[cid] = cycle
            for c in cycle:
                attractor[c] = cid
                depth[c] = 0
                status[c] = 2
            path = path[:i]
            base_att, base_depth = cid, 0
        else:
            base_att, base_depth = attractor[s], depth[s]
        for k, p in enumerate(reversed(path), start=1):
            attractor[p] = base_att
            depth[p] = base_depth + k
            status[p] = 2
    basin = Counter(attractor)
    qstar_mask = ~0b1111 & ((1 << 21) - 1)
    rows = []
    for cid, cycle in sorted(cycles.items(), key=lambda item: -basin[item[0]]):
        s = cycle[0]
        x = A.x_of(s)
        kind = ("TARGET" if (len(cycle) == 1 and x in CODEWORDS and A.aux_zero(s)) else
                "LATCHED_ALARM_FIXED_POINT" if len(cycle) == 1 else f"CYCLE_{len(cycle)}")
        rows.append({
            "attractor_id": cid, "kind": kind, "cycle_length": len(cycle),
            "states": [snapshot(A, c) for c in cycle],
            "basin_size": basin[cid], "basin_fraction": basin[cid] / n,
        })
    transients = Counter(depth)
    # Restoration landscape of the physically meaningful starts.
    qstar_starts = {bstr(A.x_of(s)): None for s in range(16)}
    for s in range(16):
        qstar_starts[bstr(A.x_of(s))] = attractor[s]
    target_ids = {A.from_x(c): None for c in CODEWORDS}
    single_flip = Counter()
    double_flip = Counter()
    for c in CODEWORDS:
        base = A.from_x(c)
        for i in range(21):
            single_flip[attractor[base ^ (1 << i)] == base] += 1
        for i, j in combinations(range(21), 2):
            double_flip[attractor[base ^ (1 << i) ^ (1 << j)] == base] += 1
    return {
        "states": n,
        "attractors": rows,
        "max_transient": max(depth),
        "transient_histogram": dict(sorted(transients.items())),
        "qstar_start_attractor": {k: v for k, v in qstar_starts.items()},
        "single_coordinate_flips_returning_to_same_target": single_flip[True],
        "single_coordinate_flips_total": single_flip[True] + single_flip[False],
        "double_coordinate_flips_returning_to_same_target": double_flip[True],
        "double_coordinate_flips_total": double_flip[True] + double_flip[False],
    }


# ====================================================================== §1
def section1_ledger():
    log("§1 inherited causal ledger: committed artifacts versus the audited network")
    committed = defaultdict(list)
    with (OUT / "p_data_traces.csv").open(encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            committed[row["trajectory_id"]].append(row)
    reproduced = 0
    for c, k, x in lesions():
        name = f"PDATA_{bstr(c)}_x{k + 1}"
        r = run(A, A.from_x(x))
        mine = [(bstr(A.x_of(s)), A.pattern(s, "D") + A.pattern(s, "E") + A.pattern(s, "L") + A.pattern(s, "P"))
                for s in r.states[:r.cycle_start + 1]]
        theirs = [(row["x"], row["q"]) for row in sorted(committed[name], key=lambda row: int(row["t"]))]
        reproduced += mine == theirs
    log(f"  committed P-DATA traces reproduced bit for bit: {reproduced}/8")

    def read(name):
        with (OUT / name).open(encoding="utf-8") as handle:
            return list(csv.DictReader(handle))

    exp01 = read("exp01_action_cut_summary.csv")
    exp02 = read("exp02_external_repair_summary.csv")
    exp03 = read("exp03_onset_gate_summary.csv")
    pfull = read("p_full_summary.csv")

    # Re-derive the EXP-01 action-cut terminal state with this module's
    # runner: the cut keeps x_i at t4 equal to x_i(t3); G from t4 on.
    exp01_match = 0
    cut_rows = [row for row in exp01 if row["arm"] == "ACTION_CUT"]
    for row in cut_rows:
        c = tuple(int(b) for b in row["target"])
        k = int(row["flipped_coordinate"][1:]) - 1
        x = list(c)
        x[k] ^= 1
        r = run(A, A.from_x(x), writes={4: {f"x{k + 1}": x[k]}})
        term = r.states[r.cycle_start]
        exp01_match += (bstr(A.x_of(term)) == row["terminal_x"] and
                        A.pattern(term, "D") + A.pattern(term, "E") + A.pattern(term, "L") + A.pattern(term, "P") == row["terminal_q"])
    log(f"  EXP-01 cut fixed point reproduced by this runner: {exp01_match}/{len(cut_rows)}")

    ledger = [
        {"phase": "ONSET", "question": "¿Qué lleva de la perturbación DATA a q != q*?",
         "intervention": "EXP-03: sustitución del padre DATA perturbado en las D incidentes (transitoria y persistente), con sham no-op",
         "observation": "persistente: x perturbada y q=q* fijos en 8/8; transitoria: misma secuencia desplazada un paso (64/64 comparaciones exactas)",
         "proves": "la transmisión x->D es necesaria para el onset P-DATA; el onset se regenera desde la perturbación DATA presente",
         "does_not_prove": "qué calculan D o E, ni de dónde sale la dirección",
         "source": "ETP_EXP_03_ONSET_CAUSAL_GATE.md; artifacts/exp03_onset_gate_summary.csv",
         "committed_rows": len(exp03)},
        {"phase": "ACTION", "question": "¿La arista p_i(t3)->x_i(t4) es necesaria para la reconstrucción?",
         "intervention": "EXP-01: corte de esa única arista en t3->t4, con shams temporal y espacial",
         "observation": "8/8 cortes quedan en un punto fijo no objetivo (x perturbada, D/E/L altos, P=0); 16 shams idénticos al natural",
         "proves": "la arista P->X es necesaria para reconstrucción DATA y para la terminación normal",
         "does_not_prove": "qué selecciona la coordenada ni por qué el pulso es único",
         "source": "ETP_EXP_01_ACTION_CUT.md; artifacts/exp01_action_cut_summary.csv",
         "committed_rows": len(exp01)},
        {"phase": "TERMINATION", "question": "¿Qué retira el soporte de D/E/L y por qué cesa P?",
         "intervention": "EXP-02: desde el punto fijo del corte, escribir sólo x=blanco con q idéntico; sham NO_OP_WRITE",
         "observation": "TARGET_RESTORATION reingresa al estado natural t4 y llega a q* en t7 (8/8); NO_OP_WRITE conserva el punto fijo",
         "proves": "la restauración de x media la terminación de D/E/L; P termina por L (terminación de pulso) aun sin x restaurada",
         "does_not_prove": "la función lógica del circuito completo",
         "source": "ETP_EXP_02_EXTERNAL_REPAIR.md; artifacts/exp02_external_repair_summary.csv",
         "committed_rows": len(exp02)},
        {"phase": "BASELINE", "question": "¿Cuál es la cronología natural?",
         "intervention": "ninguna (PRE-01, atlas basal); P-FULL: volteo de cada coordenada en cada blanco",
         "observation": "onset t1, D/E/L/P en t1/t2/t3/t3, x corregida t4, estado completo t7; P-FULL 42/42, latencia máxima 9",
         "proves": "trayectorias exactas y clases de respuesta",
         "does_not_prove": "necesidad causal de cada parte",
         "source": "ETP_PRE_01_BASELINE_CAUSAL_ATLAS.md; artifacts/p_data_traces.csv, p_full_summary.csv",
         "committed_rows": len(pfull)},
        {"phase": "PROJECTED_APD", "question": "¿Existe el mapa restaurador y puede implementarse directo con aridad <=2?",
         "intervention": "ninguna; enumeración (verificada aquí en §9) y DISCOVERY-03 (búsqueda exhaustiva X-only)",
         "observation": "Phi existe sobre R_X (bolas disjuntas); ninguna función de aridad esencial <=2 lo extiende (verificado en §9)",
         "proves": "la conducta global no es una regla directa de fan-in 2",
         "does_not_prove": "cómo la compila la red con auxiliares",
         "source": "CONTEXT.md (RESEARCHER_SUPPLIED); §9 de este instrumento",
         "committed_rows": ""},
    ]
    write_csv("causal_ledger.csv", ledger)
    return {"pdata_traces_reproduced": reproduced, "exp01_cut_fixed_point_reproduced": exp01_match,
            "exp01_cut_rows": len(cut_rows)}


# ====================================================================== §2
def syndrome(x):
    """Evaluate the D rules on x (the value D takes one step later)."""
    return tuple(x[int(a[1:]) - 1] ^ x[int(b[1:]) - 1] for a, b in (ENDPOINTS[d] for d in A.families["D"]))


def locator(syn):
    d = dict(zip(A.families["D"], syn))
    return tuple(d[CHECKS_OF[f"e{i}"][0]] & d[CHECKS_OF[f"e{i}"][1]] for i in range(1, 5))


def section2_code_theory():
    log("§2 code-theoretic characterization of R_X and Phi")
    rows = []
    checks = {"A_RX_equals_union_of_radius1_balls": True, "B_unique_nearest_codeword_on_RX": True,
              "C_weight2_is_exact_tie_set": True, "D_Phi_equals_nearest_codeword_decoding": True}
    cosets = defaultdict(list)
    for code in range(16):
        x = tuple((code >> (3 - j)) & 1 for j in range(4))
        w = sum(x)
        d0, d1 = w, 4 - w
        in_rx = w in (0, 1, 3, 4)
        ball = min(d0, d1) <= 1
        nearest = [c for c, d in zip(CODEWORDS, (d0, d1)) if d == min(d0, d1)]
        phi = (0,) * 4 if w <= 1 else (1,) * 4 if w >= 3 else None
        syn = syndrome(x)
        eps = locator(syn)
        corrected = tuple(a ^ b for a, b in zip(x, eps))
        tri = int(sum(x[:3]) >= 2)
        cosets[syn].append(x)
        checks["A_RX_equals_union_of_radius1_balls"] &= (in_rx == ball)
        if in_rx:
            checks["B_unique_nearest_codeword_on_RX"] &= len(nearest) == 1
            checks["D_Phi_equals_nearest_codeword_decoding"] &= (phi == nearest[0])
        if w == 2:
            checks["C_weight2_is_exact_tie_set"] &= (len(nearest) == 2)
        else:
            checks["C_weight2_is_exact_tie_set"] &= (len(nearest) == 1)
        rows.append({
            "x": bstr(x), "weight": w, "d_H_to_0000": d0, "d_H_to_1111": d1, "in_R_X": in_rx,
            "nearest_codewords": "|".join(bstr(c) for c in nearest), "Phi": bstr(phi) if phi else "UNDEFINED_TIE",
            "syndrome_d12_d13_d23_d14_d24": bstr(syn), "locator_e1_e4": bstr(eps),
            "x_xor_locator": bstr(corrected), "triangle_majority_x1x2x3": tri,
        })
    dmin = 4
    coset_rows = []
    for syn, members in sorted(cosets.items()):
        # coset of x modulo C = {x, x XOR 1111}; its leader is the
        # minimum-weight member, i.e. the most likely error pattern.
        weights = [sum(m) for m in members]
        min_w = min(weights)
        coset_rows.append({"syndrome": bstr(syn), "members": "|".join(bstr(m) for m in members),
                           "leader_weight": min_w,
                           "unique_leader": weights.count(min_w) == 1})
    theory = {
        **checks,
        "E_minimum_distance": dmin,
        "E_unique_decoding_radius": (dmin - 1) // 2,
        "E_error_detection_capability": dmin - 1,
        "radius1_ball_sizes": [5, 5], "states_covered_by_balls": 10, "tie_states": 6,
        "code_is_linear": True,
        "parity_checks_used": list(A.families["D"]),
        "parity_check_rank_gf2": gf2_rank([[int(v in ENDPOINTS[d]) for v in ("x1", "x2", "x3", "x4")] for d in A.families["D"]]),
        "cosets": len(cosets),
        "coset_table": coset_rows,
    }
    write_csv("code_theory.csv", rows)
    return theory, rows


def gf2_rank(matrix):
    rows = [int("".join(map(str, r)), 2) for r in matrix]
    rank = 0
    for bit in reversed(range(max(len(r) for r in matrix))):
        pivot = next((r for r in rows if (r >> bit) & 1), None)
        if pivot is None:
            continue
        rows = [r ^ pivot if (r >> bit) & 1 and r != pivot else r for r in rows if r != pivot]
        rank += 1
    return rank


# ====================================================================== §3 / §5
def section3_lesion_table():
    log("§3 error-detection mechanism: 8-lesion table from the real dynamics")
    table, timeline = [], []
    exact_single_locator = 0
    for c, k, x in lesions():
        r = run(A, A.from_x(x))
        states = r.states
        s1, s2, s3, s4 = states[1], states[2], states[3], states[4]
        e_on = [i for i in range(4) if A.get(s2, f"e{i + 1}")]
        p_on = [i for i in range(4) if A.get(s3, f"p{i + 1}")]
        # exactly one E_i at every t of the trajectory, and it is the lesion
        only_lesion = all(
            [i for i in range(4) if A.get(s, f"e{i + 1}")] in ([], [k]) for s in states)
        exact_single_locator += (e_on == [k] and p_on == [k] and only_lesion)
        summary = summarize_run(A, r, c)
        table.append({
            "lesion": lesion_id(c, k), "x_lesioned": bstr(x),
            "D_t1_d12_d13_d23_d14_d24": A.pattern(s1, "D"),
            "D_active_checks": ",".join(d for d in A.families["D"] if A.get(s1, d)),
            "E_t2_e1_e4": A.pattern(s2, "E"),
            "selected_coordinate": ",".join(f"x{i + 1}" for i in e_on),
            "is_damaged_coordinate": e_on == [k],
            "P_t3_p1_p4": A.pattern(s3, "P"),
            "X_t4_repaired": bstr(A.x_of(s4)),
            "X_t4_equals_codeword": A.x_of(s4) == c,
            "E_active_only_on_lesion_at_all_t": only_lesion,
            "p_pulses_total": summary["p_pulses"],
            "data_recovery_t": summary["data_recovery_t"],
            "full_recovery_t": summary["full_recovery_t"],
            "outcome": summary["outcome"],
        })
        for t, s in enumerate(states[:r.cycle_start + 1]):
            timeline.append({"lesion": lesion_id(c, k), "t": t, **snapshot(A, s), "aux_on": sum(A.aux_of(s))})
    write_csv("lesion_table.csv", table)
    write_csv("lesion_timelines.csv", timeline)

    # Locator theorem on all of R_X for the real E rules.
    rx_exact = True
    for code in range(16):
        x = tuple((code >> (3 - j)) & 1 for j in range(4))
        w = sum(x)
        if w in (0, 4):
            rx_exact &= locator(syndrome(x)) == (0, 0, 0, 0)
        elif w in (1, 3):
            minority = 1 if w == 1 else 0
            err = tuple(int(b == minority) for b in x)
            rx_exact &= locator(syndrome(x)) == err
    # Generalization: every witness assignment gives an exact locator on R_X.
    general = 0
    total = 0
    for wit in all_witness_assignments(4):
        total += 1
        ok = True
        for code in range(16):
            x = tuple((code >> (3 - j)) & 1 for j in range(4))
            w = sum(x)
            eps = tuple(int(x[i - 1] != x[a - 1] and x[i - 1] != x[b - 1]) for i, (a, b) in sorted(wit.items()))
            if w in (0, 4):
                ok &= eps == (0, 0, 0, 0)
            elif w in (1, 3):
                minority = 1 if w == 1 else 0
                ok &= eps == tuple(int(b == minority) for b in x)
        general += ok
    result = {
        "lesions_with_exactly_one_E_equal_to_damaged_bit": exact_single_locator,
        "locator_exact_on_all_R_X_states": rx_exact,
        "witness_assignments_with_exact_locator_on_R_X": f"{general}/{total}",
    }
    log(f"  exactly-one-E = damaged bit: {exact_single_locator}/8; all witness assignments exact: {general}/{total}")
    return result, table


def section5_temporal():
    log("§5 temporal mechanism: L as delayed E, P as rising-edge detector")
    identity_l = identity_p = 0
    total_l = total_p = 0
    blocks = []
    for c, k, x in lesions():
        r = run(A, A.from_x(x))
        st = r.states
        for t in range(1, len(st)):
            for i in range(1, 5):
                total_l += 1
                identity_l += A.get(st[t], f"l{i}") == A.get(st[t - 1], f"e{i}")
        for t in range(1, len(st) - 1):
            for i in range(1, 5):
                total_p += 1
                identity_p += A.get(st[t + 1], f"p{i}") == (A.get(st[t], f"e{i}") & (1 - A.get(st[t - 1], f"e{i}")))
        e_series = "".join(str(A.get(s, f"e{k + 1}")) for s in st)
        d_series = "".join(str(int(any(A.get(s, d) for d in CHECKS_OF[f"e{k + 1}"]))) for s in st)
        x_series = "".join(str(int(A.x_of(s) != c)) for s in st)
        p_series = "".join(str(A.get(s, f"p{k + 1}")) for s in st)
        l_series = "".join(str(A.get(s, f"l{k + 1}")) for s in st)
        rising = sum(1 for t in range(1, len(e_series)) if e_series[t] == "1" and e_series[t - 1] == "0")
        blocks.append({
            "lesion": lesion_id(c, k),
            "x_wrong_by_t": x_series, "witness_checks_on_by_t": d_series,
            "e_k_by_t": e_series, "l_k_by_t": l_series, "p_k_by_t": p_series,
            "e_k_on_steps": e_series.count("1"), "e_k_rising_edges": rising,
            "e_k_contiguous_block": "1" in e_series and "0" not in e_series.strip("0"),
        })
    result = {
        "L_equals_E_delayed_one_step": f"{identity_l}/{total_l}",
        "P_equals_rising_edge_of_E": f"{identity_p}/{total_p}",
        "all_E_blocks_contiguous_single_rising_edge": all(b["e_k_contiguous_block"] and b["e_k_rising_edges"] == 1 for b in blocks),
        "E_block_length": sorted({b["e_k_on_steps"] for b in blocks}),
    }
    write_csv("temporal_blocks.csv", blocks)
    log(f"  L=E(t-1): {identity_l}/{total_l}; P=rising edge: {identity_p}/{total_p}")
    return result, blocks


# ====================================================================== §4
def section4_direction(audit):
    log("§4 direction of repair: where the target identity lives")
    q_traj = {}
    x_traj = {}
    for c, k, x in lesions():
        r = run(A, A.from_x(x))
        q_traj[(c, k)] = tuple(A.aux_of(s) for s in r.states[:8])
        x_traj[(c, k)] = tuple(A.x_of(s) for s in r.states[:8])
    complement_same_q = all(q_traj[((0,) * 4, k)] == q_traj[((1,) * 4, k)] for k in range(4))

    def mutual_information(pairs):
        joint = Counter(pairs)
        n = sum(joint.values())
        pa = Counter(a for a, _ in pairs)
        pb = Counter(b for _, b in pairs)
        return sum(v / n * math.log2((v / n) / ((pa[a] / n) * (pb[b] / n))) for (a, b), v in joint.items())

    mi_rows = []
    for t in range(8):
        q_pairs = [(q_traj[(c, k)][t], c) for c, k, _ in lesions()]
        x_pairs = [(x_traj[(c, k)][t], c) for c, k, _ in lesions()]
        pos_pairs = [(q_traj[(c, k)][t], k) for c, k, _ in lesions()]
        mi_rows.append({"t": t, "MI_q_codeword_bits": round(mutual_information(q_pairs), 12),
                        "MI_x_codeword_bits": round(mutual_information(x_pairs), 12),
                        "MI_q_lesion_position_bits": round(mutual_information(pos_pairs), 12)})
    write_csv("direction_information.csv", mi_rows)

    # Same pulse, opposite physical change: the actuator is a toggle.
    toggles = []
    for k in range(4):
        low = ((0,) * 4, k)
        high = ((1,) * 4, k)
        toggles.append({
            "position": f"x{k + 1}",
            "pulse_pattern_same_in_both": q_traj[low][3] == q_traj[high][3],
            "x_k_change_from_0000_lesion": f"{x_traj[low][3][k]}->{x_traj[low][4][k]}",
            "x_k_change_from_1111_lesion": f"{x_traj[high][3][k]}->{x_traj[high][4][k]}",
        })
    write_csv("direction_toggle.csv", toggles)
    target_search = {
        "target_variable": "none: at both targets q = 0^17; only x1..x4 differ between them",
        "reward_or_goal_token": "none: no coordinate outside x1..x4 differs between targets, and every coordinate's observed inputs are its declared <=2 parents",
        "oracle_or_external_state": "none: G is an exhaustive table over the 21 state bits (audited)",
        "hardcoded_direction_switch": "none: G commutes with complementing x on all 2**21 states, so any repair toward 0000 has a mirror toward 1111",
        "clock_or_step_counter": "none: a single time-homogeneous table",
    }
    result = {
        "complementary_lesions_share_q_trajectory": complement_same_q,
        "max_MI_q_codeword_bits": max(r["MI_q_codeword_bits"] for r in mi_rows),
        "MI_x_codeword_bits_all_t": sorted({r["MI_x_codeword_bits"] for r in mi_rows}),
        "target_search": target_search,
        "complement_equivariant": audit["complement_equivariant_all_states"],
    }
    log(f"  q identical for complementary lesions: {complement_same_q}; max MI(q;codeword) = {result['max_MI_q_codeword_bits']}")
    return result, mi_rows, toggles


# ====================================================================== §6
def amputate(net, family, name):
    return net.edited(name, {n: Rule((), CONST0) for n in net.families[family]})


def clamp_rule(net, coordinate, name):
    return net.edited(name, {coordinate: Rule((), CONST0)})


def section6_interventions():
    log("§6 causal interventions with no-op shams")
    summaries, traces = [], []
    natural = {}
    for c, k, x in lesions():
        natural[(c, k)] = run(A, A.from_x(x)).states

    def record(family, arm, net, c, k, r, predicted, detail="", label=None):
        s = summarize_run(net, r, c)
        met = bool(predicted(s, r))
        label = label or lesion_id(c, k)
        reference = natural.get((c, k)) if label == lesion_id(c, k) else None
        row = {"family": family, "arm": arm, "network": net.name, "lesion": label,
               **s, "prediction": detail, "prediction_met": met,
               "identical_to_natural": (reference is not None and len(r.states) >= len(reference)
                                        and r.states[:len(reference)] == reference)}
        summaries.append(row)
        end = r.cycle_start + 1 if r.cycle_start is not None else None
        traces.extend(trace_rows(f"{family}|{arm}|{label}", net, r.states[:end]))
        return row

    def full_ok(s, r):
        return s["outcome"] == "FULL_ORIGINAL_TARGET"

    def stuck_lesioned(c, k):
        x = list(c)
        x[k] ^= 1
        x = tuple(x)
        return lambda s, r: s["outcome"] == "NON_CODEWORD_FIXED_POINT" and s["terminal_x"] == bstr(x) and s["p_pulses"] == 0

    # A1: detector ablation d ≡ 0.
    for d in A.families["D"]:
        net = clamp_rule(A, d, f"A_minus_{d}")
        for c, k, x in lesions():
            r = run(net, A.from_x(x))
            used = d in CHECKS_OF[f"e{k + 1}"]
            present = f"x{k + 1}" in ENDPOINTS[d]
            if used:
                record("A1_DETECTOR_ABLATION", f"{d}=0", net, c, k, r, stuck_lesioned(c, k),
                       "check used by E_k: no localization, no pulse, lesion persists")
            else:
                arm = f"{d}=0" + ("" if present else "_SHAM_NOOP")
                record("A1_DETECTOR_ABLATION", arm, net, c, k, r, full_ok,
                       "check not used by E_k: repair unaffected" + ("" if present else " (check naturally 0: identical trajectory)"))

    # A2: remove one witness from a locator (the removed D input read as 1).
    for i in range(1, 5):
        for j, removed in enumerate(CHECKS_OF[f"e{i}"]):
            kept = CHECKS_OF[f"e{i}"][1 - j]
            net = A.edited(f"A_e{i}_without_{removed}", {f"e{i}": Rule((kept,), COPY)})
            for c, k, x in lesions():
                r = run(net, A.from_x(x))
                # e_i now fires whenever `kept` fires.  kept = d_{i,w}: it also
                # fires for a lesion at w, which then toggles x_i as well.
                other = [int(v[1:]) for v in ENDPOINTS[kept] if v != f"x{i}"][0]
                false_alarm = (k + 1 == other)
                if false_alarm:
                    pred = lambda s, r: s["p_pulses"] >= 2
                    detail = f"single witness: lesion at x{other} also fires e{i}: false toggle of x{i}"
                else:
                    pred = full_ok
                    detail = "single witness not triggered by this lesion"
                record("A2_WITNESS_REMOVAL", f"e{i}={kept}", net, c, k, r, pred, detail)

    # B: locator ablation e ≡ 0.
    for i in range(1, 5):
        net = clamp_rule(A, f"e{i}", f"A_minus_e{i}")
        for c, k, x in lesions():
            r = run(net, A.from_x(x))
            if k + 1 == i:
                pred = lambda s, r, c=c, k=k: (s["outcome"] == "NON_CODEWORD_FIXED_POINT" and s["p_pulses"] == 0)
                record("B_LOCATOR_ABLATION", f"e{i}=0", net, c, k, r, pred, "disagreement present, localization removed: no repair")
            else:
                record("B_LOCATOR_ABLATION", f"e{i}=0_SHAM_NOOP", net, c, k, r, full_ok, "E_i naturally 0: identical trajectory")

    # C: locator rescue with detection amputated.
    no_d = amputate(A, "D", "A_D_amputated")
    for c, k, x in lesions():
        r = run(no_d, A.from_x(x))
        record("C_LOCATOR_RESCUE", "D_amputated_no_injection", no_d, c, k, r, stuck_lesioned(c, k),
               "no detection: lesion persists with q=q*")
        r = run(no_d, A.from_x(x), writes={2: {f"e{k + 1}": 1}})
        record("C_LOCATOR_RESCUE", "D_amputated_inject_correct_E_once_t2", no_d, c, k, r,
               lambda s, r: s["outcome"] == "FULL_ORIGINAL_TARGET" and s["p_pulses"] == 1 and s["data_recovery_t"] == 4,
               "one E event suffices: one pulse, x repaired at t4")
        r = run(no_d, A.from_x(x), clamps=[(f"e{k + 1}", 1, 2)])
        record("C_LOCATOR_RESCUE", "D_amputated_hold_correct_E_from_t2", no_d, c, k, r,
               lambda s, r: s["outcome"] == "X_ORIGINAL_Q_NONBASELINE" and s["p_pulses"] == 1 and s["x_toggles"] == 1,
               "stuck-on E still yields exactly one toggle (edge detector)")
        r = run(A, A.from_x(x), writes={2: {f"e{k + 1}": 1}})
        record("C_LOCATOR_RESCUE", "intact_inject_correct_E_t2_SHAM_NOOP", A, c, k, r,
               lambda s, r: s["outcome"] == "FULL_ORIGINAL_TARGET" and s["full_recovery_t"] == 7,
               "E_k already 1 at t2: identical to natural")

    # D: wrong locator.
    for c, k, x in lesions():
        for j in range(4):
            if j == k:
                continue
            r = run(A, A.from_x(x), writes={2: {f"e{j + 1}": 1}})
            record("D_WRONG_LOCATOR", f"intact_inject_e{j + 1}_t2", A, c, k, r,
                   lambda s, r, c=c, j=j: (s["outcome"] == "FULL_ORIGINAL_TARGET"
                                            and bstr(A.x_of(r.states[4])) == bstr(tuple(b ^ (i == j) for i, b in enumerate(c)))),
                   "misrepair at t4 (x_j toggled), then endogenous detection repairs x_j")
            r = run(no_d, A.from_x(x), writes={2: {f"e{j + 1}": 1}})
            both = tuple(b ^ (i == j) ^ (i == k) for i, b in enumerate(c))
            record("D_WRONG_LOCATOR", f"D_amputated_inject_e{j + 1}_t2", no_d, c, k, r,
                   lambda s, r, both=both: s["outcome"] == "NON_CODEWORD_FIXED_POINT" and s["terminal_x"] == bstr(both),
                   "downstream executes the wrong location: permanent double error")
    for c in CODEWORDS:
        for j in range(4):
            r = run(A, A.from_x(c), writes={0: {f"e{j + 1}": 1}})
            record("D_WRONG_LOCATOR", f"target_inject_e{j + 1}_t0", A, c, j, r,
                   lambda s, r: s["outcome"] == "FULL_ORIGINAL_TARGET" and s["x_toggles"] == 2,
                   "healthy target: induced toggle is detected and undone (P-FULL E class)",
                   label=f"{bstr(c)}:no_lesion")

    # E: actuator ablation p ≡ 0.
    for i in range(1, 5):
        net = clamp_rule(A, f"p{i}", f"A_minus_p{i}")
        for c, k, x in lesions():
            r = run(net, A.from_x(x))
            if k + 1 == i:
                pred = lambda s, r, k=k: (s["outcome"] == "NON_CODEWORD_FIXED_POINT"
                                          and A.get(r.states[r.cycle_start], f"e{k + 1}") == 1
                                          and A.get(r.states[r.cycle_start], f"l{k + 1}") == 1)
                record("E_ACTUATOR_ABLATION", f"p{i}=0", net, c, k, r, pred,
                       "detection and localization intact (D, E_k, L_k on); no action: latched alarm")
            else:
                record("E_ACTUATOR_ABLATION", f"p{i}=0_SHAM_NOOP", net, c, k, r, full_ok, "P_i naturally 0: identical")

    # F: actuator rescue with localization amputated.
    no_e = amputate(A, "E", "A_E_amputated")
    for c, k, x in lesions():
        r = run(no_e, A.from_x(x))
        record("F_ACTUATOR_RESCUE", "E_amputated_no_injection", no_e, c, k, r,
               lambda s, r: s["outcome"] == "NON_CODEWORD_FIXED_POINT" and s["p_pulses"] == 0,
               "disagreement without localization: lesion persists")
        r = run(no_e, A.from_x(x), writes={3: {f"p{k + 1}": 1}})
        record("F_ACTUATOR_RESCUE", "E_amputated_inject_correct_P_t3", no_e, c, k, r,
               lambda s, r: s["outcome"] == "FULL_ORIGINAL_TARGET" and s["data_recovery_t"] == 4 and s["full_recovery_t"] == 5,
               "one externally chosen pulse suffices physically; the choice came from outside")
        for j in range(4):
            if j == k:
                continue
            r = run(no_e, A.from_x(x), writes={3: {f"p{j + 1}": 1}})
            both = tuple(b ^ (i == j) ^ (i == k) for i, b in enumerate(c))
            record("F_ACTUATOR_RESCUE", f"E_amputated_inject_wrong_p{j + 1}_t3", no_e, c, k, r,
                   lambda s, r, both=both: s["outcome"] == "NON_CODEWORD_FIXED_POINT" and s["terminal_x"] == bstr(both),
                   "the actuator has no direction of its own")
        r = run(A, A.from_x(x), writes={3: {f"p{k + 1}": 1}})
        record("F_ACTUATOR_RESCUE", "intact_inject_correct_P_t3_SHAM_NOOP", A, c, k, r,
               lambda s, r: s["outcome"] == "FULL_ORIGINAL_TARGET" and s["full_recovery_t"] == 7,
               "P_k already 1 at t3: identical")

    # G: temporal gating removed (functional equivalents, fan-in stays <=2).
    no_l = A.edited("A_P_equals_E_no_memory", {f"p{i}": Rule((f"e{i}",), COPY) for i in range(1, 5)})
    x_reads_e = direct_e_actuator()
    for net, arm in ((no_l, "P=E_level_no_L_memory"), (x_reads_e, "X_toggles_on_E_no_L_no_P")):
        for c, k, x in lesions():
            r = run(net, A.from_x(x))
            record("G_TEMPORAL_GATE_REMOVAL", arm, net, c, k, r,
                   lambda s, r: s["outcome"] != "FULL_ORIGINAL_TARGET",
                   "without the one-shot gate a level signal toggles repeatedly: no exact restoration predicted")
    write_csv("interventions_summary.csv", summaries)
    write_csv("interventions_traces.csv", traces)
    met = sum(row["prediction_met"] for row in summaries)
    shams = [row for row in summaries if "SHAM" in row["arm"]]
    log(f"  interventions: {met}/{len(summaries)} predictions met; shams identical to natural: "
        f"{sum(row['identical_to_natural'] for row in shams)}/{len(shams)}")
    families = Counter(row["family"] for row in summaries)
    return {
        "runs": len(summaries), "predictions_met": met,
        "shams": len(shams), "shams_identical_to_natural": sum(row["identical_to_natural"] for row in shams),
        "per_family": {f: {"runs": n, "met": sum(r["prediction_met"] for r in summaries if r["family"] == f)} for f, n in families.items()},
        "failed_predictions": [{k: row[k] for k in ("family", "arm", "lesion", "outcome", "prediction")} for row in summaries if not row["prediction_met"]],
    }, summaries


def direct_e_actuator():
    """x_i' = x_i XOR e_i; no L, no P (fan-in 2 kept)."""
    base = specimen_a()
    names = base.x_names + base.families["D"] + base.families["E"]
    rules = {n: base.rules[n] for n in base.families["D"] + base.families["E"]}
    for i in range(1, 5):
        rules[f"x{i}"] = Rule((f"x{i}", f"e{i}"), XOR)
    families = {"X": base.x_names, "D": base.families["D"], "E": base.families["E"], "L": (), "P": ()}
    return Net("A_X_toggles_on_E", names, rules, families, CODEWORDS)


# ====================================================================== §7
def section7_weight2():
    log("§7 boundary: the six weight-2 DATA states from q*")
    rows, traces = [], []
    law = True
    for code in range(16):
        x = tuple((code >> (3 - j)) & 1 for j in range(4))
        r = run(A, A.from_x(x))
        term = r.states[r.cycle_start]
        tri = int(sum(x[:3]) >= 2)
        law &= (A.x_of(term) == (tri,) * 4 and A.aux_zero(term) and r.cycle_length == 1)
        if sum(x) != 2:
            continue
        s1, s2 = r.states[1], r.states[2]
        classes = ({i + 1 for i in range(4) if x[i] == 1}, {i + 1 for i in range(4) if x[i] == 0})
        firing = [i for i in range(1, 5) if A.get(s2, f"e{i}")]
        rounds = sorted({t for t, n in pulse_events(A, r.states)})
        rows.append({
            "x": bstr(x), "pairing": f"{''.join(map(str, sorted(classes[0])))}|{''.join(map(str, sorted(classes[1])))}",
            "D_t1": A.pattern(s1, "D"), "E_t2": A.pattern(s2, "E"),
            "E_firing": ",".join(f"e{i}" for i in firing),
            "E_rule_check": all((set(WITNESS[i]) <= (classes[1] if x[i - 1] == 1 else classes[0])) == (i in firing) for i in range(1, 5)),
            "pulse_times": ",".join(map(str, rounds)), "pulse_rounds": len(rounds),
            "pulse_events": ";".join(f"{n}@t{t}" for t, n in pulse_events(A, r.states)),
            "terminal_x": bstr(A.x_of(term)), "terminal_q_star": A.aux_zero(term),
            "full_settle_t": r.cycle_start, "cycle_length": r.cycle_length,
            "triangle_majority_prediction": bstr((tri,) * 4),
            "unique_nearest_codeword": "none (tie at distance 2)",
        })
        traces.extend(trace_rows(f"W2|{bstr(x)}", A, r.states[:r.cycle_start + 1]))
    # symmetry: complementary weight-2 starts share q trajectories
    comp_ok = True
    for row in rows:
        x = tuple(int(b) for b in row["x"])
        cx = tuple(1 - b for b in x)
        a = run(A, A.from_x(x)).states
        b = run(A, A.from_x(cx)).states
        comp_ok &= [A.aux_of(s) for s in a] == [A.aux_of(s) for s in b]
    write_csv("weight2_boundary.csv", rows)
    write_csv("weight2_traces.csv", traces)
    result = {
        "weight2_states": len(rows),
        "all_reach_a_codeword_with_q_star": all(r["terminal_q_star"] and r["cycle_length"] == 1 for r in rows),
        "cycles_or_stalls": sum(r["cycle_length"] != 1 or not r["terminal_q_star"] for r in rows),
        "E_firing_rule_holds": all(r["E_rule_check"] for r in rows),
        "global_law_final_codeword_equals_majority_of_x1_x2_x3_for_all_16_x": law,
        "complementary_starts_share_q": comp_ok,
        "rounds_distribution": dict(Counter(r["pulse_rounds"] for r in rows)),
    }
    log(f"  weight-2: all to codeword {result['all_reach_a_codeword_with_q_star']}; triangle law on 16 x: {law}")
    return result, rows


# ====================================================================== §8
def section8_exact_vs_functional(census):
    log("§8 exact versus functional restoration")
    rows = []
    q_trajectories = set()
    for c, k, x in lesions():
        pre = A.from_x(c)
        r = run(A, A.from_x(x))
        st = r.states
        full_t = next(t for t, s in enumerate(st) if s == pre)
        functional_only = [t for t, s in enumerate(st) if A.x_of(s) == c and s != pre]
        q_trajectories.add(tuple(A.aux_of(s) for s in st[:full_t + 1]))
        rows.append({
            "lesion": lesion_id(c, k),
            "pre_lesion_full_state_x": bstr(c), "pre_lesion_q_nonbaseline": 0,
            "x_restored_t": next(t for t, s in enumerate(st) if A.x_of(s) == c),
            "full_state_equal_to_pre_lesion_t": full_t,
            "functional_only_window": ",".join(map(str, functional_only)),
            "bits_differing_from_pre_lesion_after_full_t": max(bin(s ^ pre).count("1") for s in st[full_t:]),
            "aux_pattern_t4": snapshot(A, st[4]),
        })
    write_csv("exact_vs_functional.csv", rows)
    result = {
        "all_lesions_return_to_identical_21_bit_state": all(r["bits_differing_from_pre_lesion_after_full_t"] == 0 for r in rows),
        "functional_restoration_t": sorted({r["x_restored_t"] for r in rows}),
        "exact_restoration_t": sorted({r["full_state_equal_to_pre_lesion_t"] for r in rows}),
        "distinct_internal_trajectories": len(q_trajectories),
        "lesions": len(rows),
        "residual_memory_after_exact_restoration": "none: the restored state equals the never-lesioned state bit for bit, and G is memoryless (Markov in the 21 bits)",
        "pfull_exact_returns": f"{census['single_coordinate_flips_returning_to_same_target']}/{census['single_coordinate_flips_total']}",
        "double_flip_exact_returns": f"{census['double_coordinate_flips_returning_to_same_target']}/{census['double_coordinate_flips_total']}",
    }
    log(f"  exact 21-bit return: {result['all_lesions_return_to_identical_21_bit_state']}; distinct internal trajectories: {len(q_trajectories)}")
    return result, rows


# ====================================================================== §9
def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def essential_vars(func, n=4):
    return tuple(j for j in range(n) if any(func(x) != func(x ^ (1 << (n - 1 - j))) for x in range(1 << n)))


def section9_compilation():
    log("§9 causal compilation of the non-extendable Phi")
    # F_t(x) = x-projection of G^t(x, q*)
    maps = {}
    for t in range(0, 12):
        maps[t] = {}
    for code in range(16):
        x = tuple((code >> (3 - j)) & 1 for j in range(4))
        s = A.from_x(x)
        for t in range(12):
            maps[t][code] = A.x_of(s)
            s = A.step(s)

    def as_int(bits):
        return int(bstr(bits), 2)

    def phi(code):
        w = bin(code).count("1")
        return 0 if w <= 1 else 15 if w >= 3 else None

    first_phi_t = next(t for t in range(12) if all(as_int(maps[t][code]) == phi(code) for code in range(16) if phi(code) is not None))
    f4_ess = {}
    maj3_identity = True
    for i in range(4):
        func = lambda code, i=i: maps[4][code][i]
        f4_ess[f"x{i + 1}(4)"] = tuple(f"x{j + 1}" for j in essential_vars(func))
        a, b = WITNESS[i + 1]
        for code in range(16):
            x = tuple((code >> (3 - j)) & 1 for j in range(4))
            maj = int(x[i] + x[a - 1] + x[b - 1] >= 2)
            maj3_identity &= maps[4][code][i] == maj

    # Direct (one-step, X-only) extensions of Phi_i on R_X.
    rx = [code for code in range(16) if phi(code) is not None]
    by_arity = Counter()
    for table in range(1 << 16):
        func = lambda code, table=table: (table >> code) & 1
        for i in range(4):
            if all(func(code) == ((phi(code) >> (3 - i)) & 1) for code in rx):
                by_arity[(i, len(essential_vars(func)))] += 1
    min_arity = {f"x{i + 1}": min(ar for (j, ar) in by_arity if j == i) for i in range(4)}
    extensions_le2 = sum(v for (i, ar), v in by_arity.items() if ar <= 2)
    # X-only rules with both codewords fixed and fan-in <= 2 are monotone.
    fixed_codeword_rules = []
    for table in range(1 << 16):
        func = lambda code, table=table: (table >> code) & 1
        if func(0) == 0 and func(15) == 1 and len(essential_vars(func)) <= 2:
            fixed_codeword_rules.append(table)
    monotone = all(all(((t >> a) & 1) <= ((t >> b) & 1) for a in range(16) for b in range(16) if a & b == a)
                   for t in fixed_codeword_rules)

    log("  running DISCOVERY-02/03 instruments (read-only, print-free calls)")
    d02 = load_module(REPO / "experiments" / "primitivo_discovery02" / "discovery02.py", "discovery02_autopsy")
    d02.validate()
    d02_l2, d02_l1 = d02.all_candidates(1), d02.all_candidates(2)
    d03 = load_module(REPO / "experiments" / "primitivo_discovery03" / "discovery03.py", "discovery03_autopsy")
    d03.validate()
    d03_counts = {}
    for cls in (d03.C4, d03.C3):
        for dmax in (1, 2):
            d03_counts[f"{cls.name}_dmax{dmax}"] = len(d03.search(cls, dmax))
    allowed_c4 = [len(d03.allowed_functions(d03.C4, i, 2)) for i in range(4)]
    log(f"  DISCOVERY-02 n=3 candidates d<=1: {len(d02_l2)}, d<=2: {len(d02_l1)}; DISCOVERY-03: {d03_counts}")

    # Effective edges along the natural P-DATA trajectories (frozen helper).
    effective = 0
    for c, k, x in lesions():
        r = run(A, A.from_x(x))
        for s in r.states[:r.cycle_start]:
            effective += len(effective_edges(tuple((s >> i) & 1 for i in range(21))))
    result = {
        "first_t_with_x_equal_Phi_on_R_X": first_phi_t,
        "F4_essential_inputs": f4_ess,
        "F4_equals_maj3_of_x_i_and_its_two_witnesses_on_all_16_x": maj3_identity,
        "one_step_extensions_of_Phi_by_coordinate_and_arity": {f"x{i + 1}_arity{ar}": v for (i, ar), v in sorted(by_arity.items())},
        "extensions_with_essential_arity_le_2": extensions_le2,
        "minimum_essential_arity_to_extend_Phi_i": min_arity,
        "x_only_rules_fixing_both_codewords_with_fan_in_le_2": len(fixed_codeword_rules),
        "those_rules_are_all_monotone": monotone,
        "discovery03_allowed_functions_C4_dmax2_per_coordinate": allowed_c4,
        "discovery02_n3_candidates": {"dmax1": len(d02_l2), "dmax2": len(d02_l1)},
        "discovery03_candidates": d03_counts,
        "auxiliaries": {"D": 5, "E": 4, "L": 4, "P": 4, "total": 17},
        "causal_depth_steps_x_to_x": 4,
        "gate_layers": ["XOR (D, fan-in 2)", "AND (E, fan-in 2)", "AND-NOT with 1-step memory (P, fan-in 2)", "XOR toggle (X, fan-in 2)"],
        "static_edges": sum(len(r.parents) for r in A.rules.values()),
        "effective_edges_over_8_natural_trajectories": effective,
        "temporal_phases": {"detection": "t1 (D)", "localization": "t2 (E)", "one-shot gating": "t3 (L, P)",
                            "actuation": "t3->t4 (X)", "drain": "t5 (D), t6 (E), t7 (L)"},
    }
    write_json("compilation.json", result)
    log(f"  x = Phi on R_X from t={first_phi_t}; F4 = maj3(x_i, witnesses): {maj3_identity}; arity<=2 extensions: {extensions_le2}")
    return result


# ====================================================================== §10
def edge_constant(net, child, parent, value, name):
    rule = net.rules[child]
    if len(rule.parents) == 1:
        return net.edited(name, {child: Rule((), (rule.table[value],))})
    j = rule.parents.index(parent)
    other = rule.parents[1 - j]
    table = []
    for o in (0, 1):
        bits = [0, 0]
        bits[j] = value
        bits[1 - j] = o
        table.append(rule.table[bits[0] | (bits[1] << 1)])
    return net.edited(name, {child: Rule((other,), tuple(table))})


def merged_variants():
    base = specimen_a()
    out = []
    # D+E merged: E reads x directly (fan-in 3); D kept but unused.
    rules = {}
    for i in range(1, 5):
        a, b = WITNESS[i]
        tab = tuple(int(((code >> 0) & 1) != ((code >> 1) & 1) and ((code >> 0) & 1) != ((code >> 2) & 1)) for code in range(8))
        rules[f"e{i}"] = WideRule((f"x{i}", f"x{a}", f"x{b}"), tab)
    out.append(("MERGE_D_INTO_E_fanin3", rules))
    # P+X merged: x reads e and l (fan-in 3).
    rules = {}
    for i in range(1, 5):
        tab = tuple(((code & 1) ^ (((code >> 1) & 1) & (1 - ((code >> 2) & 1)))) for code in range(8))
        rules[f"x{i}"] = WideRule((f"x{i}", f"e{i}", f"l{i}"), tab)
    out.append(("MERGE_P_INTO_X_fanin3", rules))
    nets = []
    for name, new_rules in out:
        allr = dict(base.rules)
        allr.update(new_rules)
        nets.append(WideNet(name, base.names, allr, base.families, CODEWORDS))
    return nets


def section10_minimality():
    log("§10 minimality: ablations, gate replacements, merges, witness family")
    rows = []

    def add(kind, component, net):
        m = battery(net)
        row = {"kind": kind, "component": component, **public(m), "passes_battery": battery_passes(m)}
        rows.append(row)
        return m

    base_metrics = add("BASELINE", "A", A)
    for n in A.aux_names:
        add("AUX_CLAMPED_0", n, clamp_rule(A, n, f"A_minus_{n}"))
    for child in A.names:
        for parent in A.rules[child].parents:
            for value in (0, 1):
                add(f"EDGE_CONST_{value}", f"{parent}->{child}", edge_constant(A, child, parent, value, f"A_{parent}->{child}={value}"))
    for child in A.names:
        rule = A.rules[child]
        alternatives = TWO_INPUT_TABLES if len(rule.parents) == 2 else ((0, 0), (0, 1), (1, 0), (1, 1))
        for table in alternatives:
            if table == rule.table:
                continue
            add("GATE_REPLACED", f"{child}:{gate_name(rule.table)}->{gate_name(table)}",
                A.edited(f"A_{child}_{gate_name(table)}", {child: Rule(rule.parents, table)}))
    add("STRUCTURAL", "P=E (no one-shot memory)",
        A.edited("A_P_equals_E", {f"p{i}": Rule((f"e{i}",), COPY) for i in range(1, 5)}))
    add("STRUCTURAL", "X toggles on E (no L, no P)", direct_e_actuator())
    add("STRUCTURAL", "P = E AND NOT P (own output as memory, no L)",
        A.edited("A_P_self_memory", {f"p{i}": Rule((f"e{i}", f"p{i}"), A_AND_NOT_B) for i in range(1, 5)}))
    for net in merged_variants():
        add("MERGE_VIOLATES_FAN_IN", net.name, net)
    write_csv("ablations.csv", rows)

    witness_rows = []
    for wit in all_witness_assignments(4):
        label = ";".join(f"{i}:{a}{b}" for i, (a, b) in sorted(wit.items()))
        net = witness_net(4, wit, name=f"W[{label}]")
        m = battery(net)
        witness_rows.append({
            "witnesses": label, "is_specimen_A": wit == SPECIMEN_A_WITNESSES,
            "n_D": len(net.families["D"]), "D": ",".join(net.families["D"]),
            **{k: v for k, v in public(m).items() if k not in ("variant",)},
            "passes_battery": battery_passes(m),
            "weight2_resolved": m["half_weight_to_codeword"],
        })
    write_csv("witness_family.csv", witness_rows)

    def necessary(kind_prefix, component_filter):
        chosen = [r for r in rows if r["kind"].startswith(kind_prefix) and component_filter(r["component"])]
        return all(not r["passes_battery"] for r in chosen), len(chosen)

    summary = {
        "variants_evaluated": len(rows),
        "baseline_passes": battery_passes(base_metrics),
        "baseline_qstar_to_codeword": f"{base_metrics['qstar_starts_to_codeword']}/{base_metrics['qstar_total']}",
        "every_aux_individually_necessary": all(not r["passes_battery"] for r in rows if r["kind"] == "AUX_CLAMPED_0"),
        "aux_clamps_that_still_pass": [r["component"] for r in rows if r["kind"] == "AUX_CLAMPED_0" and r["passes_battery"]],
        "edge_substitutions_that_still_pass": [f"{r['kind']}:{r['component']}" for r in rows if r["kind"].startswith("EDGE_CONST") and r["passes_battery"]],
        "gate_replacements_that_still_pass": [r["component"] for r in rows if r["kind"] == "GATE_REPLACED" and r["passes_battery"]],
        "structural_variants": {r["component"]: {"passes": r["passes_battery"], "pdata": f"{r['pdata_full_recovery']}/{r['pdata_total']}",
                                                 "cycles": r["cycles"], "failed": r["failed_lesions"]}
                                for r in rows if r["kind"] in ("STRUCTURAL", "MERGE_VIOLATES_FAN_IN")},
        "witness_assignments": len(witness_rows),
        "witness_assignments_passing": sum(r["passes_battery"] for r in witness_rows),
        "min_D_among_passing": min(r["n_D"] for r in witness_rows if r["passes_battery"]),
        "passing_by_n_D": dict(Counter(r["n_D"] for r in witness_rows if r["passes_battery"])),
        "passing_with_all_weight2_resolved_by_n_D": dict(Counter(r["n_D"] for r in witness_rows if r["passes_battery"] and r["weight2_resolved"] == 6)),
        "specimen_A_row": next({k: r[k] for k in ("n_D", "passes_battery", "weight2_resolved", "pfull_full_recovery")} for r in witness_rows if r["is_specimen_A"]),
    }
    log(f"  {len(rows)} variants; passing aux clamps: {summary['aux_clamps_that_still_pass']}; "
        f"witness family passing: {summary['witness_assignments_passing']}/81, min D {summary['min_D_among_passing']}")
    return summary, rows, witness_rows


# ====================================================================== §11
def section11_law(theory_rows):
    log("§11 equation-level law")
    ok = True
    for c, k, x in lesions():
        r = run(A, A.from_x(x))
        st = r.states
        eps = locator(syndrome(x))
        err = tuple(a ^ b for a, b in zip(x, c))
        ok &= (tuple(int(b) for b in A.pattern(st[1], "D")) == syndrome(x))           # D(1) = H x(0)
        ok &= (tuple(int(b) for b in A.pattern(st[2], "E")) == eps == err)             # E(2) = eps(H x(0)) = error
        ok &= (tuple(int(b) for b in A.pattern(st[3], "P")) == eps)                    # P(3) = E(2) & ~E(1)
        ok &= (A.x_of(st[4]) == tuple(a ^ b for a, b in zip(x, eps)) == c)            # x(4) = x(0) ^ eps
    return {"law_verified_on_8_lesions": ok}


# ====================================================================== main
def main():
    OUT.mkdir(exist_ok=True)
    succ, audit, census, fixed_rows = section0_equation_audit()
    ledger = section1_ledger()
    theory, theory_rows = section2_code_theory()
    locator_result, lesion_rows = section3_lesion_table()
    direction, mi_rows, toggles = section4_direction(audit)
    temporal, blocks = section5_temporal()
    interventions, intervention_rows = section6_interventions()
    weight2, weight2_rows = section7_weight2()
    exactness, exact_rows = section8_exact_vs_functional(census)
    compilation = section9_compilation()
    minimality, ablation_rows, witness_rows = section10_minimality()
    law = section11_law(theory_rows)

    hcore_checks = {
        "code_theory_A_to_D": all(theory[k] for k in ("A_RX_equals_union_of_radius1_balls", "B_unique_nearest_codeword_on_RX",
                                                      "C_weight2_is_exact_tie_set", "D_Phi_equals_nearest_codeword_decoding")),
        "locator_exact_one_E_is_damaged_bit_8_of_8": locator_result["lesions_with_exactly_one_E_equal_to_damaged_bit"] == 8,
        "locator_exact_on_R_X": locator_result["locator_exact_on_all_R_X_states"],
        "q_carries_no_target_information": direction["complementary_lesions_share_q_trajectory"] and direction["max_MI_q_codeword_bits"] == 0,
        "no_target_variable_or_oracle": audit["observed_equals_declared_parents"] and audit["complement_equivariant_all_states"],
        "one_shot_rising_edge": temporal["all_E_blocks_contiguous_single_rising_edge"]
                                and temporal["P_equals_rising_edge_of_E"].split("/")[0] == temporal["P_equals_rising_edge_of_E"].split("/")[1],
        "all_intervention_predictions_met": interventions["predictions_met"] == interventions["runs"],
        "all_shams_identical_to_natural": interventions["shams_identical_to_natural"] == interventions["shams"],
        "F4_is_maj3_per_coordinate": compilation["F4_equals_maj3_of_x_i_and_its_two_witnesses_on_all_16_x"],
        "no_fan_in_2_direct_extension": compilation["extensions_with_essential_arity_le_2"] == 0,
        "exact_global_restoration": exactness["all_lesions_return_to_identical_21_bit_state"],
        "law_verified": law["law_verified_on_8_lesions"],
    }
    verdict = "CAUSAL_MECHANISM_IDENTIFIED" if all(hcore_checks.values()) else "CAUSAL_MECHANISM_PARTIAL"
    payload = {
        "instrument": "run_autopsy01_mechanism.py",
        "basis_commit": "f0fdf00c6661b466ffbf1806ab13afb4be616d13",
        "verdict": verdict,
        "hcore_checks": hcore_checks,
        "equation_audit": audit,
        "ledger_reproduction": ledger,
        "code_theory": theory,
        "locator": locator_result,
        "direction": direction,
        "temporal": temporal,
        "interventions": interventions,
        "weight2": weight2,
        "exact_vs_functional": exactness,
        "compilation": compilation,
        "minimality": minimality,
        "law": law,
        "state_space": {k: census[k] for k in census if k != "attractors"} | {
            "attractor_kinds": dict(Counter(a["kind"] for a in census["attractors"])),
            "target_basin_sizes": [a["basin_size"] for a in census["attractors"] if a["kind"] == "TARGET"],
            "latched_alarm_basin_sizes": sorted(a["basin_size"] for a in census["attractors"] if a["kind"] == "LATCHED_ALARM_FIXED_POINT"),
            "cycle_basin_sizes": sorted(a["basin_size"] for a in census["attractors"] if a["kind"].startswith("CYCLE")),
            "states_reaching_a_target": sum(a["basin_size"] for a in census["attractors"] if a["kind"] == "TARGET"),
            "states_reaching_a_cycle": sum(a["basin_size"] for a in census["attractors"] if a["kind"].startswith("CYCLE")),
            "states_reaching_a_latched_alarm": sum(a["basin_size"] for a in census["attractors"] if a["kind"] == "LATCHED_ALARM_FIXED_POINT"),
        },
        "log": LOG,
    }
    write_json("verdicts.json", payload)
    log(f"VERDICT: {verdict}")
    for key, value in hcore_checks.items():
        log(f"  {key}: {value}")


if __name__ == "__main__":
    main()
