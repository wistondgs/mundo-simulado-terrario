"""La única adquisición nueva del Nivel 1.1 · `Q(g,a)`.

Dieciséis asociaciones entre token de señal y comando motor, con el mismo conteo
Beta-Bernoulli y el mismo prior que el cuerpo. Nada más.

**Sólo aprende cuando hubo movimiento.** Una pared informa sobre el cuerpo y el
mundo, no sobre qué significa la señal: si el comando no se pudo ejecutar, no hay
dirección física que comparar, y contarlo como evidencia en contra enseñaría a
`Q` algo que no vio.

**`R` no es recompensa.** Es una propiedad objetiva de la transición —el
desplazamiento coincidió o no con la referencia— y no entra en ninguna función
de valor. La política puntúa una probabilidad conjunta, no una utilidad.
"""

from __future__ import annotations

import numpy as np

from terrario.level11.cue import ALL_CUES, CueToken
from terrario.level11.world import Direction


class DirectionalAssociation:
    """`Q(g,a) = P(coincide | señal, comando, hubo movimiento)`.

    Las dieciséis celdas nacen en `1/2`: el ser no tiene opinión sobre qué
    significa ninguna señal. Lo que debe descubrir es la correspondencia, y la
    descubre contando, no comparando nombres --el agente no tiene acceso a la
    semántica de los tokens.
    """

    def __init__(self, *, prior_alpha: float = 1.0, prior_beta: float = 1.0,
                 frozen: bool = False) -> None:
        self.prior_alpha = prior_alpha
        self.prior_beta = prior_beta
        self.frozen = frozen
        self._belief: dict[tuple[CueToken, Direction], list[float]] = {}

    def predict(self, cue: CueToken, action: Direction) -> float:
        """No escribe: consulta con valor por defecto, como todo el banco."""
        alpha, beta = self._belief.get((cue, action),
                                       (self.prior_alpha, self.prior_beta))
        return alpha / (alpha + beta)

    def observe(self, cue: CueToken, action: Direction, *, moved: int,
                physical: Direction | None,
                semantics_direction: Direction | None) -> bool:
        """Devuelve si la observación fue informativa.

        `semantics_direction` es la dirección que el token significaba en ese
        ensayo, y la calcula el EXPERIMENTO. Llega ya resuelta para que el
        aprendiz no pueda consultar la semántica ni por descuido.
        """
        if self.frozen or not moved or physical is None:
            return False
        if semantics_direction is None:
            raise ValueError("una transición con movimiento necesita su dirección de referencia")
        key = (cue, action)
        if key not in self._belief:
            self._belief[key] = [self.prior_alpha, self.prior_beta]
        aligned = int(physical == semantics_direction)
        self._belief[key][0 if aligned else 1] += 1
        return True

    def coverage(self) -> dict[tuple[CueToken, Direction], int]:
        """Evidencia informativa por asociación. El mínimo sobre las dieciséis
        es la dosis real; la media esconde celdas hambrientas."""
        return {(c, a): int(sum(self._belief.get((c, a), (1.0, 1.0))) - 2)
                for c in ALL_CUES for a in Direction}

    @property
    def informative_minimum(self) -> int:
        return min(self.coverage().values())

    @property
    def visited_cells(self) -> int:
        return len(self._belief)
