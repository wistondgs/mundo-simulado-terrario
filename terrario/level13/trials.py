"""Los bancos del Nivel 1.3 · enumerados, sin azar y sin mundo.

No hace falta generador estocástico: los casos son cuatro, sesenta y cuatro y
dieciséis. Enumerarlos elimina de golpe el canal lateral del RNG y convierte
`I(G ; o_query) = 0` en una **identidad del banco** en vez de una estimación.

Las dos observaciones son distintas a propósito. El cue tiene que sobrevivir no
sólo al tiempo lógico sino a un **cambio real de la entrada sensorial**: si la
presentación y la consulta compartieran observación, un registro indebidamente
indexado por lo que se ve pasaría el banco sin que nadie lo notara.

Ambas son fijas, alcanzables en el mundo heredado, independientes del cue e
idénticas para las cuatro historias.
"""

from __future__ import annotations

from dataclasses import dataclass

from terrario.level11.cue import ALL_CUES, CueSemantics, CueToken
from terrario.level11.world import ALL_OBSERVATIONS, Direction, Observation

#: Sellados en `docs/LEVEL13_ORACULO_PREREGISTRADO.md`.
O_PRESENT: Observation = (1, 0, 0, 0)     # UP bloqueado
O_QUERY: Observation = (0, 0, 0, 0)       # las cuatro libres


@dataclass(frozen=True)
class Trial:
    """Un ensayo. `stored_cue` puede diferir de `true_cue`: así se construye el
    control barajado sin tocar nada más."""

    o_present: Observation
    true_cue: CueToken
    stored_cue: CueToken
    o_query: Observation

    def target(self, semantics: CueSemantics) -> Direction:
        """Lo que hay que acertar es la dirección del cue **verdadero**."""
        return semantics.direction_of(self.true_cue)


def critical_bank() -> list[Trial]:
    """Cuatro historias, mismo presente. La única diferencia es lo que se vio."""
    return [Trial(O_PRESENT, c, c, O_QUERY) for c in ALL_CUES]


def parity_bank() -> list[tuple[Observation, CueToken]]:
    """Las 16×4 = 64 combinaciones, para comparar el canal contra el presente."""
    return [(o, g) for o in ALL_OBSERVATIONS for g in ALL_CUES]


def shuffled_bank() -> list[Trial]:
    """Tabla 4×4 exactamente balanceada: `P(M=c_j | G=c_i) = ¼` para todo `i,j`.

    `M ⊥ G` **exacto**, luego `R = ¼` con varianza cero. Barajar un flujo
    muestreado --como en 1.1 y 1.2-- habría arrastrado ruido de estimación.

    Y no se barajan ensayos enteros: mover junto `(g, o, objetivo)` conserva toda
    la relación y el control acabaría empatando con el brazo que controla, que
    fue exactamente el defecto del Nivel 1.1.
    """
    return [Trial(O_PRESENT, verdadero, guardado, O_QUERY)
            for verdadero in ALL_CUES for guardado in ALL_CUES]


def leaky_bank(semantics: CueSemantics) -> list[Trial]:
    """FIXTURE NEGATIVA de L13-3: la consulta codifica el cue uno a uno.

    Cuatro observaciones distintas, una por historia. Entonces
    `I(G ; o_query) = 2 bits` y el gate debe rechazar el banco.
    """
    observaciones = [(0, 0, 0, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0)]
    return [Trial(O_PRESENT, c, c, observaciones[int(c)]) for c in ALL_CUES]
