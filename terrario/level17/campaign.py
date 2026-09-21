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

#: Los trece. Que el runner ejecute menos es fatal, no una nota al pie.
REQUIRED_GATES = tuple(f"L17-{i}" for i in range(13))

PREDECESSOR_STEPS = 4096
ACQUISITION_STEPS = 1024
POST_STEPS = 2048
PAIRS_REQUIRED = 16
NULL_REPLICAS = 32


class CampaignInvalid(RuntimeError):
    """Un defecto nuestro, no del mundo. La campaña se declara INVÁLIDA."""


class LedgerIncomplete(CampaignInvalid):
    """La defensa estructural contra otro D-4.

    En V1 el runner ejecutaba **cero** de los trece gates: los trece se
    calcularon en un script escrito después de abrir las semillas, y el «13/13»
    se construyó fuera de la ruta congelada. Ya no es posible: el ledger tiene
    que contener `L17-0 … L17-12`, `L17-8` tiene que aparecer **una vez por
    vida**, con exactamente 32 muestras, y todas procedentes de esa misma vida.
    """


@dataclass(frozen=True)
class GateEntry:
    """Una ejecución de gate, con su procedencia. Sin esto no hay auditoría."""

    name: str
    scope: str                       # "campaign" o "seed:<n>"
    passed: bool
    evidence: str
    null_size: int | None = None
    null_origin: tuple[int, ...] = ()


def verify_ledger(ledger, seeds, required_null: int = NULL_REPLICAS) -> None:
    """Meta-verificación de infraestructura. No es un gate científico nuevo."""
    ejecutados = {e.name for e in ledger}
    faltan = set(REQUIRED_GATES) - ejecutados
    if faltan:
        raise LedgerIncomplete(
            f"el runner no ejecutó {sorted(faltan)}; V1 falló exactamente así")
    sobran = ejecutados - set(REQUIRED_GATES)
    if sobran:
        raise LedgerIncomplete(f"gates no reconocidos en el ledger: {sorted(sobran)}")

    por_vida = [e for e in ledger if e.name == "L17-8"]
    alcance = {e.scope for e in por_vida}
    esperado = {f"seed:{s}" for s in seeds}
    if alcance != esperado:
        raise LedgerIncomplete(
            f"L17-8 debe ejecutarse una vez por vida; faltan "
            f"{sorted(esperado - alcance)} y sobran {sorted(alcance - esperado)}")
    for entrada in por_vida:
        if entrada.null_size != required_null:
            raise LedgerIncomplete(
                f"{entrada.scope}: nula de {entrada.null_size} permutaciones, "
                f"el protocolo exige {required_null}")
        propia = int(entrada.scope.split(":")[1])
        if set(entrada.null_origin) != {propia}:
            raise LedgerIncomplete(
                f"{entrada.scope}: la nula mezcla vidas "
                f"{sorted(set(entrada.null_origin))}; debe venir sólo de la suya")


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


def _null_world_entry(seed: int, life_b, replicas: int = NULL_REPLICAS) -> GateEntry:
    """`L17-8` de UNA vida: 32 permutaciones estratificadas de **su propia** vida B.

    El observado es el `D_C^B` real de esa vida; la nula, el mismo estadístico
    bajo intercambiabilidad de las etiquetas de acción condicionada a `O_t`. No se
    mezclan muestras de otras vidas ni se agregan las dieciséis para decidir una.
    """
    from terrario.level17 import gates as gate_module

    previos = [a for a, _, _ in life_b.acquisition]
    comandos = [k for _, k, _ in life_b.acquisition]
    siguientes = [c for _, _, c in life_b.acquisition]
    puntuar = lambda f: -float(np.mean([np.log(f(a, k, c)) for a, k, c in life_b.post]))
    base = puntuar(lambda a, k, c: life_b.no_action.probability(a, c))
    observado = base - puntuar(
        lambda a, k, c: life_b.acquired.probability(a, EfferenceCopy(k), c))

    nulas = []
    for replica in range(1, replicas + 1):
        modelo = shuffled.build(life_b.inherited, previos, comandos, siguientes,
                                seed, replica)
        nulas.append(base - puntuar(
            lambda a, k, c: modelo.probability(a, EfferenceCopy(k), c)))

    reporte = gate_module.GateReport()
    gate_module.gate_null_world(reporte, observado, nulas)
    resultado = reporte.results[0]
    return GateEntry("L17-8", f"seed:{seed}", resultado.passed, resultado.evidence,
                     null_size=len(nulas), null_origin=tuple([seed] * len(nulas)))


def _read_pair(seed: int, live_two_phase, build_world_fn):
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

    entrada_nula = _null_world_entry(seed, life_b)

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
    ), entrada_nula, life_a


@dataclass(frozen=True)
class CampaignResult:
    window: tuple[int, ...]
    consumed: tuple[int, ...] = field(default_factory=tuple)
    skipped: tuple[int, ...] = field(default_factory=tuple)
    pairs: tuple[PairOutcome, ...] = field(default_factory=tuple)
    ledger: tuple[GateEntry, ...] = field(default_factory=tuple)

    @property
    def gates_executed(self) -> set[str]:
        return {e.name for e in self.ledger}

    @property
    def all_gates_passed(self) -> bool:
        return all(e.passed for e in self.ledger)

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


