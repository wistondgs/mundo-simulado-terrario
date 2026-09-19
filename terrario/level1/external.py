"""El carril externo sensorimotor · un método ajeno bajo nuestras condiciones.

Éste no es un ser nuestro. Es un mecanismo de aprendizaje **descrito fuera**,
adaptado para consumir exactamente la misma experiencia que el Agente de Nivel 1
y medirse con exactamente el mismo instrumento. La pregunta que contesta no es
«cuál es mejor» sino qué obtiene un método externo cuando no se le cambia nada
del experimento a su favor ni en su contra.

QUÉ ES ESTO Y QUÉ NO ES. Tres operaciones que el proyecto mantiene separadas:

    REPLICACIÓN    reproducir el experimento ajeno tal como se hizo -- su
                   estudio, su entorno, su código, sus condiciones y sus
                   métricas. Terrario no entra.
    TRANSFERENCIA  meter un mecanismo en NUESTRO mundo y ver qué hace aquí.
    COMPARACIÓN    contrastar perfiles entre nuestro ser y el externo.

Este módulo es **TRANSFERENCIA**, y nada más. No replica ningún experimento
publicado: no hay estudio, ni versión de código, ni configuración original que
se esté reproduciendo, y por tanto no autoriza ninguna afirmación de la forma
«obtuvimos lo que ellos obtuvieron». El orden del proyecto pone la replicación
ANTES de la transferencia, así que esto está adelantado a su turno y queda
aparcado hasta que exista la réplica que le da sentido.

PROCEDENCIA
    origen metodológico   Explauto (INRIA/FLOWERS)
    familia               nearest-neighbor forward sensorimotor model
    exploración           random motor babbling
    integración           clean-room: reimplementado desde la descripción
                          algorítmica publicada
    código incorporado    NINGUNO. Ni ficheros ni fragmentos.
    clasificación         TRANSFERENCIA, no replicación
    estudio replicado     NINGUNO

El patrón que se reproduce es el ciclo de manoteo motor: predecir la
consecuencia sensorial del propio acto, ejecutarlo, observar el efecto real y
actualizar con el ejemplar. Eso es lo que se adapta; el cuerpo, los sensores y
el espacio de actos son los nuestros.

LA DIFERENCIA ARQUITECTÓNICA, que es el objeto del experimento
    el ser propio     experiencia → conteos   (estadística suficiente)
    el carril externo experiencia → ejemplares (biblioteca de casos)

Se conserva a propósito. Colapsar los ejemplares en conteos convertiría este
brazo en nuestro propio Beta-Bernoulli con otro nombre, y el contraste dejaría
de medir nada.

DOS DECISIONES QUE NO SON DEL ALGORITMO SINO DEL PROTOCOLO, y que por eso se
declaran aquí en vez de quedar dentro de una expresión:

1. **Empates.** Con ocho bits binarios los empates a distancia mínima son la
   norma, no la excepción. Elegir «el primero que encuentre» haría que el
   resultado dependiera del orden de inserción, que es azar de implementación.
   Participan TODOS los ejemplares a distancia mínima.

2. **Salida probabilística.** Un vecino más próximo devuelve una etiqueta dura.
   Contra Brier eso mezclaría dos diferencias --el mecanismo de aprendizaje y la
   forma de la salida-- y nos haría leer como aprendizaje algo que es función de
   pérdida. La predicción es la fracción de `MOVED` entre los vecinos mínimos.
   No es un prior Beta ni suavizado de Laplace: sin ejemplares no hay voto y la
   respuesta es exactamente `1/2`, igual que el prior del ser propio, para que
   ambos partan de la misma condición epistemológica.

La etiqueta dura del algoritmo no se pierde: `native_predict` la conserva como
métrica secundaria de acierto.

COSTE
    La búsqueda es un barrido lineal sobre toda la memoria. No hay índice, ni
    árbol, ni hash, ni poda: el coste por consulta es O(|M|) y ése es uno de los
    números que el experimento quiere medir. El barrido se ejecuta en numpy en
    vez de en un bucle de Python, lo que cambia la constante y no el orden --
    sin eso, una campaña de 8.192 ejemplares y 16.384 consultas no termina en
    tiempo humano y no habría nada que medir.
"""

from __future__ import annotations

import numpy as np

from terrario.level1.world import Direction, Observation

#: Cuatro bits de sentido más cuatro de acto.
FEATURE_WIDTH = len(Direction) * 2

#: La acción NO se codifica como entero ordinal. Con `UP=0` y `RIGHT=3` la
#: distancia diría que derecha está tres veces más lejos de arriba que abajo,
#: que es una afirmación sobre el espacio motor que nadie hizo y que el
#: algoritmo se creería.
_ONE_HOT: dict[Direction, np.ndarray] = {
    d: np.eye(len(Direction), dtype=np.uint8)[int(d)] for d in Direction
}


