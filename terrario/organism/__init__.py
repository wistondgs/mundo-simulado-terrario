"""`ORGANISM-FUSION-HM-01` · el organismo que reúne las cuatro capacidades.

No es un decimal y no adquiere nada. Reúne `B` (1.0), `Q` (1.1), `H` (1.2) y
`M` (1.3) en una sola instancia para comprobar que coexisten sin alterarse y que
participan las dos últimas en una misma predicción.
"""

from terrario.organism.agent import FusedAgent, NoMemory
from terrario.organism.core import FrozenOrganism, FrozenProximity, reconstruct
from terrario.organism.experiment import SeedReport, run_seed
from terrario.organism.memory import OneStepCueMemory

__all__ = ["FrozenOrganism", "FrozenProximity", "FusedAgent", "NoMemory",
           "OneStepCueMemory", "SeedReport", "reconstruct", "run_seed"]
