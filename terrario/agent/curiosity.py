"""CURIO-A1 — el error de la propia predicción como motivo para actuar.

Procedencia: Pathak et al. 2017 (TI-0090), `CLM-0121` tipado
`OPERATIONAL_DEFINITION` — «La curiosidad se operacionaliza como error al
predecir las consecuencias de las propias acciones» —, `CLM-0122` — «El error
del modelo directo se entrega al agente como señal de recompensa intrínseca» —
y `CLM-0123` — «Cuando la recompensa externa es escasa o ausente, la señal
intrínseca impulsa la exploración».

Ese último claim describe el fallo que este repositorio midió antes de leerlo:
en un mundo generado que exige LEARN-A1, A4 recorre 2 columnas de 34, alcanza 1
estación de 8 y muere de inanición, porque no tiene razón para ir a ningún
sitio. La fuente ya nombraba el problema y el remedio.

**La línea que no se cruza.** La señal no puede depender de dónde está la
comida. Dice «andá donde tu predicción falla», nunca «las puertas son buenas».
Si supiera el mapeo habríamos construido la respuesta dentro del organismo, y
todo lo que midiéramos después seríamos nosotros. Por eso aquí sólo entran dos
cantidades que el organismo produce sobre sí mismo —lo que predijo y lo que
ocurrió— y ninguna que venga del mundo con su significado ya puesto.

**Confusor declarado y no resuelto.** `CLM-0126` advierte que el error puede
mantenerse alto por factores incontrolables, y `CLM-0125` que la dinámica
inversa es lo que lo reduce. A4 no la implementa. Un organismo curioso en un
mundo con ruido irreducible puede quedarse mirando la estática; esto no lo
impide, sólo lo deja dicho.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class IntrinsicPredictionError:
    """Convierte el error de predicción en recompensa intrínseca.

    `scale` es el peso de la señal frente a la consecuencia metabólica, y es un
    parámetro y no una constante porque su valor correcto es una pregunta
    empírica, no una convicción. `floor` descuenta una línea base corrida del
    error: lo que motiva es predecir PEOR DE LO HABITUAL, no predecir mal en
    general — sin eso, un organismo que predice mal en todas partes recibe la
    misma señal en todas partes, que es no tener dirección otra vez.
    """

    scale: float = 1.0
    floor_decay: float = 0.01
    _floor: float = 0.0
    _count: int = 0

    def signal(self, prediction_error: float | None) -> float:
        """La recompensa intrínseca de este paso.

        `None` —que es lo que A4 deja cuando no hubo predicción— vale cero, no
        un valor imputado: no saber cuánto se equivocó no es equivocarse poco.
        """
        if prediction_error is None:
            return 0.0
        error = float(prediction_error)
        self._count += 1
        self._floor += (error - self._floor) * max(self.floor_decay, 1.0 / self._count)
        return self.scale * (error - self._floor)

    def state(self) -> dict[str, Any]:
        return {"floor": self._floor, "count": self._count, "scale": self.scale}

    def reset(self) -> None:
        self._floor = 0.0
        self._count = 0
