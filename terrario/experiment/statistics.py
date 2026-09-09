"""Pure, reproducible analysis of completed evidence records."""

from __future__ import annotations

import math
from typing import Any

import numpy as np


def descriptive(values: list[float]) -> dict[str, float | int]:
    data = np.asarray([value for value in values if math.isfinite(value)], dtype=float)
    if not len(data):
        return {"n": 0, "mean": math.nan, "median": math.nan, "sd": math.nan, "iqr": math.nan, "min": math.nan, "max": math.nan}
    return {"n": len(data), "mean": float(data.mean()), "median": float(np.median(data)), "sd": float(data.std(ddof=1)) if len(data) > 1 else 0.0, "iqr": float(np.percentile(data, 75)-np.percentile(data, 25)), "min": float(data.min()), "max": float(data.max())}


def bootstrap_ci(values: list[float], seed: int = 0, samples: int = 10_000) -> tuple[float, float]:
    data = np.asarray([value for value in values if math.isfinite(value)], dtype=float)
    if not len(data): return (math.nan, math.nan)
    rng = np.random.default_rng(seed)
    means = rng.choice(data, size=(samples, len(data)), replace=True).mean(axis=1)
    return (float(np.quantile(means, .025)), float(np.quantile(means, .975)))


def paired_comparison(full: dict[int, float], ablation: dict[int, float], seed: int = 0) -> dict[str, Any]:
    pairs = [(full[key], ablation[key]) for key in sorted(set(full) & set(ablation)) if math.isfinite(full[key]) and math.isfinite(ablation[key])]
    differences = [left-right for left, right in pairs]
    wins = sum(value > 0 for value in differences); losses = sum(value < 0 for value in differences)
    scale = np.std(differences, ddof=1) if len(differences) > 1 else math.nan
    return {"n": len(differences), "mean_difference": float(np.mean(differences)) if differences else math.nan, "bootstrap_95_ci": bootstrap_ci(differences, seed), "paired_standardized_effect": float(np.mean(differences)/scale) if scale and math.isfinite(scale) and scale else math.nan, "wins": wins, "ties": len(differences)-wins-losses, "losses": losses}


def sensitivity_label(primary: float, alternatives: list[float], tolerance: float = .1) -> str:
    finite = [value for value in alternatives if math.isfinite(value)]
    if not finite: return "HIGHLY_FRAGILE"
    spread = max(abs(value-primary) for value in finite)
    return "THRESHOLD_STABLE" if spread <= tolerance else "THRESHOLD_SENSITIVE" if spread <= tolerance*2 else "HIGHLY_FRAGILE"
