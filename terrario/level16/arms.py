"""Los cuatro brazos, y el instrumento que no es un brazo.

```
FULL-1.6          S0 produce la vida · A1 la cuenta
FROZEN            misma trayectoria · la tabla se queda en el prior
TEMPORAL-SHUFFLED mismos marginales · adyacencia destruida
STATIC-BITCOUNT   q(o) = beta * k(o)/4 · sólo en la métrica secundaria
```

Los tres primeros ven **exactamente la misma vida**; lo único que cambia entre
ellos es qué se hace con ella. El cuarto es de otra clase: no es una ablación del
ser sino una hipótesis rival sobre de dónde sale la competencia en el bit de
cambio --de la geometría que se ve ahora, sin ninguna estructura temporal.

`TEMPORAL-SHUFFLED` conserva los marginales `P(o)` y `P(o')` por construcción, y
destruye el emparejamiento. El oráculo exige comprobar que la destrucción ocurrió
de verdad en vez de suponerla: una baraja defectuosa que conservara parejas reales
convertiría el control en una copia del brazo FULL y el contraste crítico en nada.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from terrario.level1.world import ALL_OBSERVATIONS, Observation
from terrario.level16.life import Life
from terrario.level16.metrics import free_directions
from terrario.level16.temporal import OBSERVATION_INDEX, TemporalModel
from terrario.level16.world import null_stream, shuffle_stream


def full(life: Life) -> TemporalModel:
    """El ser que vivió y contó. Se congela al terminar la adquisición."""
    modelo = TemporalModel()
    for anterior, siguiente in zip(life.previous, life.following):
        modelo.observe(anterior, siguiente)
    modelo.freeze()
    return modelo


def frozen(life: Life) -> TemporalModel:
    """El ser que vivió lo mismo y no actualizó nada. `M_0`."""
    modelo = TemporalModel.naive()
    modelo.freeze()
    return modelo


def temporal_shuffled(life: Life) -> TemporalModel:
    """`o_t` emparejado con `o_{pi(t)+1}`. Mismos marginales, sin adyacencia."""
    permutacion = shuffle_stream(life.seed).permutation(len(life.previous))
    modelo = TemporalModel()
    for indice, anterior in enumerate(life.previous):
        modelo.observe(anterior, life.following[permutacion[indice]])
    modelo.freeze()
    return modelo


@dataclass(frozen=True)
class ShuffleAudit:
    """¿Se destruyó la temporalidad, o sólo se movieron cosas de sitio?

    Dos contadores que es fácil confundir, y confundirlos descalibra el gate:

    * `fixed_points` son las posiciones que conservaron su pareja **por
      identidad**, `pi(t) = t`. Esperanza 1 en cualquier permutación uniforme,
      independientemente del tamaño. Es el «pares supervivientes» del oráculo.
    * `value_coincidences` son las posiciones cuya pareja barajada resultó tener
      **el mismo valor** que la real. Con dieciséis observaciones su esperanza es
      `n * sum(P(o')^2)`, del orden del 10 % del banco. **No es un defecto** y no
      puede llevarse a cero: es el alfabeto, no la baraja.

    La destrucción se juzga por la distancia a la marginal, que es la magnitud
    que de verdad responde a si queda dependencia temporal.
    """

    fixed_points: int
    value_coincidences: int
    expected_coincidences: float
    total_pairs: int
    full_distance_to_marginal: float
    shuffled_distance_to_marginal: float
    null_mean: float
    null_sd: float

    @property
    def tolerance(self) -> float:
        """Hasta dónde puede alejarse de la marginal una baraja honesta.

        Un umbral fijo --el `0.5 * distancia de FULL` que esto tenía antes-- es
        dependiente del tamaño de muestra y rechaza barajas honestas por debajo
        de unos mil pasos: con 512 pasos repartidos en dieciséis filas, una tabla
        correctamente barajada se aleja de la marginal por puro ruido de
        estimación hasta razones de 0.57. La referencia correcta es la propia
        trayectoria barajada de otras maneras, que se autocalibra a cualquier
        presupuesto.
        """
        return self.null_mean + 4.0 * self.null_sd

    @property
    def destructive(self) -> bool:
        return self.shuffled_distance_to_marginal <= self.tolerance


def audit_shuffle(life: Life, aprendido: TemporalModel, barajado: TemporalModel,
                  null_replicas: int = 8) -> ShuffleAudit:
    """Medir la destrucción por dos vías independientes.

    La primera cuenta puntos fijos de la permutación. La segunda mide cuánto se
    aleja `P(.|o)` de la marginal: si el barajado hizo su trabajo, cada fila
    *es* la marginal y la distancia cae a ruido de muestreo.
    """
    n = len(life.previous)
    permutacion = shuffle_stream(life.seed).permutation(n)
    fijos = int(sum(1 for t in range(n) if permutacion[t] == t))
    coincidencias = int(sum(1 for t in range(n)
                            if life.following[permutacion[t]] == life.following[t]))

    conteos = np.zeros(16)
    for siguiente in life.following:
        conteos[OBSERVATION_INDEX[siguiente]] += 1
    marginal = conteos / conteos.sum()
    esperadas = float(n * (marginal ** 2).sum())

    def distancia(modelo: TemporalModel) -> float:
        filas = [np.abs(modelo.predict(o) - marginal).sum() / 2
                 for o in ALL_OBSERVATIONS
                 if any(o == a for a in life.previous)]
        return float(np.mean(filas)) if filas else 0.0

    nulas = []
    for replica in range(null_replicas):
        otra = null_stream(life.seed, replica).permutation(n)
        referencia = TemporalModel()
        for indice, anterior in enumerate(life.previous):
            referencia.observe(anterior, life.following[otra[indice]])
        nulas.append(distancia(referencia))
    nulas_array = np.array(nulas)

    return ShuffleAudit(fijos, coincidencias, esperadas, n,
                        distancia(aprendido), distancia(barajado),
                        float(nulas_array.mean()), float(nulas_array.std(ddof=1)))


class StaticBitcount:
    """`q(o) = beta * k(o)/4`. Un parámetro, sin memoria y sin tiempo.

    Deliberadamente **no** tiene `probability`: no predice qué observación viene,
    sólo si algo cambiará. Pedirle el endpoint primario levanta
    `PrimaryMetricNotApplicable`, que es la forma estructural de cumplir el
    oráculo §7 --no se le fabrica una distribución para que pueda competir donde
    no le corresponde.
    """

    def __init__(self, beta: float) -> None:
        self.beta = float(beta)

    @classmethod
    def fitted(cls, life: Life) -> StaticBitcount:
        """Ajustar el único parámetro sobre la misma experiencia que vio FULL."""
        u = np.array([free_directions(o) / 4 for o in life.previous])
        c = np.array([float(a != b) for a, b in zip(life.previous, life.following)])
        denominador = float((u * u).sum())
        return cls(float((c * u).sum() / denominador) if denominador else 0.0)

    def change_probability(self, previous: Observation) -> float:
        return min(1.0, max(0.0, self.beta * free_directions(previous) / 4))
