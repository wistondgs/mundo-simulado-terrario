"""Nivel 1.2 · un ser con un motivo propio para elegir qué probar.

Los seres del Nivel 1 no eligen. El banco les entrega un flujo de actividad
motora basal --acciones uniformes, las mismas para todos-- y cada uno aprende
de la misma experiencia. Ese invariante es lo que hace la comparación pareada,
y hay un test que lo fija.

Este ser rompe ese invariante a propósito, porque sin romperlo no se puede
preguntar lo que queremos preguntar. Su mecanismo consiste en que la sorpresa
dirige la acción; con un flujo impuesto no hay nada que dirigir, y lo que
quedaría sería la mitad muerta del mecanismo.

PROCEDENCIA
    origen   Spisak, Tcaci Popescu, Rustler, Wermter, O'Regan y Hoffmann,
             «Robot in a crib», Science Robotics 11(117), eaed4106, 2026.
             DOI 10.1126/scirobotics.aed4106
    tipo     TRANSFERENCIA del mecanismo, no réplica. Su experimento corre
             sobre un iCub en Gazebo; aquí sólo viaja la manera de aprender.
    código   NINGUNO copiado. Reimplementado desde Materials and Methods.

LO QUE VIAJA, y es lo único que viaja

    pérdida de predicción   el error al predecir la consecuencia del propio acto
    sorpresa                binaria, cuando ese error supera un umbral
    tabla de interés        sube de golpe a 1 con sorpresa, baja 0,1 sin ella
    objetivo de exploración cada `refresh_rate` pasos, lo más interesante
    equilibrio              la acción sale de pesar predicción contra curiosidad

LO QUE NO VIAJA, y por qué

    El código poblacional de 990 neuronas a 18 articulaciones existe porque el
    iCub tiene articulaciones continuas. Aquí hay cuatro actos discretos: no
    hay nada que codificar. Y su pérdida de predicción de la propia acción
    --predecir los valores articulares que uno mismo va a emitir-- es trivial
    cuando el acto es una de cuatro opciones que uno elige.

    Tampoco viaja el móvil, ni Gazebo, ni el cuerpo. El papel que el móvil
    juega en su mundo --dar una consecuencia sensorial con cierto grado de
    predictibilidad-- aquí lo juega `MOVED / BLOCKED`, que ya existe.

DOS ADAPTACIONES, declaradas porque son decisiones y no traducciones

1. **El umbral de sorpresa.** El suyo es `1.0`, sobre una pérdida que suma
   errores cuadráticos de 18 articulaciones más el cambio de imagen. Aquí la
   pérdida es `(q - y)²`, acotada en `[0, 1]`: con su número la sorpresa no
   saltaría nunca. Se ancla en `0.25`, que no es arbitrario: es exactamente lo
   que produce un predictor ignorante que siempre dice `1/2`. Sorprenderse
   significa entonces «he fallado más que si no supiera nada».

2. **Sobre qué se guarda el interés.** Ellos discretizan el rango de cada
   articulación en diez grupos y guardan interés por (articulación, grupo) --
   es decir, sobre RASGOS del acto, no sobre actos completos. Aquí se guarda
   por par `(observación, dirección)`, que es la granularidad del ser que
   aprende por casos. Se eligió así para que el contraste contra
   `ContingencyTable` sea una intervención de una sola variable: mismo
   sustrato de conteo, misma granularidad, y la curiosidad como única
   diferencia. La versión por rasgos queda pendiente y sería el contraste
   contra el que aprende por reglas.
"""

from __future__ import annotations

import numpy as np

from terrario.level1.world import Direction, Grid, Observation, Transition, physics_contract

#: Los pesos con los que ellos equilibran las dos pérdidas (Methods: PW = 0.3,
#: CW = 1). Se conservan tal cual: son de ellos y no hay motivo para moverlos.
PREDICTION_WEIGHT = 0.3
CURIOSITY_WEIGHT = 1.0

#: Cada cuántos pasos recalculan el objetivo de exploración. Suyo, para
#: simulación.
REFRESH_RATE = 3

#: Cuánto decae el interés de un acto que no sorprendió. Suyo.
INTEREST_DECAY = 0.1

#: Ver la adaptación 1 del docstring. Es el Brier de un predictor ignorante.
NOVELTY_THRESHOLD = 0.25


