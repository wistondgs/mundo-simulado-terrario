"""ETP-AUTOPSY-01 errata check: the numbers behind seven corrections.

The first version of ETP_AUTOPSY_01_CAUSAL_MECHANISM.md stated seven things
more broadly than its evidence (§6, §8 arm C, §11 three times, §16 twice), and
one of them was copied into the INHIBITORS field of the candidate record.
This script recomputes, read-only, every number the corrected text uses: from
the specimen-A network (verified equal to the frozen step by
run_autopsy01_mechanism.py), from the committed artifacts, and from the
DISCOVERY-03 instrument.  It asserts each expected value and writes
artifacts/autopsy01_errata_check.json.  It runs no new experiment and
regenerates no committed artifact.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import sys
from collections import Counter
from itertools import combinations
from pathlib import Path

from autopsy01_core import run, specimen_a

ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[2]
OUT = ROOT / "artifacts"
PREFIX = "autopsy01_"

A = specimen_a()
CODEWORDS = ((0, 0, 0, 0), (1, 1, 1, 1))
TRIANGLE = ("1", "2", "3")


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def read_json(name):
    return json.loads((OUT / (PREFIX + name)).read_text(encoding="utf-8"))


def read_csv(name):
    with (OUT / (PREFIX + name)).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def bstr(bits):
    return "".join(map(str, bits))


def lesions():
    for c in CODEWORDS:
        for k in range(4):
            x = list(c)
            x[k] ^= 1
            yield c, k, tuple(x)


def lesion_id(c, k):
    return f"{bstr(c)}:x{k + 1}"


def one_hot(k, n=4):
    return "".join("1" if i == k else "0" for i in range(n))


# ------------------------------------------------------------ §6 E timeline
def check_e_timeline():
    """At most one E per step, always e_k: high t2..t5, none at t0, t1, t6, t7."""
    rows = {}
    for c, k, x in lesions():
        s = A.from_x(x)
        by_t, only_e_k = [], True
        for _ in range(9):
            on = [n for n in A.families["E"] if A.get(s, n)]
            only_e_k &= on in ([], [f"e{k + 1}"])
            by_t.append("1" if on else "0")
            s = A.step(s)
        rows[lesion_id(c, k)] = {"any_E_on_t0_to_t8": "".join(by_t),
                                 "at_most_one_E_per_step_and_only_e_k": only_e_k}
    assert all(r == {"any_E_on_t0_to_t8": "001111000", "at_most_one_E_per_step_and_only_e_k": True}
               for r in rows.values()), rows
    return rows


# ------------------------------------------------------ §8 arm C, E held on
def check_held_e_arm():
    """x restored with one toggle; E_k and L_k stay 1 under the clamp; not a latched alarm."""
    arm = "D_amputated_hold_correct_E_from_t2"
    summary = {r["lesion"]: r for r in read_csv("interventions_summary.csv")
               if r["family"] == "C_LOCATOR_RESCUE" and r["arm"] == arm}
    traces = {}
    for r in read_csv("interventions_traces.csv"):
        family, run_arm, lesion = r["run_id"].split("|")
        if family == "C_LOCATOR_RESCUE" and run_arm == arm:
            if lesion not in traces or int(r["t"]) > int(traces[lesion]["t"]):
                traces[lesion] = r
    rows = {}
    for c, k, _ in lesions():
        lid = lesion_id(c, k)
        s, last = summary[lid], traces[lid]
        rows[lid] = {
            "outcome": s["outcome"], "x_toggles": int(s["x_toggles"]), "p_pulses": int(s["p_pulses"]),
            "terminal_t": int(last["t"]), "terminal_x": last["x"], "terminal_D": last["D"],
            "terminal_E": last["E"], "terminal_L": last["L"], "terminal_P": last["P"],
        }
        assert rows[lid] == {
            "outcome": "X_ORIGINAL_Q_NONBASELINE", "x_toggles": 1, "p_pulses": 1,
            "terminal_t": 4, "terminal_x": bstr(c), "terminal_D": "00000",
            "terminal_E": one_hot(k), "terminal_L": one_hot(k), "terminal_P": "0000",
        }, (lid, rows[lid])
    return rows


# ------------------------------------------------- §11 extensions of Phi_i
def phi(x):
    w = sum(x)
    return None if w == 2 else (CODEWORDS[0] if w < 2 else CODEWORDS[1])


def check_extensions():
    """64 extensions per coordinate: 4 of arity 3 (the four triple majorities), 60 of arity 4."""
    comp = read_json("compilation.json")
    by_arity = comp["one_step_extensions_of_Phi_by_coordinate_and_arity"]
    expected = {f"x{i}_arity{a}": n for i in range(1, 5) for a, n in ((3, 4), (4, 60))}
    assert by_arity == expected, by_arity
    assert comp["extensions_with_essential_arity_le_2"] == 0
    cube = [tuple((v >> (3 - j)) & 1 for j in range(4)) for v in range(16)]
    majorities = {}
    for i in range(4):
        tables = set()
        for triple in combinations(range(4), 3):
            table = tuple(int(sum(x[j] for j in triple) >= 2) for x in cube)
            assert all(table[v] == phi(x)[i] for v, x in enumerate(cube) if phi(x) is not None), (i, triple)
            tables.add(table)
        majorities[f"x{i + 1}"] = len(tables)
    assert all(n == 4 for n in majorities.values()), majorities
    return {"by_coordinate_and_arity": by_arity,
            "extensions_per_coordinate": 2 ** sum(1 for x in cube if phi(x) is None),
            "distinct_triple_majorities_extending_Phi_i": majorities}


# ------------------------------------------------------- §11 X-only rules
def check_x_only_rules():
    """With A's codes every X-only fan-in-2 rule is monotone; with 0000/1110 some are not, and still 0 candidates."""
    d03 = load_module(REPO / "experiments" / "primitivo_discovery03" / "discovery03.py", "discovery03_errata")
    d03.validate()

    def monotone(table):
        return all(d03.output(table, a) <= d03.output(table, b)
                   for a in range(16) for b in range(16) if a & b == a)

    out = {}
    for cls in (d03.C4, d03.C3):
        per = []
        for i in range(4):
            tables = d03.allowed_functions(cls, i, 2)
            per.append({"rules": len(tables), "non_monotone": sum(not monotone(t) for t in tables)})
        out[cls.name] = {"centres": [bstr(d03.bits(0)), bstr(d03.bits(cls.one))], "dmax2_per_coordinate": per}
    assert out["DISTANCE_4"]["centres"] == ["0000", "1111"]
    assert out["DISTANCE_4"]["dmax2_per_coordinate"] == [{"rules": 16, "non_monotone": 0}] * 4
    assert out["DISTANCE_3"]["centres"] == ["0000", "1110"]
    assert out["DISTANCE_3"]["dmax2_per_coordinate"] == (
        [{"rules": 18, "non_monotone": 6}] * 3 + [{"rules": 17, "non_monotone": 12}])
    xor_rules = {}
    for j in range(3):
        table = sum((d03.bits(v)[j] ^ d03.bits(v)[3]) << v for v in range(16))
        xor_rules[f"x{j + 1}' = x{j + 1} XOR x4"] = table in d03.allowed_functions(d03.C3, j, 2)
    assert all(xor_rules.values()), xor_rules
    candidates = read_json("compilation.json")["discovery03_candidates"]
    assert all(v == 0 for v in candidates.values()), candidates
    out["xor_rules_fixing_both_C3_centres"] = xor_rules
    out["discovery03_candidates"] = candidates
    return out


