"""Agente de Nivel 1.1 · el mismo ser elemental, en un linaje sin historia.

Copia literal del Agente de Nivel 1 en `d278f59`, con un espacio de semillas
propio y verificado disjunto. Todo lo que el Experimento 1 demostró se hereda
por construcción, porque el código es el mismo.

**Qué NO se copió, y por qué.** El módulo del reversal se queda en `level1`: es
un experimento sobre aquel ser, con su preregistro sellado, su semilla quemada y
sus contratos a medio cerrar. Traerlo aquí importaría la contaminación que esta
copia existe para evitar.

**Qué está contaminado en el original.** Las 32 semillas del Experimento 1 tienen
resultados publicados; `20260919` fue además la del desarme mecanístico, donde se
leyeron dirección del efecto, suelos analíticos y mecanismo; `31415926` se quemó
verificando el reversal. Ninguna de ellas, ni sus imágenes bajo los
desplazamientos de banco y permutación, entra en el espacio de este linaje.

El espacio propio es `70000019 … 70000082`, con intersección vacía contra las 585
semillas tocadas hasta ahora.
"""

from terrario.level11.models import (  # noqa: F401
    ContingencyTable, FactoredContingency, TabularQ, oracle_policy,
)
from terrario.level11.world import (  # noqa: F401
    ALL_OBSERVATIONS, DELTA, Direction, Grid, Observation, Transition,
    physics_contract,
)

#: Espacio de semillas de este linaje. Disjunto, verificado con imágenes.
SEED_SPACE = range(70000019, 70000083)