class PredictiveCuriosity:
    """Conteo Beta-Bernoulli, más un motivo para elegir qué probar.

    El sustrato predictivo es el mismo que el del ser que aprende por casos:
    una creencia por par, prior `Beta(1,1)`, media posterior `α/(α+β)`. Lo que
    se añade encima es el lazo de ellos.

    **Límite que hay que declarar antes de leer un resultado.** Este ser hereda
    el límite del que aprende por casos: las celdas son independientes y un par
    nunca visto devuelve el prior. La curiosidad cambia QUÉ visita, no su
    capacidad de generalizar. Si mejora sobre las situaciones retiradas será
    porque las visitó, no porque las dedujera.
    """

    def __init__(self, *, prior_alpha: float = 1.0, prior_beta: float = 1.0,
                 novelty_threshold: float = NOVELTY_THRESHOLD,
                 refresh_rate: int = REFRESH_RATE,
                 prediction_weight: float = PREDICTION_WEIGHT,
                 curiosity_weight: float = CURIOSITY_WEIGHT,
                 interest_decay: float = INTEREST_DECAY,
                 frozen: bool = False) -> None:
        self.prior_alpha = prior_alpha
        self.prior_beta = prior_beta
        self.novelty_threshold = novelty_threshold
        self.refresh_rate = refresh_rate
        self.prediction_weight = prediction_weight
        self.curiosity_weight = curiosity_weight
        self.interest_decay = interest_decay
        self.frozen = frozen
        self._belief: dict[tuple[Observation, Direction], list[float]] = {}
        self._interest: dict[tuple[Observation, Direction], float] = {}
        self._step = 0
        self._goal: tuple[Observation, Direction] | None = None
        #: Para el trazo: cuántas veces se sorprendió y con qué pérdida.
        self.surprises = 0
        self.last_prediction_loss: float | None = None

    # --- lo que sabe ---------------------------------------------------------

    def predict(self, observation: Observation, direction: Direction) -> float:
        """`P(me muevo | esto que veo, esta dirección)`. No escribe nada."""
        alpha, beta = self._belief.get((observation, direction),
                                       (self.prior_alpha, self.prior_beta))
        return alpha / (alpha + beta)

    def interest(self, observation: Observation, direction: Direction) -> float:
        """Cuánto vale la pena volver a probar este acto. No escribe nada.

        Un par nunca probado vale `1.0`: lo desconocido es máximamente
        interesante. Es la lectura natural de su regla --la sorpresa lleva el
        interés a 1-- aplicada al caso en que aún no hubo ocasión de
        sorprenderse.
        """
        return self._interest.get((observation, direction), 1.0)

    # --- cómo cambia ---------------------------------------------------------

    def observe(self, observation: Observation, direction: Direction,
                moved: int) -> None:
        """Contar la consecuencia, medir la sorpresa, y actualizar el interés.

        El orden importa: la pérdida se mide contra la creencia ANTERIOR a
        contar, porque la sorpresa es sobre lo que se esperaba, no sobre lo que
        se sabe después.
        """
        if self.frozen:
            return
        key = (observation, direction)
        loss = (self.predict(observation, direction) - moved) ** 2
        self.last_prediction_loss = loss

        cell = self._belief.setdefault(key, [self.prior_alpha, self.prior_beta])
        cell[0] += moved
        cell[1] += 1 - moved

        if loss > self.novelty_threshold:
            # Sube de golpe: si sorprendió, no se ha aprendido a predecirlo y
            # hay que volver.
            self._interest[key] = 1.0
            self.surprises += 1
        else:
            # Baja despacio: acertar una vez puede ser suerte, y sólo acertar
            # repetidamente indica que ya se aprendió. Es su asimetría, literal.
            self._interest[key] = max(0.0, self.interest(*key) - self.interest_decay)

        self._step += 1
        if self._step % self.refresh_rate == 0:
            self._goal = None          # se recalcula en el próximo acto

    # --- cómo elige ----------------------------------------------------------

    def act(self, observation: Observation, rng: np.random.Generator) -> Direction:
        """La acción sale de pesar lo que predice contra lo que le intriga.

        `PW · q(o,a) + CW · interés(o,a)`, con los pesos de ellos. Empates
        rotos al azar con el generador que se le pasa, igual que el resto de
        carriles, para que la lectura conductual no difiera en nada salvo en lo
        aprendido.
        """
        values = np.asarray(
            [self.prediction_weight * self.predict(observation, d)
             + self.curiosity_weight * self.interest(observation, d)
             for d in Direction], dtype=float)
        tied = np.flatnonzero(np.isclose(values, values.max()))
        return Direction(int(rng.choice(tied)))

    def exploit(self, observation: Observation, rng: np.random.Generator) -> Direction:
        """Elegir sólo por lo predicho, sin curiosidad.

        Es la lectura conductual comparable con el resto del banco: los demás
        seres hacen `argmax q`, y compararlos contra un `act` que además
        persigue lo interesante mediría dos cosas a la vez.
        """
        values = np.asarray([self.predict(observation, d) for d in Direction],
                            dtype=float)
        tied = np.flatnonzero(np.isclose(values, values.max()))
        return Direction(int(rng.choice(tied)))

    @property
    def visited_cells(self) -> int:
        return len(self._belief)


# --- la adquisición que este ser necesita -------------------------------------

def self_directed_stream(model, cfg, seed: int) -> tuple[list[Transition], int]:
    """Experiencia que el propio ser provoca: él elige, el mundo responde.

    Misma forma que `motor_babbling` --mismas disposiciones, mismos pasos,
    mismo contrato físico comprobado-- con una sola diferencia: la dirección no
    sale del generador del mundo sino de `model.act`.

    **Separación del azar.** El mundo y la política usan generadores distintos.
    Si compartieran uno, las disposiciones que le tocan a cada ser dependerían
    de cuánto azar consumió eligiendo, y la comparación entre seres dejaría de
    ser sobre el mismo mundo.

    Devuelve también las violaciones del contrato físico, como el manoteo
    motor: es el GATE 0 y se cuenta igual, corra quien corra.
    """
    world_rng = np.random.default_rng(seed)
    policy_rng = np.random.default_rng(seed + 7_000_003)
    stream: list[Transition] = []
    violations = 0
    for _ in range(cfg.train_layouts):
        grid = Grid.random(cfg.grid_size, cfg.wall_probability, world_rng)
        for _ in range(cfg.train_steps_per_layout):
            observation = grid.observe()
            direction = model.act(observation, policy_rng)
            moved, next_observation = grid.step(direction)
            if moved != physics_contract(observation, direction):
                violations += 1
            model.observe(observation, direction, moved)
            stream.append(Transition(observation, direction, moved, next_observation))
    return stream, violations
