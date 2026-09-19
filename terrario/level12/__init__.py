"""Nivel 1.2 · proximidad cualitativa.

Una sola adquisición nueva sobre el Nivel 1.1 congelado: `H(s) = P(CERCA | s)`,
aprendida desde una señal sensorial ambigua cuya evidencia nace de la distancia
física latente de una referencia externa.

La política motora **no cambia**: `π_1.2(o,g,s) = π_1.1(o,g)`. Que la distancia
modifique la acción sería otra adquisición, y pertenece a un decimal posterior si
el usuario lo decide.
"""

from terrario.level12.agent import Level12Agent
from terrario.level12.experiment import SeedReport, run_seed
from terrario.level12.inherited import FrozenLevel11Core, reconstruct
from terrario.level12.proximity import (
    BayesDistanceOracle, ConstantDistance, QualitativeDistanceModel,
)
from terrario.level12.reference import DistanceTruth, ProximityToken, Reference

__all__ = [
    "BayesDistanceOracle", "ConstantDistance", "DistanceTruth",
    "FrozenLevel11Core", "Level12Agent", "ProximityToken",
    "QualitativeDistanceModel", "Reference", "SeedReport", "reconstruct",
    "run_seed",
]
