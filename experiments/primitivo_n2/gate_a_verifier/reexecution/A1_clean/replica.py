#!/usr/bin/env python3
"""Independent closed replica for PRIMITIVO N=2, specification v0.1."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import platform
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Callable, Iterable

N = 256
ROOT = Path(__file__).resolve().parent
SPEC = ROOT / "SPEC_PRIMITIVO_N2_A_REPLICA_CERRADA_v0_1.md"
CUTS = (("C12", "P1", "P2"), ("C13", "P1", "P3"), ("C23", "P2", "P3"))


def x1(s: int) -> int:
    return s >> 1


def x2(s: int) -> int:
    return s & 1


PARTITIONS: dict[str, Callable[[int], int]] = {
    "P1": x1, "P2": x2, "P3": lambda s: x1(s) ^ x2(s)
}


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def masks(a: str, b: str) -> tuple[int, int]:
    pa, pb = PARTITIONS[a], PARTITIONS[b]
    ma = [m for m in range(1, 4) if all(pa(s ^ m) != pa(s) and pb(s ^ m) == pb(s) for s in range(4))]
    mb = [m for m in range(1, 4) if all(pb(s ^ m) != pb(s) and pa(s ^ m) == pa(s) for s in range(4))]
    if len(ma) != 1 or len(mb) != 1:
        raise ValueError(f"non-unique masks for {a}, {b}")
    return ma[0], mb[0]


MASKS = {name: masks(a, b) for name, a, b in CUTS}


def attractors(f: tuple[int, int, int, int]) -> list[list[int]]:
    found: set[tuple[int, ...]] = set()
    for start in range(4):
        path: list[int] = []
        positions: dict[int, int] = {}
        state = start
        while state not in positions:
            positions[state] = len(path)
            path.append(state)
            state = f[state]
        found.add(tuple(sorted(path[positions[state]:])))
    return [list(cycle) for cycle in sorted(found)]


def attractor_reached(f: tuple[int, int, int, int], start: int) -> tuple[int, ...]:
    path: list[int] = []
    positions: dict[int, int] = {}
    state = start
    while state not in positions:
        positions[state] = len(path)
        path.append(state)
        state = f[state]
    return tuple(sorted(path[positions[state]:]))


def dependence(f: tuple[int, int, int, int], a: str, b: str, ma: int, mb: int) -> dict[str, object]:
    pa, pb = PARTITIONS[a], PARTITIONS[b]
    def depends(output: Callable[[int], int], mask: int) -> bool:
        return any(output(f[s]) != output(f[s ^ mask]) for s in range(4))
    graph = [depends(pa, ma), depends(pa, mb), depends(pb, ma), depends(pb, mb)]
    cross = "separable" if not graph[1] and not graph[2] else "mutua" if graph[1] and graph[2] else "unidir"
    return {"cruzada": cross, "grafo": graph}


def fraction_string(numerator: int, denominator: int) -> str:
    value = Fraction(numerator, denominator)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def robustness(f: tuple[int, int, int, int], cycles: list[list[int]], chosen_masks: Iterable[int]) -> str:
    successes = total = 0
    for cycle in cycles:
        original = tuple(cycle)
        for state in cycle:
            for mask in chosen_masks:
                total += 1
                successes += attractor_reached(f, state ^ mask) == original
    return fraction_string(successes, total)


def scheduler_dynamics(f: tuple[int, int, int, int]) -> tuple[tuple[int, int, int, int], tuple[int, int, int, int]]:
    sec12, sec21 = [], []
    for s in range(4):
        first_x1 = x1(f[s])
        middle12 = 2 * first_x1 + x2(s)
        sec12.append(2 * first_x1 + x2(f[middle12]))
        first_x2 = x2(f[s])
        middle21 = 2 * x1(s) + first_x2
        sec21.append(2 * x1(f[middle21]) + first_x2)
    return tuple(sec12), tuple(sec21)


def scheduler(f: tuple[int, int, int, int], cycles: list[list[int]]) -> dict[str, object]:
    sec12, sec21 = scheduler_dynamics(f)
    c12, c21 = attractors(sec12), attractors(sec21)
    sync_set = {tuple(c) for c in cycles}
    return {
        "atractores_distintos": sync_set != {tuple(c) for c in c12} or sync_set != {tuple(c) for c in c21},
        "ciclo_muere_sin_reloj": any(len(c) >= 2 and tuple(c) not in {tuple(v) for v in c12} and tuple(c) not in {tuple(v) for v in c21} for c in cycles),
        "sec12": c12,
        "sec21": c21,
        "sinc": cycles,
    }


def lesion_dynamics(f: tuple[int, int, int, int], variable: str, mode: str) -> tuple[int, int, int, int]:
    result = []
    for s in range(4):
        if variable == "x1":
            new_x1 = x1(s) if mode == "congelar" else 0
            result.append(2 * new_x1 + x2(f[s]))
        else:
            new_x2 = x2(s) if mode == "congelar" else 0
            result.append(2 * x1(f[s]) + new_x2)
    return tuple(result)


def lesions(f: tuple[int, int, int, int], cycles: list[list[int]]) -> dict[str, object]:
    original = {s for cycle in cycles for s in cycle}
    answer: dict[str, object] = {}
    for variable in ("x1", "x2"):
        answer[variable] = {}
        for mode in ("congelar", "fijar0"):
            damaged = lesion_dynamics(f, variable, mode)
            reached = {s for cycle in attractors(damaged) for s in cycle}
            answer[variable][mode] = reached != original
    return answer


PERMUTATIONS = list(itertools.permutations(range(4)))


def conjugate(f: tuple[int, int, int, int], p: tuple[int, int, int, int]) -> tuple[int, int, int, int]:
    result = [0] * 4
    for s in range(4):
        result[p[s]] = p[f[s]]
    return tuple(result)


def c12_permutations() -> list[tuple[int, int, int, int]]:
    all_p = []
    for swap in (False, True):
        for n1, n2 in itertools.product(range(2), repeat=2):
            p = []
            for s in range(4):
                a, b = x1(s), x2(s)
                if swap:
                    a, b = b, a
                p.append(2 * (a ^ n1) + (b ^ n2))
            all_p.append(tuple(p))
    return all_p


C12_PERMUTATIONS = c12_permutations()


def type_of(f: tuple[int, int, int, int], permutations: Iterable[tuple[int, int, int, int]]) -> list[int]:
    return list(min(conjugate(f, p) for p in permutations))


def analyze(f: tuple[int, int, int, int]) -> dict[str, object]:
    cycles = attractors(f)
    dependencies = {name: dependence(f, a, b, *MASKS[name]) for name, a, b in CUTS}
    return {
        "F": list(f),
        "atractores": cycles,
        "dependencias": dependencies,
        "lesion": lesions(f, cycles),
        "periodos": sorted(len(c) for c in cycles),
        "robustez": {name: robustness(f, cycles, MASKS[name]) for name, _, _ in CUTS},
        "scheduler": scheduler(f, cycles),
        "tipo_C12": type_of(f, C12_PERMUTATIONS),
        "tipo_S4": type_of(f, PERMUTATIONS),
    }


def all_dynamics() -> Iterable[tuple[int, int, int, int]]:
    return itertools.product(range(4), repeat=4)


def tuple_value(value: object) -> object:
    if isinstance(value, list):
        return tuple(tuple_value(v) for v in value)
    if isinstance(value, dict):
        return tuple((k, tuple_value(v)) for k, v in sorted(value.items()))
    return value


def entropy(labels: list[object]) -> float:
    total = len(labels)
    return -sum((count / total) * math.log2(count / total) for count in Counter(labels).values())


def mutual_information(left: list[object], right: list[object]) -> float:
    total = len(left)
    left_counts, right_counts = Counter(left), Counter(right)
    joint = Counter(zip(left, right))
    return sum((count / total) * math.log2((count * total) / (left_counts[a] * right_counts[b])) for (a, b), count in joint.items())


def log_comb(n: int, k: int) -> float:
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def expected_mi(left: list[object], right: list[object]) -> float:
    """Exact fixed-marginal expectation from C11's hypergeometric sum."""
    total = len(left)
    answer = 0.0
    for ai in Counter(left).values():
        for bj in Counter(right).values():
            low, high = max(1, ai + bj - total), min(ai, bj)
            for n in range(low, high + 1):
                log_probability = log_comb(ai, n) + log_comb(total - ai, bj - n) - log_comb(total, bj)
                probability = math.exp(log_probability)
                answer += (n / total) * math.log2(total * n / (ai * bj)) * probability
    return answer


