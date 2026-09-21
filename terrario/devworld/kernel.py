"""D1 · TaskKernel: qué exige un problema, separado de cómo se ve esta vez.

El generador diagnóstico (`terrario.lab.world_generator`) queda CONGELADO y no
se toca. Este paquete es la segunda clase de mundo y vive aparte a propósito:
el diagnóstico mide si una facultad está; el de desarrollo produce la
experiencia que podría hacerla aparecer. Mezclarlos haría que la capacidad se
midiera en el mismo mundo donde se adquirió.

LA DISTINCIÓN QUE SOSTIENE TODO

    x = (z, n)

    z   estructura cognitiva. QUÉ relación hay que resolver. Estable.
    n   variables incidentales. Cómo se ve esta vez. Varían sin límite.

Un kernel no es un punto en el espacio de exigencias: es un PREDICADO sobre
mundos. Esa es la corrección que hace posible la variación renovable.

    diagnóstico   delay = 5                 un mundo
    desarrollo    delay >= 3                un conjunto infinito de mundos,
                                            todos exigiendo memoria

El valor concreto dentro del conjunto que satisface el predicado es
incidental. El predicado es causal. Por eso se puede variar el retraso sin
dejar de exigir memoria, y por eso `delay` aparece a la vez en la parte causal
(como cota) y en la incidental (como valor).

POR QUÉ EL MUNDO DIAGNÓSTICO SE AGOTA, MEDIDO

En `world_generator.generate`, con `sequence=1`:

    values = (0.9,) if designated == "up" else (0.1,)

el valor del cue está DETERMINADO por la respuesta. Hay exactamente dos
situaciones distintas y no hay regla que inducir: hay dos pares que memorizar.
Un organismo que los memoriza es indistinguible de uno que aprendió algo.

Aquí el cue se sortea de un vocabulario amplio y el lado lo decide una REGLA
sobre su valor. Eso convierte «memorizar dos pares» en «inducir un umbral», y
hace posible la prueba que importa: retirar valores de cue nunca vistos y
preguntar si acierta.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Mapping, Sequence

# --- El vocabulario de cues -------------------------------------------------

#: El cue vive en el canal 0, que el organismo SÍ ve. Se sortea de una rejilla
#: fina en vez de un par de constantes. Los extremos se evitan para que el
#: umbral no sea trivialmente el borde del rango, y se deja un hueco alrededor
#: de la frontera para que ningún valor sea ambiguo por redondeo.
CUE_MIN, CUE_MAX = 0.05, 0.95
CUE_BOUNDARY = 0.5
CUE_MARGIN = 0.05
#: Resolución del vocabulario. 91 valores en la rejilla, menos los que caen en
#: la banda prohibida alrededor de la frontera.
CUE_STEP = 0.01


def cue_vocabulary(step: float = CUE_STEP) -> tuple[float, ...]:
    """Los valores de cue admisibles: rejilla fina sin la banda de la frontera."""
    n = int(round((CUE_MAX - CUE_MIN) / step))
    grid = (round(CUE_MIN + i * step, 10) for i in range(n + 1))
    return tuple(v for v in grid if abs(v - CUE_BOUNDARY) >= CUE_MARGIN)


def side_of_cue(value: float) -> str:
    """LA REGLA. Es una función del valor, no una tabla de pares.

    Esto es `z`: lo único que hay que inducir. Todo lo demás es `n`."""
    return "up" if value > CUE_BOUNDARY else "down"


# --- El kernel --------------------------------------------------------------

@dataclass(frozen=True)
class TaskKernel:
    """Una regularidad cognitiva, y qué la hace necesaria.

    `faculty`       la facultad que hay que tener para resolverlo. Es lo que el
                    oráculo amputado pierde en D5.
    `causal`        el predicado. Un mundo pertenece al kernel si lo cumple.
                    Se expresa como cotas sobre ejes, no como valores.
    `incidental`    los ejes que varían libremente. Su rango es la fuente de
                    la variedad renovable.
    `relax`         cómo se construye el gemelo: qué hay que cambiar para que
                    la facultad deje de hacer falta, y NADA MÁS.
    """

    name: str
    faculty: str
    causal: Mapping[str, tuple[float, float]]
    incidental: Mapping[str, tuple[float, float]]
    relax: str
    describe: str = ""

    def satisfies(self, **values: float) -> bool:
        """¿Una instancia con estos valores pertenece al kernel?"""
        for axis, (lo, hi) in self.causal.items():
            if axis not in values:
                raise KeyError(f"{self.name}: falta el eje causal {axis!r}")
            if not (lo <= values[axis] <= hi):
                return False
        return True

    def why_not(self, **values: float) -> tuple[str, ...]:
        """Qué ejes causales viola. Para que un fallo diga dónde."""
        return tuple(
            f"{ax}={values.get(ax)!r} fuera de [{lo}, {hi}]"
            for ax, (lo, hi) in self.causal.items()
            if not (lo <= values.get(ax, float("nan")) <= hi))


#: VIEW_RADIUS del motor es 2: con `delay <= 2` el cue sigue en la ventana al
#: elegir y no hace falta retener nada. El predicado de memoria empieza en 3.
#: El techo es de presupuesto, no de concepto: más retraso alarga el pasillo y
#: encarece la vida sin cambiar qué facultad resuelve el problema.
MEMORY = TaskKernel(
    name="MEM-DEV",
    faculty="memory",
    causal={"delay": (3.0, 8.0)},
    incidental={"cue_value": (CUE_MIN, CUE_MAX),
                "delay": (3.0, 8.0),
                "distractors": (0.0, 2.0)},
    relax="cue_at_door",
    describe="observar el cue, retenerlo mientras sale de la ventana, y usarlo "
             "para elegir puerta. La regla cue->lado es un umbral, no una tabla.")

#: Control positivo del propio banco: un kernel que NO exige memoria, para
#: comprobar que el medidor de agotamiento y la puerta antifuga no dan
#: «exige» por construcción. Aquí el cue queda dentro de la ventana.
NO_MEMORY = TaskKernel(
    name="NOMEM-DEV",
    faculty="memory",
    causal={"delay": (1.0, 2.0)},
    incidental={"cue_value": (CUE_MIN, CUE_MAX),
                "delay": (1.0, 2.0),
                "distractors": (0.0, 2.0)},
    relax="cue_at_door",
    describe="igual que MEM-DEV pero el cue sigue visible al elegir.")

KERNELS: Mapping[str, TaskKernel] = {k.name: k for k in (MEMORY, NO_MEMORY)}
