"""ETP-EXP-02: external target restoration from the EXP-01 cut state.

The experiment reuses the committed surgical action cut, then writes only DATA
at t=4.  It verifies that the repaired state exactly rejoins PRE-01 before G
resumes unmodified.
"""
from __future__ import annotations

import csv
from pathlib import Path

from build_baseline_atlas import (
    D, E, INDEX, L, P, Q, VARS, X, bits, changed, effective_edges, hamming,
    p_data_initials, pack, q_nonbaseline, state_for, step, trace,
)
from run_exp01_action_cut import cut_edge

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "artifacts"


def first_time(states, predicate, start=0):
    return next((t for t, state in enumerate(states) if t >= start and predicate(state)), None)


def prefix_through_cut(initial, target, flipped):
    natural = trace(initial, target)
    assert len(natural) == 8
    z3 = natural[3]
    cut4 = cut_edge(z3, flipped)
    natural4 = natural[4]
    assert bits(cut4, Q) == bits(natural4, Q)
    assert bits(cut4, X) != bits(natural4, X)
    assert bits(natural4, X) == target
    assert pack(bits(cut4, P)) == "0000"
    assert any(cut4[INDEX[name]] for name in D + E + L)
    return natural, [natural[0], natural[1], natural[2], natural[3], cut4]


def resume(prefix, target, write_kind=None, horizon=64):
    states = list(prefix)
    cut4 = states[4]
    write = {"kind": write_kind or "NONE", "q_preserved": True, "x_only": True}
    if write_kind == "NO_OP_WRITE":
        states[4] = state_for(bits(cut4, X), bits(cut4, Q))
    elif write_kind == "TARGET_RESTORATION":
        states[4] = state_for(target, bits(cut4, Q))
    repaired4 = states[4]
    write["q_preserved"] = bits(repaired4, Q) == bits(cut4, Q)
    write["x_only"] = all(
        repaired4[INDEX[name]] == cut4[INDEX[name]] for name in Q
    )
    seen = {state: t for t, state in enumerate(states)}
    outcome, repeated_at, cycle_length = None, None, None
    for _ in range(horizon):
        successor = step(states[-1])
        states.append(successor)
        t = len(states) - 1
        if successor == state_for(target):
            outcome = "ORIGINAL_FULL_TARGET_REACHED"
            break
        if successor in seen:
            outcome = "STATE_REPEAT"
            repeated_at = seen[successor]
            cycle_length = t - repeated_at
            break
        seen[successor] = t
    if outcome is None:
        outcome = "SAFETY_HORIZON_UNCLASSIFIED"
    return states, write, outcome, repeated_at, cycle_length


def trace_rows(arm_id, arm, target_name, flipped, states, target, write, natural4):
    rows, transition_edges = [], []
    for t, state in enumerate(states):
        prior = states[t - 1] if t else None
        if t < len(states) - 1:
            edges = effective_edges(state)
            transition_edges.append({
                "arm_id": arm_id, "arm": arm, "t": t,
                "effective_edge_count": len(edges),
                "effective_edges": ";".join(f"{parent}->{child}" for parent, child in edges),
            })
        row = {
            "arm_id": arm_id, "arm": arm, "target": target_name,
            "flipped_coordinate": flipped, "t": t, "x": pack(bits(state, X)),
            "q": pack(bits(state, Q)), "D": pack(bits(state, D)),
            "E": pack(bits(state, E)), "L": pack(bits(state, L)), "P": pack(bits(state, P)),
            "d_H_x_target": hamming(bits(state, X), target),
            "d_H_q_qstar": q_nonbaseline(state),
            "changed_x": "" if prior is None else changed(prior, state, X),
            "changed_q": "" if prior is None else changed(prior, state, Q),
            "write_at_t4": write["kind"] if t == 4 else "",
            "q_preserved_at_t4": write["q_preserved"] if t == 4 else "",
            "rejoins_natural_t4": state == natural4 if t == 4 else "",
        }
        row.update({name: state[INDEX[name]] for name in VARS})
        rows.append(row)
    return rows, transition_edges


def return_times(states):
    return {
        f"T_RETURN_{name}": first_time(states, lambda s, n=name: s[INDEX[n]] == 0, start=4)
        for name in D + E + L
    }