def metric_set(vocabulary: list[object], consequence: list[object]) -> dict[str, object]:
    h_v, h_t = entropy(vocabulary), entropy(consequence)
    observed, expected = mutual_information(vocabulary, consequence), expected_mi(vocabulary, consequence)
    denominator = max(h_v, h_t) - expected
    return {
        "I_bits": round(observed, 6),
        "E_I_permutacion_exacta_bits": round(expected, 6),
        "AMI_max": round((observed - expected) / denominator, 6) if denominator else 0.0,
    }


def label_text(value: object) -> str:
    return canonical_json(value)


def vocabulary_report(vocabulary: list[object], k: list[object], robustness_c12: list[object], consequences: dict[str, list[object]]) -> dict[str, object]:
    grouped: dict[object, list[int]] = defaultdict(list)
    for index, label in enumerate(vocabulary):
        grouped[label].append(index)
    return {
        "clases": len(grouped),
        "clases_con_colision_en_K": sum(len({k[i] for i in indices}) >= 2 for indices in grouped.values()),
        "clases_con_colision_en_robustez": sum(len({robustness_c12[i] for i in indices}) >= 2 for indices in grouped.values()),
        "colision_garantizada_por_conteo": len(grouped) < len(set(k)),
        "H_V_bits": round(entropy(vocabulary), 6),
        "consecuencias": {name: metric_set(vocabulary, values) for name, values in consequences.items()},
    }