# ---------------------------------------------------- §16 double flips
def check_double_flips():
    """Per target 183/210 return, 9 opposite, 18 into a 12-cycle; the cycling ones are exactly
    the mixed-family pairs (x+e, x+p, e+p) on two distinct triangle coordinates."""
    per_target, mixtures, non_returning = {}, Counter(), Counter()
    for c in CODEWORDS:
        target = A.from_x(c)
        opposite = A.from_x(tuple(1 - b for b in c))
        counts = Counter()
        for a, b in combinations(A.names, 2):
            r = run(A, A.flip(A.flip(target, a), b))
            end = r.states[r.cycle_start]
            if r.cycle_length == 1 and end in (target, opposite):
                outcome = "RETURN" if end == target else "OPPOSITE_CODEWORD"
            else:
                outcome = f"CYCLE_{r.cycle_length}" if r.cycle_length > 1 else "OTHER_FIXED_POINT"
            counts[outcome] += 1
            fa, fb = a[0], b[0]
            if {fa, fb} in ({"x", "e"}, {"x", "p"}, {"e", "p"}):
                if a[1:] == b[1:]:
                    kind = "same_coordinate"
                elif "4" in (a[1:], b[1:]):
                    kind = "touches_coordinate_4"
                else:
                    kind = "two_distinct_triangle_coordinates"
                mixtures[f"{kind}:{outcome}"] += 1
            if outcome != "RETURN":
                same = fa == fb and a[1:] in TRIANGLE and b[1:] in TRIANGLE
                non_returning[f"{outcome}:{'same_family_inside_triangle' if same else fa + '+' + fb}"] += 1
        per_target[bstr(c)] = dict(sorted(counts.items()))
    census = read_json("state_space_census.json")
    total = Counter()
    for counts in per_target.values():
        total.update(counts)
    assert all(v == {"CYCLE_12": 18, "OPPOSITE_CODEWORD": 9, "RETURN": 183} for v in per_target.values()), per_target
    assert total["RETURN"] == census["double_coordinate_flips_returning_to_same_target"] == 366
    assert sum(total.values()) == census["double_coordinate_flips_total"] == 420
    assert dict(mixtures) == {"same_coordinate:RETURN": 24, "touches_coordinate_4:RETURN": 36,
                              "two_distinct_triangle_coordinates:CYCLE_12": 36}, mixtures
    assert dict(non_returning) == {"OPPOSITE_CODEWORD:same_family_inside_triangle": 18,
                                   "CYCLE_12:x+e": 12, "CYCLE_12:x+p": 12, "CYCLE_12:e+p": 12}, non_returning
    return {"per_target": per_target, "total": dict(sorted(total.items())),
            "mixed_family_pairs_x_e_p": dict(sorted(mixtures.items())),
            "non_returning_by_family": dict(sorted(non_returning.items()))}


