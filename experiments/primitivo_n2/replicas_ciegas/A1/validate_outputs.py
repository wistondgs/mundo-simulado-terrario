#!/usr/bin/env python3
"""Independent structural and aggregate validation of frozen result files."""
import json
import math
import sys
from collections import Counter, defaultdict
from pathlib import Path


def canon(value):
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)


def tup(value):
    return tuple(tup(x) for x in value) if isinstance(value, list) else value


def entropy(values):
    n = len(values)
    return -sum(c / n * math.log2(c / n) for c in Counter(values).values())


def mi(a, b):
    n, ca, cb, joint = len(a), Counter(a), Counter(b), Counter(zip(a, b))
    return sum(c / n * math.log2(c * n / (ca[x] * cb[y])) for (x, y), c in joint.items())


def comb_log(n, k):
    return math.lgamma(n + 1) - math.lgamma(k + 1) - math.lgamma(n - k + 1)


def expected_mi(a, b):
    n, answer = len(a), 0.0
    for ai in Counter(a).values():
        for bj in Counter(b).values():
            for z in range(max(1, ai + bj - n), min(ai, bj) + 1):
                p = math.exp(comb_log(ai, z) + comb_log(n - ai, bj - z) - comb_log(n, bj))
                answer += z / n * math.log2(n * z / (ai * bj)) * p
    return answer


def metrics(a, b):
    h_a, h_b, observed, expected = entropy(a), entropy(b), mi(a, b), expected_mi(a, b)
    return {"I_bits": round(observed, 6), "E_I_permutacion_exacta_bits": round(expected, 6), "AMI_max": round((observed - expected) / (max(h_a, h_b) - expected), 6)}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def no_nonfinite(value):
    if isinstance(value, float):
        require(math.isfinite(value), "non-finite JSON number")
    elif isinstance(value, dict):
        for item in value.values(): no_nonfinite(item)
    elif isinstance(value, list):
        for item in value: no_nonfinite(item)


def main():
    root = Path(sys.argv[1]) if len(sys.argv) == 2 else Path(".")
    raw = (root / "por_sistema.jsonl").read_text(encoding="ascii").splitlines()
    records = [json.loads(line) for line in raw]
    require(len(records) == 256, "must contain exactly 256 records")
    required = {"F", "atractores", "dependencias", "lesion", "periodos", "robustez", "scheduler", "tipo_C12", "tipo_S4"}
    for index, (line, record) in enumerate(zip(raw, records)):
        require(set(record) == required, f"incorrect top-level keys at {index}")
        expected_f = [index // 64, (index // 16) % 4, (index // 4) % 4, index % 4]
        require(record["F"] == expected_f, f"wrong enumeration at {index}")
        require(canon(record) == line, f"noncanonical serialization at {index}")
        no_nonfinite(record)
    summary = json.loads((root / "resumen.json").read_text(encoding="ascii"))
    det = summary["deterministico"]
    cuts, cats = ("C12", "C13", "C23"), ("separable", "mutua", "unidir")
    category = {c: [r["dependencias"][c]["cruzada"] for r in records] for c in cuts}
    robust = {c: [r["robustez"][c] for r in records] for c in cuts}
    types_s4, types_c12 = [tup(r["tipo_S4"]) for r in records], [tup(r["tipo_C12"]) for r in records]
    periods = [tup(r["periodos"]) for r in records]
    k = list(zip(periods, robust["C12"]))
    require(det["n_dinamicas"] == 256 and det["tipos_S4"] == len(set(types_s4)) and det["tipos_C12"] == len(set(types_c12)), "basic aggregate mismatch")
    require(det["cruzada_en_C12"] == {c: category["C12"].count(c) for c in cats}, "cross-category mismatch")
    require(det["H_K_bits"] == round(entropy(k), 6), "H(K) mismatch")
    consequences = {"K": k, "solo_robustez_C12": robust["C12"], "solo_periodos": periods}
    vocabularies = {
        "grafo_dependencias_C12": [tup(r["dependencias"]["C12"]["grafo"]) for r in records],
        "cruzada_C12": category["C12"], "tipo_S4": types_s4,
    }
    for name, labels in vocabularies.items():
        report = det["vocabularios"][name]
        classes = defaultdict(list)
        for i, label in enumerate(labels): classes[label].append(i)
        require(report["clases"] == len(classes), f"class count mismatch: {name}")
        require(report["H_V_bits"] == round(entropy(labels), 6), f"entropy mismatch: {name}")
        for target, values in consequences.items():
            require(report["consecuencias"][target] == metrics(labels, values), f"information mismatch: {name}/{target}")
    statuses = [entry["estado"] for entry in summary["controles"].values()]
    require(all(status == "PASS" for status in statuses), "a mandatory control did not pass")
    print("VALIDATION=PASS")


if __name__ == "__main__":
    main()