def summary(records: list[dict[str, object]]) -> dict[str, object]:
    cats = ("separable", "mutua", "unidir")
    category = {cut: [r["dependencias"][cut]["cruzada"] for r in records] for cut, _, _ in CUTS}  # type: ignore[index]
    robust = {cut: [r["robustez"][cut] for r in records] for cut, _, _ in CUTS}  # type: ignore[index]
    graphs = {cut: [tuple(r["dependencias"][cut]["grafo"]) for r in records] for cut, _, _ in CUTS}  # type: ignore[index]
    types_s4 = [tuple(r["tipo_S4"]) for r in records]  # type: ignore[arg-type]
    types_c12 = [tuple(r["tipo_C12"]) for r in records]  # type: ignore[arg-type]
    periods = [tuple(r["periodos"]) for r in records]  # type: ignore[arg-type]
    k = list(zip(periods, robust["C12"]))
    consequences = {"K": k, "solo_robustez_C12": robust["C12"], "solo_periodos": periods}
    vocabularies = {
        "grafo_dependencias_C12": vocabulary_report(graphs["C12"], k, robust["C12"], consequences),
        "cruzada_C12": vocabulary_report(category["C12"], k, robust["C12"], consequences),
        "tipo_S4": vocabulary_report(types_s4, k, robust["C12"], consequences),
    }
    deterministic = {
        "n_dinamicas": len(records),
        "tipos_S4": len(set(types_s4)),
        "tipos_C12": len(set(types_c12)),
        "cruzada_en_C12": {c: category["C12"].count(c) for c in cats},
        "separable_en_algun_corte": sum(any(r["dependencias"][cut]["cruzada"] == "separable" for cut, _, _ in CUTS) for r in records),  # type: ignore[index]
        "mutua_en_los_3_cortes": sum(all(r["dependencias"][cut]["cruzada"] == "mutua" for cut, _, _ in CUTS) for r in records),  # type: ignore[index]
        "categoria_cambia_con_el_corte": sum(len({category[cut][i] for cut, _, _ in CUTS}) > 1 for i in range(N)),
        "con_al_menos_un_atractor": sum(bool(r["atractores"]) for r in records),
        "robustez_cambia_con_el_corte": sum(len({robust[cut][i] for cut, _, _ in CUTS}) > 1 for i in range(N)),
        "scheduler_puntos_fijos_distintos": sum(fixed_points_differ(r) for r in records),
        "scheduler_atractores_distintos": sum(r["scheduler"]["atractores_distintos"] for r in records),  # type: ignore[index]
        "con_ciclo_sincronico_por_cruzada": {c: sum(any(len(a) >= 2 for a in r["atractores"]) and r["dependencias"]["C12"]["cruzada"] == c for r in records) for c in cats},  # type: ignore[index]
        "ciclo_muere_sin_reloj_por_cruzada": {c: sum(r["scheduler"]["ciclo_muere_sin_reloj"] and r["dependencias"]["C12"]["cruzada"] == c for r in records) for c in cats},  # type: ignore[index]
        "lesion_veredicto_difiere_congelar_vs_fijar0": sum(r["lesion"][v]["congelar"] != r["lesion"][v]["fijar0"] for r in records for v in ("x1", "x2")),  # type: ignore[index]
        "lesion_casos": 2 * len(records),
        "perfiles_consecuencia_K": len(set(k)),
        "perfiles_robustez_C12": len(set(robust["C12"])),
        "H_K_bits": round(entropy(k), 6),
        "vocabularios": vocabularies,
    }
    return {"controles": controls(records, category, robust, graphs, types_s4), "deterministico": deterministic}


