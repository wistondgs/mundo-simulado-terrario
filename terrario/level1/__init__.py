"""Agente de Nivel 1 · el primer ser: siente, prueba y cambia.

No es una capa sobre el organismo anterior. Es un ser nuevo, con el repertorio
más pequeño con el que se puede preguntar algo: un cuerpo en una rejilla, cuatro
acciones motoras, y cuatro bits de sentido. Todo lo demás --energía, hambre,
objetos, memoria episódica, planificación-- queda deliberadamente fuera, porque
cualquiera de esas cosas sería una explicación alternativa del primer resultado.
"""

from terrario.level1.external import (  # noqa: F401
    NearestNeighborForwardModel,
)
from terrario.level1.models import (  # noqa: F401
    ContingencyTable, FactoredContingency, TabularQ, oracle_policy,
)
from terrario.level1.world import (  # noqa: F401
    DELTA, Direction, Grid, Observation, Transition,
)
