# ─────────────────────────────────────────────────────────────────────────────
# COPIA · Agente de Nivel 1.1
#
# Copiado literalmente de `terrario/level1/models.py` en `d278f59`, con el único
# cambio de la ruta del paquete. El comportamiento es idéntico por construcción:
# si estos ficheros divergieran del original, el 1.1 dejaría de heredar lo que el
# Experimento 1 demostró.
#
# **Por qué una copia y no un import.** El Nivel 1 está contaminado: sus semillas
# tienen resultados leídos, su desarme mecanístico miró la dirección del efecto, y
# el reversal vive en su mismo paquete. Importar de él ataría el linaje nuevo a
# esa historia; copiarlo lo separa de verdad, al precio de tener que mantener la
# equivalencia explícitamente.
# ─────────────────────────────────────────────────────────────────────────────

"""Lo que el Agente de Nivel 1 puede llegar a saber, y contra qué se compara.

Tres piezas, y sólo la primera es el ser:

    ContingencyTable   el Agente de Nivel 1. Una creencia por par
                       (observación, dirección), actualizada Beta-Bernoulli.
    TabularQ           el carril externo. Q-learning tabular, que NO es nuestra
                       arquitectura: es el techo contra el que se mide cuánto
                       alcanza lo barato.
    oracle_policy      el techo físico. No aprende; conoce la regla. Si no llega
                       a 1.0, el mundo o el instrumento están rotos y el
                       experimento no se interpreta.
"""

from __future__ import annotations

from collections import defaultdict

import numpy as np

from terrario.level11.world import Direction, Observation, Transition


class ContingencyTable:
    """Una creencia por par `(observación, dirección)`, nada compartido entre pares.

    Prior `Beta(1,1)`, así que antes de cualquier experiencia la creencia es
    exactamente `1/2` para todo par: el ser nace sin opinión. La media posterior
    es `α / (α + β)`.

    **Límite que hay que declarar antes de leer un resultado.** Las celdas son
    independientes: para un par nunca visto la respuesta es el prior. Este modelo
    **no puede generalizar**, sólo memorizar. Medido: entrenando con cuatro de
    las dieciséis observaciones retiradas, el Brier sobre las retiradas sale
    `0.250000` --exactamente el del brazo congelado--. Cualquier lectura de este
    experimento como «adquirió la regla» es falsa; lo que adquiere es una tabla.
    """

    def __init__(self, *, prior_alpha: float = 1.0, prior_beta: float = 1.0,
                 frozen: bool = False) -> None:
        self.prior_alpha = prior_alpha
        self.prior_beta = prior_beta
        self.frozen = frozen
        self._belief: dict[tuple[Observation, Direction], list[float]] = {}

    def _cell(self, observation: Observation, direction: Direction) -> list[float]:
        """La celda, creándola si hace falta. SÓLO para escribir."""
        key = (observation, direction)
        if key not in self._belief:
            self._belief[key] = [self.prior_alpha, self.prior_beta]
        return self._belief[key]

    def predict(self, observation: Observation, direction: Direction) -> float:
        """`P(me muevo | esto que veo, esta dirección)`. No escribe nada.

        Consulta con valor por defecto en vez de crear la celda: si preguntar
        insertara, el estado del ser cambiaría por el hecho de medirlo. Los
        números saldrían iguales --el valor devuelto es el prior de todos
        modos-- pero cualquier huella del estado adaptativo quedaría
        contaminada por la sonda, y ése es un defecto que este proyecto ya pagó
        una vez.
        """
        alpha, beta = self._belief.get((observation, direction),
                                       (self.prior_alpha, self.prior_beta))
        return alpha / (alpha + beta)

    def observe(self, observation: Observation, direction: Direction,
                moved: int) -> None:
        """La única escritura dependiente de experiencia que tiene este ser.

        El brazo congelado no bloquea el cálculo: bloquea la ESCRITURA. Calcula
        lo mismo y no lo guarda, que es la diferencia entre un control y una
        corrección posterior.
        """
        if self.frozen:
            return
        cell = self._cell(observation, direction)
        cell[0] += moved
        cell[1] += 1 - moved

    def act(self, observation: Observation, rng: np.random.Generator) -> Direction:
        """Elegir la dirección cuya consecuencia predice mejor.

        Lectura diagnóstica, no deseo: pregunta si el conocimiento adquirido
        puede usarse para elegir, no si el ser quiere moverse. Los empates se
        rompen al azar, que es lo que hace que el brazo congelado --todo a
        `1/2`-- sea exactamente una política aleatoria.
        """
        values = np.asarray([self.predict(observation, d) for d in Direction],
                            dtype=float)
        tied = np.flatnonzero(np.isclose(values, values.max()))
        return Direction(int(rng.choice(tied)))

    @property
    def visited_cells(self) -> int:
        return len(self._belief)


