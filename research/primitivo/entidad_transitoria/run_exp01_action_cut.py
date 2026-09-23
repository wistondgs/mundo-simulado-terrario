"""ETP-EXP-01: exhaustive surgical cut of the P_i -> X_i RAAC edge.

Imports the committed frozen specimen-A transition.  The only altered update is
one named edge on one transition; no source state, rule, or later step changes.
"""
from __future__ import annotations

import csv
from pathlib import Path

from build_baseline_atlas import (
    D, E, FAMILY, INDEX, L, P, Q, TARGETS, VARS, X, bits, changed,
    effective_edges, hamming, p_data_initials, pack, q_nonbaseline, state_for,
    step, trace,
)

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "artifacts"


def cut_edge(state, coordinate):
    """Return frozen G(state), except remove P_coordinate -> X_coordinate."""
    result = list(step(state))
    result[INDEX[coordinate]] = state[INDEX[coordinate]]
    return tuple(result)


def transition(state, cut_coordinate=None):
    return cut_edge(state, cut_coordinate) if cut_coordinate else step(state)


def raac_against_qstar(state, successor):
    if not q_nonbaseline(state):
        return False, ""
    baseline = bits(step(state_for(bits(state, X))), X)
    actual = bits(successor, X)
    affected = ",".join(name for name, a, b in zip(X, actual, baseline) if a != b)
    return actual != baseline, affected


def run_arm(initial, target, cut_t=None, cut_coordinate=None, horizon=64):
    states = [initial]
    seen = {initial: 0}
    transitions = []
    outcome, repeated_at, cycle_length = None, None, None
    for t in range(horizon):
        state = states[-1]
        use_cut = cut_coordinate if t == cut_t else None
        successor = transition(state, use_cut)
        frozen_successor = step(state)
        frozen_raac, frozen_affected = raac_against_qstar(state, frozen_successor)
        realized_raac, realized_affected = raac_against_qstar(state, successor)
        edges = effective_edges(state)
        realized_edges = [edge for edge in edges if edge != ("p" + coordinate_suffix(use_cut), use_cut)] if use_cut else edges
        transitions.append({
            "t": t, "cut_applied": bool(use_cut), "cut_coordinate": use_cut or "",
            "frozen_raac": frozen_raac, "frozen_raac_affected_x": frozen_affected,
            "realized_raac": realized_raac, "realized_raac_affected_x": realized_affected,
            "frozen_effective_edge_count": len(edges),
            "realized_effective_edge_count": len(realized_edges),
            "all_other_updates_equal_frozen_G": all(
                successor[INDEX[name]] == frozen_successor[INDEX[name]]
                for name in VARS if name != use_cut
            ),
            "effective_edges": ";".join(f"{parent}->{child}" for parent, child in realized_edges),
        })
        states.append(successor)
        if successor == state_for(target):
            outcome = "ORIGINAL_FULL_TARGET_REACHED"
            break
        if successor in seen:
            outcome = "STATE_REPEAT"
            repeated_at = seen[successor]
            cycle_length = len(states) - 1 - repeated_at
            break
        seen[successor] = len(states) - 1
    if outcome is None:
        outcome = "SAFETY_HORIZON_UNCLASSIFIED"
    return states, transitions, outcome, repeated_at, cycle_length


def coordinate_suffix(coordinate):
    return coordinate[1:] if coordinate else ""


def state_rows(arm_id, target_name, flipped, cut_t, cut_coordinate, states, transitions, target):
    rows = []
    for t, state in enumerate(states):
        prior = states[t - 1] if t else None
        metadata = transitions[t] if t < len(transitions) else {
            "cut_applied": False, "cut_coordinate": "", "frozen_raac": False,
            "frozen_raac_affected_x": "", "realized_raac": False,
            "realized_raac_affected_x": "", "frozen_effective_edge_count": "",
            "realized_effective_edge_count": "", "all_other_updates_equal_frozen_G": "",
            "effective_edges": "",
        }
        row = {
            "arm_id": arm_id, "target": target_name, "flipped_coordinate": flipped,
            "cut_t": "" if cut_t is None else cut_t, "cut_coordinate": cut_coordinate or "",
            "t": t, "x": pack(bits(state, X)), "q": pack(bits(state, Q)),
            "d_H_x_target": hamming(bits(state, X), target),
            "d_H_q_qstar": q_nonbaseline(state),
            "D": pack(bits(state, D)), "E": pack(bits(state, E)),
            "L": pack(bits(state, L)), "P": pack(bits(state, P)),
            "changed_x": "" if prior is None else changed(prior, state, X),
            "changed_q": "" if prior is None else changed(prior, state, Q),
        }
        row.update({name: state[INDEX[name]] for name in VARS})
        row.update(metadata)
        rows.append(row)
    return rows


def first_time(states, predicate):
    return next((t for t, state in enumerate(states) if predicate(state)), None)


