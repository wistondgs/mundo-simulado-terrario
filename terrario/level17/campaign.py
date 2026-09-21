"""La campaña confirmatoria de 1.7 · exactamente como la selló `ac12cc3`.

Una unidad = **un par A/B de la misma semilla y topología**. Nunca una transición.

```
consumo         ascendente desde la ventana ciega, parar en el decimosexto par válido
reemplazo       SÓLO por condición física anterior a la vida
invalidación    violar D_W^A > 0 o D_W^B = 0  ->  WORLD_PAIR_CONSTRUCTION_FAIL
endpoint        Γ_i = D_C^A_i − D_C^B_i
criterio        CI95_inferior( media de Γ ) > 0
```

Un resultado negativo válido **no** detiene la campaña ni permite sustituir la
vida: esa vida pertenece al denominador.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from terrario.level16.structure import describe_world, is_nonworld
from terrario.level16.world import build_world
from terrario.level17 import exposure as exposure_module
from terrario.level17 import shuffled
from terrario.level17.efference import ALL_COMMANDS, EfferenceCopy
from terrario.level17.shadow import AnalyticActionShadow
from terrario.level17.twin import MarginalisedBody, state_kernels, twin_stream
from terrario.level17.wiring import ActuatorWiring

PREDECESSOR_STEPS = 4096
ACQUISITION_STEPS = 1024
POST_STEPS = 2048
PAIRS_REQUIRED = 16
NULL_REPLICAS = 32


class CampaignInvalid(RuntimeError):
    """Un defecto nuestro, no del mundo. La campaña se declara INVÁLIDA."""


@dataclass(frozen=True)
class PairOutcome:
    """Todo lo de un par, guardado ANTES de mirar ningún agregado."""

    seed: int
    d_w_a: float
    d_w_b: float
    d_k_action_a: float
    d_k_action_b: float
    d_c_a: float
    d_c_b: float
    gamma: float
    e_rate: float
    e_total: float
    coverage: float
    counts_min: int
    shuffled_advantage: float
    shuffled_destructive: bool
    false_action_advantage: float
    lesion_loss: float
    restored_exactly: bool
    inherited_intact: bool
    component_size: int
    trajectory_hash_a: str
    trajectory_hash_b: str


def _losses(life):
    puntuar = lambda f: -float(np.mean([np.log(f(a, k, c)) for a, k, c in life.post]))
    return (puntuar(lambda a, k, c: life.no_action.probability(a, c)),
            puntuar(lambda a, k, c: life.acquired.probability(a, EfferenceCopy(k), c)))


def _false_action_loss(life, rng) -> float:
    """Ablación de consulta: `K_T` intacto, pero en POST llega un token falso."""
    return -float(np.mean([
        np.log(life.acquired.probability(
            a, EfferenceCopy(ALL_COMMANDS[int(rng.integers(4))]), c))
        for a, _k, c in life.post]))


def _read_pair(seed: int, live_two_phase, build_world_fn) -> PairOutcome:
    import terrario.level17.life as life_module

    wiring = ActuatorWiring.sampled(seed)
    kernel_a, kernel_b, signature = state_kernels(seed, wiring)

    life_a = live_two_phase(seed, PREDECESSOR_STEPS, ACQUISITION_STEPS,
                            post_steps=POST_STEPS, wiring=wiring)
    real = life_module.build_world
    try:
        life_module.build_world = lambda s: MarginalisedBody(build_world_fn(s),
                                                            twin_stream(s))
        life_b = live_two_phase(seed, PREDECESSOR_STEPS, ACQUISITION_STEPS,
                                post_steps=POST_STEPS, wiring=wiring)
    finally:
        life_module.build_world = real

    shadow_a = AnalyticActionShadow(build_world_fn(seed), wiring)
    shadow_b = AnalyticActionShadow.marginalised(shadow_a)

    l_na_a, l_m1_a = _losses(life_a)
    l_na_b, l_m1_b = _losses(life_b)

    exposure = exposure_module.measure(life_a.visits, shadow_a.divergence_matrix(),
                                       shadow_a.p_reference)

    previos = [a for a, _, _ in life_a.acquisition]
    comandos = [k for _, k, _ in life_a.acquisition]
    siguientes = [c for _, _, c in life_a.acquisition]
    brazo = shuffled.build(life_a.inherited, previos, comandos, siguientes, seed, 0)
    audit = shuffled.audit(brazo, life_a.inherited, previos, comandos, siguientes,
                           seed, replicas=NULL_REPLICAS)
    puntuar = lambda f: -float(np.mean([np.log(f(a, k, c)) for a, k, c in life_a.post]))
    l_shuffled = puntuar(lambda a, k, c: brazo.probability(a, EfferenceCopy(k), c))
    l_false = _false_action_loss(life_a, np.random.default_rng([seed, 256]))

    aprendido = life_a.acquired.acquired_snapshot()
    con_estado = l_m1_a
    life_a.acquired.lesion()
    lesionado = _losses(life_a)[1]
    intacto = life_a.acquired.inherited_is_intact()
    life_a.acquired.load_acquired(aprendido)
    restaurado = _losses(life_a)[1]

    return PairOutcome(
        seed=seed,
        d_w_a=shadow_a.available(),
        d_w_b=shadow_b.available(),
        d_k_action_a=(shadow_a.marginal_learner_error(life_a.no_action)
                      - shadow_a.learner_error(life_a.acquired)),
        d_k_action_b=(shadow_b.marginal_learner_error(life_b.no_action)
                      - shadow_b.learner_error(life_b.acquired)),
        d_c_a=l_na_a - l_m1_a,
        d_c_b=l_na_b - l_m1_b,
        gamma=(l_na_a - l_m1_a) - (l_na_b - l_m1_b),
        e_rate=exposure.rate, e_total=exposure.total,
        coverage=exposure.weighted_coverage, counts_min=exposure.counts_min,
        shuffled_advantage=l_na_a - l_shuffled,
        shuffled_destructive=audit.destructive,
        false_action_advantage=l_na_a - l_false,
        lesion_loss=lesionado,
        restored_exactly=restaurado == con_estado,
        inherited_intact=intacto,
        component_size=describe_world(seed, build_world_fn(seed)).component_size,
        trajectory_hash_a=life_a.trajectory_hash,
        trajectory_hash_b=life_b.trajectory_hash,
    )


@dataclass(frozen=True)
class CampaignResult:
    window: tuple[int, ...]
    consumed: tuple[int, ...] = field(default_factory=tuple)
    skipped: tuple[int, ...] = field(default_factory=tuple)
    pairs: tuple[PairOutcome, ...] = field(default_factory=tuple)

    @property
    def gammas(self) -> np.ndarray:
        return np.array([p.gamma for p in self.pairs])

    @property
    def interval_lower(self) -> float:
        g = self.gammas
        return float(g.mean() - 1.96 * g.std(ddof=1) / np.sqrt(len(g)))

    @property
    def primary_criterion_met(self) -> bool:
        return self.interval_lower > 0


def run_campaign(window, live_two_phase=None, build_world_fn=build_world,
                 pairs_required: int = PAIRS_REQUIRED) -> CampaignResult:
    """Recorrer la ventana y devolver los pares crudos. No interpreta nada."""
    if live_two_phase is None:
        from terrario.level17.life import live_two_phase as runner
        live_two_phase = runner

    consumed: list[int] = []
    skipped: list[int] = []
    pairs: list[PairOutcome] = []
    for seed in window:
        consumed.append(seed)
        if is_nonworld(describe_world(seed, build_world_fn(seed))):
            skipped.append(seed)          # única causa de reemplazo: física, previa
            continue
        kernel_a, kernel_b, signature = state_kernels(seed, ActuatorWiring.sampled(seed))
        if not np.allclose(kernel_a.mean(axis=1), kernel_b.mean(axis=1)):
            raise CampaignInvalid(
                f"WORLD_PAIR_CONSTRUCTION_FAIL en {seed}: dinámica marginal distinta")
        pairs.append(_read_pair(seed, live_two_phase, build_world_fn))
        if len(pairs) == pairs_required:
            break
    else:
        raise CampaignInvalid(
            f"ventana agotada con {len(pairs)} pares de {pairs_required}")
    return CampaignResult(tuple(window), tuple(consumed), tuple(skipped), tuple(pairs))
