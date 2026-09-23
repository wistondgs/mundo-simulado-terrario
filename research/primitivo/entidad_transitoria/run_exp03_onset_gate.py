"""ETP-EXP-03: parent-specific causal gate on the X -> D onset transmission.

Only the selected parent contribution to incident D XOR outputs is substituted
with that coordinate's original target value.  DATA remains physically
perturbed; D/E/L/P are never clamped or rewritten.
"""
from __future__ import annotations

import csv
from pathlib import Path

from build_baseline_atlas import (
    D, E, INDEX, L, P, Q, VARS, X, bits, changed, effective_edges, hamming,
    p_data_initials, pack, q_nonbaseline, state_for, step, trace,
)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "artifacts"
D_ENDPOINTS = {
    "d12": ("x1", "x2"), "d13": ("x1", "x3"), "d23": ("x2", "x3"),
    "d14": ("x1", "x4"), "d24": ("x2", "x4"),
}


def incident_d(source):
    return tuple(name for name, endpoints in D_ENDPOINTS.items() if source in endpoints)


def substitute_parent_at_d(state, target, source):
    """Compute G except replace source input by its target value in incident D."""
    result = list(step(state))
    source_value = target[INDEX[source]]
    for d_name, endpoints in D_ENDPOINTS.items():
        if source not in endpoints:
            continue
        other = endpoints[1] if endpoints[0] == source else endpoints[0]
        result[INDEX[d_name]] = source_value ^ state[INDEX[other]]
    return tuple(result)


def raac(state, successor):
    if not q_nonbaseline(state):
        return False
    baseline_x = bits(step(state_for(bits(state, X))), X)
    return bits(successor, X) != baseline_x


def first_time(states, predicate):
    return next((t for t, state in enumerate(states) if predicate(state)), None)


def first_raac(states, transitions):
    return next((t for t, successor in enumerate(transitions) if raac(states[t], successor)), None)


def run(initial, target, source=None, block_times=frozenset(), reset_seen_after_last_block=False, horizon=64):
    states, successors, intervention_times = [initial], [], []
    seen = {initial: 0}
    outcome, repeated_at, cycle_length = None, None, None
    for t in range(horizon):
        state = states[-1]
        blocked = source is not None and t in block_times
        successor = substitute_parent_at_d(state, target, source) if blocked else step(state)
        successors.append(successor)
        intervention_times.append(blocked)
        states.append(successor)
        if successor == state_for(target):
            outcome = "ORIGINAL_FULL_TARGET_REACHED"
            break
        # A finite block makes the t=0->t=1 transition a different regime.
        # Its repeated state cannot prove a cycle once G is restored at t=1.
        if reset_seen_after_last_block and t == max(block_times):
            seen = {successor: len(states) - 1}
            continue
        if successor in seen:
            outcome = "STATE_REPEAT"
            repeated_at = seen[successor]
            cycle_length = len(states) - 1 - repeated_at
            break
        seen[successor] = len(states) - 1
    if outcome is None:
        outcome = "SAFETY_HORIZON_UNCLASSIFIED"
    return states, successors, intervention_times, outcome, repeated_at, cycle_length


def rows_for_arm(arm_id, arm, target_name, flipped, source, states, successors, blocked, target):
    rows, edge_rows = [], []
    for t, state in enumerate(states):
        prior = states[t - 1] if t else None
        row = {
            "arm_id": arm_id, "arm": arm, "target": target_name,
            "flipped_coordinate": flipped, "substituted_parent": source or "",
            "t": t, "x": pack(bits(state, X)), "q": pack(bits(state, Q)),
            "D": pack(bits(state, D)), "E": pack(bits(state, E)),
            "L": pack(bits(state, L)), "P": pack(bits(state, P)),
            "d_H_x_target": hamming(bits(state, X), target),
            "d_H_q_qstar": q_nonbaseline(state),
            "changed_x": "" if prior is None else changed(prior, state, X),
            "changed_q": "" if prior is None else changed(prior, state, Q),
            "parent_substitution_on_transition": blocked[t] if t < len(blocked) else False,
        }
        row.update({name: state[INDEX[name]] for name in VARS})
        rows.append(row)
        if t < len(successors):
            frozen_edges = effective_edges(state)
            realized_edges = [
                edge for edge in frozen_edges
                if not (blocked[t] and edge[0] == source and edge[1] in incident_d(source))
            ]
            edge_rows.append({
                "arm_id": arm_id, "arm": arm, "t": t,
                "parent_substitution": blocked[t], "substituted_parent": source or "",
                "frozen_effective_edge_count": len(frozen_edges),
                "realized_effective_edge_count": len(realized_edges),
                "effective_edges": ";".join(f"{parent}->{child}" for parent, child in realized_edges),
            })
    return rows, edge_rows