def main():
    trace_rows, summary_rows, edge_rows = [], [], []
    for traj_id, target_name, flipped, initial, target in p_data_initials():
        natural = trace(initial, target)
        z3 = natural[3]
        assert z3[INDEX["p" + coordinate_suffix(flipped)]] == 1
        spatial = next(
            coordinate for coordinate in X
            if coordinate != flipped and z3[INDEX["p" + coordinate_suffix(coordinate)]] == 0
        )
        arms = (
            ("NATURAL", None, None),
            ("TEMPORAL_SHAM", 2, flipped),
            ("SPATIAL_SHAM", 3, spatial),
            ("ACTION_CUT", 3, flipped),
        )
        for arm_name, cut_t, cut_coordinate in arms:
            arm_id = f"{arm_name}_{traj_id}"
            states, transitions, outcome, repeated_at, cycle_length = run_arm(
                initial, target, cut_t, cut_coordinate
            )
            if arm_name == "NATURAL":
                assert states == natural
            else:
                assertion = transitions[cut_t]
                assert assertion["all_other_updates_equal_frozen_G"]
                if arm_name == "TEMPORAL_SHAM":
                    assert states == natural and z3[INDEX["p" + coordinate_suffix(flipped)]] == 1
                    assert natural[2][INDEX["p" + coordinate_suffix(flipped)]] == 0
                if arm_name == "SPATIAL_SHAM":
                    assert states == natural and z3[INDEX["p" + coordinate_suffix(spatial)]] == 0
                if arm_name == "ACTION_CUT":
                    assert z3[INDEX["p" + coordinate_suffix(flipped)]] == 1
                    assert states[4][INDEX[flipped]] == states[3][INDEX[flipped]]
                    assert states[4][INDEX["p" + coordinate_suffix(flipped)]] == 0
            trace_rows.extend(state_rows(
                arm_id, target_name, flipped, cut_t, cut_coordinate, states, transitions, target
            ))
            for item in transitions:
                edge_rows.append({
                    "arm_id": arm_id, "target": target_name, "flipped_coordinate": flipped,
                    **item,
                })
            p_name = "p" + coordinate_suffix(flipped)
            data_recovery = first_time(states, lambda s: bits(s, X) == target)
            full_recovery = first_time(states, lambda s: s == state_for(target))
            terminal = states[-1]
            summary_rows.append({
                "arm_id": arm_id, "arm": arm_name, "target": target_name,
                "flipped_coordinate": flipped, "cut_t": "" if cut_t is None else cut_t,
                "cut_coordinate": cut_coordinate or "", "natural_p_i_t3": z3[INDEX[p_name]],
                "p_i_t3_actual": states[3][INDEX[p_name]],
                "onset_preserved_through_t3": bits(states[3], Q) == bits(z3, Q),
                "state_t3_matches_natural": states[3] == z3,
                "DATA_RECOVERY_TIME": "" if data_recovery is None else data_recovery,
                "FULL_RECOVERY_TIME": "" if full_recovery is None else full_recovery,
                "outcome": outcome, "first_repeated_state_t": "" if repeated_at is None else repeated_at,
                "cycle_length": "" if cycle_length is None else cycle_length,
                "terminal_x": pack(bits(terminal, X)), "terminal_q": pack(bits(terminal, Q)),
                "terminal_D": pack(bits(terminal, D)), "terminal_E": pack(bits(terminal, E)),
                "terminal_L": pack(bits(terminal, L)), "terminal_P": pack(bits(terminal, P)),
                "terminal_is_original_target": terminal == state_for(target),
                "second_p_pulse_after_t3": any(s[INDEX[p_name]] for s in states[4:]),
                "D_E_L_nonbaseline_at_terminal": any(terminal[INDEX[name]] for name in D + E + L),
            })

    def write(name, rows):
        with (OUT / name).open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)

    write("exp01_action_cut_traces.csv", trace_rows)
    write("exp01_action_cut_summary.csv", summary_rows)
    write("exp01_effective_edges.csv", edge_rows)

    # Acceptance checks: 8 trajectories × 4 arms, all shams reproduce baseline.
    assert len(summary_rows) == 32
    by_arm = {name: [row for row in summary_rows if row["arm"] == name]
              for name in ("NATURAL", "TEMPORAL_SHAM", "SPATIAL_SHAM", "ACTION_CUT")}
    for name in ("NATURAL", "TEMPORAL_SHAM", "SPATIAL_SHAM"):
        assert len(by_arm[name]) == 8
        assert all(row["DATA_RECOVERY_TIME"] == 4 and row["FULL_RECOVERY_TIME"] == 7
                   and row["outcome"] == "ORIGINAL_FULL_TARGET_REACHED" for row in by_arm[name])
    assert len(by_arm["ACTION_CUT"]) == 8
    assert all(row["p_i_t3_actual"] == 1 and row["state_t3_matches_natural"] is True
               and row["DATA_RECOVERY_TIME"] == "" and row["FULL_RECOVERY_TIME"] == ""
               and row["outcome"] == "STATE_REPEAT" and row["cycle_length"] == 1
               and row["terminal_P"] == "0000" and row["second_p_pulse_after_t3"] is False
               and row["D_E_L_nonbaseline_at_terminal"] is True
               for row in by_arm["ACTION_CUT"])


if __name__ == "__main__":
    main()