class TabularQ:
    """Q-learning tabular. El carril externo, no nuestra teoría.

    Su papel es contestar una sola pregunta: ¿un método estándar y probado
    aprende a elegir acciones efectivas en ESTE mundo y con ESTE instrumento? Si
    no lo hace, un fracaso del Agente de Nivel 1 no significa nada y el
    experimento queda en `POSITIVE_CONTROL_FAILED`.

    La recompensa es `moved`, deliberadamente: el techo debe resolver la misma
    tarea, no una más fácil.
    """

    def __init__(self, *, learning_rate: float = 0.20, discount: float = 0.90) -> None:
        self.learning_rate = learning_rate
        self.discount = discount
        self.q: dict[Observation, np.ndarray] = defaultdict(
            lambda: np.zeros(len(Direction), dtype=float))
        self._unseen = np.zeros(len(Direction), dtype=float)

    def observe(self, transition: Transition) -> None:
        current = self.q[transition.observation][int(transition.direction)]
        # El arranque lee el siguiente estado con valor por defecto, por la misma
        # razón: aprender no debe crear celdas que nadie visitó.
        bootstrap = float(self.q.get(transition.next_observation, self._unseen).max())
        target = float(transition.moved) + self.discount * bootstrap
        self.q[transition.observation][int(transition.direction)] = (
            current + self.learning_rate * (target - current))

    def act(self, observation: Observation, rng: np.random.Generator) -> Direction:
        """No escribe. `self.q` es un `defaultdict`, así que indexarlo con una
        observación nueva la insertaría: elegir dejaría huella."""
        values = self.q.get(observation, self._unseen)
        tied = np.flatnonzero(np.isclose(values, values.max()))
        return Direction(int(rng.choice(tied)))


def oracle_policy(observation: Observation, rng: np.random.Generator) -> Direction:
    """Conoce la física. Elige una dirección libre si la hay.

    Define el techo: en toda situación con salida, se mueve. Si esto no da
    exactamente `1.0`, el fallo es del mundo o de la medición, no del ser.
    """
    free = [int(d) for d in Direction if observation[int(d)] == 0]
    if not free:
        return Direction(int(rng.integers(len(Direction))))
    return Direction(int(rng.choice(free)))


class FactoredContingency:
    """El mismo conteo, sobre RASGOS en vez de sobre CASOS.

    `ContingencyTable` guarda una creencia por situación completa, así que una
    situación nunca vista no tiene creencia: devuelve el prior. Medido sobre 32
    semillas, con cuatro de las dieciséis observaciones retiradas del
    entrenamiento, su Brier sobre las retiradas sale `0.250000` -- exactamente el
    del brazo congelado. No generaliza mal: no puede.

    Este ser descompone la situación en sus cuatro bits y guarda, para cada
    dirección de acto y cada bit, cómo le fue. La combinación es la suma de
    log-momios de Bayes ingenuo:

        logit P(muevo | o, a) = logit P(muevo | a)
                              + Σ_d [ logit P(muevo | a, o_d) − logit P(muevo | a) ]

    **No se le entrega la regla.** El ser no sabe que el bit que importa es el de
    la dirección que va a intentar: tiene los cuatro y debe descubrir que tres de
    ellos son mudos, porque los datos hacen que sus log-momios se cancelen. Lo
    que gana es que una situación nueva se puntúa con estadística aprendida de
    OTRAS situaciones que compartían bits.

    Es, literalmente, la diferencia entre haber adquirido una tabla y haber
    adquirido una regla, con la misma cantidad de experiencia y el mismo prior.
    """

    def __init__(self, *, prior_alpha: float = 1.0, prior_beta: float = 1.0,
                 frozen: bool = False) -> None:
        self.prior_alpha = prior_alpha
        self.prior_beta = prior_beta
        self.frozen = frozen
        #: por dirección de acto: cómo le fue en general
        self._base: dict[Direction, list[float]] = {}
        #: por (dirección de acto, posición del bit, valor del bit)
        self._feature: dict[tuple[Direction, int, int], list[float]] = {}

    def _counts(self, store: dict, key) -> list[float]:
        if key not in store:
            store[key] = [self.prior_alpha, self.prior_beta]
        return store[key]

    @staticmethod
    def _logit(counts: tuple[float, float] | list[float]) -> float:
        alpha, beta = counts
        return float(np.log(alpha) - np.log(beta))

    def predict(self, observation: Observation, direction: Direction) -> float:
        """No escribe: consulta con valor por defecto, como el resto del banco."""
        default = (self.prior_alpha, self.prior_beta)
        base = self._logit(self._base.get(direction, default))
        total = base
        for position, value in enumerate(observation):
            cell = self._feature.get((direction, position, value), default)
            total += self._logit(cell) - base
        return float(1.0 / (1.0 + np.exp(-total)))

    def observe(self, observation: Observation, direction: Direction,
                moved: int) -> None:
        if self.frozen:
            return
        base = self._counts(self._base, direction)
        base[0] += moved
        base[1] += 1 - moved
        for position, value in enumerate(observation):
            cell = self._counts(self._feature, (direction, position, value))
            cell[0] += moved
            cell[1] += 1 - moved

    def act(self, observation: Observation, rng: np.random.Generator) -> Direction:
        values = np.asarray([self.predict(observation, d) for d in Direction],
                            dtype=float)
        tied = np.flatnonzero(np.isclose(values, values.max()))
        return Direction(int(rng.choice(tied)))

    @property
    def visited_cells(self) -> int:
        return len(self._base) + len(self._feature)