# ------------------------------------------------------- §16 12-cycles
def check_cycles():
    """All six: 6 x-changes per period (2 move two bits), 2 toggles per coordinate, 8 P pulses.
    Two (basin 235,008) change x every 2 steps; four (199,680) alternate gaps of 1 and 3."""
    rows = []
    for att in read_json("state_space_census.json")["attractors"]:
        if att["kind"] != "CYCLE_12":
            continue
        xs = [s["x"] for s in att["states"]]
        n = len(xs)
        changes = [t for t in range(n) if xs[t] != xs[(t + 1) % n]]
        moved = [sum(a != b for a, b in zip(xs[t], xs[(t + 1) % n])) for t in changes]
        toggles = [sum(xs[t][i] != xs[(t + 1) % n][i] for t in changes) for i in range(4)]
        gaps = sorted({(changes[(j + 1) % len(changes)] - changes[j]) % n for j in range(len(changes))})
        rows.append({"attractor_id": att["attractor_id"], "basin_size": att["basin_size"],
                     "x_changes_per_period": len(changes), "two_bit_changes": moved.count(2),
                     "toggles_per_coordinate": toggles,
                     "P_pulses_per_period": sum(s["P"].count("1") for s in att["states"]),
                     "gaps_between_x_changes": gaps})
    assert len(rows) == 6
    for r in rows:
        assert (r["x_changes_per_period"], r["two_bit_changes"], r["toggles_per_coordinate"],
                r["P_pulses_per_period"]) == (6, 2, [2, 2, 2, 2], 8), r
        assert (r["basin_size"], r["gaps_between_x_changes"]) in ((235008, [2]), (199680, [1, 3])), r
    assert Counter(r["basin_size"] for r in rows) == {235008: 2, 199680: 4}
    return rows


def main():
    result = {
        "instrument": "run_autopsy01_errata_check.py",
        "scope": "read-only recomputation of the numbers used by the seven corrections",
        "s6_E_timeline": check_e_timeline(),
        "s8_C_held_E_arm": check_held_e_arm(),
        "s11_extensions_of_Phi": check_extensions(),
        "s11_x_only_rules": check_x_only_rules(),
        "s16_double_flips": check_double_flips(),
        "s16_twelve_cycles": check_cycles(),
        "all_assertions_passed": True,
    }
    (OUT / (PREFIX + "errata_check.json")).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print("errata check: all assertions passed")


if __name__ == "__main__":
    main()
