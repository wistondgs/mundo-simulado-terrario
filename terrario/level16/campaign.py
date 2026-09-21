"""La campaña confirmatoria · una sola vez, con las semillas preregistradas.

Corre el intervalo según la regla de consumo (Enmienda 01), vive cada semilla
válida, construye los cuatro brazos sobre la misma vida, mide sobre el banco POST
inmutable, interviene causalmente y clasifica según la Enmienda 03.

El criterio primario es uno solo:

    IC95_inferior( L(SHUFFLED) - L(FULL) )  >  0

El banco poblacional aparece aquí como **diagnóstico exploratorio** y está
marcado como tal: medido, invierte el signo del resultado, y el oráculo §8 le
prohíbe expresamente ser gate.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from terrario.level16 import gates as gate_module
from terrario.level16.arms import (
    StaticBitcount, audit_shuffle, frozen, full, temporal_shuffled,
)
from terrario.level16.causal import CausalProbe, probe
from terrario.level16.gates import GateReport
from terrario.level16.life import ACQUISITION_STEPS, POST_STEPS, Life, live
from terrario.level16.metrics import brier_change, log_loss
from terrario.level16.seeds import SeedLedger, consume_seeds
from terrario.level16.shadow import AnalyticShadow, teachability
from terrario.level16.temporal import TemporalModel
from terrario.level16.world import build_world

#: Enmienda 03 §3. Declarados antes de la campaña, no derivados de ella.
TEACHABLE_FLOOR = 0.05
CAPTURE_FRACTION = 0.25


@dataclass(frozen=True)
class LifeOutcome:
    """Una vida leída entera, con su clasificación y todo lo que la sostiene."""

    seed: int
    classification: str
    available: float
    gained: float
    temporal_gain: float
    loss_full: float
    loss_frozen: float
    loss_shuffled: float
    loss_shadow: float
    brier_full: float
    brier_bitcount: float
    beta: float
    updates: int
    causal: bool
    stratum: str
    component_size: int
    reachable_observations: int
    change_rate: float
    trajectory_hash: str
    shuffle_destructive: bool
    shuffle_distance_full: float
    shuffle_distance_shuffled: float


def classify(available: float, gained: float, temporal_gain: float,
             updates: int, moved: bool, causal: bool) -> str:
    """El criterio de la Enmienda 03 §3, en el mismo orden en que está escrito."""
    if updates == 0 or not moved:
        return "N-PLASTICIDAD"
    if available <= TEACHABLE_FLOOR:
        return "N-EXPERIENCIA"
    if gained < CAPTURE_FRACTION * available:
        return "N-EXPERIENCIA"
    if gained > 0 and temporal_gain > 0 and causal:
        return "POSITIVO"
    return "NEGATIVO VERDADERO"


def read_life(life: Life) -> tuple[LifeOutcome, CausalProbe]:
    """Los cuatro brazos, la sombra y la intervención, sobre un banco fijo."""
    aprendido, congelado = full(life), frozen(life)
    barajado = temporal_shuffled(life)
    control = StaticBitcount.fitted(life)
    sombra = AnalyticShadow(build_world(life.seed))

    l_full = log_loss(aprendido, life.post)
    l_frozen = log_loss(congelado, life.post)
    l_shuffled = log_loss(barajado, life.post)
    l_shadow = log_loss(sombra, life.post)

    prueba = probe(aprendido, life.post)
    auditoria = audit_shuffle(life, aprendido, barajado)
    disponible = teachability(sombra, life.post)

    salida = LifeOutcome(
        seed=life.seed,
        classification=classify(
            disponible, l_frozen - l_full, l_shuffled - l_full,
            aprendido.updates,
            aprendido.fingerprint() != TemporalModel.naive().fingerprint(),
            prueba.state_is_causal),
        available=disponible,
        gained=l_frozen - l_full,
        temporal_gain=l_shuffled - l_full,
        loss_full=l_full, loss_frozen=l_frozen, loss_shuffled=l_shuffled,
        loss_shadow=l_shadow,
        brier_full=brier_change(aprendido, life.post),
        brier_bitcount=brier_change(control, life.post),
        beta=control.beta,
        updates=aprendido.updates,
        causal=prueba.state_is_causal,
        stratum=life.instruments.stratum,
        component_size=life.instruments.component_size,
        reachable_observations=life.instruments.reachable_observations,
        change_rate=life.instruments.change_rate,
        trajectory_hash=life.instruments.trajectory_hash,
        shuffle_destructive=auditoria.destructive,
        shuffle_distance_full=auditoria.full_distance_to_marginal,
        shuffle_distance_shuffled=auditoria.shuffled_distance_to_marginal,
    )
    return salida, prueba


@dataclass(frozen=True)
class CampaignResult:
    ledger: SeedLedger
    outcomes: tuple[LifeOutcome, ...]
    report: GateReport

    @property
    def temporal_gain(self) -> np.ndarray:
        return np.array([o.temporal_gain for o in self.outcomes])

    @property
    def interval_lower(self) -> float:
        v = self.temporal_gain
        return float(v.mean() - 1.96 * v.std(ddof=1) / np.sqrt(len(v)))

    @property
    def primary_criterion_met(self) -> bool:
        return self.interval_lower > 0

    @property
    def verdict(self) -> str:
        if not self.report.all_passed:
            return "INVÁLIDO"
        clases = {o.classification for o in self.outcomes}
        if clases == {"POSITIVO"} and self.primary_criterion_met:
            return "POSITIVO"
        return "MIXTO" if "POSITIVO" in clases else "NEGATIVO"


def run_campaign(steps: int = ACQUISITION_STEPS,
                 post_steps: int = POST_STEPS) -> CampaignResult:
    """Correr el intervalo entero. Una sola vez, sin mirar y volver a lanzar."""
    libro = consume_seeds()
    vidas = [live(s, steps=steps, post_steps=post_steps) for s in libro.lives]
    leidas = [read_life(v) for v in vidas]
    salidas = tuple(s for s, _ in leidas)

    perdidas = {
        "full": np.array([s.loss_full for s in salidas]),
        "frozen": np.array([s.loss_frozen for s in salidas]),
        "shuffled": np.array([s.loss_shuffled for s in salidas]),
    }
    reporte = GateReport()
    gate_module.gate_lineage_isolation(reporte)
    gate_module.gate_action_provenance(reporte, vidas[0])
    gate_module.gate_motor_serialisation(reporte, libro.lives[0])
    gate_module.gate_no_reward_signals(reporte)
    gate_module.gate_learner_is_blind(reporte)
    gate_module.gate_trajectory_parity(reporte, vidas[0])
    gate_module.gate_experience_was_sufficient(reporte, vidas[0])
    gate_module.gate_beats_its_own_past(reporte, perdidas)
    gate_module.gate_beats_shuffled(reporte, perdidas, salidas)
    gate_module.gate_state_is_causal(reporte, [p for _, p in leidas])
    gate_module.gate_measurement_is_passive(reporte, vidas[0])
    gate_module.gate_bitcount_cannot_explain_primary(reporte, vidas[0])

    return CampaignResult(libro, salidas, reporte)


def population_bank_diagnostic(steps: int = ACQUISITION_STEPS) -> dict[str, float]:
    """DIAGNÓSTICO EXPLORATORIO. Nunca gate. Oráculo §8.

    Puntúa a cada ser contra transiciones de **otros** mundos. Mide
    generalización entre mundos, que 1.6 no declara, y por eso invierte el signo:
    cuanto más vive el organismo, peor puntúa aquí.
    """
    libro = consume_seeds()
    vidas = [live(s, steps=steps, post_steps=POST_STEPS) for s in libro.lives]
    banco = [par for v in vidas for par in v.post[:128]]
    propios = np.array([log_loss(full(v), v.post) for v in vidas])
    poblacional = np.array([log_loss(full(v), banco) for v in vidas])
    return {"banco_propio": float(propios.mean()),
            "banco_poblacional": float(poblacional.mean()),
            "frozen": float(np.log(16))}
