"""SHUFFLED-ACTION · estratificado por `O_t`, no una baraja global.

Una permutación global de acciones destruiría también `P_L(O,A)`. Lo que hay que
destruir es **sólo** la correspondencia `A ↔ O' | O`:

    (O_t, A_t, O_{t+1})   ->   (O_t, A_{π_o(t)}, O_{t+1})

permutando los tokens **dentro de cada estrato de `O_t`**. Así se conservan
exactamente la secuencia de `O_t`, la de `O_{t+1}`, el número de acciones por
observación y el tamaño de muestra.

La destructividad se calibra contra muchas permutaciones honestas de esa misma
vida. **Nunca contra un umbral fijo**: ésa fue la lección de 1.6, donde un
`< 0.5` escrito a mano rechazaba barajas honestas por debajo de mil pasos.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from terrario.level16.temporal import OBSERVATION_INDEX, TemporalModel
from terrario.level17.contingency import ActionContingencyModel
from terrario.level17.efference import ALL_COMMANDS, EfferenceCopy

_SHUFFLE_BASE = 128


def stratified_stream(seed: int, replica: int) -> np.random.Generator:
    return np.random.default_rng([seed, _SHUFFLE_BASE + replica])


def stratified_permutation(previous, rng) -> list[int]:
    """Índices destino, permutando sólo dentro de cada estrato de `O_t`."""
    orden = list(range(len(previous)))
    estratos: dict[int, list[int]] = {}
    for t, observacion in enumerate(previous):
        estratos.setdefault(OBSERVATION_INDEX[observacion], []).append(t)
    for indices in estratos.values():
        mezclado = list(rng.permutation(indices))
        for destino, origen in zip(indices, mezclado):
            orden[destino] = origen
    return orden


def build(inherited: TemporalModel, previous, commands, following,
          seed: int, replica: int = 0) -> ActionContingencyModel:
    """Un `M_1` alimentado con los comandos barajados dentro de cada estrato."""
    orden = stratified_permutation(previous, stratified_stream(seed, replica))
    modelo = ActionContingencyModel(inherited)
    for t, (anterior, siguiente) in enumerate(zip(previous, following)):
        modelo.observe(anterior, EfferenceCopy(commands[orden[t]]), siguiente)
    return modelo


@dataclass(frozen=True)
class ShuffleAudit:
    observed: float
    null_mean: float
    null_sd: float

    @property
    def tolerance(self) -> float:
        return self.null_mean + 4.0 * self.null_sd

    @property
    def destructive(self) -> bool:
        return self.observed <= self.tolerance


def row_spread(model: ActionContingencyModel) -> float:
    """Cuánto se separan entre sí las cuatro filas de cada observación.

    Si la baraja destruyó la dependencia, las cuatro deberían coincidir salvo
    ruido de muestreo.
    """
    from terrario.level1.world import ALL_OBSERVATIONS
    distancias = []
    for observacion in ALL_OBSERVATIONS:
        filas = np.array([model.predict(observacion, EfferenceCopy(c))
                          for c in ALL_COMMANDS])
        media = filas.mean(axis=0)
        distancias.append(np.abs(filas - media).sum(axis=1).mean() / 2)
    return float(np.mean(distancias))


def audit(shuffled_arm: ActionContingencyModel, inherited: TemporalModel,
          previous, commands, following, seed: int,
          replicas: int = 8) -> ShuffleAudit:
    """Comparar la dispersión del brazo barajado **que se pasa** contra su nula.

    Recibe el brazo en vez de reconstruirlo: si lo reconstruyera, una fixture que
    quisiera falsificarlo tendría que romper también la nula, y entonces la
    auditoría se compararía consigo misma y siempre aprobaría. Ése es justo el
    modo en que esta prueba falló al escribirla.
    """
    nulas = np.array([
        row_spread(build(inherited, previous, commands, following, seed, k))
        for k in range(1, replicas + 1)])
    return ShuffleAudit(row_spread(shuffled_arm), float(nulas.mean()),
                        float(nulas.std(ddof=1)))
