"""Exposición · cuatro instrumentos donde antes había uno.

`D_E ≈ D_W` a 64 pasos **no** demuestra que la exposición esté resuelta. Puede
darse aunque el organismo haya visto una o dos veces muchos contextos `(o,a)`,
porque pesa la densidad informativa de lo visitado, no cuántas veces. La propia
medición lo delataba: `D_E ≈ D_W` mientras `D_K < 0`. No faltaba calidad
informativa — faltaba evidencia estadística para estimarla.

```
D_E_rate    nats estructurales por transición vivida
D_E_total   Σ_t d(O_t, A_t)            lo acumulado, no la tasa
C_OA        Σ p_ref(o,a) · 1[N_L(o,a) > 0]     cobertura ponderada de contextos
N_L         recuentos por contexto · mínimo, mediana, percentiles
```

La distinción que separan es la que 1.6 enseñó a no colapsar:

    encuentra información   ≠   ha acumulado bastantes muestras para aprenderla
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class Exposure:
    rate: float
    total: float
    weighted_coverage: float
    contexts_visited: int
    contexts_informative: int
    counts_min: int
    counts_median: float
    counts_p10: float
    counts_p90: float

    @property
    def summary(self) -> str:
        return (f"tasa {self.rate:.4f} · total {self.total:.1f} · cobertura "
                f"{self.weighted_coverage:.4f} · N mín {self.counts_min}")


def measure(visits: np.ndarray, divergence: np.ndarray,
            p_reference: np.ndarray, informative: float = 1e-9) -> Exposure:
    """`visits[o,a]` de la vida; `divergence[o,a]` del oráculo del mundo."""
    total_visits = visits.sum()
    weighted = float(np.sum((visits / total_visits) * divergence)) if total_visits else 0.0
    accumulated = float(np.sum(visits * divergence))

    reachable = p_reference > 0
    informative_mask = reachable & (divergence > informative)
    seen = visits > 0
    coverage = float(np.sum(p_reference[informative_mask & seen]))
    coverage /= float(np.sum(p_reference[informative_mask])) or 1.0

    counts = visits[informative_mask]
    return Exposure(
        rate=weighted,
        total=accumulated,
        weighted_coverage=coverage,
        contexts_visited=int(np.sum(seen & reachable)),
        contexts_informative=int(np.sum(informative_mask)),
        counts_min=int(counts.min()) if counts.size else 0,
        counts_median=float(np.median(counts)) if counts.size else 0.0,
        counts_p10=float(np.percentile(counts, 10)) if counts.size else 0.0,
        counts_p90=float(np.percentile(counts, 90)) if counts.size else 0.0,
    )
