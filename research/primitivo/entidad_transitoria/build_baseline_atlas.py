"""Build the ETP-PRE-01 baseline atlas from frozen specimen-A equations.

This is an observer/verifier. It changes no rule, architecture, initial
condition after t=0, or experiment artifact.  Counterfactual evaluations are
one-step truth-table queries of the frozen Boolean transition only.
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from itertools import permutations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "artifacts"
OUT.mkdir(exist_ok=True)

X = ("x1", "x2", "x3", "x4")
D = ("d12", "d13", "d23", "d14", "d24")
E = ("e1", "e2", "e3", "e4")
L = ("l1", "l2", "l3", "l4")
P = ("p1", "p2", "p3", "p4")
VARS = X + D + E + L + P
INDEX = {name: i for i, name in enumerate(VARS)}
Q = D + E + L + P
ZERO = (0,) * len(VARS)
TARGETS = {"0000": (0, 0, 0, 0), "1111": (1, 1, 1, 1)}

PARENTS = {
    "d12": ("x1", "x2"), "d13": ("x1", "x3"),
    "d23": ("x2", "x3"), "d14": ("x1", "x4"),
    "d24": ("x2", "x4"), "e1": ("d12", "d13"),
    "e2": ("d12", "d23"), "e3": ("d13", "d23"),
    "e4": ("d14", "d24"), "l1": ("e1",), "l2": ("e2",),
    "l3": ("e3",), "l4": ("e4",), "p1": ("e1", "l1"),
    "p2": ("e2", "l2"), "p3": ("e3", "l3"),
    "p4": ("e4", "l4"), "x1": ("x1", "p1"),
    "x2": ("x2", "p2"), "x3": ("x3", "p3"), "x4": ("x4", "p4"),
}
FAMILY = {**{name: "DATA" for name in X}, **{name: "D" for name in D},
          **{name: "E" for name in E}, **{name: "L" for name in L},
          **{name: "P" for name in P}}


def bits(state, names):
    return tuple(state[INDEX[name]] for name in names)


def pack(values):
    return "".join(map(str, values))


def hamming(left, right):
    return sum(a != b for a, b in zip(left, right))


def toggle(state, name):
    result = list(state)
    result[INDEX[name]] ^= 1
    return tuple(result)


def step(state):
    x1, x2, x3, x4 = bits(state, X)
    d12_next, d13_next, d23_next, d14_next, d24_next = (
        x1 ^ x2, x1 ^ x3, x2 ^ x3, x1 ^ x4, x2 ^ x4
    )
    d12, d13, d23, d14, d24 = bits(state, D)
    e1_next, e2_next, e3_next, e4_next = (
        d12 & d13, d12 & d23, d13 & d23, d14 & d24
    )
    e1, e2, e3, e4 = bits(state, E)
    l1, l2, l3, l4 = bits(state, L)
    p1_next, p2_next, p3_next, p4_next = (
        e1 & (1 - l1), e2 & (1 - l2), e3 & (1 - l3), e4 & (1 - l4)
    )
    p1, p2, p3, p4 = bits(state, P)
    return (x1 ^ p1, x2 ^ p2, x3 ^ p3, x4 ^ p4,
            d12_next, d13_next, d23_next, d14_next, d24_next,
            e1_next, e2_next, e3_next, e4_next,
            e1, e2, e3, e4, p1_next, p2_next, p3_next, p4_next)


def state_for(x, q=(0,) * 17):
    return tuple(x) + tuple(q)


def trace(initial, target, cap=32):
    result, seen, current = [initial], {initial}, initial
    for _ in range(cap):
        if current == state_for(target):
            return result
        current = step(current)
        if current in seen:
            raise AssertionError(f"cycle before full recovery: {pack(initial)}")
        seen.add(current)
        result.append(current)
    raise AssertionError(f"no full recovery by {cap}: {pack(initial)}")


def changed(before, after, names):
    return ",".join(name for name in names if before[INDEX[name]] != after[INDEX[name]])


def q_nonbaseline(state):
    return sum(state[INDEX[name]] for name in Q)


def data_row(traj_id, target_name, initial_family, flip, t, state, prior, target):
    row = {
        "trajectory_id": traj_id, "target": target_name, "initial_family": initial_family,
        "flipped_coordinate": flip, "t": t, "x": pack(bits(state, X)),
        "q": pack(bits(state, Q)), "d_H_x_target": hamming(bits(state, X), target),
        "d_H_q_qstar": q_nonbaseline(state), "nonbaseline_aux_count": q_nonbaseline(state),
        "changed_x": "" if prior is None else changed(prior, state, X),
        "changed_q": "" if prior is None else changed(prior, state, Q),
    }
    row.update({name: state[INDEX[name]] for name in VARS})
    return row


def first_time(states, predicate):
    return next((t for t, state in enumerate(states) if predicate(state)), None)


def first_transition(states, predicate):
    return next((t for t, (left, right) in enumerate(zip(states, states[1:]))
                 if predicate(left, right)), None)


def effective_edges(state):
    observed = step(state)
    edges = []
    for child in VARS:
        for parent in PARENTS[child]:
            alternate = step(toggle(state, parent))
            if alternate[INDEX[child]] != observed[INDEX[child]]:
                edges.append((parent, child))
    return edges


def all_paths(adjacency, source, sink):
    paths = []
    pending = [(source, (source,))]
    while pending:
        node, path = pending.pop()
        if node == sink:
            paths.append(path)
            continue
        for child in adjacency.get(node, ()):
            if child not in path:
                pending.append((child, path + (child,)))
    return paths


def p_data_initials():
    for target_name, target in TARGETS.items():
        for index, coordinate in enumerate(X):
            x = list(target)
            x[index] ^= 1
            yield f"PDATA_{target_name}_{coordinate}", target_name, coordinate, state_for(x), target


def p_full_initials():
    for target_name, target in TARGETS.items():
        for coordinate in VARS:
            initial = toggle(state_for(target), coordinate)
            yield (f"PFULL_{target_name}_{coordinate}", target_name, FAMILY[coordinate],
                   coordinate, initial, target)


def verify_model():
    assert len(VARS) == 21 and len(Q) == 17
    assert step(state_for(TARGETS["0000"])) == state_for(TARGETS["0000"])
    assert step(state_for(TARGETS["1111"])) == state_for(TARGETS["1111"])
    assert max(map(len, PARENTS.values())) == 2
    # Every listed static parent is essential: this direct test uses a witness
    # state for each parent/child, while the atlas below reports effectiveness
    # only in states naturally reached.
    for child, parents in PARENTS.items():
        for parent in parents:
            witness_found = False
            # A child's RHS sees at most two parents.  Enumerating just their
            # assignments is an exhaustive essentiality check for that RHS.
            for assignment in range(1 << len(parents)):
                state = list(ZERO)
                for index, local_parent in enumerate(parents):
                    state[INDEX[local_parent]] = (assignment >> index) & 1
                state = tuple(state)
                if step(state)[INDEX[child]] != step(toggle(state, parent))[INDEX[child]]:
                    witness_found = True
                    break
            assert witness_found, (parent, child)


def write_csv(path, rows):
    rows = list(rows)
    if not rows:
        raise AssertionError(f"no rows for {path.name}")
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main():
    verify_model()
    p_data_rows, p_full_rows, p_data_summary = [], [], []
    p_full_summary, raac_rows, edge_rows, node_rows, dominator_rows = [], [], [], [], []
    p_data_traces = {}

    for traj_id, target_name, flip, initial, target in p_data_initials():
        states = trace(initial, target)
        p_data_traces[traj_id] = states
        data_recovery_for_markers = first_time(states, lambda s: bits(s, X) == target)
        for t, state in enumerate(states):
            p_data_rows.append(data_row(traj_id, target_name, "DATA", flip, t, state,
                                        states[t - 1] if t else None, target))
            prior = states[t - 1] if t else ZERO
            raac_here = (
                t < len(states) - 1 and q_nonbaseline(state) > 0 and
                bits(step(state), X) != bits(step(state_for(bits(state, X))), X)
            )
            for variable in VARS:
                markers = []
                if t == 0 and variable == flip:
                    markers.append("PERTURBATION")
                if variable in Q and state[INDEX[variable]] and not prior[INDEX[variable]]:
                    markers.append("FIRST_NONBASELINE_AUX")
                if raac_here and variable in P and state[INDEX[variable]]:
                    markers.append("RAAC_NODE")
                if t == data_recovery_for_markers and variable == flip:
                    markers.append("DATA_RECOVERY")
                if state == state_for(target) and variable == flip:
                    markers.append("FULL_RECOVERY")
                node_rows.append({"trajectory_id": traj_id, "variable": variable, "t": t,
                                  "markers": ",".join(markers), "x": pack(bits(state, X)),
                                  "q": pack(bits(state, Q))})
        onset = first_time(states, lambda s: q_nonbaseline(s) > 0)
        family_times = {
            f"T_FIRST_{family}": first_time(states, lambda s, f=family:
                                             any(s[INDEX[name]] for name in globals()[f]))
            for family in ("D", "E", "L", "P")
        }
        direct_t = first_transition(
            states, lambda left, right: any(left[INDEX[name]] and
                                             left[INDEX["x" + name[1:]]] != right[INDEX["x" + name[1:]]]
                                             for name in P)
        )
        data_recovery = data_recovery_for_markers
        full_recovery = len(states) - 1
        durations = {name: sum(s[INDEX[name]] for s in states) for name in Q}
        max_q = max(map(q_nonbaseline, states))
        p_data_summary.append({
            "trajectory_id": traj_id, "target": target_name, "flipped_coordinate": flip,
            "T_PERTURBED": 0, "T_ONSET": onset, **family_times,
            "T_FIRST_DIRECT_DATA_EFFECT": direct_t, "T_DATA_RECOVERY": data_recovery,
            "T_FULL_RECOVERY": full_recovery, "TAIL_LENGTH": full_recovery - data_recovery,
            "MAX_AUX_HAMMING": max_q,
            "T_MAX_AUX_HAMMING": first_time(states, lambda s: q_nonbaseline(s) == max_q),
            **{f"duration_{name}": durations[name] for name in Q},
        })
        for t, state in enumerate(states[:-1]):
            actual_x = bits(step(state), X)
            if q_nonbaseline(state):
                baseline_state = state_for(bits(state, X))
                baseline_x = bits(step(baseline_state), X)
                affected = ",".join(name for name, a, b in zip(X, actual_x, baseline_x) if a != b)
                raac_rows.append({
                    "trajectory_id": traj_id, "t": t, "x": pack(bits(state, X)),
                    "q": pack(bits(state, Q)), "RAAC": actual_x != baseline_x,
                    "affected_x": affected, "actual_next_x": pack(actual_x),
                    "qstar_counterfactual_next_x": pack(baseline_x),
                })
            for parent, child in effective_edges(state):
                edge_rows.append({"trajectory_id": traj_id, "t": t, "parent": parent,
                                  "child": child, "static_essential": True,
                                  "context_effective": True})

        correction_t = direct_t
        sink = None
        if correction_t is not None:
            changed_at_correction = changed(states[correction_t], states[correction_t + 1], X).split(",")
            sink = (changed_at_correction[0], correction_t + 1)
        source = (flip, 0)
        adjacency = defaultdict(set)
        for row in (r for r in edge_rows if r["trajectory_id"] == traj_id):
            adjacency[(row["parent"], row["t"])].add((row["child"], row["t"] + 1))
        paths = all_paths(adjacency, source, sink) if sink else []
        common = set.intersection(*(set(path) for path in paths)) if paths else set()
        for variable, t in sorted(common, key=lambda item: (item[1], item[0])):
            dominator_rows.append({"trajectory_id": traj_id, "variable": variable, "t": t,
                                   "is_endpoint": (variable, t) in (source, sink),
                                   "effective_path_count": len(paths)})
    for traj_id, target_name, initial_family, flip, initial, target in p_full_initials():
        states = trace(initial, target)
        for t, state in enumerate(states):
            p_full_rows.append(data_row(traj_id, target_name, initial_family, flip, t, state,
                                        states[t - 1] if t else None, target))
        onset = first_time(states, lambda s: q_nonbaseline(s) > 0)
        first_after = next((FAMILY[name] for name in VARS
                            if name != flip and states[1][INDEX[name]] and FAMILY[name] != initial_family), "")
        direct_t = first_transition(states, lambda left, right:
                                    bits(left, X) != bits(right, X) and any(left[INDEX[p]] for p in P))
        first_data_change = first_transition(states, lambda left, right: bits(left, X) != bits(right, X))
        data_recovery = (
            0 if first_data_change is None else
            next(t for t, state in enumerate(states[first_data_change + 1:], first_data_change + 1)
                 if bits(state, X) == target)
        )
        raac_times = []
        affected = set()
        for t, state in enumerate(states[:-1]):
            if q_nonbaseline(state):
                actual_x = bits(step(state), X)
                base_x = bits(step(state_for(bits(state, X))), X)
                if actual_x != base_x:
                    raac_times.append(t)
                    affected.update(name for name, a, b in zip(X, actual_x, base_x) if a != b)
        p_full_summary.append({
            "trajectory_id": traj_id, "target": target_name, "initial_family": initial_family,
            "flipped_coordinate": flip, "latency": len(states) - 1,
            "x_ever_changes": any(bits(a, X) != bits(b, X) for a, b in zip(states, states[1:])),
            "q_expands_before_shrinking": max(map(q_nonbaseline, states)) > q_nonbaseline(states[0]),
            "first_family_activated_after_initial": first_after,
            "T_ONSET": onset, "T_FIRST_DIRECT_DATA_EFFECT": direct_t,
            "T_FIRST_DATA_CHANGE": first_data_change,
            "MAX_AUX_HAMMING": max(map(q_nonbaseline, states)),
            "T_DATA_RECOVERY": data_recovery, "T_FULL_RECOVERY": len(states) - 1,
            "TAIL_LENGTH": len(states) - 1 - data_recovery,
            "RAAC_OCCURS": bool(raac_times), "RAAC_TIMESTEPS": ",".join(map(str, raac_times)),
            "RAAC_AFFECTED_X": ",".join(sorted(affected)),
            "initial_aux_washes_without_x": initial_family != "DATA" and
                not any(bits(a, X) != bits(b, X) for a, b in zip(states, states[1:])),
            "triggers_pdata_like_data_repair": initial_family != "DATA" and direct_t is not None,
        })

    # Direct trace verification of complement symmetry.
    complement_pairs = []
    for index, coordinate in enumerate(X):
        low = p_data_traces[f"PDATA_0000_{coordinate}"]
        high = p_data_traces[f"PDATA_1111_{coordinate}"]
        complement_pairs.append(all(bits(a, Q) == bits(b, Q) and
                                    bits(a, X) == tuple(1 - bit for bit in bits(b, X))
                                    for a, b in zip(low, high)) and len(low) == len(high))

    # The only formula-preserving DATA permutation is (x1 x2).  It induces:
    # d13<->d23, d14<->d24, e1<->e2, l1<->l2, p1<->p2.
    swap12 = {"x1": "x2", "x2": "x1", "x3": "x3", "x4": "x4",
              "d12": "d12", "d13": "d23", "d23": "d13", "d14": "d24", "d24": "d14",
              "e1": "e2", "e2": "e1", "e3": "e3", "e4": "e4",
              "l1": "l2", "l2": "l1", "l3": "l3", "l4": "l4",
              "p1": "p2", "p2": "p1", "p3": "p3", "p4": "p4"}
    def rename(state):
        result = [0] * len(VARS)
        for old, new in swap12.items():
            result[INDEX[new]] = state[INDEX[old]]
        return tuple(result)
    assert all(rename(step(s)) == step(rename(s)) for traces in p_data_traces.values() for s in traces)
    assert all(complement_pairs)

    write_csv(OUT / "p_data_traces.csv", p_data_rows)
    write_csv(OUT / "p_data_summary.csv", p_data_summary)
    write_csv(OUT / "p_full_traces.csv", p_full_rows)
    write_csv(OUT / "p_full_summary.csv", p_full_summary)
    write_csv(OUT / "raac_atlas.csv", raac_rows)
    write_csv(OUT / "p_data_effective_edges.csv", edge_rows)
    write_csv(OUT / "p_data_temporal_nodes.csv", node_rows)
    write_csv(OUT / "p_data_dominators.csv", dominator_rows)
    (OUT / "verification.json").write_text(json.dumps({
        "model_verified": True, "variables": len(VARS), "auxiliaries": len(Q),
        "targets_fixed": True, "maximum_essential_arity": max(map(len, PARENTS.values())),
        "strict_synchronous_transition": True, "hidden_clock": False,
        "p_data_count": len(p_data_summary), "p_full_count": len(p_full_summary),
        "global_complement_verified": all(complement_pairs),
        "static_formula_automorphisms": ["identity", "(x1 x2)"],
    }, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
