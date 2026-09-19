"""`LEVEL1.2-QUALITATIVE-DISTANCE-01` · una realización completa.

Igual que 1.1, **no es un experimento confirmatorio**: el oráculo está sellado en
`docs/LEVEL12_ORACULO_PREREGISTRADO.md` y la pregunta es si la implementación
reproduce el mecanismo diseñado.

Lo que sí es nuevo: **el techo no es cero**. El sensor es ambiguo por
construcción y el mejor predictor posible se queda en `8/55`. Por primera vez en
el linaje el organismo no puede acertar siempre, y el criterio no es la
perfección sino la distancia al mejor conocimiento que su sensor permite.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from terrario.level11.cue import CueSemantics, CueToken
from terrario.level11.metrics import alignment_rate_expected
from terrario.level11.world import Direction, Observation
from terrario.level12.agent import Level12Agent
from terrario.level12.inherited import reconstruct
from terrario.level12.metrics import (
    ACCURACY_ORACLE, BS_IGNORANT, BS_JOINT_ORACLE, BS_ORACLE, ORACLE,
    balanced_accuracy, body_association, body_association_envelope, confusion,
    delta_sensor_separation, direction_class_table, joint_population_brier,
    max_oracle_deviation, population_brier, single_variable_probe,
)
from terrario.level12.proximity import (
    BayesDistanceOracle, ConstantDistance, QualitativeDistanceModel,
)
from terrario.level12.reference import DistanceTruth
from terrario.level12.stream import (
    MIN_INFORMATIVE, N_DISTANCE, build_stream, train_distance,
)

#: Umbrales congelados en el preregistro. Derivados de la distribución muestral,
#: no heredados: el `0.02` del Nivel 1.1 haría caer el gate en el 99.99 % de las
#: campañas aunque el aprendiz fuera exacto.
BS_TOLERANCE = 0.1480
DEVIATION_TOLERANCE = 0.10
ENVELOPE_PERMUTATIONS = 10_000
ENVELOPE_PERCENTILE = 99.9


class BlindCore:
    """`B ≡ 1`, `Q ≡ 1`. El núcleo de SENSOR_ONLY: **es control, no organismo**.

    Existe para mostrar que clasificar distancia no implica poseer conocimiento
    corporal ni direccional.
    """

    def predict_body(self, observation: Observation, action: Direction) -> float:
        return 1.0

    def predict_orientation(self, cue: CueToken, action: Direction) -> float:
        return 1.0

    def predict(self, observation: Observation, cue: CueToken,
                action: Direction) -> float:
        return 1.0

    def act(self, observation: Observation, cue: CueToken,
            rng: np.random.Generator) -> Direction:
        return Direction(int(rng.integers(len(Direction))))

    def fingerprint(self) -> str:
        return "ciego"

    @property
    def intact(self) -> bool:
        return True


@dataclass
class SeedReport:
    seed: int
    fingerprint_before: str
    fingerprint_after: str
    informative_minimum: int
    physics_violations: int
    align_before: float
    align_after: float
    delta_separation: float
    direction_table: dict[CueToken, float] = field(default_factory=dict)
    body_stat: float = 0.0
    body_envelope: float = 0.0
    brier: dict[str, float] = field(default_factory=dict)
    posteriors: dict[str, tuple[float, ...]] = field(default_factory=dict)
    deviation: dict[str, float] = field(default_factory=dict)
    balanced_acc: dict[str, float] = field(default_factory=dict)
    joint: dict[str, tuple[float, float]] = field(default_factory=dict)
    probe: dict[str, Any] = field(default_factory=dict)

    @property
    def inherited_intact(self) -> bool:
        return self.fingerprint_before == self.fingerprint_after

    @property
    def motor_preserved(self) -> bool:
        return self.align_before == self.align_after

    def gates(self) -> dict[str, bool]:
        p = self.probe["FULL_12"]
        return {
            "L12-0 linaje": self.inherited_intact,
            "L12-2 cobertura": self.informative_minimum >= MIN_INFORMATIVE,
            "L12-3 adquisición": (
                self.brier["FULL_12"] < self.brier["FROZEN_DISTANCE"]
                and self.brier["FULL_12"] < self.brier["NO_DISTANCE"]
                and self.brier["FULL_12"] < self.brier["SHUFFLED_DISTANCE"]
                and self.brier["FULL_12"] <= BS_TOLERANCE),
            "L12-4 semántica": self.deviation["FULL_12"] <= DEVIATION_TOLERANCE,
            "L12-5 dirección": all(v == 0.5 for v in self.direction_table.values()),
            "L12-6 cuerpo": self.body_stat <= self.body_envelope,
            "L12-7 integración": p.zeros_exact(),
            "L12-8 motor": self.motor_preserved,
            "L12-10 pasividad": self.physics_violations == 0,
            "L12-11 sensor↔δ": self.delta_separation >= 0.10,
        }

    @property
    def passes(self) -> bool:
        return all(self.gates().values())


def run_seed(seed: int, *, semantics: CueSemantics | None = None) -> SeedReport:
    semantics = semantics or CueSemantics.identity()

    core = reconstruct(seed, semantics=semantics)
    antes = core.fingerprint()
    align_antes = alignment_rate_expected(core, semantics)

    stream = build_stream(seed, semantics, n=N_DISTANCE)

    h = QualitativeDistanceModel()
    train_distance(stream, h)
    h_shuffled = QualitativeDistanceModel()
    train_distance(stream, h_shuffled,
                   shuffle_rng=np.random.default_rng([seed, 24]))

    brazos: dict[str, Level12Agent] = {
        "FULL_12": Level12Agent(core, h),
        "NO_DISTANCE": Level12Agent(core, ConstantDistance(0.5), name="NO_DISTANCE"),
        "FROZEN_DISTANCE": Level12Agent(core, QualitativeDistanceModel(frozen=True),
                                        name="FROZEN_DISTANCE"),
        "SHUFFLED_DISTANCE": Level12Agent(core, h_shuffled, name="SHUFFLED_DISTANCE"),
        "SENSOR_ONLY": Level12Agent(BlindCore(), h, name="SENSOR_ONLY"),
        "BAYES_ORACLE": Level12Agent(core, BayesDistanceOracle(), name="BAYES_ORACLE"),
    }

    reporte = SeedReport(
        seed, antes, core.fingerprint(), stream.informative_minimum,
        stream.physics_violations, align_antes,
        alignment_rate_expected(brazos["FULL_12"], semantics),
        delta_sensor_separation(stream),
        direction_class_table(stream), body_association(stream),
        float(np.percentile(body_association_envelope(
            stream, rng=np.random.default_rng([seed, 25]),
            permutations=ENVELOPE_PERMUTATIONS), ENVELOPE_PERCENTILE)))

    for nombre, agente in brazos.items():
        reporte.brier[nombre] = population_brier(agente.predict_near)
        reporte.posteriors[nombre] = agente.proximity.posteriors()
        reporte.deviation[nombre] = max_oracle_deviation(agente.predict_near)
        reporte.balanced_acc[nombre] = balanced_accuracy(agente.predict_near)
        reporte.joint[nombre] = joint_population_brier(agente, semantics)
        reporte.probe[nombre] = single_variable_probe(agente)

    return reporte