def _campaign_gates(pairs, life, build_world_fn):
    """Los doce gates de alcance campaña. `L17-8` ya entró, uno por vida."""
    from terrario.level1.world import ALL_OBSERVATIONS
    from terrario.level16.temporal import OBSERVATION_INDEX
    from terrario.level17 import exposure as exposure_module
    from terrario.level17 import gates as gate_module
    from terrario.level17.contingency import ActionContingencyModel

    reporte = gate_module.GateReport()
    semillas = [p.seed for p in pairs]

    gate_module.gate_lineage(reporte)
    gate_module.gate_world_pair(
        reporte, semillas,
        lambda sd: state_kernels(sd, ActuatorWiring.sampled(sd)))
    gate_module.gate_action_provenance(
        reporte, life,
        _replay_commands)
    gate_module.gate_efference_purity(reporte, EfferenceCopy)
    gate_module.gate_incremental_invariant(
        reporte, life.inherited, ActionContingencyModel,
        list(ALL_OBSERVATIONS), list(ALL_COMMANDS))
    gate_module.gate_baseline_parity(reporte, life)

    sombra = AnalyticActionShadow(build_world_fn(life.seed), life.wiring)
    exposicion = exposure_module.measure(life.visits, sombra.divergence_matrix(),
                                         sombra.p_reference)

    def recontar(v):
        conteo = np.zeros((16, 4))
        for anterior, comando, _s in v.acquisition:
            conteo[OBSERVATION_INDEX[anterior], ALL_COMMANDS.index(comando)] += 1
        return conteo

    gate_module.gate_exposure(reporte, life, exposicion, sombra.divergence_matrix(),
                              sombra.p_reference, recontar)
    gate_module.gate_action_acquisition(reporte, [p.gamma for p in pairs])

    previos = [a for a, _, _ in life.acquisition]
    comandos = [k for _, k, _ in life.acquisition]
    siguientes = [c for _, _, c in life.acquisition]
    brazo = shuffled.build(life.inherited, previos, comandos, siguientes,
                           life.seed, 0)
    auditoria = shuffled.audit(brazo, life.inherited, previos, comandos, siguientes,
                               life.seed, replicas=NULL_REPLICAS)
    gate_module.gate_action_necessity(
        reporte, auditoria,
        float(np.mean([p.shuffled_advantage for p in pairs])),
        float(np.mean([p.false_action_advantage for p in pairs])))
    gate_module.gate_opaque_mapping(reporte)

    modelo = ActionContingencyModel(life.inherited)
    for anterior, comando, siguiente in life.acquisition:
        modelo.observe(anterior, EfferenceCopy(comando), siguiente)
    puntuar = lambda m: -float(np.mean([
        np.log(m.probability(a, EfferenceCopy(k), c)) for a, k, c in life.post]))
    gate_module.gate_internal_localization(reporte, modelo, life.inherited, puntuar)

    from terrario.level17.life import live_two_phase as runner
    gate_module.gate_passivity_replay(
        reporte, modelo, puntuar,
        lambda: runner(life.seed, 256, 256, post_steps=64,
                       wiring=life.wiring).trajectory_hash)

    return [GateEntry(r.name, "campaign", r.passed, r.evidence)
            for r in reporte.results]


def _replay_commands(seed: int, count: int):
    from terrario.level16.motor import EndogenousMotor
    from terrario.level16.world import motor_stream
    motor = EndogenousMotor(motor_stream(seed))
    return [ALL_COMMANDS[int(motor.next())] for _ in range(count)]


def run_campaign(window, live_two_phase=None, build_world_fn=build_world,
                 pairs_required: int = PAIRS_REQUIRED) -> CampaignResult:
    """Recorrer la ventana y devolver los pares crudos. No interpreta nada."""
    if live_two_phase is None:
        from terrario.level17.life import live_two_phase as runner
        live_two_phase = runner

    consumed: list[int] = []
    skipped: list[int] = []
    pairs: list[PairOutcome] = []
    ledger: list[GateEntry] = []
    primera_vida = None
    for seed in window:
        consumed.append(seed)
        if is_nonworld(describe_world(seed, build_world_fn(seed))):
            skipped.append(seed)          # única causa de reemplazo: física, previa
            continue
        kernel_a, kernel_b, signature = state_kernels(seed, ActuatorWiring.sampled(seed))
        from terrario.level17.gates import _action_information
        if not np.allclose(kernel_a.mean(axis=1), kernel_b.mean(axis=1)):
            raise CampaignInvalid(
                f"WORLD_PAIR_CONSTRUCTION_FAIL en {seed}: dinámica marginal distinta")
        # Un B estructuralmente roto muere AQUÍ, antes de vivir, y nunca llega a
        # L17-8 a disfrazarse de problema del aprendiz (§7 de la adjudicación).
        if _action_information(kernel_b, signature) > 1e-12:
            raise CampaignInvalid(
                f"WORLD_PAIR_CONSTRUCTION_FAIL en {seed}: I_B(A;O'|O) > 0")
        par, entrada_nula, vida_a = _read_pair(seed, live_two_phase, build_world_fn)
        pairs.append(par)
        ledger.append(entrada_nula)
        if primera_vida is None:
            primera_vida = vida_a
        if len(pairs) == pairs_required:
            break
    else:
        raise CampaignInvalid(
            f"ventana agotada con {len(pairs)} pares de {pairs_required}")
    ledger.extend(_campaign_gates(pairs, primera_vida, build_world_fn))
    verify_ledger(ledger, [p.seed for p in pairs])
    return CampaignResult(tuple(window), tuple(consumed), tuple(skipped),
                          tuple(pairs), tuple(ledger))