def main():
    trace_rows, summary_rows, edge_rows, phase_rows = [], [], [], []
    for trajectory_id, target_name, flipped, initial, target_x in p_data_initials():
        target = state_for(target_x)
        natural = trace(initial, target_x)
        sham_source = next(name for name in X if name != flipped)
        arms = (
            ("NATURAL", None, frozenset(), False),
            ("NO_OP_SPATIAL_SHAM", sham_source, frozenset({0}), False),
            ("TRANSIENT_ONSET_BLOCK", flipped, frozenset({0}), True),
            ("PERSISTENT_ONSET_BLOCK", flipped, frozenset(range(64)), False),
        )
        arm_results = {}
        for arm, source, block_times, reset_seen in arms:
            states, successors, blocked, outcome, repeated_at, cycle_length = run(
                initial, target_x, source, block_times, reset_seen
            )
            arm_results[arm] = (states, successors, blocked, outcome, repeated_at, cycle_length)
            if arm == "NATURAL":
                assert states == natural
            if arm == "NO_OP_SPATIAL_SHAM":
                assert states == natural
                assert states[1] == natural[1]
            if arm == "TRANSIENT_ONSET_BLOCK":
                assert states[1] == natural[0]
                assert len(states) == len(natural) + 1
                assert all(states[t + 1] == natural[t] for t in range(len(natural)))
            if arm == "PERSISTENT_ONSET_BLOCK":
                assert states == [initial, initial]
                assert bits(states[0], X) != target_x and q_nonbaseline(states[0]) == 0
            arm_id = f"{arm}_{trajectory_id}"
            rows, edges = rows_for_arm(
                arm_id, arm, target_name, flipped, source, states, successors, blocked, target_x
            )
            trace_rows.extend(rows)
            edge_rows.extend(edges)
            onset = first_time(states, lambda s: q_nonbaseline(s) > 0)
            terminal = states[-1]
            summary_rows.append({
                "arm_id": arm_id, "arm": arm, "target": target_name,
                "flipped_coordinate": flipped, "substituted_parent": source or "",
                "incident_D_outputs": ",".join(incident_d(source)) if source else "",
                "actual_x_remains_perturbed_before_recovery": all(
                    bits(s, X) == bits(initial, X) for s in states[:(first_time(states, lambda s: bits(s, X) == target_x) or len(states))]
                ),
                "T_ONSET": "" if onset is None else onset,
                "T_FIRST_D": first_time(states, lambda s: any(s[INDEX[name]] for name in D)),
                "T_FIRST_E": first_time(states, lambda s: any(s[INDEX[name]] for name in E)),
                "T_FIRST_L": first_time(states, lambda s: any(s[INDEX[name]] for name in L)),
                "T_FIRST_P": first_time(states, lambda s: any(s[INDEX[name]] for name in P)),
                "T_FIRST_RAAC": first_raac(states, successors),
                "DATA_RECOVERY_TIME": first_time(states, lambda s: bits(s, X) == target_x),
                "FULL_RECOVERY_TIME": first_time(states, lambda s: s == target),
                "outcome": outcome, "first_repeated_state_t": "" if repeated_at is None else repeated_at,
                "cycle_length": "" if cycle_length is None else cycle_length,
                "terminal_x": pack(bits(terminal, X)), "terminal_q": pack(bits(terminal, Q)),
                "terminal_is_qstar": q_nonbaseline(terminal) == 0,
            })
        transient = arm_results["TRANSIENT_ONSET_BLOCK"][0]
        for natural_t, natural_state in enumerate(natural):
            transient_t = natural_t + 1
            comparison = transient[transient_t]
            mismatches = ",".join(
                name for name in VARS if comparison[INDEX[name]] != natural_state[INDEX[name]]
            )
            phase_rows.append({
                "trajectory_id": trajectory_id, "natural_t": natural_t,
                "transient_t": transient_t, "exact_equal": comparison == natural_state,
                "mismatched_coordinates": mismatches,
            })

    assert len(summary_rows) == 32
    by_arm = {arm: [row for row in summary_rows if row["arm"] == arm]
              for arm in ("NATURAL", "NO_OP_SPATIAL_SHAM", "TRANSIENT_ONSET_BLOCK", "PERSISTENT_ONSET_BLOCK")}
    for arm in ("NATURAL", "NO_OP_SPATIAL_SHAM"):
        assert all((row["T_ONSET"], row["T_FIRST_RAAC"], row["DATA_RECOVERY_TIME"],
                    row["FULL_RECOVERY_TIME"], row["outcome"]) ==
                   (1, 3, 4, 7, "ORIGINAL_FULL_TARGET_REACHED") for row in by_arm[arm])
    assert all((row["T_ONSET"], row["T_FIRST_RAAC"], row["DATA_RECOVERY_TIME"],
                row["FULL_RECOVERY_TIME"], row["outcome"]) ==
               (2, 4, 5, 8, "ORIGINAL_FULL_TARGET_REACHED") for row in by_arm["TRANSIENT_ONSET_BLOCK"])
    assert all(row["outcome"] == "STATE_REPEAT" and row["first_repeated_state_t"] == 0
               and row["cycle_length"] == 1 and row["terminal_is_qstar"] is True
               for row in by_arm["PERSISTENT_ONSET_BLOCK"])
    assert len(phase_rows) == 64 and all(row["exact_equal"] is True for row in phase_rows)

    def write(name, rows):
        with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    write("exp03_onset_gate_traces.csv", trace_rows)
    write("exp03_onset_gate_summary.csv", summary_rows)
    write("exp03_effective_edges.csv", edge_rows)
    write("exp03_phase_shift_comparison.csv", phase_rows)


if __name__ == "__main__":
    main()
