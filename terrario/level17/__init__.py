"""Agente de Nivel 1.7 · desviaciones específicas por acción.

Una sola adquisición: `C_17(O, A, O')`, las desviaciones respecto de la
expectativa temporal que el ser **ya tenía** sobre ese mismo mundo.

    P(O'|O)  +  copia opaca de su comando   ->   desviaciones por acción
    ya aprendido        sustrato nuevo             ÚNICA adquisición de 1.7

Lo que se hereda de 1.6 es **el mecanismo**, no una tabla de otro mundo: el ser
entra en `W` con la capacidad temporal como arquitectura y estado neutro, vive la
fase P, adquiere `M_0^W`, y **se congela**. Sólo entonces se abre el canal del
comando. Trasladar una tabla aprendida en `W_1` a `W_2` sería introducir
conocimiento ambiental incorrecto: `H(O'|O)` varía entre 0.5623 y 1.5464 según el
mundo, luego esa tabla no es un baseline neutro sino uno arbitrariamente sesgado.

El invariante que hace defendible «un decimal, una adquisición»:

    C_17 = 0   =>   M_1(o, a) = M_0^W(o)   para toda acción

Al nacer, 1.7 predice exactamente lo que predecía 1.6. Y lesionar `C_17` no
devuelve al ser a la ignorancia uniforme: lo devuelve **al nivel anterior**.
"""

from terrario.level17.contingency import (  # noqa: F401
    ActionContingencyModel, ContingencyContractError,
)
from terrario.level17.efference import (  # noqa: F401
    CommandToken, EfferenceCopy, EfferenceContractError,
)
from terrario.level17.wiring import (  # noqa: F401
    ActuatorWiring, wiring_stream,
)