def main():
    all_traces, all_summary, all_edges = [], [], []
    for trajectory_id, target_name, flipped, initial, target in p_data_initials():
        natural = trace(initial, target)
        _, cut_prefix = prefix_through_cut(initial, target, flipped)
        cut4 = cut_prefix[4]
        natural4 = natural[4]
        arms = (
            ("NATURAL", natural, {"kind": "NONE", "q_preserved": True, "x_only": True},
             "ORIGINAL_FULL_TARGET_REACHED", None, None),
            ("ACTION_CUT_ONLY", *resume(cut_prefix, target)),
            ("NO_OP_WRITE", *resume(cut_prefix, target, "NO_OP_WRITE")),
            ("TARGET_RESTORATION", *resume(cut_prefix, target, "TARGET_RESTORATION")),
        )
        for arm, states, write, outcome, repeated_at, cycle_length in arms:
            arm_id = f"{arm}_{trajectory_id}"
            if arm == "NATURAL":
                assert states == natural
            if arm == "ACTION_CUT_ONLY":
                assert states[4] == cut4
            if arm == "NO_OP_WRITE":
                assert states[4] == cut4
            if arm == "TARGET_RESTORATION":
                assert bits(states[4], Q) == bits(cut4, Q)
                assert states[4] == natural4
            rows, edges = trace_rows(
                arm_id, arm, target_name, flipped, states, target, write, natural4
            )
            all_traces.extend(rows)
            all_edges.extend(edges)
            terminal = states[-1]
            data_recovery = first_time(states, lambda s: bits(s, X) == target)
            full_recovery = first_time(states, lambda s: s == state_for(target))
            all_summary.append({
                "arm_id": arm_id, "arm": arm, "target": target_name,
                "flipped_coordinate": flipped, "q_cut_4": pack(bits(cut4, Q)),
                "q_natural_4": pack(bits(natural4, Q)),
                "q_cut_4_equals_q_natural_4": bits(cut4, Q) == bits(natural4, Q),
                "x_cut_4": pack(bits(cut4, X)), "x_natural_4": pack(bits(natural4, X)),
                "x_cut_4_differs_natural_4": bits(cut4, X) != bits(natural4, X),
                "z_repaired_4_equals_z_natural_4": states[4] == natural4,
                "write_kind": write["kind"], "q_preserved_at_t4": write["q_preserved"],
                "only_x_changed_at_t4": write["x_only"],
                "DATA_RECOVERY_TIME": "" if data_recovery is None else data_recovery,
                "FULL_RECOVERY_TIME": "" if full_recovery is None else full_recovery,
                "outcome": outcome, "first_repeated_state_t": "" if repeated_at is None else repeated_at,
                "cycle_length": "" if cycle_length is None else cycle_length,
                "terminal_x": pack(bits(terminal, X)), "terminal_q": pack(bits(terminal, Q)),
                "terminal_P": pack(bits(terminal, P)),
                "P_nonzero_after_t4": any(any(s[INDEX[name]] for name in P) for s in states[5:]),
                **return_times(states),
            })

    assert len(all_summary) == 32
    by_arm = {arm: [row for row in all_summary if row["arm"] == arm]
              for arm in ("NATURAL", "ACTION_CUT_ONLY", "NO_OP_WRITE", "TARGET_RESTORATION")}
    for arm in ("NATURAL",):
        assert all(r["DATA_RECOVERY_TIME"] == 4 and r["FULL_RECOVERY_TIME"] == 7
                   and r["outcome"] == "ORIGINAL_FULL_TARGET_REACHED" for r in by_arm[arm])
    for arm in ("ACTION_CUT_ONLY", "NO_OP_WRITE"):
        assert all(r["DATA_RECOVERY_TIME"] == "" and r["FULL_RECOVERY_TIME"] == ""
                   and r["outcome"] == "STATE_REPEAT" and r["first_repeated_state_t"] == 4
                   and r["cycle_length"] == 1 for r in by_arm[arm])
    for row in by_arm["TARGET_RESTORATION"]:
        assert row["q_cut_4_equals_q_natural_4"] is True
        assert row["x_cut_4_differs_natural_4"] is True
        assert row["z_repaired_4_equals_z_natural_4"] is True
        assert row["q_preserved_at_t4"] is True and row["only_x_changed_at_t4"] is True
        assert row["DATA_RECOVERY_TIME"] == 4 and row["FULL_RECOVERY_TIME"] == 7
        assert row["outcome"] == "ORIGINAL_FULL_TARGET_REACHED"
        assert row["P_nonzero_after_t4"] is False
        for name in D:
            assert row[f"T_RETURN_{name}"] in (4, 5)
        for name in E:
            assert row[f"T_RETURN_{name}"] in (4, 6)
        for name in L:
            assert row[f"T_RETURN_{name}"] in (4, 7)

    def write(name, rows):
        with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    write("exp02_external_repair_traces.csv", all_traces)
    write("exp02_external_repair_summary.csv", all_summary)
    write("exp02_effective_edges.csv", all_edges)


if __name__ == "__main__":
    main()

