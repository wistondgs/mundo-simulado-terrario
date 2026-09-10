# Causal identifiability

The audit checks whether only the target changed and whether capacity, information, compute, training, paired seeds, and environment were matched. Its bounded conclusions are `STRONG_IDENTIFICATION`, `PARTIAL_IDENTIFICATION`, `DESCRIPTIVE_ONLY`, and `INVALID_COMPARISON`.

Controls cover baseline, placebo/sham, equal compute, equal parameters, frozen learning, architecture matching, random manipulation, temporal comparison, and transfer-only evaluation. A4 versus A0 is explicitly not a clean causal control unless capacity, information, compute, and training exposure are matched.

The confounder registry includes compute, parameter count, observation/action access, memory, exposure, reward, initialization, seeds, environment, leakage, survival bias, opportunity availability, and metric/threshold artifacts. Unmitigated critical confounders block executable compilation. Causal language must never exceed the achieved identification level.
