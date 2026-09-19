"""`ORGANISM-FUSION-HM-01` · una realización.

No es un decimal y no adquiere nada: reúne capacidades ya verificadas para
comprobar que existe **un solo organismo** que las contiene y las usa juntas.

La pregunta útil no es si las piezas caben en el mismo árbol --eso lo contestaría
una suite conjunta-- sino si ambas participan en el mismo cálculo. Eso lo
contesta el factorial, y su contenido es la **interacción**: una cantidad que
ninguna rama por sí sola podía escribir.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from terrario.level11.cue import CueSemantics
from terrario.level11.metrics import alignment_rate_expected
from terrario.level12.metrics import ORACLE
from terrario.organism.agent import FusedAgent, NoMemory
from terrario.organism.core import reconstruct
from terrario.organism.memory import MemoryPhase, OneStepCueMemory
from terrario.organism.metrics import (
    ORDEN, SEALED, SEALED_INTERACTION, cue_observation_information,
    ideal_reference, interaction, joint_population_brier,
)

#: Fijo, independiente del cue e idéntico para las cuatro historias.
O_PRESENT = (1, 0, 0, 0)


@dataclass
class SeedReport:
    seed: int
    fingerprints_before: dict[str, str]
    fingerprints_after: dict[str, str]
    single_core: bool
    align_before: float
    align_after: float
    leakage: float
    memory_semantics: bool
    joint: dict[tuple[str, str], float] = field(default_factory=dict)
    reference: dict[tuple[str, str], float] = field(default_factory=dict)
    skip_tick: float = 0.0

    @property
    def lineage_intact(self) -> bool:
        return self.fingerprints_before == self.fingerprints_after

    @property
    def measured_interaction(self) -> float:
        return interaction(self.joint)

    @property
    def reference_interaction(self) -> float:
        return interaction(self.reference)

    def gates(self) -> dict[str, bool]:
        ordenados = [self.joint[k] for k in ORDEN]
        return {
            "F-0 un solo núcleo": self.single_core,
            "F-1 linaje intacto": self.lineage_intact,
            "F-3 semántica de M": self.memory_semantics,
            "F-4 coexistencia": len(self.joint) == 4,
            "F-5 uso conjunto": (ordenados == sorted(ordenados)
                                 and len(set(ordenados)) == 4),
            "F-6 interacción superaditiva": self.measured_interaction > 0,
            "F-7 sin fuga": self.leakage == 0.0,
            "F-8 política intacta": self.align_before == self.align_after,
            "F-9 el tick hace falta": self.skip_tick > self.joint[("ON", "ON")],
        }

    @property
    def passes(self) -> bool:
        return all(self.gates().values())


def run_seed(seed: int, *, semantics: CueSemantics | None = None) -> SeedReport:
    semantics = semantics or CueSemantics.identity()
    organismo = reconstruct(seed, semantics=semantics)
    antes = organismo.fingerprints()
    align_antes = alignment_rate_expected(organismo, semantics)

    brazos = {
        ("ON", "ON"): FusedAgent(organismo, OneStepCueMemory(), use_h=True, use_m=True),
        ("ON", "OFF"): FusedAgent(organismo, NoMemory(), use_h=True, use_m=False),
        ("OFF", "ON"): FusedAgent(organismo, OneStepCueMemory(), use_h=False, use_m=True),
        ("OFF", "OFF"): FusedAgent(organismo, NoMemory(), use_h=False, use_m=False),
    }

    # F-0 · todos los caminos referencian el MISMO núcleo, comprobado por identidad
    unico = all(a.organism is organismo for a in brazos.values())

    joint = {k: joint_population_brier(a, semantics, O_PRESENT)
             for k, a in brazos.items()}
    referencia = {k: ideal_reference(organismo.predict_near, semantics,
                                     use_h=(k[0] == "ON"), use_m=(k[1] == "ON"))
                  for k in brazos}

    completo = brazos[("ON", "ON")]
    sin_tick = joint_population_brier(completo, semantics, O_PRESENT, skip_tick=True)

    # F-3 · la semántica sellada de M, comprobada aquí y no supuesta
    m = OneStepCueMemory()
    from terrario.level11.cue import CueToken
    m.write(CueToken.C1)
    semantica = m.peek() is None                      # leer antes del tick: nada
    m.tick()
    semantica = semantica and m.peek() is CueToken.C1  # un tick: conserva
    huella = m.fingerprint()
    m.peek()
    semantica = semantica and m.fingerprint() == huella   # leer no consume
    m.tick()
    semantica = semantica and m.phase is MemoryPhase.EMPTY  # dos ticks: expira

    return SeedReport(
        seed, antes, organismo.fingerprints(), unico, align_antes,
        alignment_rate_expected(organismo, semantics),
        cue_observation_information(semantics), semantica,
        joint, referencia, sin_tick)
