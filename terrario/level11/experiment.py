"""`LEVEL1.1-INTEGRATION-VERIFICATION-01` · una realización completa.

No es una campaña confirmatoria. Los resultados positivos están determinados por
la arquitectura que suministramos, así que la pregunta no es «¿funciona?» sino
**«¿reproduce la implementación el mecanismo que diseñamos?»**. El oráculo
analítico está sellado en `docs/LEVEL11_ORACULO_PREREGISTRADO.md`, y ocho
realizaciones independientes lo comprueban. Sin bootstrap, sin intervalos: ocho
realizaciones no son una muestra poblacional.

Fase 0 entrena el cuerpo con el protocolo del Nivel 1.0 y lo **congela**. A
partir de ahí la única estructura que puede cambiar es `Q`, y por eso cualquier
cambio observado tiene una causa candidata única.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from terrario.level11.agent import ConstantAgent, ConstantOrientation, Level11Agent
from terrario.level11.body import BlindBody, FrozenFactoredBody
from terrario.level11.cue import ALL_CUES, CueSemantics, CueToken
from terrario.level11.measurement import Experiment as BodyExperiment
from terrario.level11.measurement import motor_babbling
from terrario.level11.metrics import (
    BrierReport, alignment_rate_expected, brier, factorial_probe,
)
from terrario.level11.models import FactoredContingency
from terrario.level11.orientation import DirectionalAssociation
from terrario.level11.stream import (
    OrientationStream, build_holdout, orientation_babbling,
)
from terrario.level11.world import Direction, Observation

#: Congelados en el preregistro. No se tocan tras ver resultados.
N_ORIENTATION = 2048
MIN_INFORMATIVE = 30
BODY_TRANSITIONS = 8192


class JointTable:
    """Baseline de enumeración: una creencia por tripleta `(o,g,a)`.

    No es el organismo. Existe para separar **componer** de **enumerar**: sobre
    un par `(o,g)` retenido no tiene celda y se queda en su prior, mientras el
    compuesto responde porque conoce `(o,a)` y `(g,a)` por separado.
    """

    def __init__(self, *, prior: float = 1.0) -> None:
        self.prior = prior
        self._belief: dict[tuple[Observation, CueToken, Direction], list[float]] = {}

    def predict(self, observation: Observation, cue: CueToken,
                action: Direction) -> float:
        a, b = self._belief.get((observation, cue, action), (self.prior, self.prior))
        return a / (a + b)

    def observe(self, observation: Observation, cue: CueToken, action: Direction,
                z: int) -> None:
        key = (observation, cue, action)
        if key not in self._belief:
            self._belief[key] = [self.prior, self.prior]
        self._belief[key][0 if z else 1] += 1

    def act(self, observation: Observation, cue: CueToken,
            rng: np.random.Generator) -> Direction:
        v = np.asarray([self.predict(observation, cue, d) for d in Direction])
        tied = np.flatnonzero(np.isclose(v, v.max()))
        return Direction(int(rng.choice(tied)))


def train_body(seed: int) -> FrozenFactoredBody:
    """Fase 0 · el cuerpo canónico del Nivel 1.0, y después read-only."""
    cfg = BodyExperiment(train_layouts=BODY_TRANSITIONS // 64,
                         train_steps_per_layout=64)
    stream, violations = motor_babbling(cfg, seed)
    if violations:
        raise RuntimeError(f"contrato físico roto en fase 0: {violations}")
    body = FactoredContingency()
    for t in stream:
        body.observe(t.observation, t.direction, t.moved)
    return FrozenFactoredBody(body)


def train_orientation(stream: OrientationStream, semantics: CueSemantics,
                      *, frozen: bool = False,
                      shuffle_rng: np.random.Generator | None = None
                      ) -> DirectionalAssociation:
    """Aprende `Q`. Con `shuffle_rng` se rompe la correspondencia señal↔resultado.

    El control barajado ve la señal de OTRO ensayo mientras la verdad física
    sigue perteneciendo al suyo: eso destruye la contingencia sin tocar el
    cuerpo ni la cantidad de experiencia.
    """
    q = DirectionalAssociation(frozen=frozen)
    señales = [e.cue for e in stream.experiences]
    if shuffle_rng is not None:
        señales = [CueToken(int(c)) for c in
                   np.asarray(señales)[shuffle_rng.permutation(len(señales))]]
    for e, cue_vista in zip(stream.experiences, señales, strict=True):
        # El aprendiz ve `cue_vista`; la VERDAD FÍSICA sigue perteneciendo al
        # cue original del ensayo. Barajar la señal junto con su semántica sería
        # un reetiquetado consistente, no un desacople: medido, ese control
        # rendía idéntico al brazo principal, que es como se delató.
        referencia = semantics.direction_of(e.cue)
        q.observe(cue_vista, e.action, moved=e.moved, physical=e.physical,
                  semantics_direction=referencia
                  if e.moved and e.physical is not None else None)
    return q


def train_joint_table(stream: OrientationStream, semantics: CueSemantics) -> JointTable:
    table = JointTable()
    for e in stream.experiences:
        z = int(e.moved and e.physical == semantics.direction_of(e.cue))
        table.observe(e.observation, e.cue, e.action, z)
    return table


@dataclass
class SeedReport:
    seed: int
    body_digest_before: str
    body_digest_after: str
    informative_minimum: int
    physics_violations: int
    holdout_violations: int
    brier: dict[str, BrierReport] = field(default_factory=dict)
    alignment: dict[str, float] = field(default_factory=dict)
    brier_holdout: dict[str, BrierReport] = field(default_factory=dict)
    probe: dict[str, Any] = field(default_factory=dict)

    @property
    def body_intact(self) -> bool:
        return self.body_digest_before == self.body_digest_after


def run_seed(seed: int, *, semantics: CueSemantics | None = None) -> SeedReport:
    semantics = semantics or CueSemantics.identity()
    holdout = build_holdout(semantics, seed=0)          # congelado, no por semilla

    body = train_body(seed)
    antes = body.digest()

    stream = orientation_babbling(seed + 7, n=N_ORIENTATION, semantics=semantics,
                                  holdout=holdout)
    q = train_orientation(stream, semantics)
    q_frozen = DirectionalAssociation(frozen=True)
    q_shuffled = train_orientation(stream, semantics,
                                   shuffle_rng=np.random.default_rng([seed, 9]))
    table = train_joint_table(stream, semantics)

    brazos: dict[str, Any] = {
        "COMPOSITE": Level11Agent(body, q),
        "BODY-ONLY": Level11Agent(body, ConstantOrientation(0.5)),
        "CUE-ONLY": Level11Agent(BlindBody(), q),
        "FROZEN": Level11Agent(body, q_frozen),
        "SHUFFLED": Level11Agent(body, q_shuffled),
        "JOINT-TABLE": table,
        "SIEMPRE-CERO": ConstantAgent(0.0, name="cero"),
        "IGNORANTE": ConstantAgent(0.5, name="ignorante"),
    }

    from terrario.level11.metrics import all_triples
    retenidas = [(o, g, a) for (o, g, a) in all_triples() if (o, g) in holdout]

    reporte = SeedReport(seed, antes, body.digest(), stream.informative_minimum,
                         stream.violations, stream.holdout_violations)
    for nombre, agente in brazos.items():
        reporte.brier[nombre] = brier(agente, semantics)
        reporte.brier_holdout[nombre] = brier(agente, semantics, retenidas)
        reporte.alignment[nombre] = alignment_rate_expected(agente, semantics)
    reporte.probe = {n: factorial_probe(a, semantics)
                     for n, a in brazos.items() if n in ("COMPOSITE", "CUE-ONLY",
                                                         "BODY-ONLY")}
    return reporte
