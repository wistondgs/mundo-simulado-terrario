"""Nivel 1.4 · vinculación conjuntiva de dirección y proximidad cualitativa.

Una sola adquisición sobre el Nivel 1.2 congelado: `ψ : X → Y`, la correspondencia
entre dos alfabetos opacos de portadores que permite decidir qué evidencia de
proximidad pertenece al mismo referente momentáneo que un cue direccional.

No es identidad de objeto: lo que persiste es la ligadura entre portadores --un
canal--, no la ligadura a un referente.
"""

from terrario.level14.agent import Level14Agent
from terrario.level14.binding import ConjunctiveBinder, OracleBinder, UniformBinder
from terrario.level14.carriers import DirectionCarrier, ProximityCarrier, all_psi
from terrario.level14.experiment import SeedReport, run_seed
from terrario.level14.inherited import FrozenLevel12Core, FrozenProximity, reconstruct

__all__ = ["ConjunctiveBinder", "DirectionCarrier", "FrozenLevel12Core",
           "FrozenProximity", "Level14Agent", "OracleBinder", "ProximityCarrier",
           "SeedReport", "UniformBinder", "all_psi", "reconstruct", "run_seed"]
