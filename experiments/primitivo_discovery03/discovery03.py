"""PRIMITIVO · DISCOVERY-03 standalone exhaustive instrument.

It enumerates only N=4 local Boolean networks with bounded essential arity.
It imports no historical code and writes no result artifacts.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import product, permutations


STATES = tuple(range(16))
MASKS = (8, 4, 2, 1)
MAX_K = 14


def bits(state: int) -> tuple[int, int, int, int]:
    return tuple((state >> shift) & 1 for shift in (3, 2, 1, 0))  # type: ignore[return-value]


def make_state(values: tuple[int, int, int, int]) -> int:
    return sum(bit << (3 - index) for index, bit in enumerate(values))


def output(table: int, state: int) -> int:
    return (table >> state) & 1


def essential(table: int) -> frozenset[int]:
    return frozenset(
        index
        for index, mask in enumerate(MASKS)
        if any(output(table, state) != output(table, state ^ mask) for state in STATES)
    )


ESS = {table: essential(table) for table in range(1 << 16)}


def table_of(predicate) -> int:
    return sum(int(predicate(state)) << state for state in STATES)


MAJ_123 = table_of(lambda state: sum(bits(state)[:3]) >= 2)
ZERO = 0


@dataclass(frozen=True)
class CentreClass:
    name: str
    one: int
    permutations: tuple[tuple[int, int, int, int], ...]
    translations: tuple[int, ...]

    @property
    def centres(self) -> tuple[int, int]:
        return (0, self.one)

    @property
    def ball_zero(self) -> frozenset[int]:
        return frozenset((0,) + MASKS)

    @property
    def ball_one(self) -> frozenset[int]:
        return frozenset((self.one,) + tuple(self.one ^ mask for mask in MASKS))

    @property
    def free(self) -> frozenset[int]:
        return frozenset(STATES) - self.ball_zero - self.ball_one

    @property
    def labels(self) -> dict[int, int]:
        return {**{state: 0 for state in self.ball_zero}, **{state: 1 for state in self.ball_one}}


C4 = CentreClass("DISTANCE_4", 15, tuple(permutations(range(4))), (0, 15))
C3 = CentreClass(
    "DISTANCE_3",
    14,
    tuple((permutation[0], permutation[1], permutation[2], 3) for permutation in permutations(range(3))),
    (0, 14),
)


def step(network: tuple[int, int, int, int], state: int) -> int:
    return make_state(tuple(output(table, state) for table in network))


@dataclass(frozen=True)
class Candidate:
    network: tuple[int, int, int, int]
    k: int
    latencies: tuple[int, ...]
    edges: int
    d_max: int
    t0: frozenset[int]
    t1: frozenset[int]

    @property
    def transient_budget(self) -> int:
        return len(self.t0 | self.t1)


def trace(cls: CentreClass, network: tuple[int, int, int, int], initial: int) -> tuple[int, ...] | None:
    label = cls.labels[initial]
    target = cls.centres[label]
    current, seen, path = initial, {initial}, [initial]
    for _ in range(MAX_K):
        current = step(network, current)
        path.append(current)
        if current == target:
            return tuple(path)
        if current in cls.centres or current in seen:
            return None
        seen.add(current)
    return None


def candidate(cls: CentreClass, network: tuple[int, int, int, int]) -> Candidate | None:
    if step(network, 0) != 0 or step(network, cls.one) != cls.one:
        return None
    latencies, t0, t1 = [], set(), set()
    for initial, label in sorted(cls.labels.items()):
        if initial in cls.centres:
            continue
        path = trace(cls, network, initial)
        if path is None:
            return None
        transient_path = set(path) & set(cls.free)
        (t0 if label == 0 else t1).update(transient_path)
        latencies.append(len(path) - 1)
    if t0 & t1:
        raise AssertionError("a free state cannot deterministically restore both centres")
    arities = tuple(len(ESS[table]) for table in network)
    return Candidate(network, max(latencies), tuple(latencies), sum(arities), max(arities), frozenset(t0), frozenset(t1))


def allowed_functions(cls: CentreClass, output_index: int, d_max: int) -> tuple[int, ...]:
    required_one = bits(cls.one)[output_index]
    return tuple(
        table
        for table in ESS
        if len(ESS[table]) <= d_max and output(table, 0) == 0 and output(table, cls.one) == required_one
    )


def search(cls: CentreClass, d_max: int) -> list[Candidate]:
    choices = tuple(allowed_functions(cls, index, d_max) for index in range(4))
    results = []
    for network in product(*choices):
        result = candidate(cls, network)
        if result is not None:
            results.append(result)
    return results


def search_b(results: list[Candidate]) -> list[Candidate]:
    return [result for result in results if not result.t0 and not result.t1]


def state_transform(permutation: tuple[int, int, int, int], translation: int) -> tuple[int, ...]:
    return tuple(make_state(tuple(bits(state)[index] for index in permutation)) ^ translation for state in STATES)


def symmetries(cls: CentreClass) -> tuple[tuple[int, ...], ...]:
    return tuple(state_transform(permutation, translation) for permutation in cls.permutations for translation in cls.translations)


def transform_network(network: tuple[int, int, int, int], transform: tuple[int, ...]) -> tuple[int, int, int, int]:
    inverse = tuple(transform.index(state) for state in STATES)
    tables = [0, 0, 0, 0]
    for state in STATES:
        result = transform[step(network, inverse[state])]
        for index, bit in enumerate(bits(result)):
            tables[index] |= bit << state
    return tuple(tables)  # type: ignore[return-value]


def canonical(cls: CentreClass, network: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    return min(transform_network(network, transformation) for transformation in symmetries(cls))


def orbit(cls: CentreClass, network: tuple[int, int, int, int]) -> frozenset[tuple[int, int, int, int]]:
    return frozenset(transform_network(network, transformation) for transformation in symmetries(cls))


def graph(network: tuple[int, int, int, int]) -> tuple[tuple[int, int], ...]:
    return tuple((source, destination) for destination, table in enumerate(network) for source in sorted(ESS[table]))


def sccs(network: tuple[int, int, int, int]) -> tuple[tuple[int, ...], ...]:
    adjacency = {node: set() for node in range(4)}
    for source, destination in graph(network):
        adjacency[source].add(destination)
    def reachable(start: int) -> set[int]:
        seen, pending = set(), [start]
        while pending:
            node = pending.pop()
            if node not in seen:
                seen.add(node)
                pending.extend(adjacency[node] - seen)
        return seen
    remaining, result = set(range(4)), []
    while remaining:
        root = min(remaining)
        component = tuple(sorted(node for node in remaining if root in reachable(node) and node in reachable(root)))
        result.append(component)
        remaining -= set(component)
    return tuple(result)


def reachability(network: tuple[int, int, int, int], time: int) -> tuple[tuple[bool, ...], ...]:
    evolved = {}
    for state in STATES:
        current = state
        for _ in range(time):
            current = step(network, current)
        evolved[state] = current
    return tuple(
        tuple(any(bool((evolved[state] ^ evolved[state ^ source_mask]) & destination_mask) for state in STATES) for destination_mask in MASKS)
        for source_mask in MASKS
    )


def decision_carriers(cls: CentreClass, network: tuple[int, int, int, int], horizon: int) -> tuple[tuple[int, int], ...]:
    carriers = []
    for time in range(1, horizon + 1):
        for index, mask in enumerate(MASKS):
            if all(
                bool((lambda state: state)(
                    next_state(network, state, time)
                ) & mask) == bool(label)
                for state, label in cls.labels.items()
            ):
                carriers.append((time, index))
    return tuple(carriers)


def next_state(network: tuple[int, int, int, int], state: int, time: int) -> int:
    for _ in range(time):
        state = step(network, state)
    return state


def pareto(results: list[Candidate]) -> list[Candidate]:
    return [
        item
        for item in results
        if not any(
            (other.k <= item.k and other.edges <= item.edges and other.d_max <= item.d_max and other.transient_budget <= item.transient_budget)
            and (other.k, other.edges, other.d_max, other.transient_budget) != (item.k, item.edges, item.d_max, item.transient_budget)
            for other in results
        )
    ]


def validate() -> None:
    counts = Counter(len(inputs) for inputs in ESS.values())
    assert len(STATES) == 16
    assert counts[0] == 2 and counts[1] == 8 and counts[2] == 60
    assert sum(counts[degree] for degree in (0, 1)) == 10
    assert sum(counts[degree] for degree in (0, 1, 2)) == 70
    for cls, expected_group in ((C3, 12), (C4, 48)):
        assert (cls.one ^ 0).bit_count() in (3, 4)
        assert len(cls.ball_zero) == len(cls.ball_one) == 5
        assert cls.ball_zero.isdisjoint(cls.ball_one)
        assert len(cls.free) == 6
        assert len(set(symmetries(cls))) == expected_group
    # Diagnostic d_max=3 controls locate the first known permitted arity.
    controls = {
        C4: (MAJ_123, MAJ_123, MAJ_123, MAJ_123),
        C3: (MAJ_123, MAJ_123, MAJ_123, ZERO),
    }
    for cls, network in controls.items():
        result = candidate(cls, network)
        assert result is not None and result.k == 1 and result.d_max == 3
        for transformation in symmetries(cls):
            transformed = candidate(cls, transform_network(network, transformation))
            assert transformed is not None
            assert (transformed.k, transformed.edges, transformed.d_max) == (result.k, result.edges, result.d_max)
    # Identity leaves each perturbation in a non-centre cycle; copying x4 into all
    # outputs sends a C4 perturbation to the wrong fixed centre.
    identity = tuple(table_of(lambda state, mask=mask: bool(state & mask)) for mask in MASKS)
    copy_x4 = tuple(table_of(lambda state: bool(state & 1)) for _ in range(4))
    assert candidate(C4, identity) is None
    assert candidate(C4, copy_x4) is None


def brief_lesions(result: Candidate, all_d2: list[Candidate]) -> dict[str, object]:
    """State-free class tests; no arbitrary rewiring of individual truth-table rows."""
    visited = result.t0 | result.t1
    avoiding = {
        state: sum(state not in (other.t0 | other.t1) for other in all_d2)
        for state in visited
    }
    return {
        "visited": tuple(sorted(visited)),
        "search_b_exists": bool(search_b(all_d2)),
        "class_candidates_avoiding_each_visited_state": avoiding,
    }


def summarize(cls: CentreClass, d1: list[Candidate], d2: list[Candidate]) -> dict[str, object]:
    all_orbits = defaultdict(list)
    for result in d2:
        all_orbits[canonical(cls, result.network)].append(result)
    front = pareto(d2)
    representatives = {}
    for result in front:
        key = canonical(cls, result.network)
        if key in representatives:
            continue
        representative = candidate(cls, key)
        assert representative is not None
        representatives[key] = {
            "orbit_size": len(orbit(cls, key)),
            "members": len(all_orbits[key]),
            "k": representative.k,
            "edges": representative.edges,
            "d_max": representative.d_max,
            "latencies": representative.latencies,
            "t0": tuple(sorted(representative.t0)),
            "t1": tuple(sorted(representative.t1)),
            "graph": graph(key),
            "scc": sccs(key),
            "reachability": tuple(reachability(key, time) for time in range(1, representative.k + 1)),
            "decision_carriers": decision_carriers(cls, key, representative.k),
            "transient_class_test": brief_lesions(representative, d2),
        }
    return {
        "allowed_functions_dmax_1": tuple(len(allowed_functions(cls, index, 1)) for index in range(4)),
        "allowed_functions_dmax_2": tuple(len(allowed_functions(cls, index, 2)) for index in range(4)),
        "search_a_dmax_1": len(d1),
        "search_a_dmax_2": len(d2),
        "search_b_dmax_2": len(search_b(d2)),
        "minimum_k": min((item.k for item in d2), default=None),
        "minimum_edges": min((item.edges for item in d2), default=None),
        "minimum_transient_budget": min((item.transient_budget for item in d2), default=None),
        "symmetry_classes": len(all_orbits),
        "pareto_orbits": representatives,
    }


def main() -> None:
    validate()
    for cls in (C3, C4):
        d1, d2 = search(cls, 1), search(cls, 2)
        for result in d2:
            for transformation in symmetries(cls):
                transformed = candidate(cls, transform_network(result.network, transformation))
                assert transformed is not None
                assert (transformed.k, transformed.edges, transformed.d_max, transformed.transient_budget) == (result.k, result.edges, result.d_max, result.transient_budget)
                assert sorted(transformed.latencies) == sorted(result.latencies)
        print(cls.name, summarize(cls, d1, d2))


if __name__ == "__main__":
    main()