def fixed_points_differ(record: dict[str, object]) -> bool:
    schedule = record["scheduler"]  # type: ignore[assignment]
    sync = {tuple(a) for a in schedule["sinc"] if len(a) == 1}
    return sync != {tuple(a) for a in schedule["sec12"] if len(a) == 1} or sync != {tuple(a) for a in schedule["sec21"] if len(a) == 1}


def controls(records: list[dict[str, object]], category: dict[str, list[object]], robust: dict[str, list[object]], graphs: dict[str, list[object]], types_s4: list[object], oeis_status: str = "NO_VERIFICABLE") -> dict[str, object]:
    cut_counts = {cut: {c: category[cut].count(c) for c in ("separable", "mutua", "unidir")} for cut, _, _ in CUTS}
    h_robust = {cut: entropy(robust[cut]) for cut, _, _ in CUTS}
    i_graph = {cut: mutual_information(graphs[cut], robust[cut]) for cut, _, _ in CUTS}
    i_type = {cut: mutual_information(types_s4, robust[cut]) for cut, _, _ in CUTS}
    symmetric = len({canonical_json(v) for v in cut_counts.values()}) == 1 and max(h_robust.values()) - min(h_robust.values()) < 1e-12 and max(i_graph.values()) - min(i_graph.values()) < 1e-12 and max(i_type.values()) - min(i_type.values()) < 1e-12
    intrinsic: dict[object, set[str]] = defaultdict(set)
    for record in records:
        f = tuple(record["F"])  # type: ignore[arg-type]
        intrinsic[tuple(record["tipo_S4"])] .add(robustness(f, record["atractores"], (1, 2, 3)))  # type: ignore[arg-type]
    return {
        "finitud": {"metodo": "atractores por las cuatro orbitas", "resultado": all(r["atractores"] for r in records), "estado": "PASS" if all(r["atractores"] for r in records) else "FAIL"},
        "puntos_fijos_y_scheduler": {"metodo": "comparacion de atractores unitarios", "resultado": not any(fixed_points_differ(r) for r in records), "estado": "PASS" if not any(fixed_points_differ(r) for r in records) else "FAIL"},
        "simetria_entre_cortes": {"metodo": "conteos, H e I por corte", "resultado": symmetric, "estado": "PASS" if symmetric else "FAIL"},
        "ancla_oeis_A001372": {"metodo": "A001372, termino n=4 = 19; conteo de tipos_S4", "resultado": len(set(types_s4)) == 19, "estado": "PASS" if oeis_status == "PASS" and len(set(types_s4)) == 19 else "FAIL" if oeis_status == "PASS" else "NO_VERIFICABLE"},
        "guardia_consecuencias_intrinsecas": {"metodo": "robustez con mascaras 1,2,3 por tipo_S4", "resultado": all(len(values) == 1 for values in intrinsic.values()), "estado": "PASS" if all(len(values) == 1 for values in intrinsic.values()) else "FAIL"},
        "mascaras_derivadas": {"metodo": "busqueda exhaustiva de C4", "resultado": {name: list(pair) for name, pair in MASKS.items()}, "estado": "PASS"},
    }


def write_records(records: list[dict[str, object]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(canonical_json(record) + "\n" for record in records), encoding="ascii")


def write_json(value: object, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(canonical_json(value) + "\n", encoding="ascii")


def run(output: Path, oeis_status: str = "NO_VERIFICABLE") -> tuple[list[dict[str, object]], dict[str, object]]:
    records = [analyze(tuple(f)) for f in all_dynamics()]
    report = summary(records)
    oeis_control = report["controles"]["ancla_oeis_A001372"]  # type: ignore[index]
    oeis_control["estado"] = "PASS" if oeis_status == "PASS" and oeis_control["resultado"] else "FAIL" if oeis_status == "PASS" else "NO_VERIFICABLE"
    write_records(records, output / "por_sistema.jsonl")
    write_json(report, output / "resumen.json")
    write_json(report["controles"], output / "CONTROL_REPORT.json")
    return records, report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT)
    parser.add_argument("--oeis-status", choices=("PASS", "FAIL", "NO_VERIFICABLE"), default="NO_VERIFICABLE")
    args = parser.parse_args()
    run(args.output, args.oeis_status)


if __name__ == "__main__":
    main()
