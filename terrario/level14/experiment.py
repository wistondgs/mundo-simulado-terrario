"""`LEVEL1.4-CONJUNCTIVE-BINDING-01` · una realización.

Es el primer experimento del linaje en el que **los atributos presentes son
idénticos entre condiciones y sólo cambia la relación entre ellos**. 1.0 variaba
`o`, 1.1 `g`, 1.2 `s`, 1.3 la historia: los cuatro miden la respuesta a un
atributo. Aquí los conjuntos marginales son los mismos y lo único que difiere es
qué va con qué.

Los positivos son calculables antes de correr, y eso no los vacía: los convierte
en verificación de que la implementación realiza el algoritmo especificado.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from terrario.level11.cue import CueSemantics
from terrario.level14.agent import Level14Agent
from terrario.level14.binding import (
    BlindBinder, ConjunctiveBinder, OracleBinder, UniformBinder, train,
)
from terrario.level14.carriers import CANONICAL_PSI, Psi
from terrario.level14.inherited import reconstruct
from terrario.level14.metrics import (
    SEALED_BS_FLOOR, SEALED_BS_FULL, binding_brier,
    carrier_attribute_information, index_binder_accuracy, readout_mse,
    readout_reference, three_factor_probe,
)
from terrario.level14.scene import (
    acquisition_bank, evaluation_bank, ordered_evaluation_bank,
    shuffled_acquisition_bank, single_reference_bank,
)

ORDEN = ("FULL_14", "ORACLE", "SHUFFLED", "UNBOUND", "FROZEN_BINDER",
         "SINGLE_G", "SINGLE_D")


@dataclass
class SeedReport:
    seed: int
    fingerprints_before: dict[str, str]
    fingerprints_after: dict[str, str]
    brier: dict[str, float] = field(default_factory=dict)
    readout: dict[str, float] = field(default_factory=dict)
    readout_ref: dict[str, float] = field(default_factory=dict)
    info_acq: tuple[float, float] = (0.0, 0.0)
    info_eval: tuple[float, float] = (0.0, 0.0)
    index_accuracy: float = 0.0
    single_reference_brier: float = 0.0
    probe: dict[str, dict[str, float]] = field(default_factory=dict)

    @property
    def lineage_intact(self) -> bool:
        return self.fingerprints_before == self.fingerprints_after

    def gates(self) -> dict[str, bool]:
        p = self.probe
        return {
            "L14-0 linaje": self.lineage_intact,
            "L14-2 ambigüedad": (self.brier["UNBOUND"] == SEALED_BS_FLOOR
                                 and self.single_reference_brier == 0.0),
            "L14-3 adquisición": (
                abs(self.brier["FULL_14"] - SEALED_BS_FULL) < 1e-12
                and all(abs(self.brier[b] - SEALED_BS_FLOOR) < 1e-12
                        for b in ("UNBOUND", "FROZEN_BINDER", "SHUFFLED"))),
            "L14-5 sensibilidad conjunta": (p["binding"]["readout"] > 0.0
                                            and p["binding"]["C"] == 0.0),
            "L14-8 atajos": abs(self.index_accuracy - 0.5) < 1e-12,
            "L14-10 sin identidad": (self.info_acq == (0.0, 0.0)
                                     and self.info_eval == (0.0, 0.0)),
            "L14-11 probes exactos": (p["g"]["H"] == 0.0 and p["g"]["C"] == 0.0
                                      and p["s"]["Q"] == 0.0 and p["s"]["C"] == 0.0
                                      and p["binding"]["Q"] == 0.0
                                      and p["binding"]["H"] == 0.0),
        }

    @property
    def passes(self) -> bool:
        return all(self.gates().values())


def run_seed(seed: int, *, psi: Psi | None = None,
             semantics: CueSemantics | None = None) -> SeedReport:
    psi = psi or CANONICAL_PSI
    semantics = semantics or CueSemantics.identity()
    core = reconstruct(seed, semantics=semantics)
    antes = core.fingerprints()

    entrenado = ConjunctiveBinder(); train(entrenado, acquisition_bank(psi))
    barajado = ConjunctiveBinder(); train(barajado, shuffled_acquisition_bank())
    ciego_g = BlindBinder(ignore="proximity"); train(ciego_g, acquisition_bank(psi))
    ciego_d = BlindBinder(ignore="direction"); train(ciego_d, acquisition_bank(psi))

    brazos: dict[str, Level14Agent] = {
        "FULL_14": Level14Agent(core, entrenado),
        "ORACLE": Level14Agent(core, OracleBinder(psi), name="ORACLE"),
        "SHUFFLED": Level14Agent(core, barajado, name="SHUFFLED"),
        "UNBOUND": Level14Agent(core, UniformBinder(), name="UNBOUND"),
        "FROZEN_BINDER": Level14Agent(core, ConjunctiveBinder(frozen=True),
                                      name="FROZEN_BINDER"),
        "SINGLE_G": Level14Agent(core, ciego_g, name="SINGLE_G"),
        "SINGLE_D": Level14Agent(core, ciego_d, name="SINGLE_D"),
    }

    banco = evaluation_bank(psi)
    p_correct = {"FULL_14": 289 / 290, "ORACLE": 1.0}
    reporte = SeedReport(seed, antes, core.fingerprints())
    for nombre, agente in brazos.items():
        reporte.brier[nombre] = binding_brier(agente, banco)
        reporte.readout[nombre] = readout_mse(agente, banco)
        reporte.readout_ref[nombre] = readout_reference(
            agente, banco, p_correct.get(nombre, 0.5))

    reporte.info_acq = carrier_attribute_information(acquisition_bank(psi), paired=True)
    reporte.info_eval = carrier_attribute_information(banco)
    reporte.index_accuracy = index_binder_accuracy(ordered_evaluation_bank(psi))
    reporte.single_reference_brier = binding_brier(brazos["UNBOUND"],
                                                   single_reference_bank(psi))
    reporte.probe = three_factor_probe(brazos["FULL_14"], banco)
    return reporte
