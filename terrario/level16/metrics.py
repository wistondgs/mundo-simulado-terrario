"""Las dos métricas, y cuál manda.

El endpoint **primario** es la log-pérdida de la distribución completa
`P(o'|o)`: mide si el ser sabe *qué* viene, sobre las dieciséis posibilidades.

`BS_change` --el Brier sobre `c = 1[o' != o]`-- es **secundario y diagnóstico**,
y la razón está medida: `q(o) = 1 - P(o|o)` correlaciona 0.9748 con el número de
direcciones libres de `o`, y una regla estática de un solo parámetro que mira
sólo la observación actual queda a 0.0039 de la tabla aprendida. Un resultado
fuerte en `BS_change` sería compatible con no haber aprendido nada temporal.

De ahí que el control STATIC-BITCOUNT no tenga distribución sobre dieciséis
estados: no se le fabrica una para que pueda entrar en el primario. Pedirle la
métrica primaria es un error del evaluador, y se levanta como tal.
"""

from __future__ import annotations

from typing import Protocol, Sequence

import numpy as np

from terrario.level1.world import Observation


class PrimaryMetricNotApplicable(TypeError):
    """Se intentó puntuar en el endpoint primario algo que no lo predice."""


class DistributionPredictor(Protocol):
    def probability(self, previous: Observation, following: Observation) -> float: ...


class ChangePredictor(Protocol):
    def change_probability(self, previous: Observation) -> float: ...


Bank = Sequence[tuple[Observation, Observation]]


def log_loss(model: object, bank: Bank) -> float:
    """Endpoint primario. Nats por transición; menos es mejor."""
    if not hasattr(model, "probability"):
        raise PrimaryMetricNotApplicable(
            f"{type(model).__name__} no predice la distribución completa "
            "`P(o'|o)`. El oráculo §7 prohíbe fabricársela para que compita en "
            "el endpoint primario: su papel es la métrica secundaria.")
    return float(-np.mean([np.log(model.probability(a, b)) for a, b in bank]))


def brier_change(model: ChangePredictor, bank: Bank) -> float:
    """Métrica **secundaria**. Brier sobre el bit de cambio."""
    return float(np.mean([(model.change_probability(a) - float(a != b)) ** 2
                          for a, b in bank]))


def free_directions(observation: Observation) -> int:
    """Cuántas direcciones no están bloqueadas. Geometría instantánea, no memoria."""
    return 4 - sum(observation)