def encode(observation: Observation, direction: Direction) -> np.ndarray:
    """El vector sensorimotor `x = [o ; onehot(a)]`, de ocho bits."""
    return np.concatenate((
        np.asarray(observation, dtype=np.uint8), _ONE_HOT[Direction(direction)]))


class NearestNeighborForwardModel:
    """Modelo directo por vecino más próximo sobre ejemplares sensorimotores.

    Guarda cada experiencia tal cual --sin resumirla-- y contesta una consulta
    con el voto de todos los ejemplares a distancia de Hamming mínima.

    **Límite que hay que declarar antes de leer un resultado.** Este modelo sí
    puede contestar sobre una situación nunca vista, porque hay ejemplares a
    distancia 1 o 2 que votan; pero lo que vota es parecido de patrón, no la
    regla. Si los vecinos más próximos de una situación nueva discrepan sobre lo
    que le pasó a cada uno, la respuesta se acerca a `1/2` sin que eso signifique
    que el modelo «sabe que no sabe»: significa que sus vecinos no coinciden.
    """

    def __init__(self, *, initial_capacity: int = 1024) -> None:
        if initial_capacity < 1:
            raise ValueError(f"la capacidad inicial debe ser >= 1; se pidió {initial_capacity}")
        self._inputs = np.zeros((initial_capacity, FEATURE_WIDTH), dtype=np.uint8)
        self._outcomes = np.zeros(initial_capacity, dtype=np.uint8)
        self._size = 0

    # --- lo que sabe ---------------------------------------------------------

    def _neighbours(self, query: np.ndarray) -> np.ndarray:
        """Los resultados de TODOS los ejemplares a distancia mínima.

        El conjunto completo, no uno elegido: así la respuesta no depende del
        orden de inserción, que sería azar de implementación entrando en el
        resultado por la puerta de atrás.
        """
        stored = self._inputs[:self._size]
        distances = np.count_nonzero(stored != query, axis=1)
        return self._outcomes[:self._size][distances == distances.min()]

    def predict(self, observation: Observation, direction: Direction) -> float:
        """`P(me muevo | esto que veo, esta dirección)`. No escribe nada.

        Sin ejemplares la respuesta es exactamente `1/2`: el carril externo nace
        sin opinión, igual que el ser propio con su prior `Beta(1,1)`. No se
        inventa conocimiento y no se le regala un prior que su algoritmo no
        tiene.
        """
        if self._size == 0:
            return 0.5
        return float(self._neighbours(encode(observation, direction)).mean())

    def native_predict(self, observation: Observation, direction: Direction) -> int:
        """La etiqueta dura que el algoritmo externo produce de suyo.

        No alimenta Brier --mezclaría mecanismo con forma de salida-- pero se
        conserva para no ocultar la naturaleza del método: mide acierto, no
        calibración.
        """
        return int(self.predict(observation, direction) >= 0.5)

    # --- cómo cambia ---------------------------------------------------------

    def observe(self, observation: Observation, direction: Direction,
                moved: int) -> None:
        """Guardar el ejemplar. Es toda la adaptación que este modelo tiene.

        No hay tasa de aprendizaje, ni recompensa, ni olvido: la actualización es
        añadir lo que pasó. El crecimiento por duplicación es administración de
        memoria, no parte del algoritmo -- el barrido sigue siendo lineal sobre
        lo almacenado.
        """
        if self._size == len(self._outcomes):
            self._inputs = np.resize(self._inputs, (self._size * 2, FEATURE_WIDTH))
            self._outcomes = np.resize(self._outcomes, self._size * 2)
        self._inputs[self._size] = encode(observation, direction)
        self._outcomes[self._size] = int(moved)
        self._size += 1

    # --- cómo se lee ---------------------------------------------------------

    def act(self, observation: Observation, rng: np.random.Generator) -> Direction:
        """Elegir la dirección cuya consecuencia predice mejor.

        Misma política de empate que el resto de brazos comparables --sorteo
        entre los máximos con el generador que se le pasa-- para que la lectura
        conductual no difiera en nada salvo en lo que cada uno aprendió.
        """
        values = np.asarray([self.predict(observation, d) for d in Direction],
                            dtype=float)
        tied = np.flatnonzero(np.isclose(values, values.max()))
        return Direction(int(rng.choice(tied)))

    # --- lo que cuesta -------------------------------------------------------

    @property
    def memory_items(self) -> int:
        """Ejemplares guardados. Crece con la experiencia, por construcción."""
        return self._size

    @property
    def memory_bytes(self) -> int:
        """Bytes de los ejemplares en uso, sin contar capacidad reservada."""
        return self._size * (FEATURE_WIDTH + 1)
