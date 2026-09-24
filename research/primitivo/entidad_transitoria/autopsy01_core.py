"""Shared machinery for ETP-AUTOPSY-01.

A network is a tuple of named Boolean coordinates.  Each coordinate has at most
two parents and a truth table indexed by sum(parent_j << j).  Every transition
is synchronous: all coordinates read the state at t.

Interventions are explicit and named:

* a persistent clamp sets one coordinate to a constant from a given time on;
* a timed write sets one coordinate at one time step only;
* a rule edit builds a new, separately named network.

This module never touches the frozen specimen.  run_autopsy01_mechanism.py
verifies that the specimen-A network built here equals
build_baseline_atlas.step on all 2**21 states before using it.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations

# ---------------------------------------------------------------- gates

XOR = (0, 1, 1, 0)
XNOR = (1, 0, 0, 1)
AND = (0, 0, 0, 1)
OR = (0, 1, 1, 1)
A_AND_NOT_B = (0, 1, 0, 0)          # parent0 AND NOT parent1
COPY = (0, 1)
NOT = (1, 0)
CONST0 = (0,)
CONST1 = (1,)

GATE_NAMES = {XOR: "XOR", XNOR: "XNOR", AND: "AND", OR: "OR",
              A_AND_NOT_B: "A_AND_NOT_B", COPY: "COPY", NOT: "NOT",
              CONST0: "CONST0", CONST1: "CONST1"}

TWO_INPUT_TABLES = tuple(tuple((code >> k) & 1 for k in range(4)) for code in range(16))


def gate_name(table):
    if table in GATE_NAMES:
        return GATE_NAMES[table]
    return "T" + "".join(map(str, table))


@dataclass(frozen=True)
class Rule:
    parents: tuple[str, ...]
    table: tuple[int, ...]

    def __post_init__(self):
        assert len(self.parents) <= 2, "fan-in above 2 is outside the constraint"
        assert len(self.table) == 1 << len(self.parents)

    def arity_ok(self):
        return len(self.parents) <= 2


@dataclass(frozen=True)
class WideRule:
    """Only for explicitly labelled constraint-violating comparisons."""
    parents: tuple[str, ...]
    table: tuple[int, ...]

    def __post_init__(self):
        assert len(self.table) == 1 << len(self.parents)


class Net:
    """Synchronous Boolean network over named coordinates.

    names: coordinate order; bit i of a state integer is names[i].
    families: e.g. {"X": (...), "D": (...), ...}; "X" must be present.
    codewords: tuples of X values whose full state (x, 0...0) is a target.
    """

    def __init__(self, name, names, rules, families, codewords, fan_in_limit=2):
        self.name = name
        self.names = tuple(names)
        self.index = {n: i for i, n in enumerate(self.names)}
        assert set(rules) == set(self.names), set(rules) ^ set(self.names)
        self.rules = dict(rules)
        self.families = {k: tuple(v) for k, v in families.items()}
        self.x_names = self.families["X"]
        self.aux_names = tuple(n for n in self.names if n not in self.x_names)
        self.codewords = tuple(tuple(c) for c in codewords)
        self.max_fan_in = max(len(r.parents) for r in self.rules.values())
        self.respects_fan_in = self.max_fan_in <= fan_in_limit
        compiled = []
        for i, n in enumerate(self.names):
            rule = self.rules[n]
            compiled.append((i, tuple(self.index[p] for p in rule.parents), rule.table))
        self._compiled = tuple(compiled)
        self.n_vars = len(self.names)
        self.x_mask = sum(1 << self.index[n] for n in self.x_names)

    # -- state helpers
    def state(self, values=None, **assign):
        s = 0
        values = values or {}
        for n, v in {**values, **assign}.items():
            if v:
                s |= 1 << self.index[n]
        return s

    def from_x(self, x_bits, aux=None):
        s = 0
        for n, b in zip(self.x_names, x_bits):
            if b:
                s |= 1 << self.index[n]
        for n, b in (aux or {}).items():
            if b:
                s |= 1 << self.index[n]
        return s

    def get(self, s, n):
        return (s >> self.index[n]) & 1

    def x_of(self, s):
        return tuple((s >> self.index[n]) & 1 for n in self.x_names)

    def pattern(self, s, family):
        return "".join(str((s >> self.index[n]) & 1) for n in self.families[family])

    def aux_of(self, s):
        return tuple((s >> self.index[n]) & 1 for n in self.aux_names)

    def aux_zero(self, s):
        return all(not (s >> self.index[n]) & 1 for n in self.aux_names)

    def flip(self, s, n):
        return s ^ (1 << self.index[n])

    def targets(self):
        return tuple(self.from_x(c) for c in self.codewords)

    # -- dynamics
    def step(self, s):
        out = 0
        for i, ps, tab in self._compiled:
            if len(ps) == 2:
                k = ((s >> ps[0]) & 1) | (((s >> ps[1]) & 1) << 1)
            elif len(ps) == 1:
                k = (s >> ps[0]) & 1
            elif len(ps) == 0:
                k = 0
            else:
                k = 0
                for j, p in enumerate(ps):
                    k |= ((s >> p) & 1) << j
            if tab[k]:
                out |= 1 << i
        return out

    def edited(self, name, new_rules, fan_in_limit=2):
        rules = dict(self.rules)
        rules.update(new_rules)
        return Net(name, self.names, rules, self.families, self.codewords, fan_in_limit)


class WideNet(Net):
    """A Net that may contain WideRule coordinates (fan-in above 2)."""

    def __init__(self, name, names, rules, families, codewords):
        super().__init__(name, names, rules, families, codewords, fan_in_limit=99)


# ---------------------------------------------------------------- builders

def witness_net(n, witnesses, name=None, include_l=True, p_rule="EDGE", x_reads="P", codewords=None):
    """Radius-1 decoder family: D = XOR of the witness pairs actually used,
    E_i = AND of the two checks between i and its witnesses, L_i = E_i,
    P_i = E_i AND NOT L_i, x_i' = x_i XOR P_i.

    witnesses: dict i -> (a, b), 1-based coordinates, a != b, both != i.
    The same builder, with n=4 and the specimen-A witnesses, gives A.
    """
    xs = tuple(f"x{i}" for i in range(1, n + 1))

    def dname(a, b):
        a, b = sorted((a, b))
        return f"d{a}{b}" if n < 10 else f"d{a}_{b}"

    pairs = []
    for i in range(1, n + 1):
        for w in witnesses[i]:
            pair = tuple(sorted((i, w)))
            if pair not in pairs:
                pairs.append(pair)
    ds = tuple(dname(*p) for p in pairs)
    es = tuple(f"e{i}" for i in range(1, n + 1))
    ls = tuple(f"l{i}" for i in range(1, n + 1)) if include_l else ()
    ps = tuple(f"p{i}" for i in range(1, n + 1))
    rules = {}
    for (a, b), d in zip(pairs, ds):
        rules[d] = Rule((f"x{a}", f"x{b}"), XOR)
    for i in range(1, n + 1):
        a, b = witnesses[i]
        rules[f"e{i}"] = Rule((dname(i, a), dname(i, b)), AND)
        if include_l:
            rules[f"l{i}"] = Rule((f"e{i}",), COPY)
        if p_rule == "EDGE":
            rules[f"p{i}"] = Rule((f"e{i}", f"l{i}"), A_AND_NOT_B)
        elif p_rule == "LEVEL":
            rules[f"p{i}"] = Rule((f"e{i}",), COPY)
        else:
            raise ValueError(p_rule)
        source = f"p{i}" if x_reads == "P" else f"e{i}"
        rules[f"x{i}"] = Rule((f"x{i}", source), XOR)
    families = {"X": xs, "D": ds, "E": es, "L": ls, "P": ps}
    names = xs + ds + es + ls + ps
    codewords = codewords or ((0,) * n, (1,) * n)
    return Net(name or f"W{n}", names, rules, families, codewords)


SPECIMEN_A_WITNESSES = {1: (2, 3), 2: (1, 3), 3: (1, 2), 4: (1, 2)}


def specimen_a():
    """Specimen A rebuilt from its declared rules (verified elsewhere)."""
    net = witness_net(4, SPECIMEN_A_WITNESSES, name="A")
    # The declared D order of the frozen specimen is d12,d13,d23,d14,d24.
    assert net.families["D"] == ("d12", "d13", "d23", "d14", "d24"), net.families["D"]
    return net


def all_witness_assignments(n=4):
    options = {i: tuple(combinations([j for j in range(1, n + 1) if j != i], 2))
               for i in range(1, n + 1)}
    def rec(i, acc):
        if i > n:
            yield dict(acc)
            return
        for pair in options[i]:
            acc[i] = pair
            yield from rec(i + 1, acc)
        del acc[i]
    yield from rec(1, {})


# ---------------------------------------------------------------- runs

@dataclass
class RunResult:
    states: list
    homogeneous_from: int
    cycle_start: int | None
    cycle_length: int | None
    horizon_hit: bool = False
    labels: dict = field(default_factory=dict)


def run(net, initial, clamps=(), writes=None, horizon=512):
    """Synchronous run with explicit interventions.

    clamps: iterable of (coordinate, value, t_from): coordinate forced to value
            at every t >= t_from (applied to the state at that time).
    writes: {t: {coordinate: value}} applied to the state at time t only.
    Repetition is only read as a cycle once the intervened dynamics is time
    homogeneous (t >= homogeneous_from).
    """
    writes = writes or {}
    clamps = tuple(clamps)
    homogeneous_from = max([0] + [t for t in writes] + [t for _, _, t in clamps])

    def apply(s, t):
        for n, v, t_from in clamps:
            if t >= t_from:
                bit = 1 << net.index[n]
                s = (s | bit) if v else (s & ~bit)
        for n, v in writes.get(t, {}).items():
            bit = 1 << net.index[n]
            s = (s | bit) if v else (s & ~bit)
        return s

    s = apply(initial, 0)
    states = [s]
    seen = {}
    t = 0
    while t < horizon:
        if t >= homogeneous_from:
            if s in seen:
                start = seen[s]
                return RunResult(states, homogeneous_from, start, t - start)
            seen[s] = t
        s = apply(net.step(s), t + 1)
        states.append(s)
        t += 1
    return RunResult(states, homogeneous_from, None, None, horizon_hit=True)


def terminal_cycle(result):
    if result.cycle_start is None:
        return ()
    return tuple(result.states[result.cycle_start:result.cycle_start + result.cycle_length])


def classify(net, result, original_x):
    """Outcome relative to the original codeword original_x."""
    if result.horizon_hit:
        return "HORIZON_UNCLASSIFIED"
    cycle = terminal_cycle(result)
    opposite = tuple(1 - b for b in original_x)
    if len(cycle) > 1:
        xs = {net.x_of(s) for s in cycle}
        return "CYCLE_X_MOVING" if len(xs) > 1 else "CYCLE_X_STILL"
    s = cycle[0]
    x = net.x_of(s)
    aux_zero = net.aux_zero(s)
    if x == original_x:
        return "FULL_ORIGINAL_TARGET" if aux_zero else "X_ORIGINAL_Q_NONBASELINE"
    if x == opposite and opposite in net.codewords:
        return "FULL_OPPOSITE_TARGET" if aux_zero else "X_OPPOSITE_Q_NONBASELINE"
    if x in net.codewords:
        return "FULL_OTHER_CODEWORD" if aux_zero else "X_OTHER_CODEWORD_Q_NONBASELINE"
    return "NON_CODEWORD_FIXED_POINT"


def first_time(states, predicate):
    return next((t for t, s in enumerate(states) if predicate(s)), None)


def settle_time(net, result, predicate):
    """First t from which predicate holds for every later recorded state
    and every state of the terminal cycle."""
    states = result.states
    cycle = terminal_cycle(result)
    if not cycle or not all(predicate(s) for s in cycle):
        return None
    t = len(states) - 1
    while t > 0 and predicate(states[t - 1]):
        t -= 1
    return t


def pulse_events(net, states, family="P"):
    events = []
    for t, s in enumerate(states):
        for n in net.families.get(family, ()):
            if net.get(s, n):
                events.append((t, n))
    return events


def x_toggles(net, states):
    events = []
    for t in range(len(states) - 1):
        for n in net.x_names:
            if net.get(states[t], n) != net.get(states[t + 1], n):
                events.append((t + 1, n))
    return events


def summarize_run(net, result, original_x):
    target_full = net.from_x(original_x)
    outcome = classify(net, result, original_x)
    states = result.states
    data_t = settle_time(net, result, lambda s: net.x_of(s) == tuple(original_x))
    full_t = settle_time(net, result, lambda s: s == target_full)
    pulses = pulse_events(net, states)
    toggles = x_toggles(net, states)
    return {
        "outcome": outcome,
        "cycle_start": result.cycle_start,
        "cycle_length": result.cycle_length,
        "data_recovery_t": data_t,
        "full_recovery_t": full_t,
        "p_pulses": len(pulses),
        "p_pulse_events": ";".join(f"{n}@t{t}" for t, n in pulses),
        "x_toggles": len(toggles),
        "x_toggle_events": ";".join(f"{n}@t{t}" for t, n in toggles),
        "terminal_x": "".join(map(str, net.x_of(result.states[result.cycle_start]))) if result.cycle_start is not None else "",
        "max_aux_on": max(sum(net.aux_of(s)) for s in states),
    }


# ---------------------------------------------------------------- battery

def majority_codeword(net, x):
    n = len(x)
    w = sum(x)
    if 2 * w < n:
        return (0,) * n
    if 2 * w > n:
        return (1,) * n
    return None


def battery(net, full_state_census=False):
    """Standard evaluation of one network variant.

    P-DATA: every single-bit DATA lesion of every codeword, aux at baseline.
    P-FULL: every single-coordinate flip of every codeword full state.
    Q*-starts: every DATA configuration with aux at baseline.
    """
    n = len(net.x_names)
    targets_fixed = all(net.step(t) == t for t in net.targets())
    pdata = []
    for c in net.codewords:
        for k, xn in enumerate(net.x_names):
            x = list(c)
            x[k] ^= 1
            r = run(net, net.from_x(x))
            summary = summarize_run(net, r, c)
            summary.update({"codeword": "".join(map(str, c)), "lesion": xn})
            pdata.append(summary)
    pfull = []
    for c in net.codewords:
        base = net.from_x(c)
        for v in net.names:
            r = run(net, net.flip(base, v))
            summary = summarize_run(net, r, c)
            summary.update({"codeword": "".join(map(str, c)), "flipped": v})
            pfull.append(summary)
    qstar = []
    for code in range(1 << n):
        x = tuple((code >> (n - 1 - j)) & 1 for j in range(n))
        r = run(net, net.from_x(x))
        term = r.states[r.cycle_start] if r.cycle_start is not None else None
        nearest = majority_codeword(net, x)
        if nearest is not None:
            outcome_class = classify(net, r, nearest)
        elif r.cycle_length != 1:
            outcome_class = "TIE_CYCLE"
        elif net.x_of(term) in net.codewords:
            outcome_class = "TIE_TO_" + "".join(map(str, net.x_of(term))) + ("" if net.aux_zero(term) else "_AUX_ON")
        else:
            outcome_class = "TIE_NON_CODEWORD_FIXED_POINT"
        qstar.append({
            "x": "".join(map(str, x)), "weight": sum(x),
            "outcome_class": outcome_class,
            "terminal_x": "".join(map(str, net.x_of(term))) if term is not None else "",
            "terminal_aux_zero": net.aux_zero(term) if term is not None else None,
            "cycle_length": r.cycle_length,
            "p_pulses": len(pulse_events(net, r.states)),
            "settle_t": r.cycle_start,
        })
    ok_pdata = sum(row["outcome"] == "FULL_ORIGINAL_TARGET" for row in pdata)
    ok_pfull = sum(row["outcome"] == "FULL_ORIGINAL_TARGET" for row in pfull)
    false_repair = sum(row["outcome"].startswith(("FULL_OPPOSITE", "X_OPPOSITE", "FULL_OTHER", "X_OTHER")) for row in pdata + pfull)
    cycles = sum(row["outcome"].startswith("CYCLE") for row in pdata + pfull) + \
        sum((row["cycle_length"] or 0) > 1 for row in qstar)
    restored_x_nonhalting = sum(row["outcome"] == "X_ORIGINAL_Q_NONBASELINE" for row in pdata)
    half = [row for row in qstar if 2 * row["weight"] == n]
    ties_to_codeword = sum(row["terminal_x"] in ("0" * n, "1" * n) and row["terminal_aux_zero"] for row in half)
    stalls = sum(row["cycle_length"] == 1 and row["terminal_x"] not in ("0" * n, "1" * n) for row in qstar)
    failed_lesions = ",".join(f"{row['codeword']}:{row['lesion']}" for row in pdata if row["outcome"] != "FULL_ORIGINAL_TARGET")
    latencies = [row["full_recovery_t"] for row in pdata if row["full_recovery_t"] is not None]
    edges = sum(len(r.parents) for r in net.rules.values())
    return {
        "variant": net.name,
        "n_vars": net.n_vars,
        "n_aux": len(net.aux_names),
        "n_static_edges": edges,
        "max_fan_in": net.max_fan_in,
        "respects_fan_in_2": net.respects_fan_in,
        "targets_fixed": targets_fixed,
        "pdata_full_recovery": ok_pdata,
        "pdata_total": len(pdata),
        "failed_lesions": failed_lesions,
        "pdata_max_full_latency": max(latencies) if latencies else None,
        "pdata_pulses_per_lesion": ",".join(str(row["p_pulses"]) for row in pdata),
        "pfull_full_recovery": ok_pfull,
        "pfull_total": len(pfull),
        "false_repairs": false_repair,
        "cycles": cycles,
        "x_restored_without_self_halt": restored_x_nonhalting,
        "qstar_starts_to_codeword": sum(row["terminal_x"] in ("0" * n, "1" * n) and bool(row["terminal_aux_zero"]) for row in qstar),
        "qstar_total": len(qstar),
        "qstar_stalls": stalls,
        "half_weight_to_codeword": ties_to_codeword,
        "half_weight_total": len(half),
        "_pdata": pdata, "_pfull": pfull, "_qstar": qstar,
    }


def battery_passes(metrics):
    """The minimal functional requirement: fixed targets, all single DATA
    lesions restored exactly, no false repair, no cycle, self-halting."""
    return (metrics["targets_fixed"]
            and metrics["pdata_full_recovery"] == metrics["pdata_total"]
            and metrics["false_repairs"] == 0
            and metrics["cycles"] == 0
            and metrics["x_restored_without_self_halt"] == 0)


def public(metrics):
    return {k: v for k, v in metrics.items() if not k.startswith("_")}
