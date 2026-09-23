"""PRIMITIVO · DISCOVERY-02

Exhaustive search over three-bit synchronous Boolean dynamics with fixed centres
000 and 111.  This is a deliberately small, standalone instrument: it imports
nothing from the historical Terrario codebase and writes no result artifacts.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product, permutations
from collections import Counter, defaultdict
from typing import Iterable


N = 3
STATES = tuple(range(8))
CENTRES = (0, 7)
ERROR_STATES = (1, 2, 4, 3, 5, 6)  # radius-one errors of 000, then 111
MAX_K = 6  # with two fixed centres, a successful trajectory needs at most 6 steps
MAJORITY = sum(1 << s for s in STATES if s.bit_count() >= 2)


def bits(state: int) -> tuple[int, int, int]:
    return tuple((state >> shift) & 1 for shift in (2, 1, 0))  # type: ignore[return-value]


def make_state(values: Iterable[int]) -> int:
    answer = 0
    for value in values:
        answer = (answer << 1) | value
    return answer


def value(table: int, state: int) -> int:
    return (table >> state) & 1


def essential_inputs(table: int) -> frozenset[int]:
    result = set()
    for variable, mask in enumerate((4, 2, 1)):
        if any(value(table, state) != value(table, state ^ mask) for state in STATES):
            result.add(variable)
    return frozenset(result)


ESS = {table: essential_inputs(table) for table in range(256)}


def step(network: tuple[int, int, int], state: int) -> int:
    return make_state(value(table, state) for table in network)


def transition_table(network: tuple[int, int, int]) -> tuple[int, ...]:
    return tuple(step(network, state) for state in STATES)


def target(state: int) -> int:
    return 0 if state.bit_count() <= 1 else 7


@dataclass(frozen=True)
class Candidate:
    network: tuple[int, int, int]
    k_required: int
    latencies: tuple[int, ...]
    edges: int
    d_max: int


def restoration(network: tuple[int, int, int], horizon: int = MAX_K) -> tuple[int, ...] | None:
    """Return first-hit times for all six non-centre perturbations, or None."""
    if step(network, 0) != 0 or step(network, 7) != 7:
        return None
    result = []
    for initial in ERROR_STATES:
        current = initial
        wanted = target(initial)
        for time in range(1, horizon + 1):
            current = step(network, current)
            if current == wanted:
                result.append(time)
                break
            if current in CENTRES:  # fixed wrong centre: this trajectory cannot recover
                return None
        else:
            return None
    return tuple(result)


def candidate(network: tuple[int, int, int]) -> Candidate | None:
    latencies = restoration(network)
    if latencies is None:
        return None
    arities = tuple(len(ESS[table]) for table in network)
    return Candidate(network, max(latencies), latencies, sum(arities), max(arities))


def functions_with_dmax(limit: int) -> tuple[int, ...]:
    return tuple(
        table
        for table in range(256)
        if len(ESS[table]) <= limit and value(table, 0) == 0 and value(table, 7) == 1
    )


def all_candidates(limit: int) -> list[Candidate]:
    functions = functions_with_dmax(limit)
    found = []
    for network in product(functions, repeat=3):
        result = candidate(network)
        if result is not None:
            found.append(result)
    return found


def state_transform(permutation: tuple[int, int, int], complement: bool) -> tuple[int, ...]:
    transformed = []
    for state in STATES:
        original = bits(state)
        values = tuple(original[index] for index in permutation)
        if complement:
            values = tuple(1 - bit for bit in values)
        transformed.append(make_state(values))
    return tuple(transformed)


SYMMETRIES = tuple(
    state_transform(permutation, complement)
    for permutation in permutations(range(3))
    for complement in (False, True)
)


def transform_network(network: tuple[int, int, int], transform: tuple[int, ...]) -> tuple[int, int, int]:
    inverse = tuple(transform.index(state) for state in STATES)
    output_tables = [0, 0, 0]
    for state in STATES:
        output = transform[step(network, inverse[state])]
        for index, bit in enumerate(bits(output)):
            output_tables[index] |= bit << state
    return tuple(output_tables)  # type: ignore[return-value]


def orbit(network: tuple[int, int, int]) -> frozenset[tuple[int, int, int]]:
    return frozenset(transform_network(network, transform) for transform in SYMMETRIES)


def canonical(network: tuple[int, int, int]) -> tuple[int, int, int]:
    return min(orbit(network))


def graph(network: tuple[int, int, int]) -> tuple[tuple[int, int], ...]:
    return tuple(
        (source, target_node)
        for target_node, table in enumerate(network)
        for source in sorted(ESS[table])
    )


def functional_reachability(network: tuple[int, int, int], time: int) -> tuple[tuple[bool, ...], ...]:
    """Actual, not merely graph-theoretic, influence from x_j(0) to x_i(time)."""
    evolved = {}
    for state in STATES:
        current = state
        for _ in range(time):
            current = step(network, current)
        evolved[state] = current
    rows = []
    for source, mask in enumerate((4, 2, 1)):
        row = []
        for output_index, output_mask in enumerate((4, 2, 1)):
            row.append(any(bool((evolved[state] ^ evolved[state ^ mask]) & output_mask) for state in STATES))
        rows.append(tuple(row))
    return tuple(rows)


def strongly_connected_components(network: tuple[int, int, int]) -> tuple[tuple[int, ...], ...]:
    adjacency = {node: set() for node in range(3)}
    for source, destination in graph(network):
        adjacency[source].add(destination)

    def reachable(start: int) -> set[int]:
        seen, todo = set(), [start]
        while todo:
            node = todo.pop()
            if node not in seen:
                seen.add(node)
                todo.extend(adjacency[node] - seen)
        return seen

    remaining = set(range(3))
    components = []
    while remaining:
        node = min(remaining)
        component = tuple(sorted(other for other in remaining if node in reachable(other) and other in reachable(node)))
        components.append(component)
        remaining -= set(component)
    return tuple(components)


def decision_carriers(network: tuple[int, int, int], horizon: int) -> tuple[tuple[int, int], ...]:
    answer = []
    for time in range(1, horizon + 1):
        outputs = {state: state for state in STATES}
        for _ in range(time):
            outputs = {state: step(network, output) for state, output in outputs.items()}
        for index, mask in enumerate((4, 2, 1)):
            if all(bool(outputs[state] & mask) == bool(target(state)) for state in STATES):
                answer.append((time, index))
    return tuple(answer)


def edge_removals(table: int, source: int) -> tuple[int, ...]:
    """All minimum-Hamming replacements that make source non-essential."""
    mask = (4, 2, 1)[source]
    pairs = [(state, state ^ mask) for state in STATES if not state & mask]
    choices = []
    for low, high in pairs:
        low_value, high_value = value(table, low), value(table, high)
        choices.append((low_value,) if low_value == high_value else (0, 1))
    replacements = []
    for selected in product(*choices):
        replacement = 0
        for (low, high), output in zip(pairs, selected):
            replacement |= output << low
            replacement |= output << high
        replacements.append(replacement)
    return tuple(sorted(set(replacements)))


def lesion_summary(network: tuple[int, int, int]) -> dict[str, object]:
    intact = candidate(network)
    assert intact is not None
    edges = []
    for target_node, table in enumerate(network):
        for source in sorted(ESS[table]):
            replacements = edge_removals(table, source)
            outcomes = []
            for replacement in replacements:
                altered = list(network)
                altered[target_node] = replacement
                result = candidate(tuple(altered))
                outcomes.append(None if result is None else result.k_required)
            edges.append({
                "edge": (source, target_node),
                "minimal_replacements": len(replacements),
                "successful_replacements": sum(outcome is not None for outcome in outcomes),
                "replacement_k": tuple(outcomes),
            })

    freeze = {}
    for node in range(3):
        for constant in (0, 1):
            altered = list(network)
            altered[node] = 0 if constant == 0 else 255
            result = candidate(tuple(altered))
            freeze[(node, constant)] = None if result is None else result.k_required

    local_rule = {}
    for node, table in enumerate(network):
        replacements = [
            other for other in range(256)
            if ESS[other] == ESS[table] and other != table
        ]
        successes = 0
        for replacement in replacements:
            altered = list(network)
            altered[node] = replacement
            successes += candidate(tuple(altered)) is not None
        local_rule[node] = (len(replacements), successes)

    copy = {}
    for node in range(3):
        for source, mask in enumerate((4, 2, 1)):
            table = sum(((state & mask) != 0) << state for state in STATES)
            if table == network[node]:
                copy[(node, source)] = "UNCHANGED"
                continue
            altered = list(network)
            altered[node] = table
            result = candidate(tuple(altered))
            copy[(node, source)] = None if result is None else result.k_required

    decouple = {}
    for source in range(3):
        affected = [
            target_node
            for target_node, table in enumerate(network)
            if target_node != source and source in ESS[table]
        ]
        if not affected:
            decouple[source] = "NOT_APPLICABLE"
            continue
        choices = [edge_removals(network[target_node], source) for target_node in affected]
        outcomes = []
        for replacements in product(*choices):
            altered = list(network)
            for target_node, replacement in zip(affected, replacements):
                altered[target_node] = replacement
            result = candidate(tuple(altered))
            outcomes.append(None if result is None else result.k_required)
        decouple[source] = {
            "affected_targets": tuple(affected),
            "minimal_replacements": len(outcomes),
            "successful_replacements": sum(outcome is not None for outcome in outcomes),
            "replacement_k": tuple(outcomes),
        }

    return {
        "intact_k": intact.k_required,
        "edge": tuple(edges),
        "freeze": freeze,
        "local_rule": local_rule,
        "decouple": decouple,
        "copy": copy,
    }


def validate() -> None:
    assert len(ESS) == 256
    assert max((left ^ right).bit_count() for left in range(4) for right in range(4)) == 2
    assert sum(len(inputs) <= 1 for inputs in ESS.values()) == 8
    assert sum(len(inputs) <= 2 for inputs in ESS.values()) == 38
    assert ESS[MAJORITY] == frozenset({0, 1, 2})
    majority_network = (MAJORITY, MAJORITY, MAJORITY)
    assert step(majority_network, 0) == 0 and step(majority_network, 7) == 7
    assert restoration(majority_network, 1) == (1, 1, 1, 1, 1, 1)
    assert len(graph(majority_network)) == 9
    assert len(SYMMETRIES) == 12
    for transform in SYMMETRIES:
        transformed = transform_network(majority_network, transform)
        assert restoration(transformed, 1) == (1, 1, 1, 1, 1, 1)
        inverse = tuple(transform.index(state) for state in STATES)
        assert transform_network(transformed, inverse) == majority_network
        assert tuple(sorted(len(ESS[table]) for table in transformed)) == (3, 3, 3)


def summarize(candidates: list[Candidate]) -> dict[str, object]:
    by_k = Counter(result.k_required for result in candidates)
    by_k_min_edges = {
        k: min(result.edges for result in candidates if result.k_required <= k)
        for k in range(1, MAX_K + 1)
        if any(result.k_required <= k for result in candidates)
    }
    pareto = []
    for item in candidates:
        if not any(
            (other.k_required <= item.k_required and other.edges <= item.edges and other.d_max <= item.d_max)
            and (other.k_required, other.edges, other.d_max) != (item.k_required, item.edges, item.d_max)
            for other in candidates
        ):
            pareto.append(item)
    orbit_members = defaultdict(list)
    for item in candidates:
        orbit_members[canonical(item.network)].append(item)
    pareto_orbits = {}
    for item in pareto:
        key = canonical(item.network)
        representative = candidate(key)
        assert representative is not None
        pareto_orbits[key] = {
            "representative": key,
            "orbit_size": len(orbit(key)),
            "members_in_search": len(orbit_members[key]),
            "k": representative.k_required,
            "edges": representative.edges,
            "d_max": representative.d_max,
            "latencies": representative.latencies,
            "graph": graph(key),
            "scc": strongly_connected_components(key),
            "reachability": tuple(functional_reachability(key, time) for time in range(1, representative.k_required + 1)),
            "decision_carriers": decision_carriers(key, representative.k_required),
            "lesions": lesion_summary(key),
        }
    return {
        "functions_dmax_1_fixed_centres": len(functions_with_dmax(1)),
        "functions_dmax_2_fixed_centres": len(functions_with_dmax(2)),
        "candidate_count": len(candidates),
        "by_k_required": dict(sorted(by_k.items())),
        "best_edges_by_horizon": by_k_min_edges,
        "symmetry_classes": len(orbit_members),
        "pareto_count": len(pareto),
        "pareto_orbits": pareto_orbits,
    }


def main() -> None:
    validate()
    l2 = all_candidates(1)
    l1 = all_candidates(2)
    l0 = all_candidates(3)
    assert not l2, "d_max <= 1 unexpectedly has a restoring dynamics"
    assert not l1, "d_max <= 2 unexpectedly has a restoring dynamics"
    for result in l0:
        for transform in SYMMETRIES:
            transformed = candidate(transform_network(result.network, transform))
            assert transformed is not None
            assert (transformed.k_required, transformed.edges, transformed.d_max) == (
                result.k_required,
                result.edges,
                result.d_max,
            )
            assert sorted(transformed.latencies) == sorted(result.latencies)
    print("VALIDATION: PASS")
    print("L2 d_max<=1 candidates:", len(l2))
    print("L1 d_max<=2 candidates:", len(l1))
    print("L0 unrestricted-arity (but fixed-centre) summary:")
    print(summarize(l0))


if __name__ == "__main__":
    main()
