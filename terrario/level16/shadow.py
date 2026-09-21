"""K-SOMBRA · el aprendiz científico, que no es un brazo.

Su función es contestar una pregunta que el organismo no puede contestar sobre sí
mismo: **¿había algo que aprender?** Sin ella, un resultado nulo es ambiguo entre
«el mecanismo no tiene plasticidad» y «esta vida no daba para nada», y esas dos
cosas son evidencia sobre partes distintas del ser --la segunda es evidencia
negativa sobre S0, no sobre A1.

No estima: **calcula**. Bajo política uniforme con rebote, la cadena sobre celdas
es simétrica --`P(c->c') = 1/4` en ambos sentidos para cada par adyacente libre--
luego su distribución estacionaria es uniforme sobre el componente natal. Eso
permite escribir la conditional exacta

    P(o'|o) = (1/|C_o|) * sum_{c en C_o} (1/4) * sum_d 1[firma(aterriza(c,d)) = o']

donde `C_o` son las celdas alcanzables cuya firma es `o`. Es el suelo de pérdida
alcanzable en este mundo: ningún contador puede bajar de ahí salvo por azar de
muestreo.

Se calcula de la rejilla. **No ve la trayectoria, no ve la tabla y jamás
realimenta al agente** --ni su política, ni su aprendizaje, ni su evaluación.
"""

from __future__ import annotations

import numpy as np

from terrario.level1.world import DELTA, Direction, Grid, Observation
from terrario.level16.structure import _signature
from terrario.level16.temporal import OBSERVATION_INDEX, TemporalModel


class AnalyticShadow:
    """`P(o'|o)` exacta del mundo. El techo contra el que se lee todo lo demás."""

    def __init__(self, grid: Grid) -> None:
        self._table = self._solve(grid)

    @staticmethod
    def _solve(grid: Grid) -> np.ndarray:
        alcanzables = {grid.position}
        pila = [grid.position]
        while pila:
            fila, columna = pila.pop()
            for direccion in Direction:
                destino = (fila + DELTA[direccion][0], columna + DELTA[direccion][1])
                if grid.cells[destino] == 0 and destino not in alcanzables:
                    alcanzables.add(destino)
                    pila.append(destino)

        tabla = np.zeros((16, 16))
        celdas_por_firma: dict[int, int] = {}
        for celda in alcanzables:
            origen = OBSERVATION_INDEX[_signature(grid, celda)]
            celdas_por_firma[origen] = celdas_por_firma.get(origen, 0) + 1
            fila, columna = celda
            for direccion in Direction:
                destino = (fila + DELTA[direccion][0], columna + DELTA[direccion][1])
                aterriza = destino if grid.cells[destino] == 0 else celda
                tabla[origen, OBSERVATION_INDEX[_signature(grid, aterriza)]] += 0.25

        for origen, cuantas in celdas_por_firma.items():
            tabla[origen] /= cuantas
        for origen in range(16):
            if tabla[origen].sum() == 0:          # firma inalcanzable
                tabla[origen] = 1.0 / 16
        return tabla

    def probability(self, previous: Observation, following: Observation) -> float:
        return float(self._table[OBSERVATION_INDEX[previous],
                                 OBSERVATION_INDEX[following]])

    def change_probability(self, previous: Observation) -> float:
        indice = OBSERVATION_INDEX[previous]
        return float(1.0 - self._table[indice, indice])

    def as_table(self) -> np.ndarray:
        return self._table.copy()


def teachability(shadow: AnalyticShadow, bank) -> float:
    """Cuántos nats hay *disponibles* en este mundo sobre el ser sin experiencia.

    Si esto es prácticamente cero, la vida no podía enseñar nada y un nulo en A1
    no dice nada del mecanismo. Es el discriminante entre `N-EXPERIENCIA` y
    `N-PLASTICIDAD`.
    """
    from terrario.level16.metrics import log_loss
    return float(np.log(16)) - log_loss(shadow, bank)
